# REVIEW GATE RUNTIME v0.1
## Deterministic Reviewer Admission of Proposer Output, With Zero Execution Authority

**Status:** v0.1 — operational specification, normative for the reviewer-gate surface in `tools/review_gate_runtime.py` and the `reports/review_gate_runtime/` tree. The reviewer gate consumes proposer JSON output, re-derives the proposer's deterministic hash, re-classifies every proposed command against the v0.1 deny set and v0.2 execute allowlist, and emits an `approved` or `rejected` review artifact. The gate never executes a command, never reaches the network, never spawns a subprocess, never persists state outside a single per-run JSON record, and never runs in the background.

**Companion documents:** `PROPOSER-RUNTIME-v0.1.md` (input source), `REAL-AGENT-RUNTIME-v0.1.md` (admission base), `REAL-AGENT-RUNTIME-v0.2.md` (executor allowlist + execute mode), `WORKFORCE-EXECUTION-RUNTIME-v0.1.md` (work-order lifecycle), `AGENT-GOVERNANCE-WORKFORCE-v0.1.md` (roles + authority), `WAIVER-MECHANISM-v0.1.md`, `FORBIDDEN-SURFACES-v0.1.md`, `VALIDATION-LAW-v0.1.md`, `REPLAY-LAW-v0.1.md`, `TRUST-LAW-v0.1.md`.

> **Core thesis.** The reviewer gate is the missing third role from `AGENT-GOVERNANCE-WORKFORCE-v0.1.md`. It is *not* the executor. It is a deterministic admission filter between proposer output and executor input. It accepts a proposal record on disk, validates the integrity of every claim the proposer made (`work_order_id`, `agent_id`, `proposal_id`, `deterministic_hash`, command-by-command allowlist coverage, command-by-command forbidden-pattern absence, rationale presence, command-count cap), and writes a `decision` artifact that downstream operators must consult before any executor identity is invoked. The architecture is `proposer → review gate → executor`, never `proposer → executor`.

> **Explicitly stated.**
>
> - **v0.1 creates deterministic admission of proposer output.** A proposal record is parsed, re-hashed, re-classified, and converted into an approve-or-reject artifact whose own content hash is stable across re-runs.
> - **v0.1 does NOT create execution authority.** The reviewer gate has approval authority *only* over proposal admissibility. It has zero execution authority. Executor admission remains controlled by the real-agent runtime.
> - **v0.1 does NOT execute commands.** No `subprocess`, no `os.exec*`, no `os.spawn*`, no shell, no model call, no RPC.
> - **v0.1 does NOT weaken any v0.1 / v0.2 runtime policy.** The reviewer reuses the same `EXECUTE_ALLOWED_COMMANDS` allowlist and the same `FORBIDDEN_COMMAND_PATTERNS` deny set as the executor, and reuses the same `IDENTITIES` table for the proposer-identity check.
> - **v0.1 does NOT bypass the executor.** An approved review artifact is *necessary*, not *sufficient*, for a v0.2 execute-mode run. The executor's own admission, command-policy, and filesystem-policy checks remain in force.

---

## 1. Purpose

The proposer runtime (`PROPOSER-RUNTIME-v0.1.md`) closed the gap between "work order admitted" and "concrete candidate set on disk." The execute-mode runtime (`REAL-AGENT-RUNTIME-v0.2.md`) closed the gap between "approved command" and "subprocess invocation under deny-first policy." Between those two layers lies a single missing surface: a *third role* that decides whether a particular proposal is admissible for the executor at all. Without that role, the only thing standing between a proposal and an executor invocation is operator discipline. Operator discipline is not a runtime feature.

This document defines v0.1 of the reviewer-gate runtime. It is the smallest possible addition that produces a *deterministic, machine-checkable admission verdict* on proposer output. It does not add execution surface. It does not add network access. It does not add background processing. It does not relax any existing policy. It does add one and only one capability: the conversion of a proposer JSON file into an `approved` or `rejected` review artifact.

## 2. Architecture

The runtime architecture is now four roles, in order:

```
work order ──► proposer ──► review gate ──► executor (v0.2 runtime)
              (v0.1)        (this doc)      (v0.2)
```

The proposer reads the work order and writes a proposal JSON to `reports/proposer_runtime/`. The review gate reads that proposal, re-validates its integrity, and writes a review artifact JSON to `reports/review_gate_runtime/`. The executor (the v0.2 real-agent runtime under `builder-01` / `release-01` / `canon_guardian-01` / `reviewer-01`) is invoked only after a downstream operator has consulted both the proposal and the matching `approved` review artifact. The review artifact is a *necessary* admission gate, not a *sufficient* one — the executor's own admission rules in `REAL-AGENT-RUNTIME-v0.1.md` §6 and command-policy / filesystem-policy checks in `REAL-AGENT-RUNTIME-v0.2.md` remain in force.

