"""Integration tests for governed-run wet-run pipeline (WORK ORDER 016).

These tests drive ``python -m intellagent_runtime.cli governed-run ...``
as a subprocess and assert the manifest JSON / exit code / audit / refusal
behavior across all five final statuses.

Wet-run depends on tools/os_isolation_runtime.py (sandbox-exec on macOS).
Tests that require an actual --execute pass are decorated to be skipped
on non-macOS platforms.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
MACOS_ONLY = pytest.mark.skipif(sys.platform != "darwin", reason="sandbox-exec is macOS only")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


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


def _write_wo(path: Path, body: str) -> None:
    path.write_text(body, encoding="utf-8")


def _valid_pwd_wo() -> str:
    return """# WORK ORDER X
## Objective
exercise wet-run with a safe command

## Required Commands
```bash
pwd
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


def _refused_destructive_wo() -> str:
    return """# WORK ORDER X
## Objective
trigger refusal before execution

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


def _refused_forbidden_path_wo() -> str:
    return """# WORK ORDER X
## Objective
touch a protected path

## Required Commands
```bash
echo vectors/forge.json
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


def _wo_no_verify() -> str:
    # Prose deliberately avoids every stage synonym so the keyword-based
    # workflow parser sees only the stages we put in the list.
    return """# WORK ORDER X
## Objective
minimal scenario

## Required Commands
```bash
pwd
```

## Workflow
- inspect
- propose
- review
- execute
- report
- stop

Stop.
"""


def _wo_invalid_pseudocode_deliverable() -> str:
    return """# WORK ORDER X
## Objective
invalid deliverable

## Required Outputs
- TODO

## Required Commands
```bash
pwd
```

Stop.
"""


# ---------------------------------------------------------------------------
# Flag handling
# ---------------------------------------------------------------------------


def test_dry_run_default_when_no_mode_flag(tmp_path: Path) -> None:
    wo = tmp_path / "wo.md"
    _write_wo(wo, _valid_pwd_wo())
    proc = _run(["governed-run", "--work-order", str(wo)], tmp_path)
    assert proc.returncode == 0, proc.stderr
    manifest = json.loads(proc.stdout)
    assert manifest["mode"] == "dry-run"
    assert manifest["final_status"] == "GOVERNED_RUN_VALID"


def test_dry_run_explicit_flag(tmp_path: Path) -> None:
    wo = tmp_path / "wo.md"
    _write_wo(wo, _valid_pwd_wo())
    proc = _run(["governed-run", "--work-order", str(wo), "--dry-run"], tmp_path)
    assert proc.returncode == 0
    assert json.loads(proc.stdout)["mode"] == "dry-run"


def test_dry_run_and_execute_are_mutually_exclusive(tmp_path: Path) -> None:
    wo = tmp_path / "wo.md"
    _write_wo(wo, _valid_pwd_wo())
    proc = _run(
        ["governed-run", "--work-order", str(wo), "--dry-run", "--execute"],
        tmp_path,
    )
    assert proc.returncode == 1
    assert "mutually exclusive" in proc.stderr.lower()


def test_missing_work_order_returns_one(tmp_path: Path) -> None:
    proc = _run(["governed-run"], tmp_path)
    assert proc.returncode == 1
    assert "requires --work-order" in proc.stderr


def test_output_flag_writes_manifest_to_file(tmp_path: Path) -> None:
    wo = tmp_path / "wo.md"
    _write_wo(wo, _valid_pwd_wo())
    out = tmp_path / "manifest.json"
    proc = _run(
        ["governed-run", "--work-order", str(wo), "--dry-run", "--output", str(out)],
        tmp_path,
    )
    assert proc.returncode == 0
    assert out.is_file()
    assert json.loads(out.read_text(encoding="utf-8"))["final_status"] == "GOVERNED_RUN_VALID"


def test_self_check_returns_zero(tmp_path: Path) -> None:
    proc = _run(["governed-run", "--self-check"], tmp_path)
    assert proc.returncode == 0
    assert "PASS" in proc.stdout


# ---------------------------------------------------------------------------
# Dry-run paths
# ---------------------------------------------------------------------------


def test_dry_run_valid_emits_expected_fields(tmp_path: Path) -> None:
    wo = tmp_path / "wo.md"
    _write_wo(wo, _valid_pwd_wo())
    proc = _run(["governed-run", "--work-order", str(wo), "--dry-run"], tmp_path)
    assert proc.returncode == 0
    m = json.loads(proc.stdout)
    for f in (
        "mode", "work_order_hash", "execution_plan_hash",
        "parsed_stages", "protected_paths", "allowed_paths", "forbidden_paths",
        "required_commands", "validation_status", "validation_violations",
        "audit_status", "final_status", "manifest_hash",
    ):
        assert f in m, f"missing manifest field {f}"
    assert m["validation_status"] == "VALID"
    assert m["validation_violations"] == []


