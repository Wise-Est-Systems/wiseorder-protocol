"""WiseOrder v0.2.0 chain: genesis + triple appending.

INVARIANT TS-1 (timestamp precision):
  This module uses MICROSECOND precision in ``sealed_at`` (``%H:%M:%S.%fZ``).
  ``intellagent_runtime.canonical.utcnow_iso8601`` uses SECOND precision.
  These two formats are NOT to be unified.

  Why microseconds here: chain triple filenames are derived from
  ``sealed_at`` (see ``append_triple``); two triples sealed in the same
  second would collide on filename without microsecond differentiation.
  Audit memory, refusal records, and conformance vectors have no such
  constraint and use the shorter, operator-readable form.

  Why this is load-bearing: three sealed ``.win`` files on disk encode
  ``sealed_at`` at microsecond precision. Changing the format would change
  ``consequence_proof`` for future triples and break the cross-language
  verifier compatibility claim (Python, Rust, Go all expect this format).

Every artifact in the v0.2.0 chain is a ``.win`` file. Each file is one
triple. The triple shape (per ``SPEC_LOCK_v0.2.0.md §2.2``):

  {
    "algorithm":         "III",
    "author":            "III",
    "previous_action":   "<III hex of prior triple>" | "NULLASIGN" (genesis only),
    "foundational":      "<III hex of the rules in force at sealing>",
    "consequence_proof": "<III hex over the canonical body w/o consequence_proof>",
    "sealed_at":         "<ISO-8601 UTC>",
    "statement":         "<short prose>"
  }

Canonical body for ``consequence_proof``: the JSON serialization of the
triple WITHOUT the ``consequence_proof`` field, using sorted keys, compact
separators, no whitespace, UTF-8.

This module:

  - seal_genesis(...)              creates the one and only genesis triple
                                   if and only if none exists yet
  - append_triple(...)             seals a new triple, linked to the prior
                                   by its III hex digest
  - read_chain(...)                returns every .win in seal order
  - verify_chain(...)              re-derives every consequence_proof and
                                   every previous_action; returns a status
                                   (CHAIN_VALID / TAMPERED / INVALID / EMPTY)

The chain lives in a directory of ``.win`` files, named by ISO timestamp +
short hash, in seal order. The genesis is always ``genesis.win``.
"""

from __future__ import annotations

import datetime
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from intellagent_runtime.iii import iii


CHAIN_VALID = "CHAIN_VALID"
CHAIN_TAMPERED = "CHAIN_TAMPERED"
CHAIN_INVALID = "CHAIN_INVALID"
CHAIN_EMPTY = "CHAIN_EMPTY"

ALGORITHM_LABEL = "III"
AUTHOR_LABEL = "III"
GENESIS_PREVIOUS = "NULLASIGN"
GENESIS_FILENAME = "genesis.win"


@dataclass
class Triple:
    algorithm: str
    author: str
    previous_action: str
    foundational: str
    consequence_proof: str
    sealed_at: str
    statement: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Triple":
        return cls(
            algorithm=data["algorithm"],
            author=data["author"],
            previous_action=data["previous_action"],
            foundational=data["foundational"],
            consequence_proof=data["consequence_proof"],
            sealed_at=data["sealed_at"],
            statement=data["statement"],
        )

    def core_dict(self) -> dict:
        """Body that the consequence_proof commits to (excludes itself)."""
        return {
            "algorithm": self.algorithm,
            "author": self.author,
            "previous_action": self.previous_action,
            "foundational": self.foundational,
            "sealed_at": self.sealed_at,
            "statement": self.statement,
        }

    def to_dict(self) -> dict:
        d = self.core_dict()
        d["consequence_proof"] = self.consequence_proof
        return d


