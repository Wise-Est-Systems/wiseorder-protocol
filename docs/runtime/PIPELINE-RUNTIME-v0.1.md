# PIPELINE RUNTIME v0.1
## End-to-End Governed Handoff: Proposer → Review Gate → Executor

**Status:** v0.1 — operational specification, normative for the pipeline surface in `tools/pipeline_runtime.py` and the `reports/pipeline_runtime/` tree. The pipeline runtime composes three previously independent runtimes — `PROPOSER-RUNTIME-v0.1.md`, `REVIEW-GATE-RUNTIME-v0.1.md`, and `REAL-AGENT-RUNTIME-v0.2.md` execute mode — into a single deterministic handoff. It does not introduce any new policy. It does not add execution authority beyond the executor's. It does not add networking, daemons, retries, or model calls. It adds exactly one capability: the conversion of an admitted work order into either a manifest-backed executed command or a refusal-coded aggregate manifest, depending on which gate fires first.

**Companion documents:** `PROPOSER-RUNTIME-v0.1.md` (stage 1), `REVIEW-GATE-RUNTIME-v0.1.md` (stage 2), `REAL-AGENT-RUNTIME-v0.2.md` (stage 3 execute mode), `REAL-AGENT-RUNTIME-v0.1.md` (admission base), `WORKFORCE-EXECUTION-RUNTIME-v0.1.md` (work-order lifecycle), `AGENT-GOVERNANCE-WORKFORCE-v0.1.md` (roles + authority), `WAIVER-MECHANISM-v0.1.md`, `FORBIDDEN-SURFACES-v0.1.md`, `VALIDATION-LAW-v0.1.md`, `REPLAY-LAW-v0.1.md`, `TRUST-LAW-v0.1.md`.

> **Core thesis.** Three previously-disconnected stages — propose, review, execute — now share a single deterministic orchestrator that records, at every transition, which surface refused (or did not), with what code, and over what hash anchor. The pipeline is the audit envelope around the existing stages, not a new authority above them.

> **Explicitly stated.**
>
> - **The pipeline does not create autonomy.**
> - **The pipeline creates deterministic governed handoff between proposal, review, and execution.**
> - **Execution remains bounded by real-agent runtime policy.**
> - **Reviewer approval is necessary but not sufficient; executor admission still governs execution.**

---

## 1. Purpose

The proposer (`PROPOSER-RUNTIME-v0.1.md`) converts an admitted work order into a deterministically-ordered, capped-at-three candidate set. The review gate (`REVIEW-GATE-RUNTIME-v0.1.md`) converts a proposal record into an `approved` or `rejected` decision artifact. The executor (`REAL-AGENT-RUNTIME-v0.2.md`) converts an admitted command list into a sandbox-bounded subprocess invocation under a minimal environment. Each stage is independently testable and independently refusable. None of them, alone, runs end-to-end.

This document defines v0.1 of the pipeline runtime: the smallest possible orchestrator that converts a work-order path plus four identity arguments (proposer, reviewer, executor — and an optional expected work-order id) into one aggregate manifest. The pipeline does not edit any policy, does not relax any refusal code, does not add a new identity, and does not add a new authority. It produces an audit envelope: a single JSON record that names every intermediate artifact, every hash, every command, and the exact stage at which the run was admitted, refused, or executed.

## 2. Architecture

The runtime architecture is now five surfaces, in order:

```
work order
   │
   ▼
proposer           (PROPOSER-RUNTIME-v0.1.md)
   │ writes proposal JSON under reports/proposer_runtime/
   ▼
review gate        (REVIEW-GATE-RUNTIME-v0.1.md)
   │ writes review artifact JSON under reports/review_gate_runtime/
   │
   ├─ decision=rejected ─► pipeline records refusal; STOPS; executor never invoked
   │
   ▼ decision=approved
executor           (REAL-AGENT-RUNTIME-v0.2.md execute mode)
   │ admits work order under executor identity, runs approved commands
   │ inside a sandbox copy, writes manifest under workforce/real_agents/runs/
   ▼
aggregate manifest (this doc)
   │ writes pipeline-<id>.json + .md under reports/pipeline_runtime/
```

