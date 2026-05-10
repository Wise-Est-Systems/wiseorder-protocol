#!/usr/bin/env python3
"""WiseOrder/Intellagent — workforce sandbox stress suite.

Runs 300 deterministic governance cases per sandbox across 3 isolated cloned
sandboxes (900 total) per WORKFORCE-SANDBOX-STRESS-v0.1.md.

Each case writes a small fixture (work order + action log + self-verification)
into a sandbox's ``workforce/`` directory, runs the comprehensive validator
(``tools/check_workforce.py`` plus augmentations described in §5 of the spec),
and compares the verdict to the case's documented expectation.

The suite is opt-in (``make workforce-stress``). It does not modify
``tools/check_workforce.py``, the runtime, the canonicalization layer, or any
release gate. All "dangerous command" patterns (sudo, rm -rf, chmod, curl,
git push --force) appear only as text inside fixture YAML files; nothing is
ever executed.

Exit code:
    0 — every case matched expectation and every cross-sandbox identity
        property held.
    1 — one or more cases mismatched, or one or more aggregation properties
        failed.
    2 — usage or environment error.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable

REPO_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = REPO_ROOT / "reports" / "workforce_sandbox_stress"
SANDBOX_NAMES: tuple[str, ...] = ("sandbox-001", "sandbox-002", "sandbox-003")
NUM_VARIANTS_PER_RULE = 3

# Files copied into each sandbox. Minimal subset required to run the validator.
SANDBOX_COPY_FILES: tuple[str, ...] = (
    "tools/check_workforce.py",
    "workforce/templates/work_order.yaml",
    "workforce/templates/action_log.yaml",
    "workforce/templates/self_verification.md",
    "workforce/README.md",
)

SANDBOX_DIRS: tuple[str, ...] = (
    "workforce/work_orders/open",
    "workforce/work_orders/closed",
    "workforce/work_orders/rejected",
    "workforce/action_logs",
    "workforce/reports",
)

# ---- Defaults used by the canonical-valid fixtures ------------------------

DEFAULT_ALLOWED: tuple[str, ...] = ("workforce/**", "reports/**")
DEFAULT_FORBIDDEN: tuple[str, ...] = (
    "SPEC.md",
    "vectors/**",
    "intellagent_runtime/**",
    "Makefile",
)
DEFAULT_REQUIRED_GATES: tuple[str, ...] = ("make no-pseudocode", "make workforce-check")

VALID_AGENT_ROLES: frozenset[str] = frozenset(
    {
        "canon_guardian",
        "builder",
        "test",
        "docs",
        "reviewer",
        "security",
        "release",
        "outreach",
    }
)

VALID_STATUSES: frozenset[str] = frozenset(
    {
        "drafted",
        "approved",
        "assigned",
        "executed",
        "self-verified",
        "gate-checked",
        "reviewed",
        "amended",
        "human_approved",
        "closed",
        "rejected",
    }
)

# Lifecycle partial order (state -> rank). Earlier states have lower ranks.
LIFECYCLE_RANK: dict[str, int] = {
    "drafted": 0,
    "approved": 1,
    "assigned": 2,
    "executed": 3,
    "self-verified": 4,
    "gate-checked": 5,
    "reviewed": 6,
    "amended": 6,
    "human_approved": 7,
    "closed": 8,
    "rejected": 8,
}

VALID_LIFECYCLE_FOR_CLOSED: tuple[tuple[str, str, str], ...] = (
    ("drafted", "henry-wayne-wise-iii", "2026-05-07T03:00:00Z"),
    ("approved", "henry-wayne-wise-iii", "2026-05-07T03:01:00Z"),
    ("assigned", "henry-wayne-wise-iii", "2026-05-07T03:02:00Z"),
    ("executed", "agent-stress-001", "2026-05-07T03:03:00Z"),
    ("self-verified", "agent-stress-001", "2026-05-07T03:04:00Z"),
    ("gate-checked", "agent-stress-001", "2026-05-07T03:05:00Z"),
    ("reviewed", "henry-wayne-wise-iii", "2026-05-07T03:06:00Z"),
    ("human_approved", "henry-wayne-wise-iii", "2026-05-07T03:07:00Z"),
    ("closed", "henry-wayne-wise-iii", "2026-05-07T03:08:00Z"),
)

# Patterns for the "dangerous command" augmentation. Matched against
# action_log.commands_run entries. The patterns appear here only as regex
# strings; the suite never invokes the underlying commands.
DANGEROUS_COMMAND_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"\bsudo\b", "sudo"),
    (r"\bchmod\s+[0-7]+\s+/", "chmod_root_path"),
    (r"\bcurl\b", "curl"),
    (r"git\s+push\s+(--force|-f)\b", "git_force_push"),
    (r"git\s+rebase\b", "git_rebase"),
    (r"git\s+filter-branch\b", "git_filter_branch"),
)
# rm -rf check is contextual: only fail if path is not a temp path.
RM_RF_PATTERN = re.compile(r"\brm\s+-rf\s+(\S+)")
TEMP_PATH_PREFIXES: tuple[str, ...] = ("/tmp/", "/var/folders/", "/private/tmp/")

AUDIT_DELETE_PATTERNS: tuple[str, ...] = (
    r"rm\s+\S*workforce/action_logs/",
    r"rm\s+\S*workforce/reports/",
)

SECRET_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"AKIA[A-Z0-9]{16}", "aws_access_key"),
    (r"ghp_[A-Za-z0-9]{20,}", "github_personal_token"),
    (r"github_pat_[A-Za-z0-9_]{20,}", "github_fine_grained_pat"),
    (r"(?i)api[_-]?key\s*[:=]\s*['\"]?[A-Za-z0-9]{16,}", "generic_api_key"),
    (r"(?i)password\s*[:=]\s*['\"]?[^'\"\s]{6,}", "generic_password"),
    (r"BEGIN [A-Z]+ PRIVATE KEY", "private_key_marker"),
)

PSEUDOCODE_MARKERS: tuple[str, ...] = (
    "TODO",
    "NotImplementedError",
    "NotImplemented",
)

CANON_PATHS_REQUIRING_CANON_BREAK: tuple[str, ...] = (
    "canonicalization/",
    "vectors/",
    "SPEC.md",
)

# ---- Data classes --------------------------------------------------------


@dataclass(frozen=True)
class CaseFixture:
    relative_path: str   # relative to sandbox root
    content: str


@dataclass
class CaseSpec:
    rule_id: str
    category: str
    name: str
    expected_outcome: str   # "pass" or "fail"
    builder: Callable[..., tuple[CaseFixture, ...]]


@dataclass
class CaseResult:
    case_id: str
    sandbox_id: str
    rule_id: str
    category: str
    name: str
    variant: int
    expected_outcome: str
    observed_outcome: str
    observed_reasons: list[str]
    validator_outcome: str
    validator_reasons: list[str]
    matched: bool
    coverage_gap: bool
    coverage_gap_kind: str
    duration_ms: int


@dataclass
class SandboxResult:
    sandbox_id: str
    sandbox_path: str
    total_checks: int
    expected_pass_count: int
    expected_fail_count: int
    observed_pass_count: int
    observed_fail_count: int
    mismatch_case_ids: list[str]
    coverage_gap_case_ids: list[str]
    case_ids: list[str]
    cases: list[CaseResult]
    duration_ms: int
    repo_source_sha256: str
    report_sha256: str = ""


# ---- Fixture rendering helpers -------------------------------------------


def _list_field(name: str, items: tuple[str, ...]) -> str:
    if not items:
        return f"{name}: []"
    lines = [f"{name}:"]
    for item in items:
        lines.append(f'  - "{_yaml_escape(item)}"')
    return "\n".join(lines)


def _yaml_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _status_history_field(entries: tuple[tuple[str, str, str, str], ...]) -> str:
    """Each entry: (state, actor, timestamp, note)."""
    lines = ["status_history:"]
    for state, actor, ts, note in entries:
        lines.append(f'  - state: "{_yaml_escape(state)}"')
        lines.append(f'    actor: "{_yaml_escape(actor)}"')
        lines.append(f'    timestamp: "{_yaml_escape(ts)}"')
        lines.append(f'    note: "{_yaml_escape(note)}"')
    return "\n".join(lines)


def render_work_order(
    *,
    work_order_id: str,
    agent_role: str = "reviewer",
    assigned_to: str = "agent-stress-001",
    objective: str = "stress-suite synthetic work order",
    allowed_files: tuple[str, ...] = DEFAULT_ALLOWED,
    forbidden_files: tuple[str, ...] = DEFAULT_FORBIDDEN,
    constraints: tuple[str, ...] = ("synthetic case",),
    expected_outputs: tuple[str, ...] = ("workforce/dummy.txt",),
    required_gates: tuple[str, ...] = DEFAULT_REQUIRED_GATES,
    rollback_plan: tuple[str, ...] = ("delete fixture",),
    human_approval_required: bool = True,
    status: str = "closed",
    status_history: tuple[tuple[str, str, str, str], ...] | None = None,
    omit_fields: tuple[str, ...] = (),
    extra_lines: tuple[str, ...] = (),
) -> str:
    """Render a work order YAML. ``omit_fields`` removes top-level keys."""
    if status_history is None:
        status_history = tuple(
            (state, actor, ts, "stress-suite synthetic entry")
            for state, actor, ts in VALID_LIFECYCLE_FOR_CLOSED
        )

    fields: dict[str, str] = {
        "work_order_id": f'work_order_id: "{_yaml_escape(work_order_id)}"',
        "agent_role": f'agent_role: "{_yaml_escape(agent_role)}"',
        "assigned_to": f'assigned_to: "{_yaml_escape(assigned_to)}"',
        "objective": f'objective: "{_yaml_escape(objective)}"',
        "allowed_files": _list_field("allowed_files", allowed_files),
        "forbidden_files": _list_field("forbidden_files", forbidden_files),
        "constraints": _list_field("constraints", constraints),
        "expected_outputs": _list_field("expected_outputs", expected_outputs),
        "required_gates": _list_field("required_gates", required_gates),
        "rollback_plan": _list_field("rollback_plan", rollback_plan),
        "human_approval_required": (
            f"human_approval_required: {'true' if human_approval_required else 'false'}"
        ),
        "status": f'status: "{_yaml_escape(status)}"',
        "status_history": _status_history_field(status_history),
    }

    rendered: list[str] = []
    for key, line in fields.items():
        if key in omit_fields:
            continue
        rendered.append(line)
    rendered.extend(extra_lines)
    return "\n".join(rendered) + "\n"


def render_action_log(
    *,
    action_id: str,
    work_order_id: str,
    agent_role: str = "reviewer",
    timestamp_start: str = "2026-05-07T03:03:00Z",
    timestamp_end: str = "2026-05-07T03:08:00Z",
    files_read: tuple[str, ...] = ("workforce/templates/work_order.yaml",),
    files_changed: tuple[str, ...] = ("workforce/dummy.txt created",),
    commands_run: tuple[str, ...] = (
        "make no-pseudocode 0",
        "make workforce-check 0",
    ),
    command_outputs_summary: tuple[str, ...] = (
        "stress-suite synthetic gate output",
        "stress-suite synthetic gate output",
    ),
    gates_passed: tuple[str, ...] = DEFAULT_REQUIRED_GATES,
    gates_failed: tuple[str, ...] = (),
    deviations: tuple[str, ...] = ("none",),
    risk_notes: tuple[str, ...] = ("none",),
    rollback_notes: str = "not executed",
    self_verification_statement: str = "",
    omit_fields: tuple[str, ...] = (),
) -> str:
    fields: dict[str, str] = {
        "action_id": f'action_id: "{_yaml_escape(action_id)}"',
        "work_order_id": f'work_order_id: "{_yaml_escape(work_order_id)}"',
        "agent_role": f'agent_role: "{_yaml_escape(agent_role)}"',
        "timestamp_start": f'timestamp_start: "{_yaml_escape(timestamp_start)}"',
        "timestamp_end": f'timestamp_end: "{_yaml_escape(timestamp_end)}"',
        "files_read": _list_field("files_read", files_read),
        "files_changed": _list_field("files_changed", files_changed),
        "commands_run": _list_field("commands_run", commands_run),
        "command_outputs_summary": _list_field(
            "command_outputs_summary", command_outputs_summary
        ),
        "gates_passed": _list_field("gates_passed", gates_passed),
        "gates_failed": _list_field("gates_failed", gates_failed),
        "deviations": _list_field("deviations", deviations),
        "risk_notes": _list_field("risk_notes", risk_notes),
        "rollback_notes": f'rollback_notes: "{_yaml_escape(rollback_notes)}"',
        "self_verification_statement": (
            f'self_verification_statement: "{_yaml_escape(self_verification_statement)}"'
        ),
    }
    rendered: list[str] = []
    for key, line in fields.items():
        if key in omit_fields:
            continue
        rendered.append(line)
    return "\n".join(rendered) + "\n"


def render_self_verification(action_id: str) -> str:
    return (
        f"# Self-Verification — {action_id}\n\n"
        "1. In scope?  yes — synthetic stress fixture.\n"
        "2. Allowed files only?  yes — synthetic.\n"
        "3. Forbidden files avoided?  yes — synthetic.\n"
        "4. All gates run?  yes — synthetic.\n"
        "5. No pseudocode?  yes — synthetic.\n"
        "6. No drift?  yes — synthetic.\n"
        "7. No canon change?  yes — synthetic.\n"
        "8. Security posture unchanged?  yes — synthetic.\n"
        "9. Risks disclosed?  yes — none.\n"
        "10. Action log consistent?  yes — synthetic.\n"
    )


# ---- Canonical valid baseline --------------------------------------------


def _ids(rule_id: str, sandbox_id: str, variant: int) -> tuple[str, str]:
    suffix = f"{sandbox_id}-{rule_id}-V{variant}"
    return f"WO-STRESS-{suffix}", f"AL-STRESS-{suffix}"


def _self_verification_path(action_id: str) -> str:
    return f"workforce/action_logs/{action_id}.self_verification.md"


def _action_log_path(action_id: str) -> str:
    return f"workforce/action_logs/{action_id}.yaml"


def _work_order_path(work_order_id: str, status_dir: str) -> str:
    return f"workforce/work_orders/{status_dir}/{work_order_id}.yaml"


def make_valid_pair(
    rule_id: str,
    sandbox_id: str,
    variant: int,
    *,
    status_dir: str = "closed",
    work_order_overrides: dict | None = None,
    action_log_overrides: dict | None = None,
) -> tuple[CaseFixture, ...]:
    wo_id, al_id = _ids(rule_id, sandbox_id, variant)
    sv_rel = _self_verification_path(al_id)

    wo_kwargs: dict = dict(work_order_id=wo_id)
    if work_order_overrides:
        wo_kwargs.update(work_order_overrides)
    wo_yaml = render_work_order(**wo_kwargs)

    al_kwargs: dict = dict(
        action_id=al_id,
        work_order_id=wo_id,
        self_verification_statement=sv_rel,
    )
    if action_log_overrides:
        al_kwargs.update(action_log_overrides)
    al_yaml = render_action_log(**al_kwargs)

    sv_md = render_self_verification(al_id)

    return (
        CaseFixture(_work_order_path(wo_id, status_dir), wo_yaml),
        CaseFixture(_action_log_path(al_id), al_yaml),
        CaseFixture(sv_rel, sv_md),
    )


# ---- Case builders -------------------------------------------------------
# Each builder returns the fixtures for a single (rule, variant, sandbox).
# The expected_outcome is fixed in the spec registry; builders only
# construct the fixtures.


def b_A1(rule_id, sandbox_id, variant):
    return make_valid_pair(rule_id, sandbox_id, variant)


def b_A2(rule_id, sandbox_id, variant):
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        work_order_overrides={"omit_fields": ("work_order_id",)},
    )


def b_A3(rule_id, sandbox_id, variant):
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        work_order_overrides={"omit_fields": ("agent_role",)},
    )


def b_A4(rule_id, sandbox_id, variant):
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        work_order_overrides={"omit_fields": ("allowed_files",)},
    )


def b_A5(rule_id, sandbox_id, variant):
    # Malformed allowed_files: scalar instead of list. Render manually.
    wo_id, al_id = _ids(rule_id, sandbox_id, variant)
    sv_rel = _self_verification_path(al_id)
    wo_yaml = render_work_order(work_order_id=wo_id, omit_fields=("allowed_files",))
    wo_yaml += 'allowed_files: "not_a_list"\n'
    al_yaml = render_action_log(
        action_id=al_id, work_order_id=wo_id, self_verification_statement=sv_rel
    )
    return (
        CaseFixture(_work_order_path(wo_id, "closed"), wo_yaml),
        CaseFixture(_action_log_path(al_id), al_yaml),
        CaseFixture(sv_rel, render_self_verification(al_id)),
    )


def b_A6(rule_id, sandbox_id, variant):
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        work_order_overrides={"omit_fields": ("forbidden_files",)},
    )


def b_A7(rule_id, sandbox_id, variant):
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        work_order_overrides={"status": "made_up_status"},
    )


def b_A8(rule_id, sandbox_id, variant):
    # Lifecycle skips required earlier states.
    bad_history = (
        ("closed", "henry-wayne-wise-iii", "2026-05-07T03:00:00Z", "skipped earlier"),
    )
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        work_order_overrides={"status_history": bad_history},
    )


def b_A9(rule_id, sandbox_id, variant):
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        work_order_overrides={"omit_fields": ("status_history",)},
    )


def b_A10(rule_id, sandbox_id, variant):
    # human_approval_required=true but no closed entry with actor in status_history.
    history = (
        ("drafted", "henry-wayne-wise-iii", "2026-05-07T03:00:00Z", "drafted"),
        ("approved", "henry-wayne-wise-iii", "2026-05-07T03:01:00Z", "approved"),
        ("closed", "", "2026-05-07T03:08:00Z", "no actor"),
    )
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        work_order_overrides={
            "human_approval_required": True,
            "status_history": history,
        },
    )


# ---- Category B: Action log -----

def b_B1(rule_id, sandbox_id, variant):
    return make_valid_pair(rule_id, sandbox_id, variant)


def b_B2(rule_id, sandbox_id, variant):
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        action_log_overrides={"omit_fields": ("action_id",)},
    )


def b_B3(rule_id, sandbox_id, variant):
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        action_log_overrides={"omit_fields": ("work_order_id",)},
    )


def b_B4(rule_id, sandbox_id, variant):
    wo_id, al_id = _ids(rule_id, sandbox_id, variant)
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        action_log_overrides={"work_order_id": f"{wo_id}-MISMATCH"},
    )


def b_B5(rule_id, sandbox_id, variant):
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        action_log_overrides={"omit_fields": ("files_read",)},
    )


def b_B6(rule_id, sandbox_id, variant):
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        action_log_overrides={"omit_fields": ("files_changed",)},
    )


def b_B7(rule_id, sandbox_id, variant):
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        action_log_overrides={"omit_fields": ("commands_run",)},
    )


def b_B8(rule_id, sandbox_id, variant):
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        action_log_overrides={"omit_fields": ("gates_passed",)},
    )


def b_B9(rule_id, sandbox_id, variant):
    # Forbidden read recorded but deviations field is empty (undocumented deviation).
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        action_log_overrides={
            "files_read": ("Makefile",),
            "deviations": (" ",),
        },
    )


def b_B10(rule_id, sandbox_id, variant):
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        action_log_overrides={"self_verification_statement": ""},
    )


# ---- Category C: Scope enforcement -----

def b_C1(rule_id, sandbox_id, variant):
    return make_valid_pair(rule_id, sandbox_id, variant)


def b_C2(rule_id, sandbox_id, variant):
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        action_log_overrides={"files_changed": ("totally/outside/scope.txt created",)},
    )


def b_C3(rule_id, sandbox_id, variant):
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        action_log_overrides={"files_read": ("Makefile",)},
    )


def b_C4(rule_id, sandbox_id, variant):
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        action_log_overrides={"files_changed": ("Makefile modified",)},
    )


def b_C5(rule_id, sandbox_id, variant):
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        action_log_overrides={"files_changed": ("vectors/some_vector.json modified",)},
    )


def b_C6(rule_id, sandbox_id, variant):
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        action_log_overrides={"files_read": ("intellagent_runtime/state.py",)},
    )


def b_C7(rule_id, sandbox_id, variant):
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        action_log_overrides={"files_changed": ("intellagent_runtime/state.py modified",)},
    )


def b_C8(rule_id, sandbox_id, variant):
    # Allowed glob expansion: changed file matches workforce/** glob.
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        action_log_overrides={"files_changed": ("workforce/sub/dir/file.txt created",)},
    )


def b_C9(rule_id, sandbox_id, variant):
    # Deny-by-default: file outside both allowed and forbidden lists must still fail.
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        action_log_overrides={"files_changed": ("some/other/place.md created",)},
    )


def b_C10(rule_id, sandbox_id, variant):
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        action_log_overrides={"files_changed": ("SPEC.md modified",)},
    )


# ---- Category D: Gate enforcement -----

def b_D1(rule_id, sandbox_id, variant):
    return make_valid_pair(rule_id, sandbox_id, variant)


def b_D2(rule_id, sandbox_id, variant):
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        action_log_overrides={"gates_passed": ("make workforce-check",)},
    )


def b_D3(rule_id, sandbox_id, variant):
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        action_log_overrides={"gates_passed": ("make no-pseudocode",)},
    )


def b_D4(rule_id, sandbox_id, variant):
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        work_order_overrides={
            "required_gates": DEFAULT_REQUIRED_GATES + ("make canonicalization-check",),
        },
        action_log_overrides={
            "gates_passed": DEFAULT_REQUIRED_GATES,
            "command_outputs_summary": (
                "stress-suite synthetic gate output",
                "stress-suite synthetic gate output",
            ),
        },
    )


def b_D5(rule_id, sandbox_id, variant):
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        action_log_overrides={
            "gates_passed": ("make no-pseudocode",),
            "gates_failed": ("make workforce-check",),
            "command_outputs_summary": ("stress-suite synthetic gate output",),
        },
    )


def b_D6(rule_id, sandbox_id, variant):
    # Gate listed in passed but no output summary recorded.
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        action_log_overrides={
            "gates_passed": DEFAULT_REQUIRED_GATES,
            "command_outputs_summary": ("",),
        },
    )


def b_D7(rule_id, sandbox_id, variant):
    # Out-of-order gate execution: declared order is no-pseudocode then workforce-check.
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        action_log_overrides={
            "commands_run": ("make workforce-check 0", "make no-pseudocode 0"),
            "gates_passed": ("make workforce-check", "make no-pseudocode"),
        },
    )


def b_D8(rule_id, sandbox_id, variant):
    # Skipped gate: required_gates includes both, action log only records one.
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        action_log_overrides={
            "gates_passed": ("make no-pseudocode",),
            "commands_run": ("make no-pseudocode 0",),
            "command_outputs_summary": ("synthetic",),
        },
    )


def b_D9(rule_id, sandbox_id, variant):
    # False success claim: same gate in passed and failed.
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        action_log_overrides={
            "gates_passed": DEFAULT_REQUIRED_GATES,
            "gates_failed": ("make workforce-check",),
        },
    )


def b_D10(rule_id, sandbox_id, variant):
    # Closure with non-empty gates_failed.
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        action_log_overrides={
            "gates_failed": ("make no-pseudocode",),
            "gates_passed": ("make workforce-check",),
            "commands_run": (
                "make no-pseudocode 1",
                "make workforce-check 0",
            ),
            "command_outputs_summary": ("failed", "synthetic"),
        },
    )


# ---- Category E: Closure -----

def b_E1(rule_id, sandbox_id, variant):
    return make_valid_pair(rule_id, sandbox_id, variant)


def b_E2(rule_id, sandbox_id, variant):
    # Closed work order with no action log file.
    wo_id, _ = _ids(rule_id, sandbox_id, variant)
    wo_yaml = render_work_order(work_order_id=wo_id)
    return (CaseFixture(_work_order_path(wo_id, "closed"), wo_yaml),)


def b_E3(rule_id, sandbox_id, variant):
    # Action log declares self-verification path but file is not written.
    wo_id, al_id = _ids(rule_id, sandbox_id, variant)
    sv_rel = _self_verification_path(al_id)
    wo_yaml = render_work_order(work_order_id=wo_id)
    al_yaml = render_action_log(
        action_id=al_id, work_order_id=wo_id, self_verification_statement=sv_rel
    )
    return (
        CaseFixture(_work_order_path(wo_id, "closed"), wo_yaml),
        CaseFixture(_action_log_path(al_id), al_yaml),
        # Self-verification file deliberately not produced.
    )


def b_E4(rule_id, sandbox_id, variant):
    # Closed work order whose expected_outputs declares a review.md but file absent.
    wo_id, _ = _ids(rule_id, sandbox_id, variant)
    review_path = f"workforce/reports/{wo_id}/review.md"
    fixtures = list(
        make_valid_pair(
            rule_id, sandbox_id, variant,
            work_order_overrides={
                "expected_outputs": ("workforce/dummy.txt", review_path),
            },
        )
    )
    return tuple(fixtures)


def b_E5(rule_id, sandbox_id, variant):
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        work_order_overrides={
            "human_approval_required": True,
            "status_history": (
                ("drafted", "henry-wayne-wise-iii", "2026-05-07T03:00:00Z", ""),
                ("approved", "henry-wayne-wise-iii", "2026-05-07T03:01:00Z", ""),
                # No closed entry with actor.
            ),
        },
    )


def b_E6(rule_id, sandbox_id, variant):
    # status=closed but file placed in open/.
    wo_id, al_id = _ids(rule_id, sandbox_id, variant)
    sv_rel = _self_verification_path(al_id)
    wo_yaml = render_work_order(work_order_id=wo_id, status="closed")
    al_yaml = render_action_log(
        action_id=al_id, work_order_id=wo_id, self_verification_statement=sv_rel
    )
    return (
        CaseFixture(_work_order_path(wo_id, "open"), wo_yaml),
        CaseFixture(_action_log_path(al_id), al_yaml),
        CaseFixture(sv_rel, render_self_verification(al_id)),
    )


def b_E7(rule_id, sandbox_id, variant):
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        action_log_overrides={
            "gates_passed": ("make no-pseudocode",),
            "commands_run": ("make no-pseudocode 0",),
            "command_outputs_summary": ("synthetic",),
        },
    )


def b_E8(rule_id, sandbox_id, variant):
    # Closure with forbidden read but deviations empty.
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        action_log_overrides={
            "files_read": ("Makefile",),
            "deviations": (" ",),
        },
    )


def b_E9(rule_id, sandbox_id, variant):
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        action_log_overrides={"files_changed": ("SPEC.md modified",)},
    )


def b_E10(rule_id, sandbox_id, variant):
    # expected_outputs declares closure_summary but file absent.
    wo_id, _ = _ids(rule_id, sandbox_id, variant)
    cs_path = f"workforce/reports/{wo_id}-closure-summary.md"
    fixtures = list(
        make_valid_pair(
            rule_id, sandbox_id, variant,
            work_order_overrides={
                "expected_outputs": ("workforce/dummy.txt", cs_path),
            },
        )
    )
    return tuple(fixtures)


# ---- Category F: Drift / canon -----

def b_F1(rule_id, sandbox_id, variant):
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        work_order_overrides={"agent_role": "builder"},
        action_log_overrides={
            "agent_role": "builder",
            "files_changed": ("SPEC.md modified",),
        },
    )


def b_F2(rule_id, sandbox_id, variant):
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        work_order_overrides={"agent_role": "builder"},
        action_log_overrides={
            "agent_role": "builder",
            "files_changed": ("vectors/v1.json modified",),
        },
    )


def b_F3(rule_id, sandbox_id, variant):
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        work_order_overrides={"agent_role": "reviewer"},
        action_log_overrides={
            "agent_role": "reviewer",
            "files_changed": ("intellagent_runtime/runtime.py modified",),
        },
    )


def b_F4(rule_id, sandbox_id, variant):
    # Pseudocode marker embedded in YAML payload.
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        action_log_overrides={
            "deviations": ("contains TODO marker invented behavior",),
        },
    )


def b_F5(rule_id, sandbox_id, variant):
    # Canonicalization change without CANON BREAK marker anywhere in WO body.
    # Constraint text avoids the literal marker string.
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        work_order_overrides={
            "allowed_files": DEFAULT_ALLOWED + ("canonicalization/**",),
            "constraints": ("synthetic canonicalization touch fixture",),
        },
        action_log_overrides={
            "files_changed": ("canonicalization/corpus/001.json modified",),
        },
    )


def b_F6(rule_id, sandbox_id, variant):
    # Invariant change (touch INTELLAGENT.md) with human_approval_required=false.
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        work_order_overrides={
            "allowed_files": DEFAULT_ALLOWED + ("INTELLAGENT.md",),
            "human_approval_required": False,
        },
        action_log_overrides={
            "files_changed": ("INTELLAGENT.md modified",),
        },
    )


def b_F7(rule_id, sandbox_id, variant):
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        work_order_overrides={
            "allowed_files": DEFAULT_ALLOWED + ("CANONICAL-RELEASE-v0.1.md",),
            "human_approval_required": False,
        },
        action_log_overrides={
            "files_changed": ("CANONICAL-RELEASE-v0.1.md modified",),
        },
    )


def b_F8(rule_id, sandbox_id, variant):
    # Authorization semantics change without security review (role != security).
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        work_order_overrides={
            "agent_role": "builder",
            "allowed_files": DEFAULT_ALLOWED + ("intellagent_runtime/authorization.py",),
        },
        action_log_overrides={
            "agent_role": "builder",
            "files_changed": ("intellagent_runtime/authorization.py modified",),
        },
    )


def b_F9(rule_id, sandbox_id, variant):
    # Replay semantics change (memory.py) without release-continuity review.
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        work_order_overrides={
            "agent_role": "builder",
            "allowed_files": DEFAULT_ALLOWED + ("intellagent_runtime/memory.py",),
            "constraints": ("no release-continuity review attached",),
        },
        action_log_overrides={
            "agent_role": "builder",
            "files_changed": ("intellagent_runtime/memory.py modified",),
        },
    )


def b_F10(rule_id, sandbox_id, variant):
    # Both canon (SPEC.md) and implementation (runtime) in allowed_files.
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        work_order_overrides={
            "allowed_files": (
                "workforce/**",
                "reports/**",
                "SPEC.md",
                "intellagent_runtime/**",
            ),
        },
    )


# ---- Category G: Security -----

def b_G1(rule_id, sandbox_id, variant):
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        action_log_overrides={
            "risk_notes": ("AKIAABCDEFGHIJKLMNOP found in synthetic payload",),
        },
    )


def b_G2(rule_id, sandbox_id, variant):
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        work_order_overrides={
            "constraints": ("ghp_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA in payload",),
        },
    )


def b_G3(rule_id, sandbox_id, variant):
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        action_log_overrides={
            "commands_run": ("chmod 777 / 0",),
        },
    )


def b_G4(rule_id, sandbox_id, variant):
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        action_log_overrides={
            "commands_run": ("curl https://example.com/payload 0",),
        },
    )


def b_G5(rule_id, sandbox_id, variant):
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        action_log_overrides={
            "commands_run": ("git push --force origin main 0",),
        },
    )


def b_G6(rule_id, sandbox_id, variant):
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        action_log_overrides={
            "commands_run": ("rm workforce/action_logs/old.yaml 0",),
        },
    )


def b_G7(rule_id, sandbox_id, variant):
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        action_log_overrides={
            "risk_notes": ("BEGIN RSA PRIVATE KEY synthetic payload",),
        },
    )


def b_G8(rule_id, sandbox_id, variant):
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        action_log_overrides={
            "commands_run": ("curl --silent https://x.test/y 0",),
        },
    )


def b_G9(rule_id, sandbox_id, variant):
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        action_log_overrides={
            "commands_run": ("rm -rf /etc 0",),
        },
    )


def b_G10(rule_id, sandbox_id, variant):
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        action_log_overrides={
            "commands_run": ("sudo make ci 0",),
        },
    )


# ---- Category H: Mutation / resilience -----

def b_H1(rule_id, sandbox_id, variant):
    fields_to_drop = ("constraints", "expected_outputs", "rollback_plan")
    drop = (fields_to_drop[variant % len(fields_to_drop)],)
    # constraints/expected_outputs/rollback_plan are not in WORK_ORDER_REQUIRED_FIELDS,
    # so dropping them does not fail the validator. We force a required-field drop instead.
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        work_order_overrides={"omit_fields": ("constraints",)} if False else {"omit_fields": ("agent_role",)},
    )


def b_H2(rule_id, sandbox_id, variant):
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        work_order_overrides={"status": "definitely_invalid"},
    )


def b_H3(rule_id, sandbox_id, variant):
    wo_id, al_id = _ids(rule_id, sandbox_id, variant)
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        action_log_overrides={"work_order_id": "WO-COMPLETELY-DIFFERENT"},
    )


def b_H4(rule_id, sandbox_id, variant):
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        work_order_overrides={"allowed_files": ("workforce/templates/**",)},
        action_log_overrides={"files_changed": ("workforce/dummy.txt created",)},
    )


def b_H5(rule_id, sandbox_id, variant):
    # forbidden_files expanded to include a path that was read.
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        work_order_overrides={
            "forbidden_files": DEFAULT_FORBIDDEN + ("workforce/templates/**",),
        },
        action_log_overrides={
            "files_read": ("workforce/templates/work_order.yaml",),
        },
    )


def b_H6(rule_id, sandbox_id, variant):
    # Duplicate action_id: write the canonical pair plus a second action log
    # with the same action_id but different filename suffix.
    base = make_valid_pair(rule_id, sandbox_id, variant)
    wo_path, al_path, sv_path = base
    al_path_b = CaseFixture(
        al_path.relative_path.replace(".yaml", "-DUP.yaml"),
        al_path.content,
    )
    return base + (al_path_b,)


def b_H7(rule_id, sandbox_id, variant):
    # Same work_order_id appears in open/ and closed/.
    wo_id, al_id = _ids(rule_id, sandbox_id, variant)
    sv_rel = _self_verification_path(al_id)
    wo_yaml = render_work_order(work_order_id=wo_id)
    al_yaml = render_action_log(
        action_id=al_id, work_order_id=wo_id, self_verification_statement=sv_rel
    )
    return (
        CaseFixture(_work_order_path(wo_id, "closed"), wo_yaml),
        CaseFixture(_work_order_path(wo_id, "open"), wo_yaml),
        CaseFixture(_action_log_path(al_id), al_yaml),
        CaseFixture(sv_rel, render_self_verification(al_id)),
    )


def b_H8(rule_id, sandbox_id, variant):
    # Malformed YAML: no key:value lines, no list items.
    wo_id, _ = _ids(rule_id, sandbox_id, variant)
    return (
        CaseFixture(
            _work_order_path(wo_id, "closed"),
            "this is not valid yaml content at all\njust prose\n",
        ),
    )


def b_H9(rule_id, sandbox_id, variant):
    wo_id, _ = _ids(rule_id, sandbox_id, variant)
    return (CaseFixture(_work_order_path(wo_id, "closed"), ""),)


def b_H10(rule_id, sandbox_id, variant):
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        work_order_overrides={"agent_role": "made_up_role"},
        action_log_overrides={"agent_role": "made_up_role"},
    )


# ---- Category I: Positive lifecycle -----

def _lifecycle_through(stop_state: str, status: str, status_dir: str = "open"):
    history = []
    for state, actor, ts in VALID_LIFECYCLE_FOR_CLOSED:
        history.append((state, actor, ts, ""))
        if state == stop_state:
            break
    return history, status, status_dir


def _build_positive(rule_id, sandbox_id, variant, stop_state, status_dir="open"):
    history, status, sd = _lifecycle_through(stop_state, stop_state, status_dir)
    if status_dir == "closed":
        # For closed, use the full history.
        history = [(s, a, t, "") for s, a, t in VALID_LIFECYCLE_FOR_CLOSED]
        status = "closed"
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        status_dir=status_dir,
        work_order_overrides={
            "status": status,
            "status_history": tuple(history),
        },
    )


def b_I1(rule_id, sandbox_id, variant):
    return _build_positive(rule_id, sandbox_id, variant, "approved", "open")


def b_I2(rule_id, sandbox_id, variant):
    return _build_positive(rule_id, sandbox_id, variant, "assigned", "open")


def b_I3(rule_id, sandbox_id, variant):
    return _build_positive(rule_id, sandbox_id, variant, "executed", "open")


def b_I4(rule_id, sandbox_id, variant):
    return _build_positive(rule_id, sandbox_id, variant, "self-verified", "open")


def b_I5(rule_id, sandbox_id, variant):
    return _build_positive(rule_id, sandbox_id, variant, "gate-checked", "open")


def b_I6(rule_id, sandbox_id, variant):
    return _build_positive(rule_id, sandbox_id, variant, "reviewed", "open")


def b_I7(rule_id, sandbox_id, variant):
    return _build_positive(rule_id, sandbox_id, variant, "human_approved", "open")


def b_I8(rule_id, sandbox_id, variant):
    return _build_positive(rule_id, sandbox_id, variant, "closed", "closed")


def b_I9(rule_id, sandbox_id, variant):
    history = (
        ("drafted", "henry-wayne-wise-iii", "2026-05-07T03:00:00Z", ""),
        ("approved", "henry-wayne-wise-iii", "2026-05-07T03:01:00Z", ""),
        ("assigned", "henry-wayne-wise-iii", "2026-05-07T03:02:00Z", ""),
        ("executed", "agent-stress-001", "2026-05-07T03:03:00Z", ""),
        ("rejected", "henry-wayne-wise-iii", "2026-05-07T03:04:00Z", "rolled back"),
    )
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        status_dir="rejected",
        work_order_overrides={"status": "rejected", "status_history": history},
    )


def b_I10(rule_id, sandbox_id, variant):
    history = list((s, a, t, "") for s, a, t in VALID_LIFECYCLE_FOR_CLOSED)
    history.insert(
        7,
        (
            "amended",
            "henry-wayne-wise-iii",
            "2026-05-07T03:06:30Z",
            "human-owner amendment",
        ),
    )
    return make_valid_pair(
        rule_id, sandbox_id, variant,
        work_order_overrides={"status_history": tuple(history)},
    )


# ---- Category J: Sandbox-internal smoke -----

def b_J(rule_id, sandbox_id, variant):
    """All J cases are pass-through: empty fixture set, validator passes on
    a clean workforce dir, augmentations pass, observed=pass=expected.
    Aggregation evaluates the actual cross-sandbox properties globally."""
    return ()


# ---- Spec registry -------------------------------------------------------

CASE_SPECS: tuple[CaseSpec, ...] = (
    # A
    CaseSpec("A1", "A", "valid work order passes", "pass", b_A1),
    CaseSpec("A2", "A", "missing work_order_id fails", "fail", b_A2),
    CaseSpec("A3", "A", "missing agent_role fails", "fail", b_A3),
    CaseSpec("A4", "A", "missing allowed_files fails", "fail", b_A4),
    CaseSpec("A5", "A", "malformed allowed_files fails", "fail", b_A5),
    CaseSpec("A6", "A", "missing forbidden_files fails", "fail", b_A6),
    CaseSpec("A7", "A", "invalid status fails", "fail", b_A7),
    CaseSpec("A8", "A", "invalid lifecycle transition fails", "fail", b_A8),
    CaseSpec("A9", "A", "missing status_history fails", "fail", b_A9),
    CaseSpec("A10", "A", "missing human approval where required fails", "fail", b_A10),
    # B
    CaseSpec("B1", "B", "valid action log passes", "pass", b_B1),
    CaseSpec("B2", "B", "missing action_id fails", "fail", b_B2),
    CaseSpec("B3", "B", "missing work_order_id fails", "fail", b_B3),
    CaseSpec("B4", "B", "wrong work_order_id fails", "fail", b_B4),
    CaseSpec("B5", "B", "missing files_read fails", "fail", b_B5),
    CaseSpec("B6", "B", "missing files_changed fails", "fail", b_B6),
    CaseSpec("B7", "B", "missing commands_run fails", "fail", b_B7),
    CaseSpec("B8", "B", "missing gates_passed fails", "fail", b_B8),
    CaseSpec("B9", "B", "undeclared deviation fails", "fail", b_B9),
    CaseSpec("B10", "B", "missing self_verification_statement fails", "fail", b_B10),
    # C
    CaseSpec("C1", "C", "changed file inside allowed_files passes", "pass", b_C1),
    CaseSpec("C2", "C", "changed file outside allowed_files fails", "fail", b_C2),
    CaseSpec("C3", "C", "forbidden file in files_read fails", "fail", b_C3),
    CaseSpec("C4", "C", "forbidden file in files_changed fails", "fail", b_C4),
    CaseSpec("C5", "C", "forbidden directory glob fails", "fail", b_C5),
    CaseSpec("C6", "C", "hidden forbidden read fails if recorded", "fail", b_C6),
    CaseSpec("C7", "C", "hidden forbidden change fails if recorded", "fail", b_C7),
    CaseSpec("C8", "C", "allowed glob expansion works", "pass", b_C8),
    CaseSpec("C9", "C", "denied-by-default outside allowed_files works", "fail", b_C9),
    CaseSpec("C10", "C", "closed order with forbidden touch fails", "fail", b_C10),
    # D
    CaseSpec("D1", "D", "required gates subset passes", "pass", b_D1),
    CaseSpec("D2", "D", "missing make no-pseudocode fails", "fail", b_D2),
    CaseSpec("D3", "D", "missing make workforce-check fails", "fail", b_D3),
    CaseSpec("D4", "D", "missing canonicalization-check when required fails", "fail", b_D4),
    CaseSpec("D5", "D", "gate listed but failed fails", "fail", b_D5),
    CaseSpec("D6", "D", "gate listed without output summary fails", "fail", b_D6),
    CaseSpec("D7", "D", "required gate order enforced if declared", "fail", b_D7),
    CaseSpec("D8", "D", "skipped gate fails", "fail", b_D8),
    CaseSpec("D9", "D", "false success claim fails", "fail", b_D9),
    CaseSpec("D10", "D", "closure without green gates fails", "fail", b_D10),
    # E
    CaseSpec("E1", "E", "valid closure passes", "pass", b_E1),
    CaseSpec("E2", "E", "closure without action log fails", "fail", b_E2),
    CaseSpec("E3", "E", "closure without self-verification fails", "fail", b_E3),
    CaseSpec("E4", "E", "closure without reviewer signoff fails", "fail", b_E4),
    CaseSpec("E5", "E", "closure without human approval when required fails", "fail", b_E5),
    CaseSpec("E6", "E", "closure while work order still open fails", "fail", b_E6),
    CaseSpec("E7", "E", "closure with unresolved required gates fails", "fail", b_E7),
    CaseSpec("E8", "E", "closure with undocumented deviation fails", "fail", b_E8),
    CaseSpec("E9", "E", "closure with forbidden files touched fails", "fail", b_E9),
    CaseSpec("E10", "E", "closure summary mismatch fails", "fail", b_E10),
    # F
    CaseSpec("F1", "F", "SPEC.md touch by Builder Agent fails", "fail", b_F1),
    CaseSpec("F2", "F", "vectors touch by Builder Agent fails", "fail", b_F2),
    CaseSpec("F3", "F", "runtime touch by Reviewer Agent fails", "fail", b_F3),
    CaseSpec("F4", "F", "docs inventing runtime behavior fails if detectable by markers", "fail", b_F4),
    CaseSpec("F5", "F", "canonicalization change without CANON BREAK marker fails", "fail", b_F5),
    CaseSpec("F6", "F", "invariant change without human approval fails", "fail", b_F6),
    CaseSpec("F7", "F", "release law change without approval fails", "fail", b_F7),
    CaseSpec("F8", "F", "authorization semantics change without security review fails", "fail", b_F8),
    CaseSpec("F9", "F", "replay semantics change without release-continuity review fails", "fail", b_F9),
    CaseSpec("F10", "F", "work order attempting canon + implementation change fails", "fail", b_F10),
    # G
    CaseSpec("G1", "G", "AWS access key in action log fails", "fail", b_G1),
    CaseSpec("G2", "G", "GitHub token in work order fails", "fail", b_G2),
    CaseSpec("G3", "G", "chmod recorded without approval fails", "fail", b_G3),
    CaseSpec("G4", "G", "curl recorded without approval fails", "fail", b_G4),
    CaseSpec("G5", "G", "git push --force recorded fails", "fail", b_G5),
    CaseSpec("G6", "G", "deletion of audit artifact fails", "fail", b_G6),
    CaseSpec("G7", "G", "private key marker fails", "fail", b_G7),
    CaseSpec("G8", "G", "shell curl fails unless explicitly approved", "fail", b_G8),
    CaseSpec("G9", "G", "rm -rf outside sandbox temp dir fails", "fail", b_G9),
    CaseSpec("G10", "G", "sudo recorded always fails", "fail", b_G10),
    # H
    CaseSpec("H1", "H", "random required-field deletion fails", "fail", b_H1),
    CaseSpec("H2", "H", "random status mutation to invalid enum fails", "fail", b_H2),
    CaseSpec("H3", "H", "random work_order_id mismatch fails", "fail", b_H3),
    CaseSpec("H4", "H", "shrunk allowed_files reveals out-of-scope changes", "fail", b_H4),
    CaseSpec("H5", "H", "expanded forbidden_files catches prior reads", "fail", b_H5),
    CaseSpec("H6", "H", "duplicate action_id fails", "fail", b_H6),
    CaseSpec("H7", "H", "duplicate work_order_id across open/closed fails", "fail", b_H7),
    CaseSpec("H8", "H", "malformed YAML fails closed", "fail", b_H8),
    CaseSpec("H9", "H", "empty file fails closed", "fail", b_H9),
    CaseSpec("H10", "H", "unknown agent role fails closed", "fail", b_H10),
    # I
    CaseSpec("I1", "I", "drafted -> approved passes", "pass", b_I1),
    CaseSpec("I2", "I", "approved -> assigned passes", "pass", b_I2),
    CaseSpec("I3", "I", "assigned -> executed passes", "pass", b_I3),
    CaseSpec("I4", "I", "executed -> self_verified passes", "pass", b_I4),
    CaseSpec("I5", "I", "self_verified -> gate_checked passes", "pass", b_I5),
    CaseSpec("I6", "I", "gate_checked -> reviewed passes", "pass", b_I6),
    CaseSpec("I7", "I", "reviewed -> human_approved passes", "pass", b_I7),
    CaseSpec("I8", "I", "human_approved -> closed passes", "pass", b_I8),
    CaseSpec("I9", "I", "rejected lifecycle properly logged passes", "pass", b_I9),
    CaseSpec("I10", "I", "amendment lifecycle with human approval passes", "pass", b_I10),
    # J — per-sandbox smoke; aggregation evaluates cross-sandbox properties globally.
    CaseSpec("J1", "J", "sandbox produces independent report", "pass", b_J),
    CaseSpec("J2", "J", "sandbox does not write into another sandbox", "pass", b_J),
    CaseSpec("J3", "J", "report hashes differ only when expected", "pass", b_J),
    CaseSpec("J4", "J", "identical valid fixtures produce identical result", "pass", b_J),
    CaseSpec("J5", "J", "identical invalid fixtures produce identical failure", "pass", b_J),
    CaseSpec("J6", "J", "final aggregate count equals 900", "pass", b_J),
    CaseSpec("J7", "J", "any failed expected-pass check fails the suite", "pass", b_J),
    CaseSpec("J8", "J", "any passed expected-fail check fails the suite", "pass", b_J),
    CaseSpec("J9", "J", "aggregate report includes per-sandbox SHA-256", "pass", b_J),
    CaseSpec("J10", "J", "aggregate report includes exact failing case IDs", "pass", b_J),
)

assert len(CASE_SPECS) == 100, f"expected 100 rule templates, got {len(CASE_SPECS)}"


# ---- Comprehensive validator ---------------------------------------------


def _list_str_field(parsed: dict, key: str) -> list[str]:
    val = parsed.get(key)
    if isinstance(val, list):
        return [v if isinstance(v, str) else str(v) for v in val]
    if val is None:
        return []
    return [str(val)]


def _scan_str_for_secrets(text: str) -> list[str]:
    findings: list[str] = []
    for pattern, name in SECRET_PATTERNS:
        if re.search(pattern, text):
            findings.append(f"secret_pattern:{name}")
    return findings


def _scan_str_for_pseudocode(text: str) -> list[str]:
    findings: list[str] = []
    for marker in PSEUDOCODE_MARKERS:
        if marker in text:
            findings.append(f"pseudocode_marker:{marker}")
    # Bare ellipsis statement on its own line.
    if re.search(r"^\s*\.\.\.\s*$", text, re.MULTILINE):
        findings.append("pseudocode_marker:ellipsis_statement")
    if re.search(r"\breturn\s+\.\.\.", text):
        findings.append("pseudocode_marker:return_ellipsis")
    return findings


def _scan_command_dangerous(cmd: str) -> list[str]:
    findings: list[str] = []
    for pattern, name in DANGEROUS_COMMAND_PATTERNS:
        if re.search(pattern, cmd):
            findings.append(f"dangerous_command:{name}")
    m = RM_RF_PATTERN.search(cmd)
    if m:
        path = m.group(1)
        if not any(path.startswith(prefix) for prefix in TEMP_PATH_PREFIXES):
            findings.append("dangerous_command:rm_rf_outside_temp")
    for pattern in AUDIT_DELETE_PATTERNS:
        if re.search(pattern, cmd):
            findings.append("dangerous_command:audit_artifact_delete")
    return findings


def _parse_for_augmentation(path: Path) -> dict:
    """Reuse the validator's flat-YAML parser by importing it."""
    sys.path.insert(0, str(path.parent.parent / "tools"))
    try:
        import importlib
        mod = importlib.import_module("check_workforce")
        return mod.parse_flat_yaml(path)
    finally:
        if str(path.parent.parent / "tools") in sys.path:
            sys.path.remove(str(path.parent.parent / "tools"))


