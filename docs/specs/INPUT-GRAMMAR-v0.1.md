# Input Grammar v0.1
## Deterministic Human-To-Execution Translation Rules

**Status:** v0.1 — normative grammar for governed-execution input. Non-overlapping with runtime, governance, workforce, and release semantics. This document does not redefine those layers; it constrains the layer above them.

**Companion documents:** `SPEC.md`, `CANONICAL-RELEASE-v0.1.md`, `WORKFORCE-EXECUTION-RUNTIME-v0.1.md`, `AGENT-GOVERNANCE-WORKFORCE-v0.1.md`, `ARCHITECTURE-PRESSURE-TESTS-v0.1.md`, `TRANSLATION-LAYER-v0.1.md`, `SPEC-EVOLUTION-POLICY-v0.1.md`.

> **Core thesis.** Governed execution requires governed input. Operational drift often begins at the instruction layer before it appears in runtime behavior. An ungoverned input layer cannot produce a governed output layer, regardless of how well the runtime, workforce, or release stages are constrained.

---

## 1. Purpose

This document defines the immutable execution-input grammar for governed cognition operations within the WiseOrder / Intellagent stack. It standardizes the structural form of:

- human instruction structure,
- execution requests,
- work-order initiation,
- release operations,
- review requests,
- hardening requests,
- architecture requests,
- pressure-testing requests.

The grammar exists to reduce, at the input layer:

- ambiguity,
- scope drift,
- hidden authority escalation,
- role confusion,
- undefined outputs,
- uncontrolled operational variance.

It does not change runtime behavior, governance authority, workforce semantics, or release gates. It constrains the shape of instructions that flow into those layers.

---

## 2. Why Input Grammar Matters

Every layer below the input layer is already governed. The runtime is governed. The workforce is governed. Releases are gated. Architecture changes are pressure-tested. The remaining unguarded surface is the instruction itself.

If the instruction is ambiguous, the runtime executes ambiguity. If the instruction silently expands scope, the workforce silently expands scope. If the instruction touches canon without declaring so, governance has no surface to refuse. The downstream gates assume the instruction is well-formed; if it is not, the gates measure the wrong thing.

Input grammar closes this gap by making the instruction itself a governed artifact.

---

## 3. Human-To-Execution Translation

A human-issued instruction becomes an execution request through a deterministic translation:

1. The instruction is parsed against the Required Input Structure (§6).
2. Each component is checked against its Definition Rules (§§7–12).
3. The instruction is classified as one of: execution, release, review, hardening, architecture, pressure-test, translation-layer, canon-touch, CANON BREAK.
4. Operation-specific grammar (§§14–21) is applied.
5. The instruction is either accepted as a governed work order or rejected.

Translation is one-directional: the input grammar does not infer missing components, does not soften ambiguity, and does not promote implicit authority into explicit authority. Missing components are missing. Ambiguity is rejection.

---

## 4. Operational Drift At The Input Layer

Operational drift at the input layer has identifiable patterns:

- **Unstated scope expansion.** An instruction phrased as a small task that, on inspection, modifies canon, runtime, or release.
- **Undeclared canon touch.** A request to "clean up," "fix," "improve," or "align" wording in a document that turns out to be normative.
- **Authority slippage.** Phrasing that treats a reviewer-level operation as if it were an author-level operation, or treats a workforce operation as if it were a governance operation.
- **Output ambiguity.** Instructions that do not say what artifact must exist when the work is done.
- **Conflicting constraints.** Instructions that include constraints that cannot all be satisfied simultaneously.
- **Compound goals.** Instructions that fold multiple operations into a single request without separating their gates.

These patterns are not detected by the runtime, the workforce, or the release pipeline. They are detected only at the input layer, by this grammar.

---

## 5. Immutable Input Principles

The following principles are immutable. They do not depend on operation type, role, or context.

1. **Every governed execution request must be replayable from its instruction alone.** The instruction is the canonical record of intent.
2. **No instruction may grant itself authority it does not already hold.** Authority is declared, not assumed.
3. **No instruction may modify canon without declaring a canon touch.** Silent canon modification is a grammar violation, regardless of whether the modification is correct.
4. **Every governed execution request must define its own outputs.** Undefined outputs cannot be validated and cannot be closed.
5. **Every governed execution request must define its own forbidden actions.** Forbidden actions are part of scope, not separate from it.
6. **Ambiguity is rejection.** A grammar layer that resolves ambiguity by inference defeats its own purpose.
7. **Compound operations are decomposed before execution.** A single instruction may not span multiple operation classes.
8. **Constraints take precedence over goals.** When a goal cannot be reached without violating a constraint, the goal is not reached.

