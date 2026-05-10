# AUTHORITY LAW v0.1
Deterministic Authority Rules For Governed Infrastructure

---

## 1. Purpose

Authority Law defines the immutable rules governing admissible operational power across the governed cognition stack. It standardizes how authority is declared, bounded, recorded, replayed, delegated, escalated, reconstructed, revoked, and invalidated.

Authority Law does not define runtime semantics, replay semantics, workflow semantics, validator semantics, or forbidden-surface semantics. Those remain governed by their own canon. Authority Law governs only the legitimacy of the operational power exercised within those systems.

Authority Law applies to:
- humans acting on the system
- agents acting under delegation
- reviewers issuing approvals
- release operators promoting state
- any actor whose action mutates governed surface

---

## 2. Why Authority Law Matters

Governance fails where authority becomes implicit, unreconstructable, or non-replayable. Systems collapse not when bad actors exceed power, but when no one can reconstruct who held what power, under what scope, at what time.

Operational legitimacy is not a property of the action. It is a property of the authority exercised at the moment of the action. Without explicit, bounded, recorded authority, the action has no legitimacy basis — only its outcome.

Authority Law converts operational power from assumption into reconstructable legitimacy.

---

## 3. Authority As A Governed Surface

Authority is a first-class governed surface. It is not metadata. It is not commentary. It is not informal practice.

A governed surface must satisfy:
- declaration must be explicit
- scope must be bounded
- record must be durable
- transitions must be replayable
- legitimacy must be reconstructable without testimony

Authority that does not satisfy these properties is not governed authority. It is informal power. Informal power has no standing in this protocol.

---

## 4. Authority And Replay

Every authority-bearing action must be replayable from the record alone. Replay must reconstruct:
- who held authority
- the scope of that authority
- the source of that authority
- the workflow state at the time of exercise
- the role compatibility at the time of exercise
- the validation that admitted the transition

If replay cannot reconstruct legitimacy, the authority was not legitimate.

Authority Law does not modify replay semantics. It requires that authority exercise leave a record sufficient for the existing replay system to reconstruct legitimacy.

---

## 5. Authority And Workflow Legitimacy

Authority is meaningful only relative to a workflow state. The same role may hold legitimate authority in one state and no authority in another.

Authority exercised in an incompatible workflow state is invalid, regardless of role, regardless of intent, regardless of outcome.

Workflow compatibility must be evaluated at transition time, not retroactively.

Authority Law does not modify workflow semantics. It requires that authority exercise be evaluated against the workflow state defined elsewhere in canon.

---

## 6. Immutable Authority Principles

The following principles are immutable under Authority Law v0.1:

- **P-AU-1** Authority must be explicitly declared.
- **P-AU-2** Authority must be operationally bounded.
- **P-AU-3** Authority must be replayable from the record.
- **P-AU-4** Authority must be compatible with the workflow state at exercise.
- **P-AU-5** Authority must be compatible with the role scope at exercise.
- **P-AU-6** Authority must be reconstructable without testimony.
- **P-AU-7** Authority must be validated at transition time.
- **P-AU-8** Authority not satisfying P-AU-1 through P-AU-7 is not authority.

---

## 7. Explicit Authority Requirements

Authority is explicit only when:
- the holder is named
- the scope is named
- the source of delegation is named
- the workflow state of exercise is named
- the role under which authority is exercised is named
- the record is durable and addressable

Implicit authority is forbidden. Authority cannot be inferred from context, history, ownership, capability, or operator memory.

---

## 8. Bounded Authority Requirements

Authority must be bounded along at least the following dimensions:
- surface (what the authority may touch)
- scope (the operational extent within that surface)
- duration (the validity window)
- workflow state (the states in which it applies)
- transition class (the classes of transition it admits)

Unbounded authority is forbidden. Authority without recorded scope is invalid.

---

## 9. Replayable Authority Requirements

An authority-bearing action is replayable only when the record contains:
- the holder identity
- the scope declaration
- the source-of-authority reference
- the workflow state at exercise
- the role under which exercise occurred
- the validation outcome at transition time

Replay must produce the same legitimacy determination on every reconstruction. Authority whose legitimacy depends on operator recall, side-channel context, or undocumented practice is not replayable and not legitimate.

---

## 10. Delegated Authority Rules

Delegation is legitimate only when:
- the delegating authority itself satisfies P-AU-1 through P-AU-7
- the delegation is explicit and recorded
- the delegated scope is equal to or narrower than the source scope
- the delegation chain is reconstructable end-to-end from the record
- the delegated workflow compatibility is equal to or narrower than the source

Delegation cannot widen scope. Delegation cannot transfer compatibility the source did not hold. Undocumented delegation does not exist.

---

## 11. Human Authority Rules

Human authority is governed authority. It is not exempt from declaration, scope, record, or replay.

A human actor exercises legitimate authority only when:
- the human identity is recorded
- the role is declared
- the scope is bounded
- the workflow state admits the exercise
- the action leaves a replayable record

Human urgency, seniority, or ownership does not confer authority outside declared scope.

---

