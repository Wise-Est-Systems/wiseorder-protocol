# WORKFORCE SANDBOX STRESS v0.1
## 900-Check Isolation Test For Governed Agent Execution

**Status:** v0.1 — operational specification, normative for the optional `make workforce-stress` target.
**Scope:** Defines a deterministic, sandboxed stress harness that exercises the workforce governance rules against 300 cases per sandbox across 3 isolated cloned sandboxes, for 900 total checks. Does not modify WiseOrder semantics, Intellagent runtime semantics, canonicalization behavior, vectors, or existing release gates. Adds one optional Makefile target.
**Companion documents:** `WORKFORCE-EXECUTION-RUNTIME-v0.1.md` (lifecycle and validator), `AGENT-GOVERNANCE-WORKFORCE-v0.1.md` (roles), `MASTER-ROADMAP-v0.1.md` (Phase III references sandboxed workforce execution).

> **Core thesis.** A workforce governance system is not credible until it survives repeated isolated execution without leaking scope, skipping gates, corrupting canon, or mutating forbidden surfaces. This document specifies the first sandboxed stress suite that mechanically exercises that claim.

---

## 1. Purpose

The stress suite asks one question, deterministically, 900 times: *given a fixture work order and action log, does the workforce enforcement layer classify the fixture the way the documented rules require?*

It is not a verification of the canonicalization layer, the runtime, the vectors, or any release artifact. It is a verification of the workforce records-checking surface — `tools/check_workforce.py` plus the augmentations defined in §5 — under repeated isolated execution.

The suite is opt-in. It does not run as part of `make ci`. It is an optional `make workforce-stress` target intended for periodic execution against substantive workforce changes.

---

## 2. Scope

The suite covers three layers:

1. **Validator behavior.** Each case is run through the existing `tools/check_workforce.py` validator and its exit code plus reported violations are captured.
2. **Augmented behavior.** The same case is also run through the stress suite's comprehensive validator (validator + augmentations per §5). The comprehensive validator's verdict is the suite's authoritative classification.
3. **Cross-sandbox identity.** The same fixtures executed in three independently-cloned sandboxes must produce identical verdicts; cross-sandbox divergence is itself a suite failure.

Out of scope:

- the canonicalization layer
- the Intellagent runtime
- the conformance vectors
- the release law
- the cross-language canonicalization stress (covered by `make canonicalization-check`)

The stress suite is a workforce-only stress; it does not exercise any other gate.

---

## 3. Sandbox Architecture

The suite creates three independent sandboxes per run:

- `sandbox-001`
- `sandbox-002`
- `sandbox-003`

Each sandbox is a temporary directory created via `tempfile.mkdtemp(prefix="workforce-stress-<sandbox-id>-")`. The path is recorded in the per-sandbox report. Sandboxes are removed at the end of the run unless the `--preserve-sandboxes` flag is passed.

Each sandbox contains the minimal subset required to run `tools/check_workforce.py`:

```text
<sandbox-root>/
  tools/check_workforce.py            (copied from the main repo)
  workforce/
    README.md                          (copied)
    templates/work_order.yaml          (copied)
    templates/action_log.yaml          (copied)
    templates/self_verification.md     (copied)
    work_orders/
      open/
      closed/
      rejected/
    action_logs/
    reports/
```

**Isolation invariants:**

- No sandbox path overlaps with another sandbox path.
- No case writes outside its own sandbox directory.
- The main repository's `workforce/` is read-only to the suite; the suite never modifies the main `workforce/` tree.
- Final reports are written to `reports/workforce_sandbox_stress/` in the main repo; this is the only main-repo write.
- Sandboxes contain only the minimal subset above; they are not full repository clones.

**Parallelism:** the three sandboxes run in parallel via `concurrent.futures.ProcessPoolExecutor` with three worker processes. Each process owns one sandbox; no shared mutable state.

---

## 4. Case Categories

Each sandbox runs 300 cases. The 300 are produced from 100 unique rule templates (rule IDs `A1`–`J10`) with 3 deterministic variants each (`V0`, `V1`, `V2`). Variants differ only in non-substantive fields (IDs, timestamps, file-name suffixes); a variant's expected classification is identical to its base template's classification.

The 100 rule templates partition into ten categories of ten:

### A. Work order structure (10 rules)

`A1` valid work order passes. `A2` missing `work_order_id` fails. `A3` missing `agent_role` fails. `A4` missing `allowed_files` fails. `A5` malformed `allowed_files` (scalar instead of list) fails. `A6` missing `forbidden_files` fails. `A7` invalid `status` enum fails. `A8` invalid lifecycle transition fails. `A9` missing `status_history` fails. `A10` missing human approval where required fails.

### B. Action log (10 rules)

