"""Append-only audit memory for the WiseOrder runtime core.

Audit events are written to a JSONL file. Each event is a JSON object
containing at minimum::

    {
      "seq":       <int starting at 1>,
      "ts":        "<ISO-8601 UTC>",
      "event":     "<event type string>",
      "payload":   { ... },
      "prev_hash": "sha256:<hex>" | null,
      "hash":      "sha256:<hex>"
    }

The ``hash`` field is the SHA-256 of the canonical bytes of the event
object *with the ``hash`` field removed*. ``prev_hash`` chains each event
to the prior event's ``hash``; the first event has ``prev_hash: null``.

Statuses returned by :func:`verify_chain`:

  - ``AUDIT_CHAIN_VALID``     — every event verifies and chain is intact.
  - ``AUDIT_CHAIN_TAMPERED``  — at least one event's hash or prev_hash
                                 does not match the recomputed value.
  - ``AUDIT_CHAIN_EMPTY``     — file does not exist or contains no events.
  - ``AUDIT_CHAIN_INVALID``   — file exists but at least one event is
                                 structurally malformed (bad JSON or
                                 missing required field).

The module relies on :mod:`intellagent_runtime.canonical` for byte-
stable JSON and SHA-256 helpers. It does not import the kernel, state,
or runtime modules — there is no cyclic dependency.
"""

from __future__ import annotations

import datetime
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from intellagent_runtime import canonical


AUDIT_CHAIN_VALID = "AUDIT_CHAIN_VALID"
AUDIT_CHAIN_TAMPERED = "AUDIT_CHAIN_TAMPERED"
AUDIT_CHAIN_EMPTY = "AUDIT_CHAIN_EMPTY"
AUDIT_CHAIN_INVALID = "AUDIT_CHAIN_INVALID"


@dataclass
class AuditEvent:
    """One row of an audit log file."""

    seq: int
    ts: str
    event: str
    payload: dict[str, Any] = field(default_factory=dict)
    prev_hash: str | None = None
    hash: str = ""

    def core_dict(self) -> dict:
        """Return the event dict *without* the hash field — this is the
        input that ``hash`` commits to."""
        return {
            "seq": self.seq,
            "ts": self.ts,
            "event": self.event,
            "payload": self.payload,
            "prev_hash": self.prev_hash,
        }

    def to_dict(self) -> dict:
        d = self.core_dict()
        d["hash"] = self.hash
        return d


@dataclass
class ChainStatus:
    """Result of verifying an audit chain."""

    status: str
    count: int
    last_hash: str | None
    first_failure_seq: int | None = None
    reason: str = ""

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "count": self.count,
            "last_hash": self.last_hash,
            "first_failure_seq": self.first_failure_seq,
            "reason": self.reason,
        }


# ---------------------------------------------------------------------------
# I/O primitives
# ---------------------------------------------------------------------------


def _utcnow_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _compute_event_hash(event_core: dict) -> str:
    bytes_for_hash = canonical.canonical_json_bytes(event_core)
    return canonical.sha256_hex(bytes_for_hash)


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _read_last_hash(path: Path) -> tuple[int, str | None]:
    """Return (last_seq, last_hash). If the file is missing or empty,
    returns (0, None). Raises :class:`AuditMemoryError` on malformed
    trailing data."""
    if not path.is_file():
        return 0, None
    last_seq = 0
    last_hash: str | None = None
    with path.open("r", encoding="utf-8") as fh:
        for line_no, raw in enumerate(fh, start=1):
            line = raw.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as exc:
                raise AuditMemoryError(
                    f"malformed JSONL at {path}:{line_no}: {exc}"
                ) from exc
            if not isinstance(obj, dict):
                raise AuditMemoryError(f"non-object event at {path}:{line_no}")
            for key in ("seq", "ts", "event", "payload", "prev_hash", "hash"):
                if key not in obj:
                    raise AuditMemoryError(
                        f"missing field {key!r} at {path}:{line_no}"
                    )
            if not isinstance(obj["seq"], int) or obj["seq"] <= 0:
                raise AuditMemoryError(f"non-positive seq at {path}:{line_no}")
            last_seq = obj["seq"]
            last_hash = obj["hash"]
    return last_seq, last_hash


