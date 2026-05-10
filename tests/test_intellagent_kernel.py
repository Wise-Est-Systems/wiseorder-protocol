"""Tests for intellagent_runtime.kernel."""

from __future__ import annotations

import copy
from typing import Any

from intellagent_runtime.kernel import WiseOrderKernel
from intellagent_runtime.state import EpistemicState, compute_state_id
from intellagent_runtime.transitions import (
    Action,
    Authorization,
    EpistemicTransition,
)


HEX64_A = "a" * 64
HEX64_B = "b" * 64


def _initial_state() -> EpistemicState:
    return EpistemicState(
        state_id=compute_state_id([]),
        objects=[],
        audit_head_sha256=None,
        sealed_at="2026-05-06T12:00:00Z",
    )


def _mk_transition(
    regime: str,
    obj: dict[str, Any],
    *,
    from_state: str | None = None,
    action: Action | None = None,
    authorization: Authorization | None = None,
) -> EpistemicTransition:
    return EpistemicTransition(
        transition_id="t-" + regime,
        from_state=from_state if from_state is not None else compute_state_id([]),
        regime=regime,
        object_added=obj,
        objects_removed=[],
        action=action,
        authorization=authorization,
        proposer="test",
        proposed_at="2026-05-06T12:00:00Z",
    )


# ---------------------------------------------------------------------------
# Class A
# ---------------------------------------------------------------------------


def _good_class_a() -> dict[str, Any]:
    return {
        "class": "A",
        "regime": "deterministic_verification",
        "claim": "test",
        "canonicalization": "RFC8785-JCS",
        "algorithm": "SHA-256",
        "expected_digest": f"sha256:{HEX64_A}",
        "observed_digest": f"sha256:{HEX64_A}",
        "status": "VERIFIED",
    }


def test_class_a_valid_passes() -> None:
    k = WiseOrderKernel()
    v = k.verify(_mk_transition("A", _good_class_a()), _initial_state())
    assert v.passed, v.failures


def test_class_a_verified_with_mismatched_digests_fails() -> None:
    obj = _good_class_a()
    obj["observed_digest"] = f"sha256:{HEX64_B}"
    v = WiseOrderKernel().verify(_mk_transition("A", obj), _initial_state())
    assert not v.passed
    assert any("VERIFIED requires expected_digest == observed_digest" in f for f in v.failures)


def test_class_a_tampered_with_matching_digests_fails() -> None:
    obj = _good_class_a()
    obj["status"] = "TAMPERED"
    v = WiseOrderKernel().verify(_mk_transition("A", obj), _initial_state())
    assert not v.passed
    assert any("TAMPERED requires expected_digest != observed_digest" in f for f in v.failures)


def test_class_a_non_jcs_fails() -> None:
    obj = _good_class_a()
    obj["canonicalization"] = "WISEATA-CANONICAL-V1"
    v = WiseOrderKernel().verify(_mk_transition("A", obj), _initial_state())
    assert not v.passed
    assert any("CS1" in f and "RFC8785-JCS" in f for f in v.failures)


def test_class_a_missing_canonicalization_fails() -> None:
    obj = _good_class_a()
    del obj["canonicalization"]
    v = WiseOrderKernel().verify(_mk_transition("A", obj), _initial_state())
    assert not v.passed
    assert any("CS1" in f for f in v.failures)


def test_class_a_telemetry_status_fails() -> None:
    obj = _good_class_a()
    obj["status"] = "CALIBRATION_IMPROVED"
    v = WiseOrderKernel().verify(_mk_transition("A", obj), _initial_state())
    assert not v.passed
    assert any("telemetry token" in f for f in v.failures)


# ---------------------------------------------------------------------------
# Class B
# ---------------------------------------------------------------------------


def _good_class_b() -> dict[str, Any]:
    return {
        "class": "B",
        "regime": "instrumented_empirical_verification",
        "claim": "test",
        "sources": [{"id": "s1", "kind": "log", "uri": "test://s1"}],
        "timestamps": [{"source_id": "s1", "value": "2026-05-06T12:00:00Z"}],
        "observations": [{"source_id": "s1", "result": "ok", "supports_claim": True}],
        "structural_diff": {},
        "status": "SUPPORTED",
    }


def test_class_b_valid_passes() -> None:
    v = WiseOrderKernel().verify(_mk_transition("B", _good_class_b()), _initial_state())
    assert v.passed, v.failures


def test_class_b_conflicted_requires_both_sides() -> None:
    obj = _good_class_b()
    obj["status"] = "CONFLICTED"
    # Only supports_claim=True — missing the False side; B2 should fire.
    v = WiseOrderKernel().verify(_mk_transition("B", obj), _initial_state())
    assert not v.passed
    assert any("B2" in f for f in v.failures)


# ---------------------------------------------------------------------------
# Class C
# ---------------------------------------------------------------------------


