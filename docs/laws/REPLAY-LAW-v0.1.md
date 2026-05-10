# Replay Law v0.1
## Deterministic Reconstruction Rules For Governed Infrastructure

**Status:** v0.1 — normative reconstruction surface for governed execution. Non-overlapping with runtime, governance, workflow, validator, and forbidden-surface semantics. This document does not redefine those layers; it defines what it takes for an operation recorded under those layers to be reconstructable from its record.

**Companion documents:** `SPEC.md`, `INPUT-GRAMMAR-v0.1.md`, `WORKFLOW-GRAMMAR-v0.1.md`, `FORBIDDEN-SURFACES-v0.1.md`, `CANONICAL-RELEASE-v0.1.md`, `CROSS-LANGUAGE-CANONICALIZATION-v0.1.md`, `WORKFORCE-EXECUTION-RUNTIME-v0.1.md`, `AGENT-GOVERNANCE-WORKFORCE-v0.1.md`, `ARCHITECTURE-PRESSURE-TESTS-v0.1.md`, `SPEC-EVOLUTION-POLICY-v0.1.md`.

> **Core thesis.** A governed system that cannot replay its operational history cannot prove operational legitimacy. Replayability is the foundation of auditability, correction, and long-term trust accumulation.

---

## 1. Purpose

This document defines the immutable replay law governing reconstructability, reproducibility, and operational legitimacy across the governed cognition stack. It standardizes:

- replay semantics,
- replay legitimacy,
- replay boundaries,
- replay failure conditions,
- replay-compatible artifacts,
- replay-compatible workflows,
- replay-compatible releases,
- replay-compatible governance,
- replay-compatible historical continuity.

The replay law reduces, at the reconstruction layer:

- testimonial dependency,
- replay drift,
- silent canonicalization change,
- unverifiable correction claims,
- non-reproducible release evidence,
- ambiguous version compatibility,
- audit decay over time.

It does not modify runtime behavior, governance authority, workflow lifecycle, validator enforcement, or the forbidden-surface model. It defines the conditions under which an operation recorded against those layers can be reconstructed from its record alone.

---

## 2. Why Replay Matters

Each governed layer constrains what can be observed at the moment of execution. The runtime constrains runtime behavior. Governance constrains authority. The workflow constrains transitions. The validator constrains output checks. The forbidden-surface model constrains non-authority. All of these enforce in the present tense.

The unguarded surface is the past tense.

An operation that was governed at the time it occurred but cannot be reconstructed afterwards is, for audit purposes, indistinguishable from an operation that was not governed. Replay law closes this gap by making reconstruction itself a governed property of the record. A record either replays or it does not. There is no third state.

---

## 3. Replay As Operational Legitimacy

Operational legitimacy is the property that an operation's authority, gates, artifacts, and outcomes can be checked by an independent reviewer. In the present tense, legitimacy is established by direct observation. In the past tense, legitimacy is established by replay.

Replay is therefore not a debugging convenience. It is the mechanism by which an operation's legitimacy survives the moment of its execution. An operation that was legitimate at the moment it occurred but whose legitimacy cannot be reconstructed has, by the rules of this document, no legitimacy at audit time. Legitimacy that does not replay does not persist.

---

## 4. Replay As Infrastructure

Replay is infrastructure, not a report. The replay path is part of the governed system in the same way that storage, transport, and execution are part of it. The artifacts, schemas, and procedures that produce a replayable record are governed surfaces (`FORBIDDEN-SURFACES-v0.1.md` §§17–19) and are subject to the same declared-authority requirements as any other governed surface.

A change that breaks replay is not a runtime change, a documentation change, or a tooling change. It is a change to the load-bearing surface that allows the system to be audited. Replay drift is treated, throughout this document, with the same priority as canon drift.

---

## 5. Immutable Replay Principles

The following principles are immutable. They do not depend on operation type, role, or context.

