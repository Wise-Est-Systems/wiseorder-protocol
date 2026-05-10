# PROPOSER RUNTIME v0.1
## Bounded Candidate-Command Generation Under Governance, With Zero Execution Authority

**Status:** v0.1 — operational specification, normative for the proposer surface in `tools/proposer_runtime.py` and the `reports/proposer_runtime/` tree. The proposer runtime emits *candidate commands* derived from an admitted work order's declared scope; it never executes, never plans beyond a single bounded candidate set, never reaches the network, never spawns subprocesses, and never persists state outside a single per-run JSON record.

**Companion documents:** `REAL-AGENT-RUNTIME-v0.1.md` (dry-run base), `REAL-AGENT-RUNTIME-v0.2.md` (bounded subprocess execution), `WORKFORCE-EXECUTION-RUNTIME-v0.1.md` (work-order lifecycle), `AGENT-GOVERNANCE-WORKFORCE-v0.1.md` (roles + authority), `WORKFORCE-HARDENING-v0.2.md` (validator hardening), `WAIVER-MECHANISM-v0.1.md`, `FORBIDDEN-SURFACES-v0.1.md`, `VALIDATION-LAW-v0.1.md`, `REPLAY-LAW-v0.1.md`, `TRUST-LAW-v0.1.md`.

> **Core thesis.** A proposer is a candidate-generator, not an agent. It reads an admitted work order, intersects the work order's `required_gates` with the runtime's `EXECUTE_ALLOWED_COMMANDS` allowlist and the work order's `allowed_files`, and emits at most three deterministically-ordered candidate commands plus a rationale. The architecture is `proposer → reviewer gate → executor`, never `proposer → execute`. Execution authority remains exclusively with admitted executor identities under the v0.2 runtime.

> **Explicitly stated.**
>
> - **v0.1 creates governed proposal generation.** Candidate commands derived from a work order's declared scope, deterministically ordered, capped at three, classified through the v0.1/v0.2 forbidden-pattern set and the v0.2 execute-mode allowlist.
> - **v0.1 does NOT create autonomy.** The proposer cannot select work, cannot invent commands, cannot widen scope, cannot self-modify, cannot loop, cannot retry, cannot persist beyond a single proposal record, and cannot reach a kernel or a network.
> - **v0.1 does NOT execute.** No `subprocess.run`, no `os.exec*`, no `os.spawn*`, no shell, no model call, no RPC. The proposer's only output is a JSON proposal file.
> - **v0.1 does NOT bypass the reviewer.** A proposal is an *input* to a reviewer; it is not an instruction to the executor. An executor receives commands only after a separate human-or-reviewer-identity approval step that this runtime does not implement.
> - **The proposer may suggest work but possesses zero execution authority.** All execution authority remains exclusively with admitted executor identities under runtime policy enforcement.

---

## 1. Purpose

This document defines v0.1 of the Proposer Runtime. The v0.2 Real Agent Runtime closed the gap between classifier and process: an allowlisted command is now actually invoked. But v0.2 cannot decide what to run; every command is hand-supplied by the work order's `required_gates` or by an explicit operator `--command` argument. The proposer runtime closes a different, smaller gap: it converts a work order's declared scope into a small, deterministic, fully-classified set of candidate commands, so that a reviewer (human or future reviewer-identity) has a concrete object to approve or reject.

The proposer is bounded. It is the smallest possible addition that produces a *candidate set* without producing autonomy. It does not introduce model calls, network access, persistent daemons, retries, loops, or any new authority. It does not modify any v0.1 or v0.2 admission rule, command-policy verdict, filesystem-policy verdict, manifest field, or refusal code — those are imported verbatim through the v0.2 runtime's classifiers, which the proposer calls.

The proposer remains governance-anchored. It refuses to derive candidates from any work order whose status, assignment, or scope fields are inconsistent with the rules in `WORKFORCE-EXECUTION-RUNTIME-v0.1.md`. It refuses to emit any command outside the v0.2 execute allowlist. It refuses to emit any command that touches a path outside the work order's `allowed_files` (where the candidate command's argv contains path tokens). It produces a per-run proposal record under `reports/proposer_runtime/` with a deterministic content hash, and a non-zero exit status if any required field is missing, any candidate is rejected for cause, or the proposal would be empty.

## 2. Architecture

The runtime architecture is three roles, in order:

```
work order ──► proposer ──► reviewer gate ──► executor (v0.2 runtime)
              (this doc)    (out of scope)    (REAL-AGENT-RUNTIME-v0.2.md)
```