The architecture is explicitly NOT `proposer → executor`. There is no callable surface from the review gate into the executor. There is no shared queue. There is no IPC. The only surface between gate and executor is a JSON file on disk that an operator must read, match against the proposal it certifies, and operationally hand to the executor as a command argument.

## 3. What Becomes Real In v0.1

The single property v0.1 adds: a proposal record now has a deterministic, machine-checkable admission verdict associated with it. Concretely:

- A proposer JSON output at a CLI-supplied path is read, parsed, and validated for required fields (`proposal_id`, `work_order_id`, `agent_id`, `rationale`, `commands_proposed`, `deterministic_hash`).
- The proposer's claimed `deterministic_hash` is re-derived from the proposal's audit-stable subset (`agent_id`, `allowed_command_matches`, `commands_proposed`, `commands_rejected`, `policy_rejections`, `rationale`, `runtime_version`, `work_order_id`) and compared byte-for-byte against the claimed value. Mismatch is a terminal rejection.
- The proposer's `agent_id` is checked against the v0.1 / v0.2 `IDENTITIES` table. An unknown identity is a terminal rejection.
- Each entry in `commands_proposed` is re-classified through the deny-first-then-allowlist matcher used by the v0.2 executor, against the same `FORBIDDEN_COMMAND_PATTERNS` and `EXECUTE_ALLOWED_COMMANDS` constants. Any forbidden pattern match or any allowlist miss is a terminal rejection on that command.
- The total number of `commands_proposed` is checked against the v0.1 proposer cap of three. Anything greater is a terminal rejection.
- The `rationale` field is checked for non-empty content. An empty or whitespace-only rationale is a terminal rejection.
- An optional `--expected-work-order-id` argument, when supplied, is compared byte-for-byte against the proposal's `work_order_id`. Mismatch is a terminal rejection.
- The decision (`approved` or `rejected`), the per-command approval-scope list, the per-command rejection list, and the rejection-reason codes are written to a review artifact under `reports/review_gate_runtime/review-<run_id>.json` plus a Markdown summary at `review-<run_id>.md`. The artifact's own audit-stable content is hashed (sha256 over a deterministic JSON serialization with `review_id`, `timestamp`, and `review_hash` removed), and the hash is recorded as `review_hash`.

This is what becomes real in v0.1: a single deterministic admission step, captured to an audit artifact. Nothing else.

## 4. What Remains Not Real

- **Execution authority.** The reviewer gate does not invoke commands. It writes a JSON file. A subprocess is never spawned.
- **Authorization beyond admissibility.** An `approved` review artifact is the gate's claim that a proposal is *admissible* for the executor. It is not a claim that the executor will admit it (the executor re-runs its own checks under `REAL-AGENT-RUNTIME-v0.1.md` §6 / `REAL-AGENT-RUNTIME-v0.2.md` execute-mode policy), and it is not a claim that the underlying work is correct, complete, or strategically appropriate.
- **Selection.** The reviewer gate never selects a proposal to review. The proposal path is a CLI argument. The gate does not enumerate `reports/proposer_runtime/`, does not pick "next pending review," and does not schedule itself.
- **Background processing.** No daemon, no scheduler, no event loop, no `asyncio`. Each invocation is a single-shot CLI command that reads one proposal, writes one review artifact, and exits.
- **Network access.** No `urllib.request`, no `socket.connect`, no HTTP, no SSH. The reviewer's import surface is strictly stricter than the executor's.
- **Recursive self-modification.** The gate does not edit `tools/review_gate_runtime.py`, `reports/review_gate_runtime/`, or `REVIEW-GATE-RUNTIME-v0.1.md`.
- **Cross-run memory.** Two reviews do not chain. The gate carries no state between runs.
- **Cron, daemon, service, hook.** The gate is not registered with `launchd`, `systemd`, `cron`, `at`, or any git hook.
- **Inclusion in `make ci`.** v0.1's targets are opt-in.

## 5. Constraints

The reviewer gate enforces the following hard constraints. Each has a corresponding rejection-reason code (§7) and a corresponding self-check fixture (§8).