## 12. Agent Authority Rules

Agents hold no native authority. All agent authority is delegated.

An agent exercises legitimate authority only when:
- a human or recorded source has explicitly delegated the scope
- the delegation is durable and addressable
- the exercise is bounded by the delegated scope
- the exercise produces a replayable record
- the workflow state admits the exercise

Agents may not infer authority from capability, prior behavior, or model identity. Agents may not claim autonomous authority.

---

## 13. Reviewer Authority Rules

Reviewer authority is exercise-bounded and conflict-bounded.

A reviewer exercises legitimate authority only when:
- the reviewer is named
- the review scope is declared
- the reviewer holds no disqualifying conflict (authorship, ownership, beneficiary status defined elsewhere in canon)
- the review is recorded against the specific transition
- the workflow state admits review exercise

A reviewer cannot approve their own action. A reviewer cannot approve outside declared scope. A reviewer cannot retroactively legitimize a prior transition.

---

## 14. Release Authority Rules

Release authority is the strongest operational authority and is the most strictly bounded.

Release authority is legitimate only when:
- the release scope is explicitly declared
- the release artifact is named
- the workflow state is a release-admitting state
- the reviewer chain is complete and replayable
- the canon-touch profile of the release is declared
- the security-boundary profile of the release is declared

Release authority is never blanket. Release authority is never implied. Release authority that cannot be reconstructed against a specific artifact and transition is invalid.

---

## 15. Canon-Touch Authority Rules

A canon-touching action is any action that modifies governed canon.

Canon-touch authority is legitimate only when:
- the actor holds explicit canon-touch scope
- the touch is declared in advance of exercise
- the canon section touched is named
- the workflow state admits canon modification
- a reviewer with canon-touch review scope has approved
- the transition is replayable against the canon record

Canon may not be touched under general scope. Canon may not be touched as a side effect of unrelated work. Canon-touch authority does not generalize across canon sections.

---

## 16. CANON BREAK Authority Rules

A CANON BREAK is a transition that violates an existing canon rule under explicit, bounded, recorded exception.

CANON BREAK authority is legitimate only when:
- the break is declared as a CANON BREAK at transition time
- the broken rule is named
- the justification is recorded
- the scope of the break is bounded to a single transition or named scope
- a reviewer with CANON BREAK authority has approved
- the workflow state admits the break

A CANON BREAK is never silent. A CANON BREAK is never general. A CANON BREAK does not modify canon — it records a bounded exception against it. Modifying canon requires canon-touch authority, not CANON BREAK authority.

---

## 17. Security-Boundary Authority Rules

Security-boundary authority governs actions that cross trust boundaries, modify access, or change the system's exposure surface.

Security-boundary authority is legitimate only when:
- the boundary crossed is explicitly named
- the scope of the crossing is bounded
- the actor holds explicit security-boundary scope
- the workflow state admits boundary crossing
- a reviewer with security-boundary review scope has approved
- the crossing is recorded with replayable evidence

Security-boundary authority does not generalize. Each boundary is its own surface. Authority over one boundary confers no authority over another.

---

## 18. Authority Escalation Rules

Authority escalation is the explicit, recorded transition from a lower scope to a higher scope.

Escalation is legitimate only when:
- the escalation is declared in advance
- the source scope is named
- the target scope is named
- the justification is recorded
- a reviewer with escalation-review scope has approved
- the escalation is bounded in duration and surface

Hidden escalation is the most severe authority failure. Escalation by behavior, by repetition, or by tolerance is forbidden. Escalation that cannot be reconstructed from the record did not occur legitimately.

---

## 19. Authority Reconstruction Rules

Reconstruction is the process by which a third party, using only the record, determines whether an authority exercise was legitimate.

Reconstruction must yield:
- the holder
- the source-of-authority chain
- the scope at exercise
- the workflow state at exercise
- the role at exercise
- the validation outcome at exercise
- the legitimacy determination

Reconstruction must not require the participation of the original actors. A system that cannot reconstruct why an authority transition was legitimate does not possess governed authority.

---

## 20. Authority Failure Classes

The following authority failure classes are recognized:

- **AU-1 Hidden Authority** — authority exercised without declaration.
- **AU-2 Undeclared Delegation** — authority transferred without recorded delegation.
- **AU-3 Scope Escalation** — authority exercised beyond declared scope.
- **AU-4 Replay Reconstruction Failure** — authority whose legitimacy cannot be reconstructed from the record.
- **AU-5 Workflow-Incompatible Approval** — authority exercised in a workflow state that does not admit it.
- **AU-6 Canon-Touch Without Authority** — canon modified without explicit canon-touch scope and review.
- **AU-7 Security-Boundary Escalation** — boundary crossing without explicit security-boundary scope.
- **AU-8 Reviewer Conflict** — review issued by an actor holding a disqualifying conflict.
- **AU-9 Unbounded Release Authority** — release exercised without bounded artifact, scope, and reviewer chain.
- **AU-10 Autonomous Authority Claim** — actor (human or agent) asserting authority not derived from a recorded source.

