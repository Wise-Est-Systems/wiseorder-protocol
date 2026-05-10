"""Tests for tools/run_conformance.py."""

from __future__ import annotations

import json
from pathlib import Path

import run_conformance

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_main_returns_zero_on_current_repo(tmp_path: Path) -> None:
    reports_dir = tmp_path / "reports"
    rc = run_conformance.main(["--reports-dir", str(reports_dir)])
    assert rc == 0


def test_main_writes_both_report_files(tmp_path: Path) -> None:
    reports_dir = tmp_path / "reports"
    run_conformance.main(["--reports-dir", str(reports_dir)])
    assert (reports_dir / "conformance-report.json").is_file()
    assert (reports_dir / "conformance-summary.txt").is_file()


def test_overall_status_is_pass_on_current_repo(tmp_path: Path) -> None:
    reports_dir = tmp_path / "reports"
    run_conformance.main(["--reports-dir", str(reports_dir)])
    report = json.loads(
        (reports_dir / "conformance-report.json").read_text(encoding="utf-8")
    )
    assert report["overall_status"] == "PASS"
    assert report["protocol"] == "wiseorder"
    assert report["version"] == "0.1.0"


def test_empty_vector_suite_fails_closed(tmp_path: Path) -> None:
    vec_dir = tmp_path / "vectors"
    vec_dir.mkdir()
    impl_md = tmp_path / "I.md"
    impl_md.write_text(
        "```json\n"
        + json.dumps(
            {
                "implementation": "X",
                "protocol": "wiseorder",
                "version": "0.1.0",
                "classes_supported": ["A"],
                "audit_status": "NOT_AUDITED",
            }
        )
        + "\n```\n",
        encoding="utf-8",
    )
    reports_dir = tmp_path / "reports"
    rc = run_conformance.main(
        [
            "--vectors-dir",
            str(vec_dir),
            "--implementations",
            str(impl_md),
            "--reports-dir",
            str(reports_dir),
        ]
    )
    assert rc == 1
    report = json.loads(
        (reports_dir / "conformance-report.json").read_text(encoding="utf-8")
    )
    assert report["overall_status"] == "FAIL"
    assert report["vector_summary"]["total"] == 0