The pipeline is a function from `(work_order_path, proposer_agent_id, reviewer_id, executor_agent_id, optional expected_work_order_id)` to one aggregate manifest record. The intermediate artifacts (proposal, review, executor manifest) are produced by their respective runtimes and are referenced from the aggregate by path. The pipeline never bypasses any stage's refusal: a proposer refusal flows through to a reviewer rejection (`no_commands_to_approve`); a reviewer rejection halts the pipeline before the executor is invoked; an executor refusal is recorded with the executor's own refusal code.

## 3. What Becomes Real In v0.1

The single property v0.1 adds: a work order can now be deterministically driven through all three stages, with one record covering the full chain.

- The proposer is invoked with `(work_order_path, proposer_agent_id)`. The proposer's exit status, output path, deterministic hash, proposed commands, rejected commands, and policy rejection codes are captured into the aggregate.
- The review gate is invoked with `(proposer_artifact_path, expected_work_order_id, reviewer_id)`. The review's decision, approval scope, rejected commands, rejection-reason codes, hash-verification result, and review hash are captured.
- If `review.decision != "approved"`: the executor is **not** invoked, the aggregate `final_status` is set to `refused_at_review`, the `executor_manifest` field is `null`, and the pipeline exits non-zero. This branch is asserted by self-check fixture 8 (`no_execution_occurs_without_approved_review_artifact`).
- If `review.decision == "approved"`: the executor is invoked with `(work_order_path, executor_agent_id, commands=approval_scope_commands)`. The executor's run id, manifest path, exit status, repo fingerprint before/after, sandbox fingerprint before/after, commands attempted/allowed/blocked/results, gates passed/failed, and policy violations are captured.
- The aggregate manifest is hashed (sha256 over its audit-stable subset) and the hash is recorded as `pipeline_hash`. Two runs of the same work order under the same identities produce byte-identical `pipeline_hash` (modulo recorded-but-not-hashed `pipeline_id`, `timestamps`, `executor_manifest_hash`, and intermediate artifact paths).
- The aggregate is written to `reports/pipeline_runtime/pipeline-<pipeline_id>.json` and to a Markdown summary at `pipeline-<pipeline_id>.md`.

## 4. What Remains Not Real

- **No new execution surface.** The pipeline imports the proposer, the reviewer, and the executor. It does not import `subprocess` itself; the only subprocess invocation in the chain is the executor's, governed by `REAL-AGENT-RUNTIME-v0.2.md`.
- **No new authority.** The reviewer cannot now execute. The proposer cannot now bypass the reviewer. The executor's admission, command-policy, and filesystem-policy checks are not weakened.
- **No work selection.** The work-order path and identity arguments are CLI inputs.
- **No retries.** A refusal is terminal at the stage at which it fires.
- **No background loop.** `main()` returns after one work order.
- **No daemon, no cron, no scheduled re-entry, no `make ci` inclusion.** v0.1's targets are opt-in.
- **No network access, no model call, no HTTP client, no socket.**
- **No persistence beyond the aggregate manifest and intermediate artifacts.** Two pipeline runs do not share state.

## 5. Constraints

| Constraint | Enforcement |
| --- | --- |
| Single work order per invocation | CLI takes exactly one `--work-order` |
| No subprocess in the pipeline module itself | Pipeline does not `import subprocess`, `os.exec*`, `os.spawn*`, `os.popen` — those happen only inside `REAL-AGENT-RUNTIME-v0.2.md` execute mode |
| No networking | No HTTP, no socket import; constraint holds vacuously |
| No model call | No LLM, no embedding |
| Determinism | Pipeline hash is stable across re-runs on identical inputs; intermediate hashes (proposer, reviewer) inherit their stage-level determinism |
| Fail closed | Any refusal at proposer, reviewer, or executor produces a non-zero exit and a refusal-coded aggregate manifest |
| Reviewer approval is gate, not authorization | Approved review is a *necessary* condition for executor invocation, not a sufficient one — the executor still runs its own admission |
| Source repo invariance | The aggregate records `repo_fingerprint_before` and `repo_fingerprint_after`; the executor itself enforces equality and surfaces any drift as a `repo_fingerprint_drift` policy violation |

