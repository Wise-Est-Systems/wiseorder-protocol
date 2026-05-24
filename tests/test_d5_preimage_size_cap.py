"""Tests for v0.2.0 invariant D6 — preimage size cap on Class D commit stages.

D6 (proposed in SPEC_LOCK_v0.2.0 §2.5, draft in
work_orders/D5-SIZE-CAP-spec-patch.md) narrows D5 by requiring conformant
verifiers to reject any Class D artifact whose commit-chain stage carries a
canonical-JSON preimage `content` larger than 1 MiB (per-stage) or whose total
preimage size exceeds 4 MiB (per-artifact). Rejection status is
`CONDUCT_INVALID`; reason code is `PREIMAGE_OVERSIZED`.

The verifier in `tools/minimal_verifier.py` does NOT yet enforce D6. Several
assertions in this module are therefore expected to FAIL until a follow-up
work order lands the enforcement. The failures are the spec-vs-code gap; they
are tracked, not hidden.

The vector-shape and structural assertions DO pass today and are kept here so
the file is exercised by `pytest` in its current state.
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

import minimal_verifier  # noqa: E402

VECTOR_PATH = REPO_ROOT / "vectors" / "v0.2.0" / "class-d-preimage-oversized.json"
PER_STAGE_CAP_BYTES = 1_048_576  # 1 MiB
PER_ARTIFACT_CAP_BYTES = 4_194_304  # 4 MiB


def _load_vector() -> dict:
    with VECTOR_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def _canonical_size(value: object) -> int:
    """Canonical JSON byte length: sorted keys, compact separators, UTF-8.

    Matches the measurement rule declared in SPEC_LOCK_v0.2.0 §2.5.
    """
    return len(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )


# --- structural sanity (passes today) -------------------------------------


def test_vector_file_exists():
    assert VECTOR_PATH.is_file(), f"vector missing: {VECTOR_PATH}"


def test_vector_is_v020_class_d():
    v = _load_vector()
    assert v["protocol_version"] == "0.2.0"
    assert v["class"] == "D"
    assert v["vector_id"] == "class-d-preimage-oversized"


def test_vector_expected_status_is_conduct_invalid():
    v = _load_vector()
    assert v["expected_status"] == "CONDUCT_INVALID"


def test_vector_expected_reason_code_present():
    v = _load_vector()
    assert "PREIMAGE_OVERSIZED" in v["expected_reasons_contain"]


def test_vector_stage_2_actually_exceeds_per_stage_cap():
    """The vector must really exercise the cap, not just claim to."""
    v = _load_vector()
    stage2_content = v["input"]["commit_chain"][1]["content"]
    size = _canonical_size(stage2_content)
    assert size > PER_STAGE_CAP_BYTES, (
        f"stage 2 canonical content size {size} bytes is not over the "
        f"{PER_STAGE_CAP_BYTES}-byte per-stage cap; vector does not exercise D6"
    )


def test_vector_artifact_total_would_be_caught_by_per_stage_cap_first():
    """Sanity: the per-stage violation is what trips this vector, not the
    per-artifact cap. Keeps the vector single-purposed."""
    v = _load_vector()
    chain = v["input"]["commit_chain"]
    total = sum(_canonical_size(s["content"]) for s in chain)
    assert total <= PER_ARTIFACT_CAP_BYTES, (
        f"vector total preimage {total} bytes also exceeds per-artifact cap "
        f"{PER_ARTIFACT_CAP_BYTES}; rewrite vector to isolate per-stage failure"
    )


# --- D6 enforcement (will FAIL until verifier lands the cap) ---------------


def test_verifier_rejects_oversized_preimage_as_conduct_invalid():
    v = _load_vector()
    verdict = minimal_verifier.verify_class_d(v["input"])
    assert verdict.status == "CONDUCT_INVALID", (
        f"D6 violation must produce CONDUCT_INVALID; got {verdict.status!r}. "
        f"reasons={verdict.reasons!r}"
    )


def test_verifier_emits_preimage_oversized_reason_code():
    v = _load_vector()
    verdict = minimal_verifier.verify_class_d(v["input"])
    joined = " ".join(verdict.reasons or [])
    assert "PREIMAGE_OVERSIZED" in joined, (
        f"D6 rejection must include reason code PREIMAGE_OVERSIZED; "
        f"reasons={verdict.reasons!r}"
    )
