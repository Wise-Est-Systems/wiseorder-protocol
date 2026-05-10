#!/usr/bin/env python3
"""Verify the canonicalization golden corpus.

Recomputes canonical bytes and SHA-256 digests for every corpus entry and
compares the result against the committed ``golden-canonical.json`` and
``golden-digests.json`` files.

Exits 0 only if every byte matches. On any mismatch, prints the offending
file id, the mismatched field, and aborts with exit code 1.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from canonicalization.tools.generate_golden import (  # noqa: E402
    GOLDEN_CANONICAL,
    GOLDEN_DIGESTS,
    CORPUS_DIR,
    _build_golden,
    _load_corpus,
)
from intellagent_runtime.canonical import canonical_pretty  # noqa: E402


def _read_committed(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"missing committed golden file: {path}")
    return path.read_text(encoding="utf-8")


def main() -> int:
    try:
        corpus = _load_corpus(CORPUS_DIR)
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    canonical_payload, digests_payload, corpus_sha = _build_golden(corpus)
    expected_canonical_text = canonical_pretty(canonical_payload)
    expected_digests_text = canonical_pretty(digests_payload)

    try:
        committed_canonical_text = _read_committed(GOLDEN_CANONICAL)
        committed_digests_text = _read_committed(GOLDEN_DIGESTS)
    except FileNotFoundError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        print(
            "HINT: run 'make canonicalization-golden' to generate the golden files.",
            file=sys.stderr,
        )
        return 1

    failures: list[str] = []

    if committed_canonical_text != expected_canonical_text:
        # Identify per-entry divergence for actionable output.
        try:
            committed = json.loads(committed_canonical_text)
            expected = canonical_payload
            committed_entries = committed.get("entries", {})
            expected_entries = expected["entries"]
            mismatch_entries = sorted(
                set(committed_entries) | set(expected_entries),
                key=str,
            )
            for entry_id in mismatch_entries:
                c = committed_entries.get(entry_id)
                e = expected_entries.get(entry_id)
                if c != e:
                    failures.append(
                        f"  golden-canonical.json: entry '{entry_id}' diverges\n"
                        f"    committed: {c}\n"
                        f"    observed:  {e}"
                    )
        except json.JSONDecodeError:
            failures.append(
                "  golden-canonical.json: committed file is not valid JSON"
            )

    if committed_digests_text != expected_digests_text:
        try:
            committed = json.loads(committed_digests_text)
            committed_digests = committed.get("digests", {})
            expected_digests = digests_payload["digests"]
            committed_corpus = committed.get("corpus_sha256")
            expected_corpus = digests_payload["corpus_sha256"]
            if committed_corpus != expected_corpus:
                failures.append(
                    "  golden-digests.json: corpus_sha256 diverges\n"
                    f"    committed: {committed_corpus}\n"
                    f"    observed:  {expected_corpus}"
                )
            for entry_id in sorted(set(committed_digests) | set(expected_digests)):
                c = committed_digests.get(entry_id)
                e = expected_digests.get(entry_id)
                if c != e:
                    failures.append(
                        f"  golden-digests.json: digest '{entry_id}' diverges\n"
                        f"    committed: {c}\n"
                        f"    observed:  {e}"
                    )
        except json.JSONDecodeError:
            failures.append("  golden-digests.json: committed file is not valid JSON")

    if failures:
        print(
            f"FAIL: canonicalization golden mismatch ({len(failures)} divergence(s)):",
            file=sys.stderr,
        )
        for line in failures:
            print(line, file=sys.stderr)
        print(
            "\nHINT: if the divergence is intentional (corpus or canonicalizer "
            "change), rerun 'make canonicalization-golden' and commit the result.",
            file=sys.stderr,
        )
        return 1

    print(f"OK: {len(corpus)} corpus entries verified.")
    print(f"OK: corpus_sha256: {corpus_sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
