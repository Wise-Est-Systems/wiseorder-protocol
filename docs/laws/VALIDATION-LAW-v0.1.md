# VALIDATION LAW v0.1
## Deterministic Enforcement Rules For Governed Infrastructure

---

## 1. Purpose

This document defines the immutable validation law governing admissibility,
enforcement legitimacy, deterministic inspection, and operational truth surfaces
across the governed cognition stack.

It standardizes:

- validation legitimacy
- gate legitimacy
- validator legitimacy
- admissibility rules
- validation replayability
- deterministic inspection
- validation failure semantics
- validation scope boundaries
- enforcement continuity

It does not redesign runtime semantics, replay semantics, workflow semantics,
authority semantics, or forbidden-surface semantics. Existing canon is binding.
Validation law sits adjacent to those laws and governs how their enforcement
becomes mechanically inspectable.

---

## 2. Why Validation Law Matters

Governance that cannot validate itself mechanically becomes dependent on
testimony, interpretation, and trust.

Trust is not an enforcement primitive. Testimony is not an admissibility
primitive. Interpretation is not a gate primitive.

Validation law exists to convert operational legitimacy from assertion into
deterministic inspection. Without validation law, every other law in the stack
degrades into a claim. With validation law, every other law in the stack
becomes reconstructable evidence.

---

## 3. Validation As Operational Truth Surface

Validation is the only surface on which operational truth is mechanically
visible.

A protocol's runtime can be correct, its authority can be sound, its replay
can be intact, and its forbidden surfaces can be honored — and none of that
is observable to an external party without a validation surface that is
itself deterministic.

Validation is therefore the load-bearing surface between internal correctness
and external admissibility. It is the boundary at which governance becomes
inspectable infrastructure rather than internal claim.

---

## 4. Validation And Governance

Governance produces decisions. Validation produces evidence that those
decisions were reached lawfully.

A governance act without validation evidence is operationally indistinguishable
from arbitrary action. The presence of correct policy is insufficient. The
presence of inspectable enforcement is required.

Governance authority is bounded by what validation can reconstruct. Anything
beyond that boundary is asserted, not governed.

---

## 5. Validation And Replay

Replay law defines how operational history is reconstructed. Validation law
defines how the legitimacy of that reconstruction is mechanically confirmed.

Replay without validation produces a reconstruction whose correctness must be
trusted. Validation without replay produces a verdict whose history cannot
be examined. Both surfaces are required, and neither substitutes for the
other.

A validator that cannot itself be replayed is not bound by replay law. A
replay that cannot itself be validated is not bound by validation law. The
two surfaces must hold simultaneously.

---

## 6. Immutable Validation Principles

The following principles are invariant. They do not bend to implementation
convenience, performance pressure, language differences, or operator
preference.

1. Validation must be deterministic.
2. Validation must be replayable.
3. Validation must be bounded in scope.
4. Validation must be mechanically reproducible.
5. Validation must be reconstructable from the record.
6. Validation must be explicit about failure.
7. Validation must be explicit about uncertainty.
8. Validation must be explicit about unsupported claims.
9. Validation must not depend on operator interpretation.
10. Validation must not depend on hidden validator state.

A validator that violates any of these principles is not a governed validator.

---

## 7. Deterministic Validation Requirements

Validation is deterministic when, for a fixed input, fixed validator version,
and fixed declared scope, the output is identical across:

- repeated runs on the same machine
- runs on different machines
- runs across supported implementations
- runs across supported languages

Determinism is a property of the validator's output surface, not of its
internal execution path. Internal nondeterminism is permitted only where it
cannot influence any inspectable output.

A validator whose output varies under fixed inputs is not deterministic and
is therefore not legitimate.

---

## 8. Replayable Validation Requirements

A validation outcome is replayable when:

- the input record is preserved
- the validator version is recorded
- the declared scope is recorded
- the failure conditions in effect are recorded
- the outcome is reconstructable from those four elements alone

Replayability is not a claim about the validator's internals. It is a claim
about the inspectability of the verdict from the record.

