# Workforce Hardening v0.2 — Migration Report

**Date:** 2026-05-07
**Spec:** `WORKFORCE-HARDENING-v0.2.md`
**Validator file:** `tools/check_workforce.py`
**Stress suite:** `tools/workforce_sandbox_stress.py` (unmodified for this migration)

---

## 1. Coverage Gap

| Metric | v0.1 | v0.2 |
| --- | ---: | ---: |
| Total stress-suite checks | 900 | 900 |
| Negative cases (expected fail) | 666 | 666 |
| Positive cases (expected pass) | 234 | 234 |
| Mismatches (suite-level) | 0 | 0 |
| Cross-sandbox identity | all agree | all agree |
| **Coverage gap** (validator ≠ comprehensive) | **243** | **0** |
| Reduction | — | **243 / 243 = 100.00%** |

Stress-suite duration: 11.2 s (parallel, three sandboxes, 900 cases).

---

## 2. Migrated Rule Categories

All five families specified in `WORKFORCE-HARDENING-v0.2.md` §2 are now native:

- **A. Status + lifecycle** (7 rules): `lifecycle_invalid_status`, `lifecycle_invalid_agent_role`, `lifecycle_status_directory_mismatch`, `lifecycle_missing_initial_states`, `lifecycle_unknown_state`, `lifecycle_out_of_order`, `lifecycle_duplicate_terminal_state`.
- **B. Security** (2 rules covering 9 patterns): `security_secret_pattern` (AWS / GitHub / GitHub PAT / private-key marker), `security_dangerous_command` (sudo / chmod / curl / git force-push / git rebase / git filter-branch / rm-rf-outside-temp / audit-artifact-delete).
- **C. Canon discipline** (6 rules): `canon_touched_by_unauthorized_role`, `canon_change_missing_canon_break`, `invariant_change_without_human_approval`, `authorization_change_wrong_role`, `replay_change_wrong_role`, `canon_plus_implementation`.
- **D. Lifecycle artifacts** (2 rules): `lifecycle_reviewer_signoff_missing`, `lifecycle_closure_summary_missing`.
- **E. Gate order + cross-record** (6 rules): `gate_output_missing`, `gate_in_passed_and_failed`, `gate_order_violation`, `duplicate_work_order_id`, `duplicate_action_id`, `action_log_orphan`.
- **F. Pseudocode-in-YAML** (1 rule): `pseudocode_marker_in_yaml`.
- **G. Undocumented deviation** (1 rule): `undocumented_deviation`.

Total new rule names exposed to consumers: **25**.

---

## 3. Native vs Non-Native After v0.2

**Now native (catches 243/243 stress-suite augmentation cases):**

- status enum + agent role enum
- lifecycle ordering, initial-state requirement, duplicate terminal detection
- status / directory consistency
- reviewer signoff file presence
- closure summary file presence
- gate ordering vs `required_gates`
- gate output presence (`command_outputs_summary`)
- gate consistency (`gates_passed` ∩ `gates_failed` = ∅)
- duplicate IDs across directories and across action logs
- action log orphan detection
- secret patterns (AWS, GitHub, GitHub PAT, private-key markers)
- dangerous command patterns (sudo, chmod root, curl, git force-push, git rebase, git filter-branch, rm-rf outside temp, audit-artifact deletion)
- canon-touch role enforcement (builder/test/docs may not touch canon)
- canon change without `CANON BREAK` marker
- invariant change without `human_approval_required`
- authorization-path change by non-security role
- replay-path change by non-security/release role
- canon + implementation in same work order
- pseudocode markers in YAML body
- undocumented deviation (forbidden read with empty deviations field)

**Stress-suite-only after v0.2:**

None. Every v0.1-stress-suite augmentation is now native.

**Cannot be guaranteed without OS-level enforcement (deferred to a future hardening phase):**

