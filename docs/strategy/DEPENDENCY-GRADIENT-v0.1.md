# DEPENDENCY GRADIENT v0.1
## How Governed Cognition Becomes Infrastructure

**Status:** v0.1 — strategic specification, non-normative.
**Scope:** Defines the operational path by which Intellagent / WiseOrder transitions from project to dependency.
**Companion documents:** SPEC.md (canon), CONFORMANCE.md (vectors), ARCHITECTURE-PRESSURE-TESTS-v0.1.md, CANONICAL-RELEASE-v0.1.md, CROSS-LANGUAGE-CANONICALIZATION-v0.1.md.

> **Core thesis.** Infrastructure is not adopted because it is interesting. Infrastructure is adopted because removing it becomes operationally expensive.

---

## 1. Purpose

This document specifies the dependency gradient: the ordered sequence of operational properties that move a governed cognition system from "available" to "depended upon." It does not redesign architecture, add primitives, add cognition classes, or modify runtime or canonicalization semantics. It describes the path by which the existing system becomes load-bearing for systems outside it.

The gradient is one-directional. Each step compounds the prior step. Skipping steps does not accelerate adoption — it forfeits it.

---

## 2. Why Most AI Systems Fail To Become Infrastructure

Most AI systems are interesting before they are reliable. They optimize for capability demos, novelty, and surface behavior. They do not produce:

- bit-identical outputs across runs
- reproducible refusals
- replayable autonomous decisions
- audit chains that survive operator change
- behavior contracts that survive version change

Without those, no downstream system can be built on top of them. They remain consumed; they are never depended upon. When the model changes, the integration breaks. When the prompt changes, the audit breaks. When the vendor changes, the workflow breaks. Organizations route around such systems rather than into them.

A system becomes infrastructure when other systems' correctness depends on its behavior, and when that dependency is safe to take.

---

## 3. Trust Accumulation

Trust is accumulated, not declared. It accumulates through repeated, observed, identical behavior under varied conditions. The accumulation has a fixed order:

1. The system runs.
2. The system runs the same way twice.
3. The system runs the same way under load.
4. The system runs the same way across versions.
5. The system runs the same way across implementations.
6. The system runs the same way across operators.

Each rung is a precondition for the next. Marketing cannot substitute. The trust curve is set by the slowest rung the system has actually cleared, not by the rung it claims.

---

## 4. Dependency Formation

Dependency forms when a downstream system embeds an assumption about the upstream system's behavior into its own correctness. Once embedded, removal of the upstream system requires the downstream system to re-derive the guarantee internally — at higher cost and lower assurance.

Dependency formation requires three properties simultaneously:

- **Stable interface.** The contract does not move under the consumer.
- **Stable semantics.** The same input produces the same output.
- **Stable failure mode.** When it breaks, it breaks the same way.

A system with stable interface but unstable semantics is worse than no system at all, because consumers build around the false contract before discovering it.

---

## 5. Replay As Infrastructure

Replay is the foundation. A system whose past decisions cannot be re-executed bit-identically is not auditable, not debuggable, not certifiable, and not safe to depend on. Replay converts a runtime decision into a durable artifact: the decision, plus the inputs, plus the canonicalization, plus the version of every component that produced it, can be re-run and must produce the same result.

Replayability is what makes the system survive the operator who built it. Without replay, knowledge of why a decision was made lives in people. With replay, it lives in the artifact. Institutions can only depend on artifacts.

---

## 6. Auditability As Infrastructure

Auditability is replay plus chain. Each decision references the prior decision; the chain references the canonical inputs; the inputs reference their canonicalization; the canonicalization references its version. The chain is verifiable end-to-end without trusting any party in the middle, including the runtime that produced it.

Audit is not a logging feature. It is the property that allows a regulator, a counterparty, or a successor team to reconstruct the system's behavior without negotiation. Once an organization has audited Intellagent end-to-end and the audit succeeded without escalation, the cost of switching to a non-auditable alternative becomes the cost of re-auditing the alternative — which exceeds the cost of staying.

---

## 7. Authorization Guarantees