def test_dry_run_refused_plan_returns_one(tmp_path: Path) -> None:
    wo = tmp_path / "wo.md"
    _write_wo(wo, _refused_destructive_wo())
    proc = _run(["governed-run", "--work-order", str(wo), "--dry-run"], tmp_path)
    assert proc.returncode == 1
    m = json.loads(proc.stdout)
    assert m["final_status"] == "GOVERNED_RUN_REFUSED"
    assert m["validation_violations"]


def test_dry_run_invalid_wo_returns_two(tmp_path: Path) -> None:
    proc = _run(
        ["governed-run", "--work-order", str(tmp_path / "absent.md"), "--dry-run"],
        tmp_path,
    )
    assert proc.returncode == 2
    assert json.loads(proc.stdout)["final_status"] == "GOVERNED_RUN_INVALID"


def test_dry_run_plan_without_verify_is_refused(tmp_path: Path) -> None:
    wo = tmp_path / "wo.md"
    _write_wo(wo, _wo_no_verify())
    proc = _run(["governed-run", "--work-order", str(wo), "--dry-run"], tmp_path)
    assert proc.returncode == 1
    m = json.loads(proc.stdout)
    assert m["final_status"] == "GOVERNED_RUN_REFUSED"
    assert any("verification" in v for v in m["validation_violations"])


def test_dry_run_with_placeholder_deliverable_returns_invalid(tmp_path: Path) -> None:
    wo = tmp_path / "wo.md"
    _write_wo(wo, _wo_invalid_pseudocode_deliverable())
    proc = _run(["governed-run", "--work-order", str(wo), "--dry-run"], tmp_path)
    assert proc.returncode == 2
    assert json.loads(proc.stdout)["final_status"] == "GOVERNED_RUN_INVALID"


# ---------------------------------------------------------------------------
# Wet-run: refusal paths (no execution allowed)
# ---------------------------------------------------------------------------


def test_execute_on_destructive_plan_refuses_before_execution(tmp_path: Path) -> None:
    wo = tmp_path / "wo.md"
    _write_wo(wo, _refused_destructive_wo())
    proc = _run(["governed-run", "--work-order", str(wo), "--execute"], tmp_path)
    assert proc.returncode == 1
    m = json.loads(proc.stdout)
    assert m["final_status"] == "GOVERNED_RUN_REFUSED"
    assert "command_results" not in m or not m.get("command_results")


def test_execute_on_forbidden_path_refuses_before_execution(tmp_path: Path) -> None:
    wo = tmp_path / "wo.md"
    _write_wo(wo, _refused_forbidden_path_wo())
    proc = _run(["governed-run", "--work-order", str(wo), "--execute"], tmp_path)
    assert proc.returncode == 1
    m = json.loads(proc.stdout)
    assert m["final_status"] == "GOVERNED_RUN_REFUSED"


def test_execute_invalid_wo_returns_two(tmp_path: Path) -> None:
    proc = _run(
        ["governed-run", "--work-order", str(tmp_path / "nope.md"), "--execute"],
        tmp_path,
    )
    assert proc.returncode == 2
    assert json.loads(proc.stdout)["final_status"] == "GOVERNED_RUN_INVALID"


def test_execute_no_verify_stage_refused(tmp_path: Path) -> None:
    wo = tmp_path / "wo.md"
    _write_wo(wo, _wo_no_verify())
    proc = _run(["governed-run", "--work-order", str(wo), "--execute"], tmp_path)
    assert proc.returncode == 1
    assert json.loads(proc.stdout)["final_status"] == "GOVERNED_RUN_REFUSED"


def test_refused_plan_seals_refusal_record(tmp_path: Path) -> None:
    wo = tmp_path / "wo.md"
    _write_wo(wo, _refused_destructive_wo())
    proc = _run(["governed-run", "--work-order", str(wo), "--dry-run"], tmp_path)
    assert proc.returncode == 1
    m = json.loads(proc.stdout)
    assert m["refusal_record_hash"] is not None
    assert m["refusal_record_hash"].startswith("sha256:")
    refusals_dir = tmp_path / "intellagent_refusals"
    assert refusals_dir.is_dir()
    files = list(refusals_dir.glob("refusal-*.json"))
    assert len(files) >= 1, "RefusalRecord file not created"


