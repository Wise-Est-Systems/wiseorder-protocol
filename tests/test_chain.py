"""Tests for intellagent_runtime.chain — the v0.2.0 .win chain.

Covers:
  - empty chain status
  - seal_genesis happy path + uniqueness (re-seal refused)
  - append_triple linkage + filenames
  - verify_chain integrity + tamper detection (consequence_proof + previous_action)
  - foundational and consequence_proof recomputation
  - triple_hash determinism
  - schema field validation
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from intellagent_runtime.chain import (
    ALGORITHM_LABEL,
    AUTHOR_LABEL,
    CHAIN_EMPTY,
    CHAIN_INVALID,
    CHAIN_TAMPERED,
    CHAIN_VALID,
    GENESIS_FILENAME,
    GENESIS_PREVIOUS,
    Triple,
    append_triple,
    compute_consequence_proof,
    compute_foundational,
    read_chain,
    seal_genesis,
    self_check,
    triple_hash,
    verify_chain,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def spec(tmp_path: Path) -> Path:
    p = tmp_path / "_spec.bytes"
    p.write_bytes(b"test spec bytes for chain tests\n")
    return p


@pytest.fixture
def chain_dir(tmp_path: Path) -> Path:
    return tmp_path / "chain"


# ---------------------------------------------------------------------------
# Empty state
# ---------------------------------------------------------------------------


def test_verify_chain_on_missing_directory(chain_dir: Path):
    s = verify_chain(chain_dir)
    assert s.status == CHAIN_EMPTY
    assert s.count == 0
    assert s.head is None


def test_read_chain_on_missing_directory(chain_dir: Path):
    assert read_chain(chain_dir) == []


# ---------------------------------------------------------------------------
# Genesis sealing
# ---------------------------------------------------------------------------


def test_seal_genesis_creates_genesis_dot_win(chain_dir: Path, spec: Path):
    p = seal_genesis(chain_dir, [spec], "x")
    assert p.name == GENESIS_FILENAME
    assert p.is_file()


def test_seal_genesis_fields_match_schema(chain_dir: Path, spec: Path):
    p = seal_genesis(chain_dir, [spec], "self-check")
    body = json.loads(p.read_text(encoding="utf-8"))
    assert body["algorithm"] == ALGORITHM_LABEL == "III"
    assert body["author"] == AUTHOR_LABEL == "III"
    assert body["previous_action"] == GENESIS_PREVIOUS == "NULLASIGN"
    assert body["statement"] == "self-check"
    assert len(body["foundational"]) == 64
    assert len(body["consequence_proof"]) == 64
    assert all(c in "0123456789abcdef" for c in body["foundational"])
    assert all(c in "0123456789abcdef" for c in body["consequence_proof"])


def test_seal_genesis_refuses_re_seal(chain_dir: Path, spec: Path):
    seal_genesis(chain_dir, [spec], "first")
    with pytest.raises(FileExistsError):
        seal_genesis(chain_dir, [spec], "second")


def test_seal_genesis_produces_valid_chain_of_one(chain_dir: Path, spec: Path):
    seal_genesis(chain_dir, [spec], "x")
    s = verify_chain(chain_dir)
    assert s.status == CHAIN_VALID
    assert s.count == 1
    assert s.head is not None
    assert len(s.head) == 64


# ---------------------------------------------------------------------------
# Foundational + consequence_proof determinism
# ---------------------------------------------------------------------------


def test_foundational_is_deterministic(spec: Path, tmp_path: Path):
    h1 = compute_foundational([spec])
    h2 = compute_foundational([spec])
    assert h1 == h2


def test_foundational_changes_with_spec_content(spec: Path, tmp_path: Path):
    other = tmp_path / "_other.bytes"
    other.write_bytes(b"different content\n")
    h1 = compute_foundational([spec])
    h2 = compute_foundational([other])
    assert h1 != h2


def test_consequence_proof_matches_recomputation(chain_dir: Path, spec: Path):
    p = seal_genesis(chain_dir, [spec], "verify recompute")
    t = Triple.from_dict(json.loads(p.read_text(encoding="utf-8")))
    assert compute_consequence_proof(t) == t.consequence_proof


def test_triple_hash_is_deterministic(chain_dir: Path, spec: Path):
    seal_genesis(chain_dir, [spec], "x")
    t1 = read_chain(chain_dir)[0]
    t2 = read_chain(chain_dir)[0]  # re-read from disk
    assert triple_hash(t1) == triple_hash(t2)


# ---------------------------------------------------------------------------
# Append
# ---------------------------------------------------------------------------


def test_append_requires_genesis(chain_dir: Path, spec: Path):
    chain_dir.mkdir(parents=True)
    with pytest.raises(FileNotFoundError):
        append_triple(chain_dir, [spec], "no genesis present")


def test_append_creates_dot_win_file(chain_dir: Path, spec: Path):
    seal_genesis(chain_dir, [spec], "genesis")
    p = append_triple(chain_dir, [spec], "first append")
    assert p.suffix == ".win"
    assert p.is_file()
    assert p.name != GENESIS_FILENAME


def test_append_links_previous_action_to_prior_triple_hash(chain_dir: Path, spec: Path):
    seal_genesis(chain_dir, [spec], "genesis")
    triples = read_chain(chain_dir)
    expected_prev = triple_hash(triples[0])
    p = append_triple(chain_dir, [spec], "linked")
    new = Triple.from_dict(json.loads(p.read_text(encoding="utf-8")))
    assert new.previous_action == expected_prev


def test_append_preserves_chain_validity(chain_dir: Path, spec: Path):
    seal_genesis(chain_dir, [spec], "genesis")
    append_triple(chain_dir, [spec], "two")
    append_triple(chain_dir, [spec], "three")
    s = verify_chain(chain_dir)
    assert s.status == CHAIN_VALID
    assert s.count == 3


# ---------------------------------------------------------------------------
# Tamper detection
# ---------------------------------------------------------------------------


def test_tamper_genesis_statement_detected(chain_dir: Path, spec: Path):
    p = seal_genesis(chain_dir, [spec], "original")
    body = json.loads(p.read_text(encoding="utf-8"))
    body["statement"] = body["statement"] + " TAMPERED"
    p.write_text(json.dumps(body, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    s = verify_chain(chain_dir)
    assert s.status == CHAIN_TAMPERED
    assert s.first_failure_index == 0


def test_tamper_append_previous_action_detected(chain_dir: Path, spec: Path):
    seal_genesis(chain_dir, [spec], "genesis")
    p2 = append_triple(chain_dir, [spec], "two")
    body = json.loads(p2.read_text(encoding="utf-8"))
    # Flip one hex char of previous_action.
    orig = body["previous_action"]
    flipped = ("f" if orig[0] != "f" else "e") + orig[1:]
    body["previous_action"] = flipped
    # Also fix consequence_proof so the SELF-witness still passes — this
    # isolates the test to ONLY the linkage check, not the self-witness.
    new_t = Triple(
        algorithm=body["algorithm"],
        author=body["author"],
        previous_action=body["previous_action"],
        foundational=body["foundational"],
        consequence_proof="",
        sealed_at=body["sealed_at"],
        statement=body["statement"],
    )
    body["consequence_proof"] = compute_consequence_proof(new_t)
    p2.write_text(json.dumps(body, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    s = verify_chain(chain_dir)
    assert s.status == CHAIN_TAMPERED
    assert s.first_failure_index == 1
    assert "previous_action" in s.reason


def test_tamper_genesis_algorithm_label_invalid(chain_dir: Path, spec: Path):
    p = seal_genesis(chain_dir, [spec], "x")
    body = json.loads(p.read_text(encoding="utf-8"))
    body["algorithm"] = "sha256"
    p.write_text(json.dumps(body, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    s = verify_chain(chain_dir)
    assert s.status == CHAIN_INVALID
    assert "algorithm" in s.reason


def test_tamper_genesis_author_label_invalid(chain_dir: Path, spec: Path):
    p = seal_genesis(chain_dir, [spec], "x")
    body = json.loads(p.read_text(encoding="utf-8"))
    body["author"] = "someone-else"
    p.write_text(json.dumps(body, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    s = verify_chain(chain_dir)
    assert s.status == CHAIN_INVALID
    assert "author" in s.reason


def test_tamper_genesis_previous_action_invalid(chain_dir: Path, spec: Path):
    p = seal_genesis(chain_dir, [spec], "x")
    body = json.loads(p.read_text(encoding="utf-8"))
    body["previous_action"] = "not-null-assign"
    p.write_text(json.dumps(body, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    s = verify_chain(chain_dir)
    assert s.status in (CHAIN_INVALID, CHAIN_TAMPERED)


def test_malformed_genesis_json_invalid(chain_dir: Path):
    chain_dir.mkdir(parents=True)
    (chain_dir / GENESIS_FILENAME).write_text("{not valid json", encoding="utf-8")
    s = verify_chain(chain_dir)
    assert s.status == CHAIN_INVALID


# ---------------------------------------------------------------------------
# Self-check
# ---------------------------------------------------------------------------


def test_module_self_check_returns_zero():
    assert self_check() == 0


# ---------------------------------------------------------------------------
# Real genesis (the one sealed by WO-018) still verifies
# ---------------------------------------------------------------------------


REPO_ROOT = Path(__file__).resolve().parent.parent
REAL_CHAIN = REPO_ROOT / "chain"


def test_real_genesis_verifies():
    if not (REAL_CHAIN / GENESIS_FILENAME).exists():
        pytest.skip("real chain/genesis.win not present")
    s = verify_chain(REAL_CHAIN)
    assert s.status == CHAIN_VALID
    assert s.count >= 1
    assert s.head is not None


def test_real_genesis_carries_iii_and_nullasign():
    if not (REAL_CHAIN / GENESIS_FILENAME).exists():
        pytest.skip("real chain/genesis.win not present")
    body = json.loads((REAL_CHAIN / GENESIS_FILENAME).read_text(encoding="utf-8"))
    assert body["algorithm"] == "III"
    assert body["author"] == "III"
    assert body["previous_action"] == "NULLASIGN"
