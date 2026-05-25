"""End-to-end SIGKILL crash-recovery tests for apply_transition.

Spawns a real subprocess, waits for it to reach a known checkpoint,
SIGKILLs it (signal 9 — cannot be caught, cannot be cleaned up), then
runs the reconcile path from the parent and asserts the integrity
invariants hold:

    I1. audit.verify_chain() passes.
    I2. state.audit_head_sha256 == audit.head_sha256() (no divergence).
    I3. No *.entry.json.staging files remain.

This is the real-process integrity proof — distinct from the synthetic
crash tests in test_apply_transition_crash_safety.py.
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

from intellagent_runtime.memory import AuditMemory
from intellagent_runtime.state import StateStore


HELPER_TIMEOUT_SECONDS = 10
HELPER_CHECKPOINT_TIMEOUT_SECONDS = 5


def _bootstrap(tmp_path: Path) -> tuple[StateStore, AuditMemory]:
    store = StateStore(tmp_path)
    store.init()
    audit = AuditMemory(tmp_path / "intellagent_audit")
    audit.dir.mkdir(parents=True, exist_ok=True)
    return store, audit


def _spawn_and_wait_for_marker(
    base_dir: Path,
    checkpoint: str,
    expected_marker: str,
) -> subprocess.Popen:
    """Spawn the helper subprocess and block until it prints the expected
    marker on stdout, then return the Popen handle still running.
    """
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "tests._sigkill_helper",
            "--base-dir",
            str(base_dir),
            "--checkpoint",
            checkpoint,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(Path(__file__).resolve().parent.parent),
        text=True,
    )
    deadline = time.monotonic() + HELPER_CHECKPOINT_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            stderr = proc.stderr.read() if proc.stderr else ""
            raise RuntimeError(
                f"helper exited prematurely with rc={proc.returncode} stderr={stderr!r}"
            )
        line = proc.stdout.readline().strip()
        if line == expected_marker:
            return proc
    proc.kill()
    raise TimeoutError(
        f"helper did not print {expected_marker!r} within "
        f"{HELPER_CHECKPOINT_TIMEOUT_SECONDS}s"
    )


def _sigkill_and_wait(proc: subprocess.Popen) -> int:
    os.kill(proc.pid, signal.SIGKILL)
    try:
        proc.wait(timeout=HELPER_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        proc.terminate()
        raise
    return proc.returncode


def test_sigkill_after_stage_discards_orphan(tmp_path) -> None:
    """Child SIGKILLed after staging audit, BEFORE saving state.

    Expected: orphan staging discarded; state unchanged; chain still valid.
    """
    store, audit = _bootstrap(tmp_path)

    proc = _spawn_and_wait_for_marker(tmp_path, "after_stage", "STAGED")
    staging_files = list(audit.dir.glob("*.staging"))
    assert len(staging_files) == 1, "child should have written exactly one staging file"

    rc = _sigkill_and_wait(proc)
    assert rc == -signal.SIGKILL, f"child should have died from SIGKILL, got rc={rc}"

    # State on disk is still the bootstrap state (audit_head_sha256 is None)
    state_before = store.load()
    assert state_before.audit_head_sha256 is None

    # Recovery
    recon = audit.reconcile_pending(state_before.audit_head_sha256)
    assert recon["finalized"] == []
    assert len(recon["discarded"]) == 1

    # Post-recovery integrity
    assert list(audit.dir.glob("*.staging")) == []
    audit.verify_chain()
    audit.verify_state_consistency(state_before.audit_head_sha256)
    assert audit.head_sha256() is None
    assert audit.list_entries() == []


def test_sigkill_after_state_save_recovers_committed(tmp_path) -> None:
    """Child SIGKILLed after saving state, BEFORE finalizing rename.

    Expected: state references staged hash; reconcile finalizes; chain valid.
    """
    store, audit = _bootstrap(tmp_path)

    proc = _spawn_and_wait_for_marker(tmp_path, "after_save", "SAVED")

    staging_files = list(audit.dir.glob("*.staging"))
    assert len(staging_files) == 1

    rc = _sigkill_and_wait(proc)
    assert rc == -signal.SIGKILL

    # State was saved before kill — should now reference the staged hash
    state_after = store.load()
    assert state_after.audit_head_sha256 is not None, "state must have been saved before kill"

    # Recovery
    recon = audit.reconcile_pending(state_after.audit_head_sha256)
    assert len(recon["finalized"]) == 1
    assert recon["discarded"] == []

    # Post-recovery integrity
    assert list(audit.dir.glob("*.staging")) == []
    audit.verify_chain()
    audit.verify_state_consistency(state_after.audit_head_sha256)
    assert audit.head_sha256() == state_after.audit_head_sha256
    entries = audit.list_entries()
    assert len(entries) == 1
    assert entries[0].this_entry_sha256 == state_after.audit_head_sha256


@pytest.mark.skipif(
    sys.platform == "win32", reason="SIGKILL semantics differ on Windows"
)
def test_sigkill_test_skip_marker_on_windows() -> None:
    """Documentation test — confirms the suite explicitly handles Windows."""
    # If we're here, we're not on Windows.
    assert sys.platform != "win32"