Each failure class invalidates the transition it occurs within. Failure classes are detected at transition time where possible and at reconstruction time otherwise.

---

## 21. Authority Revocation Rules

Authority is revocable. Revocation is legitimate only when:
- the revoking authority itself satisfies P-AU-1 through P-AU-7
- the revoked scope is named
- the revocation is recorded
- the effective transition is named
- the workflow state admits revocation

Revocation is forward-acting. Revocation does not retroactively invalidate prior legitimate exercises. Prior exercises retain the legitimacy they held at the time of exercise, evaluated against the record then in force.

---

## 22. Authority Invalidation Rules

Invalidation is distinct from revocation. Invalidation determines that an authority exercise was never legitimate.

Invalidation occurs when:
- reconstruction reveals a failure class (AU-1 through AU-10)
- the source-of-authority chain is found to be itself invalid
- the recorded scope did not admit the action exercised
- the workflow state did not admit the action exercised
- the reviewer chain is found to contain disqualifying conflict

An invalidated exercise is treated as never having held legitimacy. Downstream actions that depended on the invalidated exercise inherit its invalidation until independently legitimized.

---

## 23. Authority Drift

Authority drift is the gradual divergence between declared scope and exercised scope over time.

Drift is detected by:
- comparing exercised scope across reconstructions
- comparing declared scope to recorded exercise patterns
- detecting recurring exercises outside narrow declared scope

Drift is treated as an accumulation of AU-3 Scope Escalation events. Drift is not a separate failure class — it is a pattern that resolves into individual failure-class instances at reconstruction time.

---

## 24. Undefined Authority

Authority that has not been explicitly declared does not exist.

Undefined authority cannot be exercised. Undefined authority cannot be inferred. Undefined authority cannot be granted retroactively to legitimize a prior action.

If a transition requires authority that has not been declared, the transition cannot proceed. Declaration must precede exercise.

---

## 25. Forbidden Authority Claims

The following authority claims are forbidden under Authority Law:

- authority inferred from urgency
- authority inferred from prior behavior
- authority inferred from operator memory
- authority inferred from repository ownership
- authority inferred from model capability
- authority inferred from seniority
- authority inferred from access level
- autonomous authority claims by agents
- autonomous authority claims by humans not derived from a recorded source
- authority without recorded scope
- approval without record
- delegation without record
- escalation without record
- review by a conflicted reviewer
- canon-touch under general scope
- release under general scope
- security-boundary crossing under general scope

A claim falling within this set is not authority. It is an authority failure event and is recorded as such.

---

## 26. Authority Across Versions

Authority Law versions are immutable upon issuance. A transition is evaluated under the Authority Law version in force at the time of exercise.

Subsequent Authority Law versions do not retroactively legitimize or invalidate prior exercises, except where reconstruction reveals a failure class that was already a failure under the prior version.

Cross-version compatibility is governed by explicit migration records. Migration is itself an authority-bearing action governed by canon-touch authority.

---

## 27. Long-Term Authority Continuity

Authority records must remain reconstructable across operational lifetimes longer than the actors who created them.

Continuity requires:
- durable storage of authority declarations
- durable storage of delegation chains
- durable storage of review records
- durable storage of workflow state at exercise
- record formats that admit reconstruction without the original tooling

Authority that depends on living testimony is not continuous and is not governed.

---

## 28. What Must Never Change

The following are immutable for the lifetime of Authority Law as a governed surface:

- Authority must be explicitly declared.
- Authority must be operationally bounded.
- Authority must be replayable from the record.
- Authority must be reconstructable without testimony.
- Authority must be validated at transition time.
- Implicit authority does not exist.
- Autonomous authority claims are forbidden.
- Delegation cannot widen scope.
- Reviewer conflict invalidates review.
- A system that cannot reconstruct legitimacy does not possess governed authority.

---

## 29. What May Evolve

The following may evolve under canon-touch authority and successor versions of Authority Law:

- the enumeration of authority failure classes
- the bounds of specific scopes (canon-touch, security-boundary, release)
- the format of authority records, provided reconstruction remains possible
- the specific reviewer-conflict definitions, provided they only narrow legitimacy
- escalation procedures, provided they remain explicit and recorded
- migration procedures across Authority Law versions

Evolution must not weaken P-AU-1 through P-AU-7. Evolution that weakens an immutable principle is not evolution — it is replacement, and requires the explicit retirement of this version.

---

## 30. Final Law

Authority is legitimate only when explicitly declared, operationally bounded, replayable from the record, compatible with workflow state, compatible with role scope, reconstructable without testimony, and validated at transition time.

Authority that does not satisfy these conditions is not authority. It is operational power without governance, and it has no standing in this protocol.

A system that cannot reconstruct why an authority transition was legitimate does not possess governed authority.

Authority Law exists to convert operational power from assumption into reconstructable legitimacy.

Without Authority Law: governance collapse, hidden power expansion, unreconstructable approval chains, unverifiable release legitimacy, implicit operational control, audit ambiguity, replay-invalid governance.

This is the final law of authority for v0.1.

---

END AUTHORITY LAW v0.1