Every governed action carries an authorization. The authorization specifies who or what permitted the action, under what scope, for what duration, with what revocation path. The runtime refuses any action whose authorization is missing, expired, or out-of-scope, and the refusal is itself a recorded, replayable artifact.

Authorization is not access control. Access control gates entry. Authorization gates each act of consequence and binds it to a justification durable enough to survive a postmortem. Systems without per-action authorization cannot be trusted with autonomous behavior.

---

## 8. Refusal Reliability

A refusal is a positive output, not an absence. A reliable refusal is:

- deterministic — the same disallowed input refuses the same way every time
- replayable — the refusal artifact contains the reason, not just the decision
- inspectable — the refusal cites the rule, scope, and version that produced it
- stable — the refusal does not silently become an allow under load, version change, or operator change

Organizations adopt systems whose refusals they trust more than they adopt systems whose acceptances they admire. A refusal that drifts is more dangerous than a capability that lags.

---

## 9. Deterministic Continuity

Deterministic continuity is the property that the system behaves identically across the boundaries that destroy other systems: process restart, host migration, version upgrade, language port, operator handoff. Determinism is not "the model is deterministic." Determinism is: every component on the path from input to action is pinned, versioned, replayable, and capable of producing bit-identical output from bit-identical input under any of the above transitions.

Continuity is what allows an organization to hire its second operator. Without it, the system is a single-operator artifact and cannot scale into infrastructure.

---

## 10. Interoperability Gravity

A system gains gravity when more than one independent implementation conforms to the same canonical specification and passes the same vector suite. At that point, the specification — not any one implementation — becomes the contract. Consumers build against the contract; implementations compete on operational properties; the cost of leaving the ecosystem is the cost of replicating the contract.

Gravity is created by conformance, not by reach. One language with a published vector suite and a second-language implementation that passes it produces more gravity than ten languages with bespoke behavior.

---

## 11. Why Conformance Matters

Conformance is the mechanism by which the gradient survives multiple implementations. A vector suite encodes the expected behavior; an implementation either passes the vectors or it does not. There is no negotiation, no "spirit of the spec," no implementation-defined behavior outside what the spec explicitly marks as such.

Conformance moves trust from the implementation to the specification. Once trust lives at the spec layer, the implementation becomes substitutable. Substitutability is the precondition for ecosystem formation: consumers can adopt without vendor lock, which paradoxically increases adoption of every conformant implementation.

---

## 12. Governance As Runtime Utility

Governance is not a compliance overlay. It is a runtime utility: a function the system performs on every action, in band, with the same latency budget as the action itself. Governance produces three runtime artifacts on every act of consequence:

- the authorization that permitted it
- the policy that scoped it
- the refusal path that would have blocked it

When governance is a runtime utility rather than a review process, the system can be trusted with autonomous behavior at higher consequence levels. Governance value scales with consequence; at low consequence it is overhead, at high consequence it is the only reason the system is allowed to run.

---

## 13. Operational Legibility

Operational legibility is the property that an operator who has never seen the system before can determine, within minutes:

- what the system did
- why it did it
- what it would have refused to do
- what version of every component produced the behavior
- how to reproduce it

Legibility is not documentation. It is a property of the artifacts the system emits. Systems that require tribal knowledge to operate cannot be depended on across organizational boundaries.

---

## 14. Failure Transparency

Failures must be:

- visible at the moment they occur
- attributable to a specific component, version, and input
- reproducible from the recorded artifact
- distinguishable from refusals (a refusal is correct behavior; a failure is not)

Hidden failures destroy the gradient instantly. A single silent mis-execution costs more trust than a hundred loud refusals. Organizations depend on systems whose failure modes they have already seen, characterized, and rehearsed; they do not depend on systems whose failures they have only been promised will not occur.

---

## 15. Institutional Trust Requirements

For an institution — not an individual — to depend on the system, the following must be true:

- the spec is published, versioned, and dated
- the conformance vectors are published and reproducible
- at least one reference implementation is auditable end-to-end
- the canonicalization is documented with every escape, ordering, and normalization rule
- replay is verifiable without contacting the originating runtime
- the failure history is recorded and not silently rewritten