def comprehensive_check(sandbox_root: Path) -> tuple[str, list[str], str, list[str]]:
    """Run the validator and the augmentations.

    Returns (observed_outcome, observed_reasons, validator_outcome, validator_reasons).
    """
    validator_path = sandbox_root / "tools" / "check_workforce.py"
    proc = subprocess.run(
        [sys.executable, str(validator_path)],
        cwd=str(sandbox_root),
        capture_output=True,
        text=True,
        timeout=30,
    )
    validator_outcome = "pass" if proc.returncode == 0 else "fail"
    validator_reasons: list[str] = []
    if proc.returncode != 0:
        for line in proc.stdout.splitlines():
            line = line.strip()
            if line.startswith("- ["):
                validator_reasons.append(line)

    augmentation_findings: list[str] = []

    workforce_dir = sandbox_root / "workforce"
    wo_open = sorted((workforce_dir / "work_orders" / "open").glob("*.yaml"))
    wo_closed = sorted((workforce_dir / "work_orders" / "closed").glob("*.yaml"))
    wo_rejected = sorted((workforce_dir / "work_orders" / "rejected").glob("*.yaml"))
    al_files = sorted((workforce_dir / "action_logs").glob("*.yaml"))

    seen_wo_ids: dict[str, list[str]] = {}
    seen_al_ids: dict[str, list[str]] = {}
    wo_required_gates: dict[str, list[str]] = {}

    def parse(path: Path) -> dict | None:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            return None
        if not text.strip():
            augmentation_findings.append(f"augmentation:empty_file:{path.name}")
            return None
        if not re.search(r"^\s*\S+:", text, re.MULTILINE) and not re.search(r"^\s*-\s+", text, re.MULTILINE):
            augmentation_findings.append(f"augmentation:malformed_yaml:{path.name}")
            return None
        try:
            return _parse_for_augmentation(path)
        except Exception as exc:  # noqa: BLE001
            augmentation_findings.append(f"augmentation:parse_error:{path.name}:{exc}")
            return None

    for status_dir, files in (
        ("open", wo_open),
        ("closed", wo_closed),
        ("rejected", wo_rejected),
    ):
        for path in files:
            parsed = parse(path)
            if parsed is None:
                continue
            text = path.read_text(encoding="utf-8")

            # Status enum.
            status = parsed.get("status")
            if isinstance(status, str) and status not in VALID_STATUSES:
                augmentation_findings.append(
                    f"augmentation:invalid_status:{path.name}:{status}"
                )

            # Status / directory consistency.
            if isinstance(status, str) and status:
                expected_dir = (
                    "closed" if status == "closed"
                    else "rejected" if status == "rejected"
                    else "open"
                )
                if status_dir != expected_dir:
                    augmentation_findings.append(
                        f"augmentation:status_directory_mismatch:{path.name}:status={status}:dir={status_dir}"
                    )

            # Stash required_gates for the action-log loop.
            wo_id_for_gates = parsed.get("work_order_id")
            if isinstance(wo_id_for_gates, str) and wo_id_for_gates:
                wo_required_gates[wo_id_for_gates] = _list_str_field(parsed, "required_gates")

            # Agent role enum.
            role = parsed.get("agent_role")
            if isinstance(role, str) and role and role not in VALID_AGENT_ROLES:
                augmentation_findings.append(
                    f"augmentation:invalid_agent_role:{path.name}:{role}"
                )

            # Lifecycle order check (only if status_history non-empty).
            history_states: list[str] = []
            in_hist = False
            for raw in text.splitlines():
                line = raw.split("#", 1)[0].rstrip()
                if line.strip().startswith("status_history"):
                    in_hist = True
                    continue
                if not in_hist:
                    continue
                m = re.match(r'\s*-\s*state:\s*"?([^"\n]+)"?\s*$', line)
                if m:
                    history_states.append(m.group(1).strip())
            if isinstance(status, str) and status in {"closed", "human_approved"}:
                if "drafted" not in history_states or "approved" not in history_states:
                    augmentation_findings.append(
                        f"augmentation:lifecycle_missing_initial:{path.name}"
                    )
            if history_states:
                ranks = [LIFECYCLE_RANK.get(s, -1) for s in history_states]
                if any(r == -1 for r in ranks):
                    augmentation_findings.append(
                        f"augmentation:lifecycle_unknown_state:{path.name}"
                    )
                # Non-decreasing ranks (allow ties for amended).
                for i in range(1, len(ranks)):
                    if ranks[i] < ranks[i - 1]:
                        augmentation_findings.append(
                            f"augmentation:lifecycle_out_of_order:{path.name}"
                        )
                        break

            # Duplicate work_order_id check.
            wo_id = parsed.get("work_order_id")
            if isinstance(wo_id, str) and wo_id:
                seen_wo_ids.setdefault(wo_id, []).append(status_dir)

            # Secret + pseudocode + canon-break checks scan the file body.
            for finding in _scan_str_for_secrets(text):
                augmentation_findings.append(f"{finding}:{path.name}")
            for finding in _scan_str_for_pseudocode(text):
                augmentation_findings.append(f"{finding}:{path.name}")

            # Canon-break marker check.
            allowed = _list_str_field(parsed, "allowed_files")
            files_changed_field: list[str] = []   # filled when scanning action logs
            if any(any(p in a for p in CANON_PATHS_REQUIRING_CANON_BREAK) for a in allowed):
                if "CANON BREAK" not in text:
                    augmentation_findings.append(
                        f"augmentation:canonicalization_change_missing_canon_break:{path.name}"
                    )

            # F10: canon + implementation in one work order.
            has_canon = any("SPEC.md" in a or "vectors/" in a or "canonicalization/" in a for a in allowed)
            has_impl = any("intellagent_runtime/" in a or a.endswith(".py") for a in allowed)
            if has_canon and has_impl:
                augmentation_findings.append(
                    f"augmentation:canon_plus_implementation:{path.name}"
                )

            # F6/F7: invariant or release-law file change without human approval.
            invariant_paths_in_allowed = [
                a for a in allowed
                if a in {"INTELLAGENT.md", "INTELLAGENT-RUNTIME.md", "CANONICAL-RELEASE-v0.1.md"}
            ]
            if invariant_paths_in_allowed:
                if str(parsed.get("human_approval_required")).lower() != "true":
                    augmentation_findings.append(
                        f"augmentation:invariant_change_without_human_approval:{path.name}"
                    )

            # F8/F9: authorization or replay semantics change must be security/release role.
            auth_change = any("authorization" in a for a in allowed)
            replay_change = any("memory.py" in a for a in allowed)
            if auth_change and role not in {"security"}:
                augmentation_findings.append(
                    f"augmentation:authorization_change_wrong_role:{path.name}:{role}"
                )
            if replay_change and role not in {"release", "security"}:
                augmentation_findings.append(
                    f"augmentation:replay_change_wrong_role:{path.name}:{role}"
                )

            # E4 reviewer signoff file check.
            if status_dir == "closed":
                expected_outputs = _list_str_field(parsed, "expected_outputs")
                for out in expected_outputs:
                    if out.endswith("/review.md") or out.endswith("review.md"):
                        out_path = sandbox_root / out
                        if not out_path.exists():
                            augmentation_findings.append(
                                f"augmentation:reviewer_signoff_missing:{path.name}:{out}"
                            )
                    if out.endswith("-closure-summary.md"):
                        out_path = sandbox_root / out
                        if not out_path.exists():
                            augmentation_findings.append(
                                f"augmentation:closure_summary_missing:{path.name}:{out}"
                            )

    # Action logs.
    for path in al_files:
        parsed = parse(path)
        if parsed is None:
            continue
        text = path.read_text(encoding="utf-8")

        action_id = parsed.get("action_id")
        if isinstance(action_id, str) and action_id:
            seen_al_ids.setdefault(action_id, []).append(path.name)

        role = parsed.get("agent_role")
        if isinstance(role, str) and role and role not in VALID_AGENT_ROLES:
            augmentation_findings.append(
                f"augmentation:invalid_agent_role:{path.name}:{role}"
            )

        # Secret + pseudocode scans.
        for finding in _scan_str_for_secrets(text):
            augmentation_findings.append(f"{finding}:{path.name}")
        for finding in _scan_str_for_pseudocode(text):
            augmentation_findings.append(f"{finding}:{path.name}")

        # Dangerous command scan.
        commands = _list_str_field(parsed, "commands_run")
        for cmd in commands:
            for finding in _scan_command_dangerous(cmd):
                augmentation_findings.append(f"{finding}:{path.name}")

        # Gate output presence: each gates_passed entry needs a non-empty summary.
        gates_passed = _list_str_field(parsed, "gates_passed")
        outputs = _list_str_field(parsed, "command_outputs_summary")
        non_empty_outputs = [o for o in outputs if o.strip()]
        if gates_passed and len(non_empty_outputs) < len(gates_passed):
            augmentation_findings.append(
                f"augmentation:gate_output_missing:{path.name}"
            )

        # Gate consistency: no overlap between passed and failed.
        gates_failed = set(_list_str_field(parsed, "gates_failed"))
        if set(gates_passed) & gates_failed:
            augmentation_findings.append(
                f"augmentation:gate_in_passed_and_failed:{path.name}"
            )

        # Gate order: gates_passed must list gates in the same order as
        # the work order's required_gates when both lists hold the same set.
        wo_ref_for_gates = parsed.get("work_order_id")
        if isinstance(wo_ref_for_gates, str) and wo_ref_for_gates in wo_required_gates:
            req = wo_required_gates[wo_ref_for_gates]
            if (
                req
                and gates_passed
                and len(gates_passed) == len(req)
                and set(gates_passed) == set(req)
                and list(gates_passed) != list(req)
            ):
                augmentation_findings.append(
                    f"augmentation:gate_order_violation:{path.name}"
                )

        # Undocumented deviation: forbidden read recorded but deviations is empty.
        files_read = _list_str_field(parsed, "files_read")
        deviations = [d for d in _list_str_field(parsed, "deviations") if d.strip()]
        forbidden_read = False
        for fr in files_read:
            for forbidden_pattern in DEFAULT_FORBIDDEN:
                from fnmatch import fnmatch
                if fr == forbidden_pattern or fnmatch(fr, forbidden_pattern):
                    forbidden_read = True
                    break
            if forbidden_read:
                break
        if forbidden_read and not deviations:
            augmentation_findings.append(
                f"augmentation:undocumented_deviation:{path.name}"
            )

        # H3: work_order_id mismatch (action log refers to nonexistent work order).
        wo_ref = parsed.get("work_order_id")
        if isinstance(wo_ref, str) and wo_ref and wo_ref not in seen_wo_ids:
            augmentation_findings.append(
                f"augmentation:action_log_orphan:{path.name}:{wo_ref}"
            )

    # Duplicate IDs.
    for wo_id, locs in seen_wo_ids.items():
        if len(locs) > 1:
            augmentation_findings.append(
                f"augmentation:duplicate_work_order_id:{wo_id}:{','.join(locs)}"
            )
    for al_id, files in seen_al_ids.items():
        if len(files) > 1:
            augmentation_findings.append(
                f"augmentation:duplicate_action_id:{al_id}:{','.join(files)}"
            )

    observed_reasons = list(validator_reasons) + augmentation_findings
    if validator_outcome == "fail" or augmentation_findings:
        observed_outcome = "fail"
    else:
        observed_outcome = "pass"

    return observed_outcome, observed_reasons, validator_outcome, validator_reasons


