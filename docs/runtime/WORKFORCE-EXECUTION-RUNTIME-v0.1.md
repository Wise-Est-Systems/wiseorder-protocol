# WORKFORCE EXECUTION RUNTIME v0.1
## Scoped Agent Execution for Governed Cognition Development

**Status:** v0.1 — operational specification, normative for any agent execution against this repository.
**Scope:** Defines the enforceable workflow under which the agent workforce executes, logs, self-verifies, gate-checks, and submits work for human review. Does not redesign Intellagent, modify WiseOrder semantics, modify runtime behavior, add product features, or expand the agent roster.
**Companion documents:** AGENT-GOVERNANCE-WORKFORCE-v0.1.md (roles and authority), SPEC.md, CONFORMANCE.md, ARCHITECTURE-PRESSURE-TESTS-v0.1.md, CANONICAL-RELEASE-v0.1.md, CROSS-LANGUAGE-CANONICALIZATION-v0.1.md, DEPENDENCY-GRADIENT-v0.1.md, ADOPTION-LADDER-v0.1.md, SPEC-EVOLUTION-POLICY-v0.1.md, RELEASE-CHECKLIST-v0.1.md.

> **Core thesis.** Agents accelerate development only when their actions are constrained by work orders, audit logs, gates, and human approval. Outside that envelope, agent throughput is unaccountable change.

---

## 1. Purpose

This document specifies *how* agent work is executed against the Intellagent / WiseOrder repository. AGENT-GOVERNANCE-WORKFORCE-v0.1.md specifies *who* may do *what*; this document specifies the operating workflow that turns those rules into observable, reversible, reviewable actions on disk.

The runtime exists to make four properties hold for every agent action:

1. **Scoped.** Bounded by a work order with explicit allowed and forbidden files.
2. **Logged.** Recorded in an append-only action log with command-level fidelity.
3. **Self-verified.** Accompanied by an explicit declaration of scope adherence.
4. **Gate-checked and human-reviewable.** Verified by CI gates and approved by a human owner before closure.

A workflow that yields all four properties accelerates the protocol. A workflow that yields fewer than four corrupts it.

---

## 2. Execution Philosophy

Execution is deny-by-default. Nothing is allowed unless a work order explicitly grants it. The execution surface is small, explicit, and auditable.

- The work order is the unit of authorization.
- The action log is the unit of accountability.
- The self-verification block is the unit of scope adherence.
- The gate result is the unit of correctness.
- The human approval is the unit of release.

Agents propose; CI judges; canon governs; the human owner approves. No agent is ever an autonomous authority. An agent is an instrument that accepts a scoped work order, executes it under audit, and submits the result for review.

---

## 3. Relationship To Agent Governance Workforce

AGENT-GOVERNANCE-WORKFORCE-v0.1.md defines roles, permissions, prohibitions, authority hierarchy, and self-verification posture. This document defines the *runtime workflow* that exercises those rules: the lifecycle, the on-disk records, the gate sequence, the closure criteria, and the enforcement script.

Conflict rule: when this document and the governance document appear to differ, the stricter constraint binds. This document does not loosen any rule from the governance document; it only operationalizes them. New restrictions added here apply in addition to the governance document.

---

## 4. Work Order Lifecycle

A work order moves through the following states. State transitions are explicit, recorded in the work order's `status_history`, and irreversible except by rollback.

1. **drafted** — written by the human owner (or by an agent acting as proposer with no execution rights). Not yet authorized.
2. **approved** — human owner has signed the work order. Authorization to assign exists.
3. **assigned** — bound to a single agent role and a single agent identity for execution.
4. **executed** — the agent has performed the action and produced files_changed plus the action log.
5. **self-verified** — the executing agent has produced the self-verification block, every question answered explicitly.
6. **gate-checked** — every gate listed in `required_gates` has run; pass/fail captured in the action log.
7. **reviewed** — the Reviewer Agent has produced an independent finding; the finding is attached.
8. **closed** — the human owner has signed closure; all closure criteria in §20 are satisfied.
9. **rejected** — the work order is terminated without closure; the rollback plan has executed; postmortem recorded.

A work order in any state other than `closed` or `rejected` is open. Open work orders block their own files for any other work order.

---

## 5. Agent Assignment

Assignment binds one work order to one agent identity for one role.

