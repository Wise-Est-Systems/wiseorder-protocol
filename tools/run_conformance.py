#!/usr/bin/env python3
"""WiseOrder Protocol v0.1.0 — conformance entrypoint.

Runs vector validation and implementation-declaration validation, then writes:

  - reports/conformance-report.json   (machine-readable, sorted keys)
  - reports/conformance-summary.txt   (human-readable)

The JSON report carries a `vectors_suite_sha256` — a single SHA-256 over the
sorted concatenation of every vector's per-file SHA-256, newline-delimited.
This is a tooling-internal suite fingerprint that detects silent vector
drift between runs. It is NOT a Class A canonicalization scheme.

Overall status is PASS only if every vector passes AND every implementation
declaration passes. Exit code is 0 on PASS, 1 on FAIL. The script does not
perform any network I/O and does not mutate any files outside reports/.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = REPO_ROOT / "tools"
REPORTS_DIR = REPO_ROOT / "reports"

sys.path.insert(0, str(TOOLS_DIR))

import validate_vectors  # noqa: E402  (deferred to after sys.path mutation)
import validate_implementations  # noqa: E402


def compute_vectors_suite_sha256(
    vector_results: list[validate_vectors.VectorResult],
) -> str:
    """Single fingerprint over the entire vector suite.

    SHA-256 of the sorted (by vector_id) concatenation of each vector's
    per-file sha256, newline-delimited. Tooling-internal — NOT a Class A
    canonicalization scheme.
    """
    digests = [
        v.sha256
        for v in sorted(vector_results, key=lambda r: r.vector_id)
        if v.sha256
    ]
    suite_input = "\n".join(digests).encode("utf-8")
    return "sha256:" + hashlib.sha256(suite_input).hexdigest()


def build_report(
    vector_results: list[validate_vectors.VectorResult],
    impl_results: list[validate_implementations.ImplResult],
) -> dict[str, Any]:
    vectors_pass = bool(vector_results) and all(r.passed for r in vector_results)
    impls_pass = bool(impl_results) and all(r.passed for r in impl_results)
    overall = "PASS" if (vectors_pass and impls_pass) else "FAIL"
    return {
        "protocol": "wiseorder",
        "version": "0.1.0",
        "vectors_suite_sha256": compute_vectors_suite_sha256(vector_results),
        "vector_results": [r.to_dict() for r in vector_results],
        "implementation_results": [r.to_dict() for r in impl_results],
        "vector_summary": {
            "total": len(vector_results),
            "passed": sum(1 for r in vector_results if r.passed),
            "failed": sum(1 for r in vector_results if not r.passed),
        },
        "implementation_summary": {
            "total": len(impl_results),
            "passed": sum(1 for r in impl_results if r.passed),
            "failed": sum(1 for r in impl_results if not r.passed),
        },
        "overall_status": overall,
    }


def render_summary(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("WiseOrder Protocol v0.1.0 — Conformance Summary")
    lines.append("=" * 60)
    lines.append(f"protocol:             {report['protocol']}")
    lines.append(f"version:              {report['version']}")
    lines.append(f"overall_status:       {report['overall_status']}")
    lines.append(f"vectors_suite_sha256: {report['vectors_suite_sha256']}")
    lines.append("")
    vs = report["vector_summary"]
    lines.append(
        f"vectors:         {vs['total']} checked, "
        f"{vs['passed']} passed, {vs['failed']} failed"
    )
    for r in report["vector_results"]:
        verdict = "PASS" if r["passed"] else "FAIL"
        lines.append(
            f"  {verdict} | {r['vector_id']:<48} | "
            f"{r['class']} | {r['expected_status']}"
        )
        for failure in r["failures"]:
            lines.append(f"       ↳ {failure}")
    lines.append("")
    is_ = report["implementation_summary"]
    lines.append(
        f"implementations: {is_['total']} checked, "
        f"{is_['passed']} passed, {is_['failed']} failed"
    )
    for r in report["implementation_results"]:
        verdict = "PASS" if r["passed"] else "FAIL"
        classes = ",".join(r["classes_supported"]) or "(none)"
        lines.append(
            f"  {verdict} | {r['implementation']:<24} | "
            f"classes=[{classes}] | audit_status={r['audit_status']}"
        )
        for failure in r["failures"]:
            lines.append(f"       ↳ {failure}")
    lines.append("")
    lines.append("=" * 60)
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run WiseOrder Protocol v0.1.0 conformance checks."
    )
    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=REPORTS_DIR,
        help=f"output directory for reports (default: {REPORTS_DIR})",
    )
    parser.add_argument(
        "--vectors-dir",
        type=Path,
        default=validate_vectors.DEFAULT_VECTORS_DIR,
        help="path to vectors directory",
    )
    parser.add_argument(
        "--implementations",
        type=Path,
        default=validate_implementations.DEFAULT_IMPL_MD,
        help="path to IMPLEMENTATIONS.md",
    )
    parser.add_argument(
        "--vector-schema",
        type=Path,
        default=validate_vectors.DEFAULT_SCHEMA_PATH,
        help="path to vector schema",
    )
    parser.add_argument(
        "--implementation-schema",
        type=Path,
        default=validate_implementations.DEFAULT_SCHEMA_PATH,
        help="path to implementation schema",
    )
    args = parser.parse_args(argv)

    args.reports_dir.mkdir(parents=True, exist_ok=True)

    vector_results = validate_vectors.validate_all(
        args.vectors_dir, args.vector_schema
    )
    impl_results = validate_implementations.validate_all(
        args.implementations, args.implementation_schema
    )

    report = build_report(vector_results, impl_results)
    summary = render_summary(report)

    report_path = args.reports_dir / "conformance-report.json"
    summary_path = args.reports_dir / "conformance-summary.txt"

    report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    summary_path.write_text(summary, encoding="utf-8")

    def _rel(p: Path) -> str:
        try:
            return str(p.relative_to(REPO_ROOT))
        except ValueError:
            return str(p)

    sys.stdout.write(summary)
    sys.stdout.write(f"\nWrote {_rel(report_path)}\n")
    sys.stdout.write(f"Wrote {_rel(summary_path)}\n")

    return 0 if report["overall_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