The strongest of these principles is principle 6: **ambiguity is rejection**. Every other principle depends on it.

---

## 6. Required Input Structure

Every governed execution request must contain, at minimum:

- **Goal.** What is the operation expected to produce.
- **Constraints.** What boundaries the operation must respect.
- **Forbidden actions.** What the operation must not do.
- **Scope.** What surface area the operation is allowed to touch.
- **Required outputs.** What artifacts must exist when the operation closes.
- **Validation requirements.** How the operation will be checked.
- **Tone requirements** where applicable. The required register of any produced text.

A request missing any required component is non-compliant and must be rejected or returned for repair before translation to a work order.

---

## 7. Goal Definition Rules

A goal must be:

- **Bounded.** It describes one operation, not a program of work.
- **Measurable.** Completion can be determined by inspection of the required outputs.
- **Singular in operation class.** A goal that mixes execution, release, and canon modification is not one goal; it is three.
- **Stated in operational terms.** "Improve clarity" is not a goal. "Rewrite §4 of document X to remove undefined terms Y and Z" is a goal.

A goal is invalid if it cannot be reached without taking actions outside the declared scope, or if its completion cannot be checked.

---

## 8. Scope Definition Rules

Scope has two parts: allowed scope and forbidden scope. Both must be stated.

- **Allowed scope** lists the files, surfaces, modules, or artifacts the operation may touch.
- **Forbidden scope** lists the files, surfaces, modules, or artifacts the operation must not touch, especially adjacent surfaces that a reasonable operator might assume are in scope.

Scope is closed by default. Anything not declared as allowed is forbidden. The forbidden scope section exists to make adjacency-driven mistakes explicit.

A scope is invalid if it overlaps with canon without a declared canon touch, or if it implies modifications outside the named surfaces.

---

## 9. Constraint Definition Rules

Constraints are operational rules the work must respect. Constraints must be:

- **Explicit.** A constraint that is not written down does not exist.
- **Non-conflicting.** Two constraints that cannot both be satisfied invalidate the input.
- **Independently checkable.** A reviewer must be able to check each constraint without reference to the others.
- **Stable for the duration of the operation.** Constraints are not negotiated mid-execution.

A constraint set is invalid if it contains internal conflicts, if any constraint is unverifiable, or if any constraint depends on undefined terms.

---

## 10. Forbidden-Action Rules

Forbidden actions are part of every governed execution request. They exist because some operations are easy to perform incidentally and hard to detect after the fact. Examples include modifying adjacent canon, expanding scope to "fix" unrelated issues, or producing artifacts not requested.

Forbidden actions must be:

- **Explicit and enumerable.** Stated as a list, not a sentiment.
- **Operational.** Phrased in terms of what the operator may do, not what the operator may feel.
- **Checkable post-hoc.** A reviewer must be able to confirm none of them occurred.

A forbidden-action set that consists only of generic prohibitions ("do not break things") is non-compliant.

---

## 11. Output Definition Rules

Required outputs are the artifacts whose existence and shape mark the operation as complete. Outputs must be:

- **Named.** Each output has a specific identity (filename, artifact type, location).
- **Shaped.** Each output has a specified structure or required sections.
- **Bounded.** The output list is exhaustive; outputs not on the list are not produced.
- **Closeable.** A reviewer can inspect each output and decide pass or fail.

An operation with undefined outputs cannot close. It can only be abandoned.

---

## 12. Role Definition Rules

Every governed execution request operates under a role. Roles include, at minimum: author, reviewer, releaser, hardener, architect, pressure-tester, translator. Role rules:

- **One role per request.** A request that requires acting in two roles is two requests.
- **Role authority is bounded by role.** A reviewer does not modify canon. A releaser does not author. A pressure-tester does not harden.
- **Role is declared, not inferred.** If the role is not stated, the request is non-compliant.
- **Role determines applicable gates.** Different roles invoke different downstream governance surfaces.

Role confusion is a leading cause of operational drift and is rejected at the input layer.

---

## 13. Validation Requirements

Every governed execution request must declare how it will be validated. Validation requirements must be:

- **Deterministic.** The same artifacts produce the same pass/fail decision on inspection.
- **Independent of the producer.** Validation does not require the producer's testimony.
- **Specific.** "Looks correct" is not validation. "Section X exists, contains subsections A, B, C, and references D" is validation.
- **Bounded in scope.** Validation does not expand into adjacent surfaces.

