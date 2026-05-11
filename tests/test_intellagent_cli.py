"""Tests for intellagent_runtime.cli (subprocess-driven, end-to-end)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
HEX64_A = "a" * 64
HEX64_B = "b" * 64


def _run(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO) + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run(
        [sys.executable, "-m", "intellagent_runtime.cli", *args],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
    )


def test_cli_init_creates_dirs_and_state(tmp_path: Path) -> None:
    proc = _run(["init"], tmp_path)
    assert proc.returncode == 0, proc.stderr
    assert "Initialized:" in proc.stdout
    assert (tmp_path / "intellagent_state" / "current.json").is_file()
    assert (tmp_path / "intellagent_audit").is_dir()
    assert (tmp_path / "intellagent_refusals").is_dir()
    assert (tmp_path / "intellagent_objects").is_dir()


def test_cli_state_prints_initial_state(tmp_path: Path) -> None:
    _run(["init"], tmp_path)
    proc = _run(["state", "--json"], tmp_path)
    assert proc.returncode == 0, proc.stderr
    body = json.loads(proc.stdout)
    assert body["objects"] == []
    assert body["audit_head_sha256"] is None
    assert body["state_id"].startswith("sha256:")


def test_cli_propose_then_transition_legitimate_class_a(tmp_path: Path) -> None:
    _run(["init"], tmp_path)
    state_body = json.loads((tmp_path / "intellagent_state" / "current.json").read_text())
    state_id = state_body["state_id"]

    transition_body = {
        "transition_id":   "prop-cli-001",
        "from_state":      state_id,
        "regime":          "A",
        "object_added": {
            "class":            "A",
            "regime":           "deterministic_verification",
            "claim":            "cli demo",
            "canonicalization": "RFC8785-JCS",
            "algorithm":        "SHA-256",
            "expected_digest":  f"sha256:{HEX64_A}",
            "observed_digest":  f"sha256:{HEX64_A}",
            "status":           "VERIFIED",
        },
        "objects_removed": [],
        "action":          None,
        "authorization":   None,
        "proposer":        "manual",
        "proposed_at":     "2026-05-06T12:00:00Z",
    }
    tfile = tmp_path / "prop.json"
    tfile.write_text(json.dumps(transition_body, indent=2), encoding="utf-8")

    p = _run(["propose", "--file", str(tfile)], tmp_path)
    assert p.returncode == 0, p.stderr
    assert "QUEUED" in p.stdout

    t = _run(["transition", "prop-cli-001"], tmp_path)
    assert t.returncode == 0, t.stderr
    assert "LEGITIMATE" in t.stdout
    assert "audit entry 0000" in t.stdout
    assert (tmp_path / "intellagent_audit" / "0000.entry.json").is_file()


def test_cli_transition_rejects_bad_class_d(tmp_path: Path) -> None:
    _run(["init"], tmp_path)
    state_body = json.loads((tmp_path / "intellagent_state" / "current.json").read_text())
    state_id = state_body["state_id"]
    bad_body = {
        "transition_id":   "prop-cli-002",
        "from_state":      state_id,
        "regime":          "D",
        "object_added": {
            "class": "D",
            "regime": "interpretive_governance",
            "claim": "bad",
            "values_frame": {"optimizing_for": ["x"], "not_optimizing_for": ["y"]},
            "alternatives": [],
            "challenge_surface": [],
            "commit_chain": [],
            "status": "CONDUCT_VALID",
        },
        "objects_removed": [],
        "action":          None,
        "authorization":   None,
        "proposer":        "manual",
        "proposed_at":     "2026-05-06T12:00:00Z",
    }
    tfile = tmp_path / "bad.json"
    tfile.write_text(json.dumps(bad_body), encoding="utf-8")
    _run(["propose", "--file", str(tfile)], tmp_path)
    t = _run(["transition", "prop-cli-002"], tmp_path)
    assert t.returncode == 0, t.stderr
    assert "REJECTED" in t.stdout
    assert "D2" in t.stdout or "D3" in t.stdout
    # No new audit entry.
    assert not (tmp_path / "intellagent_audit" / "0000.entry.json").exists()


def test_cli_audit_lists_entries(tmp_path: Path) -> None:
    _run(["init"], tmp_path)
    # Use the helper from the previous test: build a class A and commit.
    state_body = json.loads((tmp_path / "intellagent_state" / "current.json").read_text())
    state_id = state_body["state_id"]
    tbody = {
        "transition_id":   "prop-cli-003",
        "from_state":      state_id,
        "regime":          "A",
        "object_added": {
            "class":            "A",
            "regime":           "deterministic_verification",
            "claim":            "audit demo",
            "canonicalization": "RFC8785-JCS",
            "algorithm":        "SHA-256",
            "expected_digest":  f"sha256:{HEX64_A}",
            "observed_digest":  f"sha256:{HEX64_A}",
            "status":           "VERIFIED",
        },
        "objects_removed": [],
        "action": None,
        "authorization": None,
        "proposer": "manual",
        "proposed_at": "2026-05-06T12:00:00Z",
    }
    tfile = tmp_path / "audit-prop.json"
    tfile.write_text(json.dumps(tbody), encoding="utf-8")
    _run(["propose", "--file", str(tfile)], tmp_path)
    _run(["transition", "prop-cli-003"], tmp_path)

    a = _run(["audit", "--json"], tmp_path)
    assert a.returncode == 0, a.stderr
    entries = json.loads(a.stdout)
    assert len(entries) == 1
    assert entries[0]["transition"]["transition_id"] == "prop-cli-003"


def test_cli_refuse_seals_a_record(tmp_path: Path) -> None:
    _run(["init"], tmp_path)
    r = _run(["refuse", "--query", "demo refusal"], tmp_path)
    assert r.returncode == 0, r.stderr
    assert "refusal_id:" in r.stdout
    refusals = list((tmp_path / "intellagent_refusals").glob("refusal-*.json"))
    assert len(refusals) == 1


def test_cli_chain_corrupt_is_detected(tmp_path: Path) -> None:
    """If the audit chain is tampered with, `transition` fails closed (exit 2)."""
    _run(["init"], tmp_path)
    # Commit one legitimate transition so there is something to corrupt.
    state_body = json.loads((tmp_path / "intellagent_state" / "current.json").read_text())
    tbody = {
        "transition_id":   "prop-cli-004",
        "from_state":      state_body["state_id"],
        "regime":          "A",
        "object_added": {
            "class":            "A",
            "regime":           "deterministic_verification",
            "claim":            "x",
            "canonicalization": "RFC8785-JCS",
            "algorithm":        "SHA-256",
            "expected_digest":  f"sha256:{HEX64_A}",
            "observed_digest":  f"sha256:{HEX64_A}",
            "status":           "VERIFIED",
        },
        "objects_removed": [],
        "action": None,
        "authorization": None,
        "proposer": "manual",
        "proposed_at": "2026-05-06T12:00:00Z",
    }
    tfile = tmp_path / "p.json"
    tfile.write_text(json.dumps(tbody), encoding="utf-8")
    _run(["propose", "--file", str(tfile)], tmp_path)
    _run(["transition", "prop-cli-004"], tmp_path)

    # Tamper with the entry body without re-stamping its hash.
    entry_path = tmp_path / "intellagent_audit" / "0000.entry.json"
    body = json.loads(entry_path.read_text(encoding="utf-8"))
    body["resulting_state_id"] = "sha256:" + "0" * 64
    entry_path.write_text(json.dumps(body, sort_keys=True, indent=2), encoding="utf-8")

    # Try a second transition; chain check at the top of `transition` should fire.
    state_body2 = json.loads((tmp_path / "intellagent_state" / "current.json").read_text())
    tbody2 = dict(tbody)
    tbody2["transition_id"] = "prop-cli-005"
    tbody2["from_state"] = state_body2["state_id"]
    tbody2["object_added"] = {**tbody["object_added"], "claim": "y"}
    tfile2 = tmp_path / "p2.json"
    tfile2.write_text(json.dumps(tbody2), encoding="utf-8")
    _run(["propose", "--file", str(tfile2)], tmp_path)
    out = _run(["transition", "prop-cli-005"], tmp_path)
    assert out.returncode == 2
    assert "CHAIN_CORRUPT" in out.stderr


# ---------------------------------------------------------------------------
# governed-run subcommand (WORK ORDER 015)
# ---------------------------------------------------------------------------


VALID_GR_WO = """# WORK ORDER X — governed-run cli test
## Objective
exercise governed-run from the CLI

