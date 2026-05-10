# workforce/

Operational records for agent execution against this repository. Governed by:

- AGENT-GOVERNANCE-WORKFORCE-v0.1.md — roles, permissions, prohibitions, authority hierarchy.
- WORKFORCE-EXECUTION-RUNTIME-v0.1.md — lifecycle, on-disk records, gates, closure, enforcement script.

## Layout

```text
workforce/
  README.md                 — this file
  work_orders/
    open/                   — drafted, approved, assigned, executed, self-verified, gate-checked, reviewed
    closed/                 — closure approved by human owner; all §20 criteria satisfied
    rejected/               — terminated without closure; rollback executed; postmortem attached
  action_logs/              — one append-only log per executed work order
  templates/
    work_order.yaml         — work-order schema, copy-not-edit
    action_log.yaml         — action-log schema, copy-not-edit
    self_verification.md    — self-verification questions, copy-not-edit
  reports/                  — captured gate outputs, review findings, postmortems
```

## Standing rules

- No work without a work order.
- No work order without `allowed_files`.
- No agent touches `forbidden_files`.
- No agent approves its own work.
- No agent closes its own work order.
- No canon change without human approval.
- No security boundary change without human approval.
- No canonicalization change without CANON BREAK review.

## Validation

```text
make workforce-check
```

Validates the directory layout, that every closed work order has a matching action log and self-verification, that `files_changed` ⊆ `allowed_files`, that `forbidden_files` was untouched, and that every required gate is in `gates_passed`.

The script does not mutate any file. Exit codes: 0 clean, 1 violation, 2 usage error.