# ---- Sandbox setup -------------------------------------------------------


def setup_sandbox(sandbox_id: str) -> Path:
    sandbox_root = Path(tempfile.mkdtemp(prefix=f"workforce-stress-{sandbox_id}-"))
    for rel in SANDBOX_DIRS:
        (sandbox_root / rel).mkdir(parents=True, exist_ok=True)
    for rel in SANDBOX_COPY_FILES:
        src = REPO_ROOT / rel
        dest = sandbox_root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
    return sandbox_root


def repo_source_fingerprint() -> str:
    h = hashlib.sha256()
    for rel in sorted(SANDBOX_COPY_FILES):
        src = REPO_ROOT / rel
        h.update(rel.encode("utf-8"))
        h.update(b"\x00")
        h.update(src.read_bytes())
        h.update(b"\x00")
    return "sha256:" + h.hexdigest()


def clean_workforce_records(sandbox_root: Path) -> None:
    for rel in SANDBOX_DIRS:
        target = sandbox_root / rel
        if not target.is_dir():
            continue
        for child in target.iterdir():
            if child.is_file():
                child.unlink()
            elif child.is_dir():
                shutil.rmtree(child)


def write_fixtures(sandbox_root: Path, fixtures: tuple[CaseFixture, ...]) -> None:
    for fix in fixtures:
        path = sandbox_root / fix.relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(fix.content, encoding="utf-8")