The proposer reads the work order and emits a proposal. The reviewer gate (a human owner under v0.1 governance, or a future reviewer-identity under a hardening cycle) decides whether the proposal is approved. Only after reviewer approval may the executor (the v0.2 runtime under `builder-01` / `release-01` / `canon_guardian-01` / `reviewer-01`) be invoked with the approved command set.

The architecture is explicitly NOT `proposer → execute`. There is no path from the proposer to a subprocess. There is no shared object the proposer can mutate that the executor reads from. There is no callback. There is no IPC. The only surface between proposer and executor is a JSON file written under `reports/proposer_runtime/`, which a reviewer must read, approve out-of-band, and then operationally hand to the executor as a command argument.

This is by design. A proposer that could call the executor would, the moment its reviewer gate was bypassed (by mistake, by collusion, or by a future hardening change), become an autonomous agent. The architectural separation is what prevents that. The execution boundary law (§9) makes this commitment explicit.

## 3. What Becomes Real In v0.1

The single property v0.1 adds: a work order's declared scope is now *enumerated* into a small bounded candidate set, not just admitted. Concretely:

- An approved-and-assigned work order is parsed under the same flat-YAML reader the v0.2 runtime uses. Admission rules from `REAL-AGENT-RUNTIME-v0.1.md` §6 are applied unchanged. A work order that fails admission yields zero candidates and a refusal-coded proposal.
- For each entry in `required_gates`, the proposer classifies the entry through `classify_execute_command` (the v0.2 deny-first then allowlist check). Entries that match the v0.2 allowlist become *candidate-eligible*. Entries that match a forbidden pattern, or fail the allowlist, become `commands_rejected` entries with a `policy_rejection` code.
- The candidate-eligible set is sorted lexicographically by command text. The first three entries (or fewer, if fewer exist) become `commands_proposed`. The proposer emits no other commands. There is no expansion, no inference, no widening.
- Each `commands_proposed` entry is annotated with the matching allowlist entry (`allowed_command_match`), the work-order id, the agent identity, the rationale string composed from the work order's `objective` field, and the allowed-files glob list under which any output of that command would have to fall.
- The full set is hashed (sha256 over a deterministic JSON serialization), and the hash is recorded as `deterministic_hash`. Two identical work orders processed by two identical proposers MUST produce byte-identical proposals (subject to the timestamp field, which is recorded but not hashed; see §6).
- The proposal is written to `reports/proposer_runtime/proposal-<run_id>.json` and to a corresponding `proposal-<run_id>.md` summary. Exit status is zero if and only if all admission and classification rules pass and at least one candidate command was emitted.

This is what becomes real in v0.1: a single bounded enumeration step per work order, captured to a proposal record. Nothing else.

## 4. What Remains Not Real

- **Execution authority.** The proposer does not invoke commands. It writes a JSON file. A subprocess is never spawned.
- **Autonomy.** The proposer never selects which work order to process. The work-order path is a CLI argument. The proposer does not scan the work-order tree, does not pick from `workforce/work_orders/open/`, does not schedule itself.
- **Model calls.** No LLM, no embedding service, no classifier, no RPC. The candidate set is derived from string operations against the work order, not from a learned model.
- **Background processing.** No daemon, no scheduler, no event loop, no `asyncio`. Each invocation is a single-shot CLI command that reads one work order, writes one proposal, and exits.
- **Network access.** No `urllib.request`, no `socket.connect`, no HTTP, no SSH. The proposer's allowlist of operations is strictly more restrictive than the v0.2 execute allowlist: the proposer cannot emit, propose, or even reference network commands.
- **Recursive self-modification.** The proposer cannot propose commands that edit `tools/proposer_runtime.py` itself, the `reports/proposer_runtime/` tree, or the v0.2 runtime. A candidate whose argv contains any of these paths is rejected with `recursive_self_modification`.
- **Multi-step plans.** The proposer emits at most three candidate commands, with no notion of dependency, ordering-by-causation, or step-execution. The set is a *bag*, sorted lexicographically; the executor is responsible for whatever ordering it chooses.
- **Retries.** The proposer does not re-propose. A run that yields a refusal yields a refusal record; the next run, if the human owner adjusts the work order, will produce a fresh proposal.
- **Cross-run memory.** Two proposals do not chain. The proposer carries no state between runs.
- **Cron, daemon, service, hook.** The proposer is not registered with `launchd`, `systemd`, `cron`, `at`, a git hook, or any other scheduler. It runs only when explicitly invoked.
- **Inclusion in `make ci`.** v0.1's targets are opt-in.

