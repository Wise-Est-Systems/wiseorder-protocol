#!/usr/bin/env python3
"""WiseOrder/Intellagent — pseudocode-marker scanner.

Scans markdown files for pseudocode markers inside Python code blocks. Code
blocks marked with the literal first comment ``# interface example`` may
contain ``...`` ellipsis statements (Protocol method bodies); all other
markers are banned unconditionally everywhere.

Banned markers (per repo rule):

  - Bare ``...`` ellipsis as a statement                 (rule: ellipsis_statement)
  - Bare ``pass`` as a statement                          (rule: bare_pass)
  - ``return ...`` anywhere on a line                     (rule: return_ellipsis)
  - ``TODO`` anywhere on a line                           (rule: todo)
  - ``NotImplemented`` / ``NotImplementedError``          (rule: not_implemented)

Excluded files:
  - SPEC.md  (normative; its code blocks are illustrative protocol semantics)

Exit code: 0 if clean, 1 if any violation is found, 2 on usage error.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

DOCS_GLOBS: tuple[str, ...] = (
    "*.md",
    "docs/**/*.md",
    "interop/**/*.md",
    "vectors/**/*.md",
    "intellagent_runtime/**/*.md",
    "reports/canonical/**/*.md",
    "reports/repo_health/**/*.md",
)

EXCLUDED_FILENAMES: frozenset[str] = frozenset({"SPEC.md"})

# Fence detection.
_FENCE_OPEN_PYTHON_RE = re.compile(r"^\s*```python\s*$")
_FENCE_CLOSE_RE = re.compile(r"^\s*```\s*$")

# Markers (banned).
_ELLIPSIS_STATEMENT_RE = re.compile(r"^\s*\.\.\.\s*$")
_BARE_PASS_RE = re.compile(r"^\s*pass\s*$")
_RETURN_ELLIPSIS_RE = re.compile(r"\breturn\s+\.\.\.")
_TODO_RE = re.compile(r"\bTODO\b")
_NOT_IMPLEMENTED_RE = re.compile(r"\bNotImplemented(Error)?\b")

# Allowlist marker. The first non-blank line inside a Python code block may be
# this exact comment, in which case ``...`` ellipsis statements are permitted
# (intended for Protocol / abstract-interface examples). All other markers are
# banned regardless.
_INTERFACE_MARKER = "# interface example"


@dataclass(frozen=True)
class Violation:
    file: str
    line: int
    rule: str
    excerpt: str


def _scan_file(path: Path) -> list[Violation]:
    violations: list[Violation] = []
    in_block = False
    block_is_interface = False
    block_first_seen_nonblank = False

    for lineno, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line

        if not in_block:
            if _FENCE_OPEN_PYTHON_RE.match(line):
                in_block = True
                block_is_interface = False
                block_first_seen_nonblank = False
            continue

        if _FENCE_CLOSE_RE.match(line):
            in_block = False
            continue

        # Detect the interface allowlist marker on the first non-blank line.
        if not block_first_seen_nonblank and line.strip():
            block_first_seen_nonblank = True
            if line.strip() == _INTERFACE_MARKER:
                block_is_interface = True

        # Apply rules.
        if _ELLIPSIS_STATEMENT_RE.match(line) and not block_is_interface:
            violations.append(
                Violation(str(path), lineno, "ellipsis_statement", line.rstrip())
            )
        if _BARE_PASS_RE.match(line):
            violations.append(
                Violation(str(path), lineno, "bare_pass", line.rstrip())
            )
        if _RETURN_ELLIPSIS_RE.search(line):
            violations.append(
                Violation(str(path), lineno, "return_ellipsis", line.rstrip())
            )
        if _TODO_RE.search(line):
            violations.append(
                Violation(str(path), lineno, "todo", line.rstrip())
            )
        if _NOT_IMPLEMENTED_RE.search(line):
            violations.append(
                Violation(str(path), lineno, "not_implemented", line.rstrip())
            )

    return violations


def _discover_files(repo_root: Path) -> list[Path]:
    found: set[Path] = set()
    for glob in DOCS_GLOBS:
        for p in repo_root.glob(glob):
            if not p.is_file() or p.suffix != ".md":
                continue
            if p.name in EXCLUDED_FILENAMES:
                continue
            found.add(p.resolve())
    return sorted(found)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Scan docs for pseudocode markers in Python code blocks."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help=f"repository root (default: {REPO_ROOT})",
    )
    parser.add_argument(
        "--include-spec",
        action="store_true",
        help="also scan SPEC.md (normally excluded; its code is normative-illustrative)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="suppress per-violation lines; emit only the summary line",
    )
    args = parser.parse_args(argv)

    files = _discover_files(args.repo_root)
    if args.include_spec:
        spec = (args.repo_root / "SPEC.md").resolve()
        if spec.is_file() and spec not in files:
            files.append(spec)

    violations: list[Violation] = []
    for p in files:
        violations.extend(_scan_file(p))

    if not violations:
        print(
            f"OK: scanned {len(files)} markdown file(s); "
            "no pseudocode markers found in Python code blocks."
        )
        return 0

    files_with_violations = sorted({v.file for v in violations})
    if not args.quiet:
        print(
            f"FAIL: {len(violations)} pseudocode marker(s) found across "
            f"{len(files_with_violations)} file(s):"
        )
        print()
        for v in violations:
            try:
                rel = str(Path(v.file).resolve().relative_to(args.repo_root.resolve()))
            except ValueError:
                rel = v.file
            print(f"  {rel}:{v.line}: {v.rule}")
            print(f"    {v.excerpt!r}")
        print()
    print(
        f"FAIL: {len(violations)} pseudocode marker(s) across "
        f"{len(files_with_violations)} file(s)."
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
