"""Tests for tools/validate_vectors.py."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import validate_vectors as vv

REPO_ROOT = Path(__file__).resolve().parent.parent
VECTORS_DIR = REPO_ROOT / "vectors"
SCHEMA = REPO_ROOT / "schemas" / "vector.schema.json"

VALID_A_TEMPLATE: dict = {
    "vector_id": "test-class-a-valid",
    "protocol_version": "0.1.0",
    "class": "A",
    "description": "test fixture",
    "input": {
        "class": "A",
        "regime": "deterministic_verification",
        "claim": "test",
        "canonicalization": "RFC8785-JCS",
        "algorithm": "SHA-256",
        "expected_digest": "sha256:" + "a" * 64,
        "observed_digest": "sha256:" + "a" * 64,
    },
    "expected_status": "VERIFIED",
    "expected_artifact_fields": ["class", "status"],
    "why": "test",
}


def _write_vector(directory: Path, name: str, vec: dict) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{name}.json"
    path.write_text(json.dumps(vec), encoding="utf-8")
    return path


def test_real_suite_passes() -> None:
    results = vv.validate_all(VECTORS_DIR, SCHEMA)
    assert results, "no vectors discovered in repo"
    failures = [(r.vector_id, r.failures) for r in results if not r.passed]
    assert not failures, f"expected all real vectors to pass; failures: {failures}"


def test_class_a_non_jcs_with_verified_fails(tmp_path: Path) -> None:
    bad = copy.deepcopy(VALID_A_TEMPLATE)
    bad["vector_id"] = "test-bad-non-jcs"
    bad["input"]["canonicalization"] = "WISEATA-CANONICAL-V1"
    _write_vector(tmp_path / "vectors", "test-bad-non-jcs", bad)
    results = vv.validate_all(tmp_path / "vectors", SCHEMA)
    assert len(results) == 1 and not results[0].passed
    assert any("rule_class_a_jcs" in f for f in results[0].failures)


def test_class_d_status_verified_fails(tmp_path: Path) -> None:
    bad = {
        "vector_id": "test-class-d-verified",
        "protocol_version": "0.1.0",
        "class": "D",
        "description": "test",
        "input": {"class": "D"},
        "expected_status": "VERIFIED",
        "expected_artifact_fields": ["status"],
        "why": "test",
    }
    _write_vector(tmp_path / "vectors", "test-class-d-verified", bad)
    results = vv.validate_all(tmp_path / "vectors", SCHEMA)
    assert len(results) == 1 and not results[0].passed
    # Schema's per-class allOf rejects this; failures contain a schema error.
    assert any(f.startswith("schema:") for f in results[0].failures)


def test_telemetry_status_in_input_fails(tmp_path: Path) -> None:
    bad = copy.deepcopy(VALID_A_TEMPLATE)
    bad["vector_id"] = "test-telemetry"
    bad["input"]["status"] = "CALIBRATION_IMPROVED"
    bad["expected_status"] = "VERIFIED"  # mismatch with telemetry rule
    _write_vector(tmp_path / "vectors", "test-telemetry", bad)
    results = vv.validate_all(tmp_path / "vectors", SCHEMA)
    assert not results[0].passed
    assert any("rule_telemetry_rejected" in f for f in results[0].failures)


def test_missing_required_field_fails(tmp_path: Path) -> None:
    bad = copy.deepcopy(VALID_A_TEMPLATE)
    bad["vector_id"] = "test-missing-why"
    bad.pop("why")
    _write_vector(tmp_path / "vectors", "test-missing-why", bad)
    results = vv.validate_all(tmp_path / "vectors", SCHEMA)
    assert not results[0].passed
    assert any(f.startswith("schema:") and "why" in f for f in results[0].failures)


def test_vector_id_must_match_filename_stem(tmp_path: Path) -> None:
    bad = copy.deepcopy(VALID_A_TEMPLATE)
    bad["vector_id"] = "this-does-not-match-filename"
    _write_vector(tmp_path / "vectors", "actual-filename-stem", bad)
    results = vv.validate_all(tmp_path / "vectors", SCHEMA)
    assert not results[0].passed
    assert any("rule_vector_id_filename" in f for f in results[0].failures)