These boundary lines are the same as the v0.2 runtime's, with the additional *subprocess prohibition* and the *recursive-self-modification prohibition* — both stricter than v0.2.

## 5. Constraints

The proposer enforces the following hard constraints. Every constraint has a corresponding refusal code (§7) and a corresponding self-check fixture (§8).

| Constraint | Enforcement |
| --- | --- |
| At most three commands proposed | Truncation of the sorted candidate-eligible set to length 3 before emission |
| Deterministic ordering | Lexicographic sort of candidate command text |
| No networking | `FORBIDDEN_COMMAND_PATTERNS` from v0.1 imported unchanged; any candidate matching a network pattern is rejected before sorting |
| No `shell=True` | No subprocess invocation occurs; the constraint holds vacuously and is enforced at code-review time by absence of any `subprocess` import in the proposer module |
| No subprocess execution | No `subprocess`, `os.exec*`, `os.spawn*`, or `os.popen` import; the proposer module imports stdlib `argparse`, `datetime`, `fnmatch`, `hashlib`, `json`, `pathlib`, `re`, and the v0.2 runtime's classifier functions only |
| No model downloads | No HTTP client imported; no `pip install` shelled out; no model-format file referenced by the proposer module |
| No persistence beyond proposal record | Single write to `reports/proposer_runtime/proposal-<run_id>.{json,md}`; no caches, no databases, no temp directories outside the report path |
| No recursive self-modification | A candidate whose argv contains any of `tools/proposer_runtime.py`, `reports/proposer_runtime/`, or `PROPOSER-RUNTIME-v0.1.md` is rejected with `recursive_self_modification` |
| No background loop | The CLI's `main()` returns after one work order; no `while True`, no `for ever`, no signal-handler-driven re-entry |
| No daemon | No `os.fork`, no `os.setsid`, no detach-from-tty pattern |
| No cron | No CronCreate, no scheduled remote agent, no Makefile target that registers a periodic run |
| No autonomous retries | A refusal exits non-zero immediately; the proposer never re-derives, never re-classifies, never tries an alternate path |

Every constraint is a refusal class; none is a soft warning. A violation produces an exit status of one and a refusal-coded proposal record.

## 6. Proposal Output Schema

Every proposal record is a JSON file written to `reports/proposer_runtime/proposal-<run_id>.json`, accompanied by a human-readable Markdown summary at `proposal-<run_id>.md`. The JSON schema is:

| Field | Type | Meaning |
| --- | --- | --- |
| `proposal_id` | string | identifier of the form `proposal-<run_id>`, where `run_id` includes the agent id and a UTC timestamp |
| `work_order_id` | string | the admitted work order's `work_order_id` field; empty on admission refusal |
| `agent_id` | string | the proposing identity; one of the four v0.1 / v0.2 identities |
| `rationale` | string | a non-empty single sentence drawn from the work order's `objective` field; empty rationale is a refusal |
| `commands_proposed` | list of objects | up to three candidate command objects (see below); empty if every candidate was rejected |
| `commands_rejected` | list of objects | every candidate that failed classification, with the failing reason |
| `policy_rejections` | list of strings | refusal codes raised during classification (e.g., `forbidden_pattern`, `not_in_execute_allowlist`, `recursive_self_modification`, `path_outside_allowed_files`) |
| `allowed_command_matches` | list of strings | the v0.2 `EXECUTE_ALLOWED_COMMANDS` entries that the proposed commands matched, sorted lexicographically |
| `timestamp` | ISO-8601 UTC string | when the proposal was generated; not included in the deterministic hash input |
| `deterministic_hash` | `sha256:<hex>` | sha256 of the JSON serialization of the proposal record with the `timestamp` and `deterministic_hash` fields removed; verifies that two runs of the same work order produce identical proposals |
| `runtime_version` | string | `"v0.1"` for the proposer runtime |
| `exit_status` | int | 0 if the proposal succeeded with at least one command proposed; 1 otherwise |

**`commands_proposed` entry shape:**