A validation outcome that requires access to live validator state, ambient
configuration, or operator memory to be reconstructed is not replayable.

---

## 9. Gate Execution Requirements

Gates are the points at which validation outcomes admit or refuse operational
artifacts.

Gate execution must be:

- ordered
- deterministic in ordering
- inspectable in ordering
- explicit in pass/fail conditions
- explicit in scope of authority
- non-mutating with respect to the artifact under inspection

Gate reordering is forbidden. Hidden gates are forbidden. Conditional gate
suppression is forbidden. A gate that is silently skipped is operationally
equivalent to a gate that did not exist, which is operationally equivalent
to a forged validation.

---

## 10. Validation Artifact Requirements

Every validation execution must produce an artifact sufficient to reconstruct
the verdict.

The artifact must record:

- validator identity
- validator version
- declared validation scope
- input identity
- gate execution order
- per-gate outcome
- failure class on any negative outcome
- explicit unsupported surfaces, if any

The artifact is the validation. The verdict without the artifact is testimony.

---

## 11. Validator Scope Requirements

Every validator must declare its scope before execution. The declared scope
must include:

- what is validated
- what is not validated
- what is partially validated
- what is unsupported
- what failure classes are detectable
- what failure classes are explicitly out of scope

A validator that does not declare scope is operating under unbounded authority,
which validation law forbids.

---

## 12. Validator Boundary Rules

A validator's authority ends at its declared scope. It must not:

- emit verdicts about surfaces outside its declared scope
- imply correctness of surfaces it did not inspect
- absorb adjacent validation responsibilities silently
- expand scope between versions without explicit declaration
- emit pass verdicts for unsupported surfaces

A validator that exceeds its boundary is producing claims, not validations.

---

## 13. Validation Failure Rules

Failure must be:

- explicit
- classified
- recorded
- non-silent
- non-recoverable without re-validation

A validator must not convert a failure into a warning. A validator must not
convert a failure into a soft pass. A validator must not aggregate failures
into a single ambiguous verdict. A validator must not erase a failure on
re-execution without producing a record of the prior failure.

Failure rewriting is operationally equivalent to forgery.

---

## 14. Validation Drift

Validation drift is the unrecorded change in validator behavior across time,
versions, machines, implementations, or languages.

Drift is forbidden in any form that is not:

- explicit
- versioned
- recorded
- replayable against prior records

A validator whose behavior changes silently between executions is no longer
a validator. It is an oracle, and oracles are not admissible governance
infrastructure.

---

## 15. Validation Replay Requirements

A validation execution must be replayable such that:

- the prior record reproduces the prior verdict
- the prior record reproduces the prior failure class
- the prior record reproduces the prior unsupported surfaces
- replay does not require live validator state
- replay does not require ambient configuration
- replay does not require operator interpretation

Replay failure is itself a validation failure class and must be recorded
as such.

---

## 16. Validation Across Versions

When a validator version changes, the following must hold:

- prior records remain replayable against the prior version
- the new version's scope is explicitly declared
- the new version's failure classes are explicitly declared
- behavioral differences from the prior version are explicit
- pass verdicts under the prior version are not silently inherited

Version transitions must be inspectable as transitions, not as continuations.

---

## 17. Validation Across Machines

A validation execution must produce identical inspectable output across
machines for fixed inputs and fixed validator version.

Machine-local state must not influence inspectable output. Machine-local
performance characteristics must not influence verdict. Machine-local
environment must not silently shift validator behavior.

A validator whose verdict varies by machine is not a governed validator.

---

## 18. Validation Across Implementations

When multiple implementations of a validator exist, all implementations
must produce identical inspectable output for fixed inputs.

Implementation differences are permitted in execution path. Implementation
differences are forbidden in inspectable output. An implementation that
produces a different verdict from another implementation under fixed inputs
is in violation of validation law and must be marked non-conforming.

---

## 19. Validation Across Languages

Cross-language validation must produce identical inspectable output for
fixed inputs.