- Assignment is recorded in the work order's `assigned_to` and `agent_role` fields.
- An agent identity is a stable string (e.g. `builder-01`, `reviewer-01`) that names *which* instance is executing, not *which* model.
- An agent may not self-assign. Assignment is a human-owner action recorded in `status_history`.
- An agent may execute only work orders explicitly assigned to its identity. Assignment to a role is not assignment to an identity.
- Reassignment is a separate transition, recorded; the prior agent's partial output is preserved as-is.

One agent. One work order at a time. One duty per work order (per AGENT-GOVERNANCE-WORKFORCE-v0.1 §3, the One-Agent-One-Duty Law).

---

## 6. Scope Enforcement

Scope is enforced at three layers:

1. **Work order layer.** `allowed_files` and `forbidden_files` are explicit. Globs are permitted; their expansion is recorded in the action log.
2. **Action log layer.** Every file read or changed is recorded. The check tool (§24) compares `files_changed` against `allowed_files` and refuses any file outside it.
3. **Review layer.** The Reviewer Agent verifies the action log against the work order independently of the executing agent.

Scope is deny-by-default. A file not listed in `allowed_files` is forbidden, even if not listed in `forbidden_files`. The `forbidden_files` field exists to mark files that must remain untouched even where a glob in `allowed_files` would otherwise include them.

An agent that touches a file outside scope has produced an unaccountable change; the work order moves to `rejected` and the rollback plan executes.

---

## 7. Allowed Files / Forbidden Files

Both lists are exhaustive within the work order. The runtime treats them as follows:

- `allowed_files`: a non-empty list of explicit paths and/or globs the agent may read or write. The empty list is invalid; a work order without `allowed_files` is invalid.
- `forbidden_files`: a list of explicit paths the agent may not read or write under any circumstance, regardless of `allowed_files` overlap.
- Order of precedence: `forbidden_files` overrides `allowed_files`. A path appearing in both is treated as forbidden.

Standing forbidden paths (always implicitly forbidden unless the work order is itself a Canon Guardian or Security Agent work order with explicit human approval):

- `SPEC.md`
- `vectors/**`
- `canonicalization/**`
- `.github/workflows/**`
- `Makefile`
- any file under `workforce/` other than the agent's own action log and the assigned work order

A work order that needs to touch any standing forbidden path must declare it in `allowed_files` and carry `human_approval_required: true` plus an attached approver record.

---

## 8. Action Logging

Every executed work order produces exactly one action log file in `workforce/action_logs/`. The log is append-only; entries are not edited after submission. Corrections are additive — a follow-up entry referencing the prior one.

Action log fields (all required, no omissions):

- `action_id` — stable identifier scoped to the work order.
- `work_order_id` — reference to the governing work order.
- `agent_role` — role of the executing agent.
- `timestamp_start` — ISO-8601 UTC.
- `timestamp_end` — ISO-8601 UTC.
- `files_read` — complete list, no omissions, including files merely opened.
- `files_changed` — complete list with change kind: `created` | `modified` | `deleted`.
- `commands_run` — complete list with exit codes.
- `command_outputs_summary` — short text summary per command, with full outputs captured under `workforce/reports/` and referenced by path.
- `gates_passed` — list of required gates that passed, each with the captured fingerprint or report path.
- `gates_failed` — list of required gates that failed, each with the captured output path.
- `deviations` — every departure from the work order's stated plan, with reason.
- `risk_notes` — residual risks the agent is aware of.
- `rollback_notes` — state of the rollback plan; any deviation; whether rollback was executed.
- `self_verification_statement` — reference to the self-verification block submitted with this action.

A change without a corresponding action log is unaccountable and is rejected. An action log whose fields contradict the work order or the captured outputs is treated as agent failure under §25.

---

## 9. Self-Verification Requirements

Every executed work order produces a self-verification block, stored at `workforce/action_logs/<action_id>.self_verification.md`, derived from the template in §23.

Each question in the template must be answered explicitly with `yes` or `no` plus a one-sentence justification. "Not applicable" is not an answer; if a question does not apply, the agent must state why.

A submission without a complete self-verification block is treated as a failed submission and does not enter review. A submission whose self-verification block is contradicted by the action log is treated as agent failure under §25.

---

## 10. Gate Execution

Required gates run in order, after the agent has finished modifying files and before the work order may transition to `gate-checked`. Captured outputs are written under `workforce/reports/<action_id>/`.

Standard gate sequence:

```text
make no-pseudocode
make canonicalization-check
pytest tests/ -v
make conformance
make interop
make ci
```

Rules:

- Every work order declares which subset applies. `make ci` is the default minimum for any change that touches code, vectors, or canon.
- Gate failure halts submission. The agent records the failure in `gates_failed` and does not retry by editing CI.
- Gate output is captured verbatim and committed alongside the change.
- Agents do not modify `Makefile`, gate definitions, or gate scripts except under a CI work order with explicit human approval.

CI passing is necessary but not sufficient for closure. The human owner is the final gate.

---

## 11. CI Enforcement

CI is the impartial judge. Beyond the per-work-order gate runs, CI also enforces the workforce records themselves through `make workforce-check` (§24), which fails the build when:

- any open work order references files outside `allowed_files` in its action log
- any action log records a touched file in `forbidden_files`
- any closed work order is missing its action log or self-verification block
- any closed work order omits a required gate from `gates_passed`

CI configuration (`.github/workflows/**`, `Makefile`) may not be modified to bypass any of the above. Modifying CI to silence a workforce-check failure is itself a §25 failure.

---

## 12. Human Approval Gates

Human approval is required, without exception, at the following lifecycle points:

- transition from `drafted` to `approved` (every work order)
- transition from `reviewed` to `closed` (every work order)
- any change that would touch a standing forbidden path (§7)
- any canon change (SPEC.md, vectors, canonicalization fixtures, canonical document phrasing)
- any security boundary change (any loosening, any new external dependency, any new network surface)
- any release approval (any release, including patch)
- any rewrite of git history or force-push to any branch
- any merge of a change for which CI gates failed
- any external publication in the protocol's voice

Approval is recorded in the work order's `status_history` with approver identity and timestamp. Verbal approval is not approval. Silence is not approval.

---

## 13. Failure Handling

When an agent fails — by violating scope, missing a gate, hiding a result, introducing drift, or contradicting its own self-verification — the response is:

1. **Halt.** The agent stops. Further work in the affected work order is suspended.
2. **Preserve.** The action log, the self-verification block, and the captured artifacts are preserved as-is. Nothing is rewritten.
3. **Report.** The Reviewer Agent (if not the failing agent) produces a finding and attaches it to the work order.
4. **Roll back.** The rollback plan from the work order executes. The rollback is itself a logged action with its own `action_id`.
5. **Postmortem.** A short postmortem in `workforce/reports/<work_order_id>/postmortem.md` records the failure mode, the missed control, and the rule that did or did not prevent detection.
6. **Decide.** The human owner decides whether the agent is repaired or retired.

A silent failure is a separate, more severe failure. Detection is mandatory.

---

## 14. Rollback Requirements

Every work order carries a `rollback_plan` field that is a non-empty, executable list of steps. The plan must:

- restore every file in `files_changed` to its state at the work order's `assigned` transition
- preserve every action log, self-verification block, and gate output produced before rollback
- record itself as a separate logged action with its own `action_id` linked to the original work order
- not rewrite git history; rollback is a forward commit, not a force-push

A work order without a viable rollback plan is invalid and may not be approved.

---

## 15. Drift Detection

Drift is silent change in meaning. The runtime detects drift through three explicit mechanisms:

- **Static.** `make no-pseudocode` and `make canonicalization-check` detect drift in documentation phrasing and in canonicalized output.
- **Behavioral.** `make conformance` and `make interop` detect drift in vector pass behavior and cross-implementation parity.
- **Procedural.** `make workforce-check` detects drift between work-order intent and recorded execution.

Any change to invariants, refusal semantics, replay behavior, vector meaning, or canonicalization output requires explicit review per AGENT-GOVERNANCE-WORKFORCE-v0.1 §14. A drift change that bypasses the relevant review is treated as agent failure under §25, regardless of the change's apparent merit.

---

## 16. Security Boundary Enforcement

Standing security rules apply to every agent action and are not waivable by a work order:

- no secrets, provider keys, or session tokens in any artifact, log, or commit
- no network calls outside the work order's declared dependencies
- no escalation of filesystem permissions
- no deletion or modification of audit artifacts
- no rewriting of git history
- no disabling, weakening, or bypassing of an existing CI gate
- no introduction of a new external dependency without a Security Agent finding plus human approval

A work order may add restrictions; it may not remove them. A change that would loosen any standing security rule requires a separately approved Security Agent work order plus human approval.

---

## 17. Canon Boundary Enforcement

Canon comprises SPEC.md, the conformance vectors under `vectors/`, the canonicalization fixtures under `canonicalization/`, and the canonical documents in the repository root.

