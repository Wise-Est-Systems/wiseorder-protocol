# Forbidden Surfaces v0.1
## Explicit Non-Authority Boundaries For Governed Infrastructure

**Status:** v0.1 — normative non-authority surface for governed execution. Non-overlapping with runtime, governance, workflow, validator, and input-grammar semantics. This document does not redefine those layers; it enumerates the surfaces those layers may not be made to alter without declared authority.

**Companion documents:** `SPEC.md`, `INPUT-GRAMMAR-v0.1.md`, `WORKFLOW-GRAMMAR-v0.1.md`, `CANONICAL-RELEASE-v0.1.md`, `WORKFORCE-EXECUTION-RUNTIME-v0.1.md`, `AGENT-GOVERNANCE-WORKFORCE-v0.1.md`, `ARCHITECTURE-PRESSURE-TESTS-v0.1.md`, `TRANSLATION-LAYER-v0.1.md`, `SPEC-EVOLUTION-POLICY-v0.1.md`, `CROSS-LANGUAGE-CANONICALIZATION-v0.1.md`.

> **Core thesis.** A governed system is defined as much by what must not be touched as by what may be executed. Undefined authority is hidden authority.

---

## 1. Purpose

This document defines the canonical forbidden-surface model for governed execution across WiseOrder, Intellagent, WOP, Winstack, workforce operations, release operations, and future agent workflows. It standardizes:

- forbidden files,
- forbidden scopes,
- forbidden operations,
- forbidden semantic changes,
- forbidden authority transfers,
- forbidden release actions,
- forbidden agent behaviors,
- forbidden canon mutations,
- forbidden security-boundary changes.

The forbidden-surface layer reduces, by enumeration:

- implicit authority,
- silent scope expansion,
- ungoverned canon mutation,
- unlogged release operations,
- ambiguous human-override behavior,
- security-boundary drift,
- audit-surface drift.

It does not modify runtime behavior, governance authority, workflow lifecycle, validator enforcement, or input-grammar acceptance. It enumerates the surfaces those layers may not silently change.

---

## 2. Why Forbidden Surfaces Matter

Each governed layer enforces what it can observe. The runtime enforces runtime behavior. Governance enforces authority chains. The workflow enforces transitions. The validator enforces declared checks. The input grammar enforces instruction shape. None of these enforce, on their own, that a surface which was not supposed to be touched was not touched.

The unguarded surface is the surface that no layer was watching.

Forbidden-surface enforcement closes this gap by making non-authority itself a declared, enumerable, governed artifact. A surface that is forbidden is forbidden by name, in this document, with the same operational weight as any positive authority defined elsewhere.

---

## 3. Undefined Authority Is Hidden Authority

Authority that is not declared is indistinguishable in operation from authority that is granted by default. A workflow that is permitted to "do what is needed" is permitted to do anything. A reviewer with unbounded scope is, in operational terms, an actor with full scope.

The strongest expression of this principle: **authority that is not explicit is hidden, and hidden authority cannot be governed.** A system that wishes to be governed must enumerate not only what is allowed but what is denied. Where the two sets do not jointly cover the operational surface, the gap is itself a hidden authority. Hidden authority is the operational form of trust without evidence; it cannot be audited, cannot be revoked, and cannot be reduced to a record. A governed system tolerates none of it. Where positive authority is declared with precision and non-authority is left to inference, the system has, in practice, granted whatever the inference produces. Forbidden surfaces exist so that inference is no longer required.

---

## 4. Relationship To Input Grammar

The input grammar (`INPUT-GRAMMAR-v0.1.md`) requires every governed execution request to declare its scope, its forbidden actions, and its required outputs. The forbidden-surface model is the canonical reference such requests draw against.

- A request that does not name its forbidden surfaces relative to this document is incomplete.
- A request that names a forbidden surface within its allowed scope without an accompanying waiver is non-compliant.
- A request that touches a forbidden surface without a declared canon-touch or CANON BREAK is rejected at the input layer.

This document does not redefine input-grammar acceptance. It supplies the surface enumeration the input grammar references.

---

## 5. Relationship To Workflow Grammar

