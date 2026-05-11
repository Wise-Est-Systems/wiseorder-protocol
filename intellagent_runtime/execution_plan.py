"""Execution-plan builder for the WiseOrder runtime core.

Given a parsed :class:`~intellagent_runtime.work_order_parser.WorkOrder`,
this module produces an :class:`ExecutionPlan` describing how the runtime
intends to act on it. The plan does not execute anything; it expresses
intent in a form the governance layer can validate before any side
effect is permitted.

Validation rules (raise :class:`ExecutionPlanError` or returned via
:meth:`ExecutionPlan.validate`):

  - every required command must be present in the plan
  - no command may touch a forbidden / protected path
  - unbounded shell commands are rejected
  - destructive commands without explicit permission are rejected
  - the plan must include a verification step
  - the plan must include a report step
"""

from __future__ import annotations

import re
import shlex
from dataclasses import dataclass, field
from pathlib import Path

from intellagent_runtime.work_order_parser import WorkOrder
from intellagent_runtime.workflow_grammar import Stage, Workflow, parse_workflow_from_text


class ExecutionPlanError(ValueError):
    """Raised when an execution plan is impossible to construct or fails
    validation."""


# ---------------------------------------------------------------------------
# Command classification
# ---------------------------------------------------------------------------


# Programs that mutate or delete state. Their presence in a plan requires
# an explicit permission rule in the originating work order.
_DESTRUCTIVE_PROGRAMS: frozenset[str] = frozenset({
    "rm", "rmdir", "mv", "dd", "shred", "wipe",
    "mkfs", "fdisk", "format",
    "kill", "killall", "pkill",
})

# Destructive subcommand forms — a tuple of (program, first-arg substring).
_DESTRUCTIVE_SUBCOMMANDS: tuple[tuple[str, str], ...] = (
    ("git", "push --force"),
    ("git", "push -f"),
    ("git", "reset --hard"),
    ("git", "clean -fd"),
    ("git", "branch -D"),
    ("git", "checkout ."),
    ("git", "restore ."),
)

# Heuristics that mark an unbounded operation.
_UNBOUNDED_PATTERNS = (
    re.compile(r"\brm\s+-rf?\s+/"),
    re.compile(r"\bfind\s+/\b(?!.*-maxdepth)"),
    re.compile(r"\b:\s*\(\)\s*{\s*:\s*\|\s*:\s*&\s*}\s*;\s*:"),  # fork bomb
    re.compile(r"\bcurl\b.*\|\s*(bash|sh)\b"),
    re.compile(r"\bwget\b.*\|\s*(bash|sh)\b"),
    re.compile(r"\byes\b\s*(?:\||$)"),
)


def _looks_destructive(argv: list[str]) -> tuple[bool, str]:
    """Return (is_destructive, reason)."""
    if not argv:
        return False, ""
    head = Path(argv[0]).name.lower()
    if head in _DESTRUCTIVE_PROGRAMS:
        return True, f"destructive program {head!r}"
    rest = " ".join(argv[1:])
    for prog, needle in _DESTRUCTIVE_SUBCOMMANDS:
        if head == prog and needle in rest:
            return True, f"destructive subcommand {head!r} with {needle!r}"
    return False, ""


def _looks_unbounded(raw: str) -> tuple[bool, str]:
    for pat in _UNBOUNDED_PATTERNS:
        if pat.search(raw):
            return True, f"unbounded pattern matched: {pat.pattern!r}"
    return False, ""


def _command_argv(line: str) -> list[str]:
    """Best-effort argv tokenization that tolerates malformed shell text
    by falling back to whitespace split."""
    try:
        return shlex.split(line, posix=True)
    except ValueError:
        return line.split()


def _command_touches_path(line: str, path_glob: str) -> bool:
    """Conservative substring/regex match. We accept a path as
    'touched' if the command line literally mentions it, mentions its
    glob expansion form, or mentions its parent directory."""
    if not path_glob:
        return False
    # Strip the trailing /** or /* for substring matching.
    base = path_glob.rstrip("/")
    base = re.sub(r"/?\*+\Z", "", base).rstrip("/")
    if not base:
        return False
    # Build a regex that matches the path as a whole token (either by
    # word boundary or by being preceded by space / slash / quote).
    pattern = r"(^|[\s\"'/=])" + re.escape(base) + r"(/|[\s\"'])?"
    return bool(re.search(pattern, line))