class AuditMemoryError(RuntimeError):
    """Raised when the audit log is structurally unusable."""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def append_event(
    path: str | Path,
    event: str,
    payload: dict[str, Any] | None = None,
    *,
    ts: str | None = None,
) -> AuditEvent:
    """Append a new audit event to ``path`` (JSONL).

    Returns the materialized :class:`AuditEvent` (including its computed
    ``hash`` and the captured ``prev_hash``).

    The append is atomic at the line level: events are written via an
    ``a`` open-append-mode handle, fsync'd, then closed. Truncation
    between read-of-last-hash and write-of-this-line is the only
    interleaving risk, and would be caught by :func:`verify_chain` on
    the next pass.
    """
    p = Path(path)
    _ensure_parent(p)
    last_seq, last_hash = _read_last_hash(p)

    new_event = AuditEvent(
        seq=last_seq + 1,
        ts=ts or _utcnow_iso(),
        event=str(event),
        payload=dict(payload or {}),
        prev_hash=last_hash,
    )
    new_event.hash = _compute_event_hash(new_event.core_dict())

    line = json.dumps(
        new_event.to_dict(), sort_keys=True, ensure_ascii=False, separators=(",", ":")
    )
    with p.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")
        fh.flush()
        os.fsync(fh.fileno())
    return new_event


def read_events(path: str | Path) -> list[AuditEvent]:
    """Read every event from ``path`` and return them as
    :class:`AuditEvent` objects. Empty / missing file returns ``[]``."""
    p = Path(path)
    if not p.is_file():
        return []
    out: list[AuditEvent] = []
    with p.open("r", encoding="utf-8") as fh:
        for line_no, raw in enumerate(fh, start=1):
            line = raw.strip()
            if not line:
                continue
            obj = json.loads(line)
            out.append(
                AuditEvent(
                    seq=obj["seq"],
                    ts=obj["ts"],
                    event=obj["event"],
                    payload=dict(obj.get("payload") or {}),
                    prev_hash=obj.get("prev_hash"),
                    hash=obj["hash"],
                )
            )
    return out


def verify_chain(path: str | Path) -> ChainStatus:
    """Verify the audit chain at ``path`` and return a :class:`ChainStatus`."""
    p = Path(path)
    if not p.is_file():
        return ChainStatus(status=AUDIT_CHAIN_EMPTY, count=0, last_hash=None,
                           reason="file does not exist")

    count = 0
    last_hash: str | None = None
    expected_seq = 1
    with p.open("r", encoding="utf-8") as fh:
        for line_no, raw in enumerate(fh, start=1):
            line = raw.strip()
            if not line:
                continue
            count += 1
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as exc:
                return ChainStatus(
                    status=AUDIT_CHAIN_INVALID, count=count, last_hash=last_hash,
                    first_failure_seq=count,
                    reason=f"malformed JSONL at line {line_no}: {exc}",
                )
            if not isinstance(obj, dict):
                return ChainStatus(
                    status=AUDIT_CHAIN_INVALID, count=count, last_hash=last_hash,
                    first_failure_seq=count, reason=f"non-object event at line {line_no}",
                )
            for key in ("seq", "ts", "event", "payload", "prev_hash", "hash"):
                if key not in obj:
                    return ChainStatus(
                        status=AUDIT_CHAIN_INVALID, count=count, last_hash=last_hash,
                        first_failure_seq=count, reason=f"missing field {key!r} at line {line_no}",
                    )
            if obj["seq"] != expected_seq:
                return ChainStatus(
                    status=AUDIT_CHAIN_INVALID, count=count, last_hash=last_hash,
                    first_failure_seq=expected_seq,
                    reason=f"non-monotonic seq at line {line_no}: expected {expected_seq}, got {obj['seq']}",
                )
            if obj["prev_hash"] != last_hash:
                return ChainStatus(
                    status=AUDIT_CHAIN_TAMPERED, count=count, last_hash=last_hash,
                    first_failure_seq=obj["seq"],
                    reason=(
                        f"prev_hash mismatch at seq {obj['seq']}: "
                        f"expected {last_hash!r}, got {obj['prev_hash']!r}"
                    ),
                )
            recomputed = _compute_event_hash({
                "seq": obj["seq"],
                "ts": obj["ts"],
                "event": obj["event"],
                "payload": obj["payload"],
                "prev_hash": obj["prev_hash"],
            })
            if recomputed != obj["hash"]:
                return ChainStatus(
                    status=AUDIT_CHAIN_TAMPERED, count=count, last_hash=last_hash,
                    first_failure_seq=obj["seq"],
                    reason=f"hash mismatch at seq {obj['seq']}: recomputed {recomputed!r}, stored {obj['hash']!r}",
                )
            last_hash = obj["hash"]
            expected_seq += 1

    if count == 0:
        return ChainStatus(status=AUDIT_CHAIN_EMPTY, count=0, last_hash=None,
                           reason="file present but empty")
    return ChainStatus(status=AUDIT_CHAIN_VALID, count=count, last_hash=last_hash, reason="")


