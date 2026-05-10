#!/usr/bin/env python3
"""WiseOrder/Intellagent — workforce records validator.

Validates the on-disk workforce records produced under WORKFORCE-EXECUTION-RUNTIME-v0.1.

Checks performed (in order):

  1. Required directory layout exists (workforce/, work_orders/{open,closed,rejected}/,
     action_logs/, templates/, reports/) plus the three required templates.
  2. Every YAML file under workforce/work_orders/ parses and carries the required
     work-order fields per WORKFORCE-EXECUTION-RUNTIME-v0.1 §4 and §7.
  3. Every YAML file under workforce/action_logs/ parses and carries the required
     action-log fields per §8.
  4. For every work order in work_orders/closed/:
       - a matching action log exists in action_logs/ (referenced by work_order_id)
       - the action log's files_changed is a subset of the work order's allowed_files
         (path-equality or glob match)
       - the action log records no file from the work order's forbidden_files in
         either files_read or files_changed
       - the action log's gates_passed covers every entry in the work order's
         required_gates (set inclusion)
       - the action log references a self-verification block file that exists
       - if human_approval_required is true, status_history contains an entry whose
         state is "closed" with a non-empty actor

Exit codes:
  0 — clean
  1 — at least one violation
  2 — usage or environment error

This script does not mutate any file. It does not require PyYAML; it parses the
restricted flat-YAML subset that the workforce templates use (top-level scalars
and top-level lists of scalars).
"""

from __future__ import annotations

import argparse
import fnmatch
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFORCE_DIR = REPO_ROOT / "workforce"
WO_OPEN_DIR = WORKFORCE_DIR / "work_orders" / "open"
WO_CLOSED_DIR = WORKFORCE_DIR / "work_orders" / "closed"
WO_REJECTED_DIR = WORKFORCE_DIR / "work_orders" / "rejected"
ACTION_LOG_DIR = WORKFORCE_DIR / "action_logs"
TEMPLATES_DIR = WORKFORCE_DIR / "templates"
REPORTS_DIR = WORKFORCE_DIR / "reports"

REQUIRED_DIRS: tuple[Path, ...] = (
    WORKFORCE_DIR,
    WO_OPEN_DIR,
    WO_CLOSED_DIR,
    WO_REJECTED_DIR,
    ACTION_LOG_DIR,
    TEMPLATES_DIR,
    REPORTS_DIR,
)

REQUIRED_TEMPLATES: tuple[Path, ...] = (
    TEMPLATES_DIR / "work_order.yaml",
    TEMPLATES_DIR / "action_log.yaml",
    TEMPLATES_DIR / "self_verification.md",
)

WORK_ORDER_REQUIRED_FIELDS: tuple[str, ...] = (
    "work_order_id",
    "agent_role",
    "objective",
    "allowed_files",
    "forbidden_files",
    "constraints",
    "expected_outputs",
    "required_gates",
    "rollback_plan",
    "human_approval_required",
    "status",
)

ACTION_LOG_REQUIRED_FIELDS: tuple[str, ...] = (
    "action_id",
    "work_order_id",
    "agent_role",
    "timestamp_start",
    "timestamp_end",
    "files_read",
    "files_changed",
    "commands_run",
    "command_outputs_summary",
    "gates_passed",
    "gates_failed",
    "deviations",
    "risk_notes",
    "rollback_notes",
    "self_verification_statement",
)

TEMPLATE_PLACEHOLDER_IDS: frozenset[str] = frozenset(
    {"WO-YYYY-MM-DD-NNN", "AL-YYYY-MM-DD-NNN"}
)


@dataclass
class Violation:
    path: Path
    rule: str
    message: str

    def render(self) -> str:
        rel = self.path.relative_to(REPO_ROOT) if self.path.is_absolute() else self.path
        return f"  - [{self.rule}] {rel}: {self.message}"


@dataclass
class Record:
    path: Path
    fields: dict[str, object] = field(default_factory=dict)


