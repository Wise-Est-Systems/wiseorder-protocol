#!/usr/bin/env python3
"""WiseOrder Protocol v0.1.0 — implementation declaration validator.

Extracts every JSON code block from IMPLEMENTATIONS.md, filters to those that
look like implementation declarations (have a `protocol` field), and validates
each against schemas/implementation.schema.json plus cross-declaration rules:

  - Every declaration MUST have protocol == "wiseorder", version == "0.1.0".
  - Every declaration MUST have an audit_status in {NOT_AUDITED, CONFORMANT, FAILED}.
  - WISEATA MUST NOT declare Class A support under v0.1.0 (F-1).
  - Winstack MAY declare any subset of {A, B} under v0.1.0 of this registry.
  - audit_status=CONFORMANT requires evidence with BOTH:
        evidence.conformance_report  → must point at a PASS conformance report
        evidence.interop_report      → must point at a PASS interop report
    Both reports must declare protocol "wiseorder" and the same version as the
    implementation declaration. The conformance report must show passing
    vectors for every declared class (per-class coverage).
    Optional evidence.report_sha256 is a single fingerprint over the two
    individual report digests; if present it MUST match the computed value.
  - audit_status=FAILED requires a non-empty `notes` field (schema-enforced).

Exit code: 0 if every declaration passes; 1 otherwise.
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


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_IMPL_MD = REPO_ROOT / "IMPLEMENTATIONS.md"
DEFAULT_SCHEMA_PATH = REPO_ROOT / "schemas" / "implementation.schema.json"

WINSTACK_ALLOWED_CLASSES = frozenset({"A", "B"})


@dataclass(frozen=False)
class ImplResult:
    block_index: int
    implementation: str
    classes_supported: list[str]
    audit_status: str
    failures: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.failures

    def to_dict(self) -> dict[str, Any]:
        return {
            "block_index": self.block_index,
            "implementation": self.implementation,
            "classes_supported": list(self.classes_supported),
            "audit_status": self.audit_status,
            "passed": self.passed,
            "failures": list(self.failures),
        }


def extract_json_blocks(md_path: Path) -> list[tuple[int, str]]:
    """Return (block_index, raw_json_text) tuples for every ```json fence."""
    if not md_path.is_file():
        raise FileNotFoundError(f"implementations markdown not found: {md_path}")
    text = md_path.read_text(encoding="utf-8")
    blocks: list[tuple[int, str]] = []
    in_block = False
    current: list[str] = []
    block_index = 0
    for line in text.splitlines():
        stripped = line.strip()
        if not in_block and stripped == "```json":
            in_block = True
            current = []
            continue
        if in_block and stripped == "```":
            blocks.append((block_index, "\n".join(current)))
            block_index += 1
            in_block = False
            current = []
            continue
        if in_block:
            current.append(line)
    return blocks


def _is_declaration(obj: Any) -> bool:
    return isinstance(obj, dict) and obj.get("protocol") is not None


def _schema_failures(decl: Any, validator: Draft202012Validator) -> list[str]:
    failures: list[str] = []
    for err in validator.iter_errors(decl):
        path = ".".join(str(p) for p in err.absolute_path) or "<root>"
        failures.append(f"schema: {path}: {err.message}")
    return failures


def _resolve_path(path_str: str, repo_root: Path) -> Path:
    p = Path(path_str)
    if not p.is_absolute():
        p = (repo_root / path_str).resolve()
    return p


