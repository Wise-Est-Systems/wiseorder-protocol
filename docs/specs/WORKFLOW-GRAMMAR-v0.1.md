# Workflow Grammar v0.1
## Deterministic Operational Flow Rules For Governed Execution

**Status:** v0.1 — normative grammar for governed-execution workflow continuity. Non-overlapping with runtime, governance, validator, release, and input-grammar semantics. This document does not redefine those layers; it constrains the layer that connects them over time.

**Companion documents:** `SPEC.md`, `INPUT-GRAMMAR-v0.1.md`, `CANONICAL-RELEASE-v0.1.md`, `WORKFORCE-EXECUTION-RUNTIME-v0.1.md`, `AGENT-GOVERNANCE-WORKFORCE-v0.1.md`, `ARCHITECTURE-PRESSURE-TESTS-v0.1.md`, `TRANSLATION-LAYER-v0.1.md`, `SPEC-EVOLUTION-POLICY-v0.1.md`.

> **Core thesis.** Governed infrastructure requires governed workflow continuity. Operational legitimacy depends not only on what actions occur, but on how actions transition between stages over time.

---

## 1. Purpose

This document defines the immutable workflow grammar for governed cognition operations within the WiseOrder / Intellagent stack. It standardizes how operations move through the stack from intent → execution → validation → release → historical continuity.

The grammar standardizes:

- operational lifecycle flow,
- stage transitions,
- execution continuity,
- validation sequencing,
- release sequencing,
- closure sequencing,
- replay continuity,
- historical operational reconstruction.

The grammar reduces, at the workflow layer:

- lifecycle drift,
- hidden transitions,
- release inconsistency,
- validation bypass,
- authority confusion,
- operational entropy,
- non-replayable history.

It does not modify runtime behavior, governance authority, validator semantics, release gate definitions, or the input grammar. It constrains the path operations take through those layers.

---

## 2. Why Workflow Grammar Matters

Each layer of the stack is already governed in isolation. Inputs are grammar-checked. The runtime is constrained. The workforce is constrained. The validator is deterministic. Releases are gated. The unguarded surface is the *path between layers over time*.

A correctly governed instruction can still be executed in an ungoverned order. A correctly executed operation can still be released through an unrecorded transition. A correctly validated artifact can still be closed without a reproducible closure state. Each of these failures is invisible to any single layer because no single layer owns the path between them.

Workflow grammar closes this gap by making the lifecycle path itself a governed artifact.

---

## 3. Operational Continuity

Operational continuity is the property that the ordered sequence of an operation's stages, transitions, gates, artifacts, and authorities can be reconstructed in full from the recorded record alone.

Continuity requires:

- **Ordered transitions.** Stage order is fixed; later stages do not precede earlier stages.
- **Recorded gates.** Every required gate appears in the record at the position it executed.
- **Persistent artifacts.** Every required artifact exists at closure and is reachable from the record.
- **Stable authority.** The authority responsible for each transition is named and does not change retroactively.
- **No silent steps.** A step that is not recorded did not occur for the purposes of continuity.

Continuity is the precondition for replay, audit, and release legitimacy. A workflow that lacks continuity has no governed history regardless of how well its individual stages performed.

---

## 4. Replayable Workflow Semantics

A workflow is replayable when, given only its recorded record, an independent reviewer can reconstruct:

1. the originating instruction,
2. the lifecycle states the operation entered, in order,
3. the transitions between those states and the authority for each,
4. the gates that executed at each transition,
5. the artifacts produced, modified, or referenced at each stage,
6. the validation outcomes that admitted each transition,
7. the closure state, including the released or rejected disposition.

Replay does not require the original operator's testimony, the original runtime instance, or any out-of-band knowledge. A workflow whose replay depends on memory, environment, or operator availability is not replayable.

Replayability is binary. Partial replay is non-replay.

---

## 5. Immutable Workflow Principles

