# WAIVER MECHANISM v0.1
## The Only Admissible Mechanism For Scoped, Replayable, Human-Approved Operational Exceptions

**Status:** v0.1 — normative governance instrument for the WiseOrder / Intellagent stack. Non-overlapping with runtime, validator, workflow, authority, forbidden-surface, validation-law, replay-law, correction-law, trust-law, and authority-law semantics. This document does not redefine those layers; it constrains the single, named operational exception class that permits a recorded deviation from `allowed_files` / `forbidden_files` to close a work order without weakening any of those layers.
**Companion documents:** `WORKFORCE-EXECUTION-RUNTIME-v0.1.md`, `AGENT-GOVERNANCE-WORKFORCE-v0.1.md`, `AUTHORITY-LAW-v0.1.md`, `VALIDATION-LAW-v0.1.md`, `REPLAY-LAW-v0.1.md`, `CORRECTION-LAW-v0.1.md`, `TRUST-LAW-v0.1.md`, `FORBIDDEN-SURFACES-v0.1.md`, `SPEC-EVOLUTION-POLICY-v0.1.md`, `reports/DOC-COMPLETION-AUDIT-v0.1.md`.

> **Core thesis.** A waiver is a recorded exception, not an expansion of authority. It does not enlarge what the system permits; it documents, names, and time-stamps the single moment at which the system tolerated a scope deviation under explicit human-owner authority — and it does so while preserving the original deviation, the validator's verdict, every required gate, the canon, and the replay record verbatim. A waiver that cannot be replayed from on-disk record alone is not a waiver. It is hidden authority, and hidden authority is the failure mode the protocol exists to refuse.

---

## 1. Purpose

This document defines the only admissible mechanism — the **waiver mechanism** — for scoped, replayable, human-approved operational exceptions to the `allowed_files` / `forbidden_files` discipline declared by `WORKFORCE-EXECUTION-RUNTIME-v0.1.md` §21 (work-order content immutability).

A waiver is a narrow, named, file-grounded operational exception. It exists because two of the three closures performed against the workforce runtime so far (`WO-2026-05-07-001` deviations V-1 and V-3) required closure-time amendments to `forbidden_files`. Those amendments were sanctioned by the human owner under direct authority and recorded as `status_history` entries of state `amended`, but no canon document declared that this exception class exists, what fields a valid waiver must carry, or what an invalid waiver looks like. Convention was load-bearing where declaration must be.

This document terminates that gap. It defines:

- what a waiver IS,
- what a waiver IS NOT (the longer list — §4 and §15 and §16),
- when a waiver may be claimed,
- what fields a waiver must carry to be valid,
- what an invalid waiver is,
- what a waiver is forbidden from claiming,
- and how a waiver replays.

This document does NOT extend authority. It bounds and names an exception that is already being used in the absence of declaration. It does NOT redesign runtime, validator, workflow, or authority semantics; it does NOT redefine canon; it does NOT expand the remaining-doc queue identified by `reports/DOC-COMPLETION-AUDIT-v0.1.md` §15. Its function is to lock convention into declaration.

---

## 2. Why Waivers Exist

Waivers exist because real closures of audit-only and release-and-continuity work orders have required, and will require, three categories of file-scope deviation that the work-order schema cannot enumerate at draft time:

1. **Audit-grounding reads into `forbidden_files`.** A reviewer-role or canon_guardian-role audit may need to read a forbidden file to verify a claim about it (e.g., reading the Makefile to confirm that a gate is wired into CI; reading the validator script to confirm the closure-time invariants the validator enforces).
2. **Closure-time corrections to `forbidden_files`.** The validator may surface, at closure time, a `forbidden_file_read` violation that the operator's pre-closure self-check missed. The choice is then between rejecting the work order (and discarding the audit work the deviation produced) or amending `forbidden_files` to remove the file and recording the deviation openly.
3. **Procedural lifecycle reorderings.** The validator may surface lifecycle-ordering violations whose correction requires a small adjustment to a status_history timestamp without a substantive change to what occurred.

