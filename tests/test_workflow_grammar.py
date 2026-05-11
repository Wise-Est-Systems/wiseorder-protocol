"""Tests for intellagent_runtime/workflow_grammar.py."""

from __future__ import annotations

import pytest

from intellagent_runtime.workflow_grammar import (
    Stage,
    Workflow,
    WorkflowError,
    parse_workflow,
    parse_workflow_from_text,
    self_check,
    validate_stages,
)


# ---------------------------------------------------------------------------
# Stage enum
# ---------------------------------------------------------------------------


def test_stage_values_are_lowercase_strings():
    for s in Stage:
        assert s.value == s.value.lower()
        assert isinstance(s, str)


def test_stage_str_subclass_works_in_json():
    import json
    payload = {"stages": [Stage.REVIEW, Stage.EXECUTE]}
    encoded = json.dumps(payload)
    assert "review" in encoded
    assert "execute" in encoded


# ---------------------------------------------------------------------------
# Validation rules
# ---------------------------------------------------------------------------


def test_canonical_workflow_is_valid():
    w = Workflow.from_stage_names(
        ["inspect", "propose", "review", "execute", "verify", "report", "stop"]
    )
    assert w.is_valid()


def test_execute_before_review_is_rejected():
    w = Workflow.from_stage_names(["propose", "execute", "review", "report", "stop"])
    assert not w.is_valid()
    assert any("execute" in v and "review" in v for v in w.validate())


def test_verify_before_execute_rejected_without_flag():
    w = Workflow.from_stage_names(["inspect", "verify", "report", "stop"])
    assert not w.is_valid()


def test_verify_before_execute_allowed_with_flag():
    w = Workflow.from_stage_names(
        ["inspect", "verify", "report", "stop"],
        verify_over_existing_artifact=True,
    )
    assert w.is_valid()


def test_report_required_before_stop():
    w = Workflow.from_stage_names(["inspect", "propose", "review", "execute", "stop"])
    assert not w.is_valid()
    assert any("stop" in v and "report" in v for v in w.validate())


def test_stop_is_terminal():
    w = Workflow.from_stage_names(
        ["inspect", "propose", "review", "execute", "report", "stop", "report"]
    )
    assert not w.is_valid()


def test_refuse_is_terminal():
    w = Workflow.from_stage_names(
        ["inspect", "propose", "review", "refuse", "report"]
    )
    assert not w.is_valid()


def test_refusal_terminal_without_execute_is_valid():
    """A refusal that never reaches execute is a successful protocol outcome
    and MUST NOT be flagged as missing-execute."""
    w = Workflow.from_stage_names(["inspect", "propose", "review", "refuse"])
    assert w.is_valid()


def test_empty_workflow_is_invalid():
    w = Workflow(stages=[])
    assert not w.is_valid()


def test_propose_without_review_is_rejected():
    w = Workflow.from_stage_names(["inspect", "propose", "report", "stop"])
    assert not w.is_valid()


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------


def test_parse_workflow_recognizes_inline_stages():
    text = """## Stages
- inspect the world
- propose a patch
- review the patch
- execute the admitted patch
- verify post-execute
- report results
- stop
"""
    w = parse_workflow(text)
    assert w.stages[0] is Stage.INSPECT
    assert w.stages[-1] is Stage.STOP


def test_parse_workflow_skips_code_fences():
    text = """```bash
make ci
```
- inspect
- propose
- review
- execute
- verify
- report
- stop
"""
    stages = parse_workflow_from_text(text)
    assert Stage.INSPECT in stages
    assert Stage.STOP in stages


def test_parse_workflow_handles_numbered_items():
    text = """## Stages
1. inspect the repo
2. propose a change
3. review the change
4. execute
5. verify
6. report
7. stop
"""
    w = parse_workflow(text)
    assert len(w.stages) == 7


def test_from_stage_names_rejects_unknown_token():
    with pytest.raises(WorkflowError):
        Workflow.from_stage_names(["inspect", "wat", "review", "execute", "report", "stop"])


# ---------------------------------------------------------------------------
# Misc
# ---------------------------------------------------------------------------


def test_validate_stages_returns_empty_for_valid():
    assert validate_stages(
        [Stage.INSPECT, Stage.PROPOSE, Stage.REVIEW, Stage.EXECUTE, Stage.VERIFY, Stage.REPORT, Stage.STOP]
    ) == []


def test_terminal_kind_reports_stop():
    w = Workflow.from_stage_names(
        ["inspect", "propose", "review", "execute", "verify", "report", "stop"]
    )
    assert w.terminal_kind() is Stage.STOP


def test_terminal_kind_reports_refuse():
    w = Workflow.from_stage_names(["inspect", "propose", "review", "refuse"])
    assert w.terminal_kind() is Stage.REFUSE


def test_terminal_kind_returns_none_when_open():
    w = Workflow.from_stage_names(["inspect", "propose"])
    assert w.terminal_kind() is None


def test_self_check_returns_zero(capsys):
    rc = self_check()
    out = capsys.readouterr().out
    assert rc == 0
    assert "PASS" in out
