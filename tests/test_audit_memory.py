"""Tests for intellagent_runtime/audit_memory.py."""

from __future__ import annotations

import json
import pytest

from intellagent_runtime.audit_memory import (
    AUDIT_CHAIN_EMPTY,
    AUDIT_CHAIN_INVALID,
    AUDIT_CHAIN_TAMPERED,
    AUDIT_CHAIN_VALID,
    AuditEvent,
    AuditMemoryError,
    append_event,
    export_summary,
    read_events,
    self_check,
    verify_chain,
)


# ---------------------------------------------------------------------------
# Empty state
# ---------------------------------------------------------------------------


def test_verify_chain_on_missing_file(tmp_path):
    s = verify_chain(tmp_path / "absent.jsonl")
    assert s.status == AUDIT_CHAIN_EMPTY
    assert s.count == 0
    assert s.last_hash is None


def test_read_events_on_missing_file(tmp_path):
    assert read_events(tmp_path / "absent.jsonl") == []


# ---------------------------------------------------------------------------
# Append + read
# ---------------------------------------------------------------------------


def test_append_one_event(tmp_path):
    path = tmp_path / "run.jsonl"
    e = append_event(path, "run.started", {"wo": "X"})
    assert e.seq == 1
    assert e.prev_hash is None
    assert e.hash.startswith("sha256:")
    assert len(e.hash) == len("sha256:") + 64


def test_append_chains_prev_hash(tmp_path):
    path = tmp_path / "run.jsonl"
    e1 = append_event(path, "a")
    e2 = append_event(path, "b")
    assert e2.prev_hash == e1.hash
    assert e2.seq == 2


def test_read_events_returns_appended(tmp_path):
    path = tmp_path / "run.jsonl"
    append_event(path, "a", {"x": 1})
    append_event(path, "b", {"y": 2})
    events = read_events(path)
    assert len(events) == 2
    assert events[0].event == "a"
    assert events[1].event == "b"


# ---------------------------------------------------------------------------
# Hash integrity
# ---------------------------------------------------------------------------


def test_hash_is_sha256_hex(tmp_path):
    path = tmp_path / "run.jsonl"
    e = append_event(path, "x")
    assert e.hash.startswith("sha256:")
    rest = e.hash[len("sha256:"):]
    assert all(c in "0123456789abcdef" for c in rest)
    assert len(rest) == 64


def test_recompute_matches_stored(tmp_path):
    path = tmp_path / "run.jsonl"
    append_event(path, "a", {"k": "v"})
    s = verify_chain(path)
    assert s.status == AUDIT_CHAIN_VALID
    assert s.count == 1


# ---------------------------------------------------------------------------
# Tamper detection
# ---------------------------------------------------------------------------


def test_tamper_detected_payload_edit(tmp_path):
    path = tmp_path / "run.jsonl"
    append_event(path, "a", {"command_count": 3})
    append_event(path, "b", {"x": 1})
    raw = path.read_text(encoding="utf-8").splitlines()
    # Edit the payload of event 1 without recomputing its hash.
    raw[0] = raw[0].replace('"command_count":3', '"command_count":999')
    path.write_text("\n".join(raw) + "\n", encoding="utf-8")
    s = verify_chain(path)
    assert s.status == AUDIT_CHAIN_TAMPERED
    assert s.first_failure_seq == 1


def test_tamper_detected_prev_hash_edit(tmp_path):
    import re
    path = tmp_path / "run.jsonl"
    append_event(path, "a")
    append_event(path, "b")
    raw = path.read_text(encoding="utf-8").splitlines()
    # Flip exactly one hex character inside prev_hash of event 2,
    # preserving line length and JSON structure.
    line2 = raw[1]
    m = re.search(r'"prev_hash":"sha256:([0-9a-f]{64})"', line2)
    assert m, "prev_hash not found in event 2"
    orig_hex = m.group(1)
    flipped = ("f" if orig_hex[0] != "f" else "e") + orig_hex[1:]
    raw[1] = line2.replace(orig_hex, flipped)
    path.write_text("\n".join(raw) + "\n", encoding="utf-8")
    s = verify_chain(path)
    assert s.status == AUDIT_CHAIN_TAMPERED


# ---------------------------------------------------------------------------
# Invalid structure
# ---------------------------------------------------------------------------


def test_malformed_jsonl_invalid(tmp_path):
    path = tmp_path / "run.jsonl"
    path.write_text("{not valid json\n", encoding="utf-8")
    s = verify_chain(path)
    assert s.status == AUDIT_CHAIN_INVALID


def test_missing_field_invalid(tmp_path):
    path = tmp_path / "run.jsonl"
    path.write_text(json.dumps({"seq": 1, "ts": "x", "event": "a"}) + "\n", encoding="utf-8")
    s = verify_chain(path)
    assert s.status == AUDIT_CHAIN_INVALID


def test_non_monotonic_seq_invalid(tmp_path):
    path = tmp_path / "run.jsonl"
    # Write a synthetic "event 2 before event 1" log; we can't go through
    # append_event because that would auto-assign seq.
    e1 = json.dumps({
        "seq": 2, "ts": "x", "event": "a", "payload": {},
        "prev_hash": None, "hash": "0" * 64,
    })
    path.write_text(e1 + "\n", encoding="utf-8")
    s = verify_chain(path)
    assert s.status == AUDIT_CHAIN_INVALID
    assert "seq" in s.reason


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------


def test_export_summary_counts_events(tmp_path):
    path = tmp_path / "run.jsonl"
    append_event(path, "a")
    append_event(path, "a")
    append_event(path, "b")
    summary = export_summary(path)
    assert summary["event_count"] == 3
    assert summary["event_types"]["a"] == 2
    assert summary["event_types"]["b"] == 1
    assert summary["chain_status"]["status"] == AUDIT_CHAIN_VALID


def test_export_summary_on_empty_file(tmp_path):
    summary = export_summary(tmp_path / "nope.jsonl")
    assert summary["event_count"] == 0
    assert summary["chain_status"]["status"] == AUDIT_CHAIN_EMPTY


# ---------------------------------------------------------------------------
# Dataclass behavior
# ---------------------------------------------------------------------------


def test_audit_event_to_dict_includes_hash():
    e = AuditEvent(seq=1, ts="x", event="a", payload={}, prev_hash=None, hash="h")
    d = e.to_dict()
    assert d["hash"] == "h"
    assert "prev_hash" in d


def test_audit_event_core_dict_excludes_hash():
    e = AuditEvent(seq=1, ts="x", event="a", payload={}, prev_hash=None, hash="h")
    assert "hash" not in e.core_dict()


def test_self_check_returns_zero(capsys):
    rc = self_check()
    out = capsys.readouterr().out
    assert rc == 0
    assert "PASS" in out