Without waivers, the system has only two responses to such deviations: reject the work order (and lose the on-disk evidence the deviation produced) or accept the deviation silently (and lose the on-disk evidence of the exception). Both responses are corrosive. Waivers make the third response — record the exception, preserve the evidence, and preserve the validator's verdict — into a sanctioned, named, replayable mechanism.

Waivers exist for the operational reality that **deviations happen, and the protocol's job is not to deny that they happen but to record them under bounded authority such that every deviation, every justification, every original state, every post-waiver state, and every authority signature is reconstructable from on-disk record alone.**

---

## 3. Waiver Scope

A waiver applies to **exactly and only** the following work-order content fields:

- `allowed_files` (closure-time addition or modification of a single named file pattern, with the file-grounded justification recorded)
- `forbidden_files` (closure-time removal or modification of a single named file pattern, with the file-grounded justification recorded)

A waiver MUST NOT be claimed against, MUST NOT modify, and MUST NOT be construed to modify, any of the following:

- `objective`
- `agent_role`
- `assigned_to`
- `constraints`
- `expected_outputs`
- `required_gates`
- `rollback_plan`
- `human_approval_required`

These fields are immutable post-draft per `WORKFORCE-EXECUTION-RUNTIME-v0.1.md` §21 and remain immutable under every waiver claim. A waiver is the *only* declared exception to the immutability rule, and its scope is *exactly* the file-scope fields. Any claim that touches any other field is an invalid waiver and the validator MUST refuse closure (see §15).

A waiver also MUST NOT alter or remove any element of `status_history` other than appending a new entry of state `amended`. The append is the waiver record; prior entries are preserved verbatim.

---

## 4. Waiver Non-Authority

A waiver IS NOT authority. A waiver does not grant the agent any new permission to act; it records that a specific past deviation is, in retrospect, accepted by the human owner under stated rationale.

Specifically:

- A waiver does NOT permit a future agent to read, write, or otherwise act on the file pattern that was waived. The waiver applies to the single recorded deviation in the action log, not to any other action under the same work order or any other work order.
- A waiver does NOT make the file pattern "always permitted" for the role; the role's general permissions are governed by `AGENT-GOVERNANCE-WORKFORCE-v0.1.md`, not by waivers.
- A waiver does NOT delegate human-owner authority to the agent. The waiver itself must be authored by the human owner and recorded as a `status_history` entry whose actor is a human-owner identity.
- A waiver does NOT carry forward to successor work orders. Each work order's `allowed_files` and `forbidden_files` are interpreted at draft time; prior waivers on prior work orders do not modify the new work order's scope.
- A waiver does NOT reduce the validator's enforcement strength. After a waiver is recorded, the validator's enforcement of the (now-amended) `allowed_files` / `forbidden_files` continues to operate at full strength against the rest of the action log.

The relationship between authority and waivers is asymmetric. Authority creates permission; waivers record that a specific permission boundary was crossed and why. Authority is forward-looking; waivers are backward-looking. A waiver is the system declaring "this happened, and we have accepted it under recorded rationale," not "this is now allowed."

---

## 5. Human Approval Requirements

A waiver is valid only when the human owner explicitly authors and records it. Specifically:

- The waiver MUST appear in `status_history` as an entry of state `amended`.
- The `actor` field of the amended entry MUST be a human-owner identity (e.g., `henry-wayne-wise-iii`). It MUST NOT be an agent identity, a release identity, or any non-human actor string.
- The `timestamp` field MUST be ISO-8601 UTC and MUST fall within the closure-cycle window of the work order (between the predecessor action log's `timestamp_start` and the work order's `closed` `status_history` entry).
- The `note` field MUST contain, at minimum: the V-number of the deviation being waived (e.g., `V-1`), the rationale (file-grounded, referencing the specific claim the deviation supported), the *exact* change to `allowed_files` or `forbidden_files` (e.g., "remove `Makefile` from `forbidden_files`"), and a statement that the original deviation is preserved verbatim in the action log.

A waiver authored by anyone other than the human owner is an invalid waiver. A waiver whose note is non-specific, narrative-only, or fails to cite the V-number of the deviation is an invalid waiver. A waiver whose timestamp is outside the closure-cycle window is an invalid waiver.