# ---- Per-sandbox execution -----------------------------------------------


def run_sandbox(sandbox_id: str, repo_fp: str) -> SandboxResult:
    started = time.monotonic()
    sandbox_root = setup_sandbox(sandbox_id)

    cases: list[CaseResult] = []
    case_ids: list[str] = []
    expected_pass = 0
    expected_fail = 0
    observed_pass = 0
    observed_fail = 0
    mismatch_ids: list[str] = []
    coverage_gap_ids: list[str] = []

    for spec in CASE_SPECS:
        for variant in range(NUM_VARIANTS_PER_RULE):
            case_id = f"{sandbox_id}-{spec.rule_id}-V{variant}"
            case_ids.append(case_id)

            if spec.expected_outcome == "pass":
                expected_pass += 1
            else:
                expected_fail += 1

            clean_workforce_records(sandbox_root)
            try:
                fixtures = spec.builder(spec.rule_id, sandbox_id, variant)
            except Exception as exc:  # noqa: BLE001
                cases.append(
                    CaseResult(
                        case_id=case_id, sandbox_id=sandbox_id, rule_id=spec.rule_id,
                        category=spec.category, name=spec.name, variant=variant,
                        expected_outcome=spec.expected_outcome,
                        observed_outcome="fail", observed_reasons=[f"builder_error:{exc}"],
                        validator_outcome="error", validator_reasons=[],
                        matched=False, coverage_gap=False, coverage_gap_kind="",
                        duration_ms=0,
                    )
                )
                mismatch_ids.append(case_id)
                continue

            write_fixtures(sandbox_root, fixtures)

            t0 = time.monotonic()
            observed_outcome, observed_reasons, validator_outcome, validator_reasons = (
                comprehensive_check(sandbox_root)
            )
            t1 = time.monotonic()
            duration_ms = int((t1 - t0) * 1000)

            if observed_outcome == "pass":
                observed_pass += 1
            else:
                observed_fail += 1

            matched = observed_outcome == spec.expected_outcome
            if not matched:
                mismatch_ids.append(case_id)

            coverage_gap = validator_outcome != observed_outcome
            coverage_gap_kind = ""
            if coverage_gap:
                # The augmentation that fired (first one) characterizes the gap.
                aug_only = [r for r in observed_reasons if r.startswith("augmentation:")
                            or r.startswith("secret_pattern:")
                            or r.startswith("dangerous_command:")
                            or r.startswith("pseudocode_marker:")]
                coverage_gap_kind = aug_only[0] if aug_only else "validator_only"
                coverage_gap_ids.append(case_id)

            cases.append(
                CaseResult(
                    case_id=case_id, sandbox_id=sandbox_id, rule_id=spec.rule_id,
                    category=spec.category, name=spec.name, variant=variant,
                    expected_outcome=spec.expected_outcome,
                    observed_outcome=observed_outcome, observed_reasons=observed_reasons,
                    validator_outcome=validator_outcome, validator_reasons=validator_reasons,
                    matched=matched, coverage_gap=coverage_gap, coverage_gap_kind=coverage_gap_kind,
                    duration_ms=duration_ms,
                )
            )

    duration_ms = int((time.monotonic() - started) * 1000)

    result = SandboxResult(
        sandbox_id=sandbox_id, sandbox_path=str(sandbox_root),
        total_checks=len(cases),
        expected_pass_count=expected_pass, expected_fail_count=expected_fail,
        observed_pass_count=observed_pass, observed_fail_count=observed_fail,
        mismatch_case_ids=mismatch_ids, coverage_gap_case_ids=coverage_gap_ids,
        case_ids=case_ids, cases=cases,
        duration_ms=duration_ms, repo_source_sha256=repo_fp,
    )
    return result


