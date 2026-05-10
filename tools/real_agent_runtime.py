#!/usr/bin/env python3
"""WiseOrder/Intellagent — REAL AGENT RUNTIME v0.1.

Local sandboxed worker execution for governed work orders.

Spec: REAL-AGENT-RUNTIME-v0.1.md (top-level).
Governs: workforce/real_agents/{sandboxes,runs}/, reports/real_agent_runtime/.

This runtime converts role-labeled "agents" into bounded local processes
that execute approved work orders inside isolated cloned sandboxes. v0.1
is dry-run-only: admission checks are real, sandbox copying is real,
command policy enforcement is real, but commands themselves are NOT
executed under this runtime — they are logged as would-execute. Real
execution is deferred to a future hardening cycle.

Standard library only. No network calls. No model calls. No autonomous
planning. No background daemons. Deny-by-default file and command policy.

CLI:
  real_agent_runtime.py check
      Validate runtime configuration: directories, identities, Makefile
      target presence (informational only). Writes the runtime report at
      reports/real_agent_runtime/real_agent_runtime_v0.1.{md,json}.
      Exit 0 on clean, 1 on configuration violation.

  real_agent_runtime.py self-check
      Run the ten admission fixtures and refresh the runtime report.
      Exit 0 if all ten fixtures match expected outcome, 1 otherwise.

  real_agent_runtime.py dry-run --work-order PATH --agent-id ID
      Perform admission, create a sandbox copy of the repo, run the
      command policy and filesystem policy against the work order's
      declared scope, write a per-run manifest under
      workforce/real_agents/runs/, and clean up the sandbox unless
      --preserve-sandbox is passed. Does not execute commands.
      Exit 0 on accepted dry-run, 1 on refusal or policy violation.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import fnmatch
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REAL_AGENTS_DIR = REPO_ROOT / "workforce" / "real_agents"
SANDBOXES_DIR = REAL_AGENTS_DIR / "sandboxes"
RUNS_DIR = REAL_AGENTS_DIR / "runs"
REPORTS_DIR = REPO_ROOT / "reports" / "real_agent_runtime"
RUNTIME_VERSION = "v0.1"

# ---------------------------------------------------------------------------
# Identity table
# ---------------------------------------------------------------------------

ALLOWED_COMMANDS: tuple[str, ...] = (
    "pwd",
    "ls",
    "find",
    "cat",
    "python3",
    ".venv/bin/python",
    "make no-pseudocode",
    "make workforce-check",
)

FORBIDDEN_COMMAND_PATTERNS: tuple[str, ...] = (
    "sudo",
    "curl",
    "wget",
    "ssh",
    "scp",
    "git push",
    "git reset --hard",
    "git clean",
    "rm -rf",
    "chmod",
    "chown",
    "open ",
    "http://",
    "https://",
)

# v0.2 execute-mode allowlist. Strictly broader than v0.1 ALLOWED_COMMANDS in
# the script-call dimension; strictly identical in the deny-first dimension
# (FORBIDDEN_COMMAND_PATTERNS is reused unchanged). Commands are matched by
# exact equality or starts-with-plus-space, the same matcher v0.1 uses.
EXECUTE_ALLOWED_COMMANDS: tuple[str, ...] = (
    "pwd",
    "ls",
    "find",
    "cat",
    ".venv/bin/python tools/check_no_pseudocode.py",
    ".venv/bin/python tools/check_workforce.py",
    ".venv/bin/python tools/real_agent_runtime.py check",
    "make no-pseudocode",
    "make workforce-check",
    "make real-agent-check",
)

# Bounded wall-clock cap per command. A command exceeding the cap is killed
# and recorded as `timed_out` in the manifest; the run still terminates.
EXECUTE_TIMEOUT_DEFAULT_S: float = 60.0
EXECUTE_TIMEOUT_HARD_CAP_S: float = 300.0
# Captured stdout/stderr is truncated at this byte length to keep manifests
# bounded. Truncation is recorded as `..._truncated: true` in the manifest.
EXECUTE_OUTPUT_BYTE_CAP: int = 64 * 1024

DEFAULT_DENIED_PATHS: tuple[str, ...] = (
    "runtime/",
    "intellagent_runtime/",
    "vectors/",
    "canonicalization/corpus/",
    "tools/",
)

IDENTITIES: dict[str, dict] = {
    "canon_guardian-01": {
        "role": "canon_guardian",
        "allowed_statuses": ("approved", "assigned"),
        "default_denied_paths": DEFAULT_DENIED_PATHS + ("Makefile", "SPEC.md"),
        "allowed_commands": ALLOWED_COMMANDS,
        "forbidden_commands": FORBIDDEN_COMMAND_PATTERNS,
    },
    "reviewer-01": {
        "role": "reviewer",
        "allowed_statuses": ("approved", "assigned"),
        "default_denied_paths": DEFAULT_DENIED_PATHS,
        "allowed_commands": ALLOWED_COMMANDS,
        "forbidden_commands": FORBIDDEN_COMMAND_PATTERNS,
    },
    "builder-01": {
        "role": "builder",
        "allowed_statuses": ("approved", "assigned"),
        "default_denied_paths": ("vectors/", "canonicalization/corpus/", "SPEC.md"),
        "allowed_commands": ALLOWED_COMMANDS,
        "forbidden_commands": FORBIDDEN_COMMAND_PATTERNS,
    },
    "release-01": {
        "role": "release",
        "allowed_statuses": ("approved", "assigned"),
        "default_denied_paths": ("vectors/", "canonicalization/corpus/", "intellagent_runtime/"),
        "allowed_commands": ALLOWED_COMMANDS,
        "forbidden_commands": FORBIDDEN_COMMAND_PATTERNS,
    },
}

# ---------------------------------------------------------------------------
# Flat-YAML parser (restricted subset; same shape as tools/check_workforce.py)
# ---------------------------------------------------------------------------


def _strip_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


def _coerce_scalar(value: str) -> object:
    stripped = _strip_quotes(value)
    if stripped == "true":
        return True
    if stripped == "false":
        return False
    return stripped


def parse_flat_yaml(path: Path) -> dict[str, object]:
    """Parse the restricted flat-YAML subset used by workforce templates.

    Same supported shape as tools/check_workforce.py: top-level scalars,
    top-level lists of scalars, and opaque list-of-mapping items. No nested
    mapping interpretation beyond status_history-style entries.
    """
    result: dict[str, object] = {}
    current_key: str | None = None
    current_list: list[str] | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if line.startswith("  - ") or line.startswith("- "):
            item = line.strip()[2:].strip()
            item = _strip_quotes(item)
            if current_list is None:
                current_list = []
                if current_key is not None:
                    result[current_key] = current_list
            current_list.append(item)
            continue
        if line.startswith(("    ", "\t")):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        current_key = key
        if value == "":
            current_list = []
            result[key] = current_list
        else:
            current_list = None
            result[key] = _coerce_scalar(value)
    return result


def _as_str_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if isinstance(item, str)]
    return []


# ---------------------------------------------------------------------------
# Admission rules
# ---------------------------------------------------------------------------


@dataclass
class AdmissionResult:
    accepted: bool
    reason: str
    work_order_id: str = ""
    agent_id: str = ""
    refusal_code: str = ""


def admit(
    wo_fields: dict[str, object],
    agent_id: str,
) -> AdmissionResult:
    """Return AdmissionResult for the given work-order content + agent identity.

    Refusal codes:
      - unknown_agent_identity
      - missing_required_field
      - status_not_admissible
      - assigned_to_mismatch
      - missing_allowed_files
      - missing_forbidden_files
    """
    identity = IDENTITIES.get(agent_id)
    if identity is None:
        return AdmissionResult(
            accepted=False,
            reason=f"unknown agent identity: {agent_id}",
            agent_id=agent_id,
            refusal_code="unknown_agent_identity",
        )

    wo_id = str(wo_fields.get("work_order_id", ""))
    if not wo_id:
        return AdmissionResult(
            accepted=False,
            reason="work order missing work_order_id",
            agent_id=agent_id,
            refusal_code="missing_required_field",
        )

    status = wo_fields.get("status")
    if not isinstance(status, str) or not status:
        return AdmissionResult(
            accepted=False,
            reason=f"work order {wo_id} missing or empty status",
            work_order_id=wo_id,
            agent_id=agent_id,
            refusal_code="missing_required_field",
        )
    if status not in identity["allowed_statuses"]:
        return AdmissionResult(
            accepted=False,
            reason=f"work order {wo_id} status '{status}' is not admissible for {agent_id} (allowed: {sorted(identity['allowed_statuses'])})",
            work_order_id=wo_id,
            agent_id=agent_id,
            refusal_code="status_not_admissible",
        )

    assigned_to = str(wo_fields.get("assigned_to", "")).strip()
    if not assigned_to:
        return AdmissionResult(
            accepted=False,
            reason=f"work order {wo_id} has empty assigned_to",
            work_order_id=wo_id,
            agent_id=agent_id,
            refusal_code="assigned_to_mismatch",
        )
    if assigned_to != agent_id:
        return AdmissionResult(
            accepted=False,
            reason=f"work order {wo_id} assigned_to '{assigned_to}' does not match agent '{agent_id}'",
            work_order_id=wo_id,
            agent_id=agent_id,
            refusal_code="assigned_to_mismatch",
        )

    if "allowed_files" not in wo_fields or not _as_str_list(wo_fields.get("allowed_files")):
        return AdmissionResult(
            accepted=False,
            reason=f"work order {wo_id} missing or empty allowed_files",
            work_order_id=wo_id,
            agent_id=agent_id,
            refusal_code="missing_allowed_files",
        )
    if "forbidden_files" not in wo_fields or not _as_str_list(wo_fields.get("forbidden_files")):
        return AdmissionResult(
            accepted=False,
            reason=f"work order {wo_id} missing or empty forbidden_files",
            work_order_id=wo_id,
            agent_id=agent_id,
            refusal_code="missing_forbidden_files",
        )

    return AdmissionResult(
        accepted=True,
        reason=f"admission accepted for {agent_id} on {wo_id} (status={status})",
        work_order_id=wo_id,
        agent_id=agent_id,
    )


# ---------------------------------------------------------------------------
# Command policy
# ---------------------------------------------------------------------------


@dataclass
class CommandVerdict:
    command: str
    allowed: bool
    reason: str


def classify_command(command: str, identity: dict) -> CommandVerdict:
    """Return CommandVerdict: forbidden patterns block first, then allowlist."""
    cmd = command.strip()
    for pattern in identity["forbidden_commands"]:
        if pattern in cmd:
            return CommandVerdict(command=cmd, allowed=False, reason=f"matches forbidden pattern '{pattern}'")
    for allowed in identity["allowed_commands"]:
        if cmd == allowed or cmd.startswith(allowed + " "):
            return CommandVerdict(command=cmd, allowed=True, reason=f"matches allowed command '{allowed}'")
    return CommandVerdict(command=cmd, allowed=False, reason="not in allowed command list")


# ---------------------------------------------------------------------------
# Filesystem policy
# ---------------------------------------------------------------------------


@dataclass
class PathVerdict:
    path: str
    operation: str
    allowed: bool
    reason: str


def classify_read(path: str, wo_fields: dict, identity: dict) -> PathVerdict:
    forbidden = _as_str_list(wo_fields.get("forbidden_files"))
    for pattern in forbidden:
        if fnmatch.fnmatch(path, pattern):
            return PathVerdict(path=path, operation="read", allowed=False, reason=f"forbidden_files pattern '{pattern}' matched")
    for prefix in identity["default_denied_paths"]:
        if path == prefix or path.startswith(prefix):
            return PathVerdict(path=path, operation="read", allowed=False, reason=f"identity default-denied path '{prefix}' matched")
    return PathVerdict(path=path, operation="read", allowed=True, reason="read not denied")


def classify_write(path: str, wo_fields: dict, identity: dict, sandbox_root: Path) -> PathVerdict:
    forbidden = _as_str_list(wo_fields.get("forbidden_files"))
    allowed = _as_str_list(wo_fields.get("allowed_files"))
    if not (path.startswith(str(sandbox_root) + os.sep) or path.startswith("reports/real_agent_runtime/")):
        return PathVerdict(path=path, operation="write", allowed=False, reason=f"write target outside sandbox or reports/real_agent_runtime/")
    for pattern in forbidden:
        if fnmatch.fnmatch(path, pattern):
            return PathVerdict(path=path, operation="write", allowed=False, reason=f"forbidden_files pattern '{pattern}' matched")
    for pattern in allowed:
        if fnmatch.fnmatch(path, pattern):
            return PathVerdict(path=path, operation="write", allowed=True, reason=f"allowed_files pattern '{pattern}' matched")
    return PathVerdict(path=path, operation="write", allowed=False, reason="write target not in allowed_files")


# ---------------------------------------------------------------------------
# Sandbox model
# ---------------------------------------------------------------------------


_FINGERPRINT_TARGETS: tuple[str, ...] = (
    "SPEC.md",
    "STATUS-REGISTRY.md",
    "ARTIFACTS.md",
    "CONFORMANCE.md",
    "Makefile",
    "tools/check_workforce.py",
    "tools/check_no_pseudocode.py",
)


def repo_fingerprint(root: Path) -> str:
    h = hashlib.sha256()
    for relpath in _FINGERPRINT_TARGETS:
        p = root / relpath
        if p.exists():
            data = p.read_bytes()
            h.update(relpath.encode("utf-8"))
            h.update(b"\x00")
            h.update(hashlib.sha256(data).digest())
    return "sha256:" + h.hexdigest()


def _make_ignore_for_sandbox(target_root: Path):
    skip = {".venv", "venv", ".git", "__pycache__", ".pytest_cache", ".mypy_cache", "node_modules"}
    target_str = str(target_root.resolve())
    sandboxes_str = str(SANDBOXES_DIR.resolve())
    runs_str = str(RUNS_DIR.resolve())
    reports_str = str(REPORTS_DIR.resolve())

    def _ignore(directory: str, names: list[str]) -> list[str]:
        ignored: list[str] = [n for n in names if n in skip]
        try:
            dir_resolved = str(Path(directory).resolve())
        except OSError:
            return ignored
        if dir_resolved in (sandboxes_str, runs_str, reports_str):
            ignored.extend(n for n in names if n not in ignored)
            return ignored
        if dir_resolved == target_str or dir_resolved.startswith(target_str + os.sep):
            ignored.extend(n for n in names if n not in ignored)
            return ignored
        return ignored

    return _ignore


def create_sandbox(run_id: str) -> Path:
    SANDBOXES_DIR.mkdir(parents=True, exist_ok=True)
    target = Path(tempfile.mkdtemp(prefix=f"real-agent-{run_id}-", dir=str(SANDBOXES_DIR)))
    target.rmdir()
    shutil.copytree(REPO_ROOT, target, ignore=_make_ignore_for_sandbox(target))
    return target


def cleanup_sandbox(sandbox_path: Path) -> None:
    if sandbox_path.exists():
        shutil.rmtree(sandbox_path, ignore_errors=True)


# ---------------------------------------------------------------------------
# Run manifest
# ---------------------------------------------------------------------------


@dataclass
class RunManifest:
    run_id: str
    work_order_id: str
    agent_id: str
    sandbox_path: str
    repo_fingerprint_before: str
    repo_fingerprint_after: str
    commands_attempted: list[str] = field(default_factory=list)
    commands_allowed: list[str] = field(default_factory=list)
    commands_blocked: list[dict] = field(default_factory=list)
    files_read: list[str] = field(default_factory=list)
    files_changed: list[str] = field(default_factory=list)
    gates_run: list[str] = field(default_factory=list)
    gates_passed: list[str] = field(default_factory=list)
    gates_failed: list[str] = field(default_factory=list)
    policy_violations: list[dict] = field(default_factory=list)
    exit_status: int = 0
    timestamp_start: str = ""
    timestamp_end: str = ""
    runtime_version: str = RUNTIME_VERSION
    dry_run: bool = True
    # v0.2 execute-mode extensions. Defaults preserve v0.1 dry-run manifest
    # shape: dry-run manifests still serialize these fields with empty/zero
    # values, never populating command_results or sandbox fingerprints.
    mode: str = "dry-run"
    replay_mode: bool = False
    command_results: list[dict] = field(default_factory=list)
    sandbox_fingerprint_before: str = ""
    sandbox_fingerprint_after: str = ""
    sandbox_files_changed: list[str] = field(default_factory=list)
    env_keys: list[str] = field(default_factory=list)
    # v0.3 OS-level sandbox extensions. Defaults preserve v0.1 / v0.2 manifest
    # shape: a v0.1 dry-run or v0.2 execute manifest still serializes these
    # fields with neutral values that v0.1 / v0.2 readers may ignore. v0.3
    # execute-sandboxed manifests populate them; non-v0.3 modes leave them as
    # the explicit "policy-only" / `false` defaults that match what was true
    # at v0.1 / v0.2: no OS-level isolation was active at those versions.
    sandbox_strategy: str = "policy-only"
    os_level_isolation_active: bool = False
    network_denied_by_strategy: bool = False
    resource_limits_applied: list[str] = field(default_factory=list)
    fallback_policy_only: bool = True
    containment_warnings: list[str] = field(default_factory=list)


def _now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_manifest(manifest: RunManifest, runs_dir: Path) -> Path:
    runs_dir.mkdir(parents=True, exist_ok=True)
    out = runs_dir / f"{manifest.run_id}.json"
    out.write_text(json.dumps(asdict(manifest), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out


# ---------------------------------------------------------------------------
# Dry-run
# ---------------------------------------------------------------------------


def dry_run(
    wo_path: Path,
    agent_id: str,
    preserve_sandbox: bool = False,
) -> RunManifest:
    if not wo_path.exists():
        raise FileNotFoundError(f"work order not found: {wo_path}")

    wo_fields = parse_flat_yaml(wo_path)
    admission = admit(wo_fields, agent_id)
    timestamp = _now_iso()
    run_id = f"run-{timestamp.replace(':', '').replace('-', '').replace('Z', 'Z')}-{agent_id.replace('-', '_')}"

    if not admission.accepted:
        manifest = RunManifest(
            run_id=run_id,
            work_order_id=admission.work_order_id,
            agent_id=agent_id,
            sandbox_path="",
            repo_fingerprint_before=repo_fingerprint(REPO_ROOT),
            repo_fingerprint_after=repo_fingerprint(REPO_ROOT),
            policy_violations=[{"code": admission.refusal_code, "reason": admission.reason}],
            exit_status=1,
            timestamp_start=timestamp,
            timestamp_end=_now_iso(),
        )
        write_manifest(manifest, RUNS_DIR)
        return manifest

    identity = IDENTITIES[agent_id]
    fp_before = repo_fingerprint(REPO_ROOT)
    sandbox_path = create_sandbox(run_id)
    try:
        manifest = RunManifest(
            run_id=run_id,
            work_order_id=admission.work_order_id,
            agent_id=agent_id,
            sandbox_path=str(sandbox_path),
            repo_fingerprint_before=fp_before,
            repo_fingerprint_after=fp_before,
            timestamp_start=timestamp,
        )

        required_gates = _as_str_list(wo_fields.get("required_gates"))
        for gate in required_gates:
            verdict = classify_command(gate, identity)
            manifest.commands_attempted.append(gate)
            manifest.gates_run.append(gate)
            if verdict.allowed:
                manifest.commands_allowed.append(gate)
                manifest.gates_passed.append(gate)
            else:
                manifest.commands_blocked.append({"command": gate, "reason": verdict.reason})
                manifest.gates_failed.append(gate)
                manifest.policy_violations.append({
                    "code": "command_blocked",
                    "command": gate,
                    "reason": verdict.reason,
                })

        forbidden = _as_str_list(wo_fields.get("forbidden_files"))
        for pattern in forbidden:
            verdict = classify_read(pattern, wo_fields, identity)
            if verdict.allowed:
                manifest.policy_violations.append({
                    "code": "policy_inconsistency",
                    "path": pattern,
                    "reason": "forbidden_files pattern unexpectedly admitted by classify_read",
                })

        manifest.repo_fingerprint_after = repo_fingerprint(REPO_ROOT)
        if manifest.repo_fingerprint_after != manifest.repo_fingerprint_before:
            manifest.policy_violations.append({
                "code": "repo_fingerprint_drift",
                "reason": "fingerprint changed during dry-run; dry-run must not mutate repo",
            })

        if manifest.policy_violations:
            manifest.exit_status = 1
        manifest.timestamp_end = _now_iso()
        write_manifest(manifest, RUNS_DIR)
        return manifest
    finally:
        if not preserve_sandbox:
            cleanup_sandbox(sandbox_path)


# ---------------------------------------------------------------------------
# Self-check fixtures
# ---------------------------------------------------------------------------


def _build_fixture(**overrides) -> dict[str, object]:
    base: dict[str, object] = {
        "work_order_id": "WO-FIX-001",
        "agent_role": "canon_guardian",
        "assigned_to": "canon_guardian-01",
        "status": "approved",
        "allowed_files": ["*.md", "workforce/**", "reports/**"],
        "forbidden_files": ["runtime/**", "intellagent_runtime/**", "vectors/**", "tools/**", "Makefile", "SPEC.md"],
        "required_gates": ["make no-pseudocode", "make workforce-check"],
    }
    base.update(overrides)
    return base


SELF_CHECK_CASES: tuple[dict, ...] = (
    {
        "name": "approved_assigned_wo_passes_admission",
        "fixture": _build_fixture(),
        "agent_id": "canon_guardian-01",
        "expected_accepted": True,
        "expected_refusal_code": "",
    },
    {
        "name": "drafted_wo_refused",
        "fixture": _build_fixture(status="drafted"),
        "agent_id": "canon_guardian-01",
        "expected_accepted": False,
        "expected_refusal_code": "status_not_admissible",
    },
    {
        "name": "unassigned_wo_refused",
        "fixture": _build_fixture(assigned_to=""),
        "agent_id": "canon_guardian-01",
        "expected_accepted": False,
        "expected_refusal_code": "assigned_to_mismatch",
    },
    {
        "name": "wrong_agent_identity_refused",
        "fixture": _build_fixture(assigned_to="release-01"),
        "agent_id": "canon_guardian-01",
        "expected_accepted": False,
        "expected_refusal_code": "assigned_to_mismatch",
    },
    {
        "name": "forbidden_command_refused",
        "fixture": _build_fixture(required_gates=["make no-pseudocode", "curl http://example.com"]),
        "agent_id": "canon_guardian-01",
        "expected_accepted": True,
        "expected_blocked_command": "curl http://example.com",
    },
    {
        "name": "forbidden_file_read_refused",
        "fixture": _build_fixture(),
        "agent_id": "canon_guardian-01",
        "expected_accepted": True,
        "expected_read_blocked_path": "SPEC.md",
    },
    {
        "name": "write_outside_sandbox_refused",
        "fixture": _build_fixture(),
        "agent_id": "canon_guardian-01",
        "expected_accepted": True,
        "expected_write_blocked_path": "/tmp/outside_sandbox.txt",
    },
    {
        "name": "closed_wo_refused",
        "fixture": _build_fixture(status="closed"),
        "agent_id": "canon_guardian-01",
        "expected_accepted": False,
        "expected_refusal_code": "status_not_admissible",
    },
    {
        "name": "missing_allowed_files_refused",
        "fixture": _build_fixture(allowed_files=[]),
        "agent_id": "canon_guardian-01",
        "expected_accepted": False,
        "expected_refusal_code": "missing_allowed_files",
    },
    {
        "name": "missing_forbidden_files_refused",
        "fixture": _build_fixture(forbidden_files=[]),
        "agent_id": "canon_guardian-01",
        "expected_accepted": False,
        "expected_refusal_code": "missing_forbidden_files",
    },
)


def _run_self_check_case(case: dict) -> dict:
    fixture = dict(case["fixture"])
    agent_id = case["agent_id"]
    admission = admit(fixture, agent_id)
    record = {
        "case": case["name"],
        "expected_accepted": case["expected_accepted"],
        "actual_accepted": admission.accepted,
        "actual_refusal_code": admission.refusal_code,
        "actual_reason": admission.reason,
        "pass": False,
    }
    expected_code = case.get("expected_refusal_code", "")
    if case["expected_accepted"] != admission.accepted:
        return record
    if not admission.accepted and expected_code and expected_code != admission.refusal_code:
        return record

    if admission.accepted:
        identity = IDENTITIES[agent_id]
        if "expected_blocked_command" in case:
            cmd = case["expected_blocked_command"]
            verdict = classify_command(cmd, identity)
            record["command_check"] = {
                "command": cmd,
                "expected_blocked": True,
                "actual_blocked": not verdict.allowed,
                "reason": verdict.reason,
            }
            if verdict.allowed:
                return record
        if "expected_read_blocked_path" in case:
            path = case["expected_read_blocked_path"]
            verdict = classify_read(path, fixture, identity)
            record["read_check"] = {
                "path": path,
                "expected_blocked": True,
                "actual_blocked": not verdict.allowed,
                "reason": verdict.reason,
            }
            if verdict.allowed:
                return record
        if "expected_write_blocked_path" in case:
            path = case["expected_write_blocked_path"]
            verdict = classify_write(path, fixture, identity, REPO_ROOT / "nonexistent_sandbox")
            record["write_check"] = {
                "path": path,
                "expected_blocked": True,
                "actual_blocked": not verdict.allowed,
                "reason": verdict.reason,
            }
            if verdict.allowed:
                return record

    record["pass"] = True
    return record


def run_self_check() -> dict:
    timestamp = _now_iso()
    results = [_run_self_check_case(case) for case in SELF_CHECK_CASES]
    all_passed = all(r["pass"] for r in results)
    return {
        "runtime_version": RUNTIME_VERSION,
        "timestamp": timestamp,
        "self_check_results": results,
        "all_passed": all_passed,
        "case_count": len(results),
        "passed_count": sum(1 for r in results if r["pass"]),
        "failed_count": sum(1 for r in results if not r["pass"]),
        "identities": sorted(IDENTITIES.keys()),
        "policy": {
            "allowed_commands": list(ALLOWED_COMMANDS),
            "forbidden_command_patterns": list(FORBIDDEN_COMMAND_PATTERNS),
            "default_denied_paths": list(DEFAULT_DENIED_PATHS),
        },
        "directories": {
            "real_agents_dir": str(REAL_AGENTS_DIR.relative_to(REPO_ROOT)),
            "sandboxes_dir": str(SANDBOXES_DIR.relative_to(REPO_ROOT)),
            "runs_dir": str(RUNS_DIR.relative_to(REPO_ROOT)),
            "reports_dir": str(REPORTS_DIR.relative_to(REPO_ROOT)),
        },
    }


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------


def _bool_mark(b: bool) -> str:
    return "PASS" if b else "FAIL"


def render_report_md(report: dict) -> str:
    lines: list[str] = []
    lines.append(f"# Real Agent Runtime {report['runtime_version']} — Self-Check Report")
    lines.append("")
    lines.append(f"**Timestamp (UTC):** `{report['timestamp']}`")
    lines.append(f"**Cases:** {report['case_count']} ({report['passed_count']} passed / {report['failed_count']} failed)")
    lines.append(f"**Overall:** {'PASS' if report['all_passed'] else 'FAIL'}")
    lines.append("")
    lines.append("## Identities")
    lines.append("")
    for ident in report["identities"]:
        lines.append(f"- `{ident}`")
    lines.append("")
    lines.append("## Policy")
    lines.append("")
    lines.append("**Allowed commands:**")
    for c in report["policy"]["allowed_commands"]:
        lines.append(f"- `{c}`")
    lines.append("")
    lines.append("**Forbidden command patterns:**")
    for c in report["policy"]["forbidden_command_patterns"]:
        lines.append(f"- `{c}`")
    lines.append("")
    lines.append("**Default-denied paths (before per-WO forbidden_files):**")
    for p in report["policy"]["default_denied_paths"]:
        lines.append(f"- `{p}`")
    lines.append("")
    lines.append("## Self-Check Results")
    lines.append("")
    lines.append("| # | Case | Expected | Actual | Refusal Code | Result |")
    lines.append("| -: | --- | --- | --- | --- | :-: |")
    for i, r in enumerate(report["self_check_results"], 1):
        expected = "accepted" if r["expected_accepted"] else "refused"
        actual = "accepted" if r["actual_accepted"] else "refused"
        code = r.get("actual_refusal_code") or "—"
        lines.append(f"| {i} | `{r['case']}` | {expected} | {actual} | `{code}` | **{_bool_mark(r['pass'])}** |")
    lines.append("")
    lines.append("## Directories")
    lines.append("")
    for k, v in report["directories"].items():
        lines.append(f"- `{k}`: `{v}`")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("**End of Real Agent Runtime self-check report.**")
    lines.append("")
    return "\n".join(lines)


def write_reports(report: dict) -> tuple[Path, Path]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    json_path = REPORTS_DIR / f"real_agent_runtime_{RUNTIME_VERSION}.json"
    md_path = REPORTS_DIR / f"real_agent_runtime_{RUNTIME_VERSION}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(render_report_md(report), encoding="utf-8")
    return md_path, json_path


# ---------------------------------------------------------------------------
# v0.2 execute mode — bounded local subprocess execution
# ---------------------------------------------------------------------------
#
# v0.2 adds a single new path beyond v0.1 dry-run: real subprocess invocation
# of allowlisted commands inside a sandbox copy, under a minimal environment,
# with a wall-clock timeout, and with stdout / stderr / exit_code / duration /
# cwd captured into the per-run manifest. v0.1 admission, command policy,
# filesystem policy, and refusal modes are reused unchanged. v0.2 still does
# NOT provide kernel-level isolation, autonomy, model calls, background
# daemons, or network access. See REAL-AGENT-RUNTIME-v0.2.md.

EXECUTE_RUNTIME_VERSION = "v0.2"


def classify_execute_command(command: str) -> CommandVerdict:
    """v0.2 execute-mode classifier.

    Identical deny-first / allowlist-second shape as v0.1 classify_command,
    but matches against EXECUTE_ALLOWED_COMMANDS instead of the v0.1 dry-run
    ALLOWED_COMMANDS. The forbidden-pattern set is the v0.1 set, unchanged.
    """
    cmd = command.strip()
    for pattern in FORBIDDEN_COMMAND_PATTERNS:
        if pattern in cmd:
            return CommandVerdict(command=cmd, allowed=False, reason=f"matches forbidden pattern '{pattern}'")
    for allowed in EXECUTE_ALLOWED_COMMANDS:
        if cmd == allowed or cmd.startswith(allowed + " "):
            return CommandVerdict(command=cmd, allowed=True, reason=f"matches execute-allowed command '{allowed}'")
    return CommandVerdict(command=cmd, allowed=False, reason="not in execute allowed-command list")


def _resolve_command_argv(command: str) -> list[str]:
    """Tokenize command and resolve `.venv/bin/python` to sys.executable.

    The sandbox does not contain `.venv/` (it is excluded by the sandbox
    ignore filter). When an allowlisted command begins with `.venv/bin/python`
    we substitute the running interpreter's absolute path (sys.executable)
    so the command is portable across machines whose source repo may or may
    not have a venv. Script paths remain relative; they resolve against the
    subprocess cwd, which is the sandbox root.
    """
    argv = shlex.split(command)
    if not argv:
        return argv
    if argv[0] == ".venv/bin/python":
        venv_python = REPO_ROOT / ".venv" / "bin" / "python"
        argv[0] = str(venv_python) if venv_python.exists() else sys.executable
    return argv


def _minimal_env(extra_pythonpath: str | None = None) -> dict[str, str]:
    """Return the minimal environment v0.2 execute mode passes to subprocess.

    Includes only PATH (inherited from the parent so `python3`, `make`, etc.
    resolve), LC_ALL=C, LANG=C, and PYTHONPATH only when explicitly required.
    No HOME, no USER, no PWD, no SHELL, no SHLVL, no SSH_*, no AWS_*, no API
    keys, no tokens. Anything not listed here is not passed through.
    """
    env: dict[str, str] = {
        "PATH": os.environ.get("PATH", ""),
        "LC_ALL": "C",
        "LANG": "C",
    }
    if extra_pythonpath:
        env["PYTHONPATH"] = extra_pythonpath
    return env


def _truncate_bytes(data: bytes, cap: int) -> tuple[str, bool]:
    if len(data) <= cap:
        return data.decode("utf-8", errors="replace"), False
    return data[:cap].decode("utf-8", errors="replace"), True


def execute_command(
    command: str,
    sandbox_root: Path,
    timeout: float = EXECUTE_TIMEOUT_DEFAULT_S,
    pythonpath: str | None = None,
) -> dict:
    """Invoke a single allowlisted command via subprocess.run inside the sandbox.

    Returns a dict suitable for inclusion in manifest.command_results. Caller
    is responsible for calling classify_execute_command first; this function
    does NOT re-check the allowlist (callers always do, so we don't double-
    check; if a caller misuses this we still capture the run result and the
    caller can decide whether to fail closed).

    The function never raises on subprocess failure or timeout: it captures
    the failure into the returned dict so the run-level orchestrator can
    decide policy.
    """
    timeout = min(max(timeout, 0.001), EXECUTE_TIMEOUT_HARD_CAP_S)
    argv = _resolve_command_argv(command)
    env = _minimal_env(pythonpath)
    started = time.monotonic()
    started_iso = _now_iso()
    result: dict = {
        "command": command,
        "argv": argv,
        "cwd": str(sandbox_root),
        "env_keys": sorted(env.keys()),
        "timeout_s": timeout,
        "timestamp_start": started_iso,
        "status": "ok",
        "exit_code": None,
        "stdout": "",
        "stdout_truncated": False,
        "stderr": "",
        "stderr_truncated": False,
        "duration_ms": 0,
        "timed_out": False,
        "error": None,
    }
    try:
        proc = subprocess.run(
            argv,
            cwd=str(sandbox_root),
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            shell=False,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        elapsed_ms = int((time.monotonic() - started) * 1000)
        out_data = exc.output if exc.output else b""
        err_data = exc.stderr if exc.stderr else b""
        out_text, out_trunc = _truncate_bytes(out_data, EXECUTE_OUTPUT_BYTE_CAP)
        err_text, err_trunc = _truncate_bytes(err_data, EXECUTE_OUTPUT_BYTE_CAP)
        result.update({
            "status": "timed_out",
            "exit_code": None,
            "stdout": out_text,
            "stdout_truncated": out_trunc,
            "stderr": err_text,
            "stderr_truncated": err_trunc,
            "duration_ms": elapsed_ms,
            "timed_out": True,
            "error": f"command exceeded {timeout}s wall-clock cap",
            "timestamp_end": _now_iso(),
        })
        return result
    except (FileNotFoundError, OSError) as exc:
        elapsed_ms = int((time.monotonic() - started) * 1000)
        result.update({
            "status": "error",
            "exit_code": None,
            "duration_ms": elapsed_ms,
            "error": f"{type(exc).__name__}: {exc}",
            "timestamp_end": _now_iso(),
        })
        return result

    elapsed_ms = int((time.monotonic() - started) * 1000)
    out_text, out_trunc = _truncate_bytes(proc.stdout or b"", EXECUTE_OUTPUT_BYTE_CAP)
    err_text, err_trunc = _truncate_bytes(proc.stderr or b"", EXECUTE_OUTPUT_BYTE_CAP)
    result.update({
        "status": "ok" if proc.returncode == 0 else "nonzero_exit",
        "exit_code": proc.returncode,
        "stdout": out_text,
        "stdout_truncated": out_trunc,
        "stderr": err_text,
        "stderr_truncated": err_trunc,
        "duration_ms": elapsed_ms,
        "timestamp_end": _now_iso(),
    })
    return result


# Files/directories ignored when fingerprinting a sandbox tree. Build artifacts
# and runtime-derived state (sandbox-internal reports, sandbox-internal runs)
# are excluded so a `make real-agent-check` invocation inside the sandbox does
# not appear as a sandbox-policy violation.
_TREE_FINGERPRINT_IGNORE_DIRS: frozenset[str] = frozenset({
    ".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".mypy_cache",
    "node_modules",
})
_TREE_FINGERPRINT_IGNORE_PREFIXES: tuple[str, ...] = (
    "workforce/real_agents/sandboxes/",
    "workforce/real_agents/runs/",
    "reports/real_agent_runtime/",
)


def _walk_tree_files(root: Path) -> list[tuple[str, Path]]:
    """Walk a tree returning (relpath, abspath) for every regular file.

    Skips ignored directories and ignored relative-path prefixes. Returns
    sorted by relpath for deterministic fingerprinting.
    """
    out: list[tuple[str, Path]] = []
    root_resolved = root.resolve()
    for dirpath, dirnames, filenames in os.walk(root_resolved):
        dirnames[:] = [d for d in dirnames if d not in _TREE_FINGERPRINT_IGNORE_DIRS]
        for name in filenames:
            full = Path(dirpath) / name
            try:
                rel = full.relative_to(root_resolved).as_posix()
            except ValueError:
                continue
            if any(rel.startswith(pfx) for pfx in _TREE_FINGERPRINT_IGNORE_PREFIXES):
                continue
            out.append((rel, full))
    out.sort(key=lambda item: item[0])
    return out


def tree_fingerprint(root: Path) -> tuple[str, dict[str, str]]:
    """Return (aggregate sha256, per-file sha256 map) for a tree under root.

    The aggregate hash is the sha256 of (relpath \\x00 file_sha256 \\x00)
    concatenated in sorted-relpath order. The per-file map allows the caller
    to compute changed/added/removed sets between two snapshots without
    re-walking the tree.
    """
    h = hashlib.sha256()
    per_file: dict[str, str] = {}
    for rel, full in _walk_tree_files(root):
        try:
            data = full.read_bytes()
        except (OSError, PermissionError):
            continue
        digest = hashlib.sha256(data).hexdigest()
        per_file[rel] = digest
        h.update(rel.encode("utf-8"))
        h.update(b"\x00")
        h.update(digest.encode("ascii"))
        h.update(b"\x00")
    return "sha256:" + h.hexdigest(), per_file


def tree_change_set(before: dict[str, str], after: dict[str, str]) -> dict[str, list[str]]:
    """Diff two tree fingerprint per-file maps.

    Returns {"added": [...], "removed": [...], "modified": [...]}, each
    sorted alphabetically.
    """
    before_keys = set(before.keys())
    after_keys = set(after.keys())
    added = sorted(after_keys - before_keys)
    removed = sorted(before_keys - after_keys)
    modified = sorted(k for k in (before_keys & after_keys) if before[k] != after[k])
    return {"added": added, "removed": removed, "modified": modified}


def execute_run(
    wo_path: Path,
    agent_id: str,
    commands: list[str] | None = None,
    timeout: float = EXECUTE_TIMEOUT_DEFAULT_S,
    preserve_sandbox: bool = False,
    replay_mode: bool = False,
) -> RunManifest:
    """v0.2 execute mode — admission + sandbox + real subprocess + manifest.

    Differences from dry_run:
      - mode = "execute"
      - if `replay_mode=True`, a closed work order is admitted (forensic replay);
        all other refusal codes still apply, and the manifest records the
        replay flag so the audit trail is explicit.
      - commands: defaults to the work order's `required_gates`; callers may
        substitute a different list to exercise a subset.
      - each admitted command is invoked via subprocess.run with cwd=sandbox,
        a minimal environment, and a wall-clock timeout. Forbidden commands
        are blocked BEFORE subprocess invocation.
      - sandbox is fingerprinted before and after the command run so the
        manifest records every changed/added/removed sandbox file.
      - source repo fingerprint must be byte-identical pre/post-execution.
    """
    if not wo_path.exists():
        raise FileNotFoundError(f"work order not found: {wo_path}")

    wo_fields = parse_flat_yaml(wo_path)
    timestamp = _now_iso()
    run_id = f"run-{timestamp.replace(':', '').replace('-', '').replace('Z', 'Z')}-{agent_id.replace('-', '_')}-execute"

    admission = admit(wo_fields, agent_id)
    # Replay-mode override: a closed status is admissible only when the caller
    # explicitly asked for replay mode AND the work order otherwise satisfies
    # admission (assigned_to matches, fields present). Replay does NOT bypass
    # any other refusal code.
    if (
        replay_mode
        and not admission.accepted
        and admission.refusal_code == "status_not_admissible"
        and isinstance(wo_fields.get("status"), str)
        and wo_fields.get("status") == "closed"
    ):
        rebuilt = dict(wo_fields)
        rebuilt["status"] = "approved"
        retry = admit(rebuilt, agent_id)
        if retry.accepted:
            admission = AdmissionResult(
                accepted=True,
                reason=f"replay-mode admission accepted for {agent_id} on {retry.work_order_id} (original status='closed' overridden under replay flag)",
                work_order_id=retry.work_order_id,
                agent_id=agent_id,
            )

    if not admission.accepted:
        manifest = RunManifest(
            run_id=run_id,
            work_order_id=admission.work_order_id,
            agent_id=agent_id,
            sandbox_path="",
            repo_fingerprint_before=repo_fingerprint(REPO_ROOT),
            repo_fingerprint_after=repo_fingerprint(REPO_ROOT),
            policy_violations=[{"code": admission.refusal_code, "reason": admission.reason}],
            exit_status=1,
            timestamp_start=timestamp,
            timestamp_end=_now_iso(),
            mode="execute",
            replay_mode=replay_mode,
            dry_run=False,
        )
        write_manifest(manifest, RUNS_DIR)
        return manifest

    identity = IDENTITIES[agent_id]
    if commands is None:
        commands = _as_str_list(wo_fields.get("required_gates"))
    fp_repo_before = repo_fingerprint(REPO_ROOT)
    sandbox_path = create_sandbox(run_id)
    try:
        sandbox_fp_before, sandbox_files_before = tree_fingerprint(sandbox_path)
        manifest = RunManifest(
            run_id=run_id,
            work_order_id=admission.work_order_id,
            agent_id=agent_id,
            sandbox_path=str(sandbox_path),
            repo_fingerprint_before=fp_repo_before,
            repo_fingerprint_after=fp_repo_before,
            timestamp_start=timestamp,
            mode="execute",
            replay_mode=replay_mode,
            dry_run=False,
            sandbox_fingerprint_before=sandbox_fp_before,
            env_keys=sorted(_minimal_env().keys()),
        )

        for cmd in commands:
            verdict = classify_execute_command(cmd)
            manifest.commands_attempted.append(cmd)
            if not verdict.allowed:
                manifest.commands_blocked.append({"command": cmd, "reason": verdict.reason})
                manifest.policy_violations.append({
                    "code": "command_blocked",
                    "command": cmd,
                    "reason": verdict.reason,
                })
                # Block BEFORE subprocess: still record a stub in command_results
                # so the manifest's command_results length matches commands_attempted.
                manifest.command_results.append({
                    "command": cmd,
                    "status": "blocked",
                    "exit_code": None,
                    "stdout": "",
                    "stderr": "",
                    "stdout_truncated": False,
                    "stderr_truncated": False,
                    "duration_ms": 0,
                    "cwd": str(sandbox_path),
                    "env_keys": sorted(_minimal_env().keys()),
                    "timed_out": False,
                    "error": verdict.reason,
                    "timeout_s": timeout,
                    "argv": [],
                    "timestamp_start": _now_iso(),
                    "timestamp_end": _now_iso(),
                })
                # If the blocked command was also a declared gate, record gate-fail.
                if cmd in _as_str_list(wo_fields.get("required_gates")):
                    manifest.gates_run.append(cmd)
                    manifest.gates_failed.append(cmd)
                continue
            manifest.commands_allowed.append(cmd)
            result = execute_command(cmd, sandbox_path, timeout=timeout)
            manifest.command_results.append(result)
            if cmd in _as_str_list(wo_fields.get("required_gates")):
                manifest.gates_run.append(cmd)
                if result.get("status") == "ok" and result.get("exit_code") == 0:
                    manifest.gates_passed.append(cmd)
                else:
                    manifest.gates_failed.append(cmd)
                    manifest.policy_violations.append({
                        "code": "gate_failed",
                        "command": cmd,
                        "reason": f"gate exited status={result.get('status')} exit_code={result.get('exit_code')}",
                    })
            elif result.get("timed_out"):
                manifest.policy_violations.append({
                    "code": "command_timed_out",
                    "command": cmd,
                    "reason": result.get("error") or "timed out",
                })
            elif result.get("status") == "error":
                manifest.policy_violations.append({
                    "code": "command_error",
                    "command": cmd,
                    "reason": result.get("error") or "subprocess error",
                })

        sandbox_fp_after, sandbox_files_after = tree_fingerprint(sandbox_path)
        manifest.sandbox_fingerprint_after = sandbox_fp_after
        diff = tree_change_set(sandbox_files_before, sandbox_files_after)
        manifest.sandbox_files_changed = sorted(diff["added"] + diff["modified"] + diff["removed"])

        manifest.repo_fingerprint_after = repo_fingerprint(REPO_ROOT)
        if manifest.repo_fingerprint_after != manifest.repo_fingerprint_before:
            manifest.policy_violations.append({
                "code": "repo_fingerprint_drift",
                "reason": "fingerprint changed during execute mode; source repo must not mutate",
            })

        if manifest.policy_violations:
            manifest.exit_status = 1
        manifest.timestamp_end = _now_iso()
        write_manifest(manifest, RUNS_DIR)
        return manifest
    finally:
        if not preserve_sandbox:
            cleanup_sandbox(sandbox_path)


# ---------------------------------------------------------------------------
# v0.2 execute self-check fixtures
# ---------------------------------------------------------------------------


def _execute_fixture_yaml(
    *,
    work_order_id: str = "WO-FIX-EXECUTE-001",
    status: str = "approved",
    assigned_to: str = "builder-01",
    required_gates: tuple[str, ...] = ("make no-pseudocode",),
    omit_allowed_files: bool = False,
    omit_forbidden_files: bool = False,
) -> str:
    base = [
        f'work_order_id: "{work_order_id}"',
        'agent_role: "builder"',
        f'assigned_to: "{assigned_to}"',
        'objective: "v0.2 execute-mode self-check fixture (synthetic; never enters workforce lifecycle)."',
    ]
    if not omit_allowed_files:
        base.append("")
        base.append("allowed_files:")
        base.append('  - "*.md"')
        base.append('  - "workforce/**"')
        base.append('  - "reports/**"')
    if not omit_forbidden_files:
        base.append("")
        base.append("forbidden_files:")
        base.append('  - "runtime/**"')
        base.append('  - "intellagent_runtime/**"')
        base.append('  - "vectors/**"')
        base.append('  - "canonicalization/**"')
        base.append('  - "SPEC.md"')
    base.append("")
    base.append("constraints:")
    base.append('  - "execute-mode self-check fixture"')
    base.append("")
    base.append("expected_outputs:")
    base.append('  - "(none; fixture)"')
    base.append("")
    base.append("required_gates:")
    for g in required_gates:
        base.append(f'  - "{g}"')
    base.append("")
    base.append("rollback_plan:")
    base.append('  - "delete fixture file"')
    base.append("")
    base.append("human_approval_required: true")
    base.append("")
    base.append(f'status: "{status}"')
    base.append("")
    base.append("status_history:")
    base.append('  - state: "drafted"')
    base.append('    actor: "execute-self-check"')
    base.append('    timestamp: "2026-05-08T00:00:00Z"')
    base.append('    note: "fixture"')
    if status in ("approved", "assigned", "closed"):
        base.append('  - state: "approved"')
        base.append('    actor: "execute-self-check"')
        base.append('    timestamp: "2026-05-08T00:00:01Z"')
        base.append('    note: "fixture"')
    if status in ("assigned", "closed"):
        base.append('  - state: "assigned"')
        base.append('    actor: "execute-self-check"')
        base.append('    timestamp: "2026-05-08T00:00:02Z"')
        base.append('    note: "fixture"')
    if status == "closed":
        for s in ("executed", "self-verified", "gate-checked", "reviewed", "human_approved", "closed"):
            base.append(f'  - state: "{s}"')
            base.append('    actor: "execute-self-check"')
            base.append('    timestamp: "2026-05-08T00:00:03Z"')
            base.append('    note: "fixture"')
    return "\n".join(base) + "\n"


def _write_temp_fixture(yaml_text: str) -> Path:
    f = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        prefix="real-agent-execute-fixture-",
        suffix=".yaml",
        dir=str(RUNS_DIR.parent),
        delete=False,
    )
    f.write(yaml_text)
    f.close()
    return Path(f.name)


def _execute_case_allowed_command_succeeds() -> dict:
    name = "execute_allowed_command_succeeds"
    fixture = _write_temp_fixture(_execute_fixture_yaml(required_gates=("pwd",)))
    repo_fp_before = repo_fingerprint(REPO_ROOT)
    try:
        manifest = execute_run(fixture, "builder-01", commands=["pwd"], timeout=30.0)
    finally:
        try:
            fixture.unlink()
        except OSError:
            pass
    repo_fp_after = repo_fingerprint(REPO_ROOT)
    cr = manifest.command_results[0] if manifest.command_results else {}
    ok = (
        manifest.exit_status == 0
        and len(manifest.command_results) == 1
        and cr.get("status") == "ok"
        and cr.get("exit_code") == 0
        and cr.get("cwd") == manifest.sandbox_path
        and "stdout" in cr
        and "stderr" in cr
        and "duration_ms" in cr
        and not cr.get("timed_out")
        and repo_fp_before == repo_fp_after
    )
    return {
        "case": name,
        "pass": ok,
        "exit_status": manifest.exit_status,
        "command_results_len": len(manifest.command_results),
        "first_status": cr.get("status"),
        "first_exit": cr.get("exit_code"),
        "repo_unchanged": repo_fp_before == repo_fp_after,
    }


def _execute_case_forbidden_blocked_before_subprocess() -> dict:
    name = "forbidden_command_blocked_before_subprocess"
    fixture = _write_temp_fixture(_execute_fixture_yaml(required_gates=("pwd",)))
    repo_fp_before = repo_fingerprint(REPO_ROOT)
    try:
        manifest = execute_run(
            fixture,
            "builder-01",
            commands=["curl https://example.com", "git push origin main", "rm -rf /"],
            timeout=10.0,
        )
    finally:
        try:
            fixture.unlink()
        except OSError:
            pass
    repo_fp_after = repo_fingerprint(REPO_ROOT)
    blocked = manifest.commands_blocked
    statuses = [r.get("status") for r in manifest.command_results]
    ok = (
        manifest.exit_status == 1
        and len(blocked) == 3
        and all(s == "blocked" for s in statuses)
        and all(r.get("argv") == [] for r in manifest.command_results)
        and all(r.get("exit_code") is None for r in manifest.command_results)
        and repo_fp_before == repo_fp_after
    )
    return {
        "case": name,
        "pass": ok,
        "blocked_count": len(blocked),
        "statuses": statuses,
        "repo_unchanged": repo_fp_before == repo_fp_after,
    }


def _execute_case_command_timeout_recorded() -> dict:
    name = "command_timeout_recorded"
    fixture = _write_temp_fixture(_execute_fixture_yaml(required_gates=("pwd",)))
    repo_fp_before = repo_fingerprint(REPO_ROOT)
    try:
        # `make no-pseudocode` cannot start + complete in 1ms; subprocess will be
        # killed by SIGTERM via subprocess.run timeout. Recorded as timed_out.
        manifest = execute_run(
            fixture,
            "builder-01",
            commands=["make no-pseudocode"],
            timeout=0.001,
        )
    finally:
        try:
            fixture.unlink()
        except OSError:
            pass
    repo_fp_after = repo_fingerprint(REPO_ROOT)
    cr = manifest.command_results[0] if manifest.command_results else {}
    ok = (
        cr.get("timed_out") is True
        and cr.get("status") == "timed_out"
        and cr.get("exit_code") is None
        and cr.get("duration_ms", 0) >= 0
        and repo_fp_before == repo_fp_after
    )
    return {
        "case": name,
        "pass": ok,
        "timed_out": cr.get("timed_out"),
        "status": cr.get("status"),
        "duration_ms": cr.get("duration_ms"),
        "repo_unchanged": repo_fp_before == repo_fp_after,
    }


def _execute_case_wrong_identity_refused() -> dict:
    name = "wrong_agent_identity_refused"
    fixture = _write_temp_fixture(_execute_fixture_yaml(assigned_to="release-01"))
    try:
        manifest = execute_run(fixture, "builder-01", commands=["pwd"], timeout=10.0)
    finally:
        try:
            fixture.unlink()
        except OSError:
            pass
    codes = [v.get("code") for v in manifest.policy_violations]
    ok = manifest.exit_status == 1 and "assigned_to_mismatch" in codes
    return {"case": name, "pass": ok, "codes": codes}


def _execute_case_drafted_refused() -> dict:
    name = "drafted_work_order_refused"
    fixture = _write_temp_fixture(_execute_fixture_yaml(status="drafted"))
    try:
        manifest = execute_run(fixture, "builder-01", commands=["pwd"], timeout=10.0)
    finally:
        try:
            fixture.unlink()
        except OSError:
            pass
    codes = [v.get("code") for v in manifest.policy_violations]
    ok = manifest.exit_status == 1 and "status_not_admissible" in codes
    return {"case": name, "pass": ok, "codes": codes}


def _execute_case_closed_refused_unless_replay() -> dict:
    name = "closed_refused_unless_replay_mode"
    fixture = _write_temp_fixture(_execute_fixture_yaml(status="closed"))
    try:
        # 1. Without replay flag — must refuse.
        m_refused = execute_run(fixture, "builder-01", commands=["pwd"], timeout=10.0)
        # 2. With replay flag — must admit.
        m_replay = execute_run(
            fixture, "builder-01", commands=["pwd"], timeout=10.0, replay_mode=True
        )
    finally:
        try:
            fixture.unlink()
        except OSError:
            pass
    refused_codes = [v.get("code") for v in m_refused.policy_violations]
    replay_cr = m_replay.command_results[0] if m_replay.command_results else {}
    ok = (
        m_refused.exit_status == 1
        and "status_not_admissible" in refused_codes
        and m_replay.exit_status == 0
        and m_replay.replay_mode is True
        and replay_cr.get("status") == "ok"
        and replay_cr.get("exit_code") == 0
    )
    return {
        "case": name,
        "pass": ok,
        "refused_codes": refused_codes,
        "replay_status": replay_cr.get("status"),
        "replay_mode_set": m_replay.replay_mode,
    }


def _execute_case_missing_allowed_files_refused() -> dict:
    name = "missing_allowed_files_refused"
    fixture = _write_temp_fixture(_execute_fixture_yaml(omit_allowed_files=True))
    try:
        manifest = execute_run(fixture, "builder-01", commands=["pwd"], timeout=10.0)
    finally:
        try:
            fixture.unlink()
        except OSError:
            pass
    codes = [v.get("code") for v in manifest.policy_violations]
    ok = manifest.exit_status == 1 and "missing_allowed_files" in codes
    return {"case": name, "pass": ok, "codes": codes}


def _execute_case_missing_forbidden_files_refused() -> dict:
    name = "missing_forbidden_files_refused"
    fixture = _write_temp_fixture(_execute_fixture_yaml(omit_forbidden_files=True))
    try:
        manifest = execute_run(fixture, "builder-01", commands=["pwd"], timeout=10.0)
    finally:
        try:
            fixture.unlink()
        except OSError:
            pass
    codes = [v.get("code") for v in manifest.policy_violations]
    ok = manifest.exit_status == 1 and "missing_forbidden_files" in codes
    return {"case": name, "pass": ok, "codes": codes}


def _execute_case_source_repo_unchanged() -> dict:
    name = "source_repo_unchanged_after_execute"
    fixture = _write_temp_fixture(_execute_fixture_yaml(required_gates=("pwd", "ls")))
    repo_fp_before = repo_fingerprint(REPO_ROOT)
    try:
        manifest = execute_run(
            fixture, "builder-01", commands=["pwd", "ls"], timeout=30.0
        )
    finally:
        try:
            fixture.unlink()
        except OSError:
            pass
    repo_fp_after = repo_fingerprint(REPO_ROOT)
    ok = (
        manifest.exit_status == 0
        and manifest.repo_fingerprint_before == manifest.repo_fingerprint_after
        and repo_fp_before == repo_fp_after
    )
    return {
        "case": name,
        "pass": ok,
        "repo_fp_before": manifest.repo_fingerprint_before,
        "repo_fp_after": manifest.repo_fingerprint_after,
    }


def _execute_case_manifest_records_full_command_shape() -> dict:
    name = "manifest_records_stdout_stderr_exit_duration_cwd"
    fixture = _write_temp_fixture(_execute_fixture_yaml(required_gates=("pwd",)))
    try:
        manifest = execute_run(fixture, "builder-01", commands=["pwd"], timeout=30.0)
    finally:
        try:
            fixture.unlink()
        except OSError:
            pass
    cr = manifest.command_results[0] if manifest.command_results else {}
    required_keys = {"stdout", "stderr", "exit_code", "duration_ms", "cwd"}
    ok = (
        manifest.exit_status == 0
        and required_keys.issubset(cr.keys())
        and cr.get("cwd") == manifest.sandbox_path
        and isinstance(cr.get("duration_ms"), int)
        and isinstance(cr.get("stdout"), str)
        and isinstance(cr.get("stderr"), str)
        and cr.get("exit_code") == 0
    )
    return {"case": name, "pass": ok, "keys_present": sorted(required_keys & cr.keys())}


def run_execute_self_check() -> dict:
    timestamp = _now_iso()
    cases = [
        _execute_case_allowed_command_succeeds,
        _execute_case_forbidden_blocked_before_subprocess,
        _execute_case_command_timeout_recorded,
        _execute_case_wrong_identity_refused,
        _execute_case_drafted_refused,
        _execute_case_closed_refused_unless_replay,
        _execute_case_missing_allowed_files_refused,
        _execute_case_missing_forbidden_files_refused,
        _execute_case_source_repo_unchanged,
        _execute_case_manifest_records_full_command_shape,
    ]
    results = [fn() for fn in cases]
    all_passed = all(r["pass"] for r in results)
    return {
        "runtime_version": EXECUTE_RUNTIME_VERSION,
        "timestamp": timestamp,
        "execute_self_check_results": results,
        "all_passed": all_passed,
        "case_count": len(results),
        "passed_count": sum(1 for r in results if r["pass"]),
        "failed_count": sum(1 for r in results if not r["pass"]),
        "execute_allowed_commands": list(EXECUTE_ALLOWED_COMMANDS),
        "forbidden_command_patterns": list(FORBIDDEN_COMMAND_PATTERNS),
        "execute_timeout_default_s": EXECUTE_TIMEOUT_DEFAULT_S,
        "execute_timeout_hard_cap_s": EXECUTE_TIMEOUT_HARD_CAP_S,
        "execute_output_byte_cap": EXECUTE_OUTPUT_BYTE_CAP,
    }


def render_execute_report_md(report: dict) -> str:
    lines: list[str] = []
    lines.append(f"# Real Agent Runtime {report['runtime_version']} — Execute-Mode Self-Check Report")
    lines.append("")
    lines.append(f"**Timestamp (UTC):** `{report['timestamp']}`")
    lines.append(f"**Cases:** {report['case_count']} ({report['passed_count']} passed / {report['failed_count']} failed)")
    lines.append(f"**Overall:** {'PASS' if report['all_passed'] else 'FAIL'}")
    lines.append("")
    lines.append("## Execute-Mode Allowlist")
    lines.append("")
    for c in report["execute_allowed_commands"]:
        lines.append(f"- `{c}`")
    lines.append("")
    lines.append("## Forbidden Command Patterns (deny-first; identical to v0.1)")
    lines.append("")
    for c in report["forbidden_command_patterns"]:
        lines.append(f"- `{c}`")
    lines.append("")
    lines.append("## Timeout Policy")
    lines.append("")
    lines.append(f"- default per-command timeout: `{report['execute_timeout_default_s']}s`")
    lines.append(f"- hard cap: `{report['execute_timeout_hard_cap_s']}s`")
    lines.append(f"- output byte cap (per stream): `{report['execute_output_byte_cap']}`")
    lines.append("")
    lines.append("## Self-Check Results")
    lines.append("")
    lines.append("| # | Case | Result |")
    lines.append("| -: | --- | :-: |")
    for i, r in enumerate(report["execute_self_check_results"], 1):
        lines.append(f"| {i} | `{r['case']}` | **{_bool_mark(r['pass'])}** |")
    lines.append("")
    lines.append("## Detail")
    lines.append("")
    for r in report["execute_self_check_results"]:
        lines.append(f"### `{r['case']}`")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(r, indent=2, sort_keys=True))
        lines.append("```")
        lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("**End of Real Agent Runtime execute-mode self-check report.**")
    lines.append("")
    return "\n".join(lines)


def write_execute_reports(report: dict) -> tuple[Path, Path]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    json_path = REPORTS_DIR / f"real_agent_runtime_{EXECUTE_RUNTIME_VERSION}.json"
    md_path = REPORTS_DIR / f"real_agent_runtime_{EXECUTE_RUNTIME_VERSION}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(render_execute_report_md(report), encoding="utf-8")
    return md_path, json_path


# ---------------------------------------------------------------------------
# v0.3 OS-level sandboxed execution
# ---------------------------------------------------------------------------
#
# v0.3 adds a single new path beyond v0.2 execute mode: bounded local
# subprocess execution wrapped in an OS-level sandbox tool when one is
# detected and successfully probed. macOS uses sandbox-exec; Linux probes
# bwrap, then firejail, then docker. When no tool is available the runtime
# falls back to v0.2 policy-only execution and marks the manifest with
# explicit fallback flags. v0.3 NEVER reports a fallback run as sandboxed
# execution. v0.1 dry-run, v0.2 execute, and v0.2 self-check are preserved
# verbatim. See REAL-AGENT-RUNTIME-v0.3.md.

SANDBOX_RUNTIME_VERSION = "v0.3"
SANDBOX_PROBE_TIMEOUT_S: float = 5.0


@dataclass
class SandboxStrategy:
    name: str
    available: bool
    probe_passed: bool
    network_denied: bool
    write_restricted_to_sandbox: bool
    resource_limits_applied: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    tool_path: str = ""
    platform: str = ""

    @property
    def os_level_isolation_active(self) -> bool:
        return self.available and self.probe_passed and self.name != "policy-only"

    @property
    def fallback_policy_only(self) -> bool:
        return not self.os_level_isolation_active


def _fallback_strategy(extra_warnings: list[str]) -> SandboxStrategy:
    return SandboxStrategy(
        name="policy-only",
        available=False,
        probe_passed=False,
        network_denied=False,
        write_restricted_to_sandbox=False,
        resource_limits_applied=[],
        warnings=extra_warnings + [
            "OS-level isolation is NOT active. v0.3 fell back to v0.2 policy-only enforcement; the manifest does not claim sandboxed execution.",
        ],
        tool_path="",
        platform=sys.platform,
    )


def _probe_sandbox_exec(tool_path: str) -> tuple[bool, str]:
    """Probe macOS sandbox-exec with a trivial profile + /bin/echo.

    Returns (probe_passed, error_or_empty).
    """
    try:
        proc = subprocess.run(
            [tool_path, "-p", "(version 1) (allow default)", "/bin/echo", "real-agent-probe-ok"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=SANDBOX_PROBE_TIMEOUT_S,
            shell=False,
            check=False,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as exc:
        return False, f"{type(exc).__name__}: {exc}"
    if proc.returncode == 0 and b"real-agent-probe-ok" in (proc.stdout or b""):
        return True, ""
    return False, f"probe exit={proc.returncode} stderr={(proc.stderr or b'').decode('utf-8', 'replace')[:200]}"


def _probe_bwrap(tool_path: str) -> tuple[bool, str]:
    try:
        proc = subprocess.run(
            [tool_path, "--ro-bind", "/", "/", "--unshare-net", "--unshare-pid", "/bin/echo", "real-agent-probe-ok"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=SANDBOX_PROBE_TIMEOUT_S,
            shell=False,
            check=False,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as exc:
        return False, f"{type(exc).__name__}: {exc}"
    if proc.returncode == 0 and b"real-agent-probe-ok" in (proc.stdout or b""):
        return True, ""
    return False, f"probe exit={proc.returncode} stderr={(proc.stderr or b'').decode('utf-8', 'replace')[:200]}"


def _probe_firejail(tool_path: str) -> tuple[bool, str]:
    try:
        proc = subprocess.run(
            [tool_path, "--quiet", "--noprofile", "--net=none", "/bin/echo", "real-agent-probe-ok"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=SANDBOX_PROBE_TIMEOUT_S,
            shell=False,
            check=False,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as exc:
        return False, f"{type(exc).__name__}: {exc}"
    if proc.returncode == 0 and b"real-agent-probe-ok" in (proc.stdout or b""):
        return True, ""
    return False, f"probe exit={proc.returncode} stderr={(proc.stderr or b'').decode('utf-8', 'replace')[:200]}"


def _probe_docker(tool_path: str) -> tuple[bool, str]:
    """Docker probe checks daemon availability via `docker version --format`."""
    try:
        proc = subprocess.run(
            [tool_path, "version", "--format", "{{.Server.Version}}"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=SANDBOX_PROBE_TIMEOUT_S,
            shell=False,
            check=False,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as exc:
        return False, f"{type(exc).__name__}: {exc}"
    if proc.returncode == 0 and (proc.stdout or b"").strip():
        return True, ""
    return False, f"probe exit={proc.returncode} stderr={(proc.stderr or b'').decode('utf-8', 'replace')[:200]}"


def detect_sandbox_strategy() -> SandboxStrategy:
    """Detect and probe the host OS sandbox strategy.

    macOS: prefers sandbox-exec.
    Linux: prefers bwrap, then firejail, then docker.
    Otherwise (or on probe failure): falls back to policy-only.

    The returned SandboxStrategy is populated with `available`, `probe_passed`,
    `network_denied`, `write_restricted_to_sandbox`, `resource_limits_applied`,
    `warnings`, `tool_path`, and `platform`. The boolean properties
    `os_level_isolation_active` and `fallback_policy_only` are derived.

    A non-fallback strategy is returned ONLY if the tool's binary exists AND
    a trivial probe (e.g., `sandbox-exec -p '(version 1) (allow default)'
    /bin/echo …`) succeeds. v0.3 will never silently claim isolation.
    """
    if sys.platform == "darwin":
        path = shutil.which("sandbox-exec")
        if path:
            ok, err = _probe_sandbox_exec(path)
            if ok:
                return SandboxStrategy(
                    name="macos-sandbox-exec",
                    available=True,
                    probe_passed=True,
                    network_denied=True,
                    write_restricted_to_sandbox=True,
                    resource_limits_applied=[
                        "os-network-denial",
                        "fs-write-restricted-to-sandbox",
                    ],
                    warnings=[
                        "macos-sandbox-exec is deprecated by Apple but functional; v0.3 uses it as a best-effort containment until a hardened replacement (e.g., Endpoint Security or App Sandbox) is integrated.",
                    ],
                    tool_path=path,
                    platform=sys.platform,
                )
            return _fallback_strategy([
                f"sandbox-exec at {path} failed probe: {err}",
            ])
        return _fallback_strategy([
            "sandbox-exec not found on this macOS host (PATH lookup failed).",
        ])

    if sys.platform.startswith("linux"):
        for name, probe in (("bwrap", _probe_bwrap), ("firejail", _probe_firejail), ("docker", _probe_docker)):
            path = shutil.which(name)
            if not path:
                continue
            ok, err = probe(path)
            if not ok:
                continue
            if name == "bwrap":
                return SandboxStrategy(
                    name="linux-bwrap",
                    available=True,
                    probe_passed=True,
                    network_denied=True,
                    write_restricted_to_sandbox=True,
                    resource_limits_applied=[
                        "os-network-denial",
                        "fs-write-restricted-to-sandbox",
                        "user-namespace",
                        "pid-namespace",
                        "ipc-namespace",
                        "uts-namespace",
                    ],
                    warnings=[],
                    tool_path=path,
                    platform=sys.platform,
                )
            if name == "firejail":
                return SandboxStrategy(
                    name="linux-firejail",
                    available=True,
                    probe_passed=True,
                    network_denied=True,
                    write_restricted_to_sandbox=True,
                    resource_limits_applied=[
                        "os-network-denial",
                        "fs-write-restricted-to-sandbox",
                    ],
                    warnings=[
                        "firejail relies on its setuid wrapper; verify the install matches the host's distro guidance.",
                    ],
                    tool_path=path,
                    platform=sys.platform,
                )
            if name == "linux-docker":
                # Note: docker is heavyweight and v0.3 records it as available
                # but does NOT yet wrap commands through `docker run` — that
                # integration is future hardening (see §15 of the v0.3 spec).
                return SandboxStrategy(
                    name="linux-docker",
                    available=True,
                    probe_passed=True,
                    network_denied=False,
                    write_restricted_to_sandbox=False,
                    resource_limits_applied=[],
                    warnings=[
                        "docker daemon is reachable but v0.3 does NOT yet wrap commands through `docker run`; until that wrapping is implemented this strategy is recorded as detected-but-not-active and v0.3 falls back to policy-only.",
                    ],
                    tool_path=path,
                    platform=sys.platform,
                )
        return _fallback_strategy([
            "No bwrap/firejail/docker detected on this Linux host or none probed successfully.",
        ])

    return _fallback_strategy([
        f"Unsupported platform '{sys.platform}'; v0.3 has no OS-level strategy and falls back to policy-only.",
    ])


def _build_macos_sandbox_profile(sandbox_real_path: str) -> str:
    """Return the macOS sandbox-exec profile that wraps a v0.3 invocation.

    Profile semantics:
      - (allow default) provides a working baseline (forks, execs, mach lookups).
      - (deny network*) denies all network operations at the OS level.
      - (deny file-write*) globally denies writes...
      - (allow file-write* (subpath "<SANDBOX_REAL>")) ...except inside the
        sandbox subpath. The path MUST be the realpath-resolved value because
        macOS resolves symlinks (notably /tmp -> /private/tmp) before checking.
      - additional file-write allows for tempfile + /dev as Python and make
        commonly require these surfaces.
    """
    return (
        "(version 1)\n"
        "(allow default)\n"
        "(deny network*)\n"
        "(deny file-write*)\n"
        f'(allow file-write* (subpath "{sandbox_real_path}"))\n'
        '(allow file-write* (regex "^/private/var/folders/"))\n'
        '(allow file-write* (regex "^/dev/"))\n'
    )


def wrap_argv_with_strategy(strategy: SandboxStrategy, argv: list[str], sandbox_root: Path) -> list[str]:
    """Return the wrapped argv that runs `argv` under the given strategy.

    For policy-only the argv is returned unchanged (caller is responsible for
    recording fallback markers in the manifest). For an active strategy the
    argv is prefixed with the strategy tool plus its containment arguments.
    """
    if strategy.name == "macos-sandbox-exec" and strategy.os_level_isolation_active:
        sandbox_real = os.path.realpath(str(sandbox_root))
        profile = _build_macos_sandbox_profile(sandbox_real)
        return [strategy.tool_path, "-p", profile, *argv]
    if strategy.name == "linux-bwrap" and strategy.os_level_isolation_active:
        sandbox_str = str(sandbox_root)
        return [
            strategy.tool_path,
            "--ro-bind", "/usr", "/usr",
            "--ro-bind", "/lib", "/lib",
            "--ro-bind", "/lib64", "/lib64",
            "--ro-bind", "/etc", "/etc",
            "--ro-bind", "/bin", "/bin",
            "--ro-bind", "/sbin", "/sbin",
            "--bind", sandbox_str, sandbox_str,
            "--proc", "/proc",
            "--dev", "/dev",
            "--tmpfs", "/tmp",
            "--unshare-net",
            "--unshare-pid",
            "--unshare-ipc",
            "--unshare-uts",
            "--die-with-parent",
            "--chdir", sandbox_str,
            *argv,
        ]
    if strategy.name == "linux-firejail" and strategy.os_level_isolation_active:
        sandbox_str = str(sandbox_root)
        return [
            strategy.tool_path,
            "--quiet",
            "--noprofile",
            "--net=none",
            f"--private={sandbox_str}",
            *argv,
        ]
    return list(argv)


def execute_sandboxed_command(
    command: str,
    sandbox_root: Path,
    strategy: SandboxStrategy,
    timeout: float = EXECUTE_TIMEOUT_DEFAULT_S,
    pythonpath: str | None = None,
) -> dict:
    """Invoke a single allowlisted command via the configured sandbox strategy.

    Mirrors execute_command() but wraps the resolved argv with the strategy's
    containment prefix BEFORE invoking subprocess.run. Records the strategy
    name and the wrapped argv in the returned dict. Caller is responsible for
    classify_execute_command(); this function does not re-classify.
    """
    timeout = min(max(timeout, 0.001), EXECUTE_TIMEOUT_HARD_CAP_S)
    base_argv = _resolve_command_argv(command)
    wrapped_argv = wrap_argv_with_strategy(strategy, base_argv, sandbox_root)
    env = _minimal_env(pythonpath)
    started = time.monotonic()
    started_iso = _now_iso()
    result: dict = {
        "command": command,
        "argv": base_argv,
        "wrapped_argv": wrapped_argv,
        "strategy": strategy.name,
        "os_level_isolation_active": strategy.os_level_isolation_active,
        "cwd": str(sandbox_root),
        "env_keys": sorted(env.keys()),
        "timeout_s": timeout,
        "timestamp_start": started_iso,
        "status": "ok",
        "exit_code": None,
        "stdout": "",
        "stdout_truncated": False,
        "stderr": "",
        "stderr_truncated": False,
        "duration_ms": 0,
        "timed_out": False,
        "error": None,
    }
    try:
        proc = subprocess.run(
            wrapped_argv,
            cwd=str(sandbox_root),
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            shell=False,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        elapsed_ms = int((time.monotonic() - started) * 1000)
        out_data = exc.output if exc.output else b""
        err_data = exc.stderr if exc.stderr else b""
        out_text, out_trunc = _truncate_bytes(out_data, EXECUTE_OUTPUT_BYTE_CAP)
        err_text, err_trunc = _truncate_bytes(err_data, EXECUTE_OUTPUT_BYTE_CAP)
        result.update({
            "status": "timed_out",
            "exit_code": None,
            "stdout": out_text,
            "stdout_truncated": out_trunc,
            "stderr": err_text,
            "stderr_truncated": err_trunc,
            "duration_ms": elapsed_ms,
            "timed_out": True,
            "error": f"command exceeded {timeout}s wall-clock cap",
            "timestamp_end": _now_iso(),
        })
        return result
    except (FileNotFoundError, OSError) as exc:
        elapsed_ms = int((time.monotonic() - started) * 1000)
        result.update({
            "status": "error",
            "exit_code": None,
            "duration_ms": elapsed_ms,
            "error": f"{type(exc).__name__}: {exc}",
            "timestamp_end": _now_iso(),
        })
        return result

    elapsed_ms = int((time.monotonic() - started) * 1000)
    out_text, out_trunc = _truncate_bytes(proc.stdout or b"", EXECUTE_OUTPUT_BYTE_CAP)
    err_text, err_trunc = _truncate_bytes(proc.stderr or b"", EXECUTE_OUTPUT_BYTE_CAP)
    result.update({
        "status": "ok" if proc.returncode == 0 else "nonzero_exit",
        "exit_code": proc.returncode,
        "stdout": out_text,
        "stdout_truncated": out_trunc,
        "stderr": err_text,
        "stderr_truncated": err_trunc,
        "duration_ms": elapsed_ms,
        "timestamp_end": _now_iso(),
    })
    return result


def execute_sandboxed_run(
    wo_path: Path,
    agent_id: str,
    commands: list[str] | None = None,
    timeout: float = EXECUTE_TIMEOUT_DEFAULT_S,
    preserve_sandbox: bool = False,
    replay_mode: bool = False,
    force_strategy: SandboxStrategy | None = None,
) -> RunManifest:
    """v0.3 execute-sandboxed mode — admission + sandbox + OS-level wrap + manifest.

    Differences from execute_run (v0.2):
      - mode = "execute-sandboxed"
      - the manifest's sandbox_strategy / os_level_isolation_active /
        network_denied_by_strategy / resource_limits_applied /
        fallback_policy_only / containment_warnings are populated.
      - allowed commands are wrapped with the detected (or forced) sandbox
        strategy before subprocess invocation.
      - When the strategy is policy-only, the manifest is explicit:
        os_level_isolation_active=false, fallback_policy_only=true, with
        a non-empty containment_warnings list. v0.3 NEVER claims sandboxed
        execution under fallback.
      - `force_strategy` is for testing / fixture support only; production
        callers should leave it None and let detect_sandbox_strategy() run.
    """
    if not wo_path.exists():
        raise FileNotFoundError(f"work order not found: {wo_path}")

    strategy = force_strategy if force_strategy is not None else detect_sandbox_strategy()

    wo_fields = parse_flat_yaml(wo_path)
    timestamp = _now_iso()
    run_id = f"run-{timestamp.replace(':', '').replace('-', '').replace('Z', 'Z')}-{agent_id.replace('-', '_')}-sandboxed"

    admission = admit(wo_fields, agent_id)
    if (
        replay_mode
        and not admission.accepted
        and admission.refusal_code == "status_not_admissible"
        and isinstance(wo_fields.get("status"), str)
        and wo_fields.get("status") == "closed"
    ):
        rebuilt = dict(wo_fields)
        rebuilt["status"] = "approved"
        retry = admit(rebuilt, agent_id)
        if retry.accepted:
            admission = AdmissionResult(
                accepted=True,
                reason=f"replay-mode admission accepted for {agent_id} on {retry.work_order_id} (original status='closed' overridden under replay flag)",
                work_order_id=retry.work_order_id,
                agent_id=agent_id,
            )

    if not admission.accepted:
        manifest = RunManifest(
            run_id=run_id,
            work_order_id=admission.work_order_id,
            agent_id=agent_id,
            sandbox_path="",
            repo_fingerprint_before=repo_fingerprint(REPO_ROOT),
            repo_fingerprint_after=repo_fingerprint(REPO_ROOT),
            policy_violations=[{"code": admission.refusal_code, "reason": admission.reason}],
            exit_status=1,
            timestamp_start=timestamp,
            timestamp_end=_now_iso(),
            mode="execute-sandboxed",
            replay_mode=replay_mode,
            dry_run=False,
            sandbox_strategy=strategy.name,
            os_level_isolation_active=strategy.os_level_isolation_active,
            network_denied_by_strategy=strategy.network_denied,
            resource_limits_applied=list(strategy.resource_limits_applied),
            fallback_policy_only=strategy.fallback_policy_only,
            containment_warnings=list(strategy.warnings),
        )
        write_manifest(manifest, RUNS_DIR)
        return manifest

    identity = IDENTITIES[agent_id]
    if commands is None:
        commands = _as_str_list(wo_fields.get("required_gates"))
    fp_repo_before = repo_fingerprint(REPO_ROOT)
    sandbox_path = create_sandbox(run_id)
    try:
        sandbox_fp_before, sandbox_files_before = tree_fingerprint(sandbox_path)
        manifest = RunManifest(
            run_id=run_id,
            work_order_id=admission.work_order_id,
            agent_id=agent_id,
            sandbox_path=str(sandbox_path),
            repo_fingerprint_before=fp_repo_before,
            repo_fingerprint_after=fp_repo_before,
            timestamp_start=timestamp,
            mode="execute-sandboxed",
            replay_mode=replay_mode,
            dry_run=False,
            sandbox_fingerprint_before=sandbox_fp_before,
            env_keys=sorted(_minimal_env().keys()),
            sandbox_strategy=strategy.name,
            os_level_isolation_active=strategy.os_level_isolation_active,
            network_denied_by_strategy=strategy.network_denied,
            resource_limits_applied=list(strategy.resource_limits_applied),
            fallback_policy_only=strategy.fallback_policy_only,
            containment_warnings=list(strategy.warnings),
        )

        for cmd in commands:
            verdict = classify_execute_command(cmd)
            manifest.commands_attempted.append(cmd)
            if not verdict.allowed:
                manifest.commands_blocked.append({"command": cmd, "reason": verdict.reason})
                manifest.policy_violations.append({
                    "code": "command_blocked",
                    "command": cmd,
                    "reason": verdict.reason,
                })
                manifest.command_results.append({
                    "command": cmd,
                    "status": "blocked",
                    "exit_code": None,
                    "stdout": "",
                    "stderr": "",
                    "stdout_truncated": False,
                    "stderr_truncated": False,
                    "duration_ms": 0,
                    "cwd": str(sandbox_path),
                    "env_keys": sorted(_minimal_env().keys()),
                    "timed_out": False,
                    "error": verdict.reason,
                    "timeout_s": timeout,
                    "argv": [],
                    "wrapped_argv": [],
                    "strategy": strategy.name,
                    "os_level_isolation_active": strategy.os_level_isolation_active,
                    "timestamp_start": _now_iso(),
                    "timestamp_end": _now_iso(),
                })
                if cmd in _as_str_list(wo_fields.get("required_gates")):
                    manifest.gates_run.append(cmd)
                    manifest.gates_failed.append(cmd)
                continue
            manifest.commands_allowed.append(cmd)
            result = execute_sandboxed_command(cmd, sandbox_path, strategy, timeout=timeout)
            manifest.command_results.append(result)
            if cmd in _as_str_list(wo_fields.get("required_gates")):
                manifest.gates_run.append(cmd)
                if result.get("status") == "ok" and result.get("exit_code") == 0:
                    manifest.gates_passed.append(cmd)
                else:
                    manifest.gates_failed.append(cmd)
                    manifest.policy_violations.append({
                        "code": "gate_failed",
                        "command": cmd,
                        "reason": f"gate exited status={result.get('status')} exit_code={result.get('exit_code')}",
                    })
            elif result.get("timed_out"):
                manifest.policy_violations.append({
                    "code": "command_timed_out",
                    "command": cmd,
                    "reason": result.get("error") or "timed out",
                })
            elif result.get("status") == "error":
                manifest.policy_violations.append({
                    "code": "command_error",
                    "command": cmd,
                    "reason": result.get("error") or "subprocess error",
                })

        sandbox_fp_after, sandbox_files_after = tree_fingerprint(sandbox_path)
        manifest.sandbox_fingerprint_after = sandbox_fp_after
        diff = tree_change_set(sandbox_files_before, sandbox_files_after)
        manifest.sandbox_files_changed = sorted(diff["added"] + diff["modified"] + diff["removed"])

        manifest.repo_fingerprint_after = repo_fingerprint(REPO_ROOT)
        if manifest.repo_fingerprint_after != manifest.repo_fingerprint_before:
            manifest.policy_violations.append({
                "code": "repo_fingerprint_drift",
                "reason": "fingerprint changed during execute-sandboxed mode; source repo must not mutate",
            })

        if manifest.policy_violations:
            manifest.exit_status = 1
        manifest.timestamp_end = _now_iso()
        write_manifest(manifest, RUNS_DIR)
        return manifest
    finally:
        if not preserve_sandbox:
            cleanup_sandbox(sandbox_path)


# ---------------------------------------------------------------------------
# v0.3 sandbox-mode self-check fixtures
# ---------------------------------------------------------------------------


def _sandbox_case_strategy_detected() -> dict:
    name = "sandbox_strategy_detected"
    s = detect_sandbox_strategy()
    valid_names = {"macos-sandbox-exec", "linux-bwrap", "linux-firejail", "linux-docker", "policy-only"}
    ok = (
        s.name in valid_names
        and isinstance(s.warnings, list)
        and isinstance(s.resource_limits_applied, list)
        and (s.os_level_isolation_active != s.fallback_policy_only)
    )
    return {
        "case": name,
        "pass": ok,
        "strategy": s.name,
        "os_level_isolation_active": s.os_level_isolation_active,
        "fallback_policy_only": s.fallback_policy_only,
        "platform": s.platform,
        "warnings_present": len(s.warnings) > 0,
    }


def _sandbox_case_fallback_mode_explicit() -> dict:
    """Force a policy-only strategy and verify the manifest marks it explicitly."""
    name = "fallback_mode_is_explicit"
    fixture = _write_temp_fixture(_execute_fixture_yaml(required_gates=("pwd",)))
    forced = _fallback_strategy(["forced fallback for self-check fixture"])
    try:
        manifest = execute_sandboxed_run(
            fixture, "builder-01", commands=["pwd"], timeout=15.0, force_strategy=forced
        )
    finally:
        try:
            fixture.unlink()
        except OSError:
            pass
    ok = (
        manifest.sandbox_strategy == "policy-only"
        and manifest.os_level_isolation_active is False
        and manifest.fallback_policy_only is True
        and manifest.network_denied_by_strategy is False
        and len(manifest.containment_warnings) >= 1
        and any("OS-level isolation is NOT active" in w for w in manifest.containment_warnings)
    )
    return {
        "case": name,
        "pass": ok,
        "strategy": manifest.sandbox_strategy,
        "os_level_isolation_active": manifest.os_level_isolation_active,
        "fallback_policy_only": manifest.fallback_policy_only,
        "warning_count": len(manifest.containment_warnings),
    }


def _sandbox_case_forbidden_blocked_before_sandbox_execution() -> dict:
    name = "forbidden_command_blocked_before_sandbox_execution"
    fixture = _write_temp_fixture(_execute_fixture_yaml(required_gates=("pwd",)))
    repo_fp_before = repo_fingerprint(REPO_ROOT)
    try:
        manifest = execute_sandboxed_run(
            fixture,
            "builder-01",
            commands=["curl https://example.com", "git push origin main", "rm -rf /"],
            timeout=10.0,
        )
    finally:
        try:
            fixture.unlink()
        except OSError:
            pass
    repo_fp_after = repo_fingerprint(REPO_ROOT)
    blocked = manifest.commands_blocked
    statuses = [r.get("status") for r in manifest.command_results]
    ok = (
        manifest.exit_status == 1
        and len(blocked) == 3
        and all(s == "blocked" for s in statuses)
        and all(r.get("argv") == [] for r in manifest.command_results)
        and all(r.get("wrapped_argv") == [] for r in manifest.command_results)
        and all(r.get("exit_code") is None for r in manifest.command_results)
        and repo_fp_before == repo_fp_after
    )
    return {
        "case": name,
        "pass": ok,
        "blocked_count": len(blocked),
        "statuses": statuses,
        "repo_unchanged": repo_fp_before == repo_fp_after,
    }


def _sandbox_case_allowed_executes_only_in_sandbox() -> dict:
    name = "allowed_command_executes_only_in_sandbox"
    fixture = _write_temp_fixture(_execute_fixture_yaml(required_gates=("pwd",)))
    try:
        manifest = execute_sandboxed_run(
            fixture, "builder-01", commands=["pwd"], timeout=30.0
        )
    finally:
        try:
            fixture.unlink()
        except OSError:
            pass
    cr = manifest.command_results[0] if manifest.command_results else {}
    cwd_in_manifest = cr.get("cwd")
    stdout = cr.get("stdout", "")
    # subprocess `pwd` prints the cwd. macOS resolves /tmp to /private/tmp, so
    # we accept both the literal sandbox path and its realpath equivalent.
    sandbox_path = manifest.sandbox_path
    sandbox_real = os.path.realpath(sandbox_path) if sandbox_path else ""
    pwd_inside = stdout.strip() in (sandbox_path, sandbox_real)
    ok = (
        cr.get("status") == "ok"
        and cr.get("exit_code") == 0
        and cwd_in_manifest == sandbox_path
        and pwd_inside
    )
    return {
        "case": name,
        "pass": ok,
        "cwd_in_manifest": cwd_in_manifest,
        "pwd_stdout": stdout.strip()[:200],
        "matches_sandbox": pwd_inside,
    }


def _sandbox_case_source_repo_fingerprint_unchanged() -> dict:
    name = "source_repo_fingerprint_unchanged_under_sandbox"
    fixture = _write_temp_fixture(_execute_fixture_yaml(required_gates=("pwd", "ls")))
    repo_fp_before = repo_fingerprint(REPO_ROOT)
    try:
        manifest = execute_sandboxed_run(
            fixture, "builder-01", commands=["pwd", "ls"], timeout=30.0
        )
    finally:
        try:
            fixture.unlink()
        except OSError:
            pass
    repo_fp_after = repo_fingerprint(REPO_ROOT)
    ok = (
        manifest.repo_fingerprint_before == manifest.repo_fingerprint_after
        and repo_fp_before == repo_fp_after
        and manifest.repo_fingerprint_before == repo_fp_before
    )
    return {
        "case": name,
        "pass": ok,
        "repo_fp_before": manifest.repo_fingerprint_before,
        "repo_fp_after": manifest.repo_fingerprint_after,
    }


def _sandbox_case_manifest_records_isolation_status() -> dict:
    name = "manifest_records_isolation_status"
    fixture = _write_temp_fixture(_execute_fixture_yaml(required_gates=("pwd",)))
    try:
        manifest = execute_sandboxed_run(
            fixture, "builder-01", commands=["pwd"], timeout=30.0
        )
    finally:
        try:
            fixture.unlink()
        except OSError:
            pass
    required_fields = {
        "sandbox_strategy", "os_level_isolation_active", "network_denied_by_strategy",
        "resource_limits_applied", "fallback_policy_only", "containment_warnings",
    }
    manifest_dict = asdict(manifest)
    fields_present = required_fields.issubset(manifest_dict.keys())
    consistent = (manifest.os_level_isolation_active != manifest.fallback_policy_only)
    ok = (
        fields_present
        and consistent
        and isinstance(manifest.resource_limits_applied, list)
        and isinstance(manifest.containment_warnings, list)
    )
    return {
        "case": name,
        "pass": ok,
        "fields_present": sorted(required_fields & manifest_dict.keys()),
        "strategy": manifest.sandbox_strategy,
        "isolation_active_xor_fallback": consistent,
    }


def _sandbox_case_network_command_refused_before_execution() -> dict:
    name = "network_command_refused_before_execution"
    fixture = _write_temp_fixture(_execute_fixture_yaml(required_gates=("pwd",)))
    try:
        manifest = execute_sandboxed_run(
            fixture,
            "builder-01",
            commands=["curl https://example.com/payload"],
            timeout=10.0,
        )
    finally:
        try:
            fixture.unlink()
        except OSError:
            pass
    cr = manifest.command_results[0] if manifest.command_results else {}
    codes = [v.get("code") for v in manifest.policy_violations]
    ok = (
        manifest.exit_status == 1
        and cr.get("status") == "blocked"
        and cr.get("argv") == []
        and cr.get("wrapped_argv") == []
        and cr.get("exit_code") is None
        and "command_blocked" in codes
        # Verify it was blocked at the policy layer, not by the sandbox tool's
        # network denial, by checking the reason string.
        and "matches forbidden pattern" in (cr.get("error") or "")
    )
    return {
        "case": name,
        "pass": ok,
        "first_status": cr.get("status"),
        "first_error": cr.get("error", "")[:120],
        "codes": codes,
    }


def _sandbox_case_write_outside_sandbox_refused() -> dict:
    """v0.3 verifies BOTH layers refuse out-of-sandbox writes.

    Policy layer: classify_write returns DENY for a path outside the sandbox
    or reports/real_agent_runtime/.

    OS layer (when active): the strategy's resource_limits_applied contains
    "fs-write-restricted-to-sandbox" — a structural assertion that the OS
    sandbox profile itself denies the write. This avoids needing a special
    sentinel command in the allowlist, while still proving the OS-layer
    promise is recorded honestly.
    """
    name = "write_outside_sandbox_refused"
    fixture_yaml = _execute_fixture_yaml(required_gates=("pwd",))
    fixture = _write_temp_fixture(fixture_yaml)
    try:
        wo_fields = parse_flat_yaml(fixture)
        identity = IDENTITIES["builder-01"]
        sandbox_root = REPO_ROOT / "workforce" / "real_agents" / "sandboxes" / "real-agent-test-write"
        # Policy layer
        outside = "/etc/passwd"
        v_outside = classify_write(outside, wo_fields, identity, sandbox_root)
        sandbox_md = str(sandbox_root) + "/REPORT.md"
        v_inside = classify_write(sandbox_md, wo_fields, identity, sandbox_root)
        # OS layer marker
        s = detect_sandbox_strategy()
        os_layer_marker_consistent = (
            (s.os_level_isolation_active and "fs-write-restricted-to-sandbox" in s.resource_limits_applied)
            or (not s.os_level_isolation_active)
        )
    finally:
        try:
            fixture.unlink()
        except OSError:
            pass
    ok = (
        not v_outside.allowed
        and v_inside.allowed
        and "outside sandbox" in v_outside.reason
        and os_layer_marker_consistent
    )
    return {
        "case": name,
        "pass": ok,
        "policy_outside_denied": not v_outside.allowed,
        "policy_inside_allowed": v_inside.allowed,
        "policy_outside_reason": v_outside.reason,
        "os_layer_marker_consistent": os_layer_marker_consistent,
        "strategy": s.name,
    }


def _sandbox_case_timeout_recorded() -> dict:
    name = "timeout_recorded_under_sandbox"
    fixture = _write_temp_fixture(_execute_fixture_yaml(required_gates=("pwd",)))
    repo_fp_before = repo_fingerprint(REPO_ROOT)
    try:
        manifest = execute_sandboxed_run(
            fixture,
            "builder-01",
            commands=["make no-pseudocode"],
            timeout=0.001,
        )
    finally:
        try:
            fixture.unlink()
        except OSError:
            pass
    repo_fp_after = repo_fingerprint(REPO_ROOT)
    cr = manifest.command_results[0] if manifest.command_results else {}
    ok = (
        cr.get("timed_out") is True
        and cr.get("status") == "timed_out"
        and cr.get("exit_code") is None
        and repo_fp_before == repo_fp_after
    )
    return {
        "case": name,
        "pass": ok,
        "timed_out": cr.get("timed_out"),
        "status": cr.get("status"),
        "duration_ms": cr.get("duration_ms"),
        "repo_unchanged": repo_fp_before == repo_fp_after,
    }


def _sandbox_case_missing_tool_does_not_silently_claim_isolation() -> dict:
    """Force a SandboxStrategy that LOOKS like an OS strategy by name but has
    available=False / probe_passed=False, and verify the runtime treats it as
    fallback-policy-only — never claims OS isolation when the tool isn't
    actually working.
    """
    name = "missing_sandbox_tool_does_not_silently_claim_os_isolation"
    fixture = _write_temp_fixture(_execute_fixture_yaml(required_gates=("pwd",)))
    fake = SandboxStrategy(
        name="macos-sandbox-exec",  # claims a real strategy name...
        available=False,            # ...but the tool is not available
        probe_passed=False,         # ...and the probe failed.
        network_denied=False,
        write_restricted_to_sandbox=False,
        resource_limits_applied=[],
        warnings=["fixture: simulated missing tool"],
        tool_path="",
        platform=sys.platform,
    )
    try:
        manifest = execute_sandboxed_run(
            fixture, "builder-01", commands=["pwd"], timeout=15.0, force_strategy=fake
        )
    finally:
        try:
            fixture.unlink()
        except OSError:
            pass
    # The runtime MUST refuse to claim OS isolation. The os_level_isolation_active
    # property is derived from (available AND probe_passed AND name != "policy-only");
    # a "macos-sandbox-exec" with available=False yields os_level_isolation_active=False
    # and fallback_policy_only=True, regardless of the strategy name string.
    ok = (
        manifest.os_level_isolation_active is False
        and manifest.fallback_policy_only is True
        and manifest.network_denied_by_strategy is False
        and len(manifest.containment_warnings) >= 1
    )
    return {
        "case": name,
        "pass": ok,
        "claimed_strategy": manifest.sandbox_strategy,
        "os_level_isolation_active": manifest.os_level_isolation_active,
        "fallback_policy_only": manifest.fallback_policy_only,
    }


def run_sandbox_self_check() -> dict:
    timestamp = _now_iso()
    cases = [
        _sandbox_case_strategy_detected,
        _sandbox_case_fallback_mode_explicit,
        _sandbox_case_forbidden_blocked_before_sandbox_execution,
        _sandbox_case_allowed_executes_only_in_sandbox,
        _sandbox_case_source_repo_fingerprint_unchanged,
        _sandbox_case_manifest_records_isolation_status,
        _sandbox_case_network_command_refused_before_execution,
        _sandbox_case_write_outside_sandbox_refused,
        _sandbox_case_timeout_recorded,
        _sandbox_case_missing_tool_does_not_silently_claim_isolation,
    ]
    results = [fn() for fn in cases]
    all_passed = all(r["pass"] for r in results)
    detected = detect_sandbox_strategy()
    return {
        "runtime_version": SANDBOX_RUNTIME_VERSION,
        "timestamp": timestamp,
        "sandbox_self_check_results": results,
        "all_passed": all_passed,
        "case_count": len(results),
        "passed_count": sum(1 for r in results if r["pass"]),
        "failed_count": sum(1 for r in results if not r["pass"]),
        "detected_strategy": {
            "name": detected.name,
            "platform": detected.platform,
            "available": detected.available,
            "probe_passed": detected.probe_passed,
            "network_denied": detected.network_denied,
            "write_restricted_to_sandbox": detected.write_restricted_to_sandbox,
            "resource_limits_applied": list(detected.resource_limits_applied),
            "warnings": list(detected.warnings),
            "os_level_isolation_active": detected.os_level_isolation_active,
            "fallback_policy_only": detected.fallback_policy_only,
            "tool_path": detected.tool_path,
        },
    }


def render_sandbox_report_md(report: dict) -> str:
    s = report["detected_strategy"]
    lines: list[str] = []
    lines.append(f"# Real Agent Runtime {report['runtime_version']} — OS-Level Sandbox Self-Check Report")
    lines.append("")
    lines.append(f"**Timestamp (UTC):** `{report['timestamp']}`")
    lines.append(f"**Cases:** {report['case_count']} ({report['passed_count']} passed / {report['failed_count']} failed)")
    lines.append(f"**Overall:** {'PASS' if report['all_passed'] else 'FAIL'}")
    lines.append("")
    lines.append("## Detected Sandbox Strategy")
    lines.append("")
    lines.append(f"- **strategy:** `{s['name']}`")
    lines.append(f"- **platform:** `{s['platform']}`")
    lines.append(f"- **tool path:** `{s['tool_path'] or '(none)'}`")
    lines.append(f"- **available:** `{s['available']}`")
    lines.append(f"- **probe passed:** `{s['probe_passed']}`")
    lines.append(f"- **OS-level isolation active:** `{s['os_level_isolation_active']}`")
    lines.append(f"- **fallback policy-only:** `{s['fallback_policy_only']}`")
    lines.append(f"- **network denied by strategy:** `{s['network_denied']}`")
    lines.append(f"- **write restricted to sandbox:** `{s['write_restricted_to_sandbox']}`")
    lines.append("")
    if s["resource_limits_applied"]:
        lines.append("**Resource limits applied:**")
        for r in s["resource_limits_applied"]:
            lines.append(f"- `{r}`")
        lines.append("")
    if s["warnings"]:
        lines.append("**Containment warnings:**")
        for w in s["warnings"]:
            lines.append(f"- {w}")
        lines.append("")
    lines.append("## Self-Check Results")
    lines.append("")
    lines.append("| # | Case | Result |")
    lines.append("| -: | --- | :-: |")
    for i, r in enumerate(report["sandbox_self_check_results"], 1):
        lines.append(f"| {i} | `{r['case']}` | **{_bool_mark(r['pass'])}** |")
    lines.append("")
    lines.append("## Detail")
    lines.append("")
    for r in report["sandbox_self_check_results"]:
        lines.append(f"### `{r['case']}`")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(r, indent=2, sort_keys=True))
        lines.append("```")
        lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("**End of Real Agent Runtime OS-level sandbox self-check report.**")
    lines.append("")
    return "\n".join(lines)


def write_sandbox_reports(report: dict) -> tuple[Path, Path]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    json_path = REPORTS_DIR / f"real_agent_runtime_{SANDBOX_RUNTIME_VERSION}.json"
    md_path = REPORTS_DIR / f"real_agent_runtime_{SANDBOX_RUNTIME_VERSION}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(render_sandbox_report_md(report), encoding="utf-8")
    return md_path, json_path


# ---------------------------------------------------------------------------
# Configuration check
# ---------------------------------------------------------------------------


def configuration_violations() -> list[str]:
    violations: list[str] = []
    if not REAL_AGENTS_DIR.is_dir():
        violations.append(f"missing directory: {REAL_AGENTS_DIR.relative_to(REPO_ROOT)}")
    if not SANDBOXES_DIR.is_dir():
        violations.append(f"missing directory: {SANDBOXES_DIR.relative_to(REPO_ROOT)}")
    if not RUNS_DIR.is_dir():
        violations.append(f"missing directory: {RUNS_DIR.relative_to(REPO_ROOT)}")
    if not REPORTS_DIR.is_dir():
        violations.append(f"missing directory: {REPORTS_DIR.relative_to(REPO_ROOT)}")
    spec_path = REPO_ROOT / "docs" / "runtime" / "REAL-AGENT-RUNTIME-v0.1.md"
    if not spec_path.is_file():
        violations.append("missing spec: docs/runtime/REAL-AGENT-RUNTIME-v0.1.md")
    if not (REPO_ROOT / "Makefile").is_file():
        violations.append("missing Makefile")
    else:
        mk = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
        if "real-agent-check" not in mk:
            violations.append("Makefile missing target: real-agent-check")
        if "real-agent-dry-run" not in mk:
            violations.append("Makefile missing target: real-agent-dry-run")
    if "canon_guardian-01" not in IDENTITIES:
        violations.append("missing identity: canon_guardian-01")
    if "reviewer-01" not in IDENTITIES:
        violations.append("missing identity: reviewer-01")
    if "builder-01" not in IDENTITIES:
        violations.append("missing identity: builder-01")
    if "release-01" not in IDENTITIES:
        violations.append("missing identity: release-01")
    return violations


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def cmd_check(args: argparse.Namespace) -> int:
    violations = configuration_violations()
    report = run_self_check()
    md_path, json_path = write_reports(report)
    if violations:
        print("real-agent-runtime: CONFIGURATION VIOLATIONS")
        for v in violations:
            print(f"  - {v}")
        return 1
    if not report["all_passed"]:
        print(f"real-agent-runtime: SELF-CHECK FAILED ({report['failed_count']} of {report['case_count']} cases)")
        for r in report["self_check_results"]:
            if not r["pass"]:
                print(f"  - FAIL {r['case']}: expected accepted={r['expected_accepted']} got accepted={r['actual_accepted']} (code={r['actual_refusal_code']})")
        return 1
    print(f"real-agent-runtime: OK ({report['passed_count']}/{report['case_count']} fixtures pass; reports at {md_path.relative_to(REPO_ROOT)} and {json_path.relative_to(REPO_ROOT)}).")
    return 0


def cmd_self_check(args: argparse.Namespace) -> int:
    return cmd_check(args)


def cmd_dry_run(args: argparse.Namespace) -> int:
    wo_path = Path(args.work_order)
    if not wo_path.is_absolute():
        wo_path = (REPO_ROOT / wo_path).resolve()
    if args.agent_id not in IDENTITIES:
        print(f"real-agent-runtime: unknown agent identity '{args.agent_id}'. Known: {sorted(IDENTITIES.keys())}")
        return 1
    try:
        manifest = dry_run(wo_path, args.agent_id, preserve_sandbox=args.preserve_sandbox)
    except FileNotFoundError as exc:
        print(f"real-agent-runtime: {exc}")
        return 1
    relpath = (RUNS_DIR / f"{manifest.run_id}.json").relative_to(REPO_ROOT)
    if manifest.exit_status == 0:
        print(f"real-agent-runtime: dry-run ACCEPTED for {manifest.agent_id} on {manifest.work_order_id}; manifest at {relpath}")
        return 0
    print(f"real-agent-runtime: dry-run REFUSED for {manifest.agent_id} on {manifest.work_order_id or '<unknown>'}; manifest at {relpath}")
    for v in manifest.policy_violations:
        print(f"  - {v.get('code', '?')}: {v.get('reason', '')}")
    return 1


_BUILTIN_FIXTURE_YAML = """# Built-in dry-run fixture for real-agent-runtime self-test.
# Synthetic approved+assigned work order; never moves through workforce lifecycle.
# This file is created and deleted within a single built-in-dry-run invocation.