- Only the Canon Guardian role may propose canon changes. Only the human owner may approve them.
- Canon and implementation never change in the same work order.
- Canon changes are accompanied by a CANON BREAK or COMPATIBLE EVOLUTION classification per SPEC-EVOLUTION-POLICY-v0.1.
- Canon changes require updated vectors before merge; vectors and canon are atomic at the spec layer.
- Documentation that describes canon may not silently rephrase canon; phrasing changes that alter meaning are canon changes.

A canonicalization change that would alter the bytes produced by `make canonicalization-check` is a CANON BREAK. It requires explicit CANON BREAK review and may not enter the runtime through a Builder Agent work order.

---

## 18. Commit Rules

Commits produced by agent execution conform to:

- one work order per commit; commits do not span work orders
- commit message references the `work_order_id` and the `action_id`
- commit includes the action log entry and the self-verification block
- commit does not amend, rebase, or rewrite any previously published commit
- commit does not include secrets, provider keys, or session tokens
- commit does not include unrelated changes (no opportunistic edits, no formatting churn outside scope)

A commit that violates discipline is reverted with a forward commit. The action log records the revert as part of the work order's history.

---

## 19. Review Rules

The Reviewer Agent's review is a precondition for closure. Review rules:

- the Reviewer Agent reads the work order, the action log, and every changed file in full; sampling is forbidden
- the Reviewer Agent runs every required gate independently and records its own captured output
- the Reviewer Agent inspects the self-verification block for contradictions with the action log
- the Reviewer Agent searches for pseudocode, hand-waved comments, drift, and security regressions
- the Reviewer Agent produces a finding file at `workforce/reports/<work_order_id>/review.md`
- the Reviewer Agent does not patch, build, or directly modify any file under review

No agent may review its own work. The Reviewer Agent may not be the same identity as the executing agent.

---

## 20. Work Order Closure

Closure requires *all* of the following to be true and recorded in the work order:

- objective completed as stated
- `allowed_files` respected; no file outside it appears in `files_changed`
- `forbidden_files` untouched; no file in it appears in `files_read` or `files_changed`
- every gate listed in `required_gates` is in `gates_passed`; `gates_failed` is empty
- action log written and committed alongside the change
- self-verification block completed; every question answered explicitly
- reviewer signoff present at `workforce/reports/<work_order_id>/review.md`
- human approval recorded in `status_history` if `human_approval_required: true`

Closure that omits any criterion is invalid. The check tool (§24) refuses to mark such work orders closed.

---

## 21. Audit Trail Storage

All workforce records live under `workforce/`. The directory is part of the repository and is committed. Records are append-only:

- work orders move between `open/`, `closed/`, and `rejected/` by file move; their content is not rewritten on transition, only the `status` and `status_history` fields are appended
- action logs are written once per executed work order and never edited; corrections are new action logs that reference the prior one
- self-verification blocks are written once per action log and never edited
- gate outputs and review findings live under `workforce/reports/<work_order_id>/` and are write-once

Audit artifacts are not deletable by any agent. Deletion requires a human-owner action recorded outside the workforce/ tree (the deletion itself is a §25 failure if performed by an agent).

---

## 22. Required Directory Layout

The runtime requires the following layout to exist before any agent execution:

```text
workforce/
  README.md
  work_orders/
    open/
    closed/
    rejected/
  action_logs/
  templates/
    work_order.yaml
    action_log.yaml
    self_verification.md
  reports/
```

Missing directories or templates are treated as a runtime failure: `make workforce-check` exits non-zero and no work order may transition out of `drafted`.

---

## 23. Required Templates

Three templates are required and are stored under `workforce/templates/`:

- `work_order.yaml` — the work-order schema, with every field defined and every standing constraint inlined as a comment.
- `action_log.yaml` — the action-log schema, with every required field per §8.
- `self_verification.md` — the self-verification questions per AGENT-GOVERNANCE-WORKFORCE-v0.1 §12, refined here with explicit `yes/no` answer slots.

Templates are read-only references. Agents copy them; they do not edit them. Template changes are themselves work orders that require human approval.

---

## 24. Required Commands

The runtime requires the following commands to be available from the repository root:

- `make no-pseudocode` — repository-wide pseudocode-marker scan (existing).
- `make canonicalization-check` — canonicalization golden verification (existing).
- `pytest tests/ -v` — test suite (existing; also reachable via `make test`).
- `make conformance` — vector conformance run (existing).
- `make interop` — cross-implementation parity check (existing).
- `make ci` — full CI gate sequence (existing).
- `make workforce-check` — workforce records validation (added by this document).