Institutional trust is not a stronger form of individual trust. It is a different shape of trust: it requires durability across personnel, time, and counterparty change. The gradient is built for institutions; individuals adopt earlier and tolerate more.

---

## 16. Integration Friction Reduction

Adoption is gated by integration cost. The gradient lowers integration cost in a fixed order:

1. A specification a reader can finish in one sitting.
2. A vector suite an implementer can run unmodified.
3. A reference implementation an integrator can read straight through.
4. A canonicalization that produces the same bytes in every conformant tongue.
5. An artifact format that survives transport without re-canonicalization.

Each reduction compounds. A reader who finishes the spec in one sitting is the precondition for the implementer who runs the vectors; the implementer is the precondition for the integrator; the integrator is the precondition for the institutional buyer.

---

## 17. Why Demos Matter

Demos matter because they are the smallest unit of pressure-tested behavior an outside observer can verify without trusting the project. A demo that runs, refuses correctly, replays bit-identically, and emits a verifiable audit chain is worth more than any volume of claims. Demos do not sell — they remove a class of doubt that no document can remove.

A demo is infrastructure-grade when an outside operator can run it, break it, and produce the same break twice. Demos that cannot be broken in public are not demos; they are advertisements.

---

## 18. Why Stability Matters More Than Velocity

Velocity attracts early adopters. Stability retains institutions. The two are in tension: every breaking change resets the trust accumulation curve. Beyond the early phase, the cost of a breaking change is not the engineering cost of the change — it is the cost of every downstream consumer re-validating their dependency.

The correct posture past v0.1 is: small surface, stable surface, additive evolution, deprecation with overlap. Velocity inside the surface is unconstrained; velocity at the surface is rationed.

---

## 19. Adoption Sequence

The adoption sequence is fixed:

1. **Read.** A technically literate outside reader finishes the spec and understands what the system does.
2. **Run.** The reader runs the reference implementation and the conformance vectors locally and observes bit-identical results.
3. **Replay.** The reader replays a recorded decision and observes that the replay matches the original.
4. **Refuse.** The reader constructs a disallowed input and observes a deterministic, replayable refusal.
5. **Embed.** The reader integrates the system into a non-trivial workflow that contains at least one consequential action.
6. **Audit.** A second party — not the integrator — audits the workflow's decisions end-to-end and the audit succeeds.
7. **Depend.** A downstream system encodes correctness assumptions about the workflow into its own operation.
8. **Replace fear.** The organization measures the cost of removal and finds it exceeds the cost of staying.

Steps cannot be skipped. Step 8 is the threshold of infrastructure status.

---

## 20. Reference Implementation Strategy

The reference implementation is not a product. It is the operational definition of the spec: when a vector ambiguity arises, the reference implementation's behavior — together with the spec text — is the resolution. The reference implementation must be:

- minimal — every component justified by the spec
- readable — straight-through, no clever indirection
- conformant — passes its own vectors without exception
- portable — its canonicalization can be reproduced byte-for-byte in another language
- observable — every decision emits the artifacts the spec requires

A second, independent implementation in a different language — passing the same vectors — is the event that converts the reference implementation from "the implementation" into "an implementation." That event is the formal beginning of ecosystem formation.

---

## 21. Ecosystem Formation

An ecosystem forms when:

- the spec has more than one implementation
- the vectors are run by parties unaffiliated with the spec author
- the artifacts produced by one implementation are consumed by another implementation without translation
- the failure history of each implementation is observable across the ecosystem
- consumers choose implementations on operational properties, not on identity

Ecosystem formation is the point at which the spec outlives its author. From that point, the dependency gradient is no longer carried by the project — it is carried by the network of conformant systems.

---

## 22. Protocol Gravity

Protocol gravity is the asymmetry between joining the protocol and leaving it. Joining costs one integration. Leaving costs every integration the consumer has built on top, every audit trail anchored in the protocol's canonicalization, every counterparty whose systems also conform. Gravity is not lock-in; lock-in is artificial. Gravity is the natural consequence of having built correctly: the protocol is the cheapest place to do the work.

Protocols accumulate gravity through correctness, not through ownership. The owner of a protocol with gravity has a smaller share of the value than any one consumer, and that is the property that allows the gravity to grow.

