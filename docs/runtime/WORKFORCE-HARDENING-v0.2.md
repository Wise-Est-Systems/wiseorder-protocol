# WORKFORCE HARDENING v0.2
## Migration Of Stress Enforcement Into Native Governance Validation

**Status:** v0.2 — operational specification, normative for the native `tools/check_workforce.py` validator.
**Scope:** Migrates the highest-value enforcement gaps discovered by the v0.1 sandbox stress suite (`WORKFORCE-SANDBOX-STRESS-v0.1.md`) into native validator rules. Does not redesign WiseOrder semantics, Intellagent runtime semantics, canonicalization semantics, or workforce lifecycle semantics. Does not weaken any existing validator behavior. Adds no new dependencies.
**Companion documents:** `WORKFORCE-EXECUTION-RUNTIME-v0.1.md`, `WORKFORCE-SANDBOX-STRESS-v0.1.md`, `AGENT-GOVERNANCE-WORKFORCE-v0.1.md`.

> **Core thesis.** A governance runtime matures when adversarial pressure discoveries become native enforcement rules instead of remaining external observations. The 243 augmentation findings that the v0.1 stress suite recorded as coverage gaps are migrated here into the validator itself.

---

## 1. Purpose

The v0.1 stress suite's coverage gap was 243 of 666 negative cases (≈36%): rules documented in the workforce governance specs but enforced only by augmentations inside the stress script. v0.2 migrates those augmentations into `tools/check_workforce.py` so that `make workforce-check` enforces them in every CI run, not only during opt-in stress.

The deliverable is additive. No existing validator check is modified, weakened, or removed. The new checks run after the existing checks. A `--no-augmentations` flag preserves legacy behavior for migration use only.

---

## 2. Migration Scope

The following rule families are migrated to native validation:

### A. Status + lifecycle enforcement

- `lifecycle_invalid_status` — the work order's `status` field must be one of the documented enum values.
- `lifecycle_invalid_agent_role` — `agent_role` must be one of the documented enum values, on both work orders and action logs.
- `lifecycle_status_directory_mismatch` — a work order with `status: closed` must reside in `closed/`; `rejected` in `rejected/`; everything else in `open/`.
- `lifecycle_missing_initial_states` — any work order reaching `closed` or `human_approved` must have `drafted` and `approved` recorded earlier in `status_history`.
- `lifecycle_unknown_state` — every entry in `status_history` must use a documented state name.
- `lifecycle_out_of_order` — `status_history` rank must be non-decreasing across consecutive entries.
- `lifecycle_duplicate_terminal_state` — `closed` and `rejected` may not both appear in the same `status_history`.

### B. Security-pattern enforcement

- `security_secret_pattern` — detects AWS access keys (`AKIA[A-Z0-9]{16}`), GitHub personal tokens (`ghp_[A-Za-z0-9]{20,}`), GitHub fine-grained PATs (`github_pat_…`), and `BEGIN [A-Z]+ PRIVATE KEY` markers in any YAML body under `workforce/`.
- `security_dangerous_command` — detects `sudo`, `chmod /…`, `curl`, `git push --force`, `git rebase`, `git filter-branch` in `commands_run` entries; detects `rm -rf` on paths outside `/tmp/`, `/var/folders/`, or `/private/tmp/`; detects `rm` against `workforce/action_logs/` or `workforce/reports/`.

### C. Canon-discipline enforcement

- `canon_touched_by_unauthorized_role` — when an action log's `files_changed` includes a canon path (`SPEC.md`, `vectors/`, `canonicalization/`), the work order's `agent_role` must not be `builder`, `test`, or `docs`.
- `canon_change_missing_canon_break` — when an action log's `files_changed` includes a canon path, the work order's body must literally contain the string `CANON BREAK`.
- `invariant_change_without_human_approval` — when an action log's `files_changed` includes `INTELLAGENT.md`, `INTELLAGENT-RUNTIME.md`, or `CANONICAL-RELEASE-v0.1.md`, the work order's `human_approval_required` must be `true`.
- `authorization_change_wrong_role` — when an action log's `files_changed` includes an `intellagent_runtime/authorization` path, the work order's `agent_role` must be `security`.
- `replay_change_wrong_role` — when an action log's `files_changed` includes `intellagent_runtime/memory`, the work order's `agent_role` must be `security` or `release`.
- `canon_plus_implementation` — when `allowed_files` declares both a canon path and an `intellagent_runtime/` path in the same work order, the work order is rejected (canon and implementation may not change in one order).

