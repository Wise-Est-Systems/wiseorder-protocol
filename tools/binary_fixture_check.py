#!/usr/bin/env python3
"""WiseOrder Protocol v0.1.0 — Binary Fixture Check.

For each fixture under binary_fixtures/, compute SHA-256, compare against
the manifest's expected_digest, and emit a per-fixture verdict
(VERIFIED / TAMPERED) plus a derived overall PASS/FAIL.

A fixture passes if its derived verdict matches manifest.expected_verdict.
For valid fixtures, that requires the bytes on disk match the declared digest.
For tampered/truncated/byte-mutated fixtures, that requires the bytes do NOT
match the original valid digest — proving the verifier detects the tampering.

Usage:
  python3 tools/binary_fixture_check.py [--fixtures-dir DIR] [--quiet]
  python3 tools/binary_fixture_check.py self-check

Exit codes:
  0   every fixture's derived verdict matches expected_verdict
  1   one or more divergences
  2   usage / I/O error
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_FIXTURES_DIR = REPO_ROOT / "binary_fixtures"


@dataclass
class FixtureResult:
    name: str
    path: str
    size: int
    expected_digest: str
    observed_digest: str
    expected_verdict: str
    derived_verdict: str
    passed: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "path": self.path,
            "size": self.size,
            "expected_digest": self.expected_digest,
            "observed_digest": self.observed_digest,
            "expected_verdict": self.expected_verdict,
            "derived_verdict": self.derived_verdict,
            "passed": self.passed,
            "reason": self.reason,
        }


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def derive_verdict(expected_digest: str, observed_digest: str) -> str:
    return "VERIFIED" if expected_digest == observed_digest else "TAMPERED"


def check_fixtures(fixtures_dir: Path = DEFAULT_FIXTURES_DIR) -> list[FixtureResult]:
    manifest_path = fixtures_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    results: list[FixtureResult] = []
    for entry in manifest["fixtures"]:
        path = fixtures_dir / entry["path"]
        size = path.stat().st_size if path.is_file() else -1
        if not path.is_file():
            results.append(FixtureResult(
                name=entry["name"],
                path=entry["path"],
                size=-1,
                expected_digest=entry["expected_digest"],
                observed_digest="",
                expected_verdict=entry["expected_verdict"],
                derived_verdict="MISSING",
                passed=False,
                reason="fixture file not found",
            ))
            continue
        observed = sha256_of(path)
        derived = derive_verdict(entry["expected_digest"], observed)
        passed = derived == entry["expected_verdict"]
        reason = (
            "match" if passed
            else f"derived={derived} expected={entry['expected_verdict']}"
        )
        results.append(FixtureResult(
            name=entry["name"],
            path=entry["path"],
            size=size,
            expected_digest=entry["expected_digest"],
            observed_digest=observed,
            expected_verdict=entry["expected_verdict"],
            derived_verdict=derived,
            passed=passed,
            reason=reason,
        ))
    return results


def _print_table(results: list[FixtureResult]) -> None:
    print("WiseOrder Protocol v0.1.0 — Binary Fixture Check")
    print("=" * 60)
    width = max((len(r.name) for r in results), default=20)
    for r in results:
        verdict = "PASS" if r.passed else "FAIL"
        print(f"{verdict} | {r.name:<{width}} | size={r.size:>5} | "
              f"derived={r.derived_verdict:<10} expected={r.expected_verdict}")
        if not r.passed:
            print(f"       ↳ {r.reason}")
            print(f"       ↳ expected_digest={r.expected_digest}")
            print(f"       ↳ observed_digest={r.observed_digest}")
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    print("=" * 60)
    print(f"Summary: {total} fixtures, {passed} passed, {total - passed} failed")


def self_check() -> int:
    """In-memory self-check: build a fixture pair and exercise the verdict."""
    failures: list[str] = []

    def expect(name: str, condition: bool, detail: str = "") -> None:
        print(f"  [{'PASS' if condition else 'FAIL'}] {name}")
        if not condition:
            failures.append(f"{name}: {detail}")

    valid_bytes = b"WISEORDER\x00FIXTURE\x00" + b"\x00" * 64
    valid_digest = "sha256:" + hashlib.sha256(valid_bytes).hexdigest()
    tampered_bytes = bytearray(valid_bytes)
    tampered_bytes[5] ^= 1
    tampered_digest = "sha256:" + hashlib.sha256(bytes(tampered_bytes)).hexdigest()

    expect("valid_round_trip", derive_verdict(valid_digest, valid_digest) == "VERIFIED")
    expect("tampered_detected",
           derive_verdict(valid_digest, tampered_digest) == "TAMPERED")
    expect("digests_differ", valid_digest != tampered_digest)

    # Real fixture round-trip if present.
    fdir = DEFAULT_FIXTURES_DIR
    if (fdir / "manifest.json").is_file():
        results = check_fixtures(fdir)
        all_passed = all(r.passed for r in results)
        expect("real_fixtures_all_pass", all_passed,
               f"failures: {[r.to_dict() for r in results if not r.passed]}")
        # Each expected_verdict appears at least once.
        verdicts = {r.expected_verdict for r in results}
        expect("covers_VERIFIED", "VERIFIED" in verdicts)
        expect("covers_TAMPERED", "TAMPERED" in verdicts)

    if failures:
        print(f"\nFAIL: {len(failures)} self-check failures")
        return 1
    print("\nPASS: binary_fixture_check self-check")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="WiseOrder binary fixture check")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("self-check")
    check = sub.add_parser("check")
    check.add_argument("--fixtures-dir", type=Path, default=DEFAULT_FIXTURES_DIR)
    check.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)
    if args.cmd is None:
        args.cmd = "check"
        args.fixtures_dir = DEFAULT_FIXTURES_DIR
        args.quiet = False
    if args.cmd == "self-check":
        return self_check()
    results = check_fixtures(args.fixtures_dir)
    if not args.quiet:
        _print_table(results)
    failed = sum(1 for r in results if not r.passed)
    return 0 if failed == 0 and results else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