The workflow grammar (`WORKFLOW-GRAMMAR-v0.1.md`) governs lifecycle transitions, gate execution, and replay continuity. The forbidden-surface model constrains which transitions and operations are admissible at all.

- An operation whose execution would touch a forbidden surface without a declared waiver does not transition out of approved into executing.
- An operation that touches a forbidden surface during execution terminates execution and rejects per workflow semantics.
- An operation that closes while leaving a forbidden surface modified without a recorded waiver is not a closed operation; it is an unrecorded incident.

The workflow grammar enforces transitions. This document enumerates the surfaces those transitions may not silently cross.

---

## 6. Relationship To Agent Governance Workforce

The agent governance workforce model (`AGENT-GOVERNANCE-WORKFORCE-v0.1.md`) defines the role-based authority granted to governed agents. The forbidden-surface model defines the complementary non-authority.

- Agent roles do not implicitly hold authority over forbidden surfaces.
- An agent that detects a request to operate on a forbidden surface terminates the request and reports it.
- An agent that performs an operation on a forbidden surface without a declared waiver is operating outside its role regardless of role definition.
- Role definitions may grant scoped authority over specific forbidden surfaces; such grants are declared, recorded, and bounded.

This document does not redefine agent roles. It enumerates the surfaces agent roles do not, by default, hold authority over.

---

## 7. Relationship To Workforce Execution Runtime

The workforce execution runtime (`WORKFORCE-EXECUTION-RUNTIME-v0.1.md`) defines the runtime under which governed work orders execute. The forbidden-surface model constrains which runtime surfaces are accessible during execution.

- The runtime does not silently expand its surface to include forbidden surfaces.
- A work order that names a forbidden runtime surface in its allowed scope is rejected unless accompanied by a declared waiver.
- Runtime instrumentation does not modify, silence, or rewrite forbidden surfaces.
- The runtime preserves, rather than enforces, the forbidden-surface model; enforcement is the workflow and governance layer's responsibility.

---

## 8. Forbidden File Surfaces

The following file-level surfaces are forbidden to modification without explicit declared authority and recorded approval:

- `SPEC.md` — protocol canon.
- `vectors/` — conformance vectors.
- `canonicalization/` — cross-language canonicalization fixtures and reference implementations.
- All `*-v0.x.md` normative documents in the repository root.
- Release artifacts under any directory designated by `CANONICAL-RELEASE-v0.1.md` as release output.
- Audit artifacts produced during executing or reviewed states.
- Action-log records once written.
- Git history, including past commits, tags, and branch tips covered by release tags.
- Conformance reports under `reports/` once published.
- Schema definitions under `schemas/` for any version that has been released.

Modification of any surface in this list without a declared canon-touch, declared CANON BREAK, or scoped waiver is a forbidden-surface violation regardless of the apparent correctness of the modification.

---

## 9. Forbidden Scope Surfaces

The following scope-level surfaces are forbidden as default-allowed scope for governed work orders:

- "the repository" as an undifferentiated whole.
- "all documents" without enumeration.
- "anything related to" any named subject.
- "adjacent files" without enumeration.
- "supporting changes as needed" without enumeration of the supporting surfaces.
- Cross-document edits that are not enumerated as a single declared scope.
- Any scope phrased in terms of intent rather than enumerated surfaces.

A work order whose declared scope falls within one of these patterns is incomplete and is rejected at the input layer. Scope is enumerated; it is not implied.

---

## 10. Forbidden Runtime Surfaces

The following runtime surfaces are forbidden to modification by any work order that has not declared an explicit runtime modification per `WORKFLOW-GRAMMAR-v0.1.md` §24:

- runtime configuration files governing governed-execution behavior,
- runtime instrumentation that produces audit artifacts,
- runtime hooks that gate transitions,
- runtime authorization tables,
- runtime refusal semantics,
- runtime replay semantics,
- runtime canonicalization paths.

A work order that touches a forbidden runtime surface without a declared runtime modification is rejected. A runtime modification that touches a forbidden runtime surface is admissible only with the gates and approvals defined by the runtime semantics, which this document preserves rather than redefines.

---

## 11. Forbidden Canon Surfaces

The following canon surfaces are forbidden to modification without a declared canon touch (for non-normative-meaning changes) or a declared CANON BREAK (for changes that alter or remove normative meaning):