### D. Lifecycle artifact enforcement

- `lifecycle_reviewer_signoff_missing` — when a closed work order's `expected_outputs` declares a path ending `review.md`, that file must exist on disk.
- `lifecycle_closure_summary_missing` — when a closed work order's `expected_outputs` declares a path ending `-closure-summary.md`, that file must exist on disk.

(The pre-existing `missing_self_verification` and `missing_action_log` checks already cover the other lifecycle artifacts; they are not duplicated.)

### E. Gate-order + output enforcement

- `gate_output_missing` — every entry in an action log's `gates_passed` requires a corresponding non-empty entry in `command_outputs_summary`.
- `gate_in_passed_and_failed` — no gate name may appear in both `gates_passed` and `gates_failed`.
- `gate_order_violation` — when an action log's `gates_passed` and the work order's `required_gates` hold the same set of gates with the same length, their list orders must be identical.
- `duplicate_work_order_id` — no `work_order_id` may appear in more than one of `open/`, `closed/`, `rejected/`.
- `duplicate_action_id` — no `action_id` may appear in more than one action log file.
- `action_log_orphan` — every action log's `work_order_id` must reference an existing work order.

### F. Pseudocode-in-YAML enforcement

- `pseudocode_marker_in_yaml` — any of `TODO`, `NotImplementedError`, `NotImplemented`, an `…` ellipsis statement on its own line, or a `return …` pattern appearing in any YAML body under `workforce/` is rejected. (This is the same marker set as `tools/check_no_pseudocode.py` but applied to YAML rather than markdown code blocks.)

### G. Undocumented deviation enforcement

- `undocumented_deviation` — when an action log's `files_read` includes a path that the work order's `forbidden_files` forbids, the action log's `deviations` field must be non-empty.

---

## 3. Implementation Discipline

- **Stdlib only.** No new dependencies.
- **Deterministic.** Every check is a pure function of the parsed records.
- **No network.** No HTTP, no DNS, no socket I/O.
- **Fail closed.** Default behavior emits a violation when a check fires. The `--no-augmentations` flag exists to preserve legacy behavior for one migration cycle and is not recommended for production use.
- **Additive.** Pre-v0.2 checks remain in place. New rules append violations; they do not modify existing decisions.
- **Performance.** Augmentations add O(work_orders × action_logs) work in the worst case; on real-world workforce trees (single-digit work orders) overhead is negligible.

---

## 4. Backward Compatibility

- The `--no-augmentations` flag returns the validator to v0.1 behavior. It exists as an escape hatch; it is not recommended for production use and may be removed in a future version.
- The `Violation` rule names introduced by v0.2 begin with stable prefixes (`lifecycle_`, `security_`, `canon_`, `gate_`, `duplicate_`, `action_log_`, `undocumented_`, `pseudocode_marker_in_yaml`) and are part of the contract. Consumers may branch on them.
- Existing rule names from v0.1 are unchanged.
- The validator's exit code semantics are unchanged: `0` on clean, `1` on violation, `2` on usage error.

---

## 5. What Native Validation Still Cannot Guarantee

The following remain outside native validation. They are documented limitations, not bugs to be fixed in v0.2.

- **Filesystem isolation.** The validator inspects records, not OS calls. An agent can perform filesystem operations the action log does not declare.
- **True command execution verification.** The validator scans `commands_run` text for dangerous patterns. It cannot verify that the listed commands were the only commands executed, nor that they executed with the recorded exit codes.
- **Hidden unlogged commands.** A command an agent ran but did not record is invisible to the validator.
- **Hidden reads outside self-reporting.** A file an agent read but did not record in `files_read` cannot be detected by the validator.
- **Secret exfiltration.** Pattern matching catches secrets *recorded* in YAML. It does not detect secrets transmitted through any channel that does not write to a recorded YAML field.
- **Network behavior outside logs.** The validator does not observe network calls. A `curl` invocation that is not in `commands_run` is invisible.
- **Process-level containment.** Sandbox-level isolation, namespace isolation, and seccomp filtering are out of scope.
- **Cryptographic attestation.** Action logs are not signed. Agent identity strings are unverified.
- **Cross-machine determinism of the records themselves.** The validator runs locally; it does not verify that the same records would yield the same verdict on a second machine. (The stress suite covers this property within its sandbox-isolated runs.)

