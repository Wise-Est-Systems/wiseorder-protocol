"""Tests for tools/minimal_verifier.py.

This test module deliberately also asserts the verifier never imports
intellagent_runtime, which would defeat its independent-implementation purpose.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
TOOLS = REPO_ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import minimal_verifier  # noqa: E402


def test_minimal_verifier_does_not_import_intellagent_runtime():
    """The verifier MUST be re-derivable from spec; importing the reference
    runtime would defeat the point of having an independent verifier.

    Note: this is a static (AST) check on minimal_verifier.py source. We do
    not assert against sys.modules because other tests in the same pytest
    session may legitimately import intellagent_runtime."""
    import ast
    src = (TOOLS / "minimal_verifier.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert not alias.name.startswith("intellagent_runtime"), (
                    f"forbidden import: {alias.name}"
                )
        if isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            assert not mod.startswith("intellagent_runtime"), (
                f"forbidden from-import: {mod}"
            )


# --- Class A ---


def _a_base():
    return {
        "class": "A",
        "regime": "deterministic_verification",
        "claim": "x",
        "canonicalization": "RFC8785-JCS",
        "algorithm": "SHA-256",
        "expected_digest": "sha256:" + "a" * 64,
        "observed_digest": "sha256:" + "a" * 64,
        "proof": {"type": "integrity_proof", "created_at": "2026-05-10T11:00:00Z"},
    }


def test_class_a_verified():
    assert minimal_verifier.verify_class_a(_a_base()).status == "VERIFIED"


def test_class_a_tampered():
    art = _a_base()
    art["observed_digest"] = "sha256:" + "b" * 64
    assert minimal_verifier.verify_class_a(art).status == "TAMPERED"


def test_class_a_bad_canonicalization():
    art = _a_base()
    art["canonicalization"] = "RFC8785-JCS-v2"
    assert minimal_verifier.verify_class_a(art).status == "INVALID"


def test_class_a_bad_algorithm():
    art = _a_base()
    art["algorithm"] = "SHA-1"
    art["expected_digest"] = "sha1:abc"
    art["observed_digest"] = "sha1:abc"
    assert minimal_verifier.verify_class_a(art).status == "INVALID"


def test_class_a_missing_field():
    art = _a_base()
    del art["expected_digest"]
    assert minimal_verifier.verify_class_a(art).status == "INVALID"


def test_class_a_telemetry_status_rejected():
    art = _a_base()
    art["status"] = "CALIBRATION_IMPROVED"
    assert minimal_verifier.verify_class_a(art).status == "INVALID"


# --- Class B ---


def _b_base():
    return {
        "class": "B",
        "regime": "instrumented_empirical_verification",
        "claim": "x",
        "sources": [{"id": "src-1", "kind": "log", "uri": "file:///x"}],
        "timestamps": [{"source_id": "src-1", "value": "2026-01-01T00:00:00Z"}],
        "observations": [{"source_id": "src-1", "supports_claim": True}],
        "structural_diff": {},
        "proof": {"type": "empirical_support_record", "created_at": "now"},
    }


def test_class_b_supported():
    assert minimal_verifier.verify_class_b(_b_base()).status == "SUPPORTED"


def test_class_b_conflicted_via_supports_claim():
    art = _b_base()
    art["sources"].append({"id": "src-2", "kind": "log", "uri": "x"})
    art["observations"].append({"source_id": "src-2", "supports_claim": False})
    assert minimal_verifier.verify_class_b(art).status == "CONFLICTED"


def test_class_b_replay_drift():
    art = _b_base()
    art["sources"] = [{"id": "src-1"}, {"id": "src-2"}]
    art["timestamps"] = [
        {"source_id": "src-1", "value": "2026-01-01T00:00:00Z"},
        {"source_id": "src-2", "value": "2026-01-01T00:00:01Z"},
    ]
    art["observations"] = [
        {"source_id": "src-1", "input_digest": "sha256:11", "observed_result_digest": "sha256:aa"},
        {"source_id": "src-2", "input_digest": "sha256:11", "observed_result_digest": "sha256:bb"},
    ]
    assert minimal_verifier.verify_class_b(art).status == "CONFLICTED"


def test_class_b_insufficient_evidence():
    art = _b_base()
    art["observations"] = [{"source_id": "src-1", "supports_claim": None}]
    assert minimal_verifier.verify_class_b(art).status == "INSUFFICIENT_EVIDENCE"


def test_class_b_missing_sources_invalid():
    art = _b_base()
    del art["sources"]
    assert minimal_verifier.verify_class_b(art).status == "INVALID"


def test_class_b_evidence_suppression_invalid():
    art = _b_base()
    art["sources"] = [{"id": "src-1"}, {"id": "src-2"}, {"id": "src-3"}]
    art["timestamps"] = [
        {"source_id": "src-1"}, {"source_id": "src-2"}, {"source_id": "src-3"},
    ]
    art["observations"] = [
        {"source_id": "src-1", "supports_claim": True},
        {"source_id": "src-2", "supports_claim": True},
    ]
    assert minimal_verifier.verify_class_b(art).status == "INVALID"


# --- Class C ---


def _c_base():
    return {
        "class": "C",
        "regime": "protocol_bound_consensus",
        "claim": "x",
        "protocol": {
            "name": "q", "version": "0.1.0", "required_quorum": 2,
            "eligible_attesters": ["a", "b", "c"],
        },
        "evidence": [
            {"attester_id": "a", "attestation": "approve", "eligible": True},
            {"attester_id": "b", "attestation": "approve", "eligible": True},
        ],
        "action_policy": {"action_allowed": False, "action_compelled": False, "reason": ""},
        "proof": {"type": "consensus_process_record", "created_at": "now"},
    }


def test_class_c_consensus_valid():
    assert minimal_verifier.verify_class_c(_c_base()).status == "CONSENSUS_VALID"


def test_class_c_consensus_pending():
    art = _c_base()
    art["evidence"] = art["evidence"][:1]
    assert minimal_verifier.verify_class_c(art).status == "CONSENSUS_PENDING"


def test_class_c_consensus_failed_when_closed_without_quorum():
    art = _c_base()
    art["evidence"] = art["evidence"][:1]
    art["process_closed_at"] = "2026-01-01T00:00:00Z"
    assert minimal_verifier.verify_class_c(art).status == "CONSENSUS_FAILED"


def test_class_c_unauthorized_attester_invalid():
    art = _c_base()
    art["evidence"].append({
        "attester_id": "z", "attestation": "approve", "eligible": True,
    })
    assert minimal_verifier.verify_class_c(art).status == "INVALID"


def test_class_c_replay_invalid():
    art = _c_base()
    art["evidence"] = [
        {"attester_id": "a", "attestation": "approve", "eligible": True},
        {"attester_id": "a", "attestation": "approve", "eligible": True},
    ]
    assert minimal_verifier.verify_class_c(art).status == "INVALID"


def test_class_c_auto_authorize_invalid():
    art = _c_base()
    art["action_policy"] = {"action_allowed": True, "action_compelled": False, "reason": ""}
    assert minimal_verifier.verify_class_c(art).status == "INVALID"


def test_class_c_protocol_version_mismatch_invalid():
    art = _c_base()
    art["protocol"]["version"] = "0.2.0-experimental"
    assert minimal_verifier.verify_class_c(art).status == "INVALID"


def test_class_c_quorum_inflation_invalid():
    art = _c_base()
    art["evidence"] = art["evidence"][:1]
    art["action_policy"] = {
        "action_allowed": True, "action_compelled": False,
        "reason": "x", "authorization_source": "self-declared",
    }
    assert minimal_verifier.verify_class_c(art).status == "INVALID"


# --- Class D ---


def _d_base():
    return {
        "class": "D",
        "regime": "interpretive_governance",
        "claim": "x",
        "values_frame": {"optimizing_for": ["a"], "not_optimizing_for": ["b"]},
        "alternatives": [{"id": "alt-1", "summary": "x", "rejected_because": "y"}],
        "reasoning_trace": [{"step": 1, "claim": "x"}],
        "recommended_action": {"kind": "noop", "summary": "x"},
        "reversibility_score": 0.8,
        "challenge_surface": [{"id": "ch-1", "argument": "x"}],
        "calibration": {"calibration_id": "c", "review_after": "now",
                        "success_signals": [], "failure_signals": []},
        "commit_chain": [
            {"stage": 1, "name": "vf", "hash": "sha256:" + "1" * 64,
             "content": {"x": 1}, "depends_on": None,
             "created_at": "2026-01-01T00:00:00Z"},
            {"stage": 2, "name": "alt", "hash": "sha256:" + "2" * 64,
             "content": {"x": 2}, "depends_on": "sha256:" + "1" * 64,
             "created_at": "2026-01-01T00:00:01Z"},
        ],
        "meta_proof": {"process_status": "CONDUCT_VALID",
                       "artifact_hash": "sha256:" + "f" * 64},
    }


def test_class_d_conduct_valid():
    assert minimal_verifier.verify_class_d(_d_base()).status == "CONDUCT_VALID"


def test_class_d_no_alternatives_invalid():
    art = _d_base()
    art["alternatives"] = []
    assert minimal_verifier.verify_class_d(art).status == "CONDUCT_INVALID"


def test_class_d_no_counterarguments_invalid():
    art = _d_base()
    art["challenge_surface"] = []
    assert minimal_verifier.verify_class_d(art).status == "CONDUCT_INVALID"


def test_class_d_broken_depends_on_invalid():
    art = _d_base()
    art["commit_chain"][1]["depends_on"] = "sha256:" + "9" * 64
    assert minimal_verifier.verify_class_d(art).status == "CONDUCT_INVALID"


def test_class_d_stage_skip_invalid():
    art = _d_base()
    art["commit_chain"][1]["stage"] = 3
    assert minimal_verifier.verify_class_d(art).status == "CONDUCT_INVALID"


def test_class_d_forged_chain_invalid():
    """Identical hash under different content MUST be rejected."""
    art = _d_base()
    h = "sha256:" + "d" * 64
    art["commit_chain"] = [
        {"stage": 1, "name": "vf", "hash": h, "content": {"x": 1},
         "depends_on": None, "created_at": "2026-01-01T00:00:00Z"},
        {"stage": 2, "name": "alt", "hash": h, "content": {"x": 2},
         "depends_on": h, "created_at": "2026-01-01T00:00:01Z"},
    ]
    assert minimal_verifier.verify_class_d(art).status == "CONDUCT_INVALID"


def test_class_d_action_compelled_without_quorum_invalid():
    art = _d_base()
    art["recommended_action"] = {
        "kind": "compelled_irreversible_execution",
        "summary": "x", "compelled": True, "authorization_source": None,
    }
    art["reversibility_score"] = 0.05
    assert minimal_verifier.verify_class_d(art).status == "CONDUCT_INVALID"


def test_class_d_verified_status_rejected():
    art = _d_base()
    art["status"] = "VERIFIED"
    assert minimal_verifier.verify_class_d(art).status == "CONDUCT_INVALID"


def test_class_d_telemetry_rejected():
    art = _d_base()
    art["status"] = "CALIBRATION_IMPROVED"
    assert minimal_verifier.verify_class_d(art).status == "CONDUCT_INVALID"


# --- end-to-end against the real vector suite ---


def test_self_check_returns_zero():
    assert minimal_verifier.self_check() == 0


def test_full_vector_suite_derives_correct_verdicts():
    outcomes = minimal_verifier.check_vectors()
    assert len(outcomes) >= 33
    failures = [o for o in outcomes if not o.passed]
    assert failures == [], f"divergences: {[o.to_dict() for o in failures]}"


def test_cli_check_returns_zero():
    assert minimal_verifier.main(["check", "--quiet"]) == 0


def test_cli_self_check_returns_zero():
    assert minimal_verifier.main(["self-check"]) == 0