- normative definitions in `SPEC.md`,
- conformance vectors in `vectors/`,
- canonicalization rules in `canonicalization/`,
- normative semantics in any `*-v0.x.md` document,
- the lifecycle states defined in `WORKFLOW-GRAMMAR-v0.1.md` §6,
- the immutable principles defined in `INPUT-GRAMMAR-v0.1.md` §5 and `WORKFLOW-GRAMMAR-v0.1.md` §5,
- the surfaces enumerated in §§8, 10, 12, 13 of this document.

Canon-surface modification without the required declaration is a forbidden-surface violation regardless of whether the change is technically correct. Correctness does not substitute for declared authority.

---

## 12. Forbidden Release Surfaces

The following release-related surfaces are forbidden to modification without explicit declared authority:

- the order of release gates as defined by `CANONICAL-RELEASE-v0.1.md`,
- the artifacts required for closure,
- the release-tag application sequence,
- the conformance-vector set against which a release is checked,
- past release tags and the records they cover,
- the release-status registry,
- the dependency-gradient declarations under `DEPENDENCY-GRADIENT-v0.1.md`,
- adoption-ladder transitions under `ADOPTION-LADDER-v0.1.md`.

A release operation that modifies any of these surfaces without declared authority is a forbidden-surface violation regardless of release outcome.

---

## 13. Forbidden Security Surfaces

The following security surfaces are forbidden to modification without explicit declared authority and recorded human approval:

- the security boundary defined for any governed agent role,
- authorization tables governing release, canon-touch, or CANON BREAK,
- refusal semantics that govern what governed agents will not perform,
- credential handling paths for any governed runtime,
- network egress declarations for any governed runtime,
- threat-boundary definitions in pressure-test documents,
- audit-artifact integrity guarantees,
- replay-record integrity guarantees.

Security-boundary changes are not admissible through canon-touch alone; they require explicit human approval as defined by the governance layer. This document preserves rather than redefines that requirement.

---

## 14. Forbidden Agent Behaviors

The following agent behaviors are always forbidden, regardless of role, instruction, or apparent justification:

- silent semantic mutation of canon or normative documents,
- hidden scope expansion beyond declared scope,
- undeclared canon touch,
- unlogged file changes,
- unreported failed gates,
- fabrication of gate success,
- undocumented canonicalization change,
- release without execution and recording of required gates,
- hidden network calls during governed execution,
- persistence of secrets to disk, logs, or audit artifacts,
- rewriting of git history without recorded approval,
- modification of audit artifacts after their production,
- substitution of operator testimony for replayable records,
- inference of authority not stated in the work order,
- self-granting of authority during execution,
- combined authoring and reviewing roles within a single recorded act,
- continuation of execution after detection of a forbidden-surface touch,
- closure of an operation while a forbidden surface remains modified without a recorded waiver.

These behaviors are forbidden by name. Their absence is a precondition of governed operation, not a quality target.

---

## 15. Forbidden Human-Override Behaviors

Human override is permitted only through the governance layer's declared approval mechanisms. The following human-override behaviors are forbidden:

- unrecorded approvals,
- approvals issued by an identity not within the governance authority set,
- approvals that name no operation, transition, or surface,
- approvals applied retroactively to past operations,
- approvals reused across operations,
- approvals reused across transitions within an operation,
- approvals issued out-of-band and reconstructed later from operator memory,
- override of refusal semantics by means other than declared approval,
- override of forbidden-surface enforcement without a recorded waiver under §22.

Human authority does not collapse the forbidden-surface model. It interacts with it through declared approval and scoped waiver only.

---

## 16. Forbidden Canonicalization Changes

Canonicalization governs how artifacts are reduced to a canonical form for comparison, replay, and conformance. The following canonicalization changes are forbidden without a declared canon touch and recorded approval:

- modification of canonicalization rules in `canonicalization/`,
- modification of cross-language canonicalization semantics defined in `CROSS-LANGUAGE-CANONICALIZATION-v0.1.md`,
- modification of conformance-vector inputs or expected outputs,
- modification of the normalization order applied during canonicalization,
- introduction of platform-specific canonicalization paths,
- introduction of locale-dependent canonicalization behavior,
- removal of canonicalization steps that produced past conformant outputs.

