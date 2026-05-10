#!/usr/bin/env python3
"""WiseOrder Protocol v0.1.0 — Demo Runner.

Runs the six demo steps in order and emits the v0.1.0 lock fingerprints
plus a final PASS/FAIL.

Steps:
  1. make conformance              (33 vectors)
  2. make interop                  (3 fixtures)
  3. make canonicalization-check   (10 corpus entries)
  4. make minimal-verifier-check   (independent re-derivation)
  5. make replay-diff-check        (diff engine self-check)
  6. make binary-fixture-check     (4 binary fixtures)

Exit codes:
  0   every step passed AND all three frozen fingerprints match
  1   any step failed OR any fingerprint diverged
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent

# Frozen v0.1.0 lock anchors (SPEC_LOCK_v0.1.md §2.4).
EXPECTED_VECTORS_SUITE_SHA256 = (
    "sha256:6168d2075931baa98bba763f9cd537142554aae7b26f19e3e93a60de2ee5bb0f"
)
EXPECTED_MANIFESTS_SUITE_SHA256 = (
    "sha256:74eaaa62271f23172232bda43ba3340543e66c46ba1e2f5e6da18d3447a6ba29"
)
EXPECTED_CORPUS_SHA256 = (
    "sha256:c95685bff48c15abc313c462908b05ac309250bc660c2d802ae51af5a8038b09"
)


@dataclass
class Step:
    name: str
    cmd: list[str]
    rc: int = 0
    duration_s: float = 0.0
    tail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "cmd": self.cmd,
            "rc": self.rc,
            "duration_s": round(self.duration_s, 3),
        }


def run(name: str, cmd: list[str]) -> Step:
    print(f"\n→ {name}")
    print(f"  $ {' '.join(cmd)}")
    t0 = time.monotonic()
    proc = subprocess.run(
        cmd, cwd=REPO_ROOT,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True,
    )
    dt = time.monotonic() - t0
    tail = "\n".join(proc.stdout.splitlines()[-3:])
    print(f"  rc={proc.returncode}  {dt:.2f}s")
    print(f"  …tail: {tail}")
    return Step(name=name, cmd=cmd, rc=proc.returncode, duration_s=dt, tail=tail)


def read_fingerprint(path: Path, key: str) -> str | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return data.get(key)


def main() -> int:
    print("=" * 72)
    print("WiseOrder Protocol v0.1.0 — Demo")
    print("=" * 72)

    steps = [
        run("conformance",            ["make", "conformance"]),
        run("interop",                ["make", "interop"]),
        run("canonicalization-check", ["make", "canonicalization-check"]),
        run("minimal-verifier-check", ["make", "minimal-verifier-check"]),
        run("replay-diff-check",      ["make", "replay-diff-check"]),
        run("binary-fixture-check",   ["make", "binary-fixture-check"]),
    ]

    # Fingerprints from regenerated reports.
    vectors_sha = read_fingerprint(
        REPO_ROOT / "reports" / "conformance-report.json", "vectors_suite_sha256"
    )
    manifests_sha = read_fingerprint(
        REPO_ROOT / "interop" / "reports" / "interop-report.json", "manifests_suite_sha256"
    )
    # corpus_sha256 is printed by canonicalization step, not stored as JSON.
    # Re-derive deterministically by re-reading the verify_golden output.
    corpus_sha: str | None = None
    canon_step = next((s for s in steps if s.name == "canonicalization-check"), None)
    if canon_step:
        for line in canon_step.tail.splitlines():
            if "corpus_sha256:" in line:
                _, _, val = line.partition("corpus_sha256:")
                corpus_sha = val.strip()
                break

    print()
    print("=" * 72)
    print("Fingerprints")
    print("=" * 72)
    print(f"  vectors_suite_sha256:   {vectors_sha}")
    print(f"  manifests_suite_sha256: {manifests_sha}")
    print(f"  corpus_sha256:          {corpus_sha}")

    fp_match = (
        vectors_sha == EXPECTED_VECTORS_SUITE_SHA256
        and manifests_sha == EXPECTED_MANIFESTS_SUITE_SHA256
        and corpus_sha == EXPECTED_CORPUS_SHA256
    )
    steps_ok = all(s.rc == 0 for s in steps)
    overall = steps_ok and fp_match

    print()
    print("=" * 72)
    print("Step results")
    print("=" * 72)
    for s in steps:
        verdict = "PASS" if s.rc == 0 else "FAIL"
        print(f"  {verdict} | {s.name:<26} | rc={s.rc} | {s.duration_s:.2f}s")

    print()
    print("=" * 72)
    print("Fingerprint comparison")
    print("=" * 72)
    print(f"  vectors_suite_sha256    expected: {EXPECTED_VECTORS_SUITE_SHA256}")
    print(f"                          observed: {vectors_sha}")
    print(f"                          {'MATCH' if vectors_sha == EXPECTED_VECTORS_SUITE_SHA256 else 'DIVERGENT'}")
    print(f"  manifests_suite_sha256  expected: {EXPECTED_MANIFESTS_SUITE_SHA256}")
    print(f"                          observed: {manifests_sha}")
    print(f"                          {'MATCH' if manifests_sha == EXPECTED_MANIFESTS_SUITE_SHA256 else 'DIVERGENT'}")
    print(f"  corpus_sha256           expected: {EXPECTED_CORPUS_SHA256}")
    print(f"                          observed: {corpus_sha}")
    print(f"                          {'MATCH' if corpus_sha == EXPECTED_CORPUS_SHA256 else 'DIVERGENT'}")

    print()
    print("=" * 72)
    print(f"OVERALL: {'PASS' if overall else 'FAIL'}")
    print("=" * 72)
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
