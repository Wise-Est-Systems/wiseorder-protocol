#!/usr/bin/env python3
"""WiseOrder Protocol v0.1.0 — fixture manifest generator.

Reads every interop/fixtures/<impl>/*.fixture.json and writes a corresponding
*.manifest.json. Source files are validated against schemas/fixture.schema.json
and generated manifests are validated against schemas/manifest.schema.json.

Determinism contract:

  - Manifest output is byte-stable across runs (sorted keys, 2-space indent,
    trailing newline, UTF-8).
  - `generated_at` is copied from the fixture source. The wall clock is
    never read.
  - `artifact_sha256` is computed over a tooling-internal canonical JSON form
    of the embedded `artifact` field (sorted keys, compact separators). This
    is fingerprinting only — NOT a Class A canonicalization scheme. Class A
    canonicalization remains RFC 8785 JCS only, per SPEC.md §4.

Fail-closed:

  - Fixture file does not match schemas/fixture.schema.json → fail.
  - WISEATA fixtures claiming Class A → refuse to write a manifest (F-1).
  - Generated manifest does not match schemas/manifest.schema.json → fail.

Exit code: 0 if every fixture generates cleanly; 1 otherwise.
"""

from __future__ import annotations

import argparse
import hashlib
import json
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
DEFAULT_FIXTURE_SCHEMA = REPO_ROOT / "schemas" / "fixture.schema.json"
DEFAULT_MANIFEST_SCHEMA = REPO_ROOT / "schemas" / "manifest.schema.json"


@dataclass
class GenerationResult:
    fixture_path: str
    fixture_id: str
    manifest_path: str
    artifact_sha256: str
    manifest_sha256: str
    failures: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.failures

    def to_dict(self) -> dict[str, Any]:
        return {
            "fixture_path": self.fixture_path,
            "fixture_id": self.fixture_id,
            "manifest_path": self.manifest_path,
            "artifact_sha256": self.artifact_sha256,
            "manifest_sha256": self.manifest_sha256,
            "passed": self.passed,
            "failures": list(self.failures),
        }