## 6. Aggregate Manifest Schema

Every pipeline run writes `reports/pipeline_runtime/pipeline-<pipeline_id>.{json,md}`.

| Field | Type | Meaning |
| --- | --- | --- |
| `pipeline_id` | string | identifier of the form `pipeline-<run_token>`; not included in `pipeline_hash` |
| `work_order_id` | string | the admitted work order's id (empty on early refusal) |
| `proposer_artifact` | string \| null | path to the proposer JSON artifact |
| `review_artifact` | string \| null | path to the review JSON artifact (null if proposer never wrote one) |
| `executor_manifest` | string \| null | path to the executor manifest (null if executor was not invoked) |
| `proposer_hash` | string | the proposer's `deterministic_hash` |
| `review_hash` | string | the reviewer's `review_hash` |
| `executor_manifest_hash` | string \| null | sha256 of the executor manifest's audit-stable subset (null if no manifest) |
| `final_status` | string | one of: `executed`, `executed_with_violations`, `refused_at_review`, `refused_at_executor` |
| `refusal_reason` | string | the first refusal code (empty on full success) |
| `commands_proposed` | list of strings | sorted list of commands the proposer emitted as `commands_proposed` |
| `commands_approved` | list of strings | sorted list of commands the reviewer placed in `approval_scope` |
| `commands_executed` | list of strings | sorted list of commands the executor invoked as a subprocess (empty if executor not invoked or all blocked) |
| `timestamps` | object | `{start, proposer_done, review_done, executor_done, end}` ISO-8601 UTC |
| `repo_fingerprint_before` | string | source-repo `repo_fingerprint` snapshot at pipeline start |
| `repo_fingerprint_after` | string | source-repo `repo_fingerprint` snapshot at pipeline end (must equal `repo_fingerprint_before`) |
| `policy_violations` | list of objects | aggregated policy violations from the executor manifest, plus any pipeline-level violations |
| `pipeline_hash` | `sha256:<hex>` | sha256 over the aggregate's audit-stable subset (excludes `pipeline_id`, `timestamps`, `proposer_artifact`, `review_artifact`, `executor_manifest`, `executor_manifest_hash`, `pipeline_hash` itself) |
| `runtime_version` | string | `"v0.1"` |
| `exit_status` | int | 0 on `executed`, 1 otherwise |

## 7. Refusal Branch Diagram

```
proposer ──── exit_status != 0 (no commands eligible)
   │             │
   │             ▼
   │          review gate sees commands_proposed=[]
   │             │
   │             ▼
   │          decision=rejected, no_commands_to_approve
   │             │
   │             ▼
   │          PIPELINE: final_status=refused_at_review
   │
   └── exit_status == 0
         │
         ▼
       review gate ──── decision=rejected (any reason) ──► PIPELINE: final_status=refused_at_review
         │
         └── decision=approved
              │
              ▼
            executor ──── admit refused (e.g., assigned_to_mismatch) ──► PIPELINE: final_status=refused_at_executor
              │
              ├── admit OK, command blocked / gate failed / repo drift ──► PIPELINE: final_status=executed_with_violations
              │
              └── admit OK, all commands ran with exit_code=0 ──► PIPELINE: final_status=executed
```

## 8. Self-Check Fixtures

The pipeline self-check fixture suite (`run_self_check`, exposed via `make pipeline-check`) covers the eight cases below. All eight MUST pass at v0.1 closure time and at every subsequent gate run.