work_order_id: "WO-FIXTURE-DRY-RUN-001"
agent_role: "canon_guardian"
assigned_to: "canon_guardian-01"
objective: "Built-in dry-run fixture exercising the real-agent-runtime end-to-end admission + sandbox + policy + manifest pipeline."

allowed_files:
  - "*.md"
  - "workforce/**"
  - "reports/**"

forbidden_files:
  - "runtime/**"
  - "intellagent_runtime/**"
  - "vectors/**"
  - "canonicalization/**"
  - "tools/**"
  - "Makefile"
  - "SPEC.md"

constraints:
  - "built-in fixture; not a real workforce work order"

expected_outputs:
  - "(none; fixture-only)"

required_gates:
  - "make no-pseudocode"
  - "make workforce-check"

rollback_plan:
  - "delete fixture file"

human_approval_required: true

status: "approved"

status_history:
  - state: "drafted"
    actor: "real-agent-runtime-fixture"
    timestamp: "2026-05-08T00:00:00Z"
    note: "Built-in fixture generated for real-agent-runtime built-in-dry-run gate."
  - state: "approved"
    actor: "real-agent-runtime-fixture"
    timestamp: "2026-05-08T00:00:01Z"
    note: "Approved within fixture for built-in dry-run."
  - state: "assigned"
    actor: "real-agent-runtime-fixture"
    timestamp: "2026-05-08T00:00:02Z"
    note: "Assigned to canon_guardian-01 within fixture."