The following principles are immutable. They do not depend on operation type, role, or context.

1. **Every stage transition is recorded.** A transition that is not in the record did not occur.
2. **Every required gate executes before the transition it gates.** Gate order is part of the workflow, not a side concern.
3. **Every required artifact exists before the transition that depends on it.** Forward references to non-existent artifacts are invalid.
4. **Every authority transition is explicit.** Authority does not pass implicitly between stages or roles.
5. **Every closure is reproducible.** A closure that cannot be reconstructed from the record is not a closure.
6. **Every release operation is replayable.** A release whose history cannot be reconstructed is invalid regardless of its outcome.
7. **No stage transitions backward.** Lifecycle order is forward-only; corrections occur as new operations, not as state regressions.
8. **No hidden states.** Every state an operation enters is one of the declared states in §§7–12.
9. **Failed gates terminate transition.** A failed gate produces no transition; it produces a rejection or a return for repair.
10. **The record is canonical.** Where the record and any other source disagree, the record is the operational truth.

The strongest of these principles is principle 1: **every stage transition is recorded**. Every other principle depends on the existence of a complete record.

---

## 6. Workflow Lifecycle States

The standard workflow lifecycle has five sequential states and one terminal exception state:

- **draft** — intent captured; instruction grammar-checked; not yet approved.
- **approved** — instruction admitted as a governed work order; execution authorized.
- **executing** — work order is in progress under runtime and workforce governance.
- **reviewed** — execution outputs have been validated against required outputs and validation requirements.
- **closed** — operation is terminal; release, archival, or rejection has been recorded; continuity artifacts are persisted.

Optional terminal state:

- **rejected** — operation terminated without progressing to closure under success semantics; reason is recorded; artifacts produced before rejection are preserved as evidence, not as outputs.

No other states exist. An operation that appears to be in any state not listed here is in an undefined state, which is itself a workflow violation.

---

## 7. Draft State Rules

Draft is the state in which an instruction has been received and grammar-checked but has not yet been admitted as a governed work order.

- The instruction must satisfy the input grammar before draft is entered.
- No execution may occur in draft.
- No artifacts may be released in draft.
- No authority is granted in draft beyond authoring the instruction.
- Draft may exit only to **approved** or **rejected**.
- Draft does not transition to **executing**, **reviewed**, or **closed**.
- Draft entries that remain unresolved are part of the record; abandonment is recorded as rejection, not as deletion.

---

## 8. Approved State Rules

Approved is the state in which an instruction has been admitted as a governed work order and execution is authorized.

- Approval requires explicit authority, not implicit acceptance.
- The approving authority is recorded with the transition.
- Approval does not modify the instruction; modification requires return to draft.
- Approved operations have a defined scope, defined outputs, and defined validation requirements per the input grammar.
- Approved may exit only to **executing** or **rejected**.
- Approved does not transition to **reviewed** or **closed** without passing through executing.

---

## 9. Executing State Rules

Executing is the state in which the approved work order is in progress under runtime and workforce governance.

- Execution stays within the approved scope; scope expansion requires return to draft as a new operation.
- Forbidden actions, as declared in the instruction, do not occur during executing.
- Canon-touch and CANON BREAK conditions, if encountered, route through their dedicated workflows (§§20–21) and do not silently continue.
- Execution does not perform its own validation; validation is the job of the **reviewed** state.
- Executing may exit only to **reviewed** or **rejected**.
- Executing does not transition to **closed** without passing through reviewed.

---

## 10. Reviewed State Rules

Reviewed is the state in which execution outputs have been checked against required outputs and validation requirements.

- Review is performed by an authority distinct from the executing authority (§23).
- Review is deterministic: the same artifacts produce the same pass/fail decision.
- Review does not modify outputs; deficiencies return the operation to draft or rejected, not to executing.
- Review records its decision, the artifacts inspected, and the validation requirements applied.
- Reviewed may exit only to **closed** or **rejected**.
- Reviewed does not loop back to executing under any condition.

