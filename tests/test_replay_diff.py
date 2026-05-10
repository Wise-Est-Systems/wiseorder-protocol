"""Tests for tools/replay_diff.py."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
TOOLS = REPO_ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import replay_diff  # noqa: E402


def test_identical_dicts_yield_no_diffs():
    a = {"x": 1, "y": [1, 2, 3]}
    assert replay_diff.diff_json(a, a) == []


def test_hash_mismatch_is_classified():
    a = {"hash": "sha256:" + "a" * 64}
    b = {"hash": "sha256:" + "b" * 64}
    diffs = replay_diff.diff_json(a, b)
    assert len(diffs) == 1
    assert diffs[0].kind == "hash_mismatch"
    assert diffs[0].path == "$.hash"


def test_lifecycle_state_mismatch_is_classified():
    a = {"status": "VERIFIED"}
    b = {"status": "TAMPERED"}
    diffs = replay_diff.diff_json(a, b)
    assert len(diffs) == 1
    assert diffs[0].kind == "lifecycle_state_mismatch"


@pytest.mark.parametrize("key", [
    "final_status", "verdict", "process_status",
    "review_decision", "overall_status",
])
def test_lifecycle_keys_recognized(key):
    a = {key: "PASS"}
    b = {key: "FAIL"}
    diffs = replay_diff.diff_json(a, b)
    assert len(diffs) == 1
    assert diffs[0].kind == "lifecycle_state_mismatch"


def test_missing_field_detected():
    a = {"x": 1, "y": 2}
    b = {"x": 1}
    diffs = replay_diff.diff_json(a, b)
    assert len(diffs) == 1
    assert diffs[0].kind == "missing_field"
    assert diffs[0].path == "$.y"


def test_canonicalization_mismatch_top_level():
    a = {"canonicalization": "RFC8785-JCS"}
    b = {"canonicalization": "RFC8785-JCS-v2"}
    diffs = replay_diff.diff_json(a, b)
    assert len(diffs) == 1
    assert diffs[0].kind == "canonicalization_mismatch"


@pytest.mark.parametrize("key", [
    "algorithm", "expected_digest", "observed_digest", "input_digest",
])
def test_canonicalization_keys_recognized(key):
    a = {key: "X"}
    b = {key: "Y"}
    diffs = replay_diff.diff_json(a, b)
    assert len(diffs) == 1
    assert diffs[0].kind == "canonicalization_mismatch"


def test_authority_chain_mismatch_nested():
    a = {"protocol": {"required_quorum": 2, "name": "x"}}
    b = {"protocol": {"required_quorum": 3, "name": "x"}}
    diffs = replay_diff.diff_json(a, b)
    assert len(diffs) == 1
    assert diffs[0].kind == "authority_chain_mismatch"


def test_authority_chain_array_element():
    a = {"commit_chain": [{"hash": "sha256:" + "1" * 64, "stage": 1}]}
    b = {"commit_chain": [{"hash": "sha256:" + "2" * 64, "stage": 1}]}
    diffs = replay_diff.diff_json(a, b)
    assert len(diffs) == 1
    assert diffs[0].kind == "authority_chain_mismatch"


def test_authority_chain_eligible_attesters():
    a = {"protocol": {"eligible_attesters": ["a", "b"]}}
    b = {"protocol": {"eligible_attesters": ["a", "c"]}}
    diffs = replay_diff.diff_json(a, b)
    assert len(diffs) == 1
    assert diffs[0].kind == "authority_chain_mismatch"


def test_generic_value_mismatch_no_classification():
    a = {"description": "alpha"}
    b = {"description": "beta"}
    diffs = replay_diff.diff_json(a, b)
    assert len(diffs) == 1
    assert diffs[0].kind == "value_mismatch"


def test_array_length_difference_yields_missing_field():
    a = {"items": [1, 2, 3]}
    b = {"items": [1, 2]}
    diffs = replay_diff.diff_json(a, b)
    assert len(diffs) == 1
    assert diffs[0].kind == "missing_field"
    assert diffs[0].path == "$.items[2]"


def test_diff_files_round_trip(tmp_path):
    payload = {
        "status": "VERIFIED",
        "hash": "sha256:" + "f" * 64,
        "protocol": {"required_quorum": 2},
    }
    p1 = tmp_path / "a.json"
    p2 = tmp_path / "b.json"
    p1.write_text(json.dumps(payload), encoding="utf-8")
    p2.write_text(json.dumps(payload), encoding="utf-8")
    report = replay_diff.diff_files(p1, p2)
    assert report["divergent"] is False
    assert report["count"] == 0
    assert report["by_kind"] == {}


def test_diff_files_detects_divergence(tmp_path):
    p1 = tmp_path / "a.json"
    p2 = tmp_path / "b.json"
    p1.write_text(json.dumps({"status": "VERIFIED"}), encoding="utf-8")
    p2.write_text(json.dumps({"status": "TAMPERED"}), encoding="utf-8")
    report = replay_diff.diff_files(p1, p2)
    assert report["divergent"] is True
    assert report["count"] == 1
    assert report["by_kind"] == {"lifecycle_state_mismatch": 1}


def test_self_check_returns_zero(capsys):
    assert replay_diff.self_check() == 0
    captured = capsys.readouterr()
    assert "PASS" in captured.out


def test_cli_main_with_two_paths_returns_zero_when_identical(tmp_path):
    p = tmp_path / "x.json"
    p.write_text("{}", encoding="utf-8")
    assert replay_diff.main([str(p), str(p), "--quiet"]) == 0


def test_cli_main_with_two_paths_returns_one_when_diff(tmp_path):
    p1 = tmp_path / "a.json"
    p2 = tmp_path / "b.json"
    p1.write_text(json.dumps({"x": 1}), encoding="utf-8")
    p2.write_text(json.dumps({"x": 2}), encoding="utf-8")
    assert replay_diff.main([str(p1), str(p2), "--quiet"]) == 1


def test_cli_self_check_returns_zero():
    assert replay_diff.main(["self-check"]) == 0


def test_real_conformance_report_self_diff_is_empty():
    report_path = REPO_ROOT / "reports" / "conformance-report.json"
    if not report_path.is_file():
        pytest.skip("conformance report not present")
    report = replay_diff.diff_files(report_path, report_path)
    assert report["divergent"] is False
    assert report["count"] == 0