"""


def cmd_built_in_dry_run(args: argparse.Namespace) -> int:
    """Run a synthetic approved+assigned dry-run fixture end-to-end.

    Exercises the full pipeline: admission accept -> sandbox create -> command
    policy classification -> manifest write -> sandbox cleanup. Used as the
    no-arg invocation for `make real-agent-dry-run`.
    """
    fixture = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        prefix="real-agent-fixture-",
        suffix=".yaml",
        dir=str(RUNS_DIR.parent),
        delete=False,
    )
    fixture.write(_BUILTIN_FIXTURE_YAML)
    fixture.close()
    fixture_path = Path(fixture.name)
    try:
        manifest = dry_run(fixture_path, "canon_guardian-01", preserve_sandbox=False)
    finally:
        try:
            fixture_path.unlink()
        except OSError:
            pass
    relpath = (RUNS_DIR / f"{manifest.run_id}.json").relative_to(REPO_ROOT)
    if manifest.exit_status == 0:
        print(f"real-agent-runtime: built-in dry-run ACCEPTED ({len(manifest.commands_allowed)}/{len(manifest.commands_attempted)} commands allowed; {len(manifest.policy_violations)} violations); manifest at {relpath}")
        return 0
    print(f"real-agent-runtime: built-in dry-run FAILED; manifest at {relpath}")
    for v in manifest.policy_violations:
        print(f"  - {v.get('code', '?')}: {v.get('reason', '')}")
    return 1


def cmd_execute(args: argparse.Namespace) -> int:
    """v0.2 execute mode — run admitted commands inside a sandbox copy."""
    wo_path = Path(args.work_order)
    if not wo_path.is_absolute():
        wo_path = (REPO_ROOT / wo_path).resolve()
    if args.agent_id not in IDENTITIES:
        print(f"real-agent-runtime: unknown agent identity '{args.agent_id}'. Known: {sorted(IDENTITIES.keys())}")
        return 1
    commands = args.command if args.command else None
    try:
        manifest = execute_run(
            wo_path,
            args.agent_id,
            commands=commands,
            timeout=args.timeout,
            preserve_sandbox=args.preserve_sandbox,
            replay_mode=args.replay,
        )
    except FileNotFoundError as exc:
        print(f"real-agent-runtime: {exc}")
        return 1
    relpath = (RUNS_DIR / f"{manifest.run_id}.json").relative_to(REPO_ROOT)
    if manifest.exit_status == 0:
        print(
            f"real-agent-runtime: execute ACCEPTED for {manifest.agent_id} on "
            f"{manifest.work_order_id} ({len(manifest.commands_allowed)}/"
            f"{len(manifest.commands_attempted)} commands allowed; "
            f"{len(manifest.policy_violations)} violations); manifest at {relpath}"
        )
        return 0
    print(
        f"real-agent-runtime: execute REFUSED/FAILED for {manifest.agent_id} on "
        f"{manifest.work_order_id or '<unknown>'}; manifest at {relpath}"
    )
    for v in manifest.policy_violations:
        print(f"  - {v.get('code', '?')}: {v.get('reason', '')}")
    return 1


def cmd_execute_check(args: argparse.Namespace) -> int:
    """Run the v0.2 execute-mode self-check fixture suite + refresh reports."""
    report = run_execute_self_check()
    md_path, json_path = write_execute_reports(report)
    if not report["all_passed"]:
        print(
            f"real-agent-runtime: EXECUTE-CHECK FAILED "
            f"({report['failed_count']} of {report['case_count']} cases)"
        )
        for r in report["execute_self_check_results"]:
            if not r["pass"]:
                print(f"  - FAIL {r['case']}: {r}")
        return 1
    print(
        f"real-agent-runtime: EXECUTE-CHECK OK "
        f"({report['passed_count']}/{report['case_count']} fixtures pass; reports at "
        f"{md_path.relative_to(REPO_ROOT)} and {json_path.relative_to(REPO_ROOT)})."
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="WiseOrder/Intellagent — REAL AGENT RUNTIME (v0.1 dry-run + v0.2 execute)")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_check = sub.add_parser("check", help="validate runtime configuration and refresh report")
    p_check.set_defaults(func=cmd_check)
    p_self = sub.add_parser("self-check", help="run admission fixtures and refresh report")
    p_self.set_defaults(func=cmd_self_check)
    p_dry = sub.add_parser("dry-run", help="dry-run a work order under an agent identity (v0.1)")
    p_dry.add_argument("--work-order", required=True, help="path to work-order yaml (relative to repo root or absolute)")
    p_dry.add_argument("--agent-id", required=True, help="agent identity (e.g. canon_guardian-01)")
    p_dry.add_argument("--preserve-sandbox", action="store_true", help="do not delete sandbox after run")
    p_dry.set_defaults(func=cmd_dry_run)
    p_built = sub.add_parser("built-in-dry-run", help="run a synthetic approved+assigned dry-run fixture end-to-end (v0.1)")
    p_built.set_defaults(func=cmd_built_in_dry_run)
    p_exec = sub.add_parser("execute", help="(v0.2) execute admitted commands in a sandbox copy")
    p_exec.add_argument("--work-order", required=True, help="path to work-order yaml")
    p_exec.add_argument("--agent-id", required=True, help="agent identity")
    p_exec.add_argument("--command", action="append", default=None, help="command to run (repeatable; defaults to required_gates)")
    p_exec.add_argument("--timeout", type=float, default=EXECUTE_TIMEOUT_DEFAULT_S, help=f"per-command timeout in seconds (default {EXECUTE_TIMEOUT_DEFAULT_S}, hard cap {EXECUTE_TIMEOUT_HARD_CAP_S})")
    p_exec.add_argument("--preserve-sandbox", action="store_true", help="do not delete sandbox after run")
    p_exec.add_argument("--replay", action="store_true", help="permit admission of a closed work order for forensic replay")
    p_exec.set_defaults(func=cmd_execute)
    p_exec_chk = sub.add_parser("execute-check", help="(v0.2) run the execute-mode self-check fixture suite and refresh v0.2 report")
    p_exec_chk.set_defaults(func=cmd_execute_check)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
