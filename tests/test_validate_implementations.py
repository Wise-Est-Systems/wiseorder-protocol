"""Tests for tools/validate_implementations.py."""

from __future__ import annotations

import json
from pathlib import Path

import run_conformance
import validate_implementations as vi

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA = REPO_ROOT / "schemas" / "implementation.schema.json"
IMPL_MD = REPO_ROOT / "IMPLEMENTATIONS.md"
COMMITTED_INTEROP_REPORT = REPO_ROOT / "interop" / "reports" / "interop-report.json"


def _md_with(*decls: dict) -> str:
    parts = [f"```json\n{json.dumps(d, indent=2)}\n```" for d in decls]
    return "\n\n".join(parts) + "\n"


def _write_md(path: Path, *decls: dict) -> Path:
    path.write_text(_md_with(*decls), encoding="utf-8")
    return path


def test_real_implementations_pass() -> None:
    results = vi.validate_all(IMPL_MD, SCHEMA)
    assert results, "no implementation declarations discovered"
    names = [r.implementation for r in results]
    assert "Winstack" in names
    assert "WISEATA" in names
    failures = [(r.implementation, r.failures) for r in results if not r.passed]
    assert not failures, f"failed: {failures}"


def test_winstack_declares_a_b(tmp_path: Path) -> None:
    md = _write_md(
        tmp_path / "I.md",
        {
            "implementation": "Winstack",
            "protocol": "wiseorder",
            "version": "0.1.0",
            "classes_supported": ["A", "B"],
            "audit_status": "NOT_AUDITED",
        },
    )
    results = vi.validate_all(md, SCHEMA)
    assert results and results[0].passed, results[0].failures


def test_wiseata_declares_b_only(tmp_path: Path) -> None:
    md = _write_md(
        tmp_path / "I.md",
        {
            "implementation": "WISEATA",
            "protocol": "wiseorder",
            "version": "0.1.0",
            "classes_supported": ["B"],
            "audit_status": "NOT_AUDITED",
            "notes": "F-1 canonicalization incompatibility.",
        },
    )
    results = vi.validate_all(md, SCHEMA)
    assert results and results[0].passed, results[0].failures


def test_wiseata_declaring_class_a_fails(tmp_path: Path) -> None:
    md = _write_md(
        tmp_path / "I.md",
        {
            "implementation": "WISEATA",
            "protocol": "wiseorder",
            "version": "0.1.0",
            "classes_supported": ["A", "B"],
            "audit_status": "NOT_AUDITED",
        },
    )
    results = vi.validate_all(md, SCHEMA)
    assert not results[0].passed
    assert any("rule_wiseata_no_class_a" in f for f in results[0].failures)


def test_missing_audit_status_fails(tmp_path: Path) -> None:
    md = _write_md(
        tmp_path / "I.md",
        {
            "implementation": "X",
            "protocol": "wiseorder",
            "version": "0.1.0",
            "classes_supported": ["B"],
        },
    )
    results = vi.validate_all(md, SCHEMA)
    assert not results[0].passed
    assert any("audit_status" in f for f in results[0].failures)


def test_invalid_class_value_fails(tmp_path: Path) -> None:
    md = _write_md(
        tmp_path / "I.md",
        {
            "implementation": "X",
            "protocol": "wiseorder",
            "version": "0.1.0",
            "classes_supported": ["Z"],
            "audit_status": "NOT_AUDITED",
        },
    )
    results = vi.validate_all(md, SCHEMA)
    assert not results[0].passed
    assert any(f.startswith("schema:") for f in results[0].failures)


def test_conformant_without_evidence_fails(tmp_path: Path) -> None:
    md = _write_md(
        tmp_path / "I.md",
        {
            "implementation": "X",
            "protocol": "wiseorder",
            "version": "0.1.0",
            "classes_supported": ["A"],
            "audit_status": "CONFORMANT",
        },
    )
    results = vi.validate_all(md, SCHEMA)
    assert not results[0].passed
    assert any("evidence" in f for f in results[0].failures)


def test_conformant_with_passing_evidence_passes(tmp_path: Path) -> None:
    """Generate a fresh passing conformance report and pair it with the
    committed interop report; CONFORMANT against both should validate."""
    reports_dir = tmp_path / "reports"
    rc = run_conformance.main(["--reports-dir", str(reports_dir)])
    assert rc == 0, "real conformance run did not pass; cannot test evidence path"
    conformance_path = reports_dir / "conformance-report.json"
    assert COMMITTED_INTEROP_REPORT.is_file(), (
        f"committed interop report missing at {COMMITTED_INTEROP_REPORT}; "
        "run `make interop` to regenerate it."
    )
    md = _write_md(
        tmp_path / "I.md",
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
        },
    )
    results = vi.validate_all(md, SCHEMA)
    assert results and results[0].passed, results[0].failures