def _explicit_destructive_permission(work_order: WorkOrder) -> bool:
    pool = " ".join(work_order.primary_rules + work_order.allowed_actions).lower()
    needles = (
        "explicit permission to destruct",
        "explicit permission for destructive",
        "destructive operations permitted",
        "may delete",
        "may force-push",
    )
    return any(n in pool for n in needles)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class PlannedCommand:
    """A single command the plan intends to execute (or describe).

    ``raw`` is the line as it appears in the work order.
    ``argv`` is the best-effort tokenization.
    ``stage`` indicates which workflow stage the command belongs to, if
    that can be inferred from the surrounding context.
    """

    raw: str
    argv: list[str] = field(default_factory=list)
    stage: Stage | None = None

    def to_dict(self) -> dict:
        return {
            "raw": self.raw,
            "argv": list(self.argv),
            "stage": self.stage.value if self.stage else None,
        }


@dataclass
class ExecutionPlan:
    """The intent surface produced from a :class:`WorkOrder`."""

    work_order_title: str = ""
    work_order_sha256: str = ""
    workflow: Workflow = field(default_factory=lambda: Workflow(stages=[]))
    planned_commands: list[PlannedCommand] = field(default_factory=list)
    allowed_paths: list[str] = field(default_factory=list)
    forbidden_paths: list[str] = field(default_factory=list)
    protected_paths: list[str] = field(default_factory=list)
    required_commands: list[str] = field(default_factory=list)
    has_explicit_destructive_permission: bool = False

    # ---- validation ----

    def validate(self) -> list[str]:
        violations: list[str] = []

        # workflow must include verify and report.
        stage_set = {s for s in self.workflow.stages}
        if Stage.VERIFY not in stage_set:
            violations.append("plan has no verification step")
        if Stage.REPORT not in stage_set:
            violations.append("plan has no report step")

        # required commands must be planned.
        planned_raw = {c.raw.strip() for c in self.planned_commands}
        for required in self.required_commands:
            if required.strip() not in planned_raw:
                violations.append(f"required command not in plan: {required!r}")

        # Each planned command checked for forbidden paths, unbounded,
        # destructive without permission.
        forbidden_pool = list(self.protected_paths) + list(self.forbidden_paths)
        for cmd in self.planned_commands:
            for fp in forbidden_pool:
                if _command_touches_path(cmd.raw, fp):
                    violations.append(
                        f"command {cmd.raw!r} touches forbidden/protected path {fp!r}"
                    )
            unbounded, why = _looks_unbounded(cmd.raw)
            if unbounded:
                violations.append(f"command {cmd.raw!r} is unbounded: {why}")
            destructive, dwhy = _looks_destructive(cmd.argv)
            if destructive and not self.has_explicit_destructive_permission:
                violations.append(
                    f"command {cmd.raw!r} is destructive ({dwhy}) "
                    f"and the work order does not grant explicit permission"
                )
        return violations

    def is_valid(self) -> bool:
        return not self.validate()

    # ---- serialization ----

    def to_dict(self) -> dict:
        return {
            "work_order_title": self.work_order_title,
            "work_order_sha256": self.work_order_sha256,
            "workflow": [s.value for s in self.workflow.stages],
            "planned_commands": [c.to_dict() for c in self.planned_commands],
            "allowed_paths": list(self.allowed_paths),
            "forbidden_paths": list(self.forbidden_paths),
            "protected_paths": list(self.protected_paths),
            "required_commands": list(self.required_commands),
            "has_explicit_destructive_permission": self.has_explicit_destructive_permission,
        }


# ---------------------------------------------------------------------------
# Plan construction
# ---------------------------------------------------------------------------


