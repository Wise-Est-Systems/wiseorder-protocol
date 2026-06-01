#!/usr/bin/env python3
"""verify_stack.py — confirm every public repo's STACK_ROLE.md matches the
fingerprint in STRUCTURE.md.

Exit codes:
  0 — all fingerprints match
  1 — at least one drift detected
  2 — error fetching or parsing

Usage:
    python tools/verify_stack.py
    python tools/verify_stack.py --offline /path/to/repos
"""
from __future__ import annotations
import argparse
import hashlib
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

STRUCTURE_PATH = Path(__file__).resolve().parent.parent / "STRUCTURE.md"
ORG = "Wise-Est-Systems"
RAW_BASE = f"https://raw.githubusercontent.com/{ORG}"

ROW_RE = re.compile(
    r"^\|\s*([a-z0-9][a-z0-9-]*)\s*\|\s*`([^`]+)`\s*\|\s*`([0-9a-f]{64})`\s*\|",
    re.MULTILINE,
)


def parse_fingerprints(structure_md: str) -> list[tuple[str, str, str]]:
    """Return list of (repo_name, path, expected_sha256) from the Fingerprints section."""
    after = structure_md.split("## Fingerprints", 1)
    if len(after) < 2:
        raise RuntimeError("STRUCTURE.md: no '## Fingerprints' section")
    body = after[1].split("\n## ", 1)[0]
    rows = ROW_RE.findall(body)
    if not rows:
        raise RuntimeError("STRUCTURE.md: no fingerprint rows parsed")
    return rows


def fetch_role(repo: str, path: str) -> bytes:
    url = f"{RAW_BASE}/{repo}/main/{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "verify-stack/1.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read()


def local_role(base: Path, repo: str, path: str) -> bytes:
    return (base / repo / path).read_bytes()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--offline",
        type=Path,
        default=None,
        help="directory containing each repo's checkout (skips GitHub fetch)",
    )
    args = parser.parse_args()

    if not STRUCTURE_PATH.exists():
        print(f"FATAL: {STRUCTURE_PATH} not found", file=sys.stderr)
        return 2

    structure_md = STRUCTURE_PATH.read_text()
    try:
        rows = parse_fingerprints(structure_md)
    except RuntimeError as exc:
        print(f"FATAL: {exc}", file=sys.stderr)
        return 2

    drift = 0
    for repo, path, expected in rows:
        try:
            content = (
                local_role(args.offline, repo, path)
                if args.offline
                else fetch_role(repo, path)
            )
        except (urllib.error.URLError, FileNotFoundError, OSError) as exc:
            print(f"[{repo}] ERROR reading {path}: {exc}", file=sys.stderr)
            drift += 1
            continue

        actual = hashlib.sha256(content).hexdigest()
        if actual == expected:
            print(f"[{repo}] OK    {actual}")
        else:
            print(f"[{repo}] DRIFT expected={expected} actual={actual}")
            drift += 1

    total = len(rows)
    print(f"\n{total} rows checked, {drift} drift")
    return 0 if drift == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
