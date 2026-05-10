"""Tests for intellagent_runtime.authorization."""

from __future__ import annotations

import json
from pathlib import Path

from intellagent_runtime.authorization import AuthorizationGate
from intellagent_runtime.state import EpistemicState, compute_state_id
from intellagent_runtime.transitions import (
    Action,
    Authorization,
    EpistemicTransition,
)


def _make_policies(tmp_path: Path) -> Path:
    pol = tmp_path / "policies"
    pol.mkdir()
    (pol / "always_deny.json").write_text(json.dumps({
        "source_id": "always_deny",
        "kind": "always_deny",
        "rationale": "test deny",
    }), encoding="utf-8")
    (pol / "test_allowlist.json").write_text(json.dumps({
        "source_id": "test_allowlist",
        "kind": "allowlist",
        "rationale": "test allow",
        "allowed": [{"kind": "log", "target": "any"}],
    }), encoding="utf-8")
    return pol


def _state() -> EpistemicState:
    return EpistemicState(
        state_id=compute_state_id([]),
        objects=[],
        audit_head_sha256=None,
        sealed_at="2026-05-06T12:00:00Z",
    )


def _tau(action=None, auth=None) -> EpistemicTransition:
    return EpistemicTransition(
        transition_id="t-test",
        from_state=compute_state_id([]),
        regime="A",
        object_added={"class": "A"},
        objects_removed=[],
        action=action,
        authorization=auth,
        proposer="test",
        proposed_at="2026-05-06T12:00:00Z",
    )


def test_pure_state_transition_is_authorized(tmp_path: Path) -> None:
    pol = _make_policies(tmp_path)
    gate = AuthorizationGate(pol)
    decision = gate.evaluate(_tau(), _state())
    assert decision.authorized
    assert decision.authorization_source == "not-action-bearing"
    assert "AG1 not engaged" in decision.rationale


def test_action_without_authorization_is_denied(tmp_path: Path) -> None:
    pol = _make_policies(tmp_path)
    gate = AuthorizationGate(pol)
    decision = gate.evaluate(
        _tau(action=Action(kind="log", target="any"), auth=None),
        _state(),
    )
    assert not decision.authorized
    assert "AG1" in decision.rationale


def test_unknown_authorization_source_is_denied(tmp_path: Path) -> None:
    pol = _make_policies(tmp_path)
    gate = AuthorizationGate(pol)
    decision = gate.evaluate(
        _tau(
            action=Action(kind="log", target="any"),
            auth=Authorization(source_id="nonexistent", rationale="test"),
        ),
        _state(),
    )
    assert not decision.authorized
    assert "AG2" in decision.rationale


def test_always_deny_denies(tmp_path: Path) -> None:
    pol = _make_policies(tmp_path)
    gate = AuthorizationGate(pol)
    decision = gate.evaluate(
        _tau(
            action=Action(kind="log", target="any"),
            auth=Authorization(source_id="always_deny", rationale="test"),
        ),
        _state(),
    )
    assert not decision.authorized
    assert "always_deny" in decision.rationale


def test_allowlist_authorizes_matching_action(tmp_path: Path) -> None:
    pol = _make_policies(tmp_path)
    gate = AuthorizationGate(pol)
    decision = gate.evaluate(
        _tau(
            action=Action(kind="log", target="anything"),
            auth=Authorization(source_id="test_allowlist", rationale="test"),
        ),
        _state(),
    )
    assert decision.authorized
    assert decision.authorization_source == "test_allowlist"


def test_allowlist_denies_non_matching_action(tmp_path: Path) -> None:
    pol = _make_policies(tmp_path)
    gate = AuthorizationGate(pol)
    decision = gate.evaluate(
        _tau(
            action=Action(kind="write_file", target="/etc/passwd"),
            auth=Authorization(source_id="test_allowlist", rationale="test"),
        ),
        _state(),
    )
    assert not decision.authorized
    assert "no entry permits" in decision.rationale