1. **`valid_pipeline_executes_allowed_command`** — work order assigned to `builder-01` with `required_gates=["pwd"]`; proposer admits; reviewer approves; executor runs `pwd` in sandbox; aggregate `final_status=executed`, `commands_executed=["pwd"]`, `exit_status=0`, `repo_fingerprint_before == repo_fingerprint_after`.
2. **`reviewer_rejection_prevents_executor_call`** — same valid work order, but the pipeline is invoked with `expected_work_order_id` set to a value that does not match. Reviewer rejects with `wrong_work_order_id`. Aggregate `final_status=refused_at_review`, `executor_manifest is None`, `commands_executed=[]`.
3. **`mutated_proposal_hash_rejected`** — pipeline runs the proposer, then mutates the proposer JSON file's `deterministic_hash` field, then re-invokes the reviewer against the mutated file. Reviewer rejects with `deterministic_hash_mismatch`. Executor never invoked. Aggregate `final_status=refused_at_review`.
4. **`forbidden_command_proposal_rejected`** — work order with `required_gates=["curl https://example.com"]`; proposer refuses (commands_proposed empty, exit_status=1); reviewer rejects with `no_commands_to_approve` (and inherits the empty-input refusal). Executor never invoked. Aggregate `final_status=refused_at_review`.
5. **`wrong_executor_identity_refused`** — same valid work order assigned to `builder-01`; proposer and reviewer pass under matching identities; executor is invoked with `executor_agent_id="release-01"`. Executor admit refuses with `assigned_to_mismatch`. Aggregate `final_status=refused_at_executor`.
6. **`source_repo_unchanged_after_pipeline`** — running fixture 1 leaves the source-repo `repo_fingerprint` byte-identical pre/post; the executor's own `repo_fingerprint_drift` policy violation does not fire.
7. **`aggregate_manifest_hash_stable`** — running fixture 1 twice produces two aggregates whose `pipeline_hash` values are byte-identical (despite differing `pipeline_id`, `timestamps`, intermediate artifact paths, and `executor_manifest_hash`).
8. **`no_execution_occurs_without_approved_review_artifact`** — for every refusal fixture (2–5), `executor_manifest is None` AND `commands_executed == []`. The executor was demonstrably not invoked when the reviewer did not approve.

The harness writes per-run aggregate manifests to `reports/pipeline_runtime/` and a v0.1 self-check report at `reports/pipeline_runtime/pipeline_runtime_v0.1.{md,json}`.

## 9. Pipeline Boundary Law

This section is the runtime's terminal commitment. Every implementation choice in `tools/pipeline_runtime.py` MUST be consistent with the law statement below.

> **The pipeline does not create autonomy. The pipeline creates deterministic governed handoff between proposal, review, and execution. Execution remains bounded by real-agent runtime policy. Reviewer approval is necessary but not sufficient; executor admission still governs execution.**

The pipeline is a *composition* of three previously-tested runtimes. It is not a new authority. It cannot grant any identity that the executor would refuse. It cannot widen any allowlist. It cannot bypass any deny set. It cannot reach the network. It cannot run in the background. Its strongest verb is the act of *invoking* the existing runtimes in order — not of executing anything itself.

A pipeline whose proposer-stage output is handed directly to the executor without the review gate is *operator misuse*, not a runtime feature. The runtime cannot prevent operator misuse; it can only refuse to participate in it. The pipeline's contribution to that refusal is its complete absence of any code path that skips the review-gate check.

## 10. What Makes This Still Non-Autonomous

Ten properties bound the v0.1 pipeline. Removing any one would change its class of artifact.

1. **No selection.** Work-order path and identities are CLI arguments. The pipeline does not enumerate work orders, does not "pick the next pending one."
2. **No execution surface in the pipeline module.** The pipeline does not import `subprocess`, `os.exec*`, `os.spawn*`, `os.popen`, `socket`, `urllib`. The only subprocess invocation in the chain is the executor's.
3. **No persistence beyond a single aggregate manifest plus the three intermediate artifacts.** The pipeline keeps no cache between runs.
4. **No loop.** `main()` returns after one work order.
5. **No retry.** A refusal is terminal.
6. **No widening.** The pipeline cannot add a command not present in `commands_proposed`.
7. **No model.** No LLM, no embedding, no classifier — every verdict comes from the underlying runtimes' string-and-hash comparisons.
8. **No network.** No HTTP, no socket, no DNS lookup.
9. **No self-modification.** The pipeline cannot modify itself, the proposer, the reviewer, or the executor.
10. **No path to the executor without an approved review artifact.** The architectural separation in §2 and §9 means there is no code path in `tools/pipeline_runtime.py` from the proposer to the executor that does not first pass through the reviewer's `decision=approved` check.