def parse_flat_yaml(path: Path) -> dict[str, object]:
    """Parse the restricted flat-YAML subset used by workforce templates.

    Supports:
      - top-level scalars: ``key: value`` (value may be quoted with single or double quotes)
      - top-level booleans: ``key: true`` / ``key: false``
      - top-level lists of scalars where each item is on its own line as ``  - value``
      - blank lines and ``#`` comments

    Does not support nested mappings beyond a single level of list-of-mappings,
    which the validator does not need to interpret semantically (status_history
    entries are read as opaque strings).
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


def list_yaml_files(directory: Path) -> list[Path]:
    if not directory.exists():
        return []
    return sorted(p for p in directory.iterdir() if p.suffix == ".yaml" and p.is_file())


def is_template_placeholder(record: Record, id_field: str) -> bool:
    value = record.fields.get(id_field)
    return isinstance(value, str) and value in TEMPLATE_PLACEHOLDER_IDS


def check_layout() -> list[Violation]:
    violations: list[Violation] = []
    for directory in REQUIRED_DIRS:
        if not directory.is_dir():
            violations.append(
                Violation(directory, "missing_directory", "required workforce directory is absent")
            )
    for template in REQUIRED_TEMPLATES:
        if not template.is_file():
            violations.append(
                Violation(template, "missing_template", "required workforce template is absent")
            )
    return violations


def load_records(paths: list[Path], required_fields: tuple[str, ...]) -> tuple[list[Record], list[Violation]]:
    records: list[Record] = []
    violations: list[Violation] = []
    for path in paths:
        try:
            fields = parse_flat_yaml(path)
        except OSError as exc:
            violations.append(Violation(path, "unreadable_yaml", f"failed to read: {exc}"))
            continue
        record = Record(path=path, fields=fields)
        for required in required_fields:
            if required not in fields:
                violations.append(
                    Violation(path, "missing_field", f"required field absent: {required}")
                )
        records.append(record)
    return records, violations


def index_action_logs_by_work_order(action_logs: list[Record]) -> dict[str, list[Record]]:
    index: dict[str, list[Record]] = {}
    for record in action_logs:
        wo_id = record.fields.get("work_order_id")
        if isinstance(wo_id, str) and wo_id:
            index.setdefault(wo_id, []).append(record)
    return index


def files_match(candidate: str, patterns: list[str]) -> bool:
    candidate = candidate.strip()
    if not candidate:
        return False
    for pattern in patterns:
        pattern = pattern.strip()
        if not pattern:
            continue
        if candidate == pattern:
            return True
        if fnmatch.fnmatch(candidate, pattern):
            return True
    return False


def split_change_kind(entry: str) -> str:
    return entry.strip().split(" ", 1)[0]


def check_closure(
    work_order: Record,
    action_logs_for_wo: list[Record],
) -> list[Violation]:
    violations: list[Violation] = []
    wo_id = work_order.fields.get("work_order_id")

    if not action_logs_for_wo:
        violations.append(
            Violation(
                work_order.path,
                "missing_action_log",
                f"closed work order {wo_id} has no matching action log",
            )
        )
        return violations

    allowed = _as_str_list(work_order.fields.get("allowed_files"))
    forbidden = _as_str_list(work_order.fields.get("forbidden_files"))
    required_gates = set(_as_str_list(work_order.fields.get("required_gates")))

    for action_log in action_logs_for_wo:
        files_changed = _as_str_list(action_log.fields.get("files_changed"))
        files_read = _as_str_list(action_log.fields.get("files_read"))
        gates_passed = set(_as_str_list(action_log.fields.get("gates_passed")))

        for entry in files_changed:
            path_part = split_change_kind(entry)
            if not path_part:
                continue
            if not files_match(path_part, allowed):
                violations.append(
                    Violation(
                        action_log.path,
                        "out_of_scope_change",
                        f"files_changed entry '{path_part}' is not covered by allowed_files in {wo_id}",
                    )
                )
            if files_match(path_part, forbidden):
                violations.append(
                    Violation(
                        action_log.path,
                        "forbidden_file_touched",
                        f"files_changed entry '{path_part}' is in forbidden_files of {wo_id}",
                    )
                )

        for read_path in files_read:
            read_path = read_path.strip()
            if not read_path:
                continue
            if files_match(read_path, forbidden):
                violations.append(
                    Violation(
                        action_log.path,
                        "forbidden_file_read",
                        f"files_read entry '{read_path}' is in forbidden_files of {wo_id}",
                    )
                )

        missing_gates = sorted(g for g in required_gates if g and g not in gates_passed)
        if missing_gates:
            violations.append(
                Violation(
                    action_log.path,
                    "required_gate_missing",
                    f"required gates not in gates_passed: {missing_gates}",
                )
            )

        sv_ref = action_log.fields.get("self_verification_statement")
        if isinstance(sv_ref, str) and sv_ref.strip():
            sv_path = (REPO_ROOT / sv_ref.strip()).resolve()
            if not sv_path.exists():
                violations.append(
                    Violation(
                        action_log.path,
                        "missing_self_verification",
                        f"self_verification_statement points to nonexistent file: {sv_ref}",
                    )
                )
        else:
            violations.append(
                Violation(
                    action_log.path,
                    "missing_self_verification",
                    "self_verification_statement field is empty",
                )
            )

    if work_order.fields.get("human_approval_required") is True:
        # The flat-YAML parser leaves status_history as an empty list (it is a list-of-mappings).
        # Closure approval is recorded inside the work-order YAML; we require the literal token
        # "closed" to appear in the file body, with a non-empty actor field nearby.
        text = work_order.path.read_text(encoding="utf-8")
        if not _has_closure_signoff(text):
            violations.append(
                Violation(
                    work_order.path,
                    "missing_human_approval",
                    "human_approval_required is true but no closure signoff with actor was found in status_history",
                )
            )

    return violations


def _as_str_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [v if isinstance(v, str) else str(v) for v in value]
    if value is None:
        return []
    return [str(value)]


def _has_closure_signoff(text: str) -> bool:
    in_history = False
    saw_closed_state = False
    saw_actor = False
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if line.strip().startswith("status_history"):
            in_history = True
            continue
        if not in_history:
            continue
        stripped = line.strip()
        if stripped.startswith("- state:"):
            saw_closed_state = "closed" in stripped
            saw_actor = False
            continue
        if saw_closed_state and stripped.startswith("actor:"):
            value = stripped.split(":", 1)[1].strip().strip("'\"")
            if value:
                saw_actor = True
        if saw_closed_state and saw_actor:
            return True
    return False


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Validate workforce records per WORKFORCE-EXECUTION-RUNTIME-v0.1."
    )
    parser.add_argument(
        "--quiet", action="store_true", help="suppress success output; print only violations."
    )
    args = parser.parse_args(argv)

    violations: list[Violation] = []

    layout_violations = check_layout()
    violations.extend(layout_violations)
    if layout_violations:
        _emit(violations)
        return 1

    open_paths = list_yaml_files(WO_OPEN_DIR)
    closed_paths = list_yaml_files(WO_CLOSED_DIR)
    rejected_paths = list_yaml_files(WO_REJECTED_DIR)
    action_log_paths = list_yaml_files(ACTION_LOG_DIR)

    work_orders, wo_field_violations = load_records(
        open_paths + closed_paths + rejected_paths, WORK_ORDER_REQUIRED_FIELDS
    )
    action_logs, al_field_violations = load_records(action_log_paths, ACTION_LOG_REQUIRED_FIELDS)

    work_orders = [r for r in work_orders if not is_template_placeholder(r, "work_order_id")]
    action_logs = [r for r in action_logs if not is_template_placeholder(r, "action_id")]

    violations.extend(wo_field_violations)
    violations.extend(al_field_violations)

    al_index = index_action_logs_by_work_order(action_logs)

    closed_records = [r for r in work_orders if r.path.parent == WO_CLOSED_DIR]
    for work_order in closed_records:
        wo_id = work_order.fields.get("work_order_id")
        matching_logs = al_index.get(wo_id, []) if isinstance(wo_id, str) else []
        violations.extend(check_closure(work_order, matching_logs))

    if violations:
        print("workforce-check: VIOLATIONS")
        for v in violations:
            print(v.render())
        print(f"workforce-check: {len(violations)} violation(s) across {len(work_orders)} work order(s) and {len(action_logs)} action log(s).")
        return 1

    if not args.quiet:
        print(
            f"workforce-check: OK ({len(work_orders)} work order(s), "
            f"{len(action_logs)} action log(s), {len(closed_records)} closed)."
        )
    return 0


def _emit(violations: list[Violation]) -> None:
    print("workforce-check: VIOLATIONS")
    for v in violations:
        print(v.render())


# ---------------------------------------------------------------------------
# v0.2 hardening — augmentation rules migrated from the sandbox stress suite.
#
# All checks below are additive. They do not weaken existing checks. They
# extend the validator's surface to catch governance violations that the
# stress suite previously surfaced only through external augmentation.
# Each rule cites its source category from WORKFORCE-HARDENING-v0.2.md.
# ---------------------------------------------------------------------------

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

CANON_PATH_MARKERS: tuple[str, ...] = ("SPEC.md", "vectors/", "canonicalization/")
INVARIANT_PATH_MARKERS: tuple[str, ...] = (
    "INTELLAGENT.md",
    "INTELLAGENT-RUNTIME.md",
    "CANONICAL-RELEASE-v0.1.md",
)
IMPL_PATH_MARKERS: tuple[str, ...] = ("intellagent_runtime/",)
AUTHZ_PATH_MARKER = "intellagent_runtime/authorization"
REPLAY_PATH_MARKER = "intellagent_runtime/memory"

SECRET_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"AKIA[A-Z0-9]{16}", "aws_access_key"),
    (r"ghp_[A-Za-z0-9]{20,}", "github_personal_token"),
    (r"github_pat_[A-Za-z0-9_]{20,}", "github_fine_grained_pat"),
    (r"BEGIN [A-Z]+ PRIVATE KEY", "private_key_marker"),
)

PSEUDOCODE_LITERAL_MARKERS: tuple[str, ...] = (
    "TODO",
    "NotImplementedError",
    "NotImplemented",
)

DANGEROUS_COMMAND_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"\bsudo\b", "sudo"),
    (r"\bchmod\s+[0-7]+\s+/", "chmod_root_path"),
    (r"\bcurl\b", "curl"),
    (r"git\s+push\s+(--force|-f)\b", "git_force_push"),
    (r"git\s+rebase\b", "git_rebase"),
    (r"git\s+filter-branch\b", "git_filter_branch"),
)
RM_RF_PATTERN = re.compile(r"\brm\s+-rf\s+(\S+)")
TEMP_PATH_PREFIXES: tuple[str, ...] = ("/tmp/", "/var/folders/", "/private/tmp/")
AUDIT_DELETE_PATTERNS: tuple[str, ...] = (
    r"rm\s+\S*workforce/action_logs/",
    r"rm\s+\S*workforce/reports/",
)


def _scan_text_for_secrets(path: Path, text: str) -> list[Violation]:
    findings: list[Violation] = []
    for pattern, name in SECRET_PATTERNS:
        if re.search(pattern, text):
            findings.append(
                Violation(path, "security_secret_pattern", f"detected: {name}")
            )
    return findings


def _scan_text_for_pseudocode(path: Path, text: str) -> list[Violation]:
    findings: list[Violation] = []
    for marker in PSEUDOCODE_LITERAL_MARKERS:
        if marker in text:
            findings.append(
                Violation(path, "pseudocode_marker_in_yaml", f"contains: {marker}")
            )
    if re.search(r"^\s*\.\.\.\s*$", text, re.MULTILINE):
        findings.append(
            Violation(path, "pseudocode_marker_in_yaml", "ellipsis statement on its own line")
        )
    if re.search(r"\breturn\s+\.\.\.", text):
        findings.append(
            Violation(path, "pseudocode_marker_in_yaml", "return ellipsis pattern")
        )
    return findings


def _scan_command_for_danger(path: Path, cmd: str) -> list[Violation]:
    findings: list[Violation] = []
    for pattern, name in DANGEROUS_COMMAND_PATTERNS:
        if re.search(pattern, cmd):
            findings.append(
                Violation(
                    path,
                    "security_dangerous_command",
                    f"detected: {name} in commands_run entry: {cmd!r}",
                )
            )
    m = RM_RF_PATTERN.search(cmd)
    if m:
        target = m.group(1)
        if not any(target.startswith(p) for p in TEMP_PATH_PREFIXES):
            findings.append(
                Violation(
                    path,
                    "security_dangerous_command",
                    f"detected: rm_rf_outside_temp on '{target}' (allowed prefixes: {TEMP_PATH_PREFIXES})",
                )
            )
    for pattern in AUDIT_DELETE_PATTERNS:
        if re.search(pattern, cmd):
            findings.append(
                Violation(
                    path,
                    "security_dangerous_command",
                    f"detected: audit_artifact_delete in commands_run entry: {cmd!r}",
                )
            )
    return findings


def _extract_status_history_states(text: str) -> list[str]:
    states: list[str] = []
    in_history = False
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if line.strip().startswith("status_history"):
            in_history = True
            continue
        if not in_history:
            continue
        m = re.match(r'\s*-\s*state:\s*"?([^"#\n]+?)"?\s*$', line)
        if m:
            states.append(m.group(1).strip())
    return states


def _split_change_kind(entry: str) -> str:
    return entry.strip().split(" ", 1)[0]


def _entry_matches_marker(entry: str, markers: tuple[str, ...]) -> bool:
    path_part = _split_change_kind(entry)
    if not path_part:
        return False
    return any(m in path_part for m in markers)


def _allowed_files_includes_marker(allowed: list[str], markers: tuple[str, ...]) -> bool:
    return any(any(m in a for m in markers) for a in allowed)


def run_augmentations(
    work_orders: list[Record],
    action_logs: list[Record],
) -> list[Violation]:
    violations: list[Violation] = []
    seen_wo_ids: dict[str, list[str]] = {}
    seen_al_ids: dict[str, list[str]] = {}
    wo_required_gates: dict[str, list[str]] = {}
    wo_records_by_id: dict[str, Record] = {}

    # Per-work-order checks.
    for wo in work_orders:
        text = wo.path.read_text(encoding="utf-8")
        status_dir = wo.path.parent.name  # "open" | "closed" | "rejected"

        # Status enum.
        status = wo.fields.get("status")
        if isinstance(status, str) and status and status not in VALID_STATUSES:
            violations.append(
                Violation(wo.path, "lifecycle_invalid_status", f"status={status!r} not in valid enum")
            )

        # Status / directory consistency.
        if isinstance(status, str) and status:
            expected_dir = (
                "closed" if status == "closed"
                else "rejected" if status == "rejected"
                else "open"
            )
            if status_dir != expected_dir:
                violations.append(
                    Violation(
                        wo.path,
                        "lifecycle_status_directory_mismatch",
                        f"status={status!r} but file is in '{status_dir}/' (expected '{expected_dir}/')",
                    )
                )

        # Agent role enum.
        role = wo.fields.get("agent_role")
        if isinstance(role, str) and role and role not in VALID_AGENT_ROLES:
            violations.append(
                Violation(wo.path, "lifecycle_invalid_agent_role", f"agent_role={role!r} not in valid enum")
            )

        # Lifecycle order + continuity.
        history_states = _extract_status_history_states(text)
        if isinstance(status, str) and status in {"closed", "human_approved"}:
            if "drafted" not in history_states or "approved" not in history_states:
                violations.append(
                    Violation(
                        wo.path,
                        "lifecycle_missing_initial_states",
                        "status_history must contain at minimum 'drafted' and 'approved' before reaching closed/human_approved",
                    )
                )
        if history_states:
            ranks = [LIFECYCLE_RANK.get(s, -1) for s in history_states]
            if any(r == -1 for r in ranks):
                bad = [s for s, r in zip(history_states, ranks) if r == -1]
                violations.append(
                    Violation(
                        wo.path,
                        "lifecycle_unknown_state",
                        f"status_history entries not in lifecycle: {bad}",
                    )
                )
            else:
                for i in range(1, len(ranks)):
                    if ranks[i] < ranks[i - 1]:
                        violations.append(
                            Violation(
                                wo.path,
                                "lifecycle_out_of_order",
                                f"status_history non-monotonic at index {i}: '{history_states[i-1]}' (rank {ranks[i-1]}) -> '{history_states[i]}' (rank {ranks[i]})",
                            )
                        )
                        break
        # Duplicate terminal states.
        terminal_seen = [s for s in history_states if s in {"closed", "rejected"}]
        if len(terminal_seen) > 1 and len(set(terminal_seen)) == len(terminal_seen):
            violations.append(
                Violation(
                    wo.path,
                    "lifecycle_duplicate_terminal_state",
                    f"multiple terminal states recorded: {terminal_seen}",
                )
            )

        # Track for duplicate-id check + downstream lookup.
        wo_id = wo.fields.get("work_order_id")
        if isinstance(wo_id, str) and wo_id:
            seen_wo_ids.setdefault(wo_id, []).append(status_dir)
            wo_records_by_id[wo_id] = wo
            wo_required_gates[wo_id] = _as_str_list(wo.fields.get("required_gates"))

        # Secret + pseudocode scans on YAML body.
        violations.extend(_scan_text_for_secrets(wo.path, text))
        violations.extend(_scan_text_for_pseudocode(wo.path, text))

        # Reviewer signoff + closure summary file checks (closed only).
        if status_dir == "closed":
            expected_outputs = _as_str_list(wo.fields.get("expected_outputs"))
            for out in expected_outputs:
                out = out.strip()
                if not out:
                    continue
                if out.endswith("/review.md") or out.endswith("review.md"):
                    if not (REPO_ROOT / out).exists():
                        violations.append(
                            Violation(
                                wo.path,
                                "lifecycle_reviewer_signoff_missing",
                                f"expected_outputs declares {out!r} but file is absent",
                            )
                        )
                if out.endswith("-closure-summary.md"):
                    if not (REPO_ROOT / out).exists():
                        violations.append(
                            Violation(
                                wo.path,
                                "lifecycle_closure_summary_missing",
                                f"expected_outputs declares {out!r} but file is absent",
                            )
                        )

    # Per-action-log checks.
    for al in action_logs:
        text = al.path.read_text(encoding="utf-8")

        action_id = al.fields.get("action_id")
        if isinstance(action_id, str) and action_id:
            seen_al_ids.setdefault(action_id, []).append(al.path.name)

        role = al.fields.get("agent_role")
        if isinstance(role, str) and role and role not in VALID_AGENT_ROLES:
            violations.append(
                Violation(al.path, "lifecycle_invalid_agent_role", f"agent_role={role!r} not in valid enum")
            )

        # Secret + pseudocode scans.
        violations.extend(_scan_text_for_secrets(al.path, text))
        violations.extend(_scan_text_for_pseudocode(al.path, text))

        # Dangerous command scans.
        for cmd in _as_str_list(al.fields.get("commands_run")):
            violations.extend(_scan_command_for_danger(al.path, cmd))

        # Gate output presence.
        gates_passed = _as_str_list(al.fields.get("gates_passed"))
        outputs = _as_str_list(al.fields.get("command_outputs_summary"))
        non_empty_outputs = [o for o in outputs if o.strip()]
        if gates_passed and len(non_empty_outputs) < len(gates_passed):
            violations.append(
                Violation(
                    al.path,
                    "gate_output_missing",
                    f"gates_passed has {len(gates_passed)} entries but command_outputs_summary has only {len(non_empty_outputs)} non-empty entries",
                )
            )

        # Gate consistency.
        gates_failed_set = set(_as_str_list(al.fields.get("gates_failed")))
        overlap = sorted(set(gates_passed) & gates_failed_set)
        if overlap:
            violations.append(
                Violation(
                    al.path,
                    "gate_in_passed_and_failed",
                    f"gates appear in both gates_passed and gates_failed: {overlap}",
                )
            )

        # Gate order: gates_passed order must match the work order's required_gates
        # order when both lists hold the same set.
        wo_ref = al.fields.get("work_order_id")
        if isinstance(wo_ref, str) and wo_ref in wo_required_gates:
            req = wo_required_gates[wo_ref]
            if (
                req
                and gates_passed
                and len(gates_passed) == len(req)
                and set(gates_passed) == set(req)
                and list(gates_passed) != list(req)
            ):
                violations.append(
                    Violation(
                        al.path,
                        "gate_order_violation",
                        f"gates_passed order {gates_passed} differs from required_gates order {req}",
                    )
                )

        # Action log orphan: references a work_order_id that does not exist.
        if isinstance(wo_ref, str) and wo_ref and wo_ref not in seen_wo_ids:
            violations.append(
                Violation(
                    al.path,
                    "action_log_orphan",
                    f"references work_order_id={wo_ref!r} but no work order with that id was found",
                )
            )

        # Undocumented deviation: a forbidden read recorded but deviations is empty.
        # Only fires when the work order it references actually forbids the read path.
        if isinstance(wo_ref, str) and wo_ref in wo_records_by_id:
            wo_for_al = wo_records_by_id[wo_ref]
            forbidden = _as_str_list(wo_for_al.fields.get("forbidden_files"))
            files_read = _as_str_list(al.fields.get("files_read"))
            deviations = [d for d in _as_str_list(al.fields.get("deviations")) if d.strip()]
            forbidden_read = False
            for fr in files_read:
                fr = fr.strip()
                if not fr:
                    continue
                for fp in forbidden:
                    fp = fp.strip()
                    if not fp:
                        continue
                    if fr == fp or fnmatch.fnmatch(fr, fp):
                        forbidden_read = True
                        break
                if forbidden_read:
                    break
            if forbidden_read and not deviations:
                violations.append(
                    Violation(
                        al.path,
                        "undocumented_deviation",
                        "files_read includes a forbidden_files entry but deviations field is empty",
                    )
                )

    # Cross-record checks.
    for wo_id, dirs in seen_wo_ids.items():
        if len(dirs) > 1:
            violations.append(
                Violation(
                    Path(f"<duplicate>/{wo_id}"),
                    "duplicate_work_order_id",
                    f"work_order_id={wo_id!r} appears in multiple directories: {dirs}",
                )
            )
    for al_id, files in seen_al_ids.items():
        if len(files) > 1:
            violations.append(
                Violation(
                    Path(f"<duplicate>/{al_id}"),
                    "duplicate_action_id",
                    f"action_id={al_id!r} appears in multiple files: {files}",
                )
            )

    # Canon-discipline checks (per work order).
    for wo in work_orders:
        text = wo.path.read_text(encoding="utf-8")
        wo_id = wo.fields.get("work_order_id")
        allowed = _as_str_list(wo.fields.get("allowed_files"))
        role = wo.fields.get("agent_role")

        # Find action logs that reference this work order.
        al_files_changed: list[str] = []
        for al in action_logs:
            if al.fields.get("work_order_id") == wo_id:
                al_files_changed.extend(_as_str_list(al.fields.get("files_changed")))

        # Canon-touch + role enforcement.
        canon_touch = any(_entry_matches_marker(e, CANON_PATH_MARKERS) for e in al_files_changed)
        if canon_touch and isinstance(role, str) and role in {"builder", "test", "docs"}:
            violations.append(
                Violation(
                    wo.path,
                    "canon_touched_by_unauthorized_role",
                    f"role={role!r} touched canon path; only canon_guardian (proposing) plus human-owner approval may modify canon",
                )
            )

        # Canon change without CANON BREAK marker in work-order body.
        if canon_touch and "CANON BREAK" not in text:
            violations.append(
                Violation(
                    wo.path,
                    "canon_change_missing_canon_break",
                    "files_changed includes a canon path but work order body does not declare 'CANON BREAK'",
                )
            )

        # Invariant change without human approval.
        invariant_touch = any(
            _entry_matches_marker(e, INVARIANT_PATH_MARKERS) for e in al_files_changed
        )
        if invariant_touch:
            human_required = wo.fields.get("human_approval_required")
            if str(human_required).lower() != "true":
                violations.append(
                    Violation(
                        wo.path,
                        "invariant_change_without_human_approval",
                        "files_changed includes an invariant document but human_approval_required is not true",
                    )
                )

        # Authorization semantics change must be by security role.
        auth_touch = any(AUTHZ_PATH_MARKER in _split_change_kind(e) for e in al_files_changed)
        if auth_touch and isinstance(role, str) and role != "security":
            violations.append(
                Violation(
                    wo.path,
                    "authorization_change_wrong_role",
                    f"authorization-path change attempted by role={role!r}; only 'security' role may propose this change",
                )
            )

        # Replay semantics change must be by security or release role.
        replay_touch = any(REPLAY_PATH_MARKER in _split_change_kind(e) for e in al_files_changed)
        if replay_touch and isinstance(role, str) and role not in {"security", "release"}:
            violations.append(
                Violation(
                    wo.path,
                    "replay_change_wrong_role",
                    f"replay-path change attempted by role={role!r}; only 'security' or 'release' role may propose this change",
                )
            )

        # Canon + implementation in one work order.
        has_canon_in_allowed = _allowed_files_includes_marker(allowed, CANON_PATH_MARKERS)
        has_impl_in_allowed = _allowed_files_includes_marker(allowed, IMPL_PATH_MARKERS)
        if has_canon_in_allowed and has_impl_in_allowed:
            violations.append(
                Violation(
                    wo.path,
                    "canon_plus_implementation",
                    "allowed_files includes both canon paths and implementation paths; canon and implementation may not change in the same work order",
                )
            )

    return violations


# Re-export the original main with augmentations integrated.
_original_main = main


def main(argv: list[str]) -> int:  # noqa: F811 — intentional override
    parser = argparse.ArgumentParser(
        description="Validate workforce records per WORKFORCE-EXECUTION-RUNTIME-v0.1 plus WORKFORCE-HARDENING-v0.2."
    )
    parser.add_argument(
        "--quiet", action="store_true", help="suppress success output; print only violations."
    )
    parser.add_argument(
        "--no-augmentations", action="store_true",
        help="skip v0.2 hardening augmentations (legacy mode; not recommended).",
    )
    args = parser.parse_args(argv)

    violations: list[Violation] = []

    layout_violations = check_layout()
    violations.extend(layout_violations)
    if layout_violations:
        _emit(violations)
        return 1

    open_paths = list_yaml_files(WO_OPEN_DIR)
    closed_paths = list_yaml_files(WO_CLOSED_DIR)
    rejected_paths = list_yaml_files(WO_REJECTED_DIR)
    action_log_paths = list_yaml_files(ACTION_LOG_DIR)

    work_orders, wo_field_violations = load_records(
        open_paths + closed_paths + rejected_paths, WORK_ORDER_REQUIRED_FIELDS
    )
    action_logs, al_field_violations = load_records(action_log_paths, ACTION_LOG_REQUIRED_FIELDS)

    work_orders = [r for r in work_orders if not is_template_placeholder(r, "work_order_id")]
    action_logs = [r for r in action_logs if not is_template_placeholder(r, "action_id")]

    violations.extend(wo_field_violations)
    violations.extend(al_field_violations)

    al_index = index_action_logs_by_work_order(action_logs)

    closed_records = [r for r in work_orders if r.path.parent == WO_CLOSED_DIR]
    for work_order in closed_records:
        wo_id = work_order.fields.get("work_order_id")
        matching_logs = al_index.get(wo_id, []) if isinstance(wo_id, str) else []
        violations.extend(check_closure(work_order, matching_logs))

    if not args.no_augmentations:
        violations.extend(run_augmentations(work_orders, action_logs))

    if violations:
        print("workforce-check: VIOLATIONS")
        for v in violations:
            print(v.render())
        print(f"workforce-check: {len(violations)} violation(s) across {len(work_orders)} work order(s) and {len(action_logs)} action log(s).")
        return 1

    if not args.quiet:
        print(
            f"workforce-check: OK ({len(work_orders)} work order(s), "
            f"{len(action_logs)} action log(s), {len(closed_records)} closed)."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