def test_conformant_with_failing_conformance_report_fails(tmp_path: Path) -> None:
    fake_conformance = tmp_path / "fake-conformance.json"
    fake_conformance.write_text(
        json.dumps(
            {
                "protocol": "wiseorder",
                "version": "0.1.0",
                "overall_status": "FAIL",
                "vector_results": [],
                "implementation_results": [],
            }
        ),
        encoding="utf-8",
    )
    fake_interop = tmp_path / "fake-interop.json"
    fake_interop.write_text(
        json.dumps(
            {
                "protocol": "wiseorder",
                "version": "0.1.0",
                "overall_status": "PASS",
                "fixtures_checked": [],
                "interop_results": [],
            }
        ),
        encoding="utf-8",
    )
    md = _write_md(
        tmp_path / "I.md",
        {
            "implementation": "X",
            "protocol": "wiseorder",
            "version": "0.1.0",
            "classes_supported": ["A"],
            "audit_status": "CONFORMANT",
            "evidence": {
                "conformance_report": str(fake_conformance),
                "interop_report": str(fake_interop),
            },
        },
    )
    results = vi.validate_all(md, SCHEMA)
    assert not results[0].passed
    assert any("conformance report overall_status" in f for f in results[0].failures)


def test_conformant_with_failing_interop_report_fails(tmp_path: Path) -> None:
    fake_conformance = tmp_path / "fake-conformance.json"
    fake_conformance.write_text(
        json.dumps(
            {
                "protocol": "wiseorder",
                "version": "0.1.0",
                "overall_status": "PASS",
                "vector_results": [
                    {"class": "A", "vector_id": "x", "passed": True}
                ],
                "implementation_results": [],
            }
        ),
        encoding="utf-8",
    )
    fake_interop = tmp_path / "fake-interop.json"
    fake_interop.write_text(
        json.dumps(
            {
                "protocol": "wiseorder",
                "version": "0.1.0",
                "overall_status": "FAIL",
                "fixtures_checked": [],
                "interop_results": [],
            }
        ),
        encoding="utf-8",
    )
    md = _write_md(
        tmp_path / "I.md",
        {
            "implementation": "X",
            "protocol": "wiseorder",
            "version": "0.1.0",
            "classes_supported": ["A"],
            "audit_status": "CONFORMANT",
            "evidence": {
                "conformance_report": str(fake_conformance),
                "interop_report": str(fake_interop),
            },
        },
    )
    results = vi.validate_all(md, SCHEMA)
    assert not results[0].passed
    assert any("interop report overall_status" in f for f in results[0].failures)


def test_conformant_with_missing_interop_report_fails(tmp_path: Path) -> None:
    fake_conformance = tmp_path / "fake-conformance.json"
    fake_conformance.write_text(
        json.dumps({"protocol": "wiseorder", "version": "0.1.0", "overall_status": "PASS"}),
        encoding="utf-8",
    )
    md = _write_md(
        tmp_path / "I.md",
        {
            "implementation": "X",
            "protocol": "wiseorder",
            "version": "0.1.0",
            "classes_supported": ["A"],
            "audit_status": "CONFORMANT",
            "evidence": {
                "conformance_report": str(fake_conformance),
                # interop_report missing
            },
        },
    )
    results = vi.validate_all(md, SCHEMA)
    assert not results[0].passed
    # Schema-level: 'interop_report' is a required property under evidence.
    assert any("interop_report" in f for f in results[0].failures)


def test_conformant_with_report_sha256_mismatch_fails(tmp_path: Path) -> None:
    fake_conformance = tmp_path / "fake-conformance.json"
    fake_conformance.write_text(
        json.dumps(
            {
                "protocol": "wiseorder",
                "version": "0.1.0",
                "overall_status": "PASS",
                "vector_results": [
                    {"class": "A", "vector_id": "x", "passed": True}
                ],
            }
        ),
        encoding="utf-8",
    )
    fake_interop = tmp_path / "fake-interop.json"
    fake_interop.write_text(
        json.dumps(
            {
                "protocol": "wiseorder",
                "version": "0.1.0",
                "overall_status": "PASS",
            }
        ),
        encoding="utf-8",
    )
    md = _write_md(
        tmp_path / "I.md",
        {
            "implementation": "X",
            "protocol": "wiseorder",
            "version": "0.1.0",
            "classes_supported": ["A"],
            "audit_status": "CONFORMANT",
            "evidence": {
                "conformance_report": str(fake_conformance),
                "interop_report": str(fake_interop),
                "report_sha256": "sha256:" + "0" * 64,
            },
        },
    )
    results = vi.validate_all(md, SCHEMA)
    assert not results[0].passed
    assert any("report_sha256 mismatch" in f for f in results[0].failures)


def test_failed_status_requires_notes(tmp_path: Path) -> None:
    md = _write_md(
        tmp_path / "I.md",
        {
            "implementation": "X",
            "protocol": "wiseorder",
            "version": "0.1.0",
            "classes_supported": ["A"],
            "audit_status": "FAILED",
        },
    )
    results = vi.validate_all(md, SCHEMA)
    assert not results[0].passed
    assert any("notes" in f for f in results[0].failures)