Language-specific representation, encoding, or runtime behavior must not
influence verdict. Where canonicalization is required to achieve cross-language
identity, canonicalization is governed by existing canon and is not
re-defined here.

A validator whose verdict varies by language is not a governed validator
and may not claim cross-language legitimacy.

---

## 20. Validation Invalidation Rules

A validation outcome is invalidated when any of the following hold:

- the validator version is no longer reproducible
- the declared scope at the time of validation is no longer reconstructable
- the input record is no longer reconstructable
- the failure-class taxonomy at the time of validation is no longer
  reconstructable
- the artifact is missing, mutated, or unverifiable

Invalidation is not optional. An invalidated outcome must not be relied upon
as governance evidence.

---

## 21. Validation Refusal Rules

A validator must refuse to emit a verdict when:

- input is outside declared scope
- input is malformed beyond declared tolerance
- the validator cannot guarantee deterministic output
- the validator cannot guarantee replayable output
- a required artifact cannot be produced
- a required gate cannot execute deterministically

Refusal is itself a recorded outcome. Refusal must not be substituted with
a soft pass, an ambiguous verdict, or a silent skip.

---

## 22. Validation Failure Classes

The following failure classes are normative and must be used uniformly across
governed validators.

- **VL-1 Hidden Validator State.** Validator behavior depends on state not
  recorded in the artifact.
- **VL-2 Non-Deterministic Validation.** Verdict varies under fixed inputs
  and fixed version.
- **VL-3 Replay Failure.** Prior record fails to reproduce prior verdict.
- **VL-4 Validator Drift.** Validator behavior has shifted across versions,
  machines, implementations, or languages without explicit declaration.
- **VL-5 Hidden Failure Condition.** A pass verdict was emitted under a
  condition that should have produced a failure verdict.
- **VL-6 Validation Scope Expansion.** Validator emitted verdicts outside
  its declared scope.
- **VL-7 Gate Reordering.** Gate execution order deviated from the declared
  order without an explicit, recorded transition.
- **VL-8 Unsupported Claim Surface.** Validator emitted a claim about a
  surface it does not support.
- **VL-9 Validation Artifact Loss.** Required artifact is missing, mutated,
  or unverifiable.
- **VL-10 Silent Enforcement Mutation.** Enforcement behavior changed without
  a recorded version transition.

These classes are not exhaustive of all conceivable defects, but they are
the minimum taxonomy required for cross-implementation consistency.

---

## 23. Validator Legitimacy Rules

A validator is operationally legitimate only when:

- it declares its scope
- it declares its failure classes
- it produces deterministic output
- it produces replayable output
- it produces a complete artifact
- it refuses inputs outside scope
- it records its version
- it can replay its own legitimacy from the record

A validator that cannot replay its own legitimacy is not a governed validator.

---

## 24. Validator Upgrade Rules

Validator upgrades must:

- preserve the replayability of prior records under the prior version
- declare scope changes explicitly
- declare failure-class changes explicitly
- declare behavioral differences explicitly
- not silently broaden pass conditions
- not silently narrow failure conditions

A validator upgrade that cannot satisfy these conditions is not an upgrade.
It is a replacement, and prior records do not transfer to it.

---

## 25. Validation Claim Restrictions

The following claims are forbidden unless backed by mechanically reconstructable
evidence:

- validation beyond declared scope
- replay claims without replay evidence
- interoperability claims without cross-language proof
- deterministic claims without reproducibility evidence
- security claims without explicit threat boundaries
- validator completeness claims
- hidden-pass conditions of any form
- unverifiable success claims

A claim that cannot be reconstructed from the record is not a validation
claim. It is testimony, and testimony is not admissible.

---

## 26. Validation And Release Legitimacy

A release is operationally legitimate only when its validation surface is:

- complete with respect to declared scope
- replayable from the released record
- inspectable without access to internal state
- bounded explicitly with respect to unsupported surfaces
- consistent across the implementations and languages in the release