def export_summary(path: str | Path) -> dict:
    """Return a small JSON-friendly summary of the audit log."""
    p = Path(path)
    status = verify_chain(p)
    events = read_events(p) if p.is_file() else []
    event_types: dict[str, int] = {}
    for e in events:
        event_types[e.event] = event_types.get(e.event, 0) + 1
    return {
        "path": str(p),
        "chain_status": status.to_dict(),
        "event_count": len(events),
        "first_seq": events[0].seq if events else None,
        "last_seq": events[-1].seq if events else None,
        "event_types": dict(sorted(event_types.items())),
    }


# ---------------------------------------------------------------------------
# Self-check
# ---------------------------------------------------------------------------


def self_check() -> int:
    import shutil
    import tempfile

    failures: list[str] = []

    def expect(name: str, condition: bool, detail: str = "") -> None:
        print(f"  [{'PASS' if condition else 'FAIL'}] {name}")
        if not condition:
            failures.append(f"{name}: {detail}")

    workdir = Path(tempfile.mkdtemp(prefix="wo-audit-selfcheck-"))
    try:
        path = workdir / "run.jsonl"

        # Empty.
        status = verify_chain(path)
        expect("empty_status", status.status == AUDIT_CHAIN_EMPTY, status.reason)

        # Append two events.
        e1 = append_event(path, "run.started", {"work_order": "WO-001"})
        e2 = append_event(path, "plan.built", {"command_count": 3})
        expect("seq_monotonic", e1.seq == 1 and e2.seq == 2)
        expect("prev_hash_chained", e2.prev_hash == e1.hash)

        # Verify.
        status = verify_chain(path)
        expect("chain_valid_after_append",
               status.status == AUDIT_CHAIN_VALID and status.count == 2, status.reason)

        # Tamper by editing the second event in place.
        text = path.read_text(encoding="utf-8").splitlines()
        edited = text[1].replace('"command_count":3', '"command_count":999')
        path.write_text(text[0] + "\n" + edited + "\n", encoding="utf-8")
        status = verify_chain(path)
        expect("tamper_detected", status.status == AUDIT_CHAIN_TAMPERED, status.reason)

        # Invalid: malformed JSON line.
        path.write_text(text[0] + "\n" + "{garbage}\n", encoding="utf-8")
        status = verify_chain(path)
        expect("invalid_detected", status.status == AUDIT_CHAIN_INVALID, status.reason)

        # Summary.
        path.write_text(text[0] + "\n" + text[1] + "\n", encoding="utf-8")
        summary = export_summary(path)
        expect("summary_has_status", "chain_status" in summary)
        expect("summary_event_types", summary["event_types"].get("run.started", 0) == 1)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)

    if failures:
        print(f"\nFAIL: {len(failures)} self-check failures")
        for f in failures:
            print(f"  ↳ {f}")
        return 1
    print("\nPASS: audit_memory self-check")
    return 0


if __name__ == "__main__":
    raise SystemExit(self_check())