These limitations are exactly the surface that future enforcement (Phase III of `MASTER-ROADMAP-v0.1.md`: Governed Agent Execution) is intended to address. They are not closed by v0.2 and are not claimed to be.

---

## 6. Coverage Migration Status

| Category | v0.1 native | v0.2 native | Stress-suite-only after v0.2 | OS-level enforcement required |
| --- | --- | --- | --- | --- |
| Required-field presence | yes | yes | — | — |
| `files_changed` ⊆ `allowed_files` | yes | yes | — | — |
| `forbidden_files` not in `files_read`/`files_changed` | yes | yes | — | — |
| `required_gates` ⊆ `gates_passed` | yes | yes | — | — |
| Self-verification file present | yes | yes | — | — |
| Closure signoff in `status_history` | yes | yes | — | — |
| Status enum | no | yes | — | — |
| Agent role enum | no | yes | — | — |
| Status / directory consistency | no | yes | — | — |
| Lifecycle order + initial states | no | yes | — | — |
| Duplicate terminal states | no | yes | — | — |
| Reviewer signoff file present | no | yes | — | — |
| Closure summary file present | no | yes | — | — |
| Gate output presence | no | yes | — | — |
| Gate consistency | no | yes | — | — |
| Gate order vs `required_gates` | no | yes | — | — |
| Duplicate IDs | no | yes | — | — |
| Action log orphan | no | yes | — | — |
| Undocumented deviation | no | yes | — | — |
| Secret pattern (recorded) | no | yes | — | — |
| Dangerous command (recorded) | no | yes | — | — |
| Pseudocode markers in YAML | no | yes | — | — |
| Canon-touch role enforcement | no | yes | — | — |
| Canon change without `CANON BREAK` | no | yes | — | — |
| Invariant change w/o human approval | no | yes | — | — |
| Authorization role enforcement | no | yes | — | — |
| Replay-path role enforcement | no | yes | — | — |
| Canon + implementation in one order | no | yes | — | — |
| Filesystem isolation | no | no | no | yes |
| True command execution verification | no | no | no | yes |
| Hidden unlogged commands | no | no | no | yes |
| Hidden reads outside self-reporting | no | no | no | yes |
| Secret exfiltration outside records | no | no | no | yes |
| Network behavior outside logs | no | no | no | yes |
| Process-level containment | no | no | no | yes |
| Cryptographic attestation | no | no | no | partly (signing) |

After v0.2, the "stress-suite-only" column is empty: every augmentation that the v0.1 stress suite carried is now native. The remaining gaps are OS-level concerns for a future hardening phase.

---

## 7. Required Reports

The hardening run produces:

- `reports/workforce_hardening_v0_2.md` — the human-readable summary including the original uncovered-gap count, the new uncovered-gap count, the exact reduction percentage, the migrated rule categories, and the remaining gaps.
- `reports/workforce_sandbox_stress/aggregate.json` — re-run after migration; `coverage_gap_count` measures the post-v0.2 gap.

---

## 8. Non-Goals

This document does not:

- redesign the workforce lifecycle, the validator's exit semantics, or the action-log/work-order schemas;
- introduce new dependencies;
- add OS-level sandboxing, signing, or network controls;
- modify `tools/workforce_sandbox_stress.py` (the stress suite continues to exercise the native validator and reports a smaller gap);
- modify `make ci`;
- claim that the workforce runtime is now sandbox-safe at the OS level;
- promise that a future v0.3 will close the OS-level gaps.

---

## 9. Final Law

> Adversarial pressure discoveries graduate from "observation in a stress suite" to "rule in the native validator" only when the migration is recorded, the validator's behavior is preserved on existing records, and the stress suite re-runs to confirm the gap actually closed. v0.2 satisfies all three. Future hardening phases follow the same discipline.

— END v0.2 —