| Key | Type | Meaning |
| --- | --- | --- |
| `command` | string | the full command text as it appears in the work order's `required_gates` |
| `argv_preview` | list of strings | a tokenized preview of the command (for human review only; the executor will re-tokenize under v0.2 before invocation) |
| `allowed_command_match` | string | the v0.2 allowlist entry the command matched |
| `allowed_files_scope` | list of strings | the work order's `allowed_files` entries that any output of the command would have to fall under |
| `rationale` | string | the per-command rationale, derived from the work order's `objective` |

**`commands_rejected` entry shape:**

| Key | Type | Meaning |
| --- | --- | --- |
| `command` | string | the full rejected command text |
| `reason` | string | the failing classifier reason |
| `code` | string | the refusal code (one of the codes in §7) |

The proposal record is sorted by key, indented two spaces, and written in UTF-8 with a trailing newline. Both the JSON and Markdown variants are committed under `reports/proposer_runtime/`.

## 7. Refusal Classes

The proposer fails closed. Every refusal produces `exit_status = 1` and a recorded entry in `policy_rejections`.

| Refusal code | Source | Trigger |
| --- | --- | --- |
| `unknown_agent_identity` | admission (v0.2 verbatim) | agent id not in `IDENTITIES` |
| `missing_required_field` | admission (v0.2 verbatim) | work order missing `work_order_id`, `status`, or other v0.1 required field |
| `status_not_admissible` | admission (v0.2 verbatim) | work order's status not in identity's `allowed_statuses` |
| `assigned_to_mismatch` | admission (v0.2 verbatim) | work order's `assigned_to` empty or not equal to agent id |
| `missing_allowed_files` | admission (v0.2 verbatim) | work order's `allowed_files` missing or empty |
| `missing_forbidden_files` | admission (v0.2 verbatim) | work order's `forbidden_files` missing or empty |
| `empty_rationale` | proposer | work order's `objective` is empty or contains only whitespace |
| `forbidden_pattern` | classifier (v0.1 verbatim) | candidate matches `FORBIDDEN_COMMAND_PATTERNS` |
| `not_in_execute_allowlist` | classifier (v0.2 verbatim) | candidate is not blocked but does not match `EXECUTE_ALLOWED_COMMANDS` |
| `path_outside_allowed_files` | proposer | candidate's argv contains a path token that does not match any `allowed_files` glob |
| `recursive_self_modification` | proposer | candidate's argv mentions `tools/proposer_runtime.py`, `reports/proposer_runtime/`, or `PROPOSER-RUNTIME-v0.1.md` |
| `network_proposal` | proposer | candidate's argv contains `http://`, `https://`, `://`, or any of `curl`, `wget`, `ssh`, `scp` (a stricter subset of the v0.1 forbidden patterns, raised under a more specific code so reviewers can read the proposal at a glance) |
| `empty_proposal` | proposer | every candidate was rejected; no command can be proposed |
| `cap_exceeded` | proposer | the candidate-eligible set was greater than three; the cap was applied and the overflow recorded as `cap_exceeded` (not a refusal of the run, but an entry in `policy_rejections` so the audit trail makes the cap explicit) |

The runtime never fails open. Any unexpected condition surfaces as a Python exception with a traceback. The CLI does not swallow exceptions silently.

## 8. Required Self-Check Fixtures

The proposer's self-check fixture suite (`run_self_check`, exposed via `make proposer-check`) covers the seven cases below. All seven MUST pass at v0.1 closure time and at every subsequent gate run.

1. **`forbidden_command_proposal_refused`** — fixture work order whose `required_gates` includes `curl https://example.com`; classifier rejects with `forbidden_pattern`; the rejected command appears in `commands_rejected`; `policy_rejections` contains `forbidden_pattern`; if no other gate is admissible, `exit_status = 1` and the refusal code `empty_proposal` is also recorded.
2. **`proposal_outside_allowed_files_refused`** — fixture whose `required_gates` includes a candidate referencing a path outside `allowed_files`; classifier rejects with `path_outside_allowed_files`; the rejected command appears in `commands_rejected`.
3. **`recursive_self_modification_refused`** — fixture whose `required_gates` includes a candidate referencing `tools/proposer_runtime.py`; classifier rejects with `recursive_self_modification`.
4. **`network_proposal_refused`** — fixture whose `required_gates` includes a candidate referencing `https://`; classifier rejects with `network_proposal` (and additionally `forbidden_pattern`, since the v0.1 forbidden set covers `https://`).
5. **`empty_rationale_refused`** — fixture whose `objective` field is empty or whitespace; admission accepts but proposer refuses with `empty_rationale` before classification.
6. **`cap_truncates_to_three`** — fixture whose `required_gates` contains five admissible commands; the proposal contains exactly three commands, sorted lexicographically; `policy_rejections` contains `cap_exceeded`; `exit_status = 0`.
7. **`deterministic_hash_stable`** — running the proposer twice on the same fixture produces two proposals whose `deterministic_hash` values are byte-identical (despite differing `timestamp` fields).

