# Closure Summary — WO-2026-05-07-009

**Work order:** `WO-2026-05-07-009`
**Title:** Upgrade REAL-AGENT-RUNTIME-v0.1 to v0.2 with bounded local-subprocess execute mode (builder, P3 hardening cycle)
**Agent role:** `builder`
**Agent identity:** `builder-01`
**Closed at:** 2026-05-08T14:25:00Z
**Closed by:** human owner (`henry-wayne-wise-iii`)
**Governed by:** `WORKFORCE-EXECUTION-RUNTIME-v0.1.md`, `AGENT-GOVERNANCE-WORKFORCE-v0.1.md`, `WORKFORCE-HARDENING-v0.2.md`, `REAL-AGENT-RUNTIME-v0.1.md`.

---

## 1. Purpose

This document records the closure of `WO-2026-05-07-009`, the sixth governed execution cycle against the workforce runtime, the first builder work order, and the first hardening cycle that converts a previously dry-run-only runtime into a bounded subprocess-execution runtime. It states what the work order produced, which gates ran, what scope deviations occurred (none), what was proven and not proven, the basis on which human approval was granted, and the v0.2 → v0.3 enforcement gaps that remain open after this closure.

The closure summary is the audit-trail anchor that connects the work order, the builder action log, the closure action log, the self-verification block, the deliverable `REAL-AGENT-RUNTIME-v0.2.md`, the implementation extension in `tools/real_agent_runtime.py`, the Makefile additions, the v0.2 reports, the gate results, and the human-owner approval into a single, file-grounded record.

---

## 2. Work Order Objective

> Upgrade `REAL-AGENT-RUNTIME-v0.1` from dry-run policy classification into `REAL-AGENT-RUNTIME-v0.2` by extending `tools/real_agent_runtime.py` with a bounded local-subprocess execute mode under the existing admission, command-policy, filesystem-policy, and manifest layers. Author `REAL-AGENT-RUNTIME-v0.2.md` as the normative spec for the new mode. Preserve every v0.1 refusal behavior. Do not enable autonomy, models, background daemons, or network access. Do not weaken any existing rule. Add a make target `real-agent-execute-check` that exercises the new mode against built-in fixtures and is NOT included in `make ci`.

The objective was scoped to a strictly additive runtime hardening cycle. No SPEC change, no validator semantic change, no governance amendment, no canonicalization-corpus change, no protocol primitive, no new cognition class, and no new constitutional law was authorized. The deliverable specifies and the implementation realizes the smallest possible upgrade from dry-run to real subprocess execution, bounded by `cwd=sandbox`, minimal env, wall-clock timeout, and `shell=False` list-args, with full output capture into the manifest.

---

## 3. Files Produced

The work order produced exactly the following files:

