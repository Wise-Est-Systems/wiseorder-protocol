"""Crash-safety tests for ``apply_transition``.

Exercises every crash window in the stage→save→finalize commit flow.
See intellagent_runtime/memory.py and runtime.py module docstrings for the
design and WO-RES-2026-05-24 for the originating audit finding.

Each test simulates a crash by partially executing the commit flow, then
calling ``audit.reconcile_pending(state.audit_head_sha256)`` exactly as the
CLI does at startup. We assert post-recovery integrity invariants:

    I1. ``audit.verify_chain()`` passes.
    I2. ``state.audit_head_sha256 == audit.head_sha256()`` (no divergence).
    I3. No ``*.entry.json.staging`` files remain.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from intellagent_runtime.canonical import (
    canonical_pretty,
    sha256_hex,
    canonical_json_bytes,
    utcnow_iso8601,
    write_atomic,
)
from intellagent_runtime.memory import (
    AuditMemory,
    ChainCorrupt,
    StateAuditDivergence,
    _filename_for,
    _staging_filename_for,
)
from intellagent_runtime.runtime import apply_transition
from intellagent_runtime.state import (
    EpistemicState,
    StateStore,
    compute_state_id,
)
from intellagent_runtime.transitions import (
    Action,
    Authorization,
    EpistemicTransition,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_transition(
    transition_id: str = "t1",
    from_state: str | None = None,
    regime: str = "A",
    object_added: dict | None = None,
) -> EpistemicTransition:
    if object_added is None:
        object_added = {
            "class": "A",
            "canonicalization": "RFC8785-JCS",
            "algorithm": "SHA-256",
            "expected_digest": "sha256:" + "a" * 64,
            "observed_digest": "sha256:" + "a" * 64,
            "status": "VERIFIED",
        }
    return EpistemicTransition(
        transition_id=transition_id,
        from_state=from_state or compute_state_id([]),
        regime=regime,
        object_added=object_added,
        objects_removed=[],
        action=None,
        authorization=None,
        proposer="test",
        proposed_at=utcnow_iso8601(),
    )


def _bootstrap(tmp_path: Path) -> tuple[StateStore, AuditMemory, EpistemicState]:
    """Initialize a runtime root and return its bootstrap state + audit."""
    store = StateStore(tmp_path)
    state = store.init()
    audit = AuditMemory(tmp_path / "intellagent_audit")
    audit.dir.mkdir(parents=True, exist_ok=True)
    return store, audit, state


def _assert_clean(audit: AuditMemory, store: StateStore) -> None:
    """Post-recovery invariants."""
    state = store.load()
    audit.verify_chain()
    audit.verify_state_consistency(state.audit_head_sha256)
    assert not list(audit.dir.glob("*.staging")), "staging files must not survive reconciliation"


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_normal_commit_leaves_no_staging(tmp_path) -> None:
    store, audit, state = _bootstrap(tmp_path)
    tau = _make_transition()
    new_state, entry = apply_transition(tau, state, store, audit)

    # entry on disk at final path; no staging file lingering
    assert (audit.dir / _filename_for(entry.index)).is_file()
    assert not (audit.dir / _staging_filename_for(entry.index)).is_file()
    assert audit.head_sha256() == entry.this_entry_sha256
    assert new_state.audit_head_sha256 == entry.this_entry_sha256

    _assert_clean(audit, store)


def test_two_sequential_commits(tmp_path) -> None:
    store, audit, state = _bootstrap(tmp_path)
    new_state, entry1 = apply_transition(_make_transition("t1"), state, store, audit)
    new_state, entry2 = apply_transition(
        _make_transition(
            "t2",
            from_state=new_state.state_id,
            object_added={
                "class": "A",
                "canonicalization": "RFC8785-JCS",
                "algorithm": "SHA-256",
                "expected_digest": "sha256:" + "b" * 64,
                "observed_digest": "sha256:" + "b" * 64,
                "status": "VERIFIED",
            },
        ),
        new_state, store, audit,
    )
    assert entry2.index == 1
    assert entry2.prev_entry_sha256 == entry1.this_entry_sha256
    _assert_clean(audit, store)


# ---------------------------------------------------------------------------
# Crash A: between stage_entry and store.save
# (state never references staged hash → reconcile must DISCARD)
# ---------------------------------------------------------------------------


def test_crash_after_stage_before_state_save_discards_staging(tmp_path) -> None:
    store, audit, state = _bootstrap(tmp_path)
    tau = _make_transition()
    # Simulate: stage, then process dies before store.save
    entry = audit.stage_entry(
        transition=tau,
        prior_state_id=state.state_id,
        resulting_state_id=compute_state_id(["dummy"]),
    )
    # State on disk still references OLD audit head (None — bootstrap state)
    assert (audit.dir / _staging_filename_for(entry.index)).is_file()
    assert state.audit_head_sha256 is None

    # Recovery: reconcile sees state.audit_head_sha256 != entry.this_entry_sha256
    # and discards the orphan staging file.
    recon = audit.reconcile_pending(state.audit_head_sha256)
    assert recon["finalized"] == []
    assert len(recon["discarded"]) == 1

    _assert_clean(audit, store)
    assert audit.head_sha256() is None
    assert audit.list_entries() == []


# ---------------------------------------------------------------------------
# Crash B: between store.save and finalize_staged
# (state references staged hash → reconcile must FINALIZE)
# ---------------------------------------------------------------------------


def test_crash_after_state_save_before_finalize_recovers(tmp_path) -> None:
    store, audit, state = _bootstrap(tmp_path)
    tau = _make_transition()

    # Stage as apply_transition does
    new_objects: list[str] = []
    if tau.object_added is not None:
        new_objects.append(store.objects.put(tau.object_added))
    new_objects = sorted(new_objects)
    resulting_state_id = compute_state_id(new_objects)

    entry = audit.stage_entry(
        transition=tau,
        prior_state_id=state.state_id,
        resulting_state_id=resulting_state_id,
    )
    # Commit state pointing at the staged hash
    new_state = EpistemicState(
        state_id=resulting_state_id,
        objects=new_objects,
        audit_head_sha256=entry.this_entry_sha256,
        sealed_at=utcnow_iso8601(),
    )
    store.save(new_state)
    # CRASH HERE — finalize_staged is never called

    assert (audit.dir / _staging_filename_for(entry.index)).is_file()
    assert not (audit.dir / _filename_for(entry.index)).is_file()
    loaded = store.load()
    assert loaded.audit_head_sha256 == entry.this_entry_sha256

    # Recovery: reconcile sees state.audit_head matches staged hash → finalize.
    recon = audit.reconcile_pending(loaded.audit_head_sha256)
    assert len(recon["finalized"]) == 1
    assert recon["discarded"] == []

    _assert_clean(audit, store)
    assert audit.head_sha256() == entry.this_entry_sha256
    assert len(audit.list_entries()) == 1


# ---------------------------------------------------------------------------
# Mixed crash: one orphan staging + one valid staging present at the same time
# (a process that crashed twice, or two interrupted attempts at the same index)
# ---------------------------------------------------------------------------


def test_reconcile_handles_mixed_staging_orphans_and_finalizable(tmp_path) -> None:
    store, audit, state = _bootstrap(tmp_path)
    # Stage at index 0 — write but never commit state (orphan)
    orphan_entry = audit.stage_entry(
        transition=_make_transition("orphan"),
        prior_state_id=state.state_id,
        resulting_state_id=compute_state_id(["orphan-result"]),
    )
    # Manually craft a second staging at index 1 that the state DOES reference
    # (simulating a successful state save followed by crash before finalize).
    real_tau = _make_transition("real")
    new_objects = []
    if real_tau.object_added is not None:
        new_objects.append(store.objects.put(real_tau.object_added))
    new_objects = sorted(new_objects)
    resulting_state_id = compute_state_id(new_objects)

    # Index 1, because index 0 is orphan-staged (next_index counts staged)
    second_entry = audit.stage_entry(
        transition=real_tau,
        prior_state_id=state.state_id,
        resulting_state_id=resulting_state_id,
    )
    assert second_entry.index == 1
    new_state = EpistemicState(
        state_id=resulting_state_id,
        objects=new_objects,
        audit_head_sha256=second_entry.this_entry_sha256,
        sealed_at=utcnow_iso8601(),
    )
    store.save(new_state)

    # Recovery
    loaded = store.load()
    recon = audit.reconcile_pending(loaded.audit_head_sha256)
    assert len(recon["finalized"]) == 1
    assert len(recon["discarded"]) == 1

    # But: chain integrity now expects index 0 to exist. The orphan was index 0;
    # the survivor was index 1. After discard, only index 1 exists — chain is
    # GAPPED. verify_chain() should raise.
    # This is correct behavior: a state pointing at a non-zero-index entry
    # with no prior entries on disk IS corrupt. The reconciler does not
    # invent missing entries; it surfaces the inconsistency.
    with pytest.raises(ChainCorrupt):
        audit.verify_chain()


# ---------------------------------------------------------------------------
# State/audit divergence detection
# ---------------------------------------------------------------------------


def test_verify_state_consistency_detects_drift(tmp_path) -> None:
    store, audit, state = _bootstrap(tmp_path)
    tau = _make_transition()
    apply_transition(tau, state, store, audit)
    fresh = store.load()
    # Synthetic drift: pretend state's audit_head is wrong
    audit.verify_state_consistency(fresh.audit_head_sha256)  # ok
    with pytest.raises(StateAuditDivergence):
        audit.verify_state_consistency("sha256:" + "0" * 64)


# ---------------------------------------------------------------------------
# Reconcile on a clean directory is a no-op
# ---------------------------------------------------------------------------


def test_reconcile_no_staging_is_noop(tmp_path) -> None:
    store, audit, state = _bootstrap(tmp_path)
    apply_transition(_make_transition(), state, store, audit)
    recon = audit.reconcile_pending(store.load().audit_head_sha256)
    assert recon == {"finalized": [], "discarded": []}
