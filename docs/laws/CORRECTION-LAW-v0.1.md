# CORRECTION LAW v0.1
## Deterministic Divergence And Hardening Rules For Governed Infrastructure

---

## 1. Purpose

This document defines the immutable correction law governing admissible
correction, divergence handling, legitimacy restoration, and operational
hardening across the governed cognition stack.

It standardizes:

- correction legitimacy
- correction boundaries
- correction replayability
- correction workflows
- divergence handling
- correction authority
- correction validation
- correction continuity
- hardening legitimacy

It does not redesign runtime semantics, replay semantics, workflow semantics,
authority semantics, validation semantics, or trust semantics. Existing canon
is binding. Correction law sits adjacent to those laws and governs how
operational divergence from canon becomes reconstructable hardening rather
than hidden corruption.

---

## 2. Why Correction Law Matters

A governed system is not defined by the absence of failure. Every operational
system fails. The question is whether failure is converted into recorded
correction or absorbed as silent drift.

Without correction law, operational reality and canonical record diverge over
time. Each undocumented fix, each unannounced validator change, each silent
hotfix widens the gap between what the system claims to do and what the system
actually does. The record decays. The trust accumulated against that record
decays with it.

Correction law exists to convert operational divergence from hidden corruption
into reconstructable hardening continuity.

---

## 3. Failure vs Corruption

Failure is operational. Corruption is governance.

Failure is an event in which a system produced an outcome inconsistent with
its declared canon. Failure is admissible. Failure is reconstructable.
Failure is correctable.

Corruption is the condition in which failure has occurred and the record no
longer reflects it. Corruption is not an event. Corruption is the absence of
an event that occurred.

A failure that is preserved, surfaced, replayed, and corrected under recorded
authority is a hardening artifact. The same failure, silently mutated away,
is a corruption artifact. The operational outcome may appear identical. The
governance outcome is opposite.

Correction law draws this line and refuses to let it move.

---

## 4. Correction As Governance Continuity

Correction is not the opposite of failure. Correction is the continuation of
governance after failure.

A system that fails and corrects under canon retains its governance posture.
A system that fails and silently overwrites its history loses its governance
posture, regardless of whether the underlying defect is now absent.

Governance continuity is therefore preserved by correction, not by absence
of failure. The presence of recorded correction is a stronger admissibility
signal than the absence of recorded failure, because the absence of recorded
failure is consistent with both a defect-free system and a fully corrupted
record.

---

## 5. Correction And Replay

Replay law defines how operational history is reconstructed. Correction law
depends on that reconstruction directly: a correction is admissible only when
both the original failure and the corrective action can be replayed against
the record to the same outcome.

A correction that cannot be replayed is not a correction. It is a mutation
asserted to be a correction. Mutation does not accumulate hardening.

Replay does not produce correction on its own. Replay produces the substrate
on which correction is permitted to be recorded.

---

## 6. Correction And Validation

Validation law defines how operational decisions become mechanically
admissible. Correction law extends validation across the divergence event:
the corrective action, the post-correction state, and the threshold at which
the system is declared restored must each pass validation under canon.

A correction whose validator was changed during the correction is not a
validated correction. It is a validator change presented as a fix. Both the
validator change and the corrective action remain separately admissible
events; they do not collapse into one.

Validation does not produce correction on its own. Validation produces the
mechanical filter through which a candidate correction is permitted to enter
the record.

---

## 7. Correction And Trust Accumulation

Trust law defines how operational credibility accumulates across replayable,
validated continuity under pressure. Correction is the primary pressure event
against which trust is tested.

A system that accumulates trust during quiet operation but loses
reconstructability during correction has not accumulated trust. It has
accumulated the appearance of trust during periods in which the underlying
substrate was not under load.

Correction-time behavior is therefore the load-bearing surface of trust. A
correction that preserves replayability, validation, authority, and audit
continuity contributes positively to trust accumulation. A correction that
breaks any of these severs the trust chain at the correction event,
regardless of how much continuity preceded it.

---

## 8. Immutable Correction Principles

The following principles do not change across releases, implementations, or
deployments.

1. A correction is a recorded event, not a recovered state.
2. The original failure must remain reconstructable after correction.
3. Every correction has explicit, recorded authority.
4. Every correction has bounded, declared scope.
5. Every correction is replayable end-to-end against the record.
6. Every correction is validated under canon, not under exception.
7. Unsupported surfaces affected by a correction remain declared as
   unsupported.