1. **The same declared inputs reproduce the same governed result.** Determinism is the precondition of replay.
2. **Validation produces the same outcome on replay as it produced at execution.** Validators do not drift across replay.
3. **The operational chain reconstructs from the record alone.** Replay does not depend on operator testimony.
4. **Authority transitions remain reproducible.** The chain from author to reviewer to releaser is reconstructable from named identities and recorded transitions.
5. **Release legitimacy remains reconstructible.** A released operation produces the same closure state on replay.
6. **Replay failure is surfaced explicitly.** A replay that does not reconstruct produces a named failure, not a silent success.
7. **Replay does not reinterpret past records under current canon.** Past records are read under the protocol version they recorded against.
8. **Replay is binary.** Partial replay is not replay.
9. **Replay does not depend on live system state.** Reconstruction is performed against the record.
10. **Replay does not depend on operator availability.** A record whose replay requires the original operator to be present is not replayable.

The strongest of these principles is principle 3: **the operational chain reconstructs from the record alone**. Every other principle depends on it. A record that requires anything beyond itself and the public protocol documents is not the canonical record; it is a partial record.

---

## 6. Replayable Intent Requirements

The originating intent of an operation must be reconstructable from the record. Replayable intent requires:

- the original instruction text or its canonicalized equivalent,
- the input grammar declarations the instruction satisfied (scope, constraints, forbidden actions, required outputs, validation requirements, role),
- declared canon-touch or CANON BREAK status, where applicable,
- declared waivers against forbidden surfaces, where applicable,
- the timestamp at which the instruction was admitted to draft.

An operation whose intent cannot be reconstructed is not replayable regardless of how its execution proceeded. Intent is the first record; without it, every subsequent record is anchored to nothing.

---

## 7. Replayable Workflow Requirements

The workflow path of an operation must be reconstructable from the record. The workflow grammar (`WORKFLOW-GRAMMAR-v0.1.md`) defines the lifecycle states, transitions, and gates. Replay law adds:

- every state entry is reconstructable in order,
- every transition is reconstructable with its origin state, target state, gates executed, and authority,
- every gate execution is reconstructable with its outcome and the artifacts it inspected,
- every state-entry timestamp is preserved,
- the lifecycle path is reconstructable without inference of intermediate states.

A workflow whose path cannot be reconstructed is not replayable, regardless of whether its terminal state is correct.

---

## 8. Replayable Validation Requirements

Validation outcomes must be reconstructable from the record. The validator semantics are preserved by this document, not redefined. Replay law adds:

- the validation requirements applied are recorded,
- the artifacts inspected by the validator are recorded and reachable,
- the validator's outcome is recorded with the requirements it satisfied or failed,
- the validator version, configuration, and canonicalization rules in effect at execution are recorded,
- a replay of the same artifacts under the recorded validator state produces the same outcome.

A validation outcome that cannot be reproduced under its recorded state is a replay-drift event and is recorded as a failure under §16.

---

## 9. Replayable Release Requirements

Release legitimacy must be reconstructable from the record. The release semantics are preserved by `CANONICAL-RELEASE-v0.1.md`. Replay law adds:

- every release gate executed is recorded with its outcome,
- every release artifact is recorded and reachable,
- the order of release-gate execution is preserved,
- the release tag and the record it covers are recorded together,
- the release-status registry entry for the release is reachable from the record,
- a replay of the recorded gates against the recorded artifacts reproduces the recorded release outcome.

A release that cannot be reconstructed in this form is not a replayable release regardless of whether the released artifact is in production.

---

## 10. Replayable Governance Requirements

Governance acts must be reconstructable from the record. The governance layer is preserved by `AGENT-GOVERNANCE-WORKFORCE-v0.1.md` and the human-approval rules referenced throughout. Replay law adds:

- every approval is reconstructable from a named identity to a named operation, transition, and surface,
- every authority transition is reconstructable in order,
- every governance-required gate is reconstructable with its outcome,
- every CANON BREAK approval is reconstructable with its declared surface set,
- every forbidden-surface waiver is reconstructable per `FORBIDDEN-SURFACES-v0.1.md` §22.

Governance whose acts are not reconstructable is, at audit time, indistinguishable from ungoverned operation.

---

## 11. Replay-Compatible Artifact Rules