def build_plan(work_order: WorkOrder) -> ExecutionPlan:
    """Convert a parsed work order into an :class:`ExecutionPlan`.

    The function never executes anything; it materializes intent.
    Callers MUST call :meth:`ExecutionPlan.validate` (or
    :func:`validate_plan`) before taking any action on the result.
    """
    if not work_order or not work_order.objective:
        raise ExecutionPlanError("cannot build plan from empty work order")

    workflow_stages = parse_workflow_from_text(work_order.source_text)
    workflow = Workflow(stages=workflow_stages)

    planned: list[PlannedCommand] = []
    for cmd_line in work_order.required_commands:
        argv = _command_argv(cmd_line)
        planned.append(PlannedCommand(raw=cmd_line.strip(), argv=argv))

    forbidden_paths = _derive_forbidden_paths(work_order)

    return ExecutionPlan(
        work_order_title=work_order.title,
        work_order_sha256=work_order.source_sha256,
        workflow=workflow,
        planned_commands=planned,
        allowed_paths=list(work_order.mutable_paths),
        forbidden_paths=forbidden_paths,
        protected_paths=list(work_order.protected_paths),
        required_commands=list(work_order.required_commands),
        has_explicit_destructive_permission=_explicit_destructive_permission(work_order),
    )


def _derive_forbidden_paths(wo: WorkOrder) -> list[str]:
    """Heuristic: any path-shaped token inside a Forbidden Actions item
    is treated as forbidden."""
    pool: list[str] = []
    for item in wo.forbidden_actions:
        for tok in re.findall(r"[A-Za-z0-9_./\\*-]+", item):
            if "/" in tok or tok.endswith("**") or tok.endswith("/"):
                pool.append(tok)
    seen: set[str] = set()
    out: list[str] = []
    for p in pool:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def validate_plan(plan: ExecutionPlan) -> list[str]:
    """Module-level convenience identical to ``plan.validate()``."""
    return plan.validate()


# ---------------------------------------------------------------------------
# Self-check
# ---------------------------------------------------------------------------


from intellagent_runtime.work_order_parser import parse_work_order  # noqa: E402  (avoid cycle in test harness)


_VALID_WO = """# WORK ORDER X — plan demo
## Objective
Demonstrate the execution plan validator end-to-end.

## Required Commands
```bash
make ci
make demo
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

## Forbidden Actions
- writing to canonicalization/corpus/

Stop.
"""


_DESTRUCTIVE_WO = """# WORK ORDER X — destructive without permission
## Objective
Try to run a destructive command without permission.

## Required Commands
```bash
rm -rf reports/archive
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


def self_check() -> int:
    failures: list[str] = []

    def expect(name: str, condition: bool, detail: str = "") -> None:
        print(f"  [{'PASS' if condition else 'FAIL'}] {name}")
        if not condition:
            failures.append(f"{name}: {detail}")

    wo = parse_work_order(_VALID_WO)
    plan = build_plan(wo)
    expect("plan_title_set", plan.work_order_title.startswith("WORK ORDER X"))
    expect("plan_workflow_has_verify_and_report",
           Stage.VERIFY in plan.workflow.stages and Stage.REPORT in plan.workflow.stages)
    expect("plan_valid_for_valid_wo", plan.is_valid(), str(plan.validate()))

    wo_bad = parse_work_order(_DESTRUCTIVE_WO)
    plan_bad = build_plan(wo_bad)
    expect("plan_destructive_without_permission_rejected", not plan_bad.is_valid())

    # Forbidden-path touch.
    wo_touch = parse_work_order("""## Objective
x
## Required Commands
```bash
make conformance VECTORS=vectors/forge.json
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
""")
    plan_touch = build_plan(wo_touch)
    expect("plan_forbidden_path_touch_rejected", not plan_touch.is_valid())

    # Missing report step.
    wo_no_report = parse_work_order("""## Objective
x
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
- stop
Stop.
""")
    plan_no_report = build_plan(wo_no_report)
    expect("plan_missing_report_rejected", not plan_no_report.is_valid())

    if failures:
        print(f"\nFAIL: {len(failures)} self-check failures")
        for f in failures:
            print(f"  ↳ {f}")
        return 1
    print("\nPASS: execution_plan self-check")
    return 0


if __name__ == "__main__":
    raise SystemExit(self_check())