def canonical_artifact_bytes(artifact: Any) -> bytes:
    """Tooling-internal canonical JSON for fingerprinting.

    NOT a Class A canonicalization scheme. Class A artifacts use RFC 8785 JCS
    per SPEC.md §4. This function is used only to produce a stable byte
    sequence over which an `artifact_sha256` can be computed for interop
    manifests.
    """
    return json.dumps(
        artifact,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def canonical_pretty_manifest(manifest: dict[str, Any]) -> str:
    """Pretty-printed canonical form for committed manifest files."""
    return json.dumps(manifest, sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def discover_fixtures(fixtures_dir: Path) -> list[Path]:
    if not fixtures_dir.is_dir():
        raise FileNotFoundError(f"interop fixtures directory not found: {fixtures_dir}")
    return sorted(fixtures_dir.rglob("*.fixture.json"))


def _schema_failures(obj: Any, validator: Draft202012Validator, prefix: str) -> list[str]:
    failures: list[str] = []
    for err in validator.iter_errors(obj):
        path = ".".join(str(p) for p in err.absolute_path) or "<root>"
        failures.append(f"{prefix}: {path}: {err.message}")
    return failures


def _rel(p: Path, root: Path) -> str:
    try:
        return str(p.relative_to(root))
    except ValueError:
        return str(p)


def generate_one(
    fixture_path: Path,
    fixture_validator: Draft202012Validator,
    manifest_validator: Draft202012Validator,
    repo_root: Path = REPO_ROOT,
) -> GenerationResult:
    rel_fixture = _rel(fixture_path, repo_root)
    manifest_path = fixture_path.with_name(
        fixture_path.name.replace(".fixture.json", ".manifest.json")
    )
    rel_manifest = _rel(manifest_path, repo_root)

    try:
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return GenerationResult(
            fixture_path=rel_fixture,
            fixture_id="<unparseable>",
            manifest_path=rel_manifest,
            artifact_sha256="",
            manifest_sha256="",
            failures=[f"json: {exc}"],
        )

    failures = _schema_failures(fixture, fixture_validator, "fixture_schema")
    if failures:
        return GenerationResult(
            fixture_path=rel_fixture,
            fixture_id=str(fixture.get("fixture_id", "<missing>")) if isinstance(fixture, dict) else "?",
            manifest_path=rel_manifest,
            artifact_sha256="",
            manifest_sha256="",
            failures=failures,
        )

    # Filename-stem consistency: <fixture_id>.fixture.json
    expected_stem = fixture_path.name.replace(".fixture.json", "")
    if fixture["fixture_id"] != expected_stem:
        return GenerationResult(
            fixture_path=rel_fixture,
            fixture_id=str(fixture["fixture_id"]),
            manifest_path=rel_manifest,
            artifact_sha256="",
            manifest_sha256="",
            failures=[
                f"rule_fixture_id_filename: fixture_id={fixture['fixture_id']!r} "
                f"does not match filename stem {expected_stem!r}."
            ],
        )

    # F-1 enforcement at generation time.
    if fixture["implementation"] == "WISEATA" and fixture["artifact_class"] == "A":
        return GenerationResult(
            fixture_path=rel_fixture,
            fixture_id=fixture["fixture_id"],
            manifest_path=rel_manifest,
            artifact_sha256="",
            manifest_sha256="",
            failures=[
                "F-1: WISEATA fixtures MUST NOT claim Class A under v0.1.0; "
                "refusing to generate a manifest."
            ],
        )

    artifact_bytes = canonical_artifact_bytes(fixture["artifact"])
    artifact_sha256 = "sha256:" + hashlib.sha256(artifact_bytes).hexdigest()

    manifest = {
        "implementation": fixture["implementation"],
        "protocol": fixture["protocol"],
        "version": fixture["version"],
        "artifact_class": fixture["artifact_class"],
        "fixture_id": fixture["fixture_id"],
        "artifact_sha256": artifact_sha256,
        "generated_at": fixture["generated_at"],
        "aligned_vectors": list(fixture["aligned_vectors"]),
    }

    # Validate the generated manifest before writing.
    manifest_failures = _schema_failures(manifest, manifest_validator, "manifest_schema")
    if manifest_failures:
        return GenerationResult(
            fixture_path=rel_fixture,
            fixture_id=fixture["fixture_id"],
            manifest_path=rel_manifest,
            artifact_sha256=artifact_sha256,
            manifest_sha256="",
            failures=manifest_failures,
        )

    manifest_text = canonical_pretty_manifest(manifest)
    manifest_sha256 = "sha256:" + hashlib.sha256(manifest_text.encode("utf-8")).hexdigest()
    manifest_path.write_text(manifest_text, encoding="utf-8")

    return GenerationResult(
        fixture_path=rel_fixture,
        fixture_id=fixture["fixture_id"],
        manifest_path=rel_manifest,
        artifact_sha256=artifact_sha256,
        manifest_sha256=manifest_sha256,
    )


def generate_all(
    fixtures_dir: Path = DEFAULT_FIXTURES_DIR,
    repo_root: Path = REPO_ROOT,
    fixture_schema_path: Path = DEFAULT_FIXTURE_SCHEMA,
    manifest_schema_path: Path = DEFAULT_MANIFEST_SCHEMA,
) -> list[GenerationResult]:
    if not fixture_schema_path.is_file():
        raise FileNotFoundError(f"fixture schema not found: {fixture_schema_path}")
    if not manifest_schema_path.is_file():
        raise FileNotFoundError(f"manifest schema not found: {manifest_schema_path}")
    fixture_validator = Draft202012Validator(
        json.loads(fixture_schema_path.read_text(encoding="utf-8"))
    )
    manifest_validator = Draft202012Validator(
        json.loads(manifest_schema_path.read_text(encoding="utf-8"))
    )
    return [
        generate_one(p, fixture_validator, manifest_validator, repo_root)
        for p in discover_fixtures(fixtures_dir)
    ]


def _print_table(results: list[GenerationResult]) -> None:
    print("WiseOrder Protocol v0.1.0 — Fixture Manifest Generation")
    print("=" * 60)
    if not results:
        print("(no fixtures found)")
        return
    for r in results:
        verdict = "PASS" if r.passed else "FAIL"
        print(f"{verdict} | {r.fixture_id:<40} → {r.manifest_path}")
        for f in r.failures:
            print(f"       ↳ {f}")
    print("=" * 60)
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    print(f"Summary: {total} fixtures, {passed} generated, {total - passed} failed.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate WiseOrder interop fixture manifests."
    )
    parser.add_argument(
        "--fixtures-dir", type=Path, default=DEFAULT_FIXTURES_DIR,
        help=f"path to fixtures root (default: {DEFAULT_FIXTURES_DIR})",
    )
    parser.add_argument(
        "--reports-dir", type=Path, default=DEFAULT_REPORTS_DIR,
        help=f"path to reports output dir (default: {DEFAULT_REPORTS_DIR})",
    )
    parser.add_argument(
        "--fixture-schema", type=Path, default=DEFAULT_FIXTURE_SCHEMA,
        help=f"path to fixture schema (default: {DEFAULT_FIXTURE_SCHEMA})",
    )
    parser.add_argument(
        "--manifest-schema", type=Path, default=DEFAULT_MANIFEST_SCHEMA,
        help=f"path to manifest schema (default: {DEFAULT_MANIFEST_SCHEMA})",
    )
    args = parser.parse_args(argv)

    args.reports_dir.mkdir(parents=True, exist_ok=True)
    results = generate_all(
        args.fixtures_dir,
        REPO_ROOT,
        args.fixture_schema,
        args.manifest_schema,
    )
    _print_table(results)

    overall = "PASS" if results and all(r.passed for r in results) else "FAIL"
    report = {
        "protocol": "wiseorder",
        "version": "0.1.0",
        "fixtures_processed": [r.to_dict() for r in results],
        "summary": {
            "total": len(results),
            "passed": sum(1 for r in results if r.passed),
            "failed": sum(1 for r in results if not r.passed),
        },
        "overall_status": overall,
    }
    report_path = args.reports_dir / "fixture-manifest-report.json"
    report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"\nWrote {_rel(report_path, REPO_ROOT)}")
    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
