"""Append-only audit memory.

Each ``AuditEntry`` is a sealed JSON file under ``intellagent_audit/``,
content-addressed via ``this_entry_sha256`` (computed over the entry's body
with that field omitted). Entry *n* links to entry *n-1* via
``prev_entry_sha256``.

A corrupt or out-of-order chain raises :class:`ChainCorrupt` on read; the
runtime fails closed.

Crash-safe commit (WO-RES-2026-05-24)
-------------------------------------

A naive ``append(...) -> immediately write entry`` followed by
``store.save(new_state)`` can leave audit and state inconsistent under
crash: an entry is sealed to disk whose ``resulting_state_id`` was never
persisted into ``current.json``.

This module avoids that with a two-step pattern:

    1. ``stage_entry(...)`` writes the entry to ``<idx>.entry.json.staging``.
    2. caller commits ``current.json`` (which now points to the staged
       entry's hash as its ``audit_head_sha256``).
    3. ``finalize_staged(entry)`` renames the staging file to its final
       ``<idx>.entry.json`` location.

On startup, ``reconcile_pending(expected_audit_head)`` walks staging files:

  * a staging file whose ``this_entry_sha256`` matches the live state's
    ``audit_head_sha256`` is renamed to its final path (state already
    references it; commit was interrupted before the rename).
  * any other staging file is discarded (state never accepted it).

After reconciliation, ``verify_chain()`` and ``head_sha256()`` see a clean,
consistent chain in every crash scenario.
"""

from __future__ import annotations

import json
import os
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


class StateAuditDivergence(Exception):
    """state.audit_head_sha256 does not match audit.head_sha256(). Refuse to proceed."""


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


def _staging_filename_for(index: int) -> str:
    return f"{index:04d}.entry.json.staging"


class AuditMemory:
    def __init__(self, audit_dir: Path):
        self.dir = Path(audit_dir)

    # ---- Discovery -----------------------------------------------------

    def _entry_paths(self) -> list[Path]:
        if not self.dir.is_dir():
            return []
        # Only finalized entries; staging files (*.entry.json.staging) are
        # excluded from the chain view by suffix.
        return sorted(p for p in self.dir.glob("*.entry.json") if not p.name.endswith(".staging"))

    def _staging_paths(self) -> list[Path]:
        if not self.dir.is_dir():
            return []
        return sorted(self.dir.glob("*.entry.json.staging"))

    def next_index(self) -> int:
        # The next index must skip past any staged-but-not-yet-finalized entries
        # so two concurrent stage calls in the same process do not collide.
        # On a single-process runtime this is mostly defensive.
        finalized = len(self._entry_paths())
        staged = len(self._staging_paths())
        return finalized + staged

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

    # ---- Crash-safe two-step commit ------------------------------------

    def stage_entry(
        self,
        transition: EpistemicTransition,
        prior_state_id: str,
        resulting_state_id: str,
    ) -> AuditEntry:
        """Write the entry to a ``.staging`` path and return it.

        The caller is expected to commit the new state (which references
        ``entry.this_entry_sha256``) and then call :meth:`finalize_staged`.
        """
        index = self.next_index()
        prev = self.head_sha256()
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
        staging_path = self.dir / _staging_filename_for(index)
        write_atomic(staging_path, canonical_pretty(full_body))
        return AuditEntry(**full_body)

    def finalize_staged(self, entry: AuditEntry) -> Path:
        """Rename ``<idx>.entry.json.staging`` -> ``<idx>.entry.json``.

        Call this only after the state file has been committed referencing
        ``entry.this_entry_sha256`` as its ``audit_head_sha256``. Idempotent:
        if the final file already exists (e.g., reconciliation finalized it),
        no error is raised.
        """
        staging = self.dir / _staging_filename_for(entry.index)
        final = self.dir / _filename_for(entry.index)
        if final.is_file():
            # Already finalized (e.g., by reconcile_pending). Drop any leftover.
            if staging.is_file():
                staging.unlink()
            return final
        if not staging.is_file():
            raise FileNotFoundError(
                f"finalize_staged: no staging file at {staging}; cannot promote"
            )
        os.rename(staging, final)
        return final

    def reconcile_pending(self, expected_audit_head: str | None) -> dict[str, Any]:
        """Resolve any ``.staging`` audit files at startup.

        Two cases:
          * staging entry's ``this_entry_sha256`` equals
            ``expected_audit_head``: state already references it; rename
            staging -> final. Recovery from a crash between save_state and
            finalize_staged.
          * any other staging file: state never accepted this entry; discard.
            Recovery from a crash between stage_entry and save_state.

        Returns ``{"finalized": [paths], "discarded": [paths]}`` for logging.
        Safe to call on a clean directory (returns empty lists).
        """
        finalized: list[str] = []
        discarded: list[str] = []
        for staging in self._staging_paths():
            try:
                body = json.loads(staging.read_text(encoding="utf-8"))
                staged_hash = body.get("this_entry_sha256")
                staged_index = body.get("index")
            except (json.JSONDecodeError, OSError):
                staging.unlink()
                discarded.append(str(staging))
                continue
            if not isinstance(staged_hash, str) or not isinstance(staged_index, int):
                staging.unlink()
                discarded.append(str(staging))
                continue
            if expected_audit_head == staged_hash:
                final = self.dir / _filename_for(staged_index)
                if final.is_file():
                    # Should not happen, but if it does, drop the duplicate staging
                    staging.unlink()
                    discarded.append(str(staging))
                else:
                    os.rename(staging, final)
                    finalized.append(str(final))
            else:
                staging.unlink()
                discarded.append(str(staging))
        return {"finalized": finalized, "discarded": discarded}

    def verify_state_consistency(self, state_audit_head: str | None) -> None:
        """Raise StateAuditDivergence if state's audit_head does not match audit head on disk.

        Call this at startup AFTER reconcile_pending(). If they diverge,
        manual intervention is required; runtime refuses to proceed.
        """
        live = self.head_sha256()
        if state_audit_head != live:
            raise StateAuditDivergence(
                f"state.audit_head_sha256={state_audit_head!r} does not match "
                f"audit.head_sha256()={live!r} after reconciliation. "
                f"Manual investigation required."
            )

    # ---- Legacy single-step append (crash-unsafe; kept for tests) ------

    def append(
        self,
        transition: EpistemicTransition,
        prior_state_id: str,
        resulting_state_id: str,
    ) -> AuditEntry:
        """Single-step append. CRASH-UNSAFE: prefer stage_entry+finalize_staged
        in production paths (apply_transition uses the safe pattern). Retained
        for tests that need to assert the previous behavior.
        """
        entry = self.stage_entry(transition, prior_state_id, resulting_state_id)
        return AuditEntry(**json.loads(
            (self.dir / _filename_for(entry.index) if (self.dir / _filename_for(entry.index)).is_file()
             else self.finalize_staged(entry)).read_text(encoding="utf-8")
        ))

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
