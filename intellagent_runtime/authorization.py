"""Authorization gate.

The gate enforces AG1–AG3 *separately* from the kernel's verification verdicts.
A transition that the kernel accepts can still be refused at this gate; a
transition that is not action-bearing bypasses the gate entirely (the gate
returns ``authorized=True`` with rationale ``not-action-bearing``).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from intellagent_runtime.canonical import short_id, utcnow_iso8601
from intellagent_runtime.transitions import EpistemicTransition


@dataclass
class AuthorizationDecision:
    decision_id: str
    transition_id: str
    authorized: bool
    authorization_source: str | None
    rationale: str
    decided_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision_id":          self.decision_id,
            "transition_id":        self.transition_id,
            "authorized":           self.authorized,
            "authorization_source": self.authorization_source,
            "rationale":            self.rationale,
            "decided_at":           self.decided_at,
        }


# ---------------------------------------------------------------------------
# Policies
# ---------------------------------------------------------------------------


class Policy:
    """Base class for an authorization-source policy."""

    rationale: str = ""

    def evaluate(self, transition: EpistemicTransition) -> tuple[bool, str]:
        raise NotImplementedError


class AlwaysDenyPolicy(Policy):
    def __init__(self, rationale: str = "always_deny"):
        self.rationale = rationale

    def evaluate(self, transition: EpistemicTransition) -> tuple[bool, str]:
        return False, f"always_deny: {self.rationale}"


class AllowlistPolicy(Policy):
    def __init__(self, allowed: list[dict[str, str]], rationale: str = ""):
        self.allowed = allowed
        self.rationale = rationale

    def evaluate(self, transition: EpistemicTransition) -> tuple[bool, str]:
        action = transition.action
        if action is None:  # defensive; gate should not call us in that case
            return False, "policy invoked on non-action-bearing transition"
        for entry in self.allowed:
            if entry.get("kind") != action.kind:
                continue
            target = entry.get("target")
            if target == "any" or target == action.target:
                return True, (
                    f"allowlist: ({entry['kind']}, {target}) permits "
                    f"({action.kind}, {action.target})"
                )
        return False, (
            f"allowlist: no entry permits ({action.kind}, {action.target})"
        )


def _load_policy(body: dict[str, Any]) -> Policy | None:
    kind = body.get("kind")
    if kind == "always_deny":
        return AlwaysDenyPolicy(rationale=str(body.get("rationale", "")))
    if kind == "allowlist":
        return AllowlistPolicy(
            allowed=list(body.get("allowed") or []),
            rationale=str(body.get("rationale", "")),
        )
    return None


# ---------------------------------------------------------------------------
# Gate
# ---------------------------------------------------------------------------


class AuthorizationGate:
    """Resolves a transition's declared ``authorization.source_id`` against a
    local policy directory and returns an :class:`AuthorizationDecision`."""

    def __init__(self, policies_dir: Path):
        self.policies_dir = Path(policies_dir)

    def resolve_policy(self, source_id: str) -> Policy | None:
        path = self.policies_dir / f"{source_id}.json"
        if not path.is_file():
            return None
        try:
            body = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None
        return _load_policy(body)

    def evaluate(
        self,
        transition: EpistemicTransition,
        prior_state,  # EpistemicState (avoid circular import)
    ) -> AuthorizationDecision:
        if not transition.is_action_bearing:
            return AuthorizationDecision(
                decision_id=short_id(),
                transition_id=transition.transition_id,
                authorized=True,
                authorization_source="not-action-bearing",
                rationale=("Pure state transition; no external action; "
                           "AG1 not engaged."),
                decided_at=utcnow_iso8601(),
            )

        if transition.authorization is None:
            return AuthorizationDecision(
                decision_id=short_id(),
                transition_id=transition.transition_id,
                authorized=False,
                authorization_source=None,
                rationale=("AG1: action-bearing transition without declared "
                           "authorization. Refused before policy lookup."),
                decided_at=utcnow_iso8601(),
            )

        source_id = transition.authorization.source_id
        if not source_id:
            return AuthorizationDecision(
                decision_id=short_id(),
                transition_id=transition.transition_id,
                authorized=False,
                authorization_source=None,
                rationale="AG3: authorization object missing source_id.",
                decided_at=utcnow_iso8601(),
            )

        policy = self.resolve_policy(source_id)
        if policy is None:
            return AuthorizationDecision(
                decision_id=short_id(),
                transition_id=transition.transition_id,
                authorized=False,
                authorization_source=source_id,
                rationale=(f"AG2: authorization_source {source_id!r} has no "
                           "resolvable policy."),
                decided_at=utcnow_iso8601(),
            )

        allow, rationale = policy.evaluate(transition)
        return AuthorizationDecision(
            decision_id=short_id(),
            transition_id=transition.transition_id,
            authorized=allow,
            authorization_source=source_id,
            rationale=rationale,
            decided_at=utcnow_iso8601(),
        )
