"""Tests for the canonicalization golden corpus.

These tests pin:

- determinism of golden generation (same corpus → same bytes, twice);
- success of golden verification against the committed files;
- key-order normalization;
- whitespace normalization;
- Unicode stability;
- numeric formatting stability;
- Class A artifact digest stability.

The committed golden files are the source of truth. If the runtime
canonicalizer changes intentionally, rerun ``make canonicalization-golden``
and commit the result; these tests will then re-pin the new state.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
CANONICALIZATION_ROOT = REPO_ROOT / "canonicalization"
CORPUS_DIR = CANONICALIZATION_ROOT / "corpus"
GOLDEN_DIR = CANONICALIZATION_ROOT / "golden"
GOLDEN_CANONICAL = GOLDEN_DIR / "golden-canonical.json"
GOLDEN_DIGESTS = GOLDEN_DIR / "golden-digests.json"
GENERATE_SCRIPT = CANONICALIZATION_ROOT / "tools" / "generate_golden.py"
VERIFY_SCRIPT = CANONICALIZATION_ROOT / "tools" / "verify_golden.py"

# Make the runtime importable.
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from intellagent_runtime.canonical import (  # noqa: E402
    canonical_json_bytes,
    sha256_hex,
)


# ---- Helpers -------------------------------------------------------------


def _run(script: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )


def _load_committed_digests() -> dict[str, str]:
    payload = json.loads(GOLDEN_DIGESTS.read_text(encoding="utf-8"))
    return payload["digests"]


def _load_committed_corpus_sha() -> str:
    payload = json.loads(GOLDEN_DIGESTS.read_text(encoding="utf-8"))
    return payload["corpus_sha256"]


# ---- Tests ---------------------------------------------------------------


def test_corpus_directory_present_with_ten_entries() -> None:
    files = sorted(CORPUS_DIR.glob("*.json"))
    assert len(files) == 10, f"expected 10 corpus files, found {len(files)}"


def test_committed_golden_files_present() -> None:
    assert GOLDEN_CANONICAL.is_file(), "golden-canonical.json missing"
    assert GOLDEN_DIGESTS.is_file(), "golden-digests.json missing"


def test_verify_golden_passes_against_committed() -> None:
    result = _run(VERIFY_SCRIPT)
    assert result.returncode == 0, (
        f"verify_golden.py failed:\n{result.stdout}\n{result.stderr}"
    )
    assert "OK:" in result.stdout


def test_generate_golden_is_deterministic() -> None:
    """Two runs of the generator MUST produce byte-identical golden files."""
    first_canonical = GOLDEN_CANONICAL.read_bytes()
    first_digests = GOLDEN_DIGESTS.read_bytes()

    result = _run(GENERATE_SCRIPT)
    assert result.returncode == 0, result.stderr
    second_canonical = GOLDEN_CANONICAL.read_bytes()
    second_digests = GOLDEN_DIGESTS.read_bytes()

    assert first_canonical == second_canonical, (
        "golden-canonical.json drifted across two generator runs"
    )
    assert first_digests == second_digests, (
        "golden-digests.json drifted across two generator runs"
    )


def test_key_order_normalizes() -> None:
    """Two semantically-equal objects with different key order MUST canonicalize equal."""
    a = canonical_json_bytes({"b": 2, "a": 1})
    b = canonical_json_bytes({"a": 1, "b": 2})
    assert a == b == b'{"a":1,"b":2}'


def test_whitespace_normalizes_against_corpus_009() -> None:
    """Corpus 009 has heavy whitespace; canonical bytes have no whitespace."""
    raw = (CORPUS_DIR / "009-whitespace.json").read_text(encoding="utf-8")
    parsed = json.loads(raw)
    canonical = canonical_json_bytes(parsed)
    # No spaces, no newlines, no tabs in canonical output.
    assert b" " not in canonical
    assert b"\n" not in canonical
    assert b"\t" not in canonical
    # Pinned exact bytes.
    assert canonical == b'{"a":1,"b":2,"c":[10,20,30]}'


def test_unicode_is_stable() -> None:
    """Corpus 004 unicode digest MUST match committed value across runs."""
    raw = (CORPUS_DIR / "004-unicode.json").read_text(encoding="utf-8")
    parsed = json.loads(raw)
    canonical = canonical_json_bytes(parsed)
    digest = sha256_hex(canonical)
    assert digest == _load_committed_digests()["004-unicode"]
    # Non-ASCII characters survive as raw UTF-8 bytes (not \uXXXX).
    assert "café".encode("utf-8") in canonical
    assert "日本語".encode("utf-8") in canonical
    assert "🌍".encode("utf-8") in canonical


def test_number_formatting_is_stable() -> None:
    """Number-corpus digests MUST match committed values."""
    committed = _load_committed_digests()
    for entry in ("005-number-integer", "006-number-float"):
        raw = (CORPUS_DIR / f"{entry}.json").read_text(encoding="utf-8")
        parsed = json.loads(raw)
        canonical = canonical_json_bytes(parsed)
        digest = sha256_hex(canonical)
        assert digest == committed[entry], (
            f"{entry}: digest drift\n"
            f"  committed: {committed[entry]}\n"
            f"  observed:  {digest}"
        )


def test_class_a_artifact_digest_is_stable() -> None:
    """Corpus 010 (realistic Class A artifact) digest MUST match committed value."""
    raw = (CORPUS_DIR / "010-wiseorder-class-a.json").read_text(encoding="utf-8")
    parsed = json.loads(raw)
    canonical = canonical_json_bytes(parsed)
    digest = sha256_hex(canonical)
    assert digest == _load_committed_digests()["010-wiseorder-class-a"]


def test_corpus_sha256_matches_independent_recomputation() -> None:
    """Recompute corpus_sha256 from scratch and compare to committed value."""
    files = sorted(CORPUS_DIR.glob("*.json"))
    hasher = hashlib.sha256()
    for path in files:
        file_id = path.stem
        parsed = json.loads(path.read_text(encoding="utf-8"))
        cbytes = canonical_json_bytes(parsed)
        hasher.update(file_id.encode("utf-8"))
        hasher.update(b"\x00")
        hasher.update(cbytes)
        hasher.update(b"\x00")
    expected = "sha256:" + hasher.hexdigest()
    assert expected == _load_committed_corpus_sha()


def test_verify_golden_fails_on_corpus_mutation(tmp_path: Path) -> None:
    """If a corpus file is mutated, verify_golden MUST exit non-zero."""
    target = CORPUS_DIR / "001-simple-object.json"
    backup = target.read_bytes()
    try:
        target.write_text('{"b": 99, "a": 1}\n', encoding="utf-8")
        result = _run(VERIFY_SCRIPT)
        assert result.returncode == 1, (
            "verify_golden.py should fail on mutated corpus, got "
            f"exit {result.returncode}\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert "FAIL" in result.stderr or "FAIL" in result.stdout
    finally:
        target.write_bytes(backup)
    # Sanity: post-restore, verifier passes again.
    result = _run(VERIFY_SCRIPT)
    assert result.returncode == 0, (
        f"verifier failed after restoration:\n{result.stdout}\n{result.stderr}"
    )


def test_canonical_hex_decodes_to_canonical_utf8() -> None:
    """In golden-canonical.json, the hex form MUST decode to the utf8 form."""
    payload = json.loads(GOLDEN_CANONICAL.read_text(encoding="utf-8"))
    for entry_id, fields in payload["entries"].items():
        decoded = bytes.fromhex(fields["canonical_hex"]).decode("utf-8")
        assert decoded == fields["canonical_utf8"], (
            f"{entry_id}: hex/utf8 mismatch in committed golden"
        )


@pytest.mark.parametrize(
    "entry_id",
    [
        "001-simple-object",
        "002-nested-object",
        "003-array-order",
        "004-unicode",
        "005-number-integer",
        "006-number-float",
        "007-bool-null",
        "008-key-order",
        "009-whitespace",
        "010-wiseorder-class-a",
    ],
)
def test_per_entry_digest_matches_committed(entry_id: str) -> None:
    raw = (CORPUS_DIR / f"{entry_id}.json").read_text(encoding="utf-8")
    parsed = json.loads(raw)
    canonical = canonical_json_bytes(parsed)
    digest = sha256_hex(canonical)
    assert digest == _load_committed_digests()[entry_id]