---

## 11. Closed State Rules

Closed is the terminal success state in which the operation has been released, archived, or otherwise concluded with all continuity artifacts persisted.

- Closure requires that every required artifact exists and is reachable from the record.
- Closure requires that every required gate has executed and is recorded.
- Closure requires that the authority chain across draft → approved → executing → reviewed → closed is explicit and unbroken.
- Closed operations are not reopened. Subsequent corrections are new operations referencing the closed record.
- Closure is reproducible: a replay of the record reconstructs the closure state.
- A closure that cannot be reproduced from the record is not a closure; it is an unrecorded incident.

---

## 12. Rejected State Rules

Rejected is the terminal exception state in which the operation has been terminated without progressing to closure under success semantics.

- Rejection is reachable from draft, approved, executing, and reviewed.
- Rejection records the state from which it was entered, the reason, and the rejecting authority.
- Artifacts produced before rejection are preserved as evidence of what occurred, not as outputs of a successful operation.
- Rejection does not require the operation to have failed in a technical sense; an operation may be rejected for scope, authority, canon-touch, or governance reasons even when its artifacts pass validation.
- Rejected operations are not reopened. A subsequent attempt is a new operation in draft.

---

## 13. Transition Legitimacy Rules

A transition between lifecycle states is legitimate only when all of the following hold simultaneously:

1. The current state is one of the states permitted to exit to the target state per §§7–12.
2. Every gate required for the transition has executed and recorded a passing outcome.
3. Every artifact referenced as a precondition of the transition exists and is reachable.
4. The authority for the transition is explicit, recorded, and within the scope of its role per the governance layer.
5. The transition does not require modification of any prior recorded state.
6. The transition is recorded at the moment it occurs and not retroactively.

A transition that fails any of these conditions is not a legitimate transition. The operation does not move to the target state. The attempt is recorded as a rejection or as a return for repair, depending on the failure mode.

The strongest expression of transition legitimacy is this: **a workflow transition is operationally legitimate only when its gates, artifacts, authority, and ordering can be independently reconstructed from the record without reference to any party present at the time of the transition.** A transition that depends on operator memory, ambient context, or out-of-band acknowledgment is not legitimate, regardless of whether its outcome is correct.

---

## 14. Validation Sequencing Rules

Validation sequencing governs when and in what order validation occurs across the lifecycle.

- Validation does not occur in draft. Draft uses input-grammar checks, which are not validation.
- Validation does not occur in approved. Approval is an authority operation, not an output check.
- Validation occurs in **reviewed**, against the validation requirements declared at the input grammar layer.
- Validation steps execute in the order declared by the operation; reordering validation is a workflow violation.
- Validation does not run partially. A validation step that does not complete is a failure, not a deferral.
- Validation outcomes admit transitions out of reviewed; they do not loop back into executing.

---

## 15. Release Sequencing Rules

Release sequencing governs the order in which release-related gates and artifacts are executed and produced.

- Release gates do not execute before the operation reaches reviewed with a passing outcome.
- Release artifacts are produced in the order declared by the release semantics; the workflow grammar does not redefine that order, it preserves it.
- Release operations that touch canon must satisfy canon-touch workflow rules (§20) prior to release-gate execution.
- A release that occurs without the full set of preceding gates and artifacts is a workflow violation, even if the released artifact is otherwise valid.
- The release transition is part of closure; release cannot be observed in any state other than reviewed → closed.

---

## 16. Closure Sequencing Rules

Closure sequencing governs the final ordering of artifact persistence, record finalization, and release-tag application.

- Closure begins only after reviewed has produced a passing outcome and all release-sequencing requirements have been satisfied.
- Required artifacts are persisted before the record is finalized.
- The record is finalized before any release tag is applied.
- A release tag is applied only to a finalized record.
- Closure ends with a state in which a replay of the record reconstructs every preceding step in order.
- Out-of-order closure is a workflow violation regardless of whether the final state appears correct.

