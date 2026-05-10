"""Tests for intellagent_runtime.memory."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from intellagent_runtime import canonical
from intellagent_runtime.memory import AuditMemory, ChainCorrupt
from intellagent_runtime.transitions import EpistemicTransition


def _mk_transition(tid: str, from_state: str = "sha256:" + "a" * 64) -> EpistemicTransition:
    return EpistemicTransition(
        transition_id=tid,
        from_state=from_state,
        regime="A",
        object_added={"class": "A", "claim": "x"},
        objects_removed=[],
        action=None,
        authorization=None,
        proposer="test",
        proposed_at="2026-05-06T12:00:00Z",
    )


def test_empty_memory(tmp_path: Path) -> None:
    audit = AuditMemory(tmp_path / "audit")
    assert audit.head_sha256() is None
    assert audit.next_index() == 0
    assert audit.list_entries() == []


def test_append_first_entry_has_null_prev(tmp_path: Path) -> None:
    canonical.set_clock(lambda: 1735689600.0)
    try:
        audit = AuditMemory(tmp_path / "audit")
        e0 = audit.append(
            transition=_mk_transition("t0"),
            prior_state_id="sha256:" + "a" * 64,
            resulting_state_id="sha256:" + "b" * 64,
        )
    finally:
        canonical.reset_clock()
    assert e0.index == 0
    assert e0.prev_entry_sha256 is None
    assert e0.this_entry_sha256.startswith("sha256:")


def test_chain_links_consecutive_entries(tmp_path: Path) -> None:
    canonical.set_clock(lambda: 1735689600.0)
    try:
        audit = AuditMemory(tmp_path / "audit")
        e0 = audit.append(
            _mk_transition("t0"),
            "sha256:" + "a" * 64,
            "sha256:" + "b" * 64,
        )
        e1 = audit.append(
            _mk_transition("t1", from_state="sha256:" + "b" * 64),
            "sha256:" + "b" * 64,
            "sha256:" + "c" * 64,
        )
    finally:
        canonical.reset_clock()
    assert e1.prev_entry_sha256 == e0.this_entry_sha256
    assert e1.index == 1


def test_verify_chain_passes_for_healthy_chain(tmp_path: Path) -> None:
    audit = AuditMemory(tmp_path / "audit")
    audit.append(_mk_transition("t0"), "sha256:" + "a" * 64, "sha256:" + "b" * 64)
    audit.append(
        _mk_transition("t1", from_state="sha256:" + "b" * 64),
        "sha256:" + "b" * 64,
        "sha256:" + "c" * 64,
    )
    audit.verify_chain()  # should not raise


def test_tampered_entry_body_detected(tmp_path: Path) -> None:
    audit = AuditMemory(tmp_path / "audit")
    audit.append(_mk_transition("t0"), "sha256:" + "a" * 64, "sha256:" + "b" * 64)
    entry_path = audit.dir / "0000.entry.json"
    body = json.loads(entry_path.read_text(encoding="utf-8"))
    body["resulting_state_id"] = "sha256:" + "0" * 64  # tamper
    entry_path.write_text(json.dumps(body, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    with pytest.raises(ChainCorrupt):
        audit.verify_chain()


def test_broken_prev_pointer_detected(tmp_path: Path) -> None:
    audit = AuditMemory(tmp_path / "audit")
    audit.append(_mk_transition("t0"), "sha256:" + "a" * 64, "sha256:" + "b" * 64)
    audit.append(
        _mk_transition("t1", from_state="sha256:" + "b" * 64),
        "sha256:" + "b" * 64,
        "sha256:" + "c" * 64,
    )
    entry_path = audit.dir / "0001.entry.json"
    body = json.loads(entry_path.read_text(encoding="utf-8"))
    body["prev_entry_sha256"] = "sha256:" + "0" * 64  # tamper
    # Re-stamp this_entry_sha256 to a new value so the recomputed-hash check
    # would NOT fire first; we want the prev-pointer check to fire.
    from intellagent_runtime.canonical import canonical_json_bytes, sha256_hex
    without_self = {k: v for k, v in body.items() if k != "this_entry_sha256"}
    body["this_entry_sha256"] = sha256_hex(canonical_json_bytes(without_self))
    entry_path.write_text(json.dumps(body, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    with pytest.raises(ChainCorrupt):
        audit.verify_chain()
