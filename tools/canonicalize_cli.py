#!/usr/bin/env python3
"""Canonicalize a JSON file via intellagent_runtime and print a JSON report.

Output (single line, on stdout):
  {"canonical_b64":"<base64>","sha256_hex":"<hex>","length":<int>}

Exit codes:
  0  success
  2  usage / I/O / JSON parse error

Used by tools/triple_sweep.py to diff Python vs Go vs Rust canonical bytes.
"""

from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from intellagent_runtime.canonical import canonical_json_bytes, sha256_hex  # noqa: E402


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: canonicalize_cli.py <input.json>", file=sys.stderr)
        return 2
    path = Path(argv[1])
    try:
        raw = path.read_bytes()
    except OSError as exc:
        print(f"error reading {path}: {exc}", file=sys.stderr)
        return 2
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(f"error parsing {path}: {exc}", file=sys.stderr)
        return 2
    canonical = canonical_json_bytes(value)
    digest = sha256_hex(canonical)
    if digest.startswith("sha256:"):
        digest = digest[len("sha256:") :]
    report = {
        "canonical_b64": base64.b64encode(canonical).decode("ascii"),
        "sha256_hex": digest,
        "length": len(canonical),
    }
    sys.stdout.write(json.dumps(report, separators=(",", ":")) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