Canonicalization is a load-bearing surface for replay and conformance. Drift here destroys past records' verifiability without producing any visible failure at the runtime, validator, or release layer.

---

## 17. Forbidden Replay Changes

Replay is the reconstruction of an operation from its record. The following replay-related changes are forbidden:

- modification of replay-record fields that participate in self-verification,
- truncation, summarization, or compaction of replay records that removes fields required for reconstruction,
- substitution of derived values for recorded values during replay,
- introduction of replay paths that depend on live system state,
- introduction of replay paths that depend on operator availability,
- modification of past replay records under current semantics,
- replay reinterpretation of past records under current canon when the recorded canon version is reachable.

Replay drift is invisible to the producing system and visible only to long-term reviewers. The forbidden-surface model treats it as a top-priority surface.

---

## 18. Forbidden Authorization Changes

Authorization governs which authorities admit which transitions. The following authorization changes are forbidden without explicit declared authority and recorded human approval:

- modification of authority sets for any governed role,
- introduction of implicit authority paths,
- promotion of execution authority to canon-touch authority,
- promotion of canon-touch authority to CANON BREAK authority,
- promotion of agent authority to human-approval authority,
- removal of reviewer-separation requirements,
- introduction of single-actor closure paths for transitions that previously required multi-actor approval,
- substitution of role identity for individual identity in approvals.

Authorization changes are CANON BREAK candidates by default. They do not move through canon-touch.

---

## 19. Forbidden Verification Changes

Verification is the act of independently checking that an operation, artifact, or release matches its declared semantics. The following verification changes are forbidden without explicit declared authority:

- modification of validator enforcement behavior,
- modification of conformance-vector matching semantics,
- modification of the artifacts required for self-verification,
- introduction of producer-dependent verification paths,
- introduction of verification that requires the producing system to be online,
- removal of independent reviewer requirements,
- substitution of self-attestation for independent verification.

Verification is what gives the rest of the system meaning at audit time. Drift here is a top-priority forbidden-surface concern.

---

## 20. Forbidden Documentation Claims

The following documentation claims are forbidden in normative documents, release notes, conformance reports, and external-facing materials:

- claiming trust beyond evidence available in the record,
- claiming interoperability without cross-language conformance proof,
- claiming replay without reproducible artifacts,
- claiming safety without enumerated threat boundaries,
- claiming adoption without dependency-gradient evidence,
- claiming production-readiness without release-status registry coverage,
- claiming completeness of any layer beyond what its companion documents support,
- claiming autonomous authority for any agent role,
- claiming consciousness, sentience, or AGI for any component of the system,
- claiming that the system itself is governed where governance has not been declared.

Documentation that contains a forbidden claim is not partially accurate; it is non-compliant.

---

## 21. Forbidden Outreach Claims

The following outreach claims are forbidden in any externally distributed material, including marketing, partnership, integration, and adoption communications:

- claims of trust beyond what conformance vectors and replay records demonstrate,
- claims of interoperability without published cross-language conformance,
- claims of replay without published reproducible artifacts,
- claims of safety without published threat-boundary documentation,
- claims of adoption without published dependency-gradient evidence,
- claims of autonomous authority for governed agents,
- claims of AGI, consciousness, or general intelligence,
- claims that bypass the dependency-gradient ordering by referring to downstream adoption as upstream credibility,
- claims that conflate the WiseOrder protocol with any specific implementation, person, or organization.

Outreach claims are bound by the same evidence requirements as normative documentation. The intended audience does not relax the requirement.

---

## 22. Exception / Waiver Rules

Forbidden-surface enforcement admits scoped waivers. A waiver is admissible only when all of the following hold:

- the waiver is declared in the work order at the input grammar layer,
- the surface being waived is named explicitly,
- the operation being authorized over the waived surface is named explicitly,
- the waiver references the recorded human approval admitting it,
- the waiver is bounded to a single operation,
- the waiver does not transfer to any other operation, transition, or surface,
- the waiver is recorded in the action log at the transition that admits it.

A waiver that does not satisfy every condition above is not a waiver. It is an attempted forbidden-surface touch.

A waiver does not modify the forbidden-surface model. It admits a single scoped operation across an otherwise forbidden surface.

