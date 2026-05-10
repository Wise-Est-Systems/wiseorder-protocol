#!/usr/bin/env python3
"""WiseOrder Protocol v0.1.0 — vector validator.

Validates every *.json file in the vectors/ directory against
schemas/vector.schema.json and against the cross-validation rules that
encode SPEC.md semantics:

  - Class A VERIFIED vectors MUST declare input.canonicalization == "RFC8785-JCS".
  - Class A vectors with a non-JCS canonicalization MUST expect INVALID.
  - Class A vectors with no canonicalization MUST expect INVALID.
  - Class D vectors MUST NOT use VERIFIED as expected_status (also schema-enforced).
  - Vectors whose input.status is a telemetry token (CALIBRATION_*) MUST expect INVALID.

Exit code: 0 if every vector passes; 1 if any vector fails.
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
DEFAULT_VECTORS_DIR = REPO_ROOT / "vectors"
DEFAULT_SCHEMA_PATH = REPO_ROOT / "schemas" / "vector.schema.json"

TELEMETRY_TOKENS = {"CALIBRATION_IMPROVED", "CALIBRATION_DEGRADED"}


@dataclass(frozen=False)
class VectorResult:
    file: str
    vector_id: str
    cls: str
    expected_status: str
    sha256: str
    failures: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.failures

    def to_dict(self) -> dict[str, Any]:
        return {
            "file": self.file,
            "vector_id": self.vector_id,
            "class": self.cls,
            "expected_status": self.expected_status,
            "sha256": self.sha256,
            "passed": self.passed,
            "failures": list(self.failures),
        }


def _load_json(path: Path) -> Any:
    with path.open("rb") as handle:
        raw = handle.read()
    return json.loads(raw.decode("utf-8")), hashlib.sha256(raw).hexdigest()


def _schema_failures(vector: Any, validator: Draft202012Validator) -> list[str]:
    failures: list[str] = []
    for err in validator.iter_errors(vector):
        path = ".".join(str(p) for p in err.absolute_path) or "<root>"
        failures.append(f"schema: {path}: {err.message}")
    return failures


def _rule_class_a_jcs(vector: dict[str, Any]) -> list[str]:
    if vector.get("class") != "A":
        return []
    expected = vector.get("expected_status")
    canon = vector.get("input", {}).get("canonicalization")
    failures: list[str] = []
    if expected == "VERIFIED" and canon != "RFC8785-JCS":
        failures.append(
            "rule_class_a_jcs: VERIFIED Class A vector MUST declare "
            f"input.canonicalization == 'RFC8785-JCS' (got {canon!r})"
        )
    if canon is None and expected != "INVALID":
        failures.append(
            "rule_class_a_jcs: Class A vector with no input.canonicalization "
            f"MUST expect INVALID (got {expected!r})"
        )
    if canon is not None and canon != "RFC8785-JCS" and expected != "INVALID":
        failures.append(
            "rule_class_a_jcs: Class A vector with non-JCS canonicalization "
            f"({canon!r}) MUST expect INVALID (got {expected!r})"
        )
    return failures


def _rule_class_d_not_verified(vector: dict[str, Any]) -> list[str]:
    if vector.get("class") != "D":
        return []
    if vector.get("expected_status") == "VERIFIED":
        return [
            "rule_class_d_not_verified: Class D vectors MUST NOT use VERIFIED "
            "as expected_status (D4)."
        ]
    return []


def _rule_telemetry_rejected(vector: dict[str, Any]) -> list[str]:
    inp = vector.get("input")
    if not isinstance(inp, dict):
        return []
    status = inp.get("status")
    if status in TELEMETRY_TOKENS and vector.get("expected_status") != "INVALID":
        return [
            f"rule_telemetry_rejected: input.status={status!r} is a telemetry "
            "token; expected_status MUST be INVALID (got "
            f"{vector.get('expected_status')!r})."
        ]
    return []


CROSS_RULES = (
    _rule_class_a_jcs,
    _rule_class_d_not_verified,
    _rule_telemetry_rejected,
)


def discover_vectors(vectors_dir: Path) -> list[Path]:
    if not vectors_dir.is_dir():
        raise FileNotFoundError(f"vectors directory not found: {vectors_dir}")
    return sorted(p for p in vectors_dir.glob("*.json") if p.is_file())


def validate_all(
    vectors_dir: Path = DEFAULT_VECTORS_DIR,
    schema_path: Path = DEFAULT_SCHEMA_PATH,
) -> list[VectorResult]:
    if not schema_path.is_file():
        raise FileNotFoundError(f"vector schema not found: {schema_path}")
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    results: list[VectorResult] = []
    for path in discover_vectors(vectors_dir):
        try:
            rel = str(path.relative_to(REPO_ROOT))
        except ValueError:
            rel = str(path)
        try:
            vector, digest = _load_json(path)
        except json.JSONDecodeError as exc:
            results.append(
                VectorResult(
                    file=rel,
                    vector_id="<unparseable>",
                    cls="?",
                    expected_status="?",
                    sha256="",
                    failures=[f"json: {exc.msg} at line {exc.lineno} col {exc.colno}"],
                )
            )
            continue
        failures = _schema_failures(vector, validator)
        if isinstance(vector, dict):
            expected_id = path.stem
            actual_id = vector.get("vector_id")
            if actual_id != expected_id:
                failures.append(
                    "rule_vector_id_filename: "
                    f"vector_id={actual_id!r} does not match filename stem "
                    f"{expected_id!r}."
                )
            for rule in CROSS_RULES:
                failures.extend(rule(vector))
        result = VectorResult(
            file=rel,
            vector_id=str(vector.get("vector_id", "<missing>")) if isinstance(vector, dict) else "?",
            cls=str(vector.get("class", "?")) if isinstance(vector, dict) else "?",
            expected_status=str(vector.get("expected_status", "?")) if isinstance(vector, dict) else "?",
            sha256=digest,
            failures=failures,
        )
        results.append(result)
    return results


def _print_table(results: list[VectorResult]) -> None:
    print("WiseOrder Protocol v0.1.0 — Vector Validation")
    print("=" * 60)
    if not results:
        print("(no vectors found)")
        return
    width_id = max(len(r.vector_id) for r in results)
    for r in results:
        verdict = "PASS" if r.passed else "FAIL"
        print(f"{verdict} | {r.vector_id:<{width_id}} | {r.cls} | {r.expected_status}")
        for failure in r.failures:
            print(f"       ↳ {failure}")
    print("=" * 60)
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed
    print(f"Summary: {total} vectors checked, {passed} passed, {failed} failed.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate WiseOrder vectors.")
    parser.add_argument(
        "--vectors-dir",
        type=Path,
        default=DEFAULT_VECTORS_DIR,
        help=f"path to vectors directory (default: {DEFAULT_VECTORS_DIR})",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=DEFAULT_SCHEMA_PATH,
        help=f"path to vector schema (default: {DEFAULT_SCHEMA_PATH})",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="suppress the per-vector table; emit only the summary line",
    )
    args = parser.parse_args(argv)
    results = validate_all(args.vectors_dir, args.schema)
    if not args.quiet:
        _print_table(results)
    elif results:
        passed = sum(1 for r in results if r.passed)
        print(f"vectors: {len(results)} checked, {passed} passed, {len(results) - passed} failed.")
    return 0 if all(r.passed for r in results) and results else 1


if __name__ == "__main__":
    raise SystemExit(main())
