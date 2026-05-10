"""Tests for the interop layer (generate_fixture_manifest + run_interop_checks)."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import generate_fixture_manifest as gen
import run_conformance
import run_interop_checks as run
import validate_implementations as vi

REPO_ROOT = Path(__file__).resolve().parent.parent
INTEROP_FIXTURES = REPO_ROOT / "interop" / "fixtures"
COMMITTED_INTEROP_REPORT = REPO_ROOT / "interop" / "reports" / "interop-report.json"
IMPL_SCHEMA = REPO_ROOT / "schemas" / "implementation.schema.json"


VALID_FIXTURE: dict = {
    "fixture_id": "test-fixture-001",
    "implementation": "Winstack",
    "protocol": "wiseorder",
    "version": "0.1.0",
    "artifact_class": "A",
    "aligned_vectors": ["class-a-valid-wiseproof"],
    "generated_at": "2026-05-06T12:00:00Z",
    "artifact": {
        "class": "A",
        "regime": "deterministic_verification",
        "claim": "test",
        "canonicalization": "RFC8785-JCS",
        "algorithm": "SHA-256",
        "expected_digest": "sha256:" + "a" * 64,
        "observed_digest": "sha256:" + "a" * 64,
    },
}


def _write_fixture(directory: Path, fixture: dict, name: str | None = None) -> Path:
    name = name or fixture["fixture_id"]
    directory.mkdir(parents=True, exist_ok=True)
    p = directory / f"{name}.fixture.json"
    p.write_text(json.dumps(fixture, indent=2), encoding="utf-8")
    return p


def _md_with(*decls: dict) -> str:
    parts = [f"```json\n{json.dumps(d, indent=2)}\n```" for d in decls]
    return "\n\n".join(parts) + "\n"


# -----------------------------------------------------------------------------
# Determinism
# -----------------------------------------------------------------------------

def test_manifests_generate_deterministically(tmp_path: Path) -> None:
    fix_dir = tmp_path / "fixtures" / "winstack"
    _write_fixture(fix_dir, VALID_FIXTURE)

    res1 = gen.generate_all(tmp_path / "fixtures")
    assert all(r.passed for r in res1), [r.failures for r in res1]
    manifest_path = fix_dir / f"{VALID_FIXTURE['fixture_id']}.manifest.json"
    bytes1 = manifest_path.read_bytes()

    res2 = gen.generate_all(tmp_path / "fixtures")
    assert all(r.passed for r in res2)
    bytes2 = manifest_path.read_bytes()

    assert bytes1 == bytes2, "manifest generation is not byte-deterministic"


# -----------------------------------------------------------------------------
# Schema validation
# -----------------------------------------------------------------------------

def test_invalid_fixture_schema_fails(tmp_path: Path) -> None:
    bad = copy.deepcopy(VALID_FIXTURE)
    bad.pop("artifact_class")  # remove a required field
    fix_dir = tmp_path / "fixtures" / "winstack"
    _write_fixture(fix_dir, bad)

    results = gen.generate_all(tmp_path / "fixtures")
    assert len(results) == 1 and not results[0].passed
    assert any("fixture_schema" in f and "artifact_class" in f for f in results[0].failures)


def test_invalid_manifest_schema_fails(tmp_path: Path) -> None:
    fix_dir = tmp_path / "fixtures" / "winstack"
    _write_fixture(fix_dir, VALID_FIXTURE)
    gen.generate_all(tmp_path / "fixtures")

    manifest_path = fix_dir / f"{VALID_FIXTURE['fixture_id']}.manifest.json"
    # Hand-corrupt the manifest by removing a required field, then re-canonicalize
    # so the only failing check is the schema (not serialization).
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest.pop("version")
    manifest_path.write_text(
        json.dumps(manifest, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    impls = {"Winstack": ["A", "B"]}
    vector_classes = {"class-a-valid-wiseproof": "A"}
    result = run.check_one(manifest_path, impls, vector_classes)
    assert not result.passed
    assert any("manifest_schema" in f and "version" in f for f in result.failures)


# -----------------------------------------------------------------------------
# Cross-layer checks
# -----------------------------------------------------------------------------

def test_invalid_vector_reference_fails(tmp_path: Path) -> None:
    bad = copy.deepcopy(VALID_FIXTURE)
    bad["aligned_vectors"] = ["this-vector-does-not-exist"]
    fix_dir = tmp_path / "fixtures" / "winstack"
    _write_fixture(fix_dir, bad)
    gen.generate_all(tmp_path / "fixtures")

    impls = {"Winstack": ["A", "B"]}
    vector_classes = {"class-a-valid-wiseproof": "A"}
    manifest_path = fix_dir / f"{bad['fixture_id']}.manifest.json"
    result = run.check_one(manifest_path, impls, vector_classes)
    assert not result.passed
    assert any("aligned_vectors_exist" in f for f in result.failures)


def test_wiseata_class_a_fixture_fails_at_generation(tmp_path: Path) -> None:
    bad = copy.deepcopy(VALID_FIXTURE)
    bad["fixture_id"] = "wiseata-class-a-bad-001"
    bad["implementation"] = "WISEATA"
    bad["artifact_class"] = "A"
    fix_dir = tmp_path / "fixtures" / "wiseata"
    _write_fixture(fix_dir, bad)

    results = gen.generate_all(tmp_path / "fixtures")
    assert len(results) == 1 and not results[0].passed
    assert any("F-1" in f for f in results[0].failures)
    assert not (fix_dir / "wiseata-class-a-bad-001.manifest.json").exists()


def test_mismatched_class_vector_pair_fails(tmp_path: Path) -> None:
    bad = copy.deepcopy(VALID_FIXTURE)
    bad["aligned_vectors"] = ["class-b-valid-wiseexp"]  # but artifact_class is A
    fix_dir = tmp_path / "fixtures" / "winstack"
    _write_fixture(fix_dir, bad)
    gen.generate_all(tmp_path / "fixtures")

    impls = {"Winstack": ["A", "B"]}
    vector_classes = {
        "class-a-valid-wiseproof": "A",
        "class-b-valid-wiseexp": "B",
    }
    manifest_path = fix_dir / f"{bad['fixture_id']}.manifest.json"
    result = run.check_one(manifest_path, impls, vector_classes)
    assert not result.passed
    assert any("aligned_vectors_class_match" in f for f in result.failures)


def test_invalid_sha256_format_fails(tmp_path: Path) -> None:
    fix_dir = tmp_path / "fixtures" / "winstack"
    _write_fixture(fix_dir, VALID_FIXTURE)
    gen.generate_all(tmp_path / "fixtures")

    manifest_path = fix_dir / f"{VALID_FIXTURE['fixture_id']}.manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["artifact_sha256"] = "not-a-real-sha256"
    manifest_path.write_text(
        json.dumps(manifest, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    impls = {"Winstack": ["A", "B"]}
    vector_classes = {"class-a-valid-wiseproof": "A"}
    result = run.check_one(manifest_path, impls, vector_classes)
    assert not result.passed
    # Schema rejects the sha256 pattern before the cross-rule fires.
    assert any("artifact_sha256" in f for f in result.failures)


def test_stable_serialization_hashing_passes(tmp_path: Path) -> None:
    fix_dir = tmp_path / "fixtures" / "winstack"
    _write_fixture(fix_dir, VALID_FIXTURE)
    gen.generate_all(tmp_path / "fixtures")

    manifest_path = fix_dir / f"{VALID_FIXTURE['fixture_id']}.manifest.json"
    impls = {"Winstack": ["A", "B"]}
    vector_classes = {"class-a-valid-wiseproof": "A"}
    result = run.check_one(manifest_path, impls, vector_classes)
    assert result.passed, result.failures
    assert result.checks["manifest_serialization_stable"]


def test_class_not_in_implementation_fails(tmp_path: Path) -> None:
    bad = copy.deepcopy(VALID_FIXTURE)
    bad["fixture_id"] = "test-class-c-not-declared"
    bad["implementation"] = "WISEATA"
    bad["artifact_class"] = "C"
    bad["aligned_vectors"] = ["class-c-consensus-pending"]
    fix_dir = tmp_path / "fixtures" / "wiseata"
    _write_fixture(fix_dir, bad)
    gen.generate_all(tmp_path / "fixtures")

    manifest_path = fix_dir / "test-class-c-not-declared.manifest.json"
    impls = {"WISEATA": ["B"]}
    vector_classes = {
        "class-b-valid-wiseexp": "B",
        "class-c-consensus-pending": "C",
    }
    result = run.check_one(manifest_path, impls, vector_classes)
    assert not result.passed
    assert any("class_in_implementation_classes" in f for f in result.failures)


# -----------------------------------------------------------------------------
# Drift detection
# -----------------------------------------------------------------------------

def test_manifest_drift_detection(tmp_path: Path) -> None:
    fix_dir = tmp_path / "fixtures" / "winstack"
    _write_fixture(fix_dir, VALID_FIXTURE)
    gen.generate_all(tmp_path / "fixtures")
    manifest_path = fix_dir / f"{VALID_FIXTURE['fixture_id']}.manifest.json"
    pristine = manifest_path.read_bytes()

    # Hand-edit the manifest (introduce drift) — preserve canonical form so the
    # only thing that differs is the field value.
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["aligned_vectors"] = ["class-a-valid-wiseproof", "extra-vector"]
    manifest_path.write_text(
        json.dumps(manifest, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    drifted = manifest_path.read_bytes()
    assert drifted != pristine

    # Regeneration must overwrite the drift back to the pristine bytes.
    gen.generate_all(tmp_path / "fixtures")
    restored = manifest_path.read_bytes()
    assert restored == pristine, "regeneration did not heal drift"


# -----------------------------------------------------------------------------
# Suite fingerprints
# -----------------------------------------------------------------------------

def test_suite_fingerprint_determinism() -> None:
    results1 = run.check_all(INTEROP_FIXTURES)
    fp1 = run.compute_manifests_suite_sha256(results1)

    results2 = run.check_all(INTEROP_FIXTURES)
    fp2 = run.compute_manifests_suite_sha256(results2)

    assert fp1 == fp2, "manifests_suite_sha256 must be deterministic"
    assert fp1.startswith("sha256:") and len(fp1) == len("sha256:") + 64


def test_manifest_sha256_stability(tmp_path: Path) -> None:
    fix_dir = tmp_path / "fixtures" / "winstack"
    _write_fixture(fix_dir, VALID_FIXTURE)
    gen.generate_all(tmp_path / "fixtures")

    manifest_path = fix_dir / f"{VALID_FIXTURE['fixture_id']}.manifest.json"
    expected = "sha256:" + hashlib.sha256(manifest_path.read_bytes()).hexdigest()

    impls = {"Winstack": ["A", "B"]}
    vector_classes = {"class-a-valid-wiseproof": "A"}
    result = run.check_one(manifest_path, impls, vector_classes)
    assert result.manifest_sha256 == expected


# -----------------------------------------------------------------------------
# Real-suite sanity
# -----------------------------------------------------------------------------

def test_real_interop_suite_passes() -> None:
    results = run.check_all(INTEROP_FIXTURES)
    failures = [(r.fixture_id, r.failures) for r in results if not r.passed]
    assert not failures, f"interop failures: {failures}"
    assert len(results) == 3
    impls = sorted({r.implementation for r in results})
    assert impls == ["WISEATA", "Winstack"]
    classes = sorted({r.artifact_class for r in results})
    assert classes == ["A", "B"]


def test_real_suite_has_no_wiseata_class_a_manifest() -> None:
    for path in (INTEROP_FIXTURES / "wiseata").glob("*.manifest.json"):
        manifest = json.loads(path.read_text(encoding="utf-8"))
        assert manifest["artifact_class"] != "A", (
            f"WISEATA manifest at {path} claims Class A, violating F-1"
        )


# -----------------------------------------------------------------------------
# Report linkage validation
# -----------------------------------------------------------------------------

def test_report_linkage_validation(tmp_path: Path) -> None:
    """A CONFORMANT declaration with both reports should validate; missing one
    should fail."""
    reports_dir = tmp_path / "reports"
    rc = run_conformance.main(["--reports-dir", str(reports_dir)])
    assert rc == 0
    conformance_path = reports_dir / "conformance-report.json"
    assert COMMITTED_INTEROP_REPORT.is_file()

    happy = tmp_path / "I.md"
    happy.write_text(
        _md_with(
            {
                "implementation": "Winstack",
                "protocol": "wiseorder",
                "version": "0.1.0",
                "classes_supported": ["A", "B"],
                "audit_status": "CONFORMANT",
                "evidence": {
                    "conformance_report": str(conformance_path),
                    "interop_report": str(COMMITTED_INTEROP_REPORT),
                },
            }
        ),
        encoding="utf-8",
    )
    happy_results = vi.validate_all(happy, IMPL_SCHEMA)
    assert happy_results and happy_results[0].passed, happy_results[0].failures

    # Now drop the interop_report — schema should reject.
    sad = tmp_path / "I-sad.md"
    sad.write_text(
        _md_with(
            {
                "implementation": "Winstack",
                "protocol": "wiseorder",
                "version": "0.1.0",
                "classes_supported": ["A", "B"],
                "audit_status": "CONFORMANT",
                "evidence": {
                    "conformance_report": str(conformance_path),
                },
            }
        ),
        encoding="utf-8",
    )
    sad_results = vi.validate_all(sad, IMPL_SCHEMA)
    assert not sad_results[0].passed
    assert any("interop_report" in f for f in sad_results[0].failures)