Artifacts referenced in the record must satisfy the following:

- they exist at a stable identity reachable from the record,
- they are immutable after the stage in which they were produced,
- their content hashes (or equivalent identity) are recorded,
- their canonicalization rules at the time of production are recorded,
- they do not depend on platform-specific representations not declared in their canonicalization rules.

An artifact that cannot be located, has been mutated, or whose canonicalization rules at production are not recoverable is not replay-compatible. Operations whose record depends on such an artifact are not replayable.

---

## 12. Replay-Compatible Record Rules

The record itself must satisfy the following:

- it is append-only,
- it is self-describing under the protocol version against which it was written,
- its fields are reconstructable without reference to live system state,
- it does not contain fields whose meaning depends on operator memory,
- it does not contain references to identifiers that cannot be resolved against a stable namespace recorded in the record itself or in the public protocol documents.

A record that is not append-only, not self-describing, or contains operator-dependent fields is not a replay-compatible record. Such a record may have been useful at execution time and remains useless at audit time.

---

## 13. Replay-Compatible Closure Rules

Closure must be reconstructable from the record. Replay law preserves the closure rules in `WORKFLOW-GRAMMAR-v0.1.md` §§11, 16 and adds:

- closure timestamps are recorded,
- the artifact set at closure is enumerated and reachable,
- the authority chain to closure is reconstructable end to end,
- the release-tag application (if any) is recorded with its authority and timestamp,
- a replay of the record produces a closure state matching the recorded closure state by every reconstructable property.

A closure whose state diverges between original execution and replay is, by the rules of this document, not a closure. It is an unrecorded incident at the closure boundary.

---

## 14. Replay-Compatible Gate Rules

Gates must be reconstructable individually and in their original order. Replay law preserves the gate semantics in `WORKFLOW-GRAMMAR-v0.1.md` §19 and adds:

- every gate's recorded inputs are reachable,
- every gate's recorded outcome is preserved,
- every gate's executor (the runtime, validator, or governance authority that ran it) is recorded,
- gates that depend on canonicalization record the canonicalization rules in effect,
- a replay of the recorded inputs through the recorded gate produces the recorded outcome.

A gate whose replay produces a different outcome than the recorded outcome is a replay-drift event and is recorded under §16.

---

## 15. Replay-Compatible Approval Rules

Approvals must be reconstructable from named identity to named scope. Replay law preserves the approval rules in `WORKFLOW-GRAMMAR-v0.1.md` §22 and `FORBIDDEN-SURFACES-v0.1.md` §23 and adds:

- the identity issuing the approval is recorded under a stable namespace,
- the operation, transition, and surface authorized by the approval are recorded,
- the approval timestamp is recorded,
- approvals are recorded at the moment they are issued and not retroactively backfilled,
- approvals do not transfer between operations, transitions, or surfaces under replay any more than under live execution.

An approval whose chain from identity to scope cannot be reconstructed is, on replay, treated as absent regardless of whether it was honored at execution time.

---

## 16. Replay Failure Classes

The following failure classes are recognized by replay law:

- **RP-1 Hidden Input.** An input that affected execution but is not recorded.
- **RP-2 Missing Artifact.** An artifact referenced in the record cannot be located or has been mutated.
- **RP-3 Validation Drift.** Validation produces a different outcome on replay than at execution under the recorded validator state.
- **RP-4 Canonicalization Drift.** Canonicalization produces a different output on replay than at execution under the recorded rules.
- **RP-5 Authority Reconstruction Failure.** The authority chain cannot be reconstructed end to end from named identities and recorded transitions.
- **RP-6 Workflow Reconstruction Failure.** The lifecycle path cannot be reconstructed in order from the record alone.
- **RP-7 Release Reconstruction Failure.** The release gates, artifacts, or tag application cannot be reconstructed under their recorded order.
- **RP-8 Cross-Version Divergence.** Replay under the recorded protocol version produces a different outcome than expected by the record itself.
- **RP-9 Cross-Language Divergence.** Replay under a conformant alternative implementation produces a different canonicalized outcome than the original.
- **RP-10 Non-Deterministic Output.** Repeated replay under identical recorded inputs produces different outcomes.