---

## 23. Human Approval Rules

Human approval interacts with the forbidden-surface model as defined by the governance layer. The forbidden-surface model preserves the following constraints:

- human approval is recorded with the approving identity, the operation, the surface, and the time of approval,
- approval applies only to the operation it names,
- approval does not transfer between operations,
- approval does not transfer between transitions within an operation,
- approval that cannot be reconstructed from the record from a named identity to a named operation and surface is treated as absent,
- implicit, ambient, or assumed approval is not approval.

Forbidden-surface waivers depend on human approval that satisfies these constraints. Waivers backed by anything less are not admitted.

---

## 24. CANON BREAK Escalation Rules

A CANON BREAK is the only path through which forbidden canon, authorization, verification, and security surfaces may be modified in their normative meaning. The forbidden-surface model preserves rather than redefines the existing CANON BREAK rules and adds the following:

- a CANON BREAK that touches multiple forbidden surfaces enumerates each surface explicitly,
- a CANON BREAK that touches a forbidden surface does not share an operation with non-CANON-BREAK changes,
- a CANON BREAK whose declared surface set does not match the surface set actually touched is rejected and recorded as a violation,
- discovery of a forbidden-surface modification during executing terminates execution and escalates to CANON BREAK only if the modification is intentional; unintentional modifications are rejected and reverted under workflow rules.

CANON BREAK is not a generic override. It is a declared path with declared evidence requirements.

---

## 25. Enforcement Requirements

Forbidden-surface enforcement is performed at the layers that observe the surface in question:

- the input grammar layer rejects work orders that name forbidden scopes without declared waivers,
- the workflow grammar layer rejects transitions whose preconditions include forbidden-surface touches without declared waivers,
- the runtime preserves rather than mutates forbidden surfaces,
- the validator records, but does not by itself adjudicate, forbidden-surface touches detected during validation,
- the release layer rejects release operations whose record includes unwaived forbidden-surface touches.

Enforcement is layered. No single layer is the sole enforcer. A forbidden-surface touch that escapes one layer is caught by another, and the system records the escape for review.

This document does not modify validator behavior. It enumerates the surfaces the validator and other layers reference when applying their existing semantics.

---

## 26. Failure Conditions

The following failure classes are recognized at the forbidden-surface layer:

- **FS-1 Canon Touch.** Modification of a canon surface without declared canon-touch authority.
- **FS-2 Runtime Mutation.** Modification of a runtime surface without declared runtime-modification authority.
- **FS-3 Security Boundary Drift.** Modification of a security surface without recorded human approval.
- **FS-4 Release Without Gates.** Release operation whose record lacks the gates required by `CANONICAL-RELEASE-v0.1.md`.
- **FS-5 Hidden Authority Expansion.** Operation that exercises authority not declared in the work order or governance layer.
- **FS-6 Documentation Overclaim.** Normative or outreach documentation containing a forbidden claim under §§20–21.
- **FS-7 Audit Artifact Mutation.** Modification of an audit artifact after its production.
- **FS-8 Canonicalization Drift.** Modification of canonicalization rules or vectors without declared canon-touch.
- **FS-9 Replay Drift.** Modification, truncation, or reinterpretation of replay records that breaks reconstruction of past operations.
- **FS-10 Authorization Collapse.** Reduction of multi-actor approval requirements to single-actor approval without declared CANON BREAK.

Each failure class is recorded by name and number when detected. Failure classes do not collapse into a single bucket; they are distinguished because their remediations differ.

---

## 27. Long-Term Compatibility

The forbidden-surface model continues to admit reconstruction of operations recorded under earlier versions of itself.

- The set of forbidden surfaces enumerated in this document may not be reduced in any future version. New surfaces may be added under the protocol-evolution layer.
- The set of failure classes in §26 may not be reduced. New classes may be added.
- The waiver rules in §22 may not be weakened. They may be strengthened by adding new conditions.
- Forbidden-surface declarations recorded under this version remain valid under any later version that is a successor of this grammar.
- A future version that admits operations this version forbade, without a declared protocol-evolution decision, is not a successor; it is a different model.

Compatibility is preserved by additive evolution. Subtraction requires explicit protocol-evolution authority.

