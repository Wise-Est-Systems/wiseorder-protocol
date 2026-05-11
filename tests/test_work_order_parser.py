"""Tests for intellagent_runtime/work_order_parser.py."""

from __future__ import annotations

import pytest

from intellagent_runtime.work_order_parser import (
    WorkOrder,
    WorkOrderError,
    parse_work_order,
    parse_work_order_file,
    self_check,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


VALID_WO = """# WORK ORDER 999 — Demo
## Objective
Verify the parser end-to-end.

## Primary Rules
- Do not modify SPEC.md.
- Real code only.

## Allowed Actions
- Edit `intellagent_runtime/`.

## Forbidden Actions
- Delete vectors/

## Required Outputs
- A report at `reports/runtime_core/demo.md`.

## Required Commands
```bash
make ci
make demo
```

## Do Not Modify
- vectors/**
- canonicalization/corpus/**

## Final Output
- Print a summary table.

Stop.
"""


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_parses_title():
    wo = parse_work_order(VALID_WO)
    assert wo.title.startswith("WORK ORDER 999")


def test_parses_objective():
    wo = parse_work_order(VALID_WO)
    assert "parser" in wo.objective.lower()


def test_parses_primary_rules():
    wo = parse_work_order(VALID_WO)
    assert len(wo.primary_rules) >= 2
    assert any("SPEC.md" in r for r in wo.primary_rules)


def test_parses_required_commands():
    wo = parse_work_order(VALID_WO)
    assert "make ci" in wo.required_commands
    assert "make demo" in wo.required_commands


def test_parses_protected_paths():
    wo = parse_work_order(VALID_WO)
    assert "vectors/**" in wo.protected_paths
    assert "canonicalization/corpus/**" in wo.protected_paths


def test_parses_stop_condition():
    wo = parse_work_order(VALID_WO)
    assert wo.stop_condition == "Stop."


def test_source_sha256_is_sha256_prefixed():
    wo = parse_work_order(VALID_WO)
    assert wo.source_sha256.startswith("sha256:")
    assert len(wo.source_sha256) == len("sha256:") + 64


def test_to_dict_round_trip_contains_all_fields():
    wo = parse_work_order(VALID_WO)
    d = wo.to_dict()
    for key in (
        "title", "objective", "primary_rules", "allowed_actions",
        "forbidden_actions", "required_outputs", "required_commands",
        "stop_condition", "protected_paths", "mutable_paths",
        "final_reporting", "source_sha256",
    ):
        assert key in d


# ---------------------------------------------------------------------------
# Rejection paths
# ---------------------------------------------------------------------------


def test_rejects_empty_document():
    with pytest.raises(WorkOrderError):
        parse_work_order("")


def test_rejects_whitespace_only_document():
    with pytest.raises(WorkOrderError):
        parse_work_order("\n  \n\t\n")


def test_rejects_missing_objective():
    body = "## Required Commands\n```bash\nmake ci\n```\nStop.\n"
    with pytest.raises(WorkOrderError, match="objective"):
        parse_work_order(body)


def test_rejects_missing_stop():
    body = "## Objective\nDo a thing.\n"
    with pytest.raises(WorkOrderError, match="stop"):
        parse_work_order(body)


def test_rejects_placeholder_only_deliverable():
    body = """## Objective
Do a thing.

## Required Outputs
- TODO

Stop.
"""
    with pytest.raises(WorkOrderError, match="placeholder"):
        parse_work_order(body)


def test_rejects_protected_path_also_mutable_without_permission():
    body = """## Objective
Try to mutate a protected path.

## Do Not Modify
- vectors/**

## May Modify
- vectors/**

Stop.
"""
    with pytest.raises(WorkOrderError, match="protected"):
        parse_work_order(body)


def test_allows_protected_path_overlap_with_explicit_permission():
    body = """## Objective
Override one path under explicit permission.

## Primary Rules
- May modify vectors/** under explicit permission for vector renumbering.

## Do Not Modify
- vectors/**

## May Modify
- vectors/**

Stop.
"""
    wo = parse_work_order(body)
    assert "vectors/**" in wo.protected_paths
    assert "vectors/**" in wo.mutable_paths


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_label_form_objective_picked_up():
    # No '## Objective' heading; uses a bold-label syntax inline.
    body = "Objective: ship the runtime core.\n\nStop.\n"
    wo = parse_work_order(body)
    assert "ship" in wo.objective


def test_inline_stop_marker_anywhere_satisfies_stop():
    body = "## Objective\nx\n\nSome other prose.\n\nStop.\n"
    wo = parse_work_order(body)
    assert wo.stop_condition == "Stop."


def test_code_fence_contents_collected_into_commands_section():
    body = """## Objective
x

## Required Commands
```bash
make ci
go test ./go_verifier/...
```

Stop.
"""
    wo = parse_work_order(body)
    assert "make ci" in wo.required_commands
    assert "go test ./go_verifier/..." in wo.required_commands


def test_parse_work_order_file_round_trip(tmp_path):
    p = tmp_path / "wo.md"
    p.write_text(VALID_WO, encoding="utf-8")
    wo = parse_work_order_file(p)
    assert wo.title.startswith("WORK ORDER 999")


def test_self_check_returns_zero(capsys):
    rc = self_check()
    out = capsys.readouterr().out
    assert rc == 0
    assert "PASS" in out


def test_workorder_dataclass_default_is_empty():
    wo = WorkOrder()
    assert wo.title == ""
    assert wo.primary_rules == []
    assert wo.required_commands == []


def test_required_outputs_extracted():
    body = """## Objective
x

## Required Outputs
- a `report.md`
- a JSON manifest

Stop.
"""
    wo = parse_work_order(body)
    assert len(wo.required_outputs) == 2