Each failure class is recorded by name and number when detected. Failure classes do not collapse into a single bucket; their remediations differ.

---

## 17. Replay Drift

Replay drift is any divergence between the recorded outcome of an operation and the outcome produced by replay of that operation against the public protocol documents and recorded artifacts.

- Drift is detected, named under §16, and recorded.
- Drift is not silenced by adjustment of the replay procedure to match the original outcome.
- Drift is not silenced by adjustment of the recorded outcome to match the replay procedure.
- Drift is investigated as a forbidden-surface candidate under `FORBIDDEN-SURFACES-v0.1.md` §§16–19.
- Drift discovered in past records does not retroactively invalidate other operations whose own records still replay; it invalidates the operation whose record drifted.

Replay failure is not hidden corruption. **Replay failure is surfaced divergence**: a named, recorded, investigable event, not a silent state.

---

## 18. Replay Boundary Conditions

Replay is bounded by what the record contains. Outside the record, replay law makes no claims.

- Replay does not reconstruct events that did not occur within the recorded operation.
- Replay does not reconstruct system-level context that was not recorded.
- Replay does not reconstruct operator state of mind, intent, or judgment that exceeds what the input grammar required to be recorded.
- Replay does not produce truth claims; it produces reconstruction outcomes.
- Replay does not reach across operation boundaries unless the operations declare cross-references that satisfy the record rules of §12.

A replay claim that exceeds these boundaries is unsupported under §24.

---

## 19. Replay Time-Boundaries

Replay is time-bounded by the protocol version under which the record was written.

- A record written under v0.X replays under v0.X regardless of the current protocol version.
- A replay procedure that reads v0.X records under v0.Y semantics is reinterpretation, not replay.
- Records do not silently upgrade. Reinterpretation across versions is governed by `SPEC-EVOLUTION-POLICY-v0.1.md`, not by replay law.
- A record older than the earliest replay-compatible protocol version is not replayable; it is historical and is treated as evidence rather than as a reconstructable operation.

Time-boundary violations are recorded as RP-8 under §16.

---

## 20. Replay Across Versions

Replay across protocol versions is admissible only when the protocol-evolution layer declares the cross-version path replayable.

- A v0.X record replayed under v0.Y produces a result equivalent to its v0.X replay only if the protocol-evolution decision admitting v0.Y declares this equivalence.
- Cross-version replay without such a declaration is reinterpretation and is not replay.
- A claim of cross-version replay that is not backed by a protocol-evolution declaration is unsupported under §24.

Replay law does not authorize cross-version replay. It defines the conditions under which the protocol-evolution layer's cross-version replay declarations are honored.

---

## 21. Replay Across Machines

Replay across machines is admissible only when the recorded canonicalization rules and validator state are sufficient to produce identical outcomes on the alternative machine.

- Machine-dependent state that is not recorded is a Hidden Input under RP-1.
- Locale, timezone, filesystem case-folding, and floating-point ordering are machine surfaces; canonicalization rules either neutralize them or record their state.
- A machine-dependent outcome that was not declared as such at execution time is a Non-Deterministic Output under RP-10.
- A claim of machine-portable replay that is not backed by canonicalization evidence is unsupported under §24.

---

## 22. Replay Across Implementations

Replay across implementations is admissible only when the alternative implementation has demonstrated conformance against the conformance vectors declared by `SPEC.md` and `vectors/`.

- An implementation without recorded conformance against the relevant vectors is not a replay-compatible implementation.
- A replay outcome from a non-conformant implementation is evidence of that implementation, not of the original record.
- Cross-implementation replay outcomes that diverge are recorded as RP-9.
- A claim of cross-implementation replay that is not backed by published conformance is unsupported under §24.

---

## 23. Replay Across Languages

Replay across languages is admissible only when cross-language canonicalization equivalence has been demonstrated under `CROSS-LANGUAGE-CANONICALIZATION-v0.1.md`.