The human-owner authorship requirement is the load-bearing element of waiver legitimacy. A waiver is fundamentally a record of an authority exercise; without a recorded human-owner exercise, it is not a waiver.

---

## 6. Allowed Files Waiver

An **allowed_files waiver** is a closure-time addition of a single named file pattern to `allowed_files`. It is admissible only when:

- the action log records a write to a file that does not currently match `allowed_files`,
- the write was non-canon (does not modify SPEC, vectors, canonicalization corpus, runtime, or validator semantics),
- the file is not in `forbidden_files`,
- the human owner authors the waiver under §5,
- the original deviation (recorded as a violation against `allowed_files`) is preserved verbatim in the action log,
- the validator's clean exit at closure time confirms the post-waiver state.

An allowed_files waiver MUST NOT be used to:

- broaden the work order's scope after the action log has been written,
- conceal a file write that the validator has already classified as `out_of_scope_change`,
- add canon paths (e.g., `SPEC.md`, `vectors/**`, `canonicalization/corpus/**`) — those are governed by `SPEC-EVOLUTION-POLICY-v0.1.md`, not by waivers,
- permit a write to a path that is in `forbidden_files`. The path MUST first be removed from `forbidden_files` via §7's mechanism if both fields apply.

The allowed_files waiver's grammatical form: append a new `status_history` entry of state `amended`, actor = human-owner identity, timestamp = ISO-8601 UTC, note specifying the exact `allowed_files` extension and the V-number of the recorded deviation.

---

## 7. Forbidden Files Waiver

A **forbidden_files waiver** is a closure-time removal of a single named file pattern from `forbidden_files`. It is the most common waiver class in practice and was the mechanism used to close `WO-2026-05-07-001`'s V-1 (Makefile read) and V-3 (tools/check_workforce.py read) deviations.

A forbidden_files waiver is admissible only when:

- the action log records a non-mutating read into the forbidden tree,
- the read was audit-grounding (i.e., the deviation note in the action log states a specific claim the read was used to verify),
- the read produced no implementation change, no canon mutation, no validator weakening, and no security-posture change,
- the human owner authors the waiver under §5,
- the original deviation is preserved verbatim in the action log,
- the validator's clean exit at closure time confirms the post-waiver state.

A forbidden_files waiver MUST NOT be used to:

- waive a write into a forbidden tree. Writes into `forbidden_files` are not waivable; they require a successor correction work order or a rollback,
- waive reads of `SPEC.md`, `vectors/**`, `canonicalization/corpus/**`, or any path that affects canon legitimacy. Those reads are governed by `SPEC-EVOLUTION-POLICY-v0.1.md` and require a canon-touch waiver under §10 (which is itself further constrained),
- pre-emptively shrink `forbidden_files` for future agents. The waiver applies to the single recorded read, not to future reads.

The forbidden_files waiver's grammatical form: append a new `status_history` entry of state `amended`, actor = human-owner identity, timestamp = ISO-8601 UTC, note specifying the exact `forbidden_files` removal and the V-number of the recorded deviation.

---

## 8. Read-Only Waiver

A **read-only waiver** is the special case of §7 in which the deviation involved no write whatsoever. Every closure to date has involved read-only waivers and no write waivers; this is the desired profile.

A read-only waiver is admissible only when:

- `files_changed` does NOT contain the waived path,
- `files_read` records the path as a non-mutating open,
- the read served an audit-grounding purpose recorded in the action log's deviation note,
- all conditions of §7 are also met.

The read-only profile is the lowest-risk waiver class. The validator distinguishes between `forbidden_file_read` (waivable under §7 / §8) and `forbidden_file_change` (NOT waivable; requires rollback or correction work order).

The read-only waiver does not permit any persistence of file content. The agent MAY NOT copy, hash, embed, or otherwise persist the contents of the read file beyond what the action log explicitly records. Persistence beyond the action log record is hidden persistence and is forbidden under §16.

---

## 9. Closure-Time Waiver

A **closure-time waiver** is any waiver authored after the predecessor action log's `timestamp_end` and before the work order's `closed` `status_history` entry. All sanctioned waivers in v0.1 are closure-time waivers.

The closure-time waiver class is the only class of waiver permitted by this document. Specifically:

- **Pre-execution waivers are forbidden.** A waiver authored before the agent has begun executing the work order is not a waiver — it is a draft modification, and the work order should be re-drafted with the corrected scope rather than amended at closure.
- **Mid-execution waivers are forbidden.** A waiver authored between the predecessor action log's `timestamp_start` and `timestamp_end` is not a waiver — it is a real-time scope expansion, which the protocol does not permit. The agent must complete the action log honestly recording the deviation, and the waiver is then evaluated at closure time.
- **Post-closure waivers are forbidden.** A waiver authored after the work order is in `closed/` is not a waiver — it is a retroactive rewrite of a closed record, which the protocol explicitly forbids under §16.

The closure-time window is bounded: from the predecessor action log's `timestamp_end` (when the agent stops acting) through the closure action log's `timestamp_end` (when the closure operator stops acting), with the `closed` status_history entry as the terminal marker. Waivers MUST be authored within this window. A waiver authored outside this window is invalid.

---

## 10. Canon-Touch Waiver

A **canon-touch waiver** is a hypothetical waiver that would permit a deviation involving a canon path (`SPEC.md`, `STATUS-REGISTRY.md`, `ARTIFACTS.md`, `CONFORMANCE.md`, `vectors/**`, `canonicalization/corpus/**`, `IMPLEMENTATIONS.md` insofar as it carries declaration discipline).

**Canon-touch waivers DO NOT EXIST under this document.** Any deviation involving a canon path is governed by `SPEC-EVOLUTION-POLICY-v0.1.md`, not by waivers. Specifically:

- A non-mutating read of a canon path is *not* a deviation against `forbidden_files` because the canon path was readable as part of the work order's natural scope (canon documents are top-level `.md` and typically present in `allowed_files` via the `*.md` glob).
- A *write* to a canon path is *never* admissible under a waiver. It requires a canon-amendment work order under `SPEC-EVOLUTION-POLICY-v0.1.md` with explicit per-document deltas, version-bump justification, and the full release-cycle gates.
- A *read or write* of `vectors/**` or `canonicalization/corpus/**` under a work order whose `forbidden_files` includes those paths is *never* admissible under a waiver. Those paths are the protocol's truth set; they are governed by `SPEC-EVOLUTION-POLICY-v0.1.md` exclusively.

The non-existence of canon-touch waivers is load-bearing on the protocol's legitimacy. Waivers exist for operational expedience under bounded authority. Canon evolution exists for protocol evolution under maximal authority. Conflating the two would erase the distinction the protocol depends on.

---

## 11. Validator Conflict Waiver

A **validator conflict waiver** is a waiver authored when the validator surfaces, at closure time, a violation that the operator's pre-closure self-check missed. `WO-2026-05-07-001`'s V-3 deviation (the read of `tools/check_workforce.py`) was a validator conflict waiver: the closure-summary text initially claimed no amendment was needed for V-3; the validator contradicted that claim and emitted a `forbidden_file_read` violation; the human owner authored a second `amended` entry to resolve the conflict.

A validator conflict waiver is admissible only when:

- the validator has emitted a specific named violation (e.g., `forbidden_file_read`, `forbidden_file_change`, `out_of_scope_change`, `lifecycle_out_of_order`, `gates_missing`),
- the violation maps to a deviation already recorded in the action log,
- the human owner authors the waiver under §5,
- the closure summary is updated (or written for the first time) to reflect the corrected understanding,
- the original validator output is preserved (typically in the closure action log's `command_outputs_summary`).

A validator conflict waiver MUST NOT be used to:

- silence the validator. The validator's verdict is preserved in record; the waiver records that the verdict is acknowledged, not that it is rescinded.
- weaken the validator's rules. The waiver applies to a single deviation; the rule continues to fire on every other deviation.
- claim that the validator was "wrong." The validator is the authority on procedural conformance per `VALIDATION-LAW-v0.1.md`. A waiver records that the operator accepts the validator's verdict and amends the work order accordingly.

The validator conflict waiver's mechanical role: when validator and closure-summary text disagree, the validator wins. The waiver is the operator's recorded acknowledgement and the resulting amendment.

---

## 12. Waiver Record Requirements

A valid waiver MUST appear in the on-disk record as a `status_history` entry of state `amended` carrying the following sub-fields:

| Field | Type | Requirement |
| --- | --- | --- |
| `state` | string | MUST be exactly `amended`. |
| `actor` | string | MUST be a non-empty human-owner identity. |
| `timestamp` | string | MUST be ISO-8601 UTC; MUST fall within the closure-cycle window per §9. |
| `note` | string | MUST contain: V-number of the deviation; rationale (file-grounded); exact field change (e.g., "remove `Makefile` from `forbidden_files`"); statement that original deviation is preserved verbatim in the action log; statement that no canon, runtime, validator, or security-posture change occurred. |

In addition, the closure action log MUST record:

| Field | Requirement |
| --- | --- |
| `files_read` | The waived path appears here for read-only waivers; absent otherwise. |
| `files_changed` | The waived path appears here for write waivers (note: write waivers are constrained — see §7 / §10). |
| `commands_run` | Includes `make workforce-check` exit 0 *after* the waiver's status_history entry was added, demonstrating that the validator accepts the post-waiver state. |
| `command_outputs_summary` | Records both the pre-waiver validator output (the violation) and the post-waiver validator output (the clean exit). |
| `deviations` | Preserves the original deviation entry verbatim, with no edit, deletion, or rewording. |

The closure summary MUST document:

- the V-number being waived,
- the human-owner amendment timestamp,
- the rationale (referencing the file-grounded claim the deviation supported),
- a statement that the validator's pre-waiver verdict is preserved in the action log and that the post-waiver verdict was clean,
- a statement that no canon, runtime, validator, or security-posture change occurred,
- a statement that the waiver does not apply to future work orders.

The waiver record schema, derived from §8 audit-trail requirements of `WORKFORCE-EXECUTION-RUNTIME-v0.1.md`:

```
amended-entry = {
  state:     "amended",
  actor:     <human-owner-identity, non-empty>,
  timestamp: <ISO-8601 UTC, within closure-cycle window>,
  note: {
    deviation_v_number:    <V-N>,
    justification:         <file-grounded text>,
    scope:                 <"allowed_files" | "forbidden_files">,
    field_change:          <verbatim before/after specification>,
    original_state_hash:   <SHA-256 of pre-waiver work-order content; optional in v0.1>,
    post_waiver_state_hash: <SHA-256 of post-waiver work-order content; optional in v0.1>,
    predecessor_work_order_id: <WO-NNNN-NN-NN-NNN>,
    replay_invariants_preserved: [<list of preserved invariants>]
  }
}
```

The `original_state_hash` and `post_waiver_state_hash` fields are *optional in v0.1* because v0.1 records are not cryptographically attested; they become *required at v0.2* under `AGENT-IDENTITY-v0.1.md`'s eventual key-material specification (the audit's P3 entry). The `note` field's structured content above MAY be expressed as prose in v0.1 records as long as every named element is present.

---

## 13. Waiver Replay Requirements

A waiver MUST be replayable from on-disk record alone. Specifically:

- A reader, given only the on-disk repository state, MUST be able to identify every waiver by its `state: amended` `status_history` entry on a closed work order.
- A reader MUST be able to identify, for each waiver, the V-number of the deviation it waives by inspecting the action log's `deviations` field.
- A reader MUST be able to identify, for each waiver, the human-owner identity that authored it by inspecting the `actor` field.
- A reader MUST be able to identify, for each waiver, the timestamp at which it was authored by inspecting the `timestamp` field.
- A reader MUST be able to identify, for each waiver, the exact field change by inspecting the `note` field.
- A reader MUST be able to identify, for each waiver, the validator's pre-waiver verdict and post-waiver verdict by inspecting the closure action log's `command_outputs_summary`.
- A reader MUST be able to verify, for each waiver, that no canon, runtime, validator, or security-posture change occurred, by reading the closure summary.

Replay continuity is the load-bearing property of waivers. A waiver that fails any of the above replay requirements is not a waiver — it is hidden authority, even if it claims otherwise on disk. The validator MUST reject closure of any work order whose waiver claim fails replay.

---

## 14. Waiver Failure Classes