| Constraint | Enforcement |
| --- | --- |
| Read one proposal per invocation | CLI takes exactly one `--proposal` path; no globbing, no batch mode |
| No subprocess | No `subprocess`, `os.exec*`, `os.spawn*`, or `os.popen` import; the module imports stdlib `argparse`, `dataclasses`, `datetime`, `hashlib`, `json`, `pathlib`, `sys`, and the v0.2 runtime's `EXECUTE_ALLOWED_COMMANDS` / `FORBIDDEN_COMMAND_PATTERNS` / `IDENTITIES` only |
| No networking | No HTTP client, no socket, no DNS lookup; constraint holds vacuously by absence of network imports |
| No model call | No LLM, no embedding, no classifier; the verdict is pure string-and-hash comparison |
| No persistence beyond review record | Single write to `reports/review_gate_runtime/review-<run_id>.{json,md}`; no caches, no databases |
| No background loop | `main()` returns after one proposal; no `while True`, no signal-handler-driven re-entry |
| No daemon | No `os.fork`, no `os.setsid` |
| No cron | No CronCreate, no scheduled remote agent, no Makefile target that registers a periodic run |
| Deterministic verdict | Same proposal under same reviewer identity produces byte-identical `review_hash` (modulo recorded-but-not-hashed `timestamp` and `review_id`) |
| Fail closed | Any unparseable input, missing field, hash mismatch, unknown proposer, empty rationale, forbidden command, allowlist miss, command-count over cap, or expected-work-order-id mismatch yields `decision = rejected` and a non-zero exit status |

Every constraint is a rejection class; none is a soft warning.

## 6. Review Artifact Schema

Every review artifact is a JSON file written to `reports/review_gate_runtime/review-<run_id>.json`, accompanied by a human-readable Markdown summary at `review-<run_id>.md`. The JSON schema is:

| Field | Type | Meaning |
| --- | --- | --- |
| `review_id` | string | identifier of the form `review-<reviewer_id>-<proposal_id_short>-<timestamp>`; not included in the hash input |
| `proposal_id` | string | the reviewed proposal's `proposal_id` field; empty if the proposal could not be parsed |
| `work_order_id` | string | the reviewed proposal's `work_order_id`; empty if the proposal could not be parsed |
| `reviewer_id` | string | the reviewing identity; v0.1 ships exactly one identity, `review-gate-01` |
| `decision` | string | `"approved"` or `"rejected"` |
| `approval_scope` | list of objects | per-command approval entries (see below); empty if `decision = rejected` |
| `rejected_commands` | list of objects | per-command rejection entries (see below); empty on full approval |
| `rejection_reasons` | list of strings | rejection-reason codes raised during validation; empty on full approval |
| `deterministic_hash_verified` | boolean | `true` iff the recomputed proposer hash matched the proposal's claimed hash |
| `timestamp` | ISO-8601 UTC string | when the review was generated; not included in the hash input |
| `review_hash` | `sha256:<hex>` | sha256 of the JSON serialization of the review artifact with `review_id`, `timestamp`, and `review_hash` removed |
| `runtime_version` | string | `"v0.1"` |
| `exit_status` | int | 0 on `approved`, 1 on `rejected`; not included in the hash input |

**`approval_scope` entry shape:**

| Key | Type | Meaning |
| --- | --- | --- |
| `command` | string | the proposed command text |
| `allowed_command_match` | string | the v0.2 `EXECUTE_ALLOWED_COMMANDS` entry the command matched |

**`rejected_commands` entry shape:**

| Key | Type | Meaning |
| --- | --- | --- |
| `command` | string | the rejected command text |
| `code` | string | the rejection reason code (one of §7) |
| `reason` | string | a single-sentence explanation |

The artifact is sorted by key, indented two spaces, UTF-8, with a trailing newline.

## 7. Rejection Reason Codes

The reviewer fails closed. Every rejection produces `exit_status = 1`, `decision = "rejected"`, and one or more entries in `rejection_reasons`.

| Code | Trigger |
| --- | --- |
| `proposal_file_missing` | the path passed to `--proposal` does not exist |
| `proposal_json_invalid` | the file at `--proposal` cannot be JSON-parsed |
| `missing_proposal_id` | proposal record has empty or missing `proposal_id` |
| `missing_work_order_id` | proposal record has empty or missing `work_order_id` |
| `wrong_work_order_id` | `--expected-work-order-id` was supplied and does not equal the proposal's `work_order_id` |
| `missing_agent_id` | proposal record has empty or missing `agent_id` |
| `unknown_proposer` | proposal's `agent_id` is not in the v0.1 / v0.2 `IDENTITIES` table |
| `empty_rationale` | proposal's `rationale` is empty or whitespace-only |
| `no_commands_to_approve` | proposal's `commands_proposed` is empty (proposer refusal flowing through) |
| `too_many_commands` | proposal's `commands_proposed` has more than three entries |
| `forbidden_command` | a `commands_proposed` entry's `command` text matches a `FORBIDDEN_COMMAND_PATTERNS` entry |
| `not_in_execute_allowlist` | a `commands_proposed` entry's `command` text does not match any `EXECUTE_ALLOWED_COMMANDS` entry under exact-or-startswith-plus-space matching |
| `deterministic_hash_mismatch` | the recomputed proposer hash differs from the proposal's claimed `deterministic_hash` |
| `unreadable_proposer_runtime_version` | proposal's `runtime_version` is missing or not the literal `"v0.1"` (defensive; protects against future schema drift) |