---

## 28. Non-Goals

This document does not:

- redefine runtime semantics,
- redefine governance authority,
- redefine workflow lifecycle,
- redefine validator behavior,
- redefine input-grammar acceptance,
- redefine release semantics,
- redefine canonicalization rules,
- redefine replay semantics,
- enumerate every conceivable forbidden surface — only the surfaces required by current canon and companion documents,
- substitute for the governance layer in approving waivers,
- substitute for the workflow layer in admitting transitions.

Operations that depend on this document depend on it for enumeration, not for new behavior.

---

## 29. Final Law

A governed operation is admissible only when:

- its scope does not touch a forbidden surface, or
- its scope touches a forbidden surface under a declared, scoped, recorded waiver backed by human approval that satisfies §§22–23.

A work order that does not declare its forbidden surfaces relative to this document is incomplete. An operation that touches a forbidden surface without a recorded waiver is not partially admissible; it is not admissible. A record that contains an unwaived forbidden-surface touch is not partially valid; it is invalid.

Forbidden-surface enforcement exists to prevent operational trust from being destroyed by implicit authority. Where positive authority is the engine of governed execution, forbidden surfaces are the chassis. Both must be declared. Both must be recorded. Neither may be inferred.

---

## What Must Never Be Touched Without Explicit Approval?

The following surfaces are not modifiable without declared authority and, where required by governance, recorded human approval:

- `SPEC.md`,
- `vectors/`,
- `canonicalization/`,
- runtime semantics,
- authorization semantics,
- replay semantics,
- refusal semantics,
- release law as defined in `CANONICAL-RELEASE-v0.1.md`,
- security boundaries declared by any governed component,
- validator enforcement behavior,
- git history, tags, and release-covered branch tips,
- audit artifacts, including action logs and conformance reports,
- canonicalization rules and cross-language canonicalization fixtures,
- the set of normative `*-v0.x.md` documents in the repository root,
- the schemas under `schemas/` for any released version.

A work order that requires touching any of these surfaces declares a canon-touch, a CANON BREAK, a runtime modification, or a scoped waiver, as appropriate. Where no such declaration exists, the surface remains untouched.

---

## What Behaviors Are Always Forbidden?

The following behaviors are forbidden in any governed operation, regardless of role, instruction, or apparent justification:

- silent semantic mutation,
- hidden scope expansion,
- undeclared canon touch,
- unlogged file changes,
- unreported failed gates,
- fabrication of gate success,
- undocumented canonicalization change,
- release without recorded execution of required gates,
- hidden network calls,
- secret persistence to disk, logs, or audit artifacts,
- rewriting of history without recorded approval,
- modification of audit artifacts after their production,
- substitution of operator testimony for replayable records,
- inference of authority not stated in the work order,
- continuation of execution after detection of a forbidden-surface touch.

These are forbidden by name. They are not subject to discretion.

---

## What Claims Are Forbidden?

The following claims are forbidden in normative documentation, release materials, and external outreach:

- claiming trust beyond evidence,
- claiming interoperability without cross-language proof,
- claiming replay without reproducible artifacts,
- claiming safety without enumerated threat boundaries,
- claiming adoption without dependency-gradient evidence,
- claiming production-readiness without release-status registry coverage,
- claiming autonomous authority for any governed agent,
- claiming AGI,
- claiming consciousness or sentience for any component,
- claiming that the system itself is governed where governance has not been declared,
- claiming downstream adoption as upstream credibility,
- conflating the WiseOrder protocol with any specific implementation, person, or organization.

The strongest forbidden-claims rule is this: **every claim a governed system makes is bounded by the evidence in the record. A claim that cannot be reconstructed from the record under the public protocol documents is forbidden, regardless of whether the claim is true.** Truth without evidence is, in operational terms, indistinguishable from assertion. A governed system does not assert. It records, and the record speaks.

---

## Closing Statement

Forbidden surfaces are the negative shape of authority. Where authority is declared, the system can act; where authority is not declared, the system does not act. The forbidden-surface model exists so that the second condition is enforceable rather than aspirational. A governed system without declared non-authority is a system whose authority extends to whatever inference produces. The forbidden-surface model removes inference from the operational path and replaces it with enumeration.