The test harness writes per-run proposal records to `reports/proposer_runtime/` and a v0.1 self-check report to `reports/proposer_runtime/proposer_runtime_v0.1.{md,json}`.

## 9. Execution Boundary Law

This section is the runtime's terminal commitment. Every implementation choice in `tools/proposer_runtime.py` MUST be consistent with the law statement below.

> **The proposer may suggest work but possesses zero execution authority. All execution authority remains exclusively with admitted executor identities under runtime policy enforcement.**

The proposer is a *candidate-generator*, not an *agent*. Its proposal is an *input* to a reviewer, not an instruction to the executor. There is no path from `tools/proposer_runtime.py` to `subprocess.run`, no shared queue the executor reads from, no IPC, no callback. The architectural separation between proposer, reviewer, and executor is the load-bearing element of the v0.1 design. A future hardening cycle that adds a reviewer-identity (the missing third role from `AGENT-GOVERNANCE-WORKFORCE-v0.1.md`) MUST preserve this separation: a reviewer-identity may approve a proposal, but it MUST NOT be the same process as the proposer, and it MUST NOT cause the executor to be invoked without an out-of-band human-or-reviewer-identity gate.

A proposal whose review gate is bypassed and is handed directly to the executor is *operator misuse*, not a runtime feature. The runtime cannot prevent operator misuse; it can only refuse to participate in it. The proposer's contribution to that refusal is its complete absence of execution surface.

## 10. What Makes This Still Non-Autonomous

The v0.1 proposer is bounded by ten properties that, taken together, make it not an autonomous agent. Removing any one of them would change the class of artifact the proposer is.

1. **No will of its own.** The proposer never selects which work order to process. The work-order path is a CLI argument. The proposer does not enumerate the work-order tree, does not pick from `workforce/work_orders/open/`, does not have a notion of "which work order is most important right now."
2. **No execution surface.** The proposer's module imports no subprocess, no exec, no spawn, no shell. The strongest verb the proposer can perform is `Path.write_text`.
3. **No persistence beyond a single proposal record.** No cache, no database, no scratch directory. The proposer cannot remember, cannot learn, cannot adapt across runs.
4. **No loop.** `main()` returns after one work order. There is no `while`, no scheduler, no signal-handler-driven re-entry.
5. **No retry.** A refusal is terminal. The proposer does not re-derive, does not back off, does not try an alternate strategy.
6. **No widening.** The proposer cannot emit a command not present in the work order's `required_gates`. It cannot infer "the work order asked for X, so probably Y also." The candidate set is intersection, not generation.
7. **No model.** No LLM, no embedding, no classifier. The candidate set is computed by string operations against the work order text and the v0.2 allowlist.
8. **No network.** No HTTP, no socket, no DNS lookup. The proposer cannot reach a remote host even if it wanted to.
9. **No self-modification.** The proposer cannot propose commands that edit itself, its outputs, or its specification. A future change to the proposer requires a human-approved work order to `tools/proposer_runtime.py`, not a proposer-generated proposal.
10. **No path to the executor without a human-or-reviewer-identity gate.** The architectural separation in §2 and §9 means the proposer's output is a JSON file on disk, not a function call into the executor. A reviewer must approve, the operator must hand the approved command to the executor, and only then does a subprocess run.

These ten properties are what distinguish a *governed proposal generator* from an *autonomous AI agent*. A v0.2 runtime that took its commands from a future "proposer-without-reviewer" would cross that line. The v0.1 proposer does not.

## 11. CLI

The proposer exposes two CLI verbs:

- `tools/proposer_runtime.py propose --work-order PATH --agent-id ID` — read the work order at PATH, derive the candidate set under identity ID, write the proposal record under `reports/proposer_runtime/`, exit 0 if at least one command was proposed and no admission refusal was raised, 1 otherwise.
- `tools/proposer_runtime.py self-check` — run the seven self-check fixtures (§8) end-to-end, refresh the runtime report at `reports/proposer_runtime/proposer_runtime_v0.1.{md,json}`, exit 0 if all seven match expected outcome, 1 otherwise.