A request without validation requirements cannot be closed and must be rejected.

---

## 14. Release-Operation Grammar

Release operations have additional grammar requirements beyond the standard structure:

- **Release type declared.** Patch, minor, major, or canon-touch release.
- **Gates declared.** Which release gates apply (see `CANONICAL-RELEASE-v0.1.md`).
- **Surface enumerated.** The full list of artifacts being released.
- **Replay path declared.** How the release can be reproduced from inputs.
- **Rollback condition declared.** What constitutes failure and the rollback surface.

A release request lacking any of these is rejected. A release request that hides itself inside a non-release operation (e.g., a "documentation update" that bumps a version number) is a grammar violation.

---

## 15. Review-Operation Grammar

Review requests must declare:

- **What is being reviewed.** Specific artifacts, sections, or surfaces.
- **Reviewer role.** Reader, technical reviewer, governance reviewer, canon reviewer.
- **What constitutes pass and fail.** A review without an explicit decision rule is not a review.
- **Whether the reviewer may modify.** A review that produces edits and a review that produces only a verdict are different operations.

A review that produces unrequested modifications is a grammar violation, even if the modifications are improvements.

---

## 16. Hardening-Operation Grammar

Hardening requests must declare:

- **Threat or weakness being hardened against.** Hardening with no declared target is unbounded.
- **Surface being hardened.** The exact module, contract, or artifact.
- **Acceptance test for hardening.** What demonstrates the hardening has occurred.
- **Non-hardening surfaces.** Surfaces explicitly not in scope, to prevent collateral modification.

Hardening must not silently widen its surface. A hardening request that touches canon is a canon-touch operation and must be declared as such.

---

## 17. Architecture-Operation Grammar

Architecture requests must declare:

- **Architectural surface.** Which structural property is being changed (boundaries, contracts, dependency direction, layering).
- **Pressure-test linkage.** Which pressure tests apply (see `ARCHITECTURE-PRESSURE-TESTS-v0.1.md`).
- **Compatibility statement.** Whether the change is compatible, breaking, or canon-touching.
- **Dependency-gradient impact.** Which gradient steps are affected (see `DEPENDENCY-GRADIENT-v0.1.md`).

Architecture changes without these declarations cannot be governed and are rejected at the input layer.

---

## 18. Pressure-Test Grammar

Pressure-test requests must declare:

- **Hypothesis under test.** What property is being stressed.
- **Surface under test.** The bounded scope of the test.
- **Pass and fail criteria.** Determined before the test runs.
- **Disposition rule.** What happens to the system if the test fails (no automatic remediation; remediation is a separate operation).

A pressure-test request that quietly remediates is a grammar violation. Tests test; they do not fix.

---

## 19. Translation-Layer Grammar

Requests that produce or modify translation-layer artifacts (explanatory documents, cross-language canonicalization notes, translator documents) must declare:

- **Audience.** Who the document is for.
- **Normative status.** Normative, non-normative, or explanatory.
- **Canon adjacency.** Whether the document references canon, mirrors canon, or is independent.
- **Update policy.** When this document must be updated relative to canon changes.

Translation-layer documents are not canon. A translation-layer request that modifies canon under the guise of translation is a CANON BREAK.

---

## 20. Canon-Touch Grammar

A canon touch is any modification to a normative document, normative section, or normative artifact. Canon-touch requests must declare:

- **Canon surface touched.** Specific document and section.
- **Modification class.** Clarification, correction, expansion, or restriction.
- **Compatibility statement.** Whether prior conformance vectors remain valid.
- **Evolution-policy linkage.** Which clause of `SPEC-EVOLUTION-POLICY-v0.1.md` governs the change.

Silent canon modification — a canon touch performed inside a non-canon-touch request — is a grammar violation regardless of correctness.

---

## 21. CANON BREAK Grammar

A CANON BREAK is a canon touch that invalidates prior conformance. CANON BREAK requests must declare:

- **Break statement.** Explicit acknowledgement that this operation is a CANON BREAK.
- **Vectors invalidated.** The conformance vectors that no longer apply.
- **Migration path.** How prior implementations move forward.
- **Versioning impact.** The version-bump implications.
- **Rationale.** Why a non-breaking alternative was not taken.

A CANON BREAK introduced as a routine update is the most severe grammar violation defined by this document.

---

## 22. Non-Compliant Input Detection

Non-compliant input is detected at the input layer before translation to a work order. Detection rules:

- **Missing required component.** Any of Goal, Constraints, Forbidden actions, Scope, Required outputs, Validation requirements is absent.
- **Internal conflict.** Two declared elements cannot both be satisfied.
- **Operation-class mixing.** A single request spans multiple operation classes.
- **Authority assumption.** The request acts as if it has authority it has not declared.
- **Canon adjacency without declaration.** The scope or goal touches canon without naming the canon touch.
- **Output ambiguity.** Required outputs are not named, shaped, or bounded.
- **Validation absence.** No validation requirements are declared.

Detected non-compliance produces rejection, not silent repair.

---

## 23. Ambiguity Rejection Rules

Ambiguity is rejected at the input layer.

A grammar that tolerates ambiguity is not a grammar; it is a style guide. The purpose of input governance is to refuse to begin work whose intent cannot be reproduced from the instruction alone. An ambiguous goal, an ambiguous constraint, an ambiguous output specification, or an ambiguous role each trigger rejection. Rejection is not adversarial; it is the only operation that preserves replayability. Repaired instructions are accepted; inferred instructions are not. The grammar layer never softens, never guesses, never promotes implicit intent into explicit work. If the instruction cannot stand on its own as the canonical record of what was asked, the work does not begin. This rule has no exceptions across operation types, roles, or urgency levels.

---

## 24. Scope Escalation Rules

Scope escalation occurs when an operation expands beyond its declared allowed scope during execution. Rules:

- **Operations do not self-escalate.** An operation that discovers additional necessary work halts and returns a request for a follow-up operation.
- **Adjacent surfaces are not implicit scope.** Touching an adjacent file because it is "obviously related" is escalation.
- **Refactors are not free.** A refactor inside a non-refactor operation is escalation.
- **Improvements are not free.** Unrequested improvements are escalation.

Scope escalation is detected by comparing produced outputs against declared scope. Escalations are reverted, not retroactively authorized.

---

## 25. Human Override Semantics

A human may override grammar rules only by declaring the override explicitly. Override rules:

- **Override is declared, not implied.** A human cannot override by phrasing an instruction casually.
- **Override is bounded.** It applies to one request, not a session, not a project, not a class of operations.
- **Override is recorded.** The override is part of the canonical record of intent.
- **Override does not waive canon-touch grammar.** Canon and CANON BREAK declarations are not overridable.

A human override that contradicts canon-touch grammar is not an override; it is a grammar violation.

---

## 26. Workflow Continuity Rules

Workflow continuity ensures that a long-running operation across multiple instructions remains governed:

- **Continuation requests must reference their predecessor.** Each follow-up names the prior request.
- **Scope inherits, not expands.** A continuation cannot widen scope without a new declaration.
- **State is in the artifacts, not in the operator.** Continuity does not depend on the operator remembering prior context; it depends on prior outputs.
- **Closure is explicit.** A workflow does not end by drifting into idleness; it ends by satisfying its closure requirements.

A workflow that drifts open across many requests with no explicit closure is a governance hazard regardless of the quality of individual outputs.

---

## 27. Long-Term Compatibility Rules

The grammar must remain stable across long-term infrastructure evolution:

- **Required components do not shrink.** New versions may add required components; they do not remove them.
- **Operation classes are append-only.** New operation classes may be defined; existing classes are not redefined.
- **Rejection rules are append-only.** New rejection rules may be added; existing ones are not weakened.
- **Existing instructions remain interpretable under future grammar.** A v0.1-compliant instruction must remain a v0.1-compliant instruction under v0.2 and beyond.

Compatibility is maintained because the grammar is the substrate against which all governed execution is replayed.

---

## 28. What Must Never Change

The following do not change across versions of this grammar:

- The set of required components in §6.
- The principle that ambiguity is rejection (§5, §23).
- The principle that authority is declared, not assumed (§5).
- The principle that canon touches must be declared (§§5, 20).
- The principle that CANON BREAKs must be declared as such (§21).
- The principle that one request belongs to one operation class (§5, §7).
- The principle that scope is closed by default (§8).
- The principle that operations do not self-escalate (§24).

These constitute the immutable core. A change to any of them is a CANON BREAK against this grammar.

---

## 29. What May Evolve

The following may evolve under `SPEC-EVOLUTION-POLICY-v0.1.md`:

- Additional operation classes beyond those enumerated in §§14–21.
- Additional required components, added without removing existing ones.
- Additional rejection rules, added without weakening existing ones.
- Refinements to validation specifications.
- Refinements to role enumerations.
- Refinements to translation-layer adjacency rules.

Evolution is additive. Evolution that subtracts from the immutable core is not evolution; it is replacement.

---