def _combined_report_sha256(conformance_bytes: bytes, interop_bytes: bytes) -> str:
    """Single deterministic fingerprint over the two report digests.

    Defined as: sha256 over a canonical JSON object whose keys are 'conformance'
    and 'interop', sorted, with each value being the sha256:<hex> digest of
    that report's bytes. Tooling-internal canonicalization for fingerprinting;
    NOT a Class A canonicalization scheme.
    """
    c_digest = "sha256:" + hashlib.sha256(conformance_bytes).hexdigest()
    i_digest = "sha256:" + hashlib.sha256(interop_bytes).hexdigest()
    canonical = json.dumps(
        {"conformance": c_digest, "interop": i_digest},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(canonical).hexdigest()


def _rule_wiseata_no_class_a(decl: dict[str, Any], repo_root: Path) -> list[str]:
    if decl.get("implementation") != "WISEATA":
        return []
    if "A" in decl.get("classes_supported", []):
        return [
            "rule_wiseata_no_class_a: WISEATA MUST NOT declare Class A support "
            "under v0.1.0 (F-1, canonicalization incompatibility)."
        ]
    return []


def _rule_winstack_class_envelope(decl: dict[str, Any], repo_root: Path) -> list[str]:
    if decl.get("implementation") != "Winstack":
        return []
    classes = set(decl.get("classes_supported", []))
    extra = classes - WINSTACK_ALLOWED_CLASSES
    if extra:
        return [
            "rule_winstack_class_envelope: Winstack MAY declare only "
            f"{sorted(WINSTACK_ALLOWED_CLASSES)} under v0.1.0 of the registry "
            f"(extra: {sorted(extra)})."
        ]
    return []


def _rule_audit_status_evidence(decl: dict[str, Any], repo_root: Path) -> list[str]:
    """audit_status=CONFORMANT requires BOTH a passing conformance report and a
    passing interop report. NOT_AUDITED and FAILED are gated structurally by
    the schema (FAILED requires notes; NOT_AUDITED has no extra obligations)."""
    audit_status = decl.get("audit_status")
    if audit_status != "CONFORMANT":
        return []

    evidence = decl.get("evidence")
    if not isinstance(evidence, dict):
        return [
            "rule_audit_status_evidence: audit_status=CONFORMANT requires an "
            "evidence object. Fail closed."
        ]

    failures: list[str] = []
    conformance_path_str = evidence.get("conformance_report")
    interop_path_str = evidence.get("interop_report")
    if not conformance_path_str:
        failures.append(
            "rule_audit_status_evidence: evidence.conformance_report missing."
        )
    if not interop_path_str:
        failures.append(
            "rule_audit_status_evidence: evidence.interop_report missing."
        )
    if failures:
        return failures

    conformance_path = _resolve_path(conformance_path_str, repo_root)
    interop_path = _resolve_path(interop_path_str, repo_root)

    if not conformance_path.is_file():
        failures.append(
            "rule_audit_status_evidence: evidence.conformance_report "
            f"{conformance_path_str!r} does not exist."
        )
    if not interop_path.is_file():
        failures.append(
            "rule_audit_status_evidence: evidence.interop_report "
            f"{interop_path_str!r} does not exist."
        )
    if failures:
        return failures

    try:
        conformance_bytes = conformance_path.read_bytes()
        conformance = json.loads(conformance_bytes.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return [
            "rule_audit_status_evidence: could not read conformance report at "
            f"{conformance_path_str!r}: {exc}"
        ]
    try:
        interop_bytes = interop_path.read_bytes()
        interop = json.loads(interop_bytes.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return [
            "rule_audit_status_evidence: could not read interop report at "
            f"{interop_path_str!r}: {exc}"
        ]

    # Both reports MUST be PASS.
    if not isinstance(conformance, dict) or conformance.get("overall_status") != "PASS":
        failures.append(
            "rule_audit_status_evidence: conformance report overall_status is "
            f"{conformance.get('overall_status') if isinstance(conformance, dict) else None!r}, not 'PASS'."
        )
    if not isinstance(interop, dict) or interop.get("overall_status") != "PASS":
        failures.append(
            "rule_audit_status_evidence: interop report overall_status is "
            f"{interop.get('overall_status') if isinstance(interop, dict) else None!r}, not 'PASS'."
        )

    # Both reports MUST match the declared protocol/version.
    if isinstance(conformance, dict):
        if conformance.get("protocol") != "wiseorder" or conformance.get("version") != decl.get("version"):
            failures.append(
                "rule_audit_status_evidence: conformance report protocol/version "
                f"({conformance.get('protocol')!r}/{conformance.get('version')!r}) does "
                f"not match declaration ('wiseorder'/{decl.get('version')!r})."
            )
    if isinstance(interop, dict):
        if interop.get("protocol") != "wiseorder" or interop.get("version") != decl.get("version"):
            failures.append(
                "rule_audit_status_evidence: interop report protocol/version "
                f"({interop.get('protocol')!r}/{interop.get('version')!r}) does "
                f"not match declaration ('wiseorder'/{decl.get('version')!r})."
            )

    # Optional combined report_sha256 verification.
    expected_sha = evidence.get("report_sha256")
    if expected_sha:
        actual_sha = _combined_report_sha256(conformance_bytes, interop_bytes)
        if actual_sha != expected_sha:
            failures.append(
                "rule_audit_status_evidence: evidence.report_sha256 mismatch "
                f"(expected {expected_sha}, computed {actual_sha})."
            )

    if failures:
        return failures

    # Per-class coverage in the conformance report.
    classes = set(decl.get("classes_supported", []))
    classes_with_passing: set[str] = set()
    failed_in_class: list[tuple[str, str]] = []
    for v in conformance.get("vector_results", []):
        v_class = v.get("class")
        if v_class in classes:
            if v.get("passed", False):
                classes_with_passing.add(v_class)
            else:
                failed_in_class.append((v_class, v.get("vector_id", "?")))
    if failed_in_class:
        failures.append(
            "rule_audit_status_evidence: conformance report shows failing "
            f"vectors in declared classes: {failed_in_class}."
        )
    missing = classes - classes_with_passing
    if missing:
        failures.append(
            "rule_audit_status_evidence: conformance report has no passing "
            f"vectors for declared classes {sorted(missing)}."
        )
    return failures


CROSS_RULES = (
    _rule_wiseata_no_class_a,
    _rule_winstack_class_envelope,
    _rule_audit_status_evidence,
)


def validate_all(
    md_path: Path = DEFAULT_IMPL_MD,
    schema_path: Path = DEFAULT_SCHEMA_PATH,
    repo_root: Path = REPO_ROOT,
) -> list[ImplResult]:
    if not schema_path.is_file():
        raise FileNotFoundError(f"implementation schema not found: {schema_path}")
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    results: list[ImplResult] = []
    for index, raw in extract_json_blocks(md_path):
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError as exc:
            results.append(
                ImplResult(
                    block_index=index,
                    implementation="<unparseable>",
                    classes_supported=[],
                    audit_status="?",
                    failures=[f"json: {exc.msg} at line {exc.lineno} col {exc.colno}"],
                )
            )
            continue
        if not _is_declaration(obj):
            continue
        failures = _schema_failures(obj, validator)
        if isinstance(obj, dict):
            for rule in CROSS_RULES:
                failures.extend(rule(obj, repo_root))
        results.append(
            ImplResult(
                block_index=index,
                implementation=str(obj.get("implementation", "<missing>")),
                classes_supported=list(obj.get("classes_supported", [])),
                audit_status=str(obj.get("audit_status", "?")),
                failures=failures,
            )
        )
    return results


def _print_table(results: list[ImplResult]) -> None:
    print("WiseOrder Protocol v0.1.0 — Implementation Audit")
    print("=" * 60)
    if not results:
        print("(no implementation declarations found)")
        return
    width_name = max(len(r.implementation) for r in results)
    for r in results:
        verdict = "PASS" if r.passed else "FAIL"
        classes = ",".join(r.classes_supported) if r.classes_supported else "(none)"
        print(
            f"{verdict} | {r.implementation:<{width_name}} | "
            f"classes=[{classes}] | audit_status={r.audit_status}"
        )
        for failure in r.failures:
            print(f"       ↳ {failure}")
    print("=" * 60)
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed
    print(f"Summary: {total} implementations checked, {passed} passed, {failed} failed.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate WiseOrder implementation declarations."
    )
    parser.add_argument(
        "--implementations",
        type=Path,
        default=DEFAULT_IMPL_MD,
        help=f"path to IMPLEMENTATIONS.md (default: {DEFAULT_IMPL_MD})",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=DEFAULT_SCHEMA_PATH,
        help=f"path to implementation schema (default: {DEFAULT_SCHEMA_PATH})",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help="repository root (used to resolve evidence report paths)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="suppress the per-implementation table; emit only the summary line",
    )
    args = parser.parse_args(argv)
    results = validate_all(args.implementations, args.schema, args.repo_root)
    if not args.quiet:
        _print_table(results)
    elif results:
        passed = sum(1 for r in results if r.passed)
        print(
            f"implementations: {len(results)} checked, {passed} passed, "
            f"{len(results) - passed} failed."
        )
    return 0 if all(r.passed for r in results) and results else 1


if __name__ == "__main__":
    raise SystemExit(main())