`B1` valid action log passes. `B2` missing `action_id` fails. `B3` missing `work_order_id` fails. `B4` `work_order_id` does not match work order fails. `B5` missing `files_read` fails. `B6` missing `files_changed` fails. `B7` missing `commands_run` fails. `B8` missing `gates_passed` fails. `B9` undeclared deviation fails. `B10` missing `self_verification_statement` fails.

### C. Scope enforcement (10 rules)

`C1` changed file inside `allowed_files` passes. `C2` changed file outside `allowed_files` fails. `C3` forbidden file in `files_read` fails. `C4` forbidden file in `files_changed` fails. `C5` forbidden directory glob fails. `C6` recorded forbidden read fails. `C7` recorded forbidden change fails. `C8` allowed glob expansion works. `C9` deny-by-default outside `allowed_files` works. `C10` closed order with forbidden touch fails.

### D. Gate enforcement (10 rules)

`D1` required gates subset passes. `D2` missing `make no-pseudocode` from `gates_passed` fails. `D3` missing `make workforce-check` from `gates_passed` fails. `D4` missing `make canonicalization-check` when required fails. `D5` gate listed but failed fails. `D6` gate listed without output summary fails (augmentation). `D7` required gate order enforced when declared fails on out-of-order. `D8` skipped gate fails. `D9` false-success claim (gate in passed and failed lists) fails. `D10` closure without green gates fails.

### E. Closure (10 rules)

`E1` valid closure passes. `E2` closure without action log fails. `E3` closure without self-verification file fails. `E4` closure without reviewer signoff fails (augmentation). `E5` closure without human approval when required fails. `E6` closure while work order still open fails (status mismatch with directory). `E7` closure with unresolved required gates fails. `E8` closure with undocumented deviation fails (augmentation). `E9` closure with forbidden files touched fails. `E10` closure-summary mismatch fails (augmentation: closure_summary path declared but file absent).

### F. Drift / canon (10 rules)

`F1` `SPEC.md` touch by Builder Agent fails (out-of-scope). `F2` `vectors/**` touch by Builder Agent fails. `F3` `intellagent_runtime/**` touch by Reviewer Agent fails. `F4` doc inventing runtime behavior fails when detectable by markers (augmentation: pseudocode markers in YAML payload). `F5` canonicalization change without `CANON BREAK` marker fails (augmentation). `F6` invariant change without human approval fails. `F7` release law change without approval fails. `F8` authorization semantics change without security review fails (augmentation). `F9` replay semantics change without release-continuity review fails (augmentation). `F10` work order attempting canon and implementation change in one order fails (augmentation: both `SPEC.md` and a runtime path in `allowed_files`).

### G. Security (10 rules)

`G1` AWS-style key in action log fails (augmentation). `G2` GitHub-style token in work order fails (augmentation). `G3` `chmod` in `commands_run` without approval fails (augmentation). `G4` `curl` in `commands_run` without approval fails (augmentation). `G5` `git push --force` in `commands_run` fails (augmentation). `G6` deletion of audit artifact recorded without approval fails (augmentation). `G7` `BEGIN PRIVATE KEY` marker in YAML fails (augmentation). `G8` shell command with `curl` fails unless explicitly approved (augmentation). `G9` `rm -rf` outside sandbox temp path fails (augmentation). `G10` `sudo` in `commands_run` always fails (augmentation).

### H. Mutation / resilience (10 rules)

`H1` random required-field deletion fails. `H2` random `status` mutation to invalid enum fails. `H3` `work_order_id` mismatch between work order and action log fails. `H4` shrunk `allowed_files` reveals prior out-of-scope changes fails. `H5` expanded `forbidden_files` catches prior reads fails. `H6` duplicate `action_id` fails (augmentation). `H7` duplicate `work_order_id` across `open/` + `closed/` fails (augmentation). `H8` malformed YAML fails closed (augmentation). `H9` empty file fails closed. `H10` unknown agent role fails (augmentation: enum check).

### I. Positive lifecycle (10 rules)

`I1` `drafted → approved` recorded passes. `I2` `approved → assigned` recorded passes. `I3` `assigned → executed` recorded passes. `I4` `executed → self-verified` recorded passes. `I5` `self-verified → gate-checked` recorded passes. `I6` `gate-checked → reviewed` recorded passes. `I7` `reviewed → human_approved` recorded passes. `I8` `human_approved → closed` recorded passes. `I9` `rejected` lifecycle properly logged passes. `I10` waiver / amendment lifecycle with explicit human approval passes.

### J. Cross-sandbox (10 rules; per-sandbox cases plus aggregation invariants)

Per-sandbox: `J1`–`J10` are smoke cases that record sandbox-internal properties (sandbox dir is the expected one, sandbox has the expected structure, sandbox writes only inside its own root, etc.). Aggregation evaluates the cross-sandbox properties globally (see §8). A failure in any per-sandbox J case fails the suite; a failure in any aggregation-level J property fails the suite.