A single review may emit several of these codes simultaneously; each is recorded once in `rejection_reasons` in the order detected.

## 8. Required Self-Check Fixtures

The reviewer gate's self-check fixture suite (`run_self_check`, exposed via `make review-gate-check`) covers the eight cases below. All eight MUST pass at v0.1 closure time and at every subsequent gate run.

1. **`valid_proposal_approved`** — fixture proposal with three allowlisted commands, non-empty rationale, valid hash, known proposer, valid work-order id; reviewer emits `decision = approved`, populated `approval_scope`, empty `rejected_commands`, empty `rejection_reasons`, `deterministic_hash_verified = true`, `exit_status = 0`.
2. **`bad_hash_rejected`** — fixture identical to (1) but with a hand-mutated `deterministic_hash`; reviewer emits `decision = rejected`, `deterministic_hash_verified = false`, `rejection_reasons` containing `deterministic_hash_mismatch`.
3. **`forbidden_command_rejected`** — fixture whose `commands_proposed[0].command` is `curl https://example.com` with hash recomputed for consistency; reviewer emits `decision = rejected`, `rejection_reasons` containing `forbidden_command`.
4. **`too_many_commands_rejected`** — fixture with four `commands_proposed` entries and hash recomputed for consistency; reviewer emits `decision = rejected`, `rejection_reasons` containing `too_many_commands`.
5. **`empty_rationale_rejected`** — fixture with `rationale = ""` and hash recomputed for consistency; reviewer emits `decision = rejected`, `rejection_reasons` containing `empty_rationale`.
6. **`wrong_work_order_id_rejected`** — fixture identical to (1) but reviewer is invoked with `--expected-work-order-id` set to a value that does not equal the proposal's `work_order_id`; reviewer emits `decision = rejected`, `rejection_reasons` containing `wrong_work_order_id`.
7. **`unknown_proposer_rejected`** — fixture with `agent_id = "unknown-99"` and hash recomputed for consistency; reviewer emits `decision = rejected`, `rejection_reasons` containing `unknown_proposer`.
8. **`review_artifact_hash_stable`** — running the reviewer twice on fixture (1) produces two artifacts whose `review_hash` values are byte-identical (despite differing `review_id` and `timestamp`).

The harness writes per-run review artifacts to `reports/review_gate_runtime/` and a v0.1 self-check report at `reports/review_gate_runtime/review_gate_runtime_v0.1.{md,json}`.

## 9. Reviewer Authority Law

This section is the runtime's terminal commitment. Every implementation choice in `tools/review_gate_runtime.py` MUST be consistent with the law statement below.

> **The reviewer gate has approval authority only over proposal admissibility. It has zero execution authority. Executor admission remains controlled by the real-agent runtime.**

The gate's `approved` verdict is a claim that the proposal it certifies satisfies every v0.1 admission constraint defined in this document. It is not a claim that the executor will accept the same proposal — the executor re-runs its own admission checks (`REAL-AGENT-RUNTIME-v0.1.md` §6), command-policy verdicts (`REAL-AGENT-RUNTIME-v0.2.md`), and filesystem-policy verdicts. It is not a claim that the underlying work is correct. It is not a claim that the executor *should* run the commands; it is a claim that the executor *may* be invited to consider them.

A reviewer-gate verdict whose proposal is handed directly to the executor without the executor re-running its own admission is *operator misuse*, not a runtime feature. The runtime cannot prevent operator misuse; it can only refuse to participate in it. The reviewer's contribution to that refusal is its complete absence of execution surface.

## 10. What Makes This Still Non-Autonomous

The v0.1 reviewer gate is bounded by ten properties that, taken together, make it not an autonomous agent. Removing any one of them would change the class of artifact the gate is.

