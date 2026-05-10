"""WiseOrder kernel adapter for Intellagent v0.1.

The kernel performs class-specific structural checks against the WiseOrder
invariants for the regime declared by a transition. The checks here mirror
(in code) the conformance vectors under ``vectors/``; they intentionally
duplicate those rules rather than dispatch through the vector runner, so
v0.1 has no machinery dependency beyond the spec invariants themselves.

A future v0.2 may unify this with a single
``tools/verify_artifact_against_class.py`` shared between vectors and the
runtime.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from intellagent_runtime.canonical import is_sha256, utcnow_iso8601
from intellagent_runtime.transitions import EpistemicTransition

TELEMETRY_TOKENS = frozenset({"CALIBRATION_IMPROVED", "CALIBRATION_DEGRADED"})

CLASS_A_STATUSES = frozenset({"VERIFIED", "TAMPERED", "INVALID"})
CLASS_B_STATUSES = frozenset({"SUPPORTED", "CONFLICTED", "INSUFFICIENT_EVIDENCE", "INVALID"})
CLASS_C_STATUSES = frozenset({"CONSENSUS_PENDING", "CONSENSUS_VALID", "CONSENSUS_FAILED", "INVALID"})
CLASS_D_STATUSES = frozenset({"CONDUCT_VALID", "CONDUCT_INVALID"})


@dataclass
class KernelVerdict:
    passed: bool
    failures: list[str] = field(default_factory=list)
    checked_at: str = ""


# ---------------------------------------------------------------------------
# Per-class object verifiers
# ---------------------------------------------------------------------------


def _verify_class_a_object(obj: dict[str, Any]) -> list[str]:
    f: list[str] = []
    if obj.get("class") != "A":
        f.append(f"object.class must be 'A' under regime A (got {obj.get('class')!r})")

    canon = obj.get("canonicalization")
    if canon != "RFC8785-JCS":
        f.append(
            f"CS1: Class A canonicalization must be 'RFC8785-JCS' under v0.1.0 "
            f"(got {canon!r})"
        )

    if not obj.get("algorithm"):
        f.append("A2/CS1: algorithm is required")

    expected = obj.get("expected_digest")
    observed = obj.get("observed_digest")
    if not is_sha256(expected):
        f.append(f"A2: expected_digest must be 'sha256:<64 hex>' (got {expected!r})")
    if not is_sha256(observed):
        f.append(f"A2: observed_digest must be 'sha256:<64 hex>' (got {observed!r})")

    status = obj.get("status")
    if status in TELEMETRY_TOKENS:
        f.append(f"§9: telemetry token {status!r} cannot be used as artifact status")
    elif status not in CLASS_A_STATUSES:
        f.append(
            f"Class A status must be one of {sorted(CLASS_A_STATUSES)} "
            f"(got {status!r})"
        )
    elif status == "VERIFIED" and is_sha256(expected) and is_sha256(observed) and expected != observed:
        f.append("VERIFIED requires expected_digest == observed_digest (A1)")
    elif status == "TAMPERED" and is_sha256(expected) and is_sha256(observed) and expected == observed:
        f.append("TAMPERED requires expected_digest != observed_digest (A1)")
    return f


def _verify_class_b_object(obj: dict[str, Any]) -> list[str]:
    f: list[str] = []
    if obj.get("class") != "B":
        f.append(f"object.class must be 'B' under regime B (got {obj.get('class')!r})")

    sources = obj.get("sources")
    if not isinstance(sources, list) or not sources:
        f.append("B1: sources must be a non-empty list (every source declared explicitly)")

    if not isinstance(obj.get("timestamps"), list):
        f.append("B3: timestamps must be a list (auditable ordering)")
    if not isinstance(obj.get("observations"), list):
        f.append("observations must be a list")
    if not isinstance(obj.get("structural_diff"), dict):
        f.append("structural_diff must be an object")

    status = obj.get("status")
    if status in TELEMETRY_TOKENS:
        f.append(f"§9: telemetry token {status!r} cannot be used as artifact status")
    elif status not in CLASS_B_STATUSES:
        f.append(
            f"Class B status must be one of {sorted(CLASS_B_STATUSES)} "
            f"(got {status!r})"
        )

    obs = obj.get("observations") or []
    if status == "CONFLICTED":
        sup_vals = [o.get("supports_claim") for o in obs if isinstance(o, dict)]
        has_true = True in sup_vals
        has_false = False in sup_vals
        if not (has_true and has_false):
            f.append(
                "B2: CONFLICTED status requires both supporting (supports_claim=true) "
                "and refuting (supports_claim=false) observations preserved"
            )
    return f


def _verify_class_c_object(obj: dict[str, Any]) -> list[str]:
    f: list[str] = []
    if obj.get("class") != "C":
        f.append(f"object.class must be 'C' under regime C (got {obj.get('class')!r})")

    protocol = obj.get("protocol")
    if not isinstance(protocol, dict):
        f.append("C1: protocol object is required")
        return f

    if "required_quorum" not in protocol:
        f.append("C1: protocol.required_quorum is required")
    eligible_attesters = protocol.get("eligible_attesters")
    if not isinstance(eligible_attesters, list):
        f.append("C1: protocol.eligible_attesters must be a list")
        eligible_attesters = []

    eligible = set(eligible_attesters)
    evidence = obj.get("evidence")
    if not isinstance(evidence, list):
        f.append("C4: evidence must be a list")
        evidence = []

    status = obj.get("status")
    if status in TELEMETRY_TOKENS:
        f.append(f"§9: telemetry token {status!r} cannot be used as artifact status")
    elif status not in CLASS_C_STATUSES:
        f.append(
            f"Class C status must be one of {sorted(CLASS_C_STATUSES)} "
            f"(got {status!r})"
        )

    # C2: any attester not in eligible_attesters → status MUST be INVALID
    bad_attesters: list[str] = []
    for e in evidence:
        if isinstance(e, dict):
            attester = e.get("attester_id")
            if attester and attester not in eligible:
                bad_attesters.append(attester)
    if bad_attesters and status != "INVALID":
        f.append(
            f"C2: attestation(s) from unauthorized participant(s) {bad_attesters!r} "
            "present; status MUST be INVALID"
        )

    action_policy = obj.get("action_policy")
    if not isinstance(action_policy, dict):
        f.append("AG3: action_policy object is required")
        return f
    if "action_allowed" not in action_policy:
        f.append("action_policy.action_allowed is required")
    if "reason" not in action_policy:
        f.append("AG3: action_policy.reason is required")

    # AG1 contrapositive: action_allowed=true requires authorization_source.
    if action_policy.get("action_allowed") is True:
        auth_source = action_policy.get("authorization_source")
        if not auth_source:
            f.append(
                "AG1/AG3: action_allowed=true requires an explicit "
                "authorization_source; consensus is not authorization"
            )
    return f


def _verify_class_d_object(obj: dict[str, Any]) -> list[str]:
    f: list[str] = []
    if obj.get("class") != "D":
        f.append(f"object.class must be 'D' under regime D (got {obj.get('class')!r})")

    vf = obj.get("values_frame")
    if not isinstance(vf, dict):
        f.append("D1: values_frame is required (object)")
    else:
        if not vf.get("optimizing_for"):
            f.append("D1: values_frame.optimizing_for must be a non-empty list")
        if not vf.get("not_optimizing_for"):
            f.append("D1: values_frame.not_optimizing_for must be a non-empty list")

    alternatives = obj.get("alternatives")
    if not isinstance(alternatives, list) or not alternatives:
        f.append("D2: alternatives must be a non-empty list (≥1 defensible alternative)")

    challenge = obj.get("challenge_surface")
    if not isinstance(challenge, list) or not challenge:
        f.append("D3: challenge_surface must be a non-empty list (self-generated counterarguments)")

    commit_chain = obj.get("commit_chain")
    if not isinstance(commit_chain, list) or not commit_chain:
        f.append("CC3: commit_chain must be a non-empty list")
    else:
        prev_hash: str | None = None
        for i, stage in enumerate(commit_chain, start=1):
            if not isinstance(stage, dict):
                f.append(f"CC3: stage at position {i} must be an object")
                continue
            if stage.get("stage") != i:
                f.append(
                    f"CC4: stage at position {i} declares stage={stage.get('stage')!r}; "
                    "must monotonically increase from 1"
                )
            stage_hash = stage.get("hash")
            if not is_sha256(stage_hash):
                f.append(f"CC1: stage {i}.hash must be 'sha256:<64 hex>' (got {stage_hash!r})")
            if "content" not in stage or stage["content"] is None:
                f.append(
                    f"D5/CC1: stage {i} missing preimage content "
                    "(hash without preimage is unauditable)"
                )
            depends = stage.get("depends_on")
            if i == 1:
                if depends is not None:
                    f.append(f"CC2: stage 1 depends_on must be null (got {depends!r})")
            else:
                if depends != prev_hash:
                    f.append(
                        f"CC2: stage {i}.depends_on={depends!r} does not match "
                        f"prior stage hash {prev_hash!r}"
                    )
            prev_hash = stage_hash

    status = obj.get("status")
    if status == "VERIFIED":
        f.append("D4: Class D MUST NOT receive VERIFIED status (use CONDUCT_VALID/CONDUCT_INVALID)")
    elif status in TELEMETRY_TOKENS:
        f.append(f"§9: telemetry token {status!r} cannot be used as artifact status")
    elif status not in CLASS_D_STATUSES:
        f.append(
            f"Class D status must be one of {sorted(CLASS_D_STATUSES)} "
            f"(got {status!r})"
        )
    return f


_CLASS_VERIFIERS = {
    "A": _verify_class_a_object,
    "B": _verify_class_b_object,
    "C": _verify_class_c_object,
    "D": _verify_class_d_object,
}


# ---------------------------------------------------------------------------
# Kernel
# ---------------------------------------------------------------------------


class WiseOrderKernel:
    """Adapter that runs class-specific WiseOrder invariants against a
    proposed transition. Pure structural checks; no I/O."""

    def __init__(self, repo_root: Path | None = None):
        # repo_root reserved for future use (loading vector schemas dynamically).
        self.repo_root = repo_root

    def verify(
        self,
        transition: EpistemicTransition,
        prior_state,  # EpistemicState (avoid circular import)
    ) -> KernelVerdict:
        failures: list[str] = []

        if transition.regime not in {"A", "B", "C", "D"}:
            failures.append(f"transition.regime must be one of A/B/C/D (got {transition.regime!r})")
            return KernelVerdict(False, failures, utcnow_iso8601())

        if transition.from_state != prior_state.state_id:
            failures.append(
                f"transition.from_state={transition.from_state!r} does not match "
                f"current state_id {prior_state.state_id!r}"
            )

        # AG1 enforced at proposal time: an action-bearing transition MUST carry
        # a declared authorization. The gate later evaluates the source's
        # policy independently.
        if transition.is_action_bearing and transition.authorization is None:
            failures.append(
                "AG1: action-bearing transition (action != null) requires a declared "
                "authorization (separate from verification status); consensus is not "
                "authorization"
            )

        # objects_removed must reference held objects.
        for removed in transition.objects_removed:
            if removed not in prior_state.objects:
                failures.append(
                    f"objects_removed: {removed!r} not present in current state"
                )

        # Per-class object check (only if object_added is supplied).
        if transition.object_added is not None:
            verifier = _CLASS_VERIFIERS[transition.regime]
            failures.extend(verifier(transition.object_added))
        elif not transition.objects_removed:
            failures.append(
                "transition has neither object_added nor objects_removed; "
                "a transition must change the state"
            )

        return KernelVerdict(
            passed=not failures,
            failures=failures,
            checked_at=utcnow_iso8601(),
        )
