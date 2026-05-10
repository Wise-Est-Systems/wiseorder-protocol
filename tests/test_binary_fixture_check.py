"""Tests for tools/binary_fixture_check.py and the binary_fixtures/ corpus."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
TOOLS = REPO_ROOT / "tools"
FIXTURES = REPO_ROOT / "binary_fixtures"
sys.path.insert(0, str(TOOLS))

import binary_fixture_check as bfc  # noqa: E402


def test_sha256_of_known_bytes(tmp_path):
    p = tmp_path / "x.bin"
    p.write_bytes(b"hello")
    assert bfc.sha256_of(p) == "sha256:" + hashlib.sha256(b"hello").hexdigest()


def test_derive_verdict_match():
    assert bfc.derive_verdict("sha256:aa", "sha256:aa") == "VERIFIED"


def test_derive_verdict_mismatch():
    assert bfc.derive_verdict("sha256:aa", "sha256:bb") == "TAMPERED"


def test_manifest_present_and_well_formed():
    m = FIXTURES / "manifest.json"
    assert m.is_file()
    data = json.loads(m.read_text(encoding="utf-8"))
    assert "fixtures" in data
    names = {f["name"] for f in data["fixtures"]}
    assert {"valid", "corrupted", "truncated", "byte_mutated"} <= names


def test_all_fixtures_present():
    for name in ("valid.bin", "corrupted.bin", "truncated.bin", "byte_mutated.bin"):
        assert (FIXTURES / name).is_file(), f"missing: {name}"


def test_check_real_fixtures_all_pass():
    results = bfc.check_fixtures(FIXTURES)
    assert len(results) >= 4
    for r in results:
        assert r.passed, r.to_dict()


def test_valid_fixture_round_trip():
    results = bfc.check_fixtures(FIXTURES)
    valid = next(r for r in results if r.name == "valid")
    assert valid.derived_verdict == "VERIFIED"
    assert valid.expected_digest == valid.observed_digest


@pytest.mark.parametrize("name", ["corrupted", "truncated", "byte_mutated"])
def test_tampered_fixtures_detected_as_tampered(name):
    results = bfc.check_fixtures(FIXTURES)
    fix = next(r for r in results if r.name == name)
    assert fix.derived_verdict == "TAMPERED"
    assert fix.expected_digest != fix.observed_digest


def test_truncated_fixture_has_smaller_size():
    valid_size = (FIXTURES / "valid.bin").stat().st_size
    trunc_size = (FIXTURES / "truncated.bin").stat().st_size
    assert trunc_size < valid_size


def test_corrupted_fixture_same_size_as_valid():
    valid_size = (FIXTURES / "valid.bin").stat().st_size
    corr_size = (FIXTURES / "corrupted.bin").stat().st_size
    assert corr_size == valid_size


def test_byte_mutated_has_distinct_digest_from_corrupted():
    """Different mutations MUST produce different digests."""
    a = bfc.sha256_of(FIXTURES / "corrupted.bin")
    b = bfc.sha256_of(FIXTURES / "byte_mutated.bin")
    assert a != b


def test_self_check_returns_zero():
    assert bfc.self_check() == 0


def test_cli_check_returns_zero():
    assert bfc.main(["check", "--quiet"]) == 0


def test_cli_self_check_returns_zero():
    assert bfc.main(["self-check"]) == 0


def test_missing_fixture_marked_failed(tmp_path):
    """If a fixture file is referenced but absent, it MUST fail with MISSING."""
    manifest = {
        "format_version": "1.0",
        "fixtures": [
            {"name": "ghost", "path": "ghost.bin",
             "expected_digest": "sha256:" + "a" * 64,
             "expected_verdict": "VERIFIED", "size": 0},
        ],
    }
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    results = bfc.check_fixtures(tmp_path)
    assert len(results) == 1
    assert results[0].passed is False
    assert results[0].derived_verdict == "MISSING"
