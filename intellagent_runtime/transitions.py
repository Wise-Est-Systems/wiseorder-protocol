"""Transition data types.

`EpistemicTransition` is the runtime's primitive cognitive step: a typed
move from one epistemic state to the next. `Action` and `Authorization`
together gate the consequence boundary (AG1).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Action:
    kind: str
    target: str
    payload: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"kind": self.kind, "target": self.target, "payload": dict(self.payload)}

    @classmethod
    def from_dict(cls, body: dict[str, Any]) -> "Action":
        return cls(
            kind=str(body["kind"]),
            target=str(body["target"]),
            payload=dict(body.get("payload") or {}),
        )


@dataclass
class Authorization:
    source_id: str
    rationale: str

    def to_dict(self) -> dict[str, Any]:
        return {"source_id": self.source_id, "rationale": self.rationale}

    @classmethod
    def from_dict(cls, body: dict[str, Any]) -> "Authorization":
        return cls(
            source_id=str(body["source_id"]),
            rationale=str(body["rationale"]),
        )


@dataclass
class EpistemicTransition:
    transition_id: str
    from_state: str
    regime: str  # "A" | "B" | "C" | "D"
    object_added: dict[str, Any] | None
    objects_removed: list[str]
    action: Action | None
    authorization: Authorization | None
    proposer: str
    proposed_at: str

    @property
    def is_action_bearing(self) -> bool:
        return self.action is not None

    def to_dict(self) -> dict[str, Any]:
        return {
            "transition_id":   self.transition_id,
            "from_state":      self.from_state,
            "regime":          self.regime,
            "object_added":    self.object_added,
            "objects_removed": list(self.objects_removed),
            "action":          self.action.to_dict() if self.action else None,
            "authorization":   self.authorization.to_dict() if self.authorization else None,
            "proposer":        self.proposer,
            "proposed_at":     self.proposed_at,
        }

    @classmethod
    def from_dict(cls, body: dict[str, Any]) -> "EpistemicTransition":
        action = Action.from_dict(body["action"]) if body.get("action") else None
        auth = Authorization.from_dict(body["authorization"]) if body.get("authorization") else None
        return cls(
            transition_id=str(body["transition_id"]),
            from_state=str(body["from_state"]),
            regime=str(body["regime"]),
            object_added=body.get("object_added"),
            objects_removed=list(body.get("objects_removed") or []),
            action=action,
            authorization=auth,
            proposer=str(body.get("proposer", "unknown")),
            proposed_at=str(body.get("proposed_at", "")),
        )


@dataclass
class TransitionResult:
    transition_id: str
    legitimate: bool
    failures: list[str]
    resulting_state: str | None
    committed_to: int | None
    checked_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "transition_id":    self.transition_id,
            "legitimate":       self.legitimate,
            "failures":         list(self.failures),
            "resulting_state":  self.resulting_state,
            "committed_to":     self.committed_to,
            "checked_at":       self.checked_at,
        }
