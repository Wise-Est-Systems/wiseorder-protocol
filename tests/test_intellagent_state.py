"""Tests for intellagent_runtime.state."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from intellagent_runtime import canonical
from intellagent_runtime.state import (
    EpistemicState,
    ObjectStore,
    StateStore,
    StateTampered,
    compute_object_id,
    compute_state_id,
)


def test_compute_state_id_is_deterministic_for_empty_objects() -> None:
    a = compute_state_id([])
    b = compute_state_id([])
    assert a == b
    assert a.startswith("sha256:") and len(a) == len("sha256:") + 64


def test_compute_state_id_orders_objects_canonically() -> None:
    a = compute_state_id(["sha256:" + "a" * 64, "sha256:" + "b" * 64])
    b = compute_state_id(["sha256:" + "b" * 64, "sha256:" + "a" * 64])
    assert a == b


def test_compute_object_id_strips_self_field() -> None:
    body = {"class": "A", "claim": "x"}
    body_with_id = {**body, "object_id": "sha256:" + "0" * 64}
    assert compute_object_id(body) == compute_object_id(body_with_id)


def test_initial_state_has_known_state_id() -> None:
    canonical.set_clock(lambda: 1735689600.0)
    try:
        s = EpistemicState.initial()
    finally:
        canonical.reset_clock()
    assert s.objects == []
    assert s.audit_head_sha256 is None
    assert s.state_id == compute_state_id([])


def test_state_store_init_and_load_roundtrip(tmp_path: Path) -> None:
    canonical.set_clock(lambda: 1735689600.0)
    try:
        store = StateStore(tmp_path)
        initial = store.init()
        loaded = store.load()
    finally:
        canonical.reset_clock()
    assert initial.state_id == loaded.state_id
    assert loaded.objects == []


def test_state_store_refuses_double_init(tmp_path: Path) -> None:
    store = StateStore(tmp_path)
    store.init()
    with pytest.raises(FileExistsError):
        store.init()


def test_state_tampering_is_detected_on_load(tmp_path: Path) -> None:
    store = StateStore(tmp_path)
    store.init()
    body = json.loads(store.state_path.read_text(encoding="utf-8"))
    body["state_id"] = "sha256:" + "0" * 64
    store.state_path.write_text(json.dumps(body, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    with pytest.raises(StateTampered):
        store.load()


def test_object_store_round_trip(tmp_path: Path) -> None:
    obj_store = ObjectStore(tmp_path / "objects")
    body = {"class": "A", "claim": "test", "canonicalization": "RFC8785-JCS"}
    oid = obj_store.put(body)
    assert obj_store.has(oid)
    fetched = obj_store.get(oid)
    assert fetched["object_id"] == oid
    assert fetched["claim"] == "test"


def test_object_store_idempotent_put(tmp_path: Path) -> None:
    obj_store = ObjectStore(tmp_path / "objects")
    body = {"class": "A", "claim": "same"}
    a = obj_store.put(body)
    b = obj_store.put({**body})
    assert a == b