A waiver fails (i.e., is invalid and the validator MUST refuse closure) under any of the following classes:

- **F-1. Missing actor.** The `amended` `status_history` entry has an empty or non-human-owner `actor`.
- **F-2. Missing timestamp.** The `amended` entry has no `timestamp` or a timestamp outside the closure-cycle window.
- **F-3. Missing rationale.** The `amended` entry's `note` does not cite a V-number, does not state the rationale, or does not specify the exact field change.
- **F-4. Original deviation removed.** The action log's `deviations` field has been modified, edited, or pruned post-execution.
- **F-5. Canon path waived.** The waiver attempts to amend a canon path (`SPEC.md`, `vectors/**`, `canonicalization/corpus/**`) — see §10.
- **F-6. Out-of-scope field amendment.** The waiver attempts to modify any work-order field other than `allowed_files` or `forbidden_files` — see §3.
- **F-7. Validator pre-waiver verdict suppressed.** The closure action log does not record the validator's pre-waiver violation output.
- **F-8. Post-waiver verdict missing.** The closure action log does not record a `make workforce-check` exit-0 run *after* the waiver was added.
- **F-9. Out-of-window authoring.** The waiver is authored outside the closure-cycle window — see §9.
- **F-10. Forward-binding claim.** The waiver claims to apply to future work orders or to permanently broaden permissions — see §4.
- **F-11. Authority-expansion claim.** The waiver claims to grant the agent new permission rather than recording an exception — see §4.
- **F-12. Canon-mutation claim.** The waiver claims to modify canon (SPEC, vectors, canonicalization) under operational authority — see §10 and `SPEC-EVOLUTION-POLICY-v0.1.md`.
- **F-13. Validator-weakening claim.** The waiver claims to disable, soften, or stub a validator rule — see §11.
- **F-14. Gate-skip claim.** The waiver claims to skip a required gate — see §16.

These failure classes are the validator's targeting set. The validator MUST refuse closure of any work order in `closed/` whose waiver claim exhibits any of F-1 through F-14.

---

## 15. Invalid Waivers

An invalid waiver is any waiver claim that exhibits one or more of the failure classes in §14, OR that violates any of the following structural rules:

- A waiver that hides a change (e.g., does not record the modified file in `files_changed` of an action log) is invalid.
- A waiver that weakens an enforcement gate (e.g., removes a gate from `required_gates`, replaces a gate with a stub, or marks a failing gate as passed) is invalid.
- A waiver that mutates canon silently (e.g., modifies SPEC, vectors, canonicalization corpus without an explicit canon-amendment work order under `SPEC-EVOLUTION-POLICY-v0.1.md`) is invalid.
- A waiver that erases failure history (e.g., deletes a prior `gates_failed` entry, deletes a prior deviation, deletes a prior `amended` entry, deletes a prior `closed` entry, or otherwise modifies any prior status_history entry) is invalid.
- A waiver that re-anchors a closed work order's content fields beyond the explicitly-waivable file-scope fields is invalid.
- A waiver that attempts to apply itself retroactively to a record that has already been replayed (i.e., to a work order already in `closed/`) is invalid; corrections to a closed work order require a successor correction work order under `CORRECTION-LAW-v0.1.md`.

The strongest invalid-waiver rule is:

> **No waiver may hide a change, weaken an enforcement gate, mutate canon silently, or erase failure history. Any waiver that exhibits any of those properties IS NOT A WAIVER — it is an invalid claim, and the validator MUST refuse closure of any work order whose waiver claim exhibits any of those properties. Convention, expediency, operator pressure, narrative justification, and "minor" framing are all insufficient grounds; the only ground for a waiver's legitimacy is the on-disk record meeting every requirement of the waiver record schema with every replay invariant preserved.**

---

## 16. Forbidden Waiver Claims

The following claims are forbidden under the waiver mechanism. No waiver may carry these claims; if a waiver does, the validator MUST refuse closure.

