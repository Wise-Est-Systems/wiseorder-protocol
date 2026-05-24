"""Structural sanity + verifier-enforcement tests for v0.2.0 attester identity
and signature binding (WO-IDENTITY-MODEL, SPEC_LOCK_v0.2.0 §2.7).

Two layers:

  Layer 1 — STRUCTURAL SANITY (passes today).
    Vectors exist, parse, declare protocol_version "0.2.0", carry the required
    Attester identity object (kid + pubkey), and carry signatures with the
    correct length/encoding. kid is verified to equal SHA-256(pubkey)[:16]
    base64url (C7) using only the standard library.

  Layer 2 — VERIFIER ENFORCEMENT (xfail strict).
    Verifier tracks do not yet implement Ed25519 verification. Tests that
    require signature verification are marked @pytest.mark.xfail(strict=True).
    Follow-up WO will flip these.

v0.1.0 vectors and verifier behavior are untouched.
"""

from __future__ import annotations

import base64
import hashlib
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
TOOLS = REPO_ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

V020_VECTORS_DIR = REPO_ROOT / "vectors" / "v0.2.0"

# RFC 8032 §7.1 Test-1 pubkey (raw bytes hex). Used to verify kid is derived
# correctly. We do NOT need a crypto library to check kid derivation — it is
# just a hash.
RFC8032_TEST1_PUBKEY_HEX = (
    "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a"
)
EXPECTED_KID = "If4x36FUomFia_hUBG_SJw"
EXPECTED_PUBKEY_B64URL = "11qYAYKxCrfVS_7TyWQHOg7hcvPapiMlrwIaaPcHURo"


def _b64url_decode(s: str) -> bytes:
    padding = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + padding)


def _load(name: str) -> dict:
    return json.loads((V020_VECTORS_DIR / f"{name}.json").read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Layer 1 — Structural sanity. Passes today.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "vector_id",
    [
        "class-c-valid-signed-attestation",
        "class-c-invalid-signature",
    ],
)
def test_vector_is_v020_class_c(vector_id: str):
    v = _load(vector_id)
    assert v["vector_id"] == vector_id
    assert v["protocol_version"] == "0.2.0"
    assert v["class"] == "C"


@pytest.mark.parametrize(
    "vector_id",
    [
        "class-c-valid-signed-attestation",
        "class-c-invalid-signature",
    ],
)
def test_eligible_attesters_are_identity_objects(vector_id: str):
    v = _load(vector_id)
    attesters = v["input"]["protocol"]["eligible_attesters"]
    assert isinstance(attesters, list) and len(attesters) >= 1
    for a in attesters:
        assert isinstance(a, dict), "v0.2.0 attesters must be objects, not strings"
        assert "kid" in a and "pubkey" in a


@pytest.mark.parametrize(
    "vector_id",
    [
        "class-c-valid-signed-attestation",
        "class-c-invalid-signature",
    ],
)
def test_pubkey_decodes_to_32_bytes(vector_id: str):
    v = _load(vector_id)
    pk_b64 = v["input"]["protocol"]["eligible_attesters"][0]["pubkey"]
    raw = _b64url_decode(pk_b64)
    assert len(raw) == 32, f"Ed25519 pubkey must be 32 bytes; got {len(raw)}"


@pytest.mark.parametrize(
    "vector_id",
    [
        "class-c-valid-signed-attestation",
        "class-c-invalid-signature",
    ],
)
def test_signature_decodes_to_64_bytes(vector_id: str):
    v = _load(vector_id)
    sig_b64 = v["input"]["evidence"][0]["signature"]
    raw = _b64url_decode(sig_b64)
    assert len(raw) == 64, f"Ed25519 signature must be 64 bytes; got {len(raw)}"


@pytest.mark.parametrize(
    "vector_id",
    [
        "class-c-valid-signed-attestation",
        "class-c-invalid-signature",
    ],
)
def test_kid_derivation_matches_c7(vector_id: str):
    """C7: kid MUST equal SHA-256(pubkey_raw)[:16] URL-safe base64 no-pad."""
    v = _load(vector_id)
    attester = v["input"]["protocol"]["eligible_attesters"][0]
    pk_raw = _b64url_decode(attester["pubkey"])
    expected_kid_bytes = hashlib.sha256(pk_raw).digest()[:16]
    expected_kid = base64.urlsafe_b64encode(expected_kid_bytes).rstrip(b"=").decode("ascii")
    assert attester["kid"] == expected_kid, (
        f"C7 kid mismatch: declared {attester['kid']!r}, derived {expected_kid!r}"
    )


