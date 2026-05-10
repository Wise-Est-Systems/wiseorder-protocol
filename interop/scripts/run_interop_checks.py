#!/usr/bin/env python3
"""WiseOrder Protocol v0.1.0 — interoperability checker.

Reads every interop/fixtures/<impl>/*.manifest.json (already produced by
generate_fixture_manifest.py), validates each against
schemas/manifest.schema.json, and applies seven cross-layer checks:

  1. protocol_version_match            — protocol == "wiseorder", version == "0.1.0"
  2. class_in_implementation_classes   — manifest's artifact_class is in the
                                         implementation's classes_supported
                                         (per IMPLEMENTATIONS.md, via
                                         validate_implementations).
  3. aligned_vectors_exist             — every aligned_vectors entry resolves
                                         to a published vector under vectors/.
  4. aligned_vectors_class_match       — every aligned vector's class equals
                                         the manifest's artifact_class.
  5. wiseata_class_a_prohibition       — WISEATA fixtures MUST NOT claim
                                         Class A (F-1).
  6. artifact_sha256_format            — artifact_sha256 matches
                                         ^sha256:[0-9a-f]{64}$.
  7. manifest_serialization_stable     — disk bytes equal a fresh
                                         canonical_pretty_manifest re-rendering.

The JSON report carries:

  - per-result `manifest_sha256` (SHA-256 of disk bytes for that manifest)
  - top-level `manifests_suite_sha256` (SHA-256 over sorted concatenation
    of every manifest's per-file sha256, newline-delimited)

Tooling-internal fingerprints — NOT Class A canonicalization schemes.

Exit code: 0 only if every fixture passes every check.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator
except ImportError as exc:  # pragma: no cover
    sys.stderr.write(
        "error: jsonschema package not available. Install via "
        "`pip install -r requirements.txt`.\n"
    )
    raise SystemExit(2) from exc


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_FIXTURES_DIR = REPO_ROOT / "interop" / "fixtures"
DEFAULT_REPORTS_DIR = REPO_ROOT / "interop" / "reports"
DEFAULT_MANIFEST_SCHEMA = REPO_ROOT / "schemas" / "manifest.schema.json"

# Make the conformance tooling importable so we read implementations and
# vectors from a single source of truth.
TOOLS_DIR = REPO_ROOT / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import validate_implementations  # noqa: E402
import validate_vectors  # noqa: E402

SHA256_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")

CHECK_NAMES = (
    "protocol_version_match",
    "class_in_implementation_classes",
    "aligned_vectors_exist",
    "aligned_vectors_class_match",
    "wiseata_class_a_prohibition",
    "artifact_sha256_format",
    "manifest_serialization_stable",
)


@dataclass
class InteropResult:
    fixture_id: str
    implementation: str
    artifact_class: str
    aligned_vectors: list[str]
    manifest_path: str
    manifest_sha256: str = ""
    checks: dict[str, bool] = field(default_factory=dict)
    failures: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.failures

    def to_dict(self) -> dict[str, Any]:
        return {
            "fixture_id": self.fixture_id,
            "implementation": self.implementation,
            "artifact_class": self.artifact_class,
            "aligned_vectors": list(self.aligned_vectors),
            "manifest_path": self.manifest_path,
            "manifest_sha256": self.manifest_sha256,
            "checks": dict(self.checks),
            "passed": self.passed,
            "failures": list(self.failures),
        }


def canonical_pretty_manifest(manifest: dict[str, Any]) -> str:
    return json.dumps(manifest, sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def _rel(p: Path, root: Path) -> str:
    try:
        return str(p.relative_to(root))
    except ValueError:
        return str(p)


def _schema_failures(obj: Any, validator: Draft202012Validator, prefix: str) -> list[str]:
    failures: list[str] = []
    for err in validator.iter_errors(obj):
        path = ".".join(str(p) for p in err.absolute_path) or "<root>"
        failures.append(f"{prefix}: {path}: {err.message}")
    return failures


def discover_manifests(fixtures_dir: Path) -> list[Path]:
    if not fixtures_dir.is_dir():
        raise FileNotFoundError(f"interop fixtures directory not found: {fixtures_dir}")
    return sorted(fixtures_dir.rglob("*.manifest.json"))


def load_implementation_classes() -> dict[str, list[str]]:
    """Return {implementation_name: declared classes_supported}."""
    impl_results = validate_implementations.validate_all()
    return {r.implementation: list(r.classes_supported) for r in impl_results}


def load_vector_class_map() -> dict[str, str]:
    """Return {vector_id: class}."""
    vec_results = validate_vectors.validate_all()
    return {r.vector_id: r.cls for r in vec_results}


def compute_manifests_suite_sha256(results: list[InteropResult]) -> str:
    """Single fingerprint over the entire manifest suite.

    SHA-256 of the sorted (by fixture_id) concatenation of each manifest's
    per-file sha256, newline-delimited. Tooling-internal — NOT a Class A
    canonicalization scheme.
    """
    digests = [
        r.manifest_sha256
        for r in sorted(results, key=lambda r: r.fixture_id)
        if r.manifest_sha256
    ]
    suite_input = "\n".join(digests).encode("utf-8")
    return "sha256:" + hashlib.sha256(suite_input).hexdigest()


def check_one(
    manifest_path: Path,
    impls: dict[str, list[str]],
    vector_classes: dict[str, str],
    manifest_validator: Draft202012Validator | None = None,
    repo_root: Path = REPO_ROOT,
) -> InteropResult:
    rel = _rel(manifest_path, repo_root)
    if manifest_validator is None:
        manifest_validator = Draft202012Validator(
            json.loads(DEFAULT_MANIFEST_SCHEMA.read_text(encoding="utf-8"))
        )

    try:
        disk_bytes = manifest_path.read_bytes()
        disk_text = disk_bytes.decode("utf-8")
        manifest = json.loads(disk_text)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return InteropResult(
            fixture_id="<unparseable>",
            implementation="?",
            artifact_class="?",
            aligned_vectors=[],
            manifest_path=rel,
            failures=[f"could not parse manifest: {exc}"],
        )

    manifest_sha256 = "sha256:" + hashlib.sha256(disk_bytes).hexdigest()

    schema_failures = _schema_failures(manifest, manifest_validator, "manifest_schema")
    if schema_failures:
        return InteropResult(
            fixture_id=str(manifest.get("fixture_id", "<missing>")) if isinstance(manifest, dict) else "?",
            implementation=str(manifest.get("implementation", "?")) if isinstance(manifest, dict) else "?",
            artifact_class=str(manifest.get("artifact_class", "?")) if isinstance(manifest, dict) else "?",
            aligned_vectors=list(manifest.get("aligned_vectors", []) or []) if isinstance(manifest, dict) else [],
            manifest_path=rel,
            manifest_sha256=manifest_sha256,
            failures=schema_failures,
        )

    result = InteropResult(
        fixture_id=str(manifest["fixture_id"]),
        implementation=str(manifest["implementation"]),
        artifact_class=str(manifest["artifact_class"]),
        aligned_vectors=list(manifest["aligned_vectors"]),
        manifest_path=rel,
        manifest_sha256=manifest_sha256,
    )

    # 1. protocol_version_match
    pv_ok = manifest["protocol"] == "wiseorder" and manifest["version"] == "0.1.0"
    result.checks["protocol_version_match"] = pv_ok
    if not pv_ok:
        result.failures.append(
            "check_protocol_version_match: expected protocol='wiseorder' "
            f"version='0.1.0' (got protocol={manifest['protocol']!r} "
            f"version={manifest['version']!r})."
        )

    # 2. class_in_implementation_classes
    impl_classes = impls.get(manifest["implementation"], [])
    cls_ok = manifest["artifact_class"] in impl_classes
    result.checks["class_in_implementation_classes"] = cls_ok
    if not cls_ok:
        result.failures.append(
            f"check_class_in_implementation_classes: implementation "
            f"{manifest['implementation']!r} does not declare class "
            f"{manifest['artifact_class']!r} in IMPLEMENTATIONS.md "
            f"(declared: {impl_classes})."
        )

    # 3. aligned_vectors_exist
    missing_vectors = [v for v in manifest["aligned_vectors"] if v not in vector_classes]
    av_exist_ok = not missing_vectors
    result.checks["aligned_vectors_exist"] = av_exist_ok
    if not av_exist_ok:
        result.failures.append(
            f"check_aligned_vectors_exist: aligned_vectors not present in "
            f"vector suite: {missing_vectors}."
        )

    # 4. aligned_vectors_class_match
    mismatched = []
    for v in manifest["aligned_vectors"]:
        v_class = vector_classes.get(v)
        if v_class is not None and v_class != manifest["artifact_class"]:
            mismatched.append((v, v_class))
    av_class_ok = not mismatched
    result.checks["aligned_vectors_class_match"] = av_class_ok
    if not av_class_ok:
        for v, c in mismatched:
            result.failures.append(
                f"check_aligned_vectors_class_match: vector {v!r} is class "
                f"{c!r}, but fixture artifact_class is "
                f"{manifest['artifact_class']!r}."
            )

    # 5. wiseata_class_a_prohibition
    f1_ok = not (manifest["implementation"] == "WISEATA" and manifest["artifact_class"] == "A")
    result.checks["wiseata_class_a_prohibition"] = f1_ok
    if not f1_ok:
        result.failures.append(
            "check_wiseata_class_a_prohibition: WISEATA MUST NOT claim "
            "Class A under v0.1.0 (F-1)."
        )

    # 6. artifact_sha256_format
    sha = manifest["artifact_sha256"]
    sha_ok = isinstance(sha, str) and bool(SHA256_PATTERN.match(sha))
    result.checks["artifact_sha256_format"] = sha_ok
    if not sha_ok:
        result.failures.append(
            f"check_artifact_sha256_format: artifact_sha256={sha!r} is not "
            "of the form 'sha256:<64 lowercase hex>'."
        )

    # 7. manifest_serialization_stable
    expected_text = canonical_pretty_manifest(manifest)
    stable_ok = disk_text == expected_text
    result.checks["manifest_serialization_stable"] = stable_ok
    if not stable_ok:
        result.failures.append(
            "check_manifest_serialization_stable: manifest on disk is not in "
            "canonical pretty form (sorted keys, 2-space indent, trailing "
            "newline). Re-run generate_fixture_manifest.py."
        )

    return result


def check_all(
    fixtures_dir: Path = DEFAULT_FIXTURES_DIR,
    repo_root: Path = REPO_ROOT,
    manifest_schema_path: Path = DEFAULT_MANIFEST_SCHEMA,
) -> list[InteropResult]:
    if not manifest_schema_path.is_file():
        raise FileNotFoundError(f"manifest schema not found: {manifest_schema_path}")
    manifest_validator = Draft202012Validator(
        json.loads(manifest_schema_path.read_text(encoding="utf-8"))
    )
    impls = load_implementation_classes()
    vector_classes = load_vector_class_map()
    return [
        check_one(p, impls, vector_classes, manifest_validator, repo_root)
        for p in discover_manifests(fixtures_dir)
    ]


def render_summary(results: list[InteropResult], status: str, suite_sha256: str) -> str:
    lines: list[str] = []
    lines.append("WiseOrder Protocol v0.1.0 — Interoperability Summary")
    lines.append("=" * 60)
    lines.append("protocol:                 wiseorder")
    lines.append("version:                  0.1.0")
    lines.append(f"overall_status:           {status}")
    lines.append(f"manifests_suite_sha256:   {suite_sha256}")
    lines.append("")
    if not results:
        lines.append("(no fixtures found — fail closed)")
    else:
        for r in results:
            verdict = "PASS" if r.passed else "FAIL"
            lines.append(
                f"{verdict} | {r.fixture_id:<40} | {r.implementation:<10} | "
                f"class={r.artifact_class} | vectors={','.join(r.aligned_vectors)}"
            )
            for f in r.failures:
                lines.append(f"       ↳ {f}")
        total = len(results)
        passed = sum(1 for r in results if r.passed)
        lines.append("")
        lines.append(
            f"Summary: {total} fixtures, {passed} passed, "
            f"{total - passed} failed."
        )
    lines.append("=" * 60)
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run WiseOrder interop checks.")
    parser.add_argument(
        "--fixtures-dir", type=Path, default=DEFAULT_FIXTURES_DIR,
        help=f"path to fixtures root (default: {DEFAULT_FIXTURES_DIR})",
    )
    parser.add_argument(
        "--reports-dir", type=Path, default=DEFAULT_REPORTS_DIR,
        help=f"path to reports output dir (default: {DEFAULT_REPORTS_DIR})",
    )
    parser.add_argument(
        "--manifest-schema", type=Path, default=DEFAULT_MANIFEST_SCHEMA,
        help=f"path to manifest schema (default: {DEFAULT_MANIFEST_SCHEMA})",
    )
    args = parser.parse_args(argv)

    args.reports_dir.mkdir(parents=True, exist_ok=True)

    results = check_all(args.fixtures_dir, REPO_ROOT, args.manifest_schema)
    overall = "PASS" if results and all(r.passed for r in results) else "FAIL"
    suite_sha256 = compute_manifests_suite_sha256(results)

    report = {
        "protocol": "wiseorder",
        "version": "0.1.0",
        "manifests_suite_sha256": suite_sha256,
        "fixtures_checked": [
            {
                "fixture_id": r.fixture_id,
                "implementation": r.implementation,
                "artifact_class": r.artifact_class,
            }
            for r in results
        ],
        "interop_results": [r.to_dict() for r in results],
        "summary": {
            "total": len(results),
            "passed": sum(1 for r in results if r.passed),
            "failed": sum(1 for r in results if not r.passed),
        },
        "overall_status": overall,
    }
    report_path = args.reports_dir / "interop-report.json"
    summary_path = args.reports_dir / "interop-summary.txt"
    report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    summary = render_summary(results, overall, suite_sha256)
    summary_path.write_text(summary, encoding="utf-8")

    sys.stdout.write(summary)
    sys.stdout.write(f"\nWrote {_rel(report_path, REPO_ROOT)}\n")
    sys.stdout.write(f"Wrote {_rel(summary_path, REPO_ROOT)}\n")

    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
