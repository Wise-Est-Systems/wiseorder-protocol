"""Append-only audit memory.

Each ``AuditEntry`` is a sealed JSON file under ``intellagent_audit/``,
content-addressed via ``this_entry_sha256`` (computed over the entry's body
with that field omitted). Entry *n* links to entry *n−1* via
``prev_entry_sha256``.

A corrupt or out-of-order chain raises :class:`ChainCorrupt` on read; the
runtime fails closed.
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
from intellagent_runtime.transitions import EpistemicTransition


class ChainCorrupt(Exception):
    """The audit memory chain has been tampered with or otherwise broken."""


@dataclass
class AuditEntry:
    index: int
    transition: dict[str, Any]
    prior_state_id: str
    resulting_state_id: str
    prev_entry_sha256: str | None
    this_entry_sha256: str
    sealed_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "index":              self.index,
            "transition":         self.transition,
            "prior_state_id":     self.prior_state_id,
            "resulting_state_id": self.resulting_state_id,
            "prev_entry_sha256":  self.prev_entry_sha256,
            "this_entry_sha256":  self.this_entry_sha256,
            "sealed_at":          self.sealed_at,
        }

    def body_for_hashing(self) -> dict[str, Any]:
        body = self.to_dict()
        body.pop("this_entry_sha256", None)
        return body


def _filename_for(index: int) -> str:
    return f"{index:04d}.entry.json"


class AuditMemory:
    def __init__(self, audit_dir: Path):
        self.dir = Path(audit_dir)

    # ---- Discovery -----------------------------------------------------

    def _entry_paths(self) -> list[Path]:
        if not self.dir.is_dir():
            return []
        return sorted(self.dir.glob("*.entry.json"))

    def next_index(self) -> int:
        paths = self._entry_paths()
        return len(paths)

    def head_sha256(self) -> str | None:
        paths = self._entry_paths()
        if not paths:
            return None
        body = json.loads(paths[-1].read_text(encoding="utf-8"))
        return body.get("this_entry_sha256")

    def head_index(self) -> int | None:
        paths = self._entry_paths()
        if not paths:
            return None
        return len(paths) - 1

    def head(self) -> str | None:
        return self.head_sha256()

    # ---- Append --------------------------------------------------------

    def append(
        self,
        transition: EpistemicTransition,
        prior_state_id: str,
        resulting_state_id: str,
    ) -> AuditEntry:
        index = self.next_index()
        prev = self.head_sha256()  # None for first entry
        body_without_self = {
            "index":              index,
            "transition":         transition.to_dict(),
            "prior_state_id":     prior_state_id,
            "resulting_state_id": resulting_state_id,
            "prev_entry_sha256":  prev,
            "sealed_at":          utcnow_iso8601(),
        }
        this_sha = sha256_hex(canonical_json_bytes(body_without_self))
        full_body = {**body_without_self, "this_entry_sha256": this_sha}

        self.dir.mkdir(parents=True, exist_ok=True)
        path = self.dir / _filename_for(index)
        write_atomic(path, canonical_pretty(full_body))
        return AuditEntry(**full_body)

    # ---- Listing -------------------------------------------------------

    def list_entries(self) -> list[AuditEntry]:
        out: list[AuditEntry] = []
        for path in self._entry_paths():
            body = json.loads(path.read_text(encoding="utf-8"))
            out.append(AuditEntry(**body))
        return out

    # ---- Verification --------------------------------------------------

    def verify_chain(self) -> None:
        """Walk the chain, recomputing each entry's hash and checking links.

        Raises :class:`ChainCorrupt` if any entry's recomputed hash mismatches
        its declared one or if any prev pointer fails to link.
        """
        prev_hash: str | None = None
        for i, path in enumerate(self._entry_paths()):
            try:
                body = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise ChainCorrupt(f"{path}: cannot parse entry: {exc}") from exc

            if body.get("index") != i:
                raise ChainCorrupt(
                    f"{path}: entry.index={body.get('index')!r} does not match position {i}"
                )

            declared_self = body.get("this_entry_sha256")
            without_self = {k: v for k, v in body.items() if k != "this_entry_sha256"}
            recomputed = sha256_hex(canonical_json_bytes(without_self))
            if declared_self != recomputed:
                raise ChainCorrupt(
                    f"{path}: this_entry_sha256 mismatch "
                    f"(declared {declared_self}, recomputed {recomputed})"
                )

            declared_prev = body.get("prev_entry_sha256")
            if declared_prev != prev_hash:
                raise ChainCorrupt(
                    f"{path}: prev_entry_sha256={declared_prev!r} does not link to "
                    f"prior entry's hash {prev_hash!r}"
                )

            prev_hash = declared_self