- **Hidden file changes.** A waiver may not authorize a file change that is not recorded in an action log's `files_changed` field. Every file change MUST appear in record before any waiver claim about it is admissible.
- **Unlogged commands.** A waiver may not authorize a command that is not recorded in an action log's `commands_run` field with its exit code. Every command MUST appear in record before any waiver claim about it is admissible.
- **Runtime semantic mutation.** A waiver may not authorize a change to runtime semantics — kernel rules, audit-memory model, refusal-record schema, transition validity, authorization-gate logic. Such changes are governed by `SPEC-EVOLUTION-POLICY-v0.1.md` and require a canon-amendment work order.
- **Validator weakening.** A waiver may not authorize the disabling, softening, stubbing, or removal of any validator rule. Validator rules are added under hardening cycles (`WORKFORCE-HARDENING-v0.2.md`) and only via explicit hardening work orders.
- **Silent canonicalization changes.** A waiver may not authorize a change to the canonicalization function, the canonicalization corpus, the corpus_sha256, or any byte that affects Class A determinism. Such changes are governed by `CROSS-LANGUAGE-CANONICALIZATION-v0.1.md` and `SPEC-EVOLUTION-POLICY-v0.1.md`.
- **Release without gates.** A waiver may not authorize a release whose required gates have not all run and exited 0. Required gates are the release authority; a waiver does not substitute for gate execution.
- **Undefined authority.** A waiver may not be authored by an actor whose authority is not declared in `AUTHORITY-LAW-v0.1.md` or whose identity is empty. Every waiver must carry a non-empty human-owner identity per §5.
- **Hidden persistence.** A waiver may not authorize the persistence of read content (file bytes, hashes, embeddings, summaries, or derived state) beyond the explicit action-log record. Reading a file is not the same as keeping it; the action log is the only sanctioned persistence surface for read content.

### What Waivers Cannot Permit

To restate the above forbidden-claims set in the form required by the work order:

- **Waivers cannot permit hidden file changes.**
- **Waivers cannot permit unlogged commands.**
- **Waivers cannot permit runtime semantic mutation.**
- **Waivers cannot permit validator weakening.**
- **Waivers cannot permit silent canonicalization changes.**
- **Waivers cannot permit release without gates.**
- **Waivers cannot permit undefined authority.**
- **Waivers cannot permit hidden persistence.**

These eight prohibitions are non-negotiable. Each is a class whose violation produces drift, hidden authority, or replay break — exactly the failure modes the protocol exists to refuse. Any "waiver" that purports to permit any of them is not a waiver under this document; it is an attack on protocol legitimacy and the validator MUST refuse closure of any work order containing such a claim.

---

## 17. Long-Term Compatibility

This document is forward-compatible with v0.2 hardening and v0.2 / v0.3 protocol evolution under the following constraints:

- The waiver record schema in §12 specifies optional `original_state_hash` and `post_waiver_state_hash` fields that become required at v0.2 under `AGENT-IDENTITY-v0.1.md`'s key-material specification. v0.1 waivers without those fields remain valid at v0.1 closure-time but MUST be re-anchored at v0.2 transition with the hash fields populated.
- The validator's enforcement of waivers under §14's failure classes is additive; future hardening cycles MAY add new failure classes (e.g., `F-15. Missing original-state hash` becomes active at v0.2). Existing failure classes MUST NOT be removed or weakened.
- The waiver mechanism applies only to v0.1+ work-order records. Pre-v0.1 records (if any) have no waiver class and any reference to them is governed by `SPEC-EVOLUTION-POLICY-v0.1.md`'s migration rules.
- The waiver mechanism is independent of the agent identity layer. Once `AGENT-IDENTITY-v0.1.md` is closed, a waiver MUST be cryptographically attested by the human-owner identity's key. v0.1 waivers carry only an actor string; v0.2 waivers carry a signature.
- The waiver mechanism does not survive the v0.1 → v0.2 → v0.3 transitions trivially. Every protocol-version transition under `SPEC-EVOLUTION-POLICY-v0.1.md` MUST explicitly carry forward, modify, or retire the waiver mechanism. Silent inheritance is forbidden.

The forward-compatibility surface is bounded. Every projected change to the waiver mechanism is named here and is governed by `SPEC-EVOLUTION-POLICY-v0.1.md` for actual amendment.

---

## 18. Non-Goals

This document explicitly does NOT:

- redesign runtime semantics (those are governed by `SPEC.md`, `INTELLAGENT-RUNTIME.md`, `INTELLAGENT.md`),
- redesign validator semantics (those are governed by `WORKFORCE-EXECUTION-RUNTIME-v0.1.md` §8 / §20 / §21 and `WORKFORCE-HARDENING-v0.2.md`),
- redesign workflow semantics (those are governed by `WORKFLOW-GRAMMAR-v0.1.md`),
- redesign authority semantics (those are governed by `AUTHORITY-LAW-v0.1.md`),
- redefine canon (canon is `SPEC.md` and its locked extracts; canon evolution is governed by `SPEC-EVOLUTION-POLICY-v0.1.md`),
- expand the remaining-doc queue identified by `reports/DOC-COMPLETION-AUDIT-v0.1.md` §15 (this document is exactly entry 2 of that bounded queue),
- introduce new primitives, governance layers, or cognition classes,
- alter `WORKFORCE-EXECUTION-RUNTIME-v0.1.md` §21 immutability of work-order content beyond the explicitly-waivable file-scope fields,
- create a precedent for non-file-scope waivers,
- act retroactively on closed work orders (corrections of closed records require successor correction work orders under `CORRECTION-LAW-v0.1.md`),
- weaken any existing protocol guarantee.

The non-goal set is the document's anti-drift surface. Anything outside the named goals is outside the document's scope and MUST NOT be inferred from the document's text.

---

## 19. Final Law

The waiver mechanism is bounded by the following law statements. They are the document's terminal commitments; everything above is implementation of these statements.

**L-1. A waiver is a recorded exception, not an expansion of authority.** Waivers do not enlarge what the system permits; they document, name, and time-stamp the single moment at which the system tolerated a recorded scope deviation under explicit human-owner authority.

**L-2. A waiver applies only to file-scope fields.** `allowed_files` and `forbidden_files` are the only work-order content fields amendable under the waiver mechanism. Every other field remains immutable per `WORKFORCE-EXECUTION-RUNTIME-v0.1.md` §21.

**L-3. A waiver is valid only when human-owner-authored, file-grounded, and within the closure-cycle window.** Waivers authored by agents, by non-human-owner actors, by empty actor strings, before execution, during execution, or after closure are invalid.

**L-4. A waiver preserves replay continuity.** The original deviation, the validator's pre-waiver verdict, the post-waiver verdict, every required gate, the canon, and every prior status_history entry are preserved verbatim across every waiver.

**L-5. A waiver cannot weaken validator legitimacy.** The validator's rules continue to operate at full strength after every waiver. A waiver applies to a single recorded deviation; it does not modify any rule, gate, or enforcement surface.

**L-6. A waiver cannot silently mutate canon.** Canon paths (`SPEC.md`, `vectors/**`, `canonicalization/corpus/**`, locked extracts) are governed exclusively by `SPEC-EVOLUTION-POLICY-v0.1.md`. The waiver mechanism does not extend to canon.

**L-7. A waiver cannot erase failure history.** Prior deviations, prior gates_failed entries, prior status_history entries, prior closure summaries, prior validator outputs are preserved verbatim. Waivers append; they never delete or rewrite.

**L-8. A waiver cannot apply retroactively to a closed record.** Once a work order is in `closed/`, its waivers (if any) are sealed. Subsequent corrections require a successor correction work order under `CORRECTION-LAW-v0.1.md`.

**L-9. The validator MUST refuse closure of any work order whose waiver claim violates L-1 through L-8 or any failure class in §14.** Validator refusal is not narrative; it is mechanical. The validator's verdict is the authority on procedural conformance per `VALIDATION-LAW-v0.1.md`.

**L-10. Convention, expediency, operator pressure, narrative justification, and "minor" framing are insufficient grounds for waiver legitimacy.** The only ground is the on-disk record meeting every requirement of the waiver record schema with every replay invariant preserved.

These ten law statements are the waiver mechanism's normative commitments. They bound the exception class to operational reality; they refuse the failure modes the protocol exists to refuse; and they preserve the file-grounded, replay-continuous, validator-respecting, canon-preserving operational discipline that every other governance instrument in the corpus depends on.

---

**End of WAIVER-MECHANISM v0.1.**