def test_attester_kid_matches_eligible_kid_c6():
    """C6: evidence[*].attester_kid MUST equal an eligible_attesters[*].kid."""
    v = _load("class-c-valid-signed-attestation")
    eligible_kids = {a["kid"] for a in v["input"]["protocol"]["eligible_attesters"]}
    for ev in v["input"]["evidence"]:
        assert ev["attester_kid"] in eligible_kids, (
            f"attester_kid {ev['attester_kid']!r} not in eligible set {eligible_kids}"
        )


def test_test1_keypair_matches_rfc8032():
    """Sanity: the vectors use the RFC 8032 §7.1 Test-1 keypair as declared."""
    v = _load("class-c-valid-signed-attestation")
    attester = v["input"]["protocol"]["eligible_attesters"][0]
    assert attester["pubkey"] == EXPECTED_PUBKEY_B64URL
    assert attester["kid"] == EXPECTED_KID
    raw = _b64url_decode(attester["pubkey"])
    assert raw.hex() == RFC8032_TEST1_PUBKEY_HEX


def test_valid_and_invalid_signatures_differ_by_one_byte():
    """The invalid-signature vector MUST differ from the valid one in exactly
    the first byte by XOR 0x01. Otherwise the test is not a clean bit-flip
    adversarial case."""
    valid_sig = _b64url_decode(
        _load("class-c-valid-signed-attestation")["input"]["evidence"][0]["signature"]
    )
    invalid_sig = _b64url_decode(
        _load("class-c-invalid-signature")["input"]["evidence"][0]["signature"]
    )
    assert len(valid_sig) == len(invalid_sig) == 64
    assert valid_sig[1:] == invalid_sig[1:], "signatures must differ only in byte 0"
    assert valid_sig[0] ^ invalid_sig[0] == 0x01, "byte 0 must differ by exactly XOR 0x01"


def test_invalid_signature_vector_expects_signature_verify_failed():
    v = _load("class-c-invalid-signature")
    assert v["expected_status"] == "INVALID"
    assert "SIGNATURE_VERIFY_FAILED" in v["expected_reasons_contain"]


# ---------------------------------------------------------------------------
# Layer 2 — Verifier enforcement. xfail(strict=True) until verifier learns
# C5/C6/C7. Each test calls into minimal_verifier and asserts the verifier
# emits the right outcome.
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    strict=True,
    reason="C5 Ed25519 verification not yet implemented in minimal_verifier; pending follow-up WO",
)
def test_verifier_rejects_invalid_signature():
    import minimal_verifier

    v = _load("class-c-invalid-signature")
    verdict = minimal_verifier.verify_class_c(v["input"])
    assert verdict.status == "INVALID"
    assert any("SIGNATURE_VERIFY_FAILED" in r for r in verdict.reasons), (
        f"expected SIGNATURE_VERIFY_FAILED; got reasons={verdict.reasons}"
    )


@pytest.mark.xfail(
    strict=True,
    reason="C5 Ed25519 verification not yet implemented in minimal_verifier; pending follow-up WO",
)
def test_verifier_accepts_valid_signature():
    import minimal_verifier

    v = _load("class-c-valid-signed-attestation")
    verdict = minimal_verifier.verify_class_c(v["input"])
    assert verdict.status == "CONSENSUS_VALID", (
        f"expected CONSENSUS_VALID with real signature; got {verdict.status}, "
        f"reasons={verdict.reasons}"
    )


@pytest.mark.xfail(
    strict=True,
    reason="C6 attester_kid check vs eligible_attesters[*].kid not yet implemented; pending follow-up WO",
)
def test_verifier_rejects_unknown_attester_kid():
    import minimal_verifier

    v = _load("class-c-valid-signed-attestation")
    art = json.loads(json.dumps(v["input"]))  # deep copy
    art["evidence"][0]["attester_kid"] = "AAAAAAAAAAAAAAAAAAAAAA"
    verdict = minimal_verifier.verify_class_c(art)
    assert verdict.status == "INVALID"
    assert any("UNAUTHORIZED_ATTESTER_KID" in r for r in verdict.reasons)