---

## 23. What Creates Switching Costs

Legitimate switching costs are created by:

- audit histories anchored in the protocol's canonicalization
- replay artifacts that can only be verified by a conformant runtime
- governance policies expressed in the protocol's authorization vocabulary
- downstream systems whose correctness assumes the protocol's refusal semantics
- counterparty integrations that conform to the same vectors

These are switching costs the consumer chose by building correctly. They are not extracted; they are accrued. A protocol whose switching costs come from any other source — proprietary formats, hidden behavior, undocumented escape hatches — is not building gravity. It is building a trap, and the market eventually routes around traps.

---

## 24. What Destroys Trust

The following destroy trust faster than any feature can rebuild it:

- a silent change to canonicalization
- a refusal that becomes an allow without a version bump
- a replay that no longer reproduces
- an audit chain that cannot be verified without the originating runtime
- a vector that passes in one release and fails in the next without spec change
- a failure mode discovered by a consumer rather than disclosed by the project
- a public claim that contradicts an observable behavior

Each of these is recoverable individually with a public correction. Two simultaneously, or a pattern, are not recoverable. The gradient assumes the project will treat trust as the most expensive resource it manages, because it is.

---

## 25. Anti-Hype Requirements

The project must, at every layer, refuse:

- AGI rhetoric
- consciousness claims
- mythology framing in technical documents
- speculative market sizing
- enterprise claims unsupported by named, contactable references
- adoption numbers without methodology
- benchmarks without reproducibility instructions
- comparisons without runnable evidence

Hype is not a marketing failure. It is a trust failure. Every hype claim that the protocol cannot back up with an artifact reduces the credibility of every artifact the protocol can back up. The anti-hype posture is not modesty; it is operational hygiene.

---

## 26. Long-Term Infrastructure Strategy

The long-term strategy is single-purpose: be the cheapest, most reliable, most auditable place to perform governed cognition. Not the most capable. Not the most novel. The cheapest, most reliable, most auditable. Capability and novelty are downstream of that posture; reversed, they undermine it.

The strategy compounds because each year of stable behavior makes the next year of behavior cheaper to trust. A protocol that has been stable for five years requires no marketing. A protocol that has been stable for ten years cannot be displaced except by a protocol willing to be stable for fifteen.

---

## 27. Known Risks

- **Premature surface freeze.** Freezing the surface before it is correct locks in error. Mitigation: explicit v0.x designation; the surface is not stable until declared stable.
- **Reference-implementation monoculture.** A single implementation lets the implementation drift from the spec. Mitigation: prioritize a second-language implementation early.
- **Vector under-coverage.** Vectors that do not exercise the canonicalization fully allow conforming implementations to diverge in production. Mitigation: vectors are added before features, not after.
- **Hype contamination from adjacent projects.** Adjacent ecosystem actors may adopt language the protocol refuses. Mitigation: the protocol's own documents are the authoritative voice; external claims are not endorsed by silence.
- **Consequence mismatch.** Adoption at low consequence does not validate the gradient. Mitigation: pressure-test demos must include at least one high-consequence path.
- **Operator capture.** Behavior that lives in a single operator's head is not infrastructure. Mitigation: operational legibility is a release criterion, not a documentation goal.

---

## 28. Non-Goals

This document does not:

- redesign architecture
- add primitives
- add cognition classes
- modify runtime semantics
- modify canonicalization behavior
- specify business model
- specify pricing
- specify go-to-market
- claim adoption that has not occurred
- forecast market size

The dependency gradient is a description of how trust forms and how dependency follows trust. It is not a sales plan.

---

## What Would Make Organizations Depend On Intellagent?

- replayable autonomous decisions — every act of consequence can be re-executed bit-identically from its recorded artifact
- governed execution — every act passes through authorization, scope, and refusal checks in band, not after the fact
- audit-chain continuity — the chain of decisions is verifiable end-to-end without trusting the runtime that produced it
- authorization guarantees — every action carries a durable, scoped, revocable authorization recorded with the action
- deterministic verification — verification of an artifact produces the same result on any conformant implementation
- reproducible failures — a failure can be re-triggered from its artifact and characterized without access to the original runtime
- refusal correctness — the same disallowed input refuses the same way under load, version change, and operator change