@dataclass
class ChainStatus:
    status: str
    count: int
    head: str | None
    first_failure_index: int | None = None
    reason: str = ""

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "count": self.count,
            "head": self.head,
            "first_failure_index": self.first_failure_index,
            "reason": self.reason,
        }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _utc_iso() -> str:
    """MICROSECOND-precision UTC timestamp for chain triples.

    See INVARIANT TS-1 in module docstring — not to be unified with
    ``intellagent_runtime.canonical.utcnow_iso8601`` (which uses seconds).
    """
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _canonical_bytes(obj: dict) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _pretty_bytes(obj: dict) -> str:
    return json.dumps(obj, sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def compute_foundational(spec_paths: list[Path]) -> str:
    """III over the concatenation of the bytes of the rule documents
    declared as governing this triple. For v0.2.0 these are typically
    SPEC_LOCK_v0.2.0.md and intellagent_runtime/iii.py."""
    parts: list[bytes] = []
    for p in spec_paths:
        parts.append(p.read_bytes())
        parts.append(b"\x00")  # framing
    return iii(b"".join(parts))


def compute_consequence_proof(t: Triple) -> str:
    """III over the canonical body of the triple, excluding the
    consequence_proof field itself."""
    return iii(_canonical_bytes(t.core_dict()))


def triple_hash(t: Triple) -> str:
    """III over the canonical full body (including consequence_proof).
    This is what subsequent triples reference as previous_action."""
    return iii(_canonical_bytes(t.to_dict()))


# ---------------------------------------------------------------------------
# Sealing
# ---------------------------------------------------------------------------


def seal_genesis(
    chain_dir: Path,
    foundational_files: list[Path],
    statement: str,
    *,
    sealed_at: str | None = None,
) -> Path:
    """Seal the one and only genesis triple. Raises if a genesis already
    exists in chain_dir (the chain is meant to be unique)."""
    chain_dir.mkdir(parents=True, exist_ok=True)
    genesis_path = chain_dir / GENESIS_FILENAME
    if genesis_path.exists():
        raise FileExistsError(
            f"genesis already sealed at {genesis_path}; the genesis is unique. "
            f"To create a new chain, choose a different chain_dir."
        )

    found = compute_foundational(foundational_files)
    t = Triple(
        algorithm=ALGORITHM_LABEL,
        author=AUTHOR_LABEL,
        previous_action=GENESIS_PREVIOUS,
        foundational=found,
        consequence_proof="",  # filled below
        sealed_at=sealed_at or _utc_iso(),
        statement=statement,
    )
    t.consequence_proof = compute_consequence_proof(t)

    genesis_path.write_text(_pretty_bytes(t.to_dict()), encoding="utf-8")
    return genesis_path


def append_triple(
    chain_dir: Path,
    foundational_files: list[Path],
    statement: str,
    *,
    sealed_at: str | None = None,
) -> Path:
    """Seal a new triple and link it to the current chain head. Returns the
    path of the new .win file. Filename pattern: ``<sealed_at_ts>-<head8>.win``
    where head8 is the first 8 hex chars of the triple_hash."""
    triples = read_chain(chain_dir)
    if not triples:
        raise FileNotFoundError(
            f"no genesis at {chain_dir / GENESIS_FILENAME}; "
            f"call seal_genesis(...) first"
        )
    prev = triples[-1]
    prev_hash = triple_hash(prev)
    found = compute_foundational(foundational_files)
    t = Triple(
        algorithm=ALGORITHM_LABEL,
        author=AUTHOR_LABEL,
        previous_action=prev_hash,
        foundational=found,
        consequence_proof="",
        sealed_at=sealed_at or _utc_iso(),
        statement=statement,
    )
    t.consequence_proof = compute_consequence_proof(t)
    th = triple_hash(t)
    fname = f"{t.sealed_at.replace(':', '').replace('.', '_')}-{th[:8]}.win"
    out = chain_dir / fname
    out.write_text(_pretty_bytes(t.to_dict()), encoding="utf-8")
    return out


# ---------------------------------------------------------------------------
# Reading + verification
# ---------------------------------------------------------------------------


def read_chain(chain_dir: Path) -> list[Triple]:
    """Return every triple in the chain in seal order (genesis first)."""
    if not chain_dir.is_dir():
        return []
    triples: list[Triple] = []
    genesis_path = chain_dir / GENESIS_FILENAME
    if genesis_path.is_file():
        triples.append(Triple.from_dict(json.loads(genesis_path.read_text(encoding="utf-8"))))
    others = sorted(p for p in chain_dir.glob("*.win") if p.name != GENESIS_FILENAME)
    for p in others:
        triples.append(Triple.from_dict(json.loads(p.read_text(encoding="utf-8"))))
    return triples


def verify_chain(chain_dir: Path) -> ChainStatus:
    """Re-derive every consequence_proof and every previous_action link.
    Returns a ChainStatus."""
    if not chain_dir.is_dir():
        return ChainStatus(CHAIN_EMPTY, 0, None, reason=f"no chain directory at {chain_dir}")
    try:
        triples = read_chain(chain_dir)
    except (json.JSONDecodeError, KeyError) as exc:
        return ChainStatus(CHAIN_INVALID, 0, None, reason=f"malformed triple: {exc}")
    if not triples:
        return ChainStatus(CHAIN_EMPTY, 0, None, reason="chain directory has no .win files")

    for i, t in enumerate(triples):
        # Field shape.
        if t.algorithm != ALGORITHM_LABEL:
            return ChainStatus(CHAIN_INVALID, len(triples), None, first_failure_index=i,
                               reason=f"triple {i} algorithm={t.algorithm!r}, expected {ALGORITHM_LABEL!r}")
        if t.author != AUTHOR_LABEL:
            return ChainStatus(CHAIN_INVALID, len(triples), None, first_failure_index=i,
                               reason=f"triple {i} author={t.author!r}, expected {AUTHOR_LABEL!r}")
        # Self-witness.
        recomputed = compute_consequence_proof(t)
        if recomputed != t.consequence_proof:
            return ChainStatus(CHAIN_TAMPERED, len(triples), None, first_failure_index=i,
                               reason=f"triple {i} consequence_proof mismatch: stored {t.consequence_proof!r}, recomputed {recomputed!r}")
        # Linkage.
        if i == 0:
            if t.previous_action != GENESIS_PREVIOUS:
                return ChainStatus(CHAIN_INVALID, len(triples), None, first_failure_index=i,
                                   reason=f"genesis previous_action={t.previous_action!r}, expected {GENESIS_PREVIOUS!r}")
        else:
            expected_prev = triple_hash(triples[i - 1])
            if t.previous_action != expected_prev:
                return ChainStatus(CHAIN_TAMPERED, len(triples), None, first_failure_index=i,
                                   reason=f"triple {i} previous_action mismatch: stored {t.previous_action!r}, expected {expected_prev!r}")

    head = triple_hash(triples[-1])
    return ChainStatus(CHAIN_VALID, len(triples), head)


# ---------------------------------------------------------------------------
# Self-check
# ---------------------------------------------------------------------------


def self_check() -> int:
    """In-memory self-check: seal a genesis + one follow-up, verify, then
    deliberately tamper and confirm detection."""
    import tempfile

    failures: list[str] = []

    def expect(name: str, condition: bool, detail: str = "") -> None:
        print(f"  [{'PASS' if condition else 'FAIL'}] {name}")
        if not condition:
            failures.append(f"{name}: {detail}")

    with tempfile.TemporaryDirectory(prefix="wo-chain-selfcheck-") as tmpd:
        chain_dir = Path(tmpd) / "chain"

        # Empty chain.
        s = verify_chain(chain_dir)
        expect("empty_chain_status", s.status == CHAIN_EMPTY, s.reason)

        # Foundational file (synthetic — keep self-check pure).
        spec = chain_dir / "_spec.bytes"
        chain_dir.mkdir(parents=True, exist_ok=True)
        spec.write_bytes(b"self-check spec bytes\n")

        # Seal genesis.
        gpath = seal_genesis(chain_dir, [spec], "self-check genesis")
        expect("genesis_sealed", gpath.exists() and gpath.name == GENESIS_FILENAME)

        # Re-seal genesis MUST fail (genesis is unique).
        try:
            seal_genesis(chain_dir, [spec], "second genesis attempt")
            expect("genesis_re_seal_refused", False, "did not raise")
        except FileExistsError:
            expect("genesis_re_seal_refused", True)

        # Verify intact chain.
        s = verify_chain(chain_dir)
        expect("genesis_only_chain_valid", s.status == CHAIN_VALID and s.count == 1, s.reason)

        # Append a triple.
        new_path = append_triple(chain_dir, [spec], "self-check second triple")
        expect("triple_appended", new_path.exists() and new_path.suffix == ".win")

        s = verify_chain(chain_dir)
        expect("two_triple_chain_valid", s.status == CHAIN_VALID and s.count == 2, s.reason)

        # Tamper: edit the statement of the genesis without touching its hashes.
        gdata = json.loads(gpath.read_text(encoding="utf-8"))
        gdata["statement"] = gdata["statement"] + " (tampered)"
        gpath.write_text(_pretty_bytes(gdata), encoding="utf-8")
        s = verify_chain(chain_dir)
        expect("tamper_detected", s.status == CHAIN_TAMPERED, s.reason)

    if failures:
        print(f"\nFAIL: {len(failures)} self-check failures")
        for f in failures:
            print(f"  ↳ {f}")
        return 1
    print("\nPASS: chain self-check")
    return 0


if __name__ == "__main__":
    raise SystemExit(self_check())
