#!/usr/bin/env python3
"""Generate the canonicalization golden corpus.

Reads every ``canonicalization/corpus/*.json`` file in lexicographic filename
order, canonicalizes its parsed JSON value with the runtime canonicalizer
``intellagent_runtime.canonical.canonical_json_bytes``, computes the SHA-256
of the canonical bytes, and writes:

  - ``canonicalization/golden/golden-canonical.json``
  - ``canonicalization/golden/golden-digests.json``

Output files are written via ``canonical_pretty`` (sorted keys, 2-space
indent, trailing newline) so they are themselves byte-stable across runs.

Fail-closed: any unparseable corpus file aborts the generator with a non-zero
exit code; no partial golden files are written.

Exit code: 0 on success, 1 on corpus or I/O error.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Make the runtime importable when this script is invoked directly.
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from intellagent_runtime.canonical import (  # noqa: E402
    canonical_json_bytes,
    canonical_pretty,
    sha256_hex,
    write_atomic,
)

CANONICALIZATION_ROOT = REPO_ROOT / "canonicalization"
CORPUS_DIR = CANONICALIZATION_ROOT / "corpus"
GOLDEN_DIR = CANONICALIZATION_ROOT / "golden"
GOLDEN_CANONICAL = GOLDEN_DIR / "golden-canonical.json"
GOLDEN_DIGESTS = GOLDEN_DIR / "golden-digests.json"

SCHEMA_VERSION = "0.1.0"
CANONICALIZATION_SCHEME_ID = "python-json-sortkeys-compact-utf8"
DIGEST_ALGORITHM = "SHA-256"


def _file_id(path: Path) -> str:
    """Return the corpus file identifier (stem, e.g. ``001-simple-object``)."""
    return path.stem


def _load_corpus(corpus_dir: Path) -> list[tuple[str, Any]]:
    """Read every JSON file under ``corpus_dir`` in filename order.

    Fails closed if any file is not valid JSON.
    """
    if not corpus_dir.is_dir():
        raise FileNotFoundError(f"corpus directory not found: {corpus_dir}")

    files = sorted(p for p in corpus_dir.glob("*.json") if p.is_file())
    if not files:
        raise RuntimeError(f"corpus is empty: {corpus_dir}")

    loaded: list[tuple[str, Any]] = []
    for path in files:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}: invalid JSON ({exc})") from exc
        loaded.append((_file_id(path), value))
    return loaded


def _build_golden(
    corpus: list[tuple[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any], str]:
    """Return (canonical_payload, digests_payload, corpus_sha256)."""
    canonical_entries: dict[str, dict[str, str]] = {}
    digests_entries: dict[str, str] = {}
    corpus_hasher = hashlib.sha256()

    for file_id, value in corpus:
        cbytes = canonical_json_bytes(value)
        digest = sha256_hex(cbytes)
        canonical_entries[file_id] = {
            "canonical_hex": cbytes.hex(),
            "canonical_utf8": cbytes.decode("utf-8"),
        }
        digests_entries[file_id] = digest

        # corpus_sha256: stable concatenation of (file_id, canonical_bytes) in
        # filename-sorted order, separated by NUL bytes to remove ambiguity.
        corpus_hasher.update(file_id.encode("utf-8"))
        corpus_hasher.update(b"\x00")
        corpus_hasher.update(cbytes)
        corpus_hasher.update(b"\x00")

    corpus_sha = "sha256:" + corpus_hasher.hexdigest()

    canonical_payload = {
        "schema_version": SCHEMA_VERSION,
        "canonicalization": CANONICALIZATION_SCHEME_ID,
        "entries": canonical_entries,
    }
    digests_payload = {
        "schema_version": SCHEMA_VERSION,
        "canonicalization": CANONICALIZATION_SCHEME_ID,
        "digest_algorithm": DIGEST_ALGORITHM,
        "corpus_sha256": corpus_sha,
        "digests": digests_entries,
    }
    return canonical_payload, digests_payload, corpus_sha


def main() -> int:
    try:
        corpus = _load_corpus(CORPUS_DIR)
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    canonical_payload, digests_payload, corpus_sha = _build_golden(corpus)

    GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
    write_atomic(GOLDEN_CANONICAL, canonical_pretty(canonical_payload))
    write_atomic(GOLDEN_DIGESTS, canonical_pretty(digests_payload))

    print(f"OK: wrote {GOLDEN_CANONICAL.relative_to(REPO_ROOT)}")
    print(f"OK: wrote {GOLDEN_DIGESTS.relative_to(REPO_ROOT)}")
    print(f"OK: corpus_sha256: {corpus_sha}")
    print(f"OK: {len(corpus)} corpus entries canonicalized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