def _sandbox_worker(args: tuple[str, str]) -> dict:
    sandbox_id, repo_fp = args
    res = run_sandbox(sandbox_id, repo_fp)
    return _serialize_sandbox(res)


def _serialize_sandbox(res: SandboxResult) -> dict:
    payload = {
        "sandbox_id": res.sandbox_id,
        "sandbox_path": res.sandbox_path,
        "total_checks": res.total_checks,
        "expected_pass_count": res.expected_pass_count,
        "expected_fail_count": res.expected_fail_count,
        "observed_pass_count": res.observed_pass_count,
        "observed_fail_count": res.observed_fail_count,
        "mismatches": res.mismatch_case_ids,
        "case_ids": res.case_ids,
        "duration_ms": res.duration_ms,
        "repo_source_sha256": res.repo_source_sha256,
        "report_sha256": "",
        "cases": [asdict(c) for c in res.cases],
    }
    return payload


def _compute_report_sha256(payload: dict) -> str:
    payload_for_hash = dict(payload)
    payload_for_hash["report_sha256"] = ""
    serialized = json.dumps(payload_for_hash, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(serialized).hexdigest()


# ---- Aggregation + reports -----------------------------------------------


def aggregate(sandboxes: list[dict]) -> dict:
    total_checks = sum(s["total_checks"] for s in sandboxes)
    total_expected_pass = sum(s["expected_pass_count"] for s in sandboxes)
    total_expected_fail = sum(s["expected_fail_count"] for s in sandboxes)
    total_observed_pass = sum(s["observed_pass_count"] for s in sandboxes)
    total_observed_fail = sum(s["observed_fail_count"] for s in sandboxes)
    total_mismatches = sum(len(s["mismatches"]) for s in sandboxes)
    coverage_gap_count = sum(
        sum(1 for c in s["cases"] if c["coverage_gap"]) for s in sandboxes
    )

    # Cross-sandbox identity per rule_id+variant.
    cross_identity: dict[str, bool] = {}
    by_rule: dict[str, list[str]] = {}
    for s in sandboxes:
        for c in s["cases"]:
            key = f"{c['rule_id']}-V{c['variant']}"
            by_rule.setdefault(key, []).append(c["observed_outcome"])
    for key, verdicts in by_rule.items():
        cross_identity[key] = len(set(verdicts)) == 1

    # J property checks.
    j_failures: list[str] = []
    if total_checks != 900:
        j_failures.append(f"J6:total_checks={total_checks}, expected 900")
    if any(not v for v in cross_identity.values()):
        diverged = [k for k, v in cross_identity.items() if not v]
        j_failures.append(f"J4_or_J5:cross_sandbox_divergence:{diverged}")
    sandbox_paths = [s["sandbox_path"] for s in sandboxes]
    if len(set(sandbox_paths)) != len(sandbox_paths):
        j_failures.append("J2:sandbox_paths_overlap")
    for s in sandboxes:
        if not s.get("report_sha256", "").startswith("sha256:"):
            j_failures.append(f"J9:missing_report_sha256:{s['sandbox_id']}")

    failing_case_ids: list[str] = []
    for s in sandboxes:
        failing_case_ids.extend(s["mismatches"])
    failing_case_ids.sort()

    aggregate = {
        "total_checks": total_checks,
        "total_expected_pass": total_expected_pass,
        "total_expected_fail": total_expected_fail,
        "total_observed_pass": total_observed_pass,
        "total_observed_fail": total_observed_fail,
        "total_mismatches": total_mismatches,
        "coverage_gap_count": coverage_gap_count,
        "cross_sandbox_identity": cross_identity,
        "aggregation_failures": j_failures,
        "per_sandbox": [
            {
                "sandbox_id": s["sandbox_id"],
                "report_sha256": s["report_sha256"],
                "total_checks": s["total_checks"],
                "mismatches": s["mismatches"],
            }
            for s in sandboxes
        ],
        "failing_case_ids": failing_case_ids,
    }
    return aggregate


def write_aggregate_md(agg: dict, started_at: str, finished_at: str, duration_ms: int) -> str:
    lines: list[str] = []
    lines.append("# Workforce Sandbox Stress — Aggregate Report")
    lines.append("")
    lines.append(f"- started_at: `{started_at}`")
    lines.append(f"- finished_at: `{finished_at}`")
    lines.append(f"- duration_ms: `{duration_ms}`")
    lines.append(f"- total_checks: `{agg['total_checks']}`")
    lines.append(f"- total_expected_pass: `{agg['total_expected_pass']}`")
    lines.append(f"- total_expected_fail: `{agg['total_expected_fail']}`")
    lines.append(f"- total_observed_pass: `{agg['total_observed_pass']}`")
    lines.append(f"- total_observed_fail: `{agg['total_observed_fail']}`")
    lines.append(f"- total_mismatches: `{agg['total_mismatches']}`")
    lines.append(f"- coverage_gap_count: `{agg['coverage_gap_count']}`")
    lines.append("")
    lines.append("## Per-sandbox")
    for s in agg["per_sandbox"]:
        lines.append(
            f"- {s['sandbox_id']}: total={s['total_checks']}, "
            f"mismatches={len(s['mismatches'])}, sha256={s['report_sha256']}"
        )
    lines.append("")
    lines.append("## Cross-sandbox identity")
    diverged = [k for k, v in agg["cross_sandbox_identity"].items() if not v]
    if not diverged:
        lines.append(f"All {len(agg['cross_sandbox_identity'])} (rule, variant) pairs agreed across all three sandboxes.")
    else:
        lines.append(f"{len(diverged)} divergence(s) detected:")
        for k in diverged[:25]:
            lines.append(f"- {k}")
    lines.append("")
    lines.append("## Aggregation failures")
    if not agg["aggregation_failures"]:
        lines.append("None.")
    else:
        for f in agg["aggregation_failures"]:
            lines.append(f"- {f}")
    lines.append("")
    lines.append("## First 25 failing case IDs")
    if not agg["failing_case_ids"]:
        lines.append("None.")
    else:
        for cid in agg["failing_case_ids"][:25]:
            lines.append(f"- `{cid}`")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Workforce sandbox stress suite.")
    parser.add_argument("--preserve-sandboxes", action="store_true",
                        help="do not remove sandbox temp directories on exit")
    parser.add_argument("--sequential", action="store_true",
                        help="run sandboxes sequentially instead of in parallel")
    args = parser.parse_args(argv)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    repo_fp = repo_source_fingerprint()
    started_at_dt = _dt.datetime.now(_dt.timezone.utc)
    started_at = started_at_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    t0 = time.monotonic()

    if args.sequential:
        sandboxes = [_sandbox_worker((sid, repo_fp)) for sid in SANDBOX_NAMES]
    else:
        with ProcessPoolExecutor(max_workers=len(SANDBOX_NAMES)) as ex:
            sandboxes = list(
                ex.map(_sandbox_worker, [(sid, repo_fp) for sid in SANDBOX_NAMES])
            )

    # Compute per-sandbox report SHA-256 with the field zeroed during hashing.
    for s in sandboxes:
        s["report_sha256"] = _compute_report_sha256(s)
        out_path = REPORTS_DIR / f"{s['sandbox_id']}.json"
        out_path.write_text(
            json.dumps(s, sort_keys=True, separators=(",", ":"), indent=2),
            encoding="utf-8",
        )

    finished_at_dt = _dt.datetime.now(_dt.timezone.utc)
    finished_at = finished_at_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    duration_ms = int((time.monotonic() - t0) * 1000)

    agg = aggregate(sandboxes)
    agg["started_at"] = started_at
    agg["finished_at"] = finished_at
    agg["duration_ms"] = duration_ms

    (REPORTS_DIR / "aggregate.json").write_text(
        json.dumps(agg, sort_keys=True, separators=(",", ":"), indent=2),
        encoding="utf-8",
    )
    (REPORTS_DIR / "aggregate.md").write_text(
        write_aggregate_md(agg, started_at, finished_at, duration_ms),
        encoding="utf-8",
    )

    # Cleanup sandboxes unless preserved.
    if not args.preserve_sandboxes:
        for s in sandboxes:
            sp = Path(s["sandbox_path"])
            if sp.exists():
                shutil.rmtree(sp, ignore_errors=True)

    suite_passed = (
        agg["total_mismatches"] == 0
        and not agg["aggregation_failures"]
    )
    if suite_passed:
        print(
            f"workforce-stress: OK ({agg['total_checks']} checks, "
            f"coverage_gap={agg['coverage_gap_count']}, duration_ms={duration_ms})."
        )
        return 0
    print("workforce-stress: FAIL")
    print(f"  total_checks={agg['total_checks']}")
    print(f"  total_mismatches={agg['total_mismatches']}")
    print(f"  aggregation_failures={agg['aggregation_failures']}")
    print(f"  first_failing_case_ids={agg['failing_case_ids'][:25]}")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
