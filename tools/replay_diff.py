#!/usr/bin/env python3
"""WiseOrder Protocol v0.1.0 — Replay Diff Engine.

Compare two manifest/report JSON files and classify every divergence by kind:

  - hash_mismatch              both sides match sha\\d+:hex; values differ
  - lifecycle_state_mismatch   key in {status, final_status, verdict, ...}
  - missing_field              present on one side, absent on the other
  - authority_chain_mismatch   key in/under commit_chain, evidence, protocol, ...
  - canonicalization_mismatch  key in {canonicalization, algorithm, *_digest}
  - value_mismatch             everything else

Usage:
  python3 tools/replay_diff.py <left.json> <right.json> [--quiet]
  python3 tools/replay_diff.py diff <left.json> <right.json>
  python3 tools/replay_diff.py self-check

Exit codes:
  0   no divergence
  1   divergence (or self-check failed)
  2   usage / I/O error
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent

HASH_RE = re.compile(r"^sha\d+:[0-9a-fA-F]+$")

LIFECYCLE_KEYS = frozenset({
    "final_status", "status", "state", "process_status",
    "expected_status", "verdict", "decision", "review_decision",
    "overall_status", "exit_status",
})

CANONICALIZATION_KEYS = frozenset({
    "canonicalization", "algorithm", "expected_digest", "observed_digest",
    "digest", "input_digest", "observed_result_digest",
})

AUTHORITY_KEYS = frozenset({
    "commit_chain", "evidence", "eligible_attesters", "authorization_source",
    "attester_id", "attesters", "protocol", "quorum", "required_quorum",
    "action_policy", "action_allowed", "action_compelled",
})

_MISSING = object()


@dataclass
class Diff:
    path: str
    kind: str
    left: Any
    right: Any

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "kind": self.kind,
            "left": self.left,
            "right": self.right,
        }


def _segments(path: str) -> list[str]:
    cleaned = re.sub(r"\[\d+\]", "", path)
    return [s for s in cleaned.split(".") if s and s != "$"]


def classify(path: str, key: str | None, left: Any, right: Any) -> str:
    if left is _MISSING or right is _MISSING:
        return "missing_field"
    segs = _segments(path)
    if key is not None and key in AUTHORITY_KEYS:
        return "authority_chain_mismatch"
    if any(s in AUTHORITY_KEYS for s in segs):
        return "authority_chain_mismatch"
    if key is not None and key in CANONICALIZATION_KEYS:
        return "canonicalization_mismatch"
    if any(s in CANONICALIZATION_KEYS for s in segs):
        return "canonicalization_mismatch"
    if key is not None and key in LIFECYCLE_KEYS:
        return "lifecycle_state_mismatch"
    if isinstance(left, str) and isinstance(right, str):
        if HASH_RE.match(left) and HASH_RE.match(right):
            return "hash_mismatch"
    return "value_mismatch"


def diff_json(left: Any, right: Any, path: str = "$", key: str | None = None) -> list[Diff]:
    diffs: list[Diff] = []
    if isinstance(left, dict) and isinstance(right, dict):
        for k in sorted(set(left.keys()) | set(right.keys())):
            sub_left = left.get(k, _MISSING)
            sub_right = right.get(k, _MISSING)
            sub_path = f"{path}.{k}"
            if sub_left is _MISSING or sub_right is _MISSING:
                diffs.append(Diff(
                    path=sub_path,
                    kind="missing_field",
                    left=None if sub_left is _MISSING else sub_left,
                    right=None if sub_right is _MISSING else sub_right,
                ))
            else:
                diffs.extend(diff_json(sub_left, sub_right, sub_path, k))
    elif isinstance(left, list) and isinstance(right, list):
        n = max(len(left), len(right))
        for i in range(n):
            sub_left = left[i] if i < len(left) else _MISSING
            sub_right = right[i] if i < len(right) else _MISSING
            sub_path = f"{path}[{i}]"
            if sub_left is _MISSING or sub_right is _MISSING:
                diffs.append(Diff(
                    path=sub_path,
                    kind="missing_field",
                    left=None if sub_left is _MISSING else sub_left,
                    right=None if sub_right is _MISSING else sub_right,
                ))
            else:
                diffs.extend(diff_json(sub_left, sub_right, sub_path, key))
    else:
        if left != right:
            diffs.append(Diff(
                path=path,
                kind=classify(path, key, left, right),
                left=left,
                right=right,
            ))
    return diffs


def _by_kind(diffs: list[Diff]) -> dict[str, int]:
    out: dict[str, int] = {}
    for d in diffs:
        out[d.kind] = out.get(d.kind, 0) + 1
    return dict(sorted(out.items()))


def diff_files(left_path: Path, right_path: Path) -> dict[str, Any]:
    left = json.loads(left_path.read_text(encoding="utf-8"))
    right = json.loads(right_path.read_text(encoding="utf-8"))
    diffs = diff_json(left, right)
    return {
        "left": str(left_path),
        "right": str(right_path),
        "divergent": bool(diffs),
        "count": len(diffs),
        "by_kind": _by_kind(diffs),
        "diffs": [d.to_dict() for d in diffs],
    }


def self_check() -> int:
    failures: list[str] = []

    def expect(name: str, condition: bool, detail: str = "") -> None:
        if not condition:
            failures.append(f"{name}: {detail}")
        print(f"  [{'PASS' if condition else 'FAIL'}] {name}")

    # 1. Identical → no diffs.
    a = {"x": 1, "hash": "sha256:" + "a" * 64, "status": "VERIFIED"}
    res = diff_json(a, a)
    expect("identical_no_diff", res == [], f"got {res}")

    # 2. Hash mismatch.
    b = {**a, "hash": "sha256:" + "b" * 64}
    res = diff_json(a, b)
    expect("hash_mismatch_classified",
           len(res) == 1 and res[0].kind == "hash_mismatch", str(res))

    # 3. Lifecycle state mismatch.
    c = {**a, "status": "TAMPERED"}
    res = diff_json(a, c)
    expect("lifecycle_state_classified",
           len(res) == 1 and res[0].kind == "lifecycle_state_mismatch", str(res))

    # 4. Missing field.
    d = {"x": 1}
    res = diff_json(a, d)
    expect("missing_field_detected",
           any(r.kind == "missing_field" for r in res), str(res))

    # 5. Canonicalization mismatch.
    e = {"canonicalization": "RFC8785-JCS"}
    f = {"canonicalization": "RFC8785-JCS-v2"}
    res = diff_json(e, f)
    expect("canonicalization_classified",
           len(res) == 1 and res[0].kind == "canonicalization_mismatch", str(res))

    # 6. Authority chain mismatch (nested under protocol).
    g = {"protocol": {"required_quorum": 2}}
    h = {"protocol": {"required_quorum": 3}}
    res = diff_json(g, h)
    expect("authority_chain_classified_nested",
           len(res) == 1 and res[0].kind == "authority_chain_mismatch", str(res))

    # 7. Authority chain mismatch — commit_chain element value.
    i = {"commit_chain": [{"hash": "sha256:" + "1" * 64, "stage": 1}]}
    j = {"commit_chain": [{"hash": "sha256:" + "2" * 64, "stage": 1}]}
    res = diff_json(i, j)
    expect("authority_chain_array_path",
           len(res) == 1 and res[0].kind == "authority_chain_mismatch", str(res))

    # 8. Generic value mismatch (no special classification).
    k = {"description": "alpha"}
    l = {"description": "beta"}
    res = diff_json(k, l)
    expect("generic_value_mismatch",
           len(res) == 1 and res[0].kind == "value_mismatch", str(res))

    # 9. Round-trip: real conformance report against itself.
    report = REPO_ROOT / "reports" / "conformance-report.json"
    if report.is_file():
        out = diff_files(report, report)
        expect("real_report_self_diff_empty",
               out["divergent"] is False and out["count"] == 0, str(out))

    if failures:
        print(f"\nFAIL: {len(failures)} self-check failures")
        for f in failures:
            print(f"  ↳ {f}")
        return 1
    print("\nPASS: replay_diff self-check")
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = list(argv) if argv is not None else sys.argv[1:]
    if not argv:
        sys.stderr.write(__doc__ or "")
        return 2

    if argv[0] == "self-check":
        return self_check()

    if argv[0] == "diff":
        argv = argv[1:]

    parser = argparse.ArgumentParser(prog="replay_diff", add_help=True)
    parser.add_argument("left", type=Path)
    parser.add_argument("right", type=Path)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    try:
        report = diff_files(args.left, args.right)
    except FileNotFoundError as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 2
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"error: invalid JSON: {exc}\n")
        return 2

    if not args.quiet:
        print(json.dumps(report, sort_keys=True, indent=2))
    return 1 if report["divergent"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