## 30. Final Law

The input layer is part of governance. Poorly governed instructions produce poorly governed execution, regardless of how well the runtime, workforce, and release stages are constrained. Input grammar exists to reduce operational entropy across long-term infrastructure evolution. It is not a style; it is a substrate.

---

## Appendix A — Standard Input Template

Every governed execution request should be expressible in the following structure. Missing fields indicate non-compliance.

```
Goal:
  <single-operation, bounded, measurable goal statement>

Context:
  <minimum context required to disambiguate the goal>

Allowed scope:
  - <named surface 1>
  - <named surface 2>

Forbidden scope:
  - <named adjacent surface 1>
  - <named adjacent surface 2>

Required outputs:
  - <named artifact 1, shape, location>
  - <named artifact 2, shape, location>

Required gates:
  - <gate 1>
  - <gate 2>

Non-goals:
  - <explicit out-of-scope item 1>
  - <explicit out-of-scope item 2>

Constraints:
  - <constraint 1>
  - <constraint 2>

Validation requirements:
  - <deterministic check 1>
  - <deterministic check 2>

Closure requirements:
  - <condition under which this request is considered closed>
```

A request that does not fit this structure does not enter the work-order pipeline.

---

## Appendix B — What Makes An Input Unsafe?

An input is unsafe when it permits governed execution to begin without governed intent. Unsafe patterns include:

- **Undefined authority.** The instruction acts under a role that is not stated.
- **Hidden scope escalation.** The instruction's surface, on inspection, exceeds the surface it appears to claim.
- **Ambiguous goals.** Completion cannot be determined by inspection.
- **Conflicting constraints.** Two constraints cannot both hold.
- **Undefined outputs.** No artifacts are named.
- **Canon-touch without declaration.** Normative material is being modified silently.
- **Release operations without gates.** A release is requested without naming which gates apply.
- **Silent semantic changes.** Vocabulary or definitions shift inside a request that does not declare a canon touch.

Unsafe inputs are rejected, not repaired by inference.

---

## Appendix C — What Makes An Input Operationally Valid?

An input is operationally valid when it can stand alone as the canonical record of intent. Validity requires:

- **Bounded scope.** Allowed and forbidden scope are both stated and non-overlapping.
- **Measurable outputs.** Required outputs are named, shaped, and bounded.
- **Explicit constraints.** Each constraint is independently checkable.
- **Deterministic validation.** The same artifacts produce the same pass/fail decision on inspection.
- **Explicit authority.** The role under which the operation acts is declared and matches its operation class.
- **Replayable intent.** The instruction is sufficient to reconstruct the work without reference to the operator's memory or session state.
- **Role compatibility.** The declared role is permitted to perform the declared operation class.

An input that satisfies these is admissible. An input that does not, is not.

---

## Appendix D — What Inputs Must Be Rejected?

The following inputs must be rejected at the grammar layer regardless of operator, urgency, or apparent merit:

- **Conflicting goals.** A single request demanding mutually exclusive end-states.
- **Undefined release scope.** A release request that does not enumerate its surface.
- **Ambiguous canon modification.** A request that may or may not modify canon depending on interpretation.
- **Runtime modification hidden inside documentation requests.** A request whose declared class is documentation but whose execution modifies runtime semantics.
- **Undefined validation requirements.** A request with no deterministic check for closure.
- **Authority escalation without declaration.** A request that requires authority the operator has not declared.
- **Compound operations.** A request that spans more than one operation class.
- **CANON BREAK introduced as a routine change.** Any breaking modification not declared as such.

Rejection at this layer prevents drift before it becomes runtime cost.

---

## Appendix E — What Happens Without Input Governance?

Without input governance, the downstream governance layers measure the wrong thing. Observable consequences:

- **Execution drift.** Operations gradually diverge from their stated intent because intent was never tightly stated.
- **Semantic erosion.** Terms shift meaning across releases because canon is touched silently.
- **Hidden authority expansion.** Roles accumulate latitude they were never granted.
- **Inconsistent releases.** The same nominal release performs different operations across iterations.
- **Unverifiable operational history.** Past work cannot be reconstructed because the instructions that produced it were not canonical.
- **Non-replayable intent.** Replays produce different outputs because the instruction did not pin them down.
- **Governance collapse through ambiguity.** Each individual ambiguity is small; their accumulation is the failure mode.

Input governance is the load-bearing gate that prevents these. Removing it does not produce faster operations; it produces operations whose meaning cannot be defended.

---

**End of INPUT-GRAMMAR-v0.1.md.**
