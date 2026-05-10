"""State store and content-addressed object store.

The epistemic state is a list of object_ids plus an audit-head pointer. The
state's identity (``state_id``) is computed from its sorted object list only;
``audit_head_sha256`` is an authenticated pointer into audit memory but is
not part of the state's content-address. This is what breaks the otherwise
circular dependency between state_id and audit-entry hashes (since each
audit entry references resulting_state_id, while each state references
audit_head).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from intellagent_runtime.canonical import (
    canonical_json_bytes,
    canonical_pretty,
    sha256_hex,
    utcnow_iso8601,
    write_atomic,
)


class StateTampered(Exception):
    """Raised when the on-disk state's recomputed state_id does not match its declared one."""


def compute_object_id(body: dict[str, Any]) -> str:
    """Content-address an EpistemicObject body. The body MUST NOT include the
    ``object_id`` field (or it is stripped before hashing)."""
    pruned = {k: v for k, v in body.items() if k != "object_id"}
    return sha256_hex(canonical_json_bytes(pruned))


def compute_state_id(objects: list[str]) -> str:
    """Compute a state_id from the sorted object_id list.

    Rationale: the state's identity is the multiset of objects it holds.
    Audit history is recorded *separately* in audit memory; including it in
    state_id would create a cycle with audit-entry hashes.
    """
    return sha256_hex(canonical_json_bytes({"objects": sorted(objects)}))


@dataclass
class EpistemicState:
    state_id: str
    objects: list[str]
    audit_head_sha256: str | None
    sealed_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "state_id":          self.state_id,
            "objects":           list(self.objects),
            "audit_head_sha256": self.audit_head_sha256,
            "sealed_at":         self.sealed_at,
        }

    @classmethod
    def from_dict(cls, body: dict[str, Any]) -> "EpistemicState":
        return cls(
            state_id=str(body["state_id"]),
            objects=list(body.get("objects") or []),
            audit_head_sha256=body.get("audit_head_sha256"),
            sealed_at=str(body.get("sealed_at", "")),
        )

    @classmethod
    def initial(cls) -> "EpistemicState":
        objects: list[str] = []
        return cls(
            state_id=compute_state_id(objects),
            objects=objects,
            audit_head_sha256=None,
            sealed_at=utcnow_iso8601(),
        )


class ObjectStore:
    """Content-addressed object store. Each object body is written under
    ``<hex>.json`` (the hex part of its sha256 object_id)."""

    def __init__(self, objects_dir: Path):
        self.dir = Path(objects_dir)

    def _path_for(self, object_id: str) -> Path:
        hex_part = object_id.replace("sha256:", "")
        return self.dir / f"{hex_part}.json"

    def put(self, body: dict[str, Any]) -> str:
        """Write the object to the store (no-op if already present). Returns object_id."""
        oid = compute_object_id(body)
        path = self._path_for(oid)
        if path.exists():
            return oid
        full = {**{k: v for k, v in body.items() if k != "object_id"}, "object_id": oid}
        self.dir.mkdir(parents=True, exist_ok=True)
        write_atomic(path, canonical_pretty(full))
        return oid

    def get(self, object_id: str) -> dict[str, Any]:
        path = self._path_for(object_id)
        if not path.is_file():
            raise FileNotFoundError(f"object {object_id!r} not found in store")
        return json.loads(path.read_text(encoding="utf-8"))

    def has(self, object_id: str) -> bool:
        return self._path_for(object_id).is_file()


class StateStore:
    """Manages the working state on disk, plus the object store."""

    STATE_FILENAME = "current.json"

    def __init__(self, base_dir: Path):
        self.base = Path(base_dir)
        self.state_dir = self.base / "intellagent_state"
        self.queue_dir = self.state_dir / "queue"
        self.objects = ObjectStore(self.base / "intellagent_objects")

    @property
    def state_path(self) -> Path:
        return self.state_dir / self.STATE_FILENAME

    def init(self, force: bool = False) -> EpistemicState:
        """Create directories and seal the initial empty state."""
        if self.state_path.exists() and not force:
            raise FileExistsError(
                f"runtime already initialized at {self.state_dir}; use force=True to overwrite"
            )
        for d in (self.state_dir, self.queue_dir, self.objects.dir):
            d.mkdir(parents=True, exist_ok=True)
        initial = EpistemicState.initial()
        self.save(initial)
        return initial

    def load(self) -> EpistemicState:
        """Load the current state, verifying its content-address."""
        if not self.state_path.is_file():
            raise FileNotFoundError(f"no state found at {self.state_path}; run `intellagent init`")
        body = json.loads(self.state_path.read_text(encoding="utf-8"))
        state = EpistemicState.from_dict(body)
        recomputed = compute_state_id(state.objects)
        if recomputed != state.state_id:
            raise StateTampered(
                f"state_id mismatch on load: declared {state.state_id}, "
                f"recomputed {recomputed}"
            )
        return state

    def save(self, state: EpistemicState) -> None:
        # Recompute state_id defensively to prevent accidental drift.
        expected = compute_state_id(state.objects)
        if expected != state.state_id:
            raise StateTampered(
                f"refusing to save state: state_id {state.state_id} does not match "
                f"recomputed {expected} from objects"
            )
        write_atomic(self.state_path, canonical_pretty(state.to_dict()))