The Makefile exposes two targets, neither in `make ci`:

- `make proposer-propose WO=<path> AGENT=<id>` — invoke `propose` with the given work order and agent identity.
- `make proposer-check` — invoke `self-check`.

## 12. Future Work

The v0.1 proposer is the smallest possible candidate-generator. Future hardening work is enumerated here for the record; none of it is authorized by this document, and each item requires its own drafted-approved-assigned governance work order.

- **Reviewer identity.** The missing third role from `AGENT-GOVERNANCE-WORKFORCE-v0.1.md` is the natural consumer of the proposer's output. A `reviewer-02` identity that reads proposal records, applies a policy, and emits an `approval` or `rejection` artifact would be the next layer above the proposer. Implementing it must preserve the architectural separation in §9.
- **Multi-step proposals.** A future proposer could emit ordered candidate sequences (with declared dependency edges), provided the cap remains small (three is the v0.1 cap; any expansion is a governance decision, not a runtime decision) and the determinism property remains intact.
- **Proposal replay validation.** A future tool could re-derive a proposal from its work order and compare the new `deterministic_hash` against the recorded one, flagging any drift in either the work order or the proposer's classifier.
- **Reviewer-identity policy DSL.** A future reviewer-identity could read a small declarative policy file and approve or reject proposals automatically, provided every approval still requires a human-or-reviewer-identity gate before the executor is invoked.

None of these expand execution authority. Every one of them preserves the boundary in §9.

## 13. Final Law

The proposer is bounded by the following ten law statements. They are this document's terminal commitments; everything above is implementation.

**L-1. v0.1 creates governed proposal generation.** A previously absent layer between work-order admission and command execution now exists. A work order's declared scope is enumerated, classified, sorted, capped, hashed, and committed to a proposal record under `reports/proposer_runtime/`.

**L-2. v0.1 does NOT create autonomy.** The proposer cannot select work, cannot invent commands, cannot widen scope, cannot persist beyond a single proposal record, cannot loop, cannot retry, cannot reach a network, cannot call a model, cannot modify itself, and cannot invoke the executor.

**L-3. v0.1 does NOT execute.** No subprocess is spawned. No shell is invoked. The proposer's strongest verb is a single JSON file write. Execution authority remains exclusively with the v0.2 runtime under admitted executor identities.

**L-4. v0.1 enforces the architecture proposer → reviewer gate → executor.** There is no path from the proposer to the executor that does not pass through a reviewer gate. The reviewer gate is implemented in v0.1 as the human owner; a future hardening cycle may add a reviewer-identity, provided the architectural separation is preserved.

**L-5. v0.1 preserves every v0.1 and v0.2 runtime refusal.** The proposer reuses the v0.1 / v0.2 admission rules, the v0.1 forbidden-pattern set, and the v0.2 execute-mode allowlist verbatim. No previously refused command can be proposed by this runtime.

**L-6. v0.1 caps proposal size at three commands.** Even a work order whose `required_gates` contains many admissible entries produces at most three proposed commands, deterministically sorted. The cap is a hard constraint enforced at emission time.

**L-7. v0.1 produces a deterministic content hash.** Two runs of the same work order under the same proposer version produce byte-identical proposals (modulo the recorded-but-not-hashed `timestamp` field). The `deterministic_hash` is the audit anchor.

**L-8. v0.1 fails closed.** Any unknown identity, missing field, inadmissible status, mismatched assignment, missing scope list, empty rationale, forbidden pattern, allowlist miss, path-outside-allowed-files match, recursive-self-modification reference, or empty proposal produces `exit_status = 1` and a recorded refusal code in `policy_rejections`.

**L-9. v0.1 is not added to `make ci`.** `make proposer-check` is opt-in. A future hardening cycle may evaluate inclusion in `make ci`; v0.1 explicitly does not.

**L-10. The proposer may suggest work but possesses zero execution authority.** All execution authority remains exclusively with admitted executor identities under runtime policy enforcement. This is the proposer's defining boundary, the property that distinguishes a governed candidate-generator from an autonomous agent.

These ten law statements are the proposer's normative commitments at v0.1. They name what is now real (governed candidate generation), what is still not real (autonomy, execution, persistence, loops, networks, models), preserve every v0.1 and v0.2 boundary, and establish the smallest reviewable surface on which a future hardening cycle can build a reviewer-identity without ever crossing into autonomous agency.

---

**End of PROPOSER RUNTIME v0.1.**