8. Audit history is append-only across correction events.
9. Canonicalization rules do not change silently as part of a correction.
10. Release identity is preserved across correction; corrections do not
    rewrite prior releases.

These principles are jointly necessary. The failure of any one invalidates
the correction.

---

## 9. Legitimate Correction Requirements

A correction is operationally legitimate only when all of the following hold:

- divergence is surfaced explicitly in the record
- the original failure remains reconstructable from preserved evidence
- correction authority is explicit, recorded, and bounded
- correction scope is declared and does not silently expand
- correction validation is replayable against canon
- correction artifacts (inputs, transforms, outputs, validator results)
  are preserved
- unsupported surfaces remain declared as unsupported
- historical continuity is preserved end-to-end across the correction event

A correction missing any of these requirements is not a legitimate
correction. It is an operational mutation. Operational mutations do not
contribute to hardening continuity and do not restore trust.

---

## 10. Divergence Detection Rules

Divergence detection governs the moment at which operational reality is
recognized to depart from canonical reality.

1. Divergence is detected against canon, not against expectation.
2. Divergence detection is recorded as an event, distinct from the corrective
   action.
3. The detector, the detection input, and the detection threshold are all
   recorded.
4. Detection does not authorize correction. Detection authorizes the
   correction workflow to begin.
5. Suppressed divergence is itself a correction failure event.
6. Divergence detected and not recorded is treated as undetected for the
   purposes of admissibility.

A system that observes divergence and does not record the observation has not
detected divergence. It has chosen not to.

---

## 11. Correction Workflow Rules

Correction is a workflow, not an act. Workflow grammar applies to it without
exception.

1. The correction workflow is initiated by a recorded divergence event.
2. The workflow declares its scope, its authority, and its expected
   post-state before the corrective action is applied.
3. Each step of the workflow is recorded against canon.
4. The corrective action is bounded to declared scope; surfaces outside
   scope are not modified by the correction.
5. The workflow terminates only after post-correction validation has passed
   under canon.
6. A workflow that terminates without recorded validation is not a completed
   correction.
7. Correction workflows do not nest silently; a correction that requires a
   secondary correction declares the secondary as a distinct workflow.

The correction workflow is the governance object. The corrective action is
one step inside it.

---

## 12. Correction Validation Rules

Correction validation is the mechanical filter that determines whether a
candidate correction is admissible to the record.

1. Validation runs against canon at the time of correction, with the
   canonical version recorded alongside the result.
2. Validation covers the corrective action, the post-correction state, and
   the divergence boundary that triggered the workflow.
3. Validators are not modified during the correction they validate.
4. A correction that requires validator modification declares that
   modification as a distinct, prior event.
5. Validation results are append-only and replayable.
6. A correction that passes validation under a non-canonical exception is
   not a validated correction.

Validation under exception is a recorded operational decision, not a
correction. The two are not interchangeable.

---

## 13. Correction Replay Rules

Replay is the substrate against which corrections are tested for
reconstructability.

1. The pre-correction state is replayable from the record.
2. The corrective action is replayable from the record.
3. The post-correction state is replayable from the record.
4. The divergence detection event is replayable from the record.
5. The validation pass that admitted the correction is replayable from the
   record.
6. A correction whose replay does not converge to the recorded
   post-correction state is not a correction. It is unrecorded divergence
   wearing the label of a correction.

Replayability is binary. A partially replayable correction is not a
correction.

---

## 14. Correction Authority Rules

Authority law applies to every correction event without exception.

1. Every correction has a named authority.
2. The authority is recorded against the correction event.
3. Authority is bounded to the scope of the correction; it does not extend
   to adjacent surfaces.
4. Authority for correction is not implicit in operational access.
5. Authority cannot be assigned retroactively.
6. A correction without recorded authority is an authority-less mutation,
   regardless of whether the underlying defect is now absent.

Authority does not produce correctness. Authority produces accountability.
Correction without authority is therefore unaccountable, even when correct.

---

## 15. Correction Boundary Rules

Correction boundaries govern the surface area within which a correction is
permitted to act.

1. The boundary is declared before the correction is applied.
2. The boundary is recorded against the correction event.
3. The corrective action does not modify state outside the declared
   boundary.
4. Side effects that cross the boundary are themselves correction events,
   each with their own authority, validation, and replay.
5. Implicit cross-boundary corrections are forbidden.
6. Boundary expansion mid-correction terminates the workflow and requires a
   new, distinct correction workflow.

A correction that quietly grew is not a correction. It is two events
recorded as one.

---