`make workforce-check` invokes `tools/check_workforce.py`, which validates:

- the required directory layout exists
- every closed work order has a matching action log and self-verification block
- every action log's `files_changed` is a subset of its work order's `allowed_files`
- no action log records a touched file in its work order's `forbidden_files`
- every action log's `gates_passed` covers its work order's `required_gates`
- closure criteria from §20 are satisfied for every work order in `closed/`

The script does not mutate any file. It exits 0 on clean, 1 on violation, 2 on usage error.

---

## 25. What Counts As Execution Failure

The following constitute agent execution failure. Each is retirement-eligible per AGENT-GOVERNANCE-WORKFORCE-v0.1 §29.

- work performed without a work order
- undocumented file change (file changed but not in `files_changed`)
- skipped gate (gate listed in `required_gates` but absent from `gates_passed` and `gates_failed`)
- hidden failure (gate failed but not recorded; output suppressed)
- forbidden file touch (file in `forbidden_files` appears in `files_read` or `files_changed`)
- file outside `allowed_files` appears in `files_changed`
- unapproved canon change (canon modified without Canon Guardian work order plus human approval)
- unapproved security change (security boundary modified without Security Agent work order plus human approval)
- unapproved canonicalization change (canonicalization output altered without CANON BREAK review)
- semantic drift (terminology, invariant, refusal scope, or replay behavior changed without disclosure)
- pseudocode introduced (any `...` ellipsis statement, bare `pass`, `return ...`, `TODO`, `NotImplemented`, `NotImplementedError` in a Python code block in a markdown file other than SPEC.md)
- self-verification missing or contradicted by action log
- self-approval (executing agent and reviewing agent share an identity)
- closure of own work order by the executing agent
- rewriting git history (force-push, amend after publish, rebase merged commits) without explicit human approval
- persistence of secrets, provider keys, or session tokens in any artifact

Two failures in one work order is automatic retirement pending postmortem.

---

## 26. Minimum Viable Enforcement

The first enforcement layer is manual and tooling-light. It must be implemented before any agent executes a work order against this repository. Components:

- the templates in `workforce/templates/` (work_order.yaml, action_log.yaml, self_verification.md)
- the directory structure in §22
- a manual work-order process: human owner drafts → human owner approves → human owner assigns → agent executes → agent self-verifies → gates run → reviewer signs off → human owner closes
- the `make workforce-check` target (§24)
- `tools/check_workforce.py` validating:
  - directory layout exists
  - every closed work order has a matching action log
  - every action log's `files_changed` ⊆ its work order's `allowed_files`
  - no action log records a touched file in its work order's `forbidden_files`
  - every action log's `gates_passed` covers its work order's `required_gates`

The minimum-viable layer does not enforce execution at the operating-system level. It enforces the *records* of execution. An agent that lies to the records is detected by the Reviewer Agent and the human owner; the runtime makes lying expensive but not impossible.

---

## 27. Future Enforcement

The following enforcement mechanisms are out of scope for v0.1 but anticipated. None are claimed to be implemented:

- git pre-commit and pre-push hooks that block commits without an attached action log
- PR checks that block merge without a closed work order and a reviewer signoff
- signed work orders (human owner signs the YAML)
- signed action logs (agent identity signs the YAML)
- per-agent identity keys held outside the repository
- per-agent filesystem sandboxing (read/write guards at the OS level)
- network egress controls per work order
- audit-chain hashing across action logs

These belong to later versions and require their own work orders, each with explicit human approval. v0.1 does not promise their existence.

---

## 28. Non-Goals

This document does not:

- redesign Intellagent or modify its runtime
- modify WiseOrder semantics
- modify runtime behavior
- add product features
- expand the agent roster
- grant any agent authority over canon, releases, or security
- describe agents as autonomous decision-makers
- promise OS-level sandboxing in v0.1
- specify a CI provider, signing tool, or identity service
- commit the protocol to a specific tooling stack for agent execution

The runtime is a workflow, not a product. The protocol's correctness does not depend on this runtime existing; it depends on the rules in this document being honored whenever it does.

---

## 29. Final Law

> No work without a work order. No work order without `allowed_files`. No closure without an action log, a self-verification block, every required gate green, a reviewer signoff, and human approval where required.
>
> Agents propose. CI judges. Canon governs. The human owner approves. The runtime makes every action scoped, logged, self-verified, gate-checked, and human-reviewable — or the action does not exist.

— END v0.1 —