---

## 17. Action-Log Continuity Rules

The action log is the ordered, append-only record of stage entries, transitions, gate executions, artifact references, and authority assignments for an operation.

- Every state entry is logged.
- Every transition is logged with its origin state, target state, gates executed, and authority.
- Every gate execution is logged with its outcome.
- Every artifact reference is logged at the stage in which the artifact was produced or modified.
- Logs are append-only; corrections are new entries that reference the prior entry, not edits of the prior entry.
- A gap in the action log is a continuity failure regardless of the apparent correctness of the surrounding entries.

---

## 18. Self-Verification Continuity Rules

Self-verification continuity is the property that the workflow record contains, at closure, sufficient evidence to verify itself without dependence on the producing system.

- The record contains the instruction, the lifecycle path, the gates executed, the artifacts produced, the validation outcomes, and the authority chain.
- The record can be verified by an external reviewer using only the record and the public protocol documents.
- Self-verification does not depend on system uptime, operator availability, or live runtime state.
- A record that requires the producing system to be present in order to be verified does not satisfy self-verification continuity.

---

## 19. Gate-Execution Rules

Gates are deterministic checks executed at defined points in the lifecycle. The workflow grammar does not define what gates exist; it defines how their execution is sequenced and recorded.

- A gate is either passing, failing, or not-yet-executed; no other states are recognized.
- Gates execute at the transition they govern, not before and not after.
- A skipped gate is a failed gate for workflow purposes.
- Gate execution is recorded in the action log with its outcome and the artifacts it inspected.
- A gate that depends on a missing artifact records a failure, not a deferral.
- Gate order is part of the workflow; gates do not commute unless explicitly declared as order-independent in their defining document.

---

## 20. Canon-Touch Workflow Rules

A canon touch is any operation that modifies normative documents. The workflow grammar preserves the existing definition of canon touch and constrains how such operations move through the lifecycle.

- A canon touch must be declared at the input grammar layer; an undeclared canon touch is rejected.
- A canon-touch operation cannot transition out of approved into executing without recording the canon-touch declaration in the action log.
- A canon-touch operation requires reviewer authority distinct from the author for the reviewed transition.
- A canon-touch release does not occur without explicit human approval as defined by the governance layer.
- A canon touch that is discovered during executing terminates execution and rejects the operation; the modification is repackaged as a new draft with explicit canon-touch declaration.

---

## 21. CANON BREAK Workflow Rules

A CANON BREAK is a canon modification that alters or removes normative meaning. The workflow grammar preserves the existing definition of CANON BREAK and constrains its lifecycle treatment.

- CANON BREAK is declared at the input grammar layer; an undeclared CANON BREAK is rejected.
- CANON BREAK cannot move from draft to approved without explicit human approval as defined by the governance layer.
- CANON BREAK cannot share an operation with non-CANON-BREAK changes; compound operations are rejected.
- CANON BREAK release sequencing follows the canon-release semantics defined in `CANONICAL-RELEASE-v0.1.md`; the workflow grammar does not redefine those semantics, it preserves their ordering.
- A CANON BREAK discovered during executing terminates execution and rejects the operation regardless of partial output validity.

---

## 22. Human-Approval Workflow Rules

Human approval is required at the transitions defined by the governance layer. The workflow grammar does not redefine which transitions require human approval; it constrains how such approvals are recorded.

- Human approval is recorded with the approving identity, the transition it admits, and the time of approval.
- Approval does not transfer between operations; an approval applies only to the operation it names.
- Approval does not transfer between transitions within an operation; each gated transition records its own approval.
- An approval that cannot be reconstructed from the record from a named identity to a named transition is treated as absent.
- Implicit, ambient, or assumed approval is not approval.

---

## 23. Reviewer Separation Rules

Reviewer separation is the rule that the authority that reviews an operation is distinct from the authority that executed it.

