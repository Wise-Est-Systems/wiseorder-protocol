"""Structural sanity + verifier-enforcement tests for the v0.2.0 Class B state
machine (WO-CLASS-B-STATE-MACHINE, SPEC_LOCK_v0.2.0 §2.6).

Two layers:

  Layer 1 — STRUCTURAL SANITY (passes today).
    The three v0.2.0 vectors under vectors/v0.2.0/ exist, parse as JSON,
    declare protocol_version == "0.2.0" and class == "B", and carry the
    required transition fields. These tests do NOT depend on the verifier.

  Layer 2 — VERIFIER ENFORCEMENT (xfail strict).
    The minimal verifier has not yet learned the new B4-B7 rules. Tests that
    exercise the new rules are marked @pytest.mark.xfail(strict=True). When
    a follow-up work order teaches the verifier, these flip and strict=True
    forces the xfail markers to be removed.

v0.1.0 vectors and verifier behavior are untouched.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
TOOLS = REPO_ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

V020_VECTORS_DIR = REPO_ROOT / "vectors" / "v0.2.0"

REQUIRED_TRANSITION_FIELDS = (
    "prior_status",
    "transition_reason",
    "prior_artifact_hash",
)

ALLOWED_PRIOR_STATUSES = {
    "SUPPORTED",
    "CONFLICTED",
    "INSUFFICIENT_EVIDENCE",
    "INVALID",
}

ALLOWED_TRANSITIONS = {
    ("INSUFFICIENT_EVIDENCE", "SUPPORTED"),
    ("INSUFFICIENT_EVIDENCE", "CONFLICTED"),
    ("CONFLICTED", "SUPPORTED"),
    ("SUPPORTED", "CONFLICTED"),
}

POSITIVE_REASON_CODES = {
    "NEW_EVIDENCE_REACHED_THRESHOLD",
    "NEW_EVIDENCE_INTRODUCED_CONFLICT",
    "CONTRADICTING_SOURCE_RETRACTED",
}

REJECTION_REASON_CODES = {
    "INVALID_TERMINAL_TRANSITION",
    "TRANSITION_REASON_MISSING",
    "PRIOR_STATUS_MISSING",
    "DISALLOWED_STATE_TRANSITION",
    "PRIOR_ARTIFACT_HASH_MISSING",
}


def _load(name: str) -> dict:
    path = V020_VECTORS_DIR / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Layer 1 — Structural sanity. These pass today.
# ---------------------------------------------------------------------------


def test_v020_vectors_dir_exists():
    assert V020_VECTORS_DIR.is_dir(), (
        f"vectors/v0.2.0/ must exist; got {V020_VECTORS_DIR}"
    )


@pytest.mark.parametrize(
    "vector_id",
    [
        "class-b-transition-insufficient-to-supported",
        "class-b-transition-conflicted-to-supported",
        "class-b-transition-invalid-is-terminal",
    ],
)
def test_vector_file_exists_and_is_json(vector_id: str):
    path = V020_VECTORS_DIR / f"{vector_id}.json"
    assert path.is_file(), f"missing vector: {path}"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["vector_id"] == vector_id
    assert data["protocol_version"] == "0.2.0"
    assert data["class"] == "B"


@pytest.mark.parametrize(
    "vector_id",
    [
        "class-b-transition-insufficient-to-supported",
        "class-b-transition-conflicted-to-supported",
        "class-b-transition-invalid-is-terminal",
    ],
)
def test_vector_declares_transition_fields(vector_id: str):
    data = _load(vector_id)
    inp = data["input"]
    for field in REQUIRED_TRANSITION_FIELDS:
        assert field in inp, f"{vector_id}: missing transition field {field}"
    assert inp["prior_status"] in ALLOWED_PRIOR_STATUSES, (
        f"{vector_id}: prior_status {inp['prior_status']!r} not in allowed set"
    )
    assert isinstance(inp["transition_reason"], dict)
    assert "code" in inp["transition_reason"]
    assert "narrative" in inp["transition_reason"]
    assert isinstance(inp["prior_artifact_hash"], str)
    assert len(inp["prior_artifact_hash"]) == 64


def test_insufficient_to_supported_is_allowed_pair():
    data = _load("class-b-transition-insufficient-to-supported")
    pair = (data["input"]["prior_status"], data["expected_status"])
    assert pair in ALLOWED_TRANSITIONS, f"pair {pair} not in allowed set"
    assert data["input"]["transition_reason"]["code"] in POSITIVE_REASON_CODES
    assert data["expected_reasons_contain"] == []


def test_conflicted_to_supported_is_allowed_pair():
    data = _load("class-b-transition-conflicted-to-supported")
    pair = (data["input"]["prior_status"], data["expected_status"])
    assert pair in ALLOWED_TRANSITIONS, f"pair {pair} not in allowed set"
    assert data["input"]["transition_reason"]["code"] in POSITIVE_REASON_CODES
    assert data["expected_reasons_contain"] == []


def test_invalid_terminal_expects_rejection_code():
    data = _load("class-b-transition-invalid-is-terminal")
    assert data["input"]["prior_status"] == "INVALID"
    assert data["expected_status"] == "INVALID"
    assert "INVALID_TERMINAL_TRANSITION" in data["expected_reasons_contain"]
    assert "INVALID_TERMINAL_TRANSITION" in REJECTION_REASON_CODES


def test_evidence_preservation_in_conflicted_to_supported():
    """The CONFLICTED->SUPPORTED vector MUST preserve the contradicting
    observation rather than delete it (§2.6.5 / B2 extension)."""
    data = _load("class-b-transition-conflicted-to-supported")
    observations = data["input"]["observations"]
    retracted = [o for o in observations if o.get("retracted") is True]
    assert retracted, (
        "CONFLICTED->SUPPORTED vector MUST keep the retracted observation "
        "visible, not delete it; B2 extension"
    )


# ---------------------------------------------------------------------------
# Layer 2 — Verifier enforcement. xfail(strict=True) until verifier learns
# the new rules. Each test imports the live minimal_verifier and asserts the
# new B4-B7 semantics. They will xpass once a follow-up WO ships the rules,
# at which point xfail must be removed.
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    strict=True,
    reason="B4 not yet enforced by minimal_verifier; pending follow-up WO",
)
def test_verifier_rejects_transition_out_of_invalid():
    import minimal_verifier

    art = _load("class-b-transition-invalid-is-terminal")["input"]
    verdict = minimal_verifier.verify_class_b(art)
    assert verdict.status == "INVALID"
    assert any(
        "INVALID_TERMINAL_TRANSITION" in r for r in verdict.reasons
    ), f"expected INVALID_TERMINAL_TRANSITION; got reasons={verdict.reasons}"


@pytest.mark.xfail(
    strict=True,
    reason="B5 not yet enforced by minimal_verifier; pending follow-up WO",
)
def test_verifier_rejects_missing_prior_status_when_transition_implied():
    import minimal_verifier

    art = _load("class-b-transition-insufficient-to-supported")["input"]
    art_bad = dict(art)
    del art_bad["prior_status"]
    verdict = minimal_verifier.verify_class_b(art_bad)
    assert verdict.status == "INVALID"
    assert any("PRIOR_STATUS_MISSING" in r for r in verdict.reasons)


@pytest.mark.xfail(
    strict=True,
    reason="B5 not yet enforced by minimal_verifier; pending follow-up WO",
)
def test_verifier_rejects_missing_transition_reason():
    import minimal_verifier

    art = _load("class-b-transition-insufficient-to-supported")["input"]
    art_bad = dict(art)
    del art_bad["transition_reason"]
    verdict = minimal_verifier.verify_class_b(art_bad)
    assert verdict.status == "INVALID"
    assert any("TRANSITION_REASON_MISSING" in r for r in verdict.reasons)


@pytest.mark.xfail(
    strict=True,
    reason="B7 not yet enforced by minimal_verifier; pending follow-up WO",
)
def test_verifier_rejects_missing_prior_artifact_hash():
    import minimal_verifier

    art = _load("class-b-transition-conflicted-to-supported")["input"]
    art_bad = dict(art)
    del art_bad["prior_artifact_hash"]
    verdict = minimal_verifier.verify_class_b(art_bad)
    assert verdict.status == "INVALID"
    assert any("PRIOR_ARTIFACT_HASH_MISSING" in r for r in verdict.reasons)


@pytest.mark.xfail(
    strict=True,
    reason="Allowed-transition acceptance not yet enforced by minimal_verifier",
)
def test_verifier_accepts_insufficient_to_supported_allowed_transition():
    import minimal_verifier

    art = _load("class-b-transition-insufficient-to-supported")["input"]
    verdict = minimal_verifier.verify_class_b(art)
    assert verdict.status == "SUPPORTED", (
        f"INSUFFICIENT_EVIDENCE->SUPPORTED with affirming new source and no "
        f"contradiction MUST be SUPPORTED; got {verdict.status}, "
        f"reasons={verdict.reasons}"
    )


@pytest.mark.xfail(
    strict=True,
    reason="Allowed-transition acceptance not yet enforced by minimal_verifier",
)
def test_verifier_accepts_conflicted_to_supported_when_source_retracted():
    import minimal_verifier

    art = _load("class-b-transition-conflicted-to-supported")["input"]
    verdict = minimal_verifier.verify_class_b(art)
    assert verdict.status == "SUPPORTED", (
        f"CONFLICTED->SUPPORTED with retracted source MUST be SUPPORTED; got "
        f"{verdict.status}, reasons={verdict.reasons}"
    )