- filesystem isolation (the validator inspects records, not OS calls)
- true command execution verification (the validator scans recorded `commands_run` text, not actual processes)
- hidden unlogged commands (an unrecorded command is invisible)
- hidden reads outside `files_read` (an unrecorded read is invisible)
- secret exfiltration outside YAML fields (only the recorded surface is scanned)
- network behavior outside `commands_run` text (no network observation)
- process-level containment (no sandbox, namespace, or seccomp)
- cryptographic attestation of action log or work order integrity (no signing)
- cross-machine determinism of the records themselves (the stress suite covers this within its own sandboxes; the validator does not re-verify on a second machine)

**Intentionally deferred (out of scope for v0.2):**

- a formal waiver mechanism for `allowed_files` / `forbidden_files` amendments at closure (operational lesson L-3 from `WO-2026-05-07-001`); v0.2 still treats amendments as exceptions executed under direct human-owner authority.
- a second reviewer identity (operational lesson L-1); the human-owner-as-reviewer fallback is not codified yet.
- splitting `forbidden_files` into `forbidden_writes` and `forbidden_reads` (operational lesson L-2); the stress suite handled this through human-owner amendment.

---

## 4. Validator Performance Impact

| Measurement | Pre-v0.2 | Post-v0.2 |
| --- | ---: | ---: |
| `make workforce-check` on the live tree | < 100 ms | < 150 ms |
| Stress suite parallel runtime (900 checks, 3 sandboxes) | 10.4 s | 11.2 s |

The augmentations add O(work_orders × action_logs) work in the worst case. On the live tree (1 work order, 2 action logs) the overhead is negligible. On the stress sandboxes (1 work order, 1 action log per case, 300 cases per sandbox) the overhead is < 1 second per sandbox — within the budget for an opt-in stress run.

Validator complexity remains maintainable: the v0.2 changes added approximately **400 lines** to `tools/check_workforce.py`, bringing the file to roughly **870 lines**. The augmentation block is structurally separate and clearly delimited.

---

## 5. Backward Compatibility

- Existing rule names (`out_of_scope_change`, `forbidden_file_touched`, `forbidden_file_read`, `required_gate_missing`, `missing_self_verification`, `missing_human_approval`, `missing_action_log`, `missing_field`, `missing_directory`, `missing_template`, `unreadable_yaml`) are unchanged.
- Existing exit code semantics are unchanged: 0 on clean, 1 on violation, 2 on usage error.
- `--no-augmentations` flag exists as a one-cycle migration escape hatch and is not recommended for production use.
- The live workforce tree (`WO-2026-05-07-001` closed; `AL-…-reviewer.yaml` and `AL-…-closure.yaml` action logs; `WO-…-closure-summary.md`) passes the hardened validator with no violations. Backward-compat verified.

---

## 6. Re-run Verification

```text
make no-pseudocode      → OK: scanned 33 markdown files; clean.
make workforce-check    → OK (1 work order, 2 action logs, 1 closed).
make workforce-stress   → OK (900 checks, coverage_gap=0, duration_ms=11165).
```

All three gates pass after the migration.

---

## 7. Aggregate Outcome

- v0.1 uncovered-gap inventory: **243** stress-suite augmentation cases the native validator missed.
- v0.2 uncovered-gap inventory: **0**.
- Reduction: **100.00%** of the previously identified gap.
- Cross-sandbox identity: all 300 (rule, variant) pairs agree across all three sandboxes.
- Suite mismatches: 0 (the comprehensive validator and the native validator now agree on every case in the stress suite).
- Live workforce tree: passes hardened validator with no new violations.

---

## 8. Final Statement

The 243 augmentation findings recorded by the v0.1 stress suite have been migrated into native validator rules. The stress suite continues to function as a regression harness: it now reports `coverage_gap=0` because the native validator catches every case the comprehensive validator catches. Future stress findings (rules the comprehensive validator catches but the native validator misses) will resurface as a non-zero coverage gap and will be candidates for a future v0.3 hardening cycle.

Native validation does not replace OS-level enforcement. Filesystem isolation, command execution verification, network containment, and cryptographic attestation remain outside the validator's reach and are explicitly listed as gaps. The closure of those gaps belongs to a future Governed Agent Execution phase per `MASTER-ROADMAP-v0.1.md` Phase III.

— END Workforce Hardening v0.2 Report —
