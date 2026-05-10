#!/usr/bin/env python3
"""WiseOrder Protocol v0.1.0 — Minimal Independent Verifier.

A from-spec re-derivation of vector verdict logic. This module MUST NOT
import intellagent_runtime; it exists to demonstrate that v0.1.0 protocol
semantics can be re-implemented from spec text alone.

Implements:
  - vector schema check (via jsonschema, not project code)
  - Class A verdicts (VERIFIED / TAMPERED / INVALID)
  - Class B basic evidence rules (SUPPORTED / CONFLICTED /
    INSUFFICIENT_EVIDENCE / INVALID)
  - Class C quorum basics (CONSENSUS_VALID / CONSENSUS_PENDING /
    CONSENSUS_FAILED / INVALID)
  - Class D commit-chain basics (CONDUCT_VALID / CONDUCT_INVALID)
  - telemetry-status rejection (CALIBRATION_* MUST never be a per-claim status)

Usage:
  python3 tools/minimal_verifier.py [--vectors-dir DIR] [--quiet]
  python3 tools/minimal_verifier.py self-check

Exit codes:
  0   every vector's derived verdict matches expected_status
  1   one or more divergences
  2   usage / I/O error
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_VECTORS_DIR = REPO_ROOT / "vectors"
DEFAULT_SCHEMA_PATH = REPO_ROOT / "schemas" / "vector.schema.json"

CANONICAL_SCHEME = "RFC8785-JCS"
CANONICAL_ALGORITHM = "SHA-256"
PROTOCOL_VERSION = "0.1.0"

TELEMETRY_TOKENS = frozenset({"CALIBRATION_IMPROVED", "CALIBRATION_DEGRADED"})

DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")

REQUIRED_BY_CLASS = {
    "A": (
        "class", "regime", "claim", "canonicalization", "algorithm",
        "expected_digest", "observed_digest", "proof",
    ),
    "B": (
        "class", "regime", "claim", "sources", "observations",
        "structural_diff", "proof",
    ),
    "C": (
        "class", "regime", "claim", "protocol", "evidence",
        "action_policy", "proof",
    ),
    "D": (
        "class", "regime", "claim", "values_frame", "alternatives",
        "reasoning_trace", "recommended_action", "reversibility_score",
        "challenge_surface", "calibration", "commit_chain", "meta_proof",
    ),
}


@dataclass
class Verdict:
    status: str
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"status": self.status, "reasons": list(self.reasons)}


def _is_telemetry_status(artifact: dict) -> bool:
    return artifact.get("status") in TELEMETRY_TOKENS


def _missing_fields(artifact: dict, required: tuple[str, ...]) -> list[str]:
    return [f for f in required if f not in artifact]


def verify_class_a(art: dict) -> Verdict:
    if _is_telemetry_status(art):
        return Verdict("INVALID", ["telemetry status rejected"])
    missing = _missing_fields(art, REQUIRED_BY_CLASS["A"])
    if missing:
        return Verdict("INVALID", [f"missing field(s): {missing}"])
    if art.get("canonicalization") != CANONICAL_SCHEME:
        return Verdict("INVALID", [
            f"canonicalization MUST be {CANONICAL_SCHEME!r}, "
            f"got {art.get('canonicalization')!r}"
        ])
    if art.get("algorithm") != CANONICAL_ALGORITHM:
        return Verdict("INVALID", [
            f"algorithm MUST be {CANONICAL_ALGORITHM!r}, "
            f"got {art.get('algorithm')!r}"
        ])
    expected = art.get("expected_digest", "")
    observed = art.get("observed_digest", "")
    if not (isinstance(expected, str) and DIGEST_RE.match(expected)):
        return Verdict("INVALID", [f"expected_digest format invalid: {expected!r}"])
    if not (isinstance(observed, str) and DIGEST_RE.match(observed)):
        return Verdict("INVALID", [f"observed_digest format invalid: {observed!r}"])
    if expected == observed:
        return Verdict("VERIFIED")
    return Verdict("TAMPERED", ["expected_digest != observed_digest"])


def verify_class_b(art: dict) -> Verdict:
    if _is_telemetry_status(art):
        return Verdict("INVALID", ["telemetry status rejected"])
    missing = _missing_fields(art, REQUIRED_BY_CLASS["B"])
    if missing:
        return Verdict("INVALID", [f"missing field(s): {missing}"])
    sources = art.get("sources") or []
    if not isinstance(sources, list) or len(sources) == 0:
        return Verdict("INVALID", ["sources missing or empty (B1)"])
    observations = art.get("observations") or []
    timestamps = art.get("timestamps") or []
    if len(observations) < len(sources) and len(timestamps) >= len(sources):
        return Verdict("INVALID", [
            "selective omission: declared sources/timestamps exceed observations (B1/B2)"
        ])
    # Replay drift: same input_digest, different observed_result_digest.
    seen: dict[str, str] = {}
    for obs in observations:
        if not isinstance(obs, dict):
            continue
        inp = obs.get("input_digest")
        outd = obs.get("observed_result_digest")
        if isinstance(inp, str) and isinstance(outd, str):
            prev = seen.get(inp)
            if prev is not None and prev != outd:
                return Verdict("CONFLICTED", [
                    f"replay drift: input_digest {inp} produced different observed_result_digest values"
                ])
            seen[inp] = outd
    # supports_claim distribution.
    sc = [o.get("supports_claim") for o in observations if isinstance(o, dict)]
    has_true = any(v is True for v in sc)
    has_false = any(v is False for v in sc)
    has_null = any(v is None for v in sc)
    if has_true and has_false:
        return Verdict("CONFLICTED", ["observations contain both supports_claim=true and false"])
    if sc and all(v is None for v in sc):
        return Verdict("INSUFFICIENT_EVIDENCE", ["all observations have supports_claim=null"])
    # structural_diff with conflict markers (e.g., digest_match=false).
    sd = art.get("structural_diff") or {}
    if isinstance(sd, dict):
        flat = json.dumps(sd, sort_keys=True)
        if has_true and has_false is False and ('"digest_match": false' in flat):
            return Verdict("CONFLICTED", ["structural_diff records digest mismatch"])
    if has_true and not has_false and not has_null:
        return Verdict("SUPPORTED")
    if has_null and (has_true or has_false):
        return Verdict("INSUFFICIENT_EVIDENCE", ["mixed supports_claim with null values"])
    return Verdict("INSUFFICIENT_EVIDENCE", ["unable to derive positive support"])


def _action_authorization_violation(art: dict) -> Verdict | None:
    pol = art.get("action_policy") or {}
    if not isinstance(pol, dict):
        return Verdict("INVALID", ["action_policy missing or malformed"])
    allowed = pol.get("action_allowed", False)
    auth_source = pol.get("authorization_source")
    if allowed is True and not auth_source:
        return Verdict("INVALID", [
            "action_allowed=true REQUIRES authorization_source (AG2/AG3)"
        ])
    return None


def verify_class_c(art: dict) -> Verdict:
    if _is_telemetry_status(art):
        return Verdict("INVALID", ["telemetry status rejected"])
    missing = _missing_fields(art, REQUIRED_BY_CLASS["C"])
    if missing:
        return Verdict("INVALID", [f"missing field(s): {missing}"])
    proto = art.get("protocol") or {}
    if not isinstance(proto, dict):
        return Verdict("INVALID", ["protocol field malformed"])
    if proto.get("version") != PROTOCOL_VERSION:
        return Verdict("INVALID", [
            f"protocol.version MUST be {PROTOCOL_VERSION!r}, got {proto.get('version')!r}"
        ])
    eligible = proto.get("eligible_attesters") or []
    if not isinstance(eligible, list) or len(eligible) == 0:
        return Verdict("INVALID", ["eligible_attesters missing or empty"])
    required_quorum = proto.get("required_quorum")
    if not isinstance(required_quorum, int) or required_quorum <= 0:
        return Verdict("INVALID", ["required_quorum missing or non-positive"])

    evidence = art.get("evidence") or []
    eligible_set = set(eligible)
    seen_attesters: set[str] = set()
    approve_count = 0
    reject_count = 0
    for ev in evidence:
        if not isinstance(ev, dict):
            return Verdict("INVALID", ["evidence entry malformed"])
        aid = ev.get("attester_id")
        if aid not in eligible_set:
            return Verdict("INVALID", [f"unauthorized attester: {aid!r}"])
        if ev.get("eligible") is False:
            return Verdict("INVALID", [f"evidence claims ineligibility for {aid!r}"])
        if aid in seen_attesters:
            return Verdict("INVALID", [
                f"duplicate attestation from {aid!r} (replay poisoning)"
            ])
        seen_attesters.add(aid)
        att = ev.get("attestation")
        if att == "approve":
            approve_count += 1
        elif att == "reject":
            reject_count += 1

    auth_violation = _action_authorization_violation(art)
    if auth_violation is not None:
        return auth_violation

    pol = art.get("action_policy") or {}
    if pol.get("action_allowed") is True and approve_count < required_quorum:
        return Verdict("INVALID", [
            "action_allowed=true with quorum below required_quorum (authority escalation)"
        ])

    if approve_count >= required_quorum:
        return Verdict("CONSENSUS_VALID")
    if "process_closed_at" in art:
        return Verdict("CONSENSUS_FAILED", [
            f"process closed with {approve_count}/{required_quorum} approvals"
        ])
    return Verdict("CONSENSUS_PENDING", [
        f"{approve_count}/{required_quorum} approvals collected"
    ])


def verify_class_d(art: dict) -> Verdict:
    if _is_telemetry_status(art):
        return Verdict("CONDUCT_INVALID", ["telemetry status rejected"])
    # D4: any non-Class-D status on input is a structural error.
    bad_status = {"VERIFIED", "TAMPERED", "SUPPORTED", "CONSENSUS_VALID"}
    if art.get("status") in bad_status:
        return Verdict("CONDUCT_INVALID", [
            f"non-Class-D status {art.get('status')!r} forbidden by D4"
        ])
    missing = _missing_fields(art, REQUIRED_BY_CLASS["D"])
    if missing:
        return Verdict("CONDUCT_INVALID", [f"missing field(s): {missing}"])

    if not art.get("alternatives"):
        return Verdict("CONDUCT_INVALID", ["alternatives empty (D2)"])
    if not art.get("challenge_surface"):
        return Verdict("CONDUCT_INVALID", ["challenge_surface empty (D3)"])

    rec = art.get("recommended_action") or {}
    rev = art.get("reversibility_score")
    if isinstance(rev, (int, float)) and rec.get("compelled") is True and rev < 0.1:
        return Verdict("CONDUCT_INVALID", [
            "recommended_action.compelled=true with reversibility_score<0.1 "
            "is a forbidden coupling (AG2)"
        ])

    chain = art.get("commit_chain") or []
    if not isinstance(chain, list) or len(chain) == 0:
        return Verdict("CONDUCT_INVALID", ["commit_chain empty (CC3)"])

    prev_stage = 0
    prev_hash: str | None = None
    prev_time = ""
    seen_hashes: dict[str, str] = {}  # hash -> serialized content (for forgery detect)
    for entry in chain:
        if not isinstance(entry, dict):
            return Verdict("CONDUCT_INVALID", ["commit_chain entry malformed"])
        stage = entry.get("stage")
        if not isinstance(stage, int) or stage <= 0:
            return Verdict("CONDUCT_INVALID", ["stage missing or non-positive"])
        if stage != prev_stage + 1:
            return Verdict("CONDUCT_INVALID", [
                f"stage numbers non-contiguous: expected {prev_stage + 1}, got {stage} (CC3/CC4)"
            ])
        h = entry.get("hash")
        if not isinstance(h, str) or not DIGEST_RE.match(h):
            return Verdict("CONDUCT_INVALID", ["stage hash format invalid"])
        content = entry.get("content")
        if content is None or content == {} or content == []:
            return Verdict("CONDUCT_INVALID", [
                f"stage {stage} preimage content missing or empty (CC1)"
            ])
        depends = entry.get("depends_on", "<absent>")
        if stage == 1:
            if depends not in (None,):
                return Verdict("CONDUCT_INVALID", [
                    f"stage 1 depends_on MUST be null, got {depends!r}"
                ])
        else:
            if depends != prev_hash:
                return Verdict("CONDUCT_INVALID", [
                    f"stage {stage} depends_on does not equal prior stage hash (CC2)"
                ])
        ts = entry.get("created_at", "")
        if not isinstance(ts, str) or ts < prev_time:
            return Verdict("CONDUCT_INVALID", [
                f"stage {stage} created_at not monotonic (CC4)"
            ])
        # Forgery detection: identical hash with different content.
        serial = json.dumps(content, sort_keys=True)
        if h in seen_hashes and seen_hashes[h] != serial:
            return Verdict("CONDUCT_INVALID", [
                f"forged commit chain: identical hash {h} under differing content"
            ])
        seen_hashes[h] = serial
        prev_stage = stage
        prev_hash = h
        prev_time = ts

    return Verdict("CONDUCT_VALID")


def verify_artifact(cls: str, artifact: dict) -> Verdict:
    if cls == "A":
        return verify_class_a(artifact)
    if cls == "B":
        return verify_class_b(artifact)
    if cls == "C":
        return verify_class_c(artifact)
    if cls == "D":
        return verify_class_d(artifact)
    return Verdict("INVALID", [f"unknown class: {cls!r}"])


# --- driver / vector-suite check ---


@dataclass
class VectorOutcome:
    file: str
    vector_id: str
    cls: str
    expected: str
    derived: str
    passed: bool
    reasons: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "file": self.file,
            "vector_id": self.vector_id,
            "class": self.cls,
            "expected": self.expected,
            "derived": self.derived,
            "passed": self.passed,
            "reasons": list(self.reasons),
        }


def _load_vector(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_schema(vector: dict, schema: dict) -> list[str]:
    try:
        from jsonschema import Draft202012Validator
    except ImportError:  # pragma: no cover
        return ["jsonschema not installed"]
    validator = Draft202012Validator(schema)
    return [
        f"{'.'.join(str(p) for p in e.absolute_path) or '<root>'}: {e.message}"
        for e in validator.iter_errors(vector)
    ]


def check_vectors(
    vectors_dir: Path = DEFAULT_VECTORS_DIR,
    schema_path: Path = DEFAULT_SCHEMA_PATH,
) -> list[VectorOutcome]:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    outcomes: list[VectorOutcome] = []
    for path in sorted(vectors_dir.glob("*.json")):
        vector = _load_vector(path)
        schema_errs = _validate_schema(vector, schema)
        cls = str(vector.get("class", "?"))
        expected = str(vector.get("expected_status", "?"))
        if schema_errs:
            outcomes.append(VectorOutcome(
                file=str(path.relative_to(REPO_ROOT)),
                vector_id=vector.get("vector_id", "<missing>"),
                cls=cls,
                expected=expected,
                derived="SCHEMA_FAIL",
                passed=False,
                reasons=schema_errs,
            ))
            continue
        verdict = verify_artifact(cls, vector.get("input", {}))
        outcomes.append(VectorOutcome(
            file=str(path.relative_to(REPO_ROOT)),
            vector_id=vector["vector_id"],
            cls=cls,
            expected=expected,
            derived=verdict.status,
            passed=(verdict.status == expected),
            reasons=verdict.reasons,
        ))
    return outcomes


def _print_table(outcomes: list[VectorOutcome]) -> None:
    print("WiseOrder Protocol v0.1.0 — Minimal Independent Verifier")
    print("=" * 60)
    width = max((len(o.vector_id) for o in outcomes), default=20)
    for o in outcomes:
        verdict = "PASS" if o.passed else "FAIL"
        print(f"{verdict} | {o.vector_id:<{width}} | {o.cls} | "
              f"expected={o.expected:<22} derived={o.derived}")
        if not o.passed:
            for r in o.reasons:
                print(f"       ↳ {r}")
    total = len(outcomes)
    passed = sum(1 for o in outcomes if o.passed)
    print("=" * 60)
    print(f"Summary: {total} vectors, {passed} passed, {total - passed} failed")


def self_check() -> int:
    """Built-in self-check that exercises each class with hand-crafted inputs."""
    failures: list[str] = []

    def expect(name: str, got: Verdict, want: str) -> None:
        ok = got.status == want
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}: derived={got.status} expected={want}")
        if not ok:
            failures.append(f"{name}: derived={got.status} expected={want} reasons={got.reasons}")

    # Class A
    a_valid = {
        "class": "A", "regime": "deterministic_verification", "claim": "x",
        "canonicalization": "RFC8785-JCS", "algorithm": "SHA-256",
        "expected_digest": "sha256:" + "a" * 64,
        "observed_digest": "sha256:" + "a" * 64,
        "proof": {"type": "integrity_proof", "created_at": "2026-05-10T11:00:00Z"},
    }
    expect("class_a_verified", verify_class_a(a_valid), "VERIFIED")
    a_tamp = {**a_valid, "observed_digest": "sha256:" + "b" * 64}
    expect("class_a_tampered", verify_class_a(a_tamp), "TAMPERED")
    a_bad_canon = {**a_valid, "canonicalization": "RFC8785-JCS-v2"}
    expect("class_a_bad_canon", verify_class_a(a_bad_canon), "INVALID")
    a_bad_alg = {**a_valid, "algorithm": "SHA-1", "expected_digest": "sha1:abc",
                 "observed_digest": "sha1:abc"}
    expect("class_a_bad_alg", verify_class_a(a_bad_alg), "INVALID")
    a_telemetry = {**a_valid, "status": "CALIBRATION_IMPROVED"}
    expect("class_a_telemetry_rejected", verify_class_a(a_telemetry), "INVALID")

    # Class B
    b_valid = {
        "class": "B", "regime": "instrumented_empirical_verification", "claim": "x",
        "sources": [{"id": "src-1"}],
        "timestamps": [{"source_id": "src-1", "value": "2026-01-01T00:00:00Z"}],
        "observations": [{"source_id": "src-1", "supports_claim": True}],
        "structural_diff": {},
        "proof": {"type": "empirical_support_record", "created_at": "now"},
    }
    expect("class_b_supported", verify_class_b(b_valid), "SUPPORTED")
    b_conf = {**b_valid, "observations": [
        {"source_id": "src-1", "supports_claim": True},
        {"source_id": "src-2", "supports_claim": False},
    ], "sources": [{"id": "src-1"}, {"id": "src-2"}]}
    expect("class_b_conflicted", verify_class_b(b_conf), "CONFLICTED")
    b_no_sources = {k: v for k, v in b_valid.items() if k != "sources"}
    expect("class_b_invalid_no_sources", verify_class_b(b_no_sources), "INVALID")

    # Class C
    c_valid = {
        "class": "C", "regime": "protocol_bound_consensus", "claim": "x",
        "protocol": {"name": "q", "version": "0.1.0", "required_quorum": 2,
                     "eligible_attesters": ["a", "b"]},
        "evidence": [
            {"attester_id": "a", "attestation": "approve", "eligible": True},
            {"attester_id": "b", "attestation": "approve", "eligible": True},
        ],
        "action_policy": {"action_allowed": False, "action_compelled": False, "reason": ""},
        "proof": {"type": "consensus_process_record", "created_at": "now"},
    }
    expect("class_c_valid", verify_class_c(c_valid), "CONSENSUS_VALID")
    c_dup = {**c_valid, "evidence": [
        {"attester_id": "a", "attestation": "approve", "eligible": True},
        {"attester_id": "a", "attestation": "approve", "eligible": True},
    ]}
    expect("class_c_replay_invalid", verify_class_c(c_dup), "INVALID")
    c_auth = {**c_valid, "action_policy": {
        "action_allowed": True, "action_compelled": False, "reason": ""}}
    expect("class_c_auto_auth_invalid", verify_class_c(c_auth), "INVALID")

    # Class D
    d_valid = {
        "class": "D", "regime": "interpretive_governance", "claim": "x",
        "values_frame": {"optimizing_for": ["a"], "not_optimizing_for": ["b"]},
        "alternatives": [{"id": "alt-1", "summary": "x", "rejected_because": "y"}],
        "reasoning_trace": [{"step": 1, "claim": "x"}],
        "recommended_action": {"kind": "noop", "summary": "x"},
        "reversibility_score": 0.8,
        "challenge_surface": [{"id": "ch-1", "argument": "x"}],
        "calibration": {"calibration_id": "c", "review_after": "now",
                        "success_signals": [], "failure_signals": []},
        "commit_chain": [
            {"stage": 1, "name": "vf", "hash": "sha256:" + "1" * 64,
             "content": {"x": 1}, "depends_on": None,
             "created_at": "2026-01-01T00:00:00Z"},
            {"stage": 2, "name": "alt", "hash": "sha256:" + "2" * 64,
             "content": {"x": 2}, "depends_on": "sha256:" + "1" * 64,
             "created_at": "2026-01-01T00:00:01Z"},
        ],
        "meta_proof": {"process_status": "CONDUCT_VALID",
                       "artifact_hash": "sha256:" + "f" * 64},
    }
    expect("class_d_valid", verify_class_d(d_valid), "CONDUCT_VALID")
    d_no_alt = {**d_valid, "alternatives": []}
    expect("class_d_no_alt_invalid", verify_class_d(d_no_alt), "CONDUCT_INVALID")
    d_broken = {**d_valid, "commit_chain": [
        d_valid["commit_chain"][0],
        {**d_valid["commit_chain"][1], "depends_on": "sha256:" + "9" * 64},
    ]}
    expect("class_d_broken_depends_on", verify_class_d(d_broken), "CONDUCT_INVALID")

    if failures:
        print(f"\nFAIL: {len(failures)} self-check failures")
        return 1
    print("\nPASS: minimal_verifier self-check (14 fixtures)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="WiseOrder minimal independent verifier")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("self-check", help="run hand-crafted per-class fixtures")
    check = sub.add_parser("check", help="verify all vectors under vectors/")
    check.add_argument("--vectors-dir", type=Path, default=DEFAULT_VECTORS_DIR)
    check.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA_PATH)
    check.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)
    if args.cmd is None:
        args.cmd = "check"
        args.vectors_dir = DEFAULT_VECTORS_DIR
        args.schema = DEFAULT_SCHEMA_PATH
        args.quiet = False
    if args.cmd == "self-check":
        return self_check()
    outcomes = check_vectors(args.vectors_dir, args.schema)
    if not args.quiet:
        _print_table(outcomes)
    failed = sum(1 for o in outcomes if not o.passed)
    return 0 if failed == 0 and outcomes else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