## Required Commands
```bash
make ci
```

## Workflow
- inspect
- propose
- review
- execute
- verify
- report
- stop

## Do Not Modify
- vectors/**

Stop.
"""


REFUSED_GR_WO = """# WORK ORDER X — governed-run refused
## Objective
trigger refusal

## Required Commands
```bash
rm -rf /
```

## Workflow
- inspect
- propose
- review
- execute
- verify
- report
- stop

Stop.
"""


def test_governed_run_self_check_returns_zero(tmp_path: Path) -> None:
    proc = _run(["governed-run", "--self-check"], tmp_path)
    assert proc.returncode == 0, proc.stderr
    assert "PASS" in proc.stdout


def test_governed_run_valid_returns_zero_and_valid_status(tmp_path: Path) -> None:
    wo = tmp_path / "wo.md"
    wo.write_text(VALID_GR_WO, encoding="utf-8")
    proc = _run(["governed-run", "--work-order", str(wo), "--dry-run"], tmp_path)
    assert proc.returncode == 0, proc.stderr
    manifest = json.loads(proc.stdout)
    assert manifest["final_status"] == "GOVERNED_RUN_VALID"
    assert manifest["validation_status"] == "VALID"
    assert "make ci" in manifest["required_commands"]
    assert "vectors/**" in manifest["protected_paths"]


def test_governed_run_refused_returns_one_and_refused_status(tmp_path: Path) -> None:
    wo = tmp_path / "wo.md"
    wo.write_text(REFUSED_GR_WO, encoding="utf-8")
    proc = _run(["governed-run", "--work-order", str(wo), "--dry-run"], tmp_path)
    assert proc.returncode == 1, proc.stderr
    manifest = json.loads(proc.stdout)
    assert manifest["final_status"] == "GOVERNED_RUN_REFUSED"
    assert manifest["validation_status"] == "REFUSED"
    assert manifest["validation_violations"], "expected violations"


def test_governed_run_invalid_work_order_returns_two(tmp_path: Path) -> None:
    proc = _run(["governed-run", "--work-order", str(tmp_path / "nope.md"), "--dry-run"], tmp_path)
    assert proc.returncode == 2, proc.stderr
    manifest = json.loads(proc.stdout)
    assert manifest["final_status"] == "GOVERNED_RUN_INVALID"


def test_governed_run_emits_valid_json(tmp_path: Path) -> None:
    wo = tmp_path / "wo.md"
    wo.write_text(VALID_GR_WO, encoding="utf-8")
    proc = _run(["governed-run", "--work-order", str(wo), "--dry-run"], tmp_path)
    # JSON must parse cleanly.
    parsed = json.loads(proc.stdout)
    for field in (
        "work_order_hash", "parsed_stages", "protected_paths", "allowed_paths",
        "forbidden_paths", "required_commands", "validation_status",
        "audit_status", "final_status",
    ):
        assert field in parsed


def test_governed_run_appends_audit_log(tmp_path: Path) -> None:
    wo = tmp_path / "wo.md"
    wo.write_text(VALID_GR_WO, encoding="utf-8")
    audit = tmp_path / "audit" / "run.jsonl"
    proc = _run(
        ["governed-run", "--work-order", str(wo), "--audit", str(audit), "--dry-run"],
        tmp_path,
    )
    assert proc.returncode == 0, proc.stderr
    assert audit.is_file()
    lines = [ln for ln in audit.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) >= 2  # started + plan_valid
    manifest = json.loads(proc.stdout)
    assert manifest["audit_status"] is not None
    assert manifest["audit_status"]["status"] == "AUDIT_CHAIN_VALID"


def test_governed_run_missing_work_order_arg(tmp_path: Path) -> None:
    proc = _run(["governed-run", "--dry-run"], tmp_path)
    assert proc.returncode == 1
    assert "requires --work-order" in proc.stderr