## 11. CLI

The pipeline exposes two CLI verbs:

- `tools/pipeline_runtime.py run --work-order PATH --proposer-agent-id ID --reviewer-id ID --executor-agent-id ID [--expected-work-order-id ID] [--timeout SECONDS]` — orchestrate the three stages, write the aggregate manifest under `reports/pipeline_runtime/`, exit 0 on `final_status=executed`, 1 otherwise.
- `tools/pipeline_runtime.py self-check` — run the eight self-check fixtures (§8), refresh the runtime report at `reports/pipeline_runtime/pipeline_runtime_v0.1.{md,json}`, exit 0 if all eight match expected outcome, 1 otherwise.

The Makefile exposes two targets, neither in `make ci`:

- `make pipeline-check` — invoke `self-check`.
- `make pipeline-run-fixture` — invoke `run` with the canonical fixture work order under `reports/pipeline_runtime/_fixtures/`.

## 12. Future Work

Future hardening work is enumerated for the record; none of it is authorized by this document.

- **Multi-work-order batching.** A future pipeline could accept a directory of work orders and emit one aggregate per file, provided per-aggregate determinism is preserved.
- **Reviewer chaining.** A future protocol could require multiple `approved` review artifacts under distinct reviewer identities before the pipeline invokes the executor (mirroring `Class C` consensus).
- **Pipeline-level policy DSL.** A future orchestrator could read a small declarative policy file (e.g., "this pipeline run requires both reviewer-A and reviewer-B approval"), provided every approval still requires its own out-of-band gate.
- **Inclusion in `make ci`.** v0.1 explicitly does NOT add `pipeline-check` to `make ci`. A future hardening cycle may evaluate inclusion.

None of these expand execution authority. Every one of them preserves the boundary in §9.

## 13. Final Law

The pipeline is bounded by the following ten law statements. They are this document's terminal commitments.

**L-1. v0.1 creates deterministic governed handoff between proposer, reviewer, and executor.** A previously absent end-to-end orchestration now exists.

**L-2. v0.1 does NOT create autonomy.** The pipeline cannot select work, cannot widen scope, cannot persist beyond a single aggregate, cannot loop, cannot retry, cannot reach a network, cannot call a model, cannot modify itself, and cannot bypass any stage's refusal.

**L-3. v0.1 does NOT execute commands itself.** The pipeline module does not import `subprocess` or any exec / spawn / popen surface. The only subprocess invocation in the chain is the executor's, governed by `REAL-AGENT-RUNTIME-v0.2.md`.

**L-4. v0.1 enforces the architecture proposer → review gate → executor.** There is no code path from the proposer to the executor that does not first pass through `review.decision == "approved"`.

**L-5. v0.1 preserves every v0.1 / v0.2 runtime refusal.** The pipeline reuses every admission rule, every command-policy verdict, every filesystem-policy verdict, every refusal code from the underlying runtimes.

**L-6. v0.1 records every transition.** Proposer hash, reviewer hash, executor manifest hash, commands at each stage, repo fingerprints, timestamps, and the exact refusal stage are all captured in the aggregate manifest.

**L-7. v0.1 produces a deterministic pipeline hash.** Two runs of the same work order under the same identities produce byte-identical `pipeline_hash`.

**L-8. v0.1 fails closed.** Any proposer refusal, reviewer rejection, or executor refusal produces `final_status` set to the corresponding stage and `exit_status = 1`.

**L-9. v0.1 is not added to `make ci`.** `make pipeline-check` and `make pipeline-run-fixture` are opt-in.

**L-10. The pipeline does not create autonomy. The pipeline creates deterministic governed handoff between proposal, review, and execution. Execution remains bounded by real-agent runtime policy. Reviewer approval is necessary but not sufficient; executor admission still governs execution.**

---

**End of PIPELINE RUNTIME v0.1.**
