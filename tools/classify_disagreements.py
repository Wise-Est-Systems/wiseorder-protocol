#!/usr/bin/env python3
"""Classify triple_sweep disagreements by cross-implementation signature.

Reads the most recent (or specified) reports/triple_sweep/<ts>/disagreements.jsonl,
computes a stable bug signature per record, and groups records by signature.

Signature components (in order):
  - which subset of {python, go, rust} agreed (e.g. "py+rust", "py+go", "py", "all-3-different")
  - which implementation differed (the outlier)
  - the byte-pattern of the difference (escape-vs-raw, len-delta sign, contains-u2028 marker,
    contains-bigint marker, contains-emoji marker, etc.)

Output:
  reports/triple_sweep/<ts>/classified_bugs.json   (signature -> {count, examples, ...})
  reports/triple_sweep/<ts>/bugs/<signature>.md    (one human-readable bug report each)

Usage:
  classify_disagreements.py [--run <run_dir>]
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
SWEEP_ROOT = REPO_ROOT / "reports" / "triple_sweep"

IMPLS = ("python", "go", "rust")


def _latest_run() -> Path:
    runs = sorted([p for p in SWEEP_ROOT.iterdir() if p.is_dir()])
    if not runs:
        raise SystemExit("no sweep runs found under reports/triple_sweep/")
    return runs[-1]


def _decode(b64: str) -> bytes:
    try:
        return base64.b64decode(b64)
    except Exception:  # noqa: BLE001
        return b""


def _shape_of_value(value: Any) -> set[str]:
    """Surface markers about a JSON value used in bug signatures."""
    markers: set[str] = set()

    def walk(v: Any) -> None:
        if isinstance(v, dict):
            for k, sub in v.items():
                walk(k)
                walk(sub)
        elif isinstance(v, list):
            for sub in v:
                walk(sub)
        elif isinstance(v, str):
            for ch in v:
                cp = ord(ch)
                if cp == 0x2028:
                    markers.add("contains-U+2028")
                elif cp == 0x2029:
                    markers.add("contains-U+2029")
                elif 0x1F600 <= cp <= 0x1F6FF:
                    markers.add("contains-emoji")
                elif cp == 0xFEFF:
                    markers.add("contains-BOM")
                elif cp <= 0x001F:
                    markers.add("contains-C0-control")
                elif 0x0080 <= cp <= 0x009F:
                    markers.add("contains-C1-control")
                elif cp == 0x007F:
                    markers.add("contains-DEL")
                elif cp > 0xFFFF:
                    markers.add("contains-SMP")
        elif isinstance(v, bool):
            return
        elif isinstance(v, int):
            if v > 2**53 or v < -(2**53):
                markers.add("contains-bigint>2^53")
            if v > 2**63 - 1 or v < -(2**63):
                markers.add("contains-bigint>i64")
            if v >= 2**64:
                markers.add("contains-bigint>=2^64")

    walk(value)
    return markers


def _signature(rec: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """Return (signature, extra_meta) for a single disagreement record."""
    results = rec.get("results", {})
    digests = {}
    for impl in IMPLS:
        r = results.get(impl)
        if r and r.get("ok"):
            digests[impl] = r["sha256_hex"]
    # Group implementations by their digest.
    by_digest: dict[str, list[str]] = defaultdict(list)
    for impl, d in digests.items():
        by_digest[d].append(impl)
    groups = sorted(by_digest.values(), key=lambda g: (len(g) * -1, g))

    if len(groups) == 1:
        # All three agreed on bytes but disagreed structurally? Shouldn't happen.
        partition = "all-agree"
        outlier = "none"
    elif len(groups) == 2:
        # One impl differs from the other two.
        majority = sorted(groups, key=lambda g: -len(g))[0]
        minority = sorted(groups, key=lambda g: -len(g))[1]
        partition = f"agree:{'+'.join(sorted(majority))}|outlier:{'+'.join(sorted(minority))}"
        outlier = "+".join(sorted(minority))
    else:
        partition = "all-three-different"
        outlier = "all-three-different"

    markers = sorted(_shape_of_value(rec.get("input_value")))
    marker_str = ",".join(markers) if markers else "no-markers"

    # Length-pattern: which impl produced the longest canon (escaping clue).
    lengths = {impl: results[impl].get("length", -1) for impl in IMPLS if impl in results and results[impl].get("ok")}
    if lengths:
        max_impl = max(lengths, key=lambda k: lengths[k])
        min_impl = min(lengths, key=lambda k: lengths[k])
        length_pattern = f"longest:{max_impl},shortest:{min_impl}"
    else:
        length_pattern = "no-lengths"

    signature = f"{partition} | {length_pattern} | markers:{marker_str}"
    meta = {
        "partition": partition,
        "outlier": outlier,
        "length_pattern": length_pattern,
        "markers": markers,
    }
    return signature, meta


def _minimal_repro(rec: dict[str, Any]) -> dict[str, Any]:
    results = rec.get("results", {})
    canons = {}
    for impl in IMPLS:
        r = results.get(impl)
        if not r or not r.get("ok"):
            continue
        raw = _decode(r["canonical_b64"])
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            text = repr(raw)
        canons[impl] = {
            "length": r["length"],
            "sha256_hex": r["sha256_hex"],
            "canonical_text": text,
        }
    return {
        "input_value": rec.get("input_value"),
        "input_path": rec.get("input_path"),
        "generator": rec.get("generator"),
        "canonical_per_impl": canons,
    }


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", type=Path, default=None)
    args = ap.parse_args(argv)

    run_dir = args.run if args.run else _latest_run()
    if not run_dir.is_dir():
        raise SystemExit(f"not a directory: {run_dir}")

    disagreements_path = run_dir / "disagreements.jsonl"
    if not disagreements_path.is_file():
        raise SystemExit(f"missing: {disagreements_path}")

    buckets: dict[str, dict[str, Any]] = {}
    total = 0
    with disagreements_path.open() as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            sig, meta = _signature(rec)
            total += 1
            bucket = buckets.setdefault(
                sig,
                {
                    "signature": sig,
                    "meta": meta,
                    "count": 0,
                    "generators": defaultdict(int),
                    "examples": [],
                },
            )
            bucket["count"] += 1
            bucket["generators"][rec.get("generator", "?")] += 1
            if len(bucket["examples"]) < 3:
                bucket["examples"].append(_minimal_repro(rec))

    # Serialize buckets (convert defaultdicts).
    classified: list[dict[str, Any]] = []
    for sig, bucket in sorted(buckets.items(), key=lambda kv: -kv[1]["count"]):
        bucket_out = dict(bucket)
        bucket_out["generators"] = dict(bucket["generators"])
        classified.append(bucket_out)

    out_path = run_dir / "classified_bugs.json"
    out_path.write_text(
        json.dumps(
            {"total_disagreements": total, "signatures": len(classified), "buckets": classified},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    bugs_dir = run_dir / "bugs"
    bugs_dir.mkdir(exist_ok=True)
    for i, bucket in enumerate(classified, start=1):
        slug = f"sig-{i:02d}"
        md_path = bugs_dir / f"{slug}.md"
        lines = []
        lines.append(f"# Disagreement signature {i}")
        lines.append("")
        lines.append(f"**Signature:** `{bucket['signature']}`")
        lines.append("")
        lines.append(f"**Count:** {bucket['count']}")
        lines.append("")
        lines.append("**Partition:** " + bucket["meta"]["partition"])
        lines.append("")
        lines.append("**Outlier:** " + bucket["meta"]["outlier"])
        lines.append("")
        lines.append("**Markers:** " + (", ".join(bucket["meta"]["markers"]) or "none"))
        lines.append("")
        lines.append("**Length pattern:** " + bucket["meta"]["length_pattern"])
        lines.append("")
        lines.append("**By generator:**")
        for g, c in sorted(bucket["generators"].items(), key=lambda kv: -kv[1]):
            lines.append(f"  - {g}: {c}")
        lines.append("")
        lines.append("## Examples")
        lines.append("")
        for j, ex in enumerate(bucket["examples"], start=1):
            lines.append(f"### Example {j}")
            lines.append("")
            lines.append(f"- generator: `{ex['generator']}`")
            lines.append(f"- input: `{json.dumps(ex['input_value'], ensure_ascii=False)}`")
            lines.append("")
            lines.append("Canonical per implementation:")
            for impl in IMPLS:
                c = ex["canonical_per_impl"].get(impl)
                if c is None:
                    lines.append(f"- **{impl}**: <missing>")
                else:
                    lines.append(f"- **{impl}** (len {c['length']}, sha {c['sha256_hex'][:16]}...):")
                    lines.append("")
                    lines.append("  ```")
                    text = c["canonical_text"]
                    if len(text) > 200:
                        text = text[:200] + "  ...[truncated]"
                    lines.append("  " + text)
                    lines.append("  ```")
            lines.append("")
        md_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"run_dir: {run_dir}")
    print(f"total_disagreements: {total}")
    print(f"distinct_signatures: {len(classified)}")
    print(f"output: {out_path}")
    print(f"per-signature reports: {bugs_dir}/")
    print()
    print("Top signatures (count, signature):")
    for bucket in classified[:10]:
        print(f"  {bucket['count']:5d}  {bucket['signature']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