## 16. Correction Failure Rules

Corrections themselves can fail. Correction law treats correction failure as
a first-class event.

1. A failed correction is recorded as a failed correction, not as an
   incomplete correction.
2. Failed corrections do not implicitly authorize a follow-up correction;
   the follow-up declares its own authority.
3. The failure mode of the correction is recorded.
4. The state of the system after a failed correction is recorded.
5. A correction that silently retried until success is recorded as multiple
   correction events, not one.

A correction that succeeds on retry without recording the prior attempts is
not a successful correction. It is a successful corruption of the record.

---

## 17. Correction Drift

Correction drift is the gradual divergence between declared correction
behavior and actual correction behavior.

Correction drift is detected by replaying historical corrections under
current canon and comparing the outcomes to recorded outcomes. Divergence
between replay outcome and recorded outcome is correction drift.

Correction drift is itself a divergence event. It is surfaced, recorded,
authorized, validated, and corrected under the same correction law that
governs operational divergence. Correction law applies recursively to itself.

A claim of zero correction drift is not admissible. The admissible claim is
that correction drift is detected, recorded, and bounded under canon.

---

## 18. Correction Across Versions

Corrections are scoped to a specific canonical version.

1. A correction declares the canon version under which it is admitted.
2. A correction valid under one canon version is not automatically valid
   under another.
3. Cross-version correction requires explicit re-validation under the new
   canon.
4. A correction whose admissibility depends on a deprecated canon does not
   become inadmissible retroactively, but does not extend forward implicitly.
5. Version transitions do not silently re-author corrections.

Versioning preserves the historical correction record without dragging it
forward as live admissibility.

---

## 19. Correction Across Releases

Releases bound the operational identity of the system at a point in time.

1. A correction does not rewrite a prior release.
2. A correction issued against a prior release is recorded as a correction
   against that release, not as a modification of it.
3. Release identity, hashes, and contents are append-only.
4. A patched release is a new release, not the same release.
5. Release notes are amended only by recorded amendment events; they are
   not silently updated.

Release rewriting is one of the strongest signals of governance failure. It
is forbidden under correction law.

---

## 20. Correction Across Implementations

Multiple implementations of the same canon may exist. Corrections do not
implicitly propagate between them.

1. A correction is admitted against a specific implementation.
2. The same divergence in another implementation is a separate correction
   event, with its own authority, scope, validation, and replay.
3. Cross-implementation corrections require declared, replayable evidence
   that the correction is valid in the target implementation.
4. Implementation-specific corrections do not modify canon; they modify the
   implementation's conformance posture against canon.

A claim that "the fix applies to all implementations" is not admissible
without per-implementation correction records.

---

## 21. Correction Claims

The following are admissible correction claims:

- "Divergence X was detected at time T against canon version V."
- "Correction workflow W was authorized by A, scoped to S, and recorded."
- "Post-correction state passed validation under canon version V."
- "The pre-correction failure remains reconstructable from record R."
- "Replay of the correction converges to the recorded post-correction
  state."
- "Unsupported surfaces affected by the correction remain declared as
  unsupported."
- "Correction drift is detected and bounded under canon."

Each claim is reconstructable from the record. Each claim is replayable.
Each claim has a named authority and a bounded scope.

---

## 22. Forbidden Correction Claims

The following claims are inadmissible under correction law.

- claiming correction without replay evidence
- claiming resolution without preserved failure state
- claiming interoperability after unverified modification
- claiming restored trust without validation continuity
- claiming safety without threat-boundary replay
- claiming drift elimination
- hidden hotfix claims
- undocumented rollback claims
- claiming a release was "always" in its current state
- claiming a validator was "always" canonical
- claiming a correction was authorized when authority was not recorded at
  the time of correction
- claiming convergence without replay convergence

A system making any of these claims is asserting governance that the record
does not support. The claim is inadmissible regardless of the operational
truth behind it.

---

## 23. Correction Failure Classes

Correction failures are classified for record consistency.

- **CR-1 Hidden Correction.** A correction was applied without a recorded
  correction event.
- **CR-2 Replay-Invalid Fix.** A correction was recorded but does not
  replay to its recorded post-state.
- **CR-3 Authority-Less Mutation.** State was changed without recorded
  authority.
- **CR-4 Validation Drift.** Validators changed during the correction they
  were used to validate.
- **CR-5 Canonicalization Drift.** Canonicalization rules were changed
  silently as part of a correction.