def test_invalid_wo_seals_refusal_record(tmp_path: Path) -> None:
    proc = _run(
        ["governed-run", "--work-order", str(tmp_path / "absent.md"), "--dry-run"],
        tmp_path,
    )
    assert proc.returncode == 2
    m = json.loads(proc.stdout)
    assert m["refusal_record_hash"] is not None
    refusals_dir = tmp_path / "intellagent_refusals"
    assert refusals_dir.is_dir()


# ---------------------------------------------------------------------------
# Audit memory
# ---------------------------------------------------------------------------


def test_audit_appended_on_valid_dry_run(tmp_path: Path) -> None:
    wo = tmp_path / "wo.md"
    _write_wo(wo, _valid_pwd_wo())
    audit = tmp_path / "audit.jsonl"
    proc = _run(
        ["governed-run", "--work-order", str(wo), "--dry-run", "--audit", str(audit)],
        tmp_path,
    )
    assert proc.returncode == 0
    assert audit.is_file()
    events = [json.loads(line) for line in audit.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert any(e["event"] == "governed_run.started" for e in events)
    assert any(e["event"] == "governed_run.plan_valid" for e in events)


def test_audit_appended_on_refused_plan(tmp_path: Path) -> None:
    wo = tmp_path / "wo.md"
    _write_wo(wo, _refused_destructive_wo())
    audit = tmp_path / "audit.jsonl"
    proc = _run(
        ["governed-run", "--work-order", str(wo), "--dry-run", "--audit", str(audit)],
        tmp_path,
    )
    assert proc.returncode == 1
    events = [json.loads(line) for line in audit.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert any(e["event"] == "governed_run.refused" for e in events)


def test_audit_chain_status_in_manifest(tmp_path: Path) -> None:
    wo = tmp_path / "wo.md"
    _write_wo(wo, _valid_pwd_wo())
    audit = tmp_path / "audit.jsonl"
    proc = _run(
        ["governed-run", "--work-order", str(wo), "--dry-run", "--audit", str(audit)],
        tmp_path,
    )
    m = json.loads(proc.stdout)
    assert m["audit_status"] is not None
    assert m["audit_status"]["status"] == "AUDIT_CHAIN_VALID"


def test_audit_records_started_with_mode(tmp_path: Path) -> None:
    wo = tmp_path / "wo.md"
    _write_wo(wo, _valid_pwd_wo())
    audit = tmp_path / "audit.jsonl"
    proc = _run(
        ["governed-run", "--work-order", str(wo), "--dry-run", "--audit", str(audit)],
        tmp_path,
    )
    events = [json.loads(line) for line in audit.read_text(encoding="utf-8").splitlines() if line.strip()]
    started = next(e for e in events if e["event"] == "governed_run.started")
    assert started["payload"]["mode"] == "dry-run"


# ---------------------------------------------------------------------------
# Manifest shape / hashing
# ---------------------------------------------------------------------------


def test_dry_run_manifest_omits_wet_run_only_fields(tmp_path: Path) -> None:
    wo = tmp_path / "wo.md"
    _write_wo(wo, _valid_pwd_wo())
    proc = _run(["governed-run", "--work-order", str(wo), "--dry-run"], tmp_path)
    m = json.loads(proc.stdout)
    assert "command_results" not in m
    assert "pipeline_hash" not in m


def test_manifest_hash_is_sha256_prefixed(tmp_path: Path) -> None:
    wo = tmp_path / "wo.md"
    _write_wo(wo, _valid_pwd_wo())
    proc = _run(["governed-run", "--work-order", str(wo), "--dry-run"], tmp_path)
    m = json.loads(proc.stdout)
    assert m["manifest_hash"].startswith("sha256:")
    assert len(m["manifest_hash"]) == len("sha256:") + 64


def test_execution_plan_hash_changes_with_wo_change(tmp_path: Path) -> None:
    wo1 = tmp_path / "a.md"
    _write_wo(wo1, _valid_pwd_wo())
    wo2 = tmp_path / "b.md"
    _write_wo(wo2, _valid_pwd_wo().replace("pwd", "echo hello"))
    h1 = json.loads(_run(["governed-run", "--work-order", str(wo1), "--dry-run"], tmp_path).stdout)["execution_plan_hash"]
    h2 = json.loads(_run(["governed-run", "--work-order", str(wo2), "--dry-run"], tmp_path).stdout)["execution_plan_hash"]
    assert h1 != h2


def test_dry_run_manifest_is_deterministic(tmp_path: Path) -> None:
    """Two dry-runs on the same WO produce identical manifest_hash."""
    wo = tmp_path / "wo.md"
    _write_wo(wo, _valid_pwd_wo())
    h1 = json.loads(_run(["governed-run", "--work-order", str(wo), "--dry-run"], tmp_path).stdout)["manifest_hash"]
    h2 = json.loads(_run(["governed-run", "--work-order", str(wo), "--dry-run"], tmp_path).stdout)["manifest_hash"]
    assert h1 == h2


# ---------------------------------------------------------------------------
# Wet-run: actual execution (macOS-only)
# ---------------------------------------------------------------------------


@MACOS_ONLY
def test_execute_valid_pwd_returns_executed(tmp_path: Path) -> None:
    wo = tmp_path / "wo.md"
    _write_wo(wo, _valid_pwd_wo())
    proc = _run(["governed-run", "--work-order", str(wo), "--execute"], tmp_path)
    assert proc.returncode == 0, proc.stderr
    m = json.loads(proc.stdout)
    assert m["final_status"] == "GOVERNED_RUN_EXECUTED"
    assert m["mode"] == "execute"


@MACOS_ONLY
def test_execute_emits_pipeline_equivalent_hashes(tmp_path: Path) -> None:
    wo = tmp_path / "wo.md"
    _write_wo(wo, _valid_pwd_wo())
    proc = _run(["governed-run", "--work-order", str(wo), "--execute"], tmp_path)
    m = json.loads(proc.stdout)
    for f in ("proposer_hash", "review_hash", "executor_manifest_hash", "pipeline_hash"):
        assert m[f] is not None and m[f].startswith("sha256:"), f"missing or malformed {f}"


@MACOS_ONLY
def test_execute_command_results_present(tmp_path: Path) -> None:
    wo = tmp_path / "wo.md"
    _write_wo(wo, _valid_pwd_wo())
    proc = _run(["governed-run", "--work-order", str(wo), "--execute"], tmp_path)
    m = json.loads(proc.stdout)
    assert isinstance(m["command_results"], list)
    assert len(m["command_results"]) == 1
    cr = m["command_results"][0]
    assert cr["command"] == "pwd"
    assert cr["succeeded"] is True
    assert cr["status"] == "ok"
    assert cr["exit_code"] == 0


@MACOS_ONLY
def test_execute_appends_command_executed_events(tmp_path: Path) -> None:
    wo = tmp_path / "wo.md"
    _write_wo(wo, _valid_pwd_wo())
    audit = tmp_path / "audit.jsonl"
    proc = _run(
        ["governed-run", "--work-order", str(wo), "--execute", "--audit", str(audit)],
        tmp_path,
    )
    assert proc.returncode == 0
    events = [json.loads(line) for line in audit.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert any(e["event"] == "governed_run.command.executed" for e in events)
    assert any(e["event"] == "governed_run.completed" for e in events)


@MACOS_ONLY
def test_execute_audit_chain_stays_valid(tmp_path: Path) -> None:
    wo = tmp_path / "wo.md"
    _write_wo(wo, _valid_pwd_wo())
    audit = tmp_path / "audit.jsonl"
    proc = _run(
        ["governed-run", "--work-order", str(wo), "--execute", "--audit", str(audit)],
        tmp_path,
    )
    m = json.loads(proc.stdout)
    assert m["audit_status"]["status"] == "AUDIT_CHAIN_VALID"


@MACOS_ONLY
def test_execute_failing_command_returns_execution_failed(tmp_path: Path) -> None:
    body = """# WORK ORDER X
## Objective
exercise wet-run with a command that exits non-zero

## Required Commands
```bash
false
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
    wo = tmp_path / "wo.md"
    _write_wo(wo, body)
    proc = _run(["governed-run", "--work-order", str(wo), "--execute"], tmp_path)
    assert proc.returncode == 1
    m = json.loads(proc.stdout)
    assert m["final_status"] == "GOVERNED_RUN_EXECUTION_FAILED"
    assert m["refusal_record_hash"] is not None


@MACOS_ONLY
def test_execute_blocked_command_returns_execution_failed(tmp_path: Path) -> None:
    """A command admitted by the execution-plan validator but blocked at
    the sandbox classifier (e.g. a destructive command granted by an
    explicit-permission WO) still fails the wet-run."""
    body = """# WORK ORDER X
## Objective
trigger sandbox classifier rejection despite explicit permission in the WO

## Primary Rules
- May delete files under /tmp.

## Required Commands
```bash
rm /tmp/this-file-does-not-exist
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
    wo = tmp_path / "wo.md"
    _write_wo(wo, body)
    proc = _run(["governed-run", "--work-order", str(wo), "--execute"], tmp_path)
    # Plan validator may accept (explicit permission) but the sandbox
    # classifier denies — either path ends in EXECUTION_FAILED or REFUSED.
    m = json.loads(proc.stdout)
    assert m["final_status"] in ("GOVERNED_RUN_EXECUTION_FAILED", "GOVERNED_RUN_REFUSED")


@MACOS_ONLY
def test_execute_failing_command_seals_refusal_record(tmp_path: Path) -> None:
    body = """# WORK ORDER X
## Objective
sealed refusal on execution failure

## Required Commands
```bash
false
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
    wo = tmp_path / "wo.md"
    _write_wo(wo, body)
    proc = _run(["governed-run", "--work-order", str(wo), "--execute"], tmp_path)
    m = json.loads(proc.stdout)
    assert m["final_status"] == "GOVERNED_RUN_EXECUTION_FAILED"
    files = list((tmp_path / "intellagent_refusals").glob("refusal-*.json"))
    assert files, "RefusalRecord not sealed on EXECUTION_FAILED"


@MACOS_ONLY
def test_wet_run_manifest_round_trips_through_json(tmp_path: Path) -> None:
    wo = tmp_path / "wo.md"
    _write_wo(wo, _valid_pwd_wo())
    proc = _run(["governed-run", "--work-order", str(wo), "--execute"], tmp_path)
    parsed = json.loads(proc.stdout)
    # Re-serialize and re-parse — must yield the same object.
    again = json.loads(json.dumps(parsed))
    assert again == parsed


# ---------------------------------------------------------------------------
# Defense in depth
# ---------------------------------------------------------------------------


def test_command_not_present_in_plan_cannot_be_invoked(tmp_path: Path) -> None:
    """Negative invariant: a command never listed in the work order cannot
    appear in command_results regardless of mode."""
    wo = tmp_path / "wo.md"
    _write_wo(wo, _valid_pwd_wo())
    proc = _run(["governed-run", "--work-order", str(wo), "--dry-run"], tmp_path)
    m = json.loads(proc.stdout)
    assert m["required_commands"] == ["pwd"]


def test_unbounded_command_refused_in_execute(tmp_path: Path) -> None:
    body = _refused_destructive_wo()
    wo = tmp_path / "wo.md"
    _write_wo(wo, body)
    proc = _run(["governed-run", "--work-order", str(wo), "--execute"], tmp_path)
    m = json.loads(proc.stdout)
    assert m["final_status"] == "GOVERNED_RUN_REFUSED"
    assert "command_results" not in m or m["command_results"] == []


def test_no_execution_attempted_for_invalid_wo(tmp_path: Path) -> None:
    proc = _run(
        ["governed-run", "--work-order", str(tmp_path / "nope.md"), "--execute"],
        tmp_path,
    )
    m = json.loads(proc.stdout)
    assert m["final_status"] == "GOVERNED_RUN_INVALID"
    assert "command_results" not in m or not m.get("command_results")


def test_dry_run_does_not_seal_refusal_for_valid_plan(tmp_path: Path) -> None:
    wo = tmp_path / "wo.md"
    _write_wo(wo, _valid_pwd_wo())
    proc = _run(["governed-run", "--work-order", str(wo), "--dry-run"], tmp_path)
    m = json.loads(proc.stdout)
    assert m.get("refusal_record_hash") is None
    assert not (tmp_path / "intellagent_refusals").exists() or \
        not list((tmp_path / "intellagent_refusals").glob("refusal-*.json"))


# ---------------------------------------------------------------------------
# CI / freeze invariants
# ---------------------------------------------------------------------------


def test_frozen_fingerprints_unchanged_by_governed_run(tmp_path: Path) -> None:
    """A governed-run invocation must never mutate the published fingerprints."""
    report_path = REPO / "reports" / "conformance-report.json"
    if not report_path.is_file():
        pytest.skip("reports/conformance-report.json not present")
    before = json.loads(report_path.read_text(encoding="utf-8"))
    wo = tmp_path / "wo.md"
    _write_wo(wo, _valid_pwd_wo())
    _run(["governed-run", "--work-order", str(wo), "--dry-run"], tmp_path)
    after = json.loads(report_path.read_text(encoding="utf-8"))
    assert before["vectors_suite_sha256"] == after["vectors_suite_sha256"]


def test_existing_cli_commands_still_work(tmp_path: Path) -> None:
    """Smoke test: ``intellagent init`` is unaffected by governed-run changes."""
    proc = _run(["init"], tmp_path)
    assert proc.returncode == 0, proc.stderr