A release whose validation surface cannot be replayed by an external party
from the released record is not a governed release. It is a published
artifact accompanied by claim.

---

## 27. Long-Term Validation Continuity

Validation continuity must hold across:

- time
- versions
- machines
- implementations
- languages
- operators
- organizations

Continuity does not require behavioral stasis. It requires that every
behavioral change is explicit, recorded, and replayable against the prior
record. A validator that loses continuity loses legitimacy retroactively to
the point of loss.

---

## 28. What Must Never Change

The following are invariant under all future revisions of this law and all
future revisions of any validator governed by it:

- determinism is required
- replayability is required
- scope must be declared
- failure must be explicit
- artifacts must be complete
- gate ordering must be inspectable
- unsupported surfaces must be explicit
- hidden validator state is forbidden
- silent enforcement mutation is forbidden
- validation outcome rewriting is forbidden

These are the load-bearing invariants. They do not bend.

---

## 29. What May Evolve

The following may evolve under explicit, versioned, recorded transitions:

- the failure-class taxonomy beyond the VL-1..VL-10 minimum
- the artifact schema, provided prior artifacts remain replayable
- the declared scope of any individual validator
- the cross-language and cross-implementation conformance surface
- the ordering and composition of gates within a validator
- the canonicalization surfaces invoked by validators, under existing canon

Evolution is not drift. Evolution is recorded, declared, and replayable.
Drift is none of those.

---

## 30. Final Law

Validation law exists to convert operational correctness from trust into
reconstructable evidence.

A validator that cannot replay its own legitimacy is not a governed validator.

A governance surface that cannot be validated is not a governance surface.
It is a claim.

Validation is the boundary at which governed infrastructure becomes
externally inspectable. Beyond that boundary, governance does not exist.

---

## Appendix A. What Makes Validation Invalid?

The following conditions render a validation outcome invalid:

- hidden validator state
- undocumented validator behavior
- non-deterministic inspection
- validation dependent on operator interpretation
- missing validation artifacts
- silent validator mutation
- validator/version ambiguity
- validation outcome rewriting

Any one of these conditions is sufficient to invalidate the outcome. They do
not compound; they each independently terminate legitimacy.

---

## Appendix B. What Makes Validation Operationally Legitimate?

The following conditions are jointly necessary for operational legitimacy:

- deterministic outputs
- explicit failure conditions
- replayable inspection
- bounded scope
- reconstructable outcomes
- explicit unsupported surfaces
- reproducible gate execution
- inspectable validator behavior

Partial satisfaction does not yield partial legitimacy. Legitimacy is binary
at the artifact level: an outcome is either reconstructable from the record
under these conditions, or it is not.

---

## Appendix C. What Validation Claims Are Forbidden?

The following claims are forbidden unless each is backed by mechanically
reconstructable evidence within the validation artifact:

- validation beyond scope
- replay claims without replay evidence
- interoperability claims without cross-language proof
- deterministic claims without reproducibility evidence
- security claims without threat boundaries
- validator completeness claims
- hidden-pass conditions
- unverifiable success claims

A forbidden claim that appears in or alongside a validation artifact does
not merely weaken the artifact. It invalidates the artifact, because an
artifact that contains an unverifiable claim is itself unverifiable.

---

## Appendix D. What Happens Without Validation Law?

In the absence of validation law, the following outcomes are not hypothetical.
They are the steady-state result.

- governance collapse — every governance act degrades into testimony
- unverifiable releases — releases cannot be inspected by external parties
- hidden drift — validator behavior shifts without record
- validator inconsistency — different machines, implementations, or languages
  return different verdicts under fixed inputs
- replay-invalid operations — prior records can no longer reproduce prior
  verdicts
- enforcement ambiguity — gates pass and fail under conditions that cannot
  be reconstructed
- operational trust erosion — external parties have no surface on which to
  verify, only surfaces on which to trust

Validation law is not a feature. It is the precondition under which the rest
of the stack remains operational infrastructure rather than asserted claim.

---

*End of VALIDATION LAW v0.1.*