- `REAL-AGENT-RUNTIME-v0.2.md` — top-level governance instrument with all 17 required sections in order, the six explicit-state items in the headline block (v0.2 creates real local subprocess execution; v0.2 does not create autonomous AI planning; v0.2 does not create background agents; v0.2 does not provide kernel-level isolation; v0.2 is still policy-layer containment, not OS-level containment; agents become real only as bounded worker processes executing approved work orders in sandbox copies), the v0.2-vs-v0.1 difference table in §2, the subprocess-boundary specification in §6, the sandbox-tree fingerprint specification in §7, the v0.2 execute allowlist in §8, the environment policy in §10, the manifest extensions in §11, the timeout policy in §12, the failure-mode table in §13, the security non-guarantees in §14, the ten required test cases in §15, the OS-isolation roadmap in §16, and the L-1 through L-10 final-law block in §17.
- `tools/real_agent_runtime.py` — extended with the v0.2 execute-mode surface. New constants: `EXECUTE_ALLOWED_COMMANDS`, `EXECUTE_TIMEOUT_DEFAULT_S`, `EXECUTE_TIMEOUT_HARD_CAP_S`, `EXECUTE_OUTPUT_BYTE_CAP`, `EXECUTE_RUNTIME_VERSION`. New functions: `classify_execute_command`, `_resolve_command_argv`, `_minimal_env`, `_truncate_bytes`, `execute_command`, `_walk_tree_files`, `tree_fingerprint`, `tree_change_set`, `execute_run`, `_execute_fixture_yaml`, `_write_temp_fixture`, ten `_execute_case_*` fixture functions, `run_execute_self_check`, `render_execute_report_md`, `write_execute_reports`, `cmd_execute`, `cmd_execute_check`. Extended `RunManifest` dataclass with seven optional v0.2 fields (`mode`, `replay_mode`, `command_results`, `sandbox_fingerprint_before`, `sandbox_fingerprint_after`, `sandbox_files_changed`, `env_keys`). Extended `main()` with `execute` and `execute-check` subcommands. v0.1 dry-run code paths and refusal codes preserved verbatim.
- `Makefile` — added `.PHONY` entries `real-agent-execute` and `real-agent-execute-check`; added the `real-agent-execute` target with optional WO/AGENT/TIMEOUT/REPLAY/CMD parameters; added the `real-agent-execute-check` target invoking `python3 tools/real_agent_runtime.py execute-check`. The `ci` target is unchanged: `ci: no-pseudocode test conformance interop canonicalization-check`. Neither v0.2 target is added to `make ci`.
- `reports/real_agent_runtime/real_agent_runtime_v0.2.md` — execute-mode self-check fixture report; 10/10 cases pass; markdown rendering with allowlist, forbidden patterns, timeout policy, per-case results table, and per-case JSON detail.
- `reports/real_agent_runtime/real_agent_runtime_v0.2.json` — machine-checkable v0.2 self-check report; 10/10 cases pass; sorted-key JSON.
- `workforce/work_orders/closed/WO-2026-05-07-009.yaml` — closed work order with full status_history (drafted → approved → assigned → executed → self-verified → gate-checked → reviewed → human_approved → closed).
- `workforce/action_logs/WO-2026-05-07-009-builder.yaml` — builder execution action log (predecessor).
- `workforce/action_logs/WO-2026-05-07-009-builder.self_verification.md` — self-verification block.
- `workforce/action_logs/WO-2026-05-07-009-closure.yaml` — closure action log (successor; references the predecessor by id).
- `workforce/reports/WO-2026-05-07-009-closure-summary.md` — this file.

The original `workforce/work_orders/open/WO-2026-05-07-009.yaml` was moved to the `closed/` directory; the original copy in `open/` was deleted as part of the move.

No file in `forbidden_files` (`runtime/**`, `intellagent_runtime/**`, `vectors/**`, `canonicalization/**`, `SPEC.md`) was read or written.

---

## 4. Gates Executed

Required gates declared by the work order:

- `make no-pseudocode`
- `make workforce-check`
- `make real-agent-check`
- `make real-agent-dry-run`
- `make real-agent-execute-check`

All five gates ran at execution time and again at closure time. Both runs exited 0.

Pre-closure run:
- `make no-pseudocode` — exit 0; 45 markdown files scanned (the +2 vs. WO-005 closure are `REAL-AGENT-RUNTIME-v0.2.md` and `reports/real_agent_runtime/wo005_dry_run_report_v0.1.md`); no pseudocode markers in any Python code block.
- `make workforce-check` — exit 0; 6 work orders, 13 action logs, 5 closed at run time; new builder execution log AL-2026-05-07-009 parses with required fields.
- `make real-agent-check` — exit 0; 10/10 v0.1 admission fixtures pass; configuration check clean.
- `make real-agent-dry-run` — exit 0; built-in dry-run ACCEPTED for canon_guardian-01 on synthetic fixture; 2/2 commands allowed; 0 violations.
- `make real-agent-execute-check` — exit 0; 10/10 v0.2 execute-mode fixtures pass.

Post-closure run:
- `make no-pseudocode` — exit 0 (re-run after closure summary written; same 45-file scope).
- `make workforce-check` — exit 0; 6 work orders, 14 action logs, 6 closed; new closed WO-009 satisfies all closure invariants.
- `make real-agent-check` — exit 0; 10/10.
- `make real-agent-dry-run` — exit 0; built-in dry-run ACCEPTED.
- `make real-agent-execute-check` — exit 0; 10/10.

