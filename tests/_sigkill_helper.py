"""Worker subprocess for the SIGKILL crash-recovery test.

Usage:
    python -m tests._sigkill_helper --base-dir <dir> --checkpoint after_stage
    python -m tests._sigkill_helper --base-dir <dir> --checkpoint after_save

The child runs the early part of an ``apply_transition`` flow, prints a
single-line marker to stdout (``STAGED`` or ``SAVED``), flushes, and then
pauses indefinitely (``signal.pause()``). The parent test reads the
marker, SIGKILLs the child, and then asserts that startup reconciliation
brings the on-disk state to a consistent point.

This is the real-process crash-recovery proof — not a synthetic crash
inside one Python interpreter.
"""

from __future__ import annotations

import argparse
import signal
import sys
from pathlib import Path

from intellagent_runtime.canonical import utcnow_iso8601
from intellagent_runtime.memory import AuditMemory
from intellagent_runtime.state import (
    EpistemicState,
    StateStore,
    compute_state_id,
)
from intellagent_runtime.transitions import EpistemicTransition


def _make_transition(from_state: str) -> EpistemicTransition:
    return EpistemicTransition(
        transition_id="sigkill_probe",
        from_state=from_state,
        regime="A",
        object_added={
            "class": "A",
            "canonicalization": "RFC8785-JCS",
            "algorithm": "SHA-256",
            "expected_digest": "sha256:" + "a" * 64,
            "observed_digest": "sha256:" + "a" * 64,
            "status": "VERIFIED",
        },
        objects_removed=[],
        action=None,
        authorization=None,
        proposer="sigkill_helper",
        proposed_at=utcnow_iso8601(),
    )


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--base-dir", required=True)
    p.add_argument(
        "--checkpoint",
        required=True,
        choices=["after_stage", "after_save"],
    )
    args = p.parse_args()

    base = Path(args.base_dir).resolve()
    store = StateStore(base)
    audit = AuditMemory(base / "intellagent_audit")
    state = store.load()

    tau = _make_transition(state.state_id)

    # Mirror the apply_transition flow step by step so we can pause at
    # the desired checkpoint.

    # Compute the would-be resulting state
    new_object_id = store.objects.put(tau.object_added)
    new_objects = sorted(set(state.objects + [new_object_id]))
    resulting_state_id = compute_state_id(new_objects)

    # (1) stage audit
    entry = audit.stage_entry(
        transition=tau,
        prior_state_id=state.state_id,
        resulting_state_id=resulting_state_id,
    )

    if args.checkpoint == "after_stage":
        # State is still old; staging file exists.
        sys.stdout.write("STAGED\n")
        sys.stdout.flush()
        signal.pause()  # block until SIGKILL — never returns
        return 99  # unreachable

    # (2) save state — now references the staged hash
    new_state = EpistemicState(
        state_id=resulting_state_id,
        objects=new_objects,
        audit_head_sha256=entry.this_entry_sha256,
        sealed_at=utcnow_iso8601(),
    )
    store.save(new_state)

    if args.checkpoint == "after_save":
        # State references staged hash; staging file not yet renamed.
        sys.stdout.write("SAVED\n")
        sys.stdout.flush()
        signal.pause()
        return 99  # unreachable

    # (3) finalize — would normally happen, included for completeness
    audit.finalize_staged(entry)
    sys.stdout.write("FINALIZED\n")
    sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