- The author of an operation does not perform its review.
- The executor of an operation does not perform its review.
- Where a single party holds both authoring and reviewing roles in the larger system, the workflow grammar requires that the review act be recorded under the reviewer role, with explicit separation of artifacts under inspection from artifacts under authorship.
- Combined-role reviews that cannot be separated in the record are rejected for the reviewed transition.
- Reviewer separation does not depend on the apparent quality of the artifacts; quality does not substitute for separation.

---

## 24. Runtime Modification Workflow Rules

Runtime modifications are operations that change runtime behavior, configuration, or governance. The workflow grammar preserves the existing runtime semantics and constrains how runtime-modifying operations move through the lifecycle.

- Runtime modifications declare themselves at the input grammar layer.
- Runtime-modifying operations record the affected runtime surface in the action log at executing entry.
- Runtime-modifying operations do not close without producing the artifacts required to replay the modification.
- A runtime modification whose closure cannot be replayed without the original operator's testimony is a workflow violation regardless of its technical correctness.
- Rollback of a runtime modification is itself a new operation in draft, not a regression of the original operation's state.

---

## 25. Release-Tag Workflow Rules

Release tags are markers applied to finalized records to identify a release. The workflow grammar preserves the existing release semantics and constrains the application of release tags.

- A release tag is applied only at the closed state.
- A release tag is applied only to a finalized action log.
- A release tag does not modify any prior log entry; it appends to the record.
- A release tag is recorded with the operation it tags, the artifacts it covers, and the authority that applied it.
- Tags applied out of order, applied before closure, or applied without an authority record are workflow violations.

---

## 26. Historical Reconstruction Rules

Historical reconstruction is the property that any past operation can be replayed in full from its record, regardless of how much time has passed since closure.

- Historical reconstruction depends only on the recorded artifacts and the public protocol documents at the version under which the operation closed.
- Historical reconstruction does not depend on current system state, current canon version, or current operator availability.
- A reconstruction that requires reinterpretation of past records under current semantics is not reconstruction; it is reinterpretation, and is a continuity violation.
- Past records are read under the protocol version they recorded against. Version drift is handled at the protocol-evolution layer (`SPEC-EVOLUTION-POLICY-v0.1.md`), not by re-writing past records.

---

## 27. Long-Term Compatibility Rules

Long-term compatibility is the property that the workflow grammar continues to admit reconstruction of operations recorded under earlier versions of itself.

- The set of lifecycle states defined in §6 may not be reduced in any future version. New states may be added in non-overlapping positions when accompanied by a governed protocol-evolution decision.
- The transition legitimacy rules (§13) may not be weakened. They may be strengthened by adding new conditions when accompanied by a governed protocol-evolution decision.
- The action-log continuity rules (§17) may not be weakened. Logs that were complete under a prior version remain complete under any later version.
- A future version that cannot replay a past compliant record is not a successor of this grammar; it is a different grammar.

---

## 28. What Must Never Change

The following elements of this grammar do not change across versions:

- The five-state lifecycle (draft, approved, executing, reviewed, closed) plus the rejected exception state.
- The forward-only ordering of state transitions.
- The append-only character of the action log.
- The requirement that every transition be recorded.
- The requirement that every gate execute at the transition it governs.
- The requirement that closure be reproducible from the record alone.
- The requirement that release tags apply only at closure to a finalized record.
- The requirement that reviewer authority be distinct from authoring and executing authority.

These are the load-bearing surfaces of the workflow grammar. Changing them changes what governance means at the workflow layer.

---

## 29. What May Evolve

The following elements may evolve under the protocol-evolution layer without breaking compatibility:

- The set of gates that execute at a given transition, provided their order and recording requirements are preserved.
- The naming of authority roles, provided role separation is preserved.
- The format of action-log entries, provided the existing fields remain reconstructible.
- The set of artifact types produced at a given stage, provided required artifacts are not removed.
- The expansion of canon-touch and CANON BREAK declarations to cover additional surfaces, provided existing surfaces are not removed.