`make ci` was not declared as required for this work order and was not executed. Its absence is intentional and consistent with L-9 of `REAL-AGENT-RUNTIME-v0.2.md`: the v0.2 targets remain opt-in.

---

## 5. Scope Violations

**None.** No deviation was recorded. No file in `forbidden_files` was read or written. No file outside `allowed_files` was changed. No amendment of `allowed_files` or `forbidden_files` was required for closure. The work order closed cleanly on the first attempt with no validator violations and no waiver claims.

---

## 6. Proven Guarantees

This closure proves that a builder hardening cycle can convert a dry-run-only runtime into a bounded subprocess-execution runtime without weakening any v0.1 refusal behavior, any v0.1 admission rule, any v0.1 manifest field, or any v0.1 refusal code.

- **G1.** The deliverable `REAL-AGENT-RUNTIME-v0.2.md` exists at top-level with all 17 required sections in order, each non-empty.
- **G2.** The six required explicit-state items appear verbatim in the headline block and are reinforced in §3, §4, §5, §6, §10, and §17 (L-1 through L-10).
- **G3.** `tools/real_agent_runtime.py` v0.1 dry-run code paths are preserved verbatim. The v0.1 self-check fixture suite (`make real-agent-check`) still reports 10/10 fixtures pass after the upgrade. The configuration check is still clean. Dry-run admission still refuses every non-(approved/assigned) work order with the v0.1 refusal codes.
- **G4.** The v0.2 execute mode runs only allowlisted commands (the 10 entries in §8 of the spec). Forbidden patterns are blocked deny-first, before any subprocess is spawned. The fixture `forbidden_command_blocked_before_subprocess` verifies that for `curl https://example.com`, `git push origin main`, and `rm -rf /` no subprocess is invoked (manifest's `argv` empty for all three) and `commands_blocked` length is 3.
- **G5.** The v0.2 subprocess execution boundary uses `subprocess.run` with `cwd=<sandbox>`, `env=_minimal_env()` (PATH + LC_ALL=C + LANG=C only), `stdin=DEVNULL`, `stdout=PIPE`, `stderr=PIPE`, `timeout=<bounded>`, `shell=False`, and `check=False`. The fixture `manifest_records_stdout_stderr_exit_duration_cwd` verifies that every command_results entry contains stdout, stderr, exit_code, duration_ms, and cwd, with `cwd` equal to the manifest's `sandbox_path`.
- **G6.** Wall-clock timeout enforcement works. The fixture `command_timeout_recorded` invokes `make no-pseudocode` with `timeout=0.001` and observes `status="timed_out"`, `timed_out=true`, `exit_code=null`. The hard cap is 300s and the floor is 0.001s; both clamp caller-supplied timeouts.
- **G7.** Source repository is unchanged across execute mode. `repo_fingerprint_before == repo_fingerprint_after` for every fixture, including the timeout fixture and the forbidden-command fixture. The fixture `source_repo_unchanged_after_execute` verifies this against an independently-computed fingerprint outside the manifest.
- **G8.** Sandbox tree fingerprinting works. `tree_fingerprint(sandbox)` produces a deterministic sha256 over sorted (relpath, file_sha256) tuples; `tree_change_set` diffs before/after maps into added/modified/removed sets. Manifests record both fingerprints and the union of changes as `sandbox_files_changed`.
- **G9.** Replay mode admits a closed work order ONLY when the only refusal would be `status_not_admissible` AND status is exactly `"closed"`. Every other refusal still applies. The fixture `closed_refused_unless_replay_mode` verifies both halves: refusal without `--replay`, admission with `--replay`, and `replay_mode: true` recorded in the manifest.
- **G10.** All five required gates green at execution time and at closure time, under the canonical interpreter.

This closure does not prove that the runtime survives kernel-level adversarial pressure; the sandbox is `shutil.copytree`, not a kernel container. It proves that the *policy boundary* of the runtime now extends to bounded subprocess invocation with full output capture and that future hardening cycles have a clear migration target (R-2 retargeted to v0.3+).

---

## 7. Remaining Unknowns

This closure resolves the dry-run-only enforcement gap by introducing bounded subprocess execution. It does not resolve, but bounds:

- **R-1 (now closed at v0.2).** Real subprocess execution under sandbox isolation. v0.2 implements this for the bounded allowlist; v0.3+ may extend.
- **R-2 (open).** OS-level isolation. The sandbox remains a directory copy. UNIX user namespaces, jails, containers, microvms remain future enforcement.
- **R-3 (open).** Cryptographic attestation of manifests. Manifests are unsigned JSON. AGENT-IDENTITY-v0.1.md (audit P3) addresses this.
- **R-4 (open).** Hash-chained manifests. Each manifest is independent.
- **R-5 (open).** Resource limits beyond wall-clock. Memory, CPU, FD count, process count are unbounded.
- **R-6 (open).** Cross-validation between `tools/check_workforce.py` and the runtime.
- **R-7 (open).** Adversarial pressure suite for the execute-mode surface.
- **R-8 (retargeted).** Manifest schema validator. Now retargeted from the v0.1 16-field schema to the v0.2 16+7-field schema.
- **R-9 (open).** Inclusion in `make ci`. v0.2 explicitly remains opt-in.
- **R-10 (open).** Per-identity capability matrix beyond the current uniform allowlist.

Beyond these, the audit's bounded ten-document queue is unchanged: 2 P1 + 3 P2 + 3 P3 + 1 P0 remaining (this work order is a hardening cycle, not a queue-document; it does not advance the queue counter).

---

## 8. Human Approval Basis

The human owner granted closure on the basis of the following file-grounded findings:

- The deliverable exists at the declared top-level path `REAL-AGENT-RUNTIME-v0.2.md`.
- All 17 required sections are present, in order, each non-empty.
- The six required explicit-state items appear verbatim in the headline block and are reinforced throughout.
- The runtime tool is extended with the execute-mode surface; v0.1 dry-run code paths are preserved.
- The Makefile gained `real-agent-execute` and `real-agent-execute-check` targets; `ci` is unchanged.
- Both v0.2 reports exist at `reports/real_agent_runtime/real_agent_runtime_v0.2.{md,json}` with 10/10 fixtures pass.
- The action logs (`AL-2026-05-07-009-builder` and `AL-2026-05-07-009-closure`) record every read, write, command, gate result; deviations field is empty in both.
- The self-verification block answers all ten questions explicitly with no scope violations.
- All five required gates ran and exited 0 at execution time and at closure time.
- No file in `forbidden_files` was read or written.
- The rollback plan in the closed work order is intact and executable.

Approval is recorded in `status_history` with state `human_approved`, actor `henry-wayne-wise-iii`, timestamp `2026-05-08T14:22:00Z`. The on-disk record is the basis of closure.

---

## 9. Why Closure Was Allowed

Closure was allowed because the closure criteria in `WORKFORCE-EXECUTION-RUNTIME-v0.1.md` §20 plus the work-order's own closure criteria were satisfied:

- objective completed as stated (execute mode exists, subprocess execution works for allowlisted commands, forbidden commands blocked before subprocess, source repo unchanged during execute tests, manifests include command results, timeout behavior tested, both v0.2 reports exist, all five required gates green, work order moved to closed/, replay continuity preserved).
- `allowed_files` respected on `files_changed` (every changed file matches one of: `REAL-AGENT-RUNTIME-v0.1.md`, `REAL-AGENT-RUNTIME-v0.2.md`, `tools/real_agent_runtime.py`, `tests/**`, `reports/real_agent_runtime/**`, `workforce/**`, `Makefile`).
- `forbidden_files` untouched on both `files_read` and `files_changed` (no `runtime/**`, `intellagent_runtime/**`, `vectors/**`, `canonicalization/**`, `SPEC.md` access).
- every gate listed in `required_gates` is in `gates_passed`; `gates_failed` is empty in both action logs.
- both action logs (builder execution and closure) written and committed alongside the change.
- self-verification block completed; every question answered explicitly with no scope or canon violation.
- closure summary present at this path.
- lifecycle ordering monotonic per validator rank.
- human approval recorded in `status_history` with state `closed` and non-empty actor.

This work order required no amendment of `allowed_files` or `forbidden_files`. The disciplined runtime-only hardening scope and the explicit avoidance of canon-adjacent paths kept the closure cycle clean.

---

## 10. Operational Lessons

Two operational observations emerged from this cycle. They are not candidate amendment work orders; they are recorded continuity notes.

- **L-8. v0.2 fixture timeouts via tight wall-clock are a reliable testing primitive.** The `command_timeout_recorded` fixture invokes `make no-pseudocode` with `timeout=0.001` to force a `subprocess.TimeoutExpired`. This works because `make` plus `python3` startup easily exceeds 1ms. It is more reliable than introducing a `sleep` command into the allowlist for the sole purpose of testing timeout, and it avoids broadening the allowlist beyond what production needs. Future timeout tests should follow this pattern.

- **L-9. Replay mode is a forensic-replay capability, not a closure-undo capability.** The `--replay` flag admits a closed work order for re-execution under v0.2 execute mode, but it does NOT modify the closed work order's lifecycle, does NOT append to its action log, and records `replay_mode: true` in the manifest. Forensic re-runs are explicit in the audit trail. A reviewer who sees `replay_mode: true` knows the work order's status was bypassed by the operator's choice, not by a runtime bug. This is a positive lesson — the runtime makes the bypass surface visible — and does not require an amendment work order.

---

## 11. Required Follow-Up Work

The audit's bounded queue is unchanged by this closure (this is a hardening cycle, not a queue-document). The following items remain unauthorized:

**Audit-queue P1 batch (closure blockers — 2 of 3 remaining):**
- `REVIEWER-IDENTITY-v0.1.md`
- `AUDIT-READ-GRANTS-v0.1.md`

**Audit-queue P2 batch — 3 of 3 remaining.**
**Audit-queue P3 batch — 3 of 3 remaining.**
**Audit-queue P0 — 1 of 1 remaining.**

**Hardening-cycle follow-ups created or retargeted by this closure:**
- **R-2 (carry-forward to v0.3+):** OS-level sandbox isolation (UNIX user namespaces, jails, containers, microvms).
- **R-3 (carry-forward):** Cryptographic attestation of manifests.
- **R-4 (carry-forward):** Hash-chained manifests.
- **R-5 (carry-forward):** Resource limits beyond wall-clock.
- **R-6 (carry-forward):** Cross-validation between `tools/check_workforce.py` and the runtime.
- **R-7 (carry-forward):** Adversarial pressure suite for execute mode.
- **R-8 (retargeted):** Manifest schema validator now applies to the v0.2 schema (16 v0.1 fields plus 7 v0.2 extension fields).
- **R-9 (carry-forward):** Inclusion in `make ci`.
- **R-10 (carry-forward):** Per-identity capability matrix.

None of R-2 through R-10 is authorized by this closure.

---

## 12. Final Closure Statement

Work order `WO-2026-05-07-009` is closed. The audit-trail anchor for the closure is this file plus the ten files it cites in §3. The deliverable `REAL-AGENT-RUNTIME-v0.2.md` is on disk at the top-level path, contains every required section and explicit-state item, specifies the subprocess execution boundary, the sandbox boundary, the command policy, the filesystem policy, the environment policy, the manifest extensions, the timeout policy, the failure modes, the security non-guarantees, the ten required tests, the OS-isolation roadmap, and the L-1 through L-10 final-law block. `tools/real_agent_runtime.py` is the canonical implementation; v0.1 dry-run code paths are preserved verbatim and v0.2 execute mode is layered additively. The Makefile gained two opt-in targets without touching `make ci`. Both v0.2 reports record 10/10 fixture pass at execution time and at closure time. No SPEC change occurred; no validator semantic was altered; no governance amendment occurred; no protocol primitive was added; no new cognition class was introduced; no scope deviation occurred. Required gates ran green at both execution time and closure time, under the canonical interpreter.

This closure does NOT achieve OS-level sandbox isolation. It records that policy-layer subprocess execution has been added to the runtime; kernel-level isolation remains future enforcement. It does NOT close any of the unresolved canonicalization risks. It does NOT modify the workforce validator's enforcement of waiver failure classes F-1 through F-14. It does NOT advance the audit's bounded ten-document queue.

This closure DOES prove that a builder hardening cycle can carry a runtime from dry-run-only to bounded subprocess execution while preserving every prior refusal behavior, every prior admission rule, every prior manifest field, every prior refusal code, and every prior gate semantic. The deliverable is on disk; the implementation is exercised by 10/10 self-check fixtures; both v0.2 reports are the durable machine-checkable evidence. Future hardening cycles have a clear migration target for OS-level confinement.

---

## What Did This Work Order Actually Validate?

- Builder hardening lifecycle continuity from `drafted` through `closed`, with every intermediate state recorded with actor, timestamp, and note.
- Existence of a 17-section + six-explicit-state + difference-table + execute-allowlist + manifest-extension + timeout-policy + failure-mode-table + ten-required-tests + OS-isolation-roadmap + ten-final-law governance instrument at the declared top-level path.
- Strictly additive runtime extension: v0.1 dry-run code paths preserved verbatim; v0.2 execute mode layered as a new code path.
- Self-verification execution: the builder operator answered all ten self-verification questions explicitly with no scope or canon violation.
- Gate execution continuity for all five required gates at both execution time and closure time, under the canonical interpreter.
- Action-log generation: a predecessor action log (builder execution) and a successor action log (closure) were produced, each with the full required field set, and the successor explicitly references the predecessor by id.
- Real subprocess execution under bounded parameters: 10/10 v0.2 fixtures pass, including end-to-end execute, forbidden-block-before-subprocess, timeout, identity refusal, status refusal, replay mode, missing-allowed-files, missing-forbidden-files, source-repo-invariance, and full manifest shape.
- Source repository invariance under execute mode: every fixture verified `repo_fingerprint_before == repo_fingerprint_after`.

The validation surface above is the workforce runtime's builder hardening cycle and the runtime's policy-layer subprocess execution, not OS-level confinement and not autonomy.

---

## What Remains Unvalidated?

- OS-level sandbox isolation. The sandbox is `shutil.copytree`; a subprocess with sufficient operator privilege could escape the sandbox path. R-2 (retargeted to v0.3+) addresses this.
- Cryptographic attestation of v0.2 manifests. The manifest is plain JSON; an attacker with write access to `workforce/real_agents/runs/` could edit a manifest after the fact. R-3 / `AGENT-IDENTITY-v0.1.md` (audit P3) addresses this.
- Hash-chained manifest integrity across runs. R-4 carries forward.
- Resource limits beyond wall-clock time. v0.2 bounds time only; memory / CPU / FD / process-count are unbounded. R-5 carries forward.
- Manifest schema validator under the v0.2 schema. R-8 is retargeted but not authorized by this closure.
- Cross-validation between the workforce validator and the real-agent runtime. R-6 carries forward.
- Adversarial pressure suite for the execute-mode surface. R-7 carries forward.
- Inclusion in `make ci`. v0.2 remains opt-in per L-9.
- Per-identity allowed-write-glob and per-identity allowed-gate sets refining the current uniform allowlist. R-10 carries forward.
- Adversarial reviewer signoff under a second reviewer identity. The reviewer-identity fallback used in this cycle is the human owner under L-1; the audit's P1 entry `REVIEWER-IDENTITY-v0.1.md` addresses this gap and is not authorized by this closure.

Each item above is a known v0.2 enforcement gap. Closure of this work order does not narrow any of them. v0.3+ will narrow some.

---

**End of Closure Summary — WO-2026-05-07-009.**