- Canonicalization paths that differ across languages without a declared equivalence are non-replay-compatible.
- A language-specific replay outcome that diverges from the canonicalized outcome is recorded as RP-9.
- A claim of cross-language replay that is not backed by published cross-language canonicalization evidence is unsupported under §24.

Replay law does not redefine cross-language canonicalization. It defers to the canonicalization document and treats absence of declared equivalence as a non-replay-compatible boundary.

---

## 24. Replay Compatibility vs Replay Claims

Replay compatibility is a property of the record. Replay claims are statements made about a record. The two are distinct.

- A record may be replay-compatible and have no claims made about it.
- A claim of replay must be backed by evidence in the record under the rules of this document.
- Claims that exceed what the record supports are unsupported, regardless of whether the claim happens to be true.
- Unsupported replay claims fall under the forbidden documentation and outreach claims rules in `FORBIDDEN-SURFACES-v0.1.md` §§20–21.

A replay claim is supported only when the reconstruction it asserts can be performed by an independent reviewer against the record and the public protocol documents.

---

## 25. Replay Refusal Conditions

A governed replay procedure refuses to produce an outcome under the following conditions:

- the record is incomplete with respect to §§6–15,
- a referenced artifact is missing or has been mutated,
- canonicalization rules at the time of execution cannot be reconstructed,
- the protocol version under which the record was written is unknown to the replay procedure,
- the record contains fields the replay procedure cannot interpret,
- the record references operator testimony as a precondition.

A replay procedure that does not refuse under these conditions is not a governed replay procedure. It is producing outcomes against incomplete inputs.

---

## 26. Replay Invalidation Rules

A record is invalidated as replayable when:

- its referenced artifacts have been mutated,
- its canonicalization rules have been retroactively changed under its recorded protocol version,
- its action log has been edited rather than appended to,
- its validator state has been retroactively changed under its recorded protocol version,
- its authority chain has been retroactively modified.

Invalidation is recorded. An invalidated record is not deleted; it is marked as no longer replay-compatible, with the invalidating event named.

Invalidation does not propagate by association. Operations whose own records still replay remain replay-compatible. Replay invalidation is per-record, not per-domain.

---

## 27. Long-Term Replay Continuity

Long-term replay continuity is the property that a record written under any released version of the replay law continues to be replay-compatible under that same version, regardless of how much time has passed.

- The replay-compatibility of a record is determined by the version under which it was written, not by the current version.
- Successor versions of replay law preserve replay-compatibility for records written under their predecessors.
- A successor version that admits records its predecessor invalidated, or invalidates records its predecessor admitted, is not a successor; it is a different replay law.

Replay continuity over time is the mechanism by which operational legitimacy survives long enough to compound into trust.

---

## 28. What Must Never Change

The following elements of replay law do not change across versions:

- the binary character of replay (replays or does not),
- the requirement that replay reconstruct from the record alone,
- the requirement that replay not depend on operator testimony,
- the requirement that replay not depend on live system state,
- the requirement that replay outcomes be deterministic under recorded inputs,
- the requirement that replay failure be surfaced rather than silenced,
- the requirement that replay not reinterpret past records under current canon,
- the failure-class enumeration in §16 (additions are admissible; reductions are not),
- the refusal conditions in §25 (additions are admissible; reductions are not).

These are the load-bearing surfaces of replay law. Changing them changes what reconstruction means.

---

## 29. What May Evolve

The following elements may evolve under the protocol-evolution layer without breaking replay continuity:

- the addition of new failure classes under §16,
- the addition of new refusal conditions under §25,
- the format of replay-compatible records, provided existing fields remain reconstructible,
- the canonicalization rules referenced by replay procedures, provided cross-version equivalence is declared,
- the conformance-vector set used to admit replay-compatible implementations,
- the procedures by which replay drift is investigated, provided drift continues to be surfaced.

Evolution that touches §28 is not evolution. It is replacement, governed by `SPEC-EVOLUTION-POLICY-v0.1.md`.

---

## 30. Final Law

A replay is operationally legitimate if and only if:

- the same declared inputs reproduce the same governed result,
- validation produces the same outcome on replay as at execution,
- the operational chain reconstructs from the record alone,
- authority transitions remain reproducible,
- release legitimacy remains reconstructible,
- replay failure, where it occurs, is surfaced explicitly.

A replay that satisfies these conditions is legitimate. A replay that violates any one of them is not partially legitimate; it is not legitimate.

A system that requires operator memory to reconstruct legitimacy is not replayable. A system whose records do not reconstruct from the record alone has no governed history regardless of how much governance was applied at execution time. **Replay law exists to convert operational history from testimony into reconstructable evidence.** Where evidence is reconstructable, governance persists across time. Where it is not, governance ends at the moment execution ends.

---

## What Makes A Replay Invalid?

A replay is invalid when any of the following are present:

- hidden inputs that affected execution but are not in the record,
- undeclared dependencies whose state at execution cannot be reconstructed,
- missing artifacts referenced by the record,
- missing validation state for any recorded validation step,
- missing gate outputs for any recorded gate,
- hidden operator decisions that influenced outcomes without being recorded,
- unreconstructable authority transitions,
- canonicalization drift between execution and replay,
- replay-version ambiguity where the protocol version of the record is unclear,
- references that cannot be resolved against a stable namespace,
- mutated artifacts whose recorded identity no longer matches their content,
- non-deterministic outputs under identical recorded inputs.

Invalid replay is not a partial outcome. It is a named failure class under §16 and is recorded.

---

## What Makes A Replay Claim Unsupported?

A replay claim is unsupported when:

- replay is claimed without artifacts sufficient for reconstruction,
- replay is claimed across languages without published cross-language canonicalization equivalence,
- replay is claimed across machines without canonicalization evidence sufficient to neutralize machine-dependent state,
- replay is claimed across versions without a protocol-evolution declaration admitting cross-version replay,
- replay is claimed without reproducible validation outputs,
- replay is claimed for a record whose action log has been edited rather than appended to,
- replay is claimed for an operation whose record references operator testimony as a precondition,
- replay is claimed against a non-conformant implementation,
- replay is claimed against canonicalization rules that have been retroactively changed.

Unsupported replay claims are forbidden under `FORBIDDEN-SURFACES-v0.1.md` §§20–21. The truth value of the claim does not relax the requirement.

---

## What Must Always Replay?

The following must always replay from the record alone, under the protocol version against which the record was written:

- gate outcomes,
- validator results,
- release legitimacy,
- closure legitimacy,
- workflow transitions,
- action-log continuity,
- approval-chain continuity,
- canonicalization outputs,
- forbidden-surface waivers, where declared,
- canon-touch and CANON BREAK declarations and approvals, where declared,
- runtime-modification artifacts sufficient for replay, per `WORKFLOW-GRAMMAR-v0.1.md` §24.

If any of these does not replay, the operation has no replay-legitimate history at the level on which it failed, even if other levels still reconstruct.

---

## What Happens Without Replay Law?

Without governance at the replay layer, the following degradations occur regardless of how well execution was governed in the moment:

- audit collapse as past records cease to be reconstructable,
- unverifiable releases whose legitimacy cannot be checked after the fact,
- non-reconstructable governance whose authority chains cannot be retraced,
- hidden operational drift visible only across long timescales,
- unverifiable correction claims because the operations being corrected cannot be reconstructed,
- release ambiguity where the same release tag covers different reconstructable histories,
- institutional memory loss as operator turnover removes the testimony on which non-replayable records depended,
- forbidden-surface drift that was waivable in the moment but not auditable in retrospect,
- canon drift that was declared at the time but unverifiable later.

These failures are invisible at the moment of execution. They are visible only at audit. Replay law exists because that surface is otherwise unguarded.

---

## Closing Statement

Replay law converts operational history from testimony into reconstructable evidence. A governed system that records its operations under runtime, governance, workflow, validator, and forbidden-surface semantics still depends on a single property to remain legitimate over time: that those records, alone, reconstruct what occurred. Where reconstruction is possible, governance compounds across time into auditable trust. Where it is not, governance ends when execution ends, and what remains is artifact without evidence.
