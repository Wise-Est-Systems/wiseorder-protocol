"""Tests for intellagent_runtime.runtime (search loop and apply_transition)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from intellagent_runtime import canonical
from intellagent_runtime.authorization import AuthorizationGate
from intellagent_runtime.kernel import WiseOrderKernel
from intellagent_runtime.proposer import InMemoryProposer
from intellagent_runtime.runtime import Query, RuntimeLoop
from intellagent_runtime.state import StateStore, compute_state_id
from intellagent_runtime.transitions import (
    Action,
    Authorization,
    EpistemicTransition,
)


HEX64_A = "a" * 64


def _setup_runtime(tmp_path: Path) -> RuntimeLoop:
    store = StateStore(tmp_path)
    store.init()
    pol = tmp_path / "policies"
    pol.mkdir()
    (pol / "test_allowlist.json").write_text(json.dumps({
        "source_id": "test_allowlist",
        "kind": "allowlist",
        "rationale": "test",
        "allowed": [{"kind": "log", "target": "any"}],
    }), encoding="utf-8")
    return RuntimeLoop(tmp_path, WiseOrderKernel(), AuthorizationGate(pol))


def _good_class_a_transition(state_id: str, tid: str = "t-a-1") -> EpistemicTransition:
    return EpistemicTransition(
        transition_id=tid,
        from_state=state_id,
        regime="A",
        object_added={
            "class": "A",
            "regime": "deterministic_verification",
            "claim": "demo",
            "canonicalization": "RFC8785-JCS",
            "algorithm": "SHA-256",
            "expected_digest": f"sha256:{HEX64_A}",
            "observed_digest": f"sha256:{HEX64_A}",
            "status": "VERIFIED",
        },
        objects_removed=[],
        action=None,
        authorization=None,
        proposer="test",
        proposed_at="2026-05-06T12:00:00Z",
    )


def test_satisfiable_query_commits_one_transition(tmp_path: Path) -> None:
    rt = _setup_runtime(tmp_path)
    state = rt.store.load()
    tau = _good_class_a_transition(state.state_id)
    proposer = InMemoryProposer("inmem", [tau])
    query = Query("state has at least one object", lambda s: len(s.objects) > 0)

    result = rt.search(query, proposer)
    assert result.satisfied
    assert result.refusal is None
    assert result.audit_head is not None
    assert len(rt.audit.list_entries()) == 1


def test_empty_proposer_yields_refusal(tmp_path: Path) -> None:
    rt = _setup_runtime(tmp_path)
    proposer = InMemoryProposer("empty", [])
    query = Query("never satisfied", lambda s: False)
    result = rt.search(query, proposer)
    assert not result.satisfied
    assert result.refusal is not None
    assert result.refusal.candidates_rejected
    # The refusal must record at least the no-candidates marker.
    assert any(
        "proposer_returned_no_candidates" in f
        for entry in result.refusal.candidates_rejected
        for f in entry["legitimacy_failures"]
    )


def test_all_rejected_yields_refusal_with_full_challenge_surface(tmp_path: Path) -> None:
    rt = _setup_runtime(tmp_path)
    state = rt.store.load()
    bad_d = EpistemicTransition(
        transition_id="t-bad-d",
        from_state=state.state_id,
        regime="D",
        object_added={
            "class": "D",
            "regime": "interpretive_governance",
            "claim": "bad",
            "values_frame": {"optimizing_for": ["x"], "not_optimizing_for": ["y"]},
            "alternatives": [],         # D2 violation
            "challenge_surface": [],    # D3 violation
            "commit_chain": [],         # CC3 violation
            "status": "CONDUCT_VALID",
        },
        objects_removed=[],
        action=None,
        authorization=None,
        proposer="test",
        proposed_at="2026-05-06T12:00:00Z",
    )
    proposer = InMemoryProposer("bad", [bad_d])
    query = Query("never satisfied", lambda s: False)

    result = rt.search(query, proposer)
    assert not result.satisfied
    assert result.refusal is not None
    failures_flat = [
        f for entry in result.refusal.candidates_rejected
        for f in entry["legitimacy_failures"]
    ]
    assert any("D2" in f for f in failures_flat)
    assert any("D3" in f for f in failures_flat)


def test_max_iters_zero_returns_budget_exhausted_refusal(tmp_path: Path) -> None:
    rt = _setup_runtime(tmp_path)
    proposer = InMemoryProposer("never-called", [])
    query = Query("always unsat", lambda s: False)
    result = rt.search(query, proposer, max_iters=0)
    assert not result.satisfied
    assert result.refusal is not None
    assert any(
        "budget_exhausted" in f
        for entry in result.refusal.candidates_rejected
        for f in entry["legitimacy_failures"]
    )


def test_action_bearing_with_allowlist_is_committed(tmp_path: Path) -> None:
    rt = _setup_runtime(tmp_path)
    state = rt.store.load()
    tau = EpistemicTransition(
        transition_id="t-a-action",
        from_state=state.state_id,
        regime="A",
        object_added={
            "class": "A",
            "regime": "deterministic_verification",
            "claim": "act-bearing",
            "canonicalization": "RFC8785-JCS",
            "algorithm": "SHA-256",
            "expected_digest": f"sha256:{HEX64_A}",
            "observed_digest": f"sha256:{HEX64_A}",
            "status": "VERIFIED",
        },
        objects_removed=[],
        action=Action(kind="log", target="any", payload={}),
        authorization=Authorization(source_id="test_allowlist", rationale="test"),
        proposer="test",
        proposed_at="2026-05-06T12:00:00Z",
    )
    proposer = InMemoryProposer("act", [tau])
    query = Query("state has at least one object", lambda s: len(s.objects) > 0)
    result = rt.search(query, proposer)
    assert result.satisfied, (
        result.refusal.to_dict() if result.refusal else "no refusal but not satisfied"
    )


def test_action_bearing_without_authorization_is_refused(tmp_path: Path) -> None:
    """AG1: kernel rejects the transition before the gate ever runs."""
    rt = _setup_runtime(tmp_path)
    state = rt.store.load()
    tau = EpistemicTransition(
        transition_id="t-a-noauth",
        from_state=state.state_id,
        regime="A",
        object_added={
            "class": "A",
            "regime": "deterministic_verification",
            "claim": "act-bearing-noauth",
            "canonicalization": "RFC8785-JCS",
            "algorithm": "SHA-256",
            "expected_digest": f"sha256:{HEX64_A}",
            "observed_digest": f"sha256:{HEX64_A}",
            "status": "VERIFIED",
        },
        objects_removed=[],
        action=Action(kind="log", target="any", payload={}),
        authorization=None,  # AG1 violation
        proposer="test",
        proposed_at="2026-05-06T12:00:00Z",
    )
    proposer = InMemoryProposer("act", [tau])
    query = Query("never sat", lambda s: False)
    result = rt.search(query, proposer)
    assert not result.satisfied
    assert result.refusal is not None
    failures_flat = [
        f for entry in result.refusal.candidates_rejected
        for f in entry["legitimacy_failures"]
    ]
    assert any("AG1" in f for f in failures_flat)


def test_deterministic_replay(tmp_path: Path) -> None:
    """Same inputs + fixed clock + fixed id-fn → byte-identical audit memory."""
    fixed_t = 1735689600.0
    fixed_id = iter(["id-0001", "id-0002", "id-0003", "id-0004", "id-0005", "id-0006"])

    def reset_clock_and_ids():
        canonical.set_clock(lambda: fixed_t)
        nonlocal fixed_id
        fixed_id = iter(["id-0001", "id-0002", "id-0003", "id-0004", "id-0005", "id-0006"])
        canonical.set_id_fn(lambda: next(fixed_id))

    def run(dir: Path) -> bytes:
        reset_clock_and_ids()
        rt = _setup_runtime(dir)
        state = rt.store.load()
        tau = _good_class_a_transition(state.state_id)
        proposer = InMemoryProposer("rep", [tau])
        query = Query("state has at least one object", lambda s: len(s.objects) > 0)
        rt.search(query, proposer)
        # Concatenate canonical audit entry bytes
        body = b""
        for path in sorted((dir / "intellagent_audit").glob("*.entry.json")):
            body += path.read_bytes()
        return body

    try:
        a = run(tmp_path / "run-a")
        b = run(tmp_path / "run-b")
    finally:
        canonical.reset_clock()
        canonical.reset_id_fn()

    assert a == b, "deterministic replay failed: audit memories differ"
    assert a, "no entries were produced"