Evolution that touches §28 is not evolution. It is replacement, and is governed by `SPEC-EVOLUTION-POLICY-v0.1.md`.

---

## 30. Final Law

A workflow is operationally valid if and only if:

- every stage transition is recorded,
- every required gate executes at the transition it governs,
- every required artifact exists at the transition that depends on it,
- every authority transition is explicit and recorded,
- every closure is reproducible from the record alone,
- every release operation is replayable without operator testimony.

A workflow that satisfies these conditions is operationally legitimate. A workflow that violates any one of them is not partially legitimate; it is not legitimate.

---

## What Makes A Workflow Unsafe?

A workflow is unsafe when any of the following are present:

- hidden lifecycle transitions not represented in the record,
- skipped validation at the reviewed state,
- release without execution of required gates,
- canon touch without explicit declaration,
- closure without replayability,
- ambiguous or unrecorded approval authority,
- inconsistent or interrupted action logs,
- orphaned artifacts not reachable from the record,
- backward state transitions used in place of corrective new operations,
- runtime modifications whose replay depends on operator testimony,
- release-tag application before closure or to an unfinalized record,
- combined-role reviews where reviewer and executor cannot be separated in the record.

Unsafety at the workflow layer is not a quality problem; it is a continuity problem. A workflow that is unsafe cannot be made safe by improving the artifacts it produced. It can only be reissued as a new operation.

---

## What Makes A Workflow Operationally Legitimate?

A workflow is operationally legitimate when all of the following are present:

- replayable transitions reconstructible from the record alone,
- deterministic validation against declared requirements,
- explicit authority recorded at every transition,
- ordered gate execution at the transitions they govern,
- complete artifact continuity from production through closure,
- reproducible closure state derivable from the record,
- audit-preserving execution that does not depend on live system state,
- distinct reviewer authority separate from authoring and executing authority,
- declared canon-touch and CANON BREAK operations where canon is modified,
- self-verifying records that can be checked against the public protocol documents.

Legitimacy is the conjunction of these properties. Partial legitimacy is illegitimacy.

---

## What Workflow States Must Reject Transition?

The following transitions are rejected without exception:

- draft → closed,
- draft → executing,
- draft → reviewed,
- approved → reviewed without passing through executing,
- approved → closed without passing through executing and reviewed,
- executing → closed without passing through reviewed,
- executing → released without validation in reviewed,
- reviewed → executing,
- closed → any state,
- canon-touch → release without recorded canon-touch declaration,
- canon-touch → release without explicit human approval where required by governance,
- runtime modification → closure without artifacts sufficient for replay,
- failed gate → admitted transition,
- compound operation containing CANON BREAK with non-CANON-BREAK changes,
- backward transitions of any kind.

These are not enforcement preferences. They are grammar.

---

## What Happens Without Workflow Governance?

Without governance at the workflow layer, the following degradations occur regardless of the quality of individual stages:

- operational drift across releases as transitions become inconsistent,
- unreplayable releases that depend on operator memory or live state,
- unverifiable approval chains where authority cannot be reconstructed,
- release inconsistency where the same instruction produces different lifecycle paths on different runs,
- historical corruption as past records lose continuity with current semantics,
- governance erosion at lower layers as their gates measure operations that did not pass through the expected path,
- audit collapse as records cease to be self-verifying.

These failures are not visible at the runtime, validator, or release layer in isolation. They are visible only across operations and across time. The workflow grammar exists because that surface is otherwise unguarded.

---

## Closing Statement

Workflow grammar exists to preserve deterministic operational continuity across long-term infrastructure evolution. Inputs may be governed, runtimes may be governed, validators may be governed, and releases may be governed; without governed continuity between them, the system has well-formed pieces and an ungoverned history. The workflow grammar is the layer at which the history itself becomes a governed artifact.
