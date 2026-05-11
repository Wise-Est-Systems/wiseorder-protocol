"""Workflow grammar for the WiseOrder runtime core.

A workflow is an ordered sequence of named stages that govern how a work
order is executed. The grammar enforces the ordering rules required by
SPEC.md §7 (Action Governance — verification precedes authorization
which precedes execution) and INTELLAGENT-RUNTIME §refusal-sealing.

Stages:

  INSPECT  — read the world; produces no mutating side-effect
  PROPOSE  — emit a candidate action; zero execution authority
  REVIEW   — admit or refuse a candidate; zero execution authority
  EXECUTE  — apply an admitted action; bounded
  VERIFY   — confirm a state property (post-execute OR over an existing artifact)
  REPORT   — record the outcome
  STOP     — terminal; nothing may follow
  REFUSE   — terminal; a sealed refusal is a successful protocol outcome

Ordering rules (enforced):

  - EXECUTE MUST be preceded by REVIEW.
  - VERIFY MUST be preceded by EXECUTE unless the verification is over a
    pre-existing artifact (see ``Workflow.from_stage_names`` second arg).
  - REPORT MUST occur before STOP.
  - STOP is terminal; nothing may follow.
  - REFUSE is terminal; nothing may follow.
  - A workflow that ends in REFUSE without ever reaching EXECUTE is a
    valid governance outcome and MUST NOT be rejected for "no execute".
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable


class Stage(str, Enum):
    """Canonical stage names. Inherits from :class:`str` so values can
    appear directly in JSON output without manual conversion."""

    INSPECT = "inspect"
    PROPOSE = "propose"
    REVIEW = "review"
    EXECUTE = "execute"
    VERIFY = "verify"
    REPORT = "report"
    STOP = "stop"
    REFUSE = "refuse"


# Synonyms recognized when parsing prose. The map is deliberately narrow
# — only words that unambiguously describe one stage are accepted.
_STAGE_SYNONYMS: dict[str, Stage] = {
    "inspect": Stage.INSPECT,
    "inspection": Stage.INSPECT,
    "survey": Stage.INSPECT,
    "scan": Stage.INSPECT,
    "audit-inspect": Stage.INSPECT,
    "propose": Stage.PROPOSE,
    "proposal": Stage.PROPOSE,
    "draft": Stage.PROPOSE,
    "candidate": Stage.PROPOSE,
    "review": Stage.REVIEW,
    "gate": Stage.REVIEW,
    "approve": Stage.REVIEW,
    "admit": Stage.REVIEW,
    "execute": Stage.EXECUTE,
    "execution": Stage.EXECUTE,
    "run": Stage.EXECUTE,
    "apply": Stage.EXECUTE,
    "commit": Stage.EXECUTE,
    "verify": Stage.VERIFY,
    "verification": Stage.VERIFY,
    "check": Stage.VERIFY,
    "validate": Stage.VERIFY,
    "test": Stage.VERIFY,
    "report": Stage.REPORT,
    "summary": Stage.REPORT,
    "output": Stage.REPORT,
    "write-report": Stage.REPORT,
    "stop": Stage.STOP,
    "halt": Stage.STOP,
    "terminate": Stage.STOP,
    "refuse": Stage.REFUSE,
    "refusal": Stage.REFUSE,
}


@dataclass
class WorkflowError(Exception):
    """Raised when a workflow violates the grammar."""

    message: str
    violations: list[str] = field(default_factory=list)

    def __str__(self) -> str:  # pragma: no cover - cosmetic
        if self.violations:
            return f"{self.message}: {self.violations}"
        return self.message


@dataclass
class Workflow:
    """A workflow is a sequence of stages plus a flag indicating whether
    any VERIFY stage acts on a pre-existing artifact (rather than the
    output of a fresh EXECUTE)."""

    stages: list[Stage]
    verify_over_existing_artifact: bool = False

    @classmethod
    def from_stage_names(
        cls,
        names: Iterable[str],
        *,
        verify_over_existing_artifact: bool = False,
    ) -> "Workflow":
        out: list[Stage] = []
        for n in names:
            s = _coerce_stage(n)
            if s is None:
                raise WorkflowError(message=f"unknown stage: {n!r}")
            out.append(s)
        return cls(stages=out, verify_over_existing_artifact=verify_over_existing_artifact)

    def validate(self) -> list[str]:
        """Return the list of ordering violations. Empty list means the
        workflow is valid."""
        return validate_stages(
            self.stages,
            verify_over_existing_artifact=self.verify_over_existing_artifact,
        )

    def is_valid(self) -> bool:
        return not self.validate()

    def terminal_kind(self) -> Stage | None:
        if not self.stages:
            return None
        last = self.stages[-1]
        if last in (Stage.STOP, Stage.REFUSE):
            return last
        return None


# ---------------------------------------------------------------------------
# Validation rules
# ---------------------------------------------------------------------------


def validate_stages(
    stages: list[Stage],
    *,
    verify_over_existing_artifact: bool = False,
) -> list[str]:
    """Return ordering violations. The check is conservative: every rule
    in the grammar is enforced and the *first* failing index for each
    rule is reported."""
    violations: list[str] = []
    if not stages:
        return ["empty workflow"]

    # Track whether each predecessor has been seen.
    seen_review_after_propose = False
    seen_review = False
    seen_execute = False
    seen_propose = False
    seen_report = False

    for i, stage in enumerate(stages):
        # No stage may follow STOP or REFUSE.
        if i > 0 and stages[i - 1] in (Stage.STOP, Stage.REFUSE):
            violations.append(
                f"stage at index {i} ({stage.value!r}) follows terminal "
                f"{stages[i - 1].value!r}; nothing may follow a terminal stage"
            )
            break  # any further check is meaningless after a terminal violation

        if stage is Stage.PROPOSE:
            seen_propose = True
        if stage is Stage.REVIEW:
            seen_review = True
            if seen_propose:
                seen_review_after_propose = True
        if stage is Stage.EXECUTE:
            if not seen_review:
                violations.append(
                    f"execute at index {i} is not preceded by a review stage"
                )
            seen_execute = True
        if stage is Stage.VERIFY:
            if not seen_execute and not verify_over_existing_artifact:
                violations.append(
                    f"verify at index {i} is not preceded by an execute stage "
                    f"(set verify_over_existing_artifact=True to verify a pre-existing artifact)"
                )
        if stage is Stage.REPORT:
            seen_report = True
        if stage is Stage.STOP:
            if not seen_report:
                violations.append(
                    f"stop at index {i} is not preceded by a report stage"
                )

    # Soft expectation: a propose-then-review pairing. We only flag a
    # missing review *if* a propose existed and no review followed it.
    if seen_propose and not seen_review_after_propose:
        violations.append("propose stage was emitted but never reviewed")

    return violations


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

_STAGE_KEY_PATTERN = re.compile(r"\b([a-zA-Z][a-zA-Z_-]{2,15})\b")


def _coerce_stage(token: str) -> Stage | None:
    key = token.strip().lower().rstrip(".:,")
    if not key:
        return None
    if key in _STAGE_SYNONYMS:
        return _STAGE_SYNONYMS[key]
    return None


def parse_workflow_from_text(text: str) -> list[Stage]:
    """Extract a stage sequence from arbitrary structured prose by
    scanning each non-fenced line for a recognizable stage keyword.

    A line contributes at most one stage. Order is preserved.
    """
    out: list[Stage] = []
    in_fence = False
    for raw in text.splitlines():
        s = raw.strip()
        if s.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or not s:
            continue
        # Headings, bullets, numbered items.
        head = re.sub(r"^[\s#\-*0-9.]+", "", s).strip()
        if not head:
            continue
        tokens = _STAGE_KEY_PATTERN.findall(head)
        # First synonymous token on the line wins.
        for tok in tokens:
            stage = _coerce_stage(tok)
            if stage is not None:
                out.append(stage)
                break
    return out


def parse_workflow(text: str, *, verify_over_existing_artifact: bool = False) -> Workflow:
    """Public entry point: parse text into a :class:`Workflow`."""
    stages = parse_workflow_from_text(text)
    return Workflow(stages=stages, verify_over_existing_artifact=verify_over_existing_artifact)


# ---------------------------------------------------------------------------
# Self-check
# ---------------------------------------------------------------------------


def self_check() -> int:
    failures: list[str] = []

    def expect(name: str, condition: bool, detail: str = "") -> None:
        print(f"  [{'PASS' if condition else 'FAIL'}] {name}")
        if not condition:
            failures.append(f"{name}: {detail}")

    # 1. canonical happy path.
    w = Workflow.from_stage_names(
        ["inspect", "propose", "review", "execute", "verify", "report", "stop"]
    )
    expect("canonical_path_valid", w.is_valid(), str(w.validate()))

    # 2. execute before review.
    w = Workflow.from_stage_names(["propose", "execute", "review", "report", "stop"])
    expect("execute_before_review_rejected", not w.is_valid())

    # 3. verify before execute, no existing-artifact flag.
    w = Workflow.from_stage_names(["inspect", "verify", "report", "stop"])
    expect("verify_before_execute_rejected", not w.is_valid())

    # 4. verify before execute WITH existing-artifact flag.
    w = Workflow.from_stage_names(
        ["inspect", "verify", "report", "stop"],
        verify_over_existing_artifact=True,
    )
    expect("verify_existing_artifact_allowed", w.is_valid(), str(w.validate()))

    # 5. report missing before stop.
    w = Workflow.from_stage_names(["inspect", "propose", "review", "execute", "stop"])
    expect("stop_without_report_rejected", not w.is_valid())

    # 6. stage after stop.
    w = Workflow.from_stage_names(["inspect", "propose", "review", "execute", "report", "stop", "report"])
    expect("stage_after_stop_rejected", not w.is_valid())

    # 7. refusal is a valid terminal even without execute.
    w = Workflow.from_stage_names(["inspect", "propose", "review", "refuse"])
    expect("refusal_terminal_valid", w.is_valid(), str(w.validate()))

    # 8. parse_workflow_from_text.
    text = """## Stages
- inspect the world
- propose a patch
- review the patch
- execute the admitted patch
- verify post-execute
- report results
- stop
"""
    parsed = parse_workflow(text)
    expect("parser_recognizes_stages", parsed.stages and parsed.stages[0] is Stage.INSPECT)

    # 9. propose without review is flagged.
    w = Workflow.from_stage_names(["inspect", "propose", "report", "stop"])
    expect("propose_without_review_rejected", not w.is_valid())

    # 10. empty workflow.
    w = Workflow(stages=[])
    expect("empty_workflow_rejected", not w.is_valid())

    if failures:
        print(f"\nFAIL: {len(failures)} self-check failures")
        for f in failures:
            print(f"  ↳ {f}")
        return 1
    print("\nPASS: workflow_grammar self-check")
    return 0


if __name__ == "__main__":
    raise SystemExit(self_check())