- **CR-6 Audit Erasure.** Audit history was modified rather than appended.
- **CR-7 Unsupported Restoration Claim.** A correction was claimed to
  restore an unsupported surface to supported status without explicit
  re-declaration.
- **CR-8 Release Rewrite.** A prior release was modified rather than
  superseded.
- **CR-9 Hidden Rollback.** A rollback was applied without a recorded
  rollback event.
- **CR-10 Divergence Suppression.** Divergence was detected and not
  recorded.

Each class is a distinct admissibility failure. Multiple classes can attach
to a single event. None subsume any other.

---

## 24. Correction Recovery Rules

Recovery from a correction failure is itself a correction event, governed
by this same law.

1. Recovery declares which correction failure class it addresses.
2. Recovery does not erase the original correction failure record.
3. Recovery has its own authority, scope, validation, and replay.
4. Recovery does not implicitly restore trust; trust restoration is governed
   separately.
5. A recovery that requires further recovery is recorded as a chain of
   distinct events.

Recovery is layered on top of the failure record, not substituted for it.

---

## 25. Trust Restoration Rules

Trust restoration after a correction failure follows trust law and is
bounded by correction law's evidentiary requirements.

1. Trust does not restore on the basis of corrective action alone.
2. Trust restores only across replayable, validated continuity following
   the correction.
3. The duration and pressure of post-correction continuity required for
   trust restoration are not shortened by the urgency of the correction.
4. Trust restoration claims that bypass continuity are forbidden.
5. A correction that succeeds operationally does not by itself restore
   trust; it produces the substrate on which trust may begin to
   re-accumulate.

Correction restores governance continuity. Time under canon restores trust.
The two are not interchangeable.

---

## 26. Canonical Correction Rules

Canon itself is correctable, under stricter conditions than operational
state.

1. A canon correction is a recorded, authorized event with declared scope.
2. Canon corrections are versioned; prior canon versions are preserved.
3. A canon correction does not retroactively invalidate corrections admitted
   under prior canon.
4. A canon correction does not silently re-author historical records.
5. Canon corrections require evidence that the change is consistent with
   the immutable principles of the affected law.
6. A proposed canon correction that conflicts with an immutable principle
   is inadmissible.

Canon is correctable. Canon's immutable principles are not.

---

## 27. Long-Term Hardening Continuity

Hardening is the cumulative artifact of corrections recorded under canon
across time. It is not the same as defect absence.

1. Hardening is measured by the reconstructability of correction history,
   not by the count of corrections.
2. A long, replayable correction history is a stronger hardening signal
   than a short, sparse one.
3. Gaps in the correction record degrade hardening continuity even if no
   defects are visible.
4. Hardening continuity is bounded to the system that produced it; it does
   not transfer by association, branding, or shared dependency.
5. A system that resets its correction record loses hardening continuity,
   regardless of operational state.

Hardening is what a system has survived under canon. It cannot be
manufactured. It can only be accumulated.

---

## 28. What Must Never Change

The following are immutable across all versions, releases, and
implementations.

- Failure is admissible; corruption is not.
- Every correction is a recorded event with explicit authority.
- Every correction is bounded, replayable, and validated under canon.
- Original failure evidence is preserved across correction.
- Audit history is append-only across correction events.
- Canonicalization rules do not change silently as part of a correction.
- Releases are not rewritten by corrections.
- Unsupported surfaces remain declared as unsupported across corrections.
- Correction drift is itself a divergence event under this law.
- Forbidden correction claims remain forbidden.

These are the load-bearing surfaces of correction law. They are not subject
to evolution.

---

## 29. What May Evolve

The following are permitted to evolve under recorded canon corrections.

- the specific format of correction records
- the specific transport of correction artifacts
- the specific validators used to admit a correction
- the granularity of divergence detection
- the operational tooling around correction workflows
- the classification taxonomy of correction failures, additively
- the cross-implementation conformance evidence requirements

Evolution of these surfaces is itself governed by this same correction law.
Evolution that bypasses correction law is not evolution. It is drift.

---

## 30. Final Law

A governed system is not defined by the absence of failure. It is defined
by whether failure becomes hidden corruption or recorded correction.

A correction that is surfaced, bounded, authorized, validated, and
replayable converts operational divergence into hardening continuity. A
correction that is hidden, unbounded, unauthorized, unvalidated, or
unreplayable converts operational divergence into corruption.

A system that cannot preserve and replay its own failures cannot accumulate
trustworthy correction history.

Correction law exists to convert operational divergence from hidden
corruption into reconstructable hardening continuity.

This is the law.