These are the properties that move a system from "useful" to "load-bearing." Each is testable. Each produces an artifact a second party can verify without negotiation.

---

## What Prevents Infrastructure Adoption?

- semantic drift — outputs change meaning across versions without the spec changing
- unstable replay — recorded decisions do not reproduce on re-execution
- undocumented behavior — observable behavior not described in the spec
- hidden canonicalization changes — byte-level output changes without a documented canonicalization version bump
- unstable APIs — surface changes that consumers cannot anticipate from the version number
- unverifiable outputs — artifacts whose correctness requires the originating runtime
- mythology and hype contamination — claims the system cannot demonstrate, attached to a system that otherwise could
- implementation inconsistency — multiple implementations diverging on inputs the vectors do not cover

Any one of these, sustained, prevents the gradient from forming. Two of them, simultaneously, foreclose it.

---

## What Creates Infrastructure Gravity?

- stable vectors — a vector suite that does not silently change between releases
- reproducible demos — demos an outside operator can run, break, and re-break identically
- cross-language compatibility — the same canonicalization producing the same bytes in every conformant language
- operational predictability — behavior consistent across load, host, version, and operator
- low integration ambiguity — every integration question answerable from the spec or the vectors, not from a maintainer
- reliable refusal semantics — refusals that are deterministic, scoped, and recorded
- deterministic audits — audits that produce the same finding from the same artifact, on any conformant verifier

Gravity is the absence of surprise. Each of these is a class of surprise the protocol has eliminated.

---

## What Creates Dependency?

- systems built around replay guarantees — downstream correctness assumes the upstream replay holds
- governance pipelines — workflows whose authorization vocabulary is the protocol's
- audit workflows — institutional audit processes anchored in the protocol's chain format
- verification tooling — third-party tools that verify the protocol's artifacts
- compliance integration — regulatory or contractual evidence produced as protocol artifacts
- autonomous-action boundaries — limits on autonomous behavior expressed in the protocol's refusal semantics

Dependency is the moment a downstream system's correctness statement contains a clause that begins "assuming the protocol …". Once that clause exists, removal is no longer a swap; it is a rebuild.

---

## Adoption, Trust, Integration, Operational Maturity — Exact Progressions

### Adoption progression
1. read the spec
2. run the vectors
3. run the reference implementation
4. replay a recorded decision
5. observe a deterministic refusal
6. integrate into a non-trivial workflow
7. integrate into a consequential workflow
8. encode the protocol into a downstream correctness statement
9. measure removal cost; find it exceeds retention cost
10. treat the protocol as infrastructure in budget and personnel decisions

### Trust progression
1. it ran
2. it ran twice the same way
3. it ran the same way under load
4. it ran the same way across versions
5. it ran the same way across implementations
6. it ran the same way across operators
7. it failed the same way twice
8. it refused the same way twice
9. it survived an external audit
10. an institution staked a regulated process on it

### Integration progression
1. local demo
2. scripted local integration
3. batch integration in a non-production workflow
4. live integration in a non-consequential workflow
5. live integration in a consequential workflow
6. live integration where the protocol's refusal is the safety boundary
7. live integration where the protocol's audit is the compliance evidence
8. live integration where a counterparty also conforms
9. cross-organization workflow on a shared vector set
10. cross-organization workflow on multi-implementation vectors

### Operational maturity progression
1. one operator can run it
2. two operators can run it without consulting each other
3. handoff between operators requires only the artifacts
4. on-call rotation can recover from a failure using only recorded artifacts
5. version upgrades preserve replay across the upgrade boundary
6. implementation swap preserves replay across the swap boundary
7. failure characterization is published and not silently rewritten
8. audit cadence is external, not self-administered
9. the protocol's behavior is cited in postmortems by parties who do not maintain it
10. the protocol is treated as a dependency in disaster-recovery planning

---

## Final Law

> The goal is not virality. The goal is operational indispensability.
>
> A system becomes infrastructure when organizations trust its failure behavior more than they trust anyone's marketing claims — including the project's own.

— END v0.1 —