1. **No will of its own.** The gate never selects which proposal to review. The proposal path is a CLI argument.
2. **No execution surface.** The module imports no `subprocess`, `os.exec*`, `os.spawn*`, or `os.popen`. The strongest verb the gate can perform is `Path.write_text`.
3. **No persistence beyond a single review record.** No cache, no database, no scratch directory.
4. **No loop.** `main()` returns after one proposal.
5. **No retry.** A rejection is terminal. The gate does not re-derive, back off, or try an alternate strategy.
6. **No widening.** The gate cannot approve a command not present in `commands_proposed`.
7. **No model.** No LLM, no embedding. The verdict is computed by string comparison and sha256.
8. **No network.** No HTTP, no socket, no DNS lookup.
9. **No self-modification.** The gate cannot approve commands that edit itself, its outputs, or its specification (its allowlist matcher is the v0.2 executor's; the proposer's recursive-self-modification check already removed self-pointing commands at proposal time).
10. **No path to the executor without an out-of-band operator step.** The architectural separation in §2 and §9 means the gate's output is a JSON file on disk, not a function call into the executor.

## 11. CLI

The reviewer gate exposes two CLI verbs:

- `tools/review_gate_runtime.py review --proposal PATH [--expected-work-order-id ID] [--reviewer-id ID]` — read the proposal at PATH, validate, write the review artifact under `reports/review_gate_runtime/`, exit 0 on `approved`, 1 on `rejected`. Default `reviewer-id` is `review-gate-01`.
- `tools/review_gate_runtime.py self-check` — run the eight self-check fixtures (§8), refresh the runtime report at `reports/review_gate_runtime/review_gate_runtime_v0.1.{md,json}`, exit 0 if all eight match expected outcome, 1 otherwise.

The Makefile exposes one target, not in `make ci`:

- `make review-gate-check` — invoke `self-check`.

## 12. Future Work

The v0.1 reviewer gate is the smallest possible admission filter. Future hardening work is enumerated for the record; none of it is authorized by this document, and each item requires its own drafted-approved-assigned governance work order.

- **Multi-proposal review batching.** A future gate could accept a directory of proposals and emit one review artifact per file, provided determinism per artifact is preserved and no batch-level decision (e.g., "approve all if any approve") is added.
- **Reviewer policy DSL.** A future gate could read a small declarative policy file and apply additional reviewer-specific constraints beyond the v0.1 set (e.g., "this reviewer rejects any proposal whose rationale exceeds 120 characters").
- **Reviewer chaining.** A future protocol could require multiple `approved` review artifacts (under distinct reviewer identities) before the executor admits a proposal, mirroring `Class C` consensus semantics.
- **Reviewer-identity admission table.** A future workforce extension could expand `IDENTITIES` to declare which proposer identities each reviewer identity is authorized to admit.

None of these expand execution authority. Every one of them preserves the boundary in §9.

## 13. Final Law

The reviewer gate is bounded by the following ten law statements. They are this document's terminal commitments.

**L-1. v0.1 creates deterministic admission of proposer output.** A previously absent layer between proposer and executor now exists.

**L-2. v0.1 does NOT create autonomy.** The gate cannot select work, cannot select proposals, cannot widen scope, cannot persist beyond a single review record, cannot loop, cannot retry, cannot reach a network, cannot call a model, cannot modify itself, and cannot invoke the executor.

**L-3. v0.1 does NOT execute.** No subprocess. No shell. The reviewer's strongest verb is a single JSON file write.

**L-4. v0.1 enforces the architecture proposer → review gate → executor.** There is no path from the proposer to the executor that does not pass through this gate, and there is no path from this gate into the executor that does not pass through an out-of-band operator step.

**L-5. v0.1 preserves every v0.1 / v0.2 runtime refusal.** The gate reuses the v0.1 / v0.2 admission identities, the v0.1 forbidden-pattern set, and the v0.2 execute-mode allowlist verbatim.

**L-6. v0.1 caps approved command count at three.** Any proposal whose `commands_proposed` exceeds three is rejected unconditionally.

**L-7. v0.1 produces a deterministic review hash.** Two runs of the same proposal under the same reviewer identity produce byte-identical `review_hash` (modulo the recorded-but-not-hashed `review_id` and `timestamp`).

**L-8. v0.1 fails closed.** Any unparseable input, missing field, hash mismatch, unknown proposer, empty rationale, forbidden command, allowlist miss, command-count over cap, or expected-work-order-id mismatch produces `decision = rejected` and `exit_status = 1`.

**L-9. v0.1 is not added to `make ci`.** `make review-gate-check` is opt-in.

**L-10. The reviewer gate has approval authority only over proposal admissibility. It has zero execution authority. Executor admission remains controlled by the real-agent runtime.** This is the gate's defining boundary, the property that distinguishes a deterministic admission filter from an autonomous agent.

---

**End of REVIEW GATE RUNTIME v0.1.**
