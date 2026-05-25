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
        """Construct from a dict, validating types and value constraints.

        Raises :class:`TransitionSchemaError` if the body is malformed.
        Validation happens HERE (at load time), not at kernel time, so a typo
        in ``regime`` cannot bypass kernel checks by being silently coerced.
        """
        if not isinstance(body, dict):
            raise TransitionSchemaError(f"transition body must be a dict, got {type(body).__name__}")

        tid = body.get("transition_id")
        if not isinstance(tid, str) or not tid:
            raise TransitionSchemaError("transition_id must be a non-empty string")
        if "/" in tid or ".." in tid or "\x00" in tid:
            raise TransitionSchemaError(f"transition_id contains forbidden characters: {tid!r}")

        from_state = body.get("from_state")
        if not isinstance(from_state, str) or not from_state:
            raise TransitionSchemaError("from_state must be a non-empty string")

        regime = body.get("regime")
        if regime not in {"A", "B", "C", "D"}:
            raise TransitionSchemaError(f"regime must be one of A/B/C/D, got {regime!r}")

        object_added = body.get("object_added")
        if object_added is not None and not isinstance(object_added, dict):
            raise TransitionSchemaError("object_added must be a dict or null")

        objects_removed = body.get("objects_removed") or []
        if not isinstance(objects_removed, list):
            raise TransitionSchemaError("objects_removed must be a list")
        for i, oid in enumerate(objects_removed):
            if not isinstance(oid, str):
                raise TransitionSchemaError(f"objects_removed[{i}] must be a string, got {type(oid).__name__}")

        action_body = body.get("action")
        if action_body is not None and not isinstance(action_body, dict):
            raise TransitionSchemaError("action must be a dict or null")
        action = Action.from_dict(action_body) if action_body else None

        auth_body = body.get("authorization")
        if auth_body is not None and not isinstance(auth_body, dict):
            raise TransitionSchemaError("authorization must be a dict or null")
        auth = Authorization.from_dict(auth_body) if auth_body else None

        proposer = body.get("proposer", "unknown")
        if not isinstance(proposer, str):
            raise TransitionSchemaError("proposer must be a string")

        proposed_at = body.get("proposed_at", "")
        if not isinstance(proposed_at, str):
            raise TransitionSchemaError("proposed_at must be a string")

        return cls(
            transition_id=tid,
            from_state=from_state,
            regime=regime,
            object_added=object_added,
            objects_removed=list(objects_removed),
            action=action,
            authorization=auth,
            proposer=proposer,
            proposed_at=proposed_at,
        )


class TransitionSchemaError(ValueError):
    """Raised when a transition body fails surface-syntax validation."""


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