def _good_class_c() -> dict[str, Any]:
    return {
        "class": "C",
        "regime": "protocol_bound_consensus",
        "claim": "test",
        "protocol": {
            "name": "test",
            "version": "0.1.0",
            "required_quorum": 2,
            "eligible_attesters": ["a", "b", "c"],
        },
        "evidence": [
            {"attester_id": "a", "attestation": "approve", "eligible": True},
            {"attester_id": "b", "attestation": "approve", "eligible": True},
        ],
        "action_policy": {
            "action_allowed": False,
            "action_compelled": False,
            "reason": "consensus is not authorization (AG1)",
        },
        "status": "CONSENSUS_VALID",
    }


def test_class_c_valid_passes() -> None:
    v = WiseOrderKernel().verify(_mk_transition("C", _good_class_c()), _initial_state())
    assert v.passed, v.failures


def test_class_c_unauthorized_attester_requires_invalid() -> None:
    obj = _good_class_c()
    obj["evidence"].append(
        {"attester_id": "rogue", "attestation": "approve", "eligible": False}
    )
    # status remains CONSENSUS_VALID → C2 should fire
    v = WiseOrderKernel().verify(_mk_transition("C", obj), _initial_state())
    assert not v.passed
    assert any("C2" in f and "rogue" in f for f in v.failures)


def test_class_c_action_allowed_without_source_fails() -> None:
    obj = _good_class_c()
    obj["action_policy"] = {
        "action_allowed": True,
        "action_compelled": False,
        "reason": "tries to lift consensus to authorization",
    }
    v = WiseOrderKernel().verify(_mk_transition("C", obj), _initial_state())
    assert not v.passed
    assert any("AG1" in f for f in v.failures)


# ---------------------------------------------------------------------------
# Class D
# ---------------------------------------------------------------------------


def _good_class_d() -> dict[str, Any]:
    return {
        "class": "D",
        "regime": "interpretive_governance",
        "claim": "test",
        "values_frame": {
            "optimizing_for": ["a"],
            "not_optimizing_for": ["b"],
        },
        "alternatives": [{"id": "alt-1", "summary": "x"}],
        "challenge_surface": [{"id": "ch-1", "argument": "y"}],
        "commit_chain": [
            {
                "stage": 1,
                "name": "values_frame_commit",
                "hash": f"sha256:{HEX64_A}",
                "content": {"x": 1},
                "depends_on": None,
                "created_at": "2026-05-06T12:00:00Z",
            }
        ],
        "status": "CONDUCT_VALID",
    }


def test_class_d_valid_passes() -> None:
    v = WiseOrderKernel().verify(_mk_transition("D", _good_class_d()), _initial_state())
    assert v.passed, v.failures


def test_class_d_empty_alternatives_fails() -> None:
    obj = _good_class_d()
    obj["alternatives"] = []
    v = WiseOrderKernel().verify(_mk_transition("D", obj), _initial_state())
    assert not v.passed
    assert any("D2" in f for f in v.failures)


def test_class_d_empty_challenge_fails() -> None:
    obj = _good_class_d()
    obj["challenge_surface"] = []
    v = WiseOrderKernel().verify(_mk_transition("D", obj), _initial_state())
    assert not v.passed
    assert any("D3" in f for f in v.failures)


def test_class_d_status_verified_fails() -> None:
    obj = _good_class_d()
    obj["status"] = "VERIFIED"
    v = WiseOrderKernel().verify(_mk_transition("D", obj), _initial_state())
    assert not v.passed
    assert any("D4" in f for f in v.failures)


def test_class_d_missing_preimage_fails() -> None:
    obj = _good_class_d()
    obj["commit_chain"][0]["content"] = None
    v = WiseOrderKernel().verify(_mk_transition("D", obj), _initial_state())
    assert not v.passed
    assert any("D5" in f or "CC1" in f for f in v.failures)


def test_class_d_broken_depends_on_fails() -> None:
    obj = _good_class_d()
    obj["commit_chain"].append(
        {
            "stage": 2,
            "name": "alternatives_commit",
            "hash": f"sha256:{HEX64_B}",
            "content": {"x": 2},
            "depends_on": "sha256:" + "9" * 64,  # wrong
            "created_at": "2026-05-06T12:00:01Z",
        }
    )
    v = WiseOrderKernel().verify(_mk_transition("D", obj), _initial_state())
    assert not v.passed
    assert any("CC2" in f for f in v.failures)


# ---------------------------------------------------------------------------
# Cross-cutting: AG1 at proposal time
# ---------------------------------------------------------------------------


def test_action_bearing_without_authorization_fails() -> None:
    obj = _good_class_a()
    tau = _mk_transition(
        "A",
        obj,
        action=Action(kind="write_file", target="/tmp/x", payload={}),
        authorization=None,  # AG1 violation
    )
    v = WiseOrderKernel().verify(tau, _initial_state())
    assert not v.passed
    assert any("AG1" in f for f in v.failures)


def test_from_state_mismatch_fails() -> None:
    obj = _good_class_a()
    tau = _mk_transition("A", obj, from_state="sha256:" + "0" * 64)
    v = WiseOrderKernel().verify(tau, _initial_state())
    assert not v.passed
    assert any("from_state" in f for f in v.failures)