---

## 5. Comprehensive Validator

The comprehensive validator is the suite's authoritative classifier. It is the existing `tools/check_workforce.py` plus the augmentations below. Augmentations live only in the stress script (`tools/workforce_sandbox_stress.py`) and are not added to the existing validator.

**Augmentations:**

- **Status enum check.** `status` must be one of `drafted`, `approved`, `assigned`, `executed`, `self-verified`, `gate-checked`, `reviewed`, `amended`, `human_approved`, `closed`, `rejected`.
- **Agent role enum check.** `agent_role` must be one of `canon_guardian`, `builder`, `test`, `docs`, `reviewer`, `security`, `release`, `outreach`.
- **Lifecycle order check.** `status_history` must contain at minimum `drafted` followed by `approved`; if `closed`, must contain a `closed` entry; entries must be ordered such that earlier states precede later ones in the documented partial order.
- **Duplicate ID check.** No `work_order_id` may appear in more than one of `open/`, `closed/`, `rejected/`. No `action_id` may appear twice across `action_logs/`.
- **Empty / malformed file check.** A file under `workforce/` whose YAML body is empty or unparseable in the flat-YAML subset (no `key: value` lines and no `  - item` lines) is treated as a failure.
- **Reviewer signoff file check.** A closed work order requires a `workforce/reports/<work_order_id>/review.md` file (per `WORKFORCE-EXECUTION-RUNTIME-v0.1.md` §19).
- **Closure summary file check.** A closed work order requires a `workforce/reports/<work_order_id>-closure-summary.md` file when `expected_outputs` declares one.
- **Documented deviation check.** Every entry in an action log's `deviations` field must be non-empty if any of its `files_read` matches a forbidden pattern; an undocumented deviation (a forbidden read with empty deviations list) fails.
- **Pseudocode marker check.** Any of `...` (ellipsis statement), bare `pass`, `return ...`, `TODO`, `NotImplemented`, `NotImplementedError` appearing in any string field of a workforce YAML fails. (This is the same marker set as `tools/check_no_pseudocode.py` but applied to YAML contents rather than to markdown code blocks.)
- **Secret pattern check.** Any of the following regular expressions matching any string field fails: AWS access key (`AKIA[A-Z0-9]{16}`); GitHub token (`ghp_[A-Za-z0-9]{20,}` or `github_pat_[A-Za-z0-9_]{20,}`); generic API key marker (`(?i)api[_-]?key\s*[:=]\s*['\"]?[A-Za-z0-9]{16,}`); generic password marker (`(?i)password\s*[:=]\s*['\"]?[^'\"\\s]{6,}`); private-key marker (`BEGIN [A-Z]+ PRIVATE KEY`).
- **Dangerous command check.** Any entry in `commands_run` matching any of the following patterns fails unless the case fixture's status_history contains an explicit human-owner approval note for the command: `\bsudo\b`; `\bchmod\s+[0-7]+\s+/`; `\bcurl\b`; `\brm\s+-rf\b` outside a path beginning with `/tmp/` or `/var/folders/`; `git\s+push\s+(--force|-f)\b`; `git\s+rebase\b`; `git\s+filter-branch\b`. `sudo` is always a failure regardless of approval (it cannot be safely approved by an agent record).
- **Audit-artifact deletion check.** Any command in `commands_run` matching `rm\s+.*workforce/action_logs/` or `rm\s+.*workforce/reports/` fails (audit artifacts are non-deletable per `WORKFORCE-EXECUTION-RUNTIME-v0.1.md` §21).
- **Gate output presence check.** Every entry in `gates_passed` must have a corresponding non-empty entry in `command_outputs_summary`.
- **Gate consistency check.** No gate may appear in both `gates_passed` and `gates_failed` simultaneously.

The comprehensive validator returns `pass` when no validator violation and no augmentation violation is raised, and `fail` otherwise. Reasons (validator and augmentation) are concatenated into the case result.

---

## 6. Validator Coverage Gap Reporting

For each case, the suite records two outcomes:

- `validator_outcome`: what `tools/check_workforce.py` produces (subprocess exit code).
- `observed_outcome`: what the comprehensive validator (validator + augmentations) produces.

When the two disagree, the case is recorded as a *coverage gap*. Coverage gaps are not suite failures by themselves; they are evidence that the existing validator does not enforce a documented rule that the comprehensive validator does. The aggregate report enumerates every coverage gap with rule ID, sandbox ID, and the augmentation that fired.

The expectation: a future hardening work order migrates augmentations from the stress script into the existing validator, narrowing the coverage gap toward zero.

---

## 7. Test Oracle Honesty

The comprehensive validator is the suite's test oracle. The suite's correctness depends on the oracle being correct.

To prevent silent oracle bugs:

- The oracle is implemented in pure Python in the stress script and is short enough to inspect by reading.
- Every augmentation in §5 is traced to the documented rule it enforces (citation in the script's comments).
- Every case has its `expected_outcome` set from the rule template, not from the oracle's output. If `expected_outcome` and the oracle's verdict disagree, the suite fails — surfacing oracle bugs immediately on first run.
- The oracle is deterministic: same inputs produce same outputs; cross-sandbox identity is enforced by aggregation (see §8).

A case where `expected_outcome` and the oracle disagree is recorded as a `mismatch` and counted toward the suite's failure tally.

---

## 8. Required Reports

The suite writes the following reports under `reports/workforce_sandbox_stress/`:

- `aggregate.json` — machine-readable aggregate.
- `aggregate.md` — human-readable aggregate.
- `sandbox-001.json`
- `sandbox-002.json`
- `sandbox-003.json`

Each per-sandbox JSON contains:

- `sandbox_id`
- `sandbox_path` (temp path; reported even after cleanup so the location is auditable)
- `total_checks` (must equal 300)
- `expected_pass_count`
- `expected_fail_count`
- `observed_pass_count`
- `observed_fail_count`
- `mismatches` (list of case IDs whose `observed_outcome != expected_outcome`)
- `case_ids` (every case ID executed in this sandbox, in deterministic order)
- `duration_ms`
- `repo_source_sha256` (the SHA-256 of the source files copied into the sandbox, computed deterministically over their content in sorted-path order)
- `report_sha256` (the SHA-256 of this report file's content with `report_sha256` field zeroed during computation)
- `cases` (full list of case results: case_id, rule_id, category, name, variant, expected_outcome, observed_outcome, observed_reasons, validator_outcome, validator_reasons, matched, duration_ms)

The aggregate JSON contains:

- `total_checks` (must equal 900)
- `total_expected_pass`
- `total_expected_fail`
- `total_observed_pass`
- `total_observed_fail`
- `total_mismatches`
- `coverage_gap_count` (cases where validator_outcome != observed_outcome)
- `cross_sandbox_identity` (object with one key per rule_id whose value is `true` if all three sandboxes' results agreed, `false` otherwise; the suite fails if any value is `false`)
- `per_sandbox` (list of three references, each containing `sandbox_id`, `report_sha256`, `total_checks`, `mismatches`)
- `failing_case_ids` (every case ID across all sandboxes whose `matched` is `false`)
- `started_at` / `finished_at` (ISO-8601 UTC)
- `duration_ms`

The aggregate Markdown summarizes the JSON in a human-readable form: total counts, mismatches per sandbox, coverage gap with the augmentation that fired for each gap case, the strongest validator finding (most-frequently-fired augmentation), and a list of the first 25 failing case IDs.

---

## 9. Required Make Targets

Adds one target:

- `make workforce-stress` — runs `python3 tools/workforce_sandbox_stress.py`, writes the reports listed in §8, exits 0 if every case in every sandbox matches expectation and every cross-sandbox identity property holds.

`make ci` is **not** modified. The stress suite is opt-in.

---

## 10. What This Suite Validates

- The existing validator's behavior on 100 distinct rule templates × 3 variants × 3 sandboxes (900 invocations).
- The comprehensive validator's behavior on the same 900 cases against documented expectations.
- Cross-sandbox determinism: identical fixtures produce identical verdicts in three independent sandboxes.
- Sandbox isolation: no sandbox writes outside its own root.
- Parallel execution under `ProcessPoolExecutor`: no shared mutable state corrupts a sandbox's results.

---

## 11. What This Suite Does NOT Validate

- Filesystem-level enforcement: the suite does not exercise OS-level read/write blocking; agent records are checked, not OS calls.
- Cryptographic integrity: action logs are not signed; the suite does not verify signatures it does not produce.
- Cross-language replay: the suite is Python-only and does not exercise any non-Python validator.
- Cross-machine determinism: the suite runs in one process tree on one machine.
- Real agent behavior: the cases are fixtures, not the output of a real agent.
- Canonicalization, runtime, or vector behavior: out of scope.
- Network egress: the suite does not exercise network controls.
- Sandbox security beyond directory isolation: no chroot, no seccomp, no namespace isolation.

---

## 12. Non-Goals

- introduce a runtime change
- modify `tools/check_workforce.py`
- add a CI dependency that blocks `make ci`
- claim that the workforce runtime is sandbox-safe at the OS level
- claim that the comprehensive validator is complete
- replace the existing validator with the comprehensive validator
- promise specific runtime budgets across machines

---

## 13. Final Law

> Workforce governance is credible only when it survives repeated, isolated, deterministic execution against fixtures it did not author. This suite is the first such test. It does not prove that the runtime is sandboxed; it proves only that the records-checking surface is deterministic, identity-stable across isolated sandboxes, and honest about its coverage gaps.

— END v0.1 —
