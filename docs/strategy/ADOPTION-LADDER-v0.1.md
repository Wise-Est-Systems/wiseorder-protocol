# ADOPTION LADDER v0.1
## Operational Progression Toward Governed Cognition Infrastructure

**Status:** v0.1 — strategic specification, non-normative.
**Scope:** Defines the ordered operational stages by which Intellagent / WiseOrder moves from isolated protocol to trusted infrastructure dependency. Does not redesign architecture, introduce new primitives, modify runtime semantics, or specify enterprise features beyond what the existing system supports.
**Companion documents:** SPEC.md, CONFORMANCE.md, ARCHITECTURE-PRESSURE-TESTS-v0.1.md, CANONICAL-RELEASE-v0.1.md, CROSS-LANGUAGE-CANONICALIZATION-v0.1.md, DEPENDENCY-GRADIENT-v0.1.md.

> **Core thesis.** Infrastructure adoption occurs in stages. Trust accumulates through reproducible operational behavior under increasing consequence pressure.

---

## 1. Purpose

This document specifies the adoption ladder: the ordered, one-directional sequence of operational stages a governed cognition system must clear to become trusted infrastructure. It does not specify capabilities, features, market segments, or business model. It specifies the operational properties an outside party can verify at each stage, and the property each stage must produce before the next stage can begin.

The ladder is sequential. Stages cannot be skipped. Skipping a stage does not accelerate adoption — it creates a class of doubt that downstream consumers will eventually surface, at which point the ladder resets to the last stage that was actually cleared.

---

## 2. Why Adoption Is Sequential

Adoption is sequential because trust is sequential. Each stage establishes a property whose presence is the precondition for the credibility of the next property. A system that cannot reproduce its own output on the same machine cannot credibly claim to reproduce it on a different machine; a system that cannot reproduce on a different machine cannot credibly claim to reproduce in a different language; a system whose cross-language behavior is unverified cannot credibly claim ecosystem gravity.

Outside observers do not grade the ladder on the highest stage claimed. They grade it on the lowest stage actually demonstrated. Adoption stalls at the lowest unverified rung.

---

## 3. Stage 0 — Internal Determinism

**Property:** The system produces bit-identical output from bit-identical input within a single process.

**Verification:** A maintainer runs the same input twice, in the same process, and observes identical canonical output, identical refusal artifacts, and identical audit fragments.

**Exit criterion:** No nondeterministic component remains on the path from input to artifact. Every randomness source is seeded; every clock dependency is captured; every concurrent path is ordered.

**What this stage is not:** It is not a guarantee that the system is correct. It is the guarantee that the system is repeatable. Correctness is verified later; repeatability is the precondition that makes verification possible.

---

## 4. Stage 1 — Local Reproducibility

**Property:** The system produces bit-identical output from bit-identical input across separate processes on the same host.

**Verification:** Run, terminate, restart, run again. Compare canonical output, refusal artifacts, and audit fragments byte-for-byte.

**Exit criterion:** Process restart, working-directory change, environment reset, and shell change do not perturb output. Hidden process-local state has been promoted to recorded state, or eliminated.

**Failure mode this closes:** "It works in my session." A system that requires a warm process to behave consistently is not yet adoptable by a second operator on the same machine, let alone by a second organization.

---

## 5. Stage 2 — External Reproduction

**Property:** A party unaffiliated with the project clones the repository, follows the published instructions, and reproduces the canonical output and the conformance vectors without contacting the maintainers.

**Verification:** External party submits a reproduction report containing the artifact hashes they obtained. Hashes match.

**Exit criterion:** The instructions are sufficient. No undocumented step, no maintainer-only tool, no implicit environment assumption is required to reproduce. The vector suite passes from a cold clone on a clean host.

**Failure mode this closes:** "It works on the maintainer's machine." External reproduction is the first stage that requires the system to survive without the project's own context.

---

## 6. Stage 3 — Cross-Machine Stability

**Property:** Bit-identical canonical output is produced across multiple distinct hosts — different CPU architectures, operating systems, filesystem encodings, locale settings, and Python or runtime patch versions — within the supported matrix.

**Verification:** The vector suite passes on at least three independent host configurations spanning the documented support matrix. Hashes match across all of them.

**Exit criterion:** The supported matrix is published. Behavior outside the matrix is documented as out-of-scope, not silently tolerated. Within the matrix, no host property perturbs canonical output.

**Failure mode this closes:** "It works on Linux but not macOS." Cross-machine stability is the precondition for any institutional adoption, because no institution operates on a single host configuration.

---

## 7. Stage 4 — Cross-Language Stability

**Property:** A second, independent implementation in a different programming language produces bit-identical canonical output for every conformance vector. Canonicalization is byte-equal across implementations.

**Verification:** The second implementation passes the published vector suite without modification to the vectors. Artifacts produced by one implementation are consumed and verified by the other.

**Exit criterion:** The specification — not the reference implementation — is the contract. A vector ambiguity that produces divergence is resolved by amending the spec or the vectors, not by adjusting either implementation in isolation.

**Failure mode this closes:** "It works in the reference language only." A protocol with a single implementation is a project. A protocol with two conformant implementations is the beginning of infrastructure.

---

## 8. Stage 5 — Adversarial Validation

**Property:** External parties attempt, in public, to break determinism, replay, refusal, audit, or canonicalization. Successful breaks are disclosed, characterized, and fixed without silently rewriting prior artifacts.

**Verification:** A documented log of attempted breaks, their outcomes, and the resulting spec or implementation changes. The log is append-only; corrections are additive, not destructive.

**Exit criterion:** The system has survived attempted breaks across at least the four surfaces — replay, refusal, audit, canonicalization — and the failure history is publicly readable. No undisclosed break is known to the maintainers.

**Failure mode this closes:** "Nobody has tried to break it." Untested systems are not safe to depend on; they are merely unproven. Adversarial validation converts unproven into characterized.

---

## 9. Stage 6 — Operational Utility

**Property:** The system performs governed cognition that is useful in its own right — not as a demo, but as the cheapest correct way to perform a specific class of work for at least one operator.

**Verification:** The operator runs the system regularly, depends on its output, and would experience operational pain if it stopped. The pain is describable in operational terms (work that must be re-done by hand, audits that must be reconstructed, decisions that must be re-justified).

**Exit criterion:** At least one workload exists where the protocol's combination of replay, refusal, audit, and governance is the reason the operator chose it over alternatives. The choice is justifiable in operational terms, not in advocacy terms.

**Failure mode this closes:** "It is interesting but not used." A system that produces no operational dependence in its own author's workflow has no claim on anyone else's.

---

## 10. Stage 7 — Workflow Embedding

**Property:** The protocol is embedded in a non-trivial workflow that contains at least one consequential action — an action whose incorrect execution would require remediation, not just retry.

**Verification:** The workflow's correctness statement contains a clause of the form "assuming the protocol's replay, refusal, or audit behavior holds." The clause is explicit. Removing the protocol requires the workflow to re-derive the guarantee.

**Exit criterion:** The protocol is not a tool the workflow calls; the protocol is a property the workflow assumes. The boundary between the protocol's responsibility and the workflow's responsibility is documented.

**Failure mode this closes:** "It is integrated, but the workflow could replace it on a weekend." Workflow embedding is the stage at which removal cost begins to exceed retention cost for the first integrator.

---

## 11. Stage 8 — Organizational Dependency

**Property:** An organization — not an individual — depends on the protocol's behavior across personnel change, version change, and time. The dependency survives the operator who introduced it.

**Verification:** The protocol appears in the organization's runbooks, on-call procedures, audit evidence, and disaster-recovery plans. New operators are trained on the protocol's artifacts, not on the operator's habits.

**Exit criterion:** The organization's correctness, compliance, or operational continuity contains the protocol as a dependency that would require an explicit, budgeted project to remove.

**Failure mode this closes:** "One person knows how it works." Organizational dependency requires that the system survive the loss of any single person who has ever touched it. Until that is true, the dependency is on the person, not the protocol.

---

## 12. Stage 9 — Ecosystem Gravity

**Property:** Multiple independent organizations depend on the protocol; multiple independent implementations conform to the same vectors; artifacts produced in one organization are consumed by another without translation; the spec is cited by parties who do not maintain it.

**Verification:** Cross-organization workflows operate on shared vector sets. Counterparty integrations conform. Third-party tooling verifies the protocol's artifacts. Failure characterizations are published by parties unaffiliated with the project.

**Exit criterion:** The protocol's behavior is treated as a fact of the operating environment, not as a vendor relationship. Removal would require coordinated action across multiple organizations, not a single procurement decision.

**Failure mode this closes:** "It is depended on by one organization." A single-organization dependency is recoverable for that organization. Ecosystem gravity is the stage at which the protocol survives the loss of any one organization, including the one that produced it.

---

## 13. Trust Accumulation Mechanics

Trust accumulates through repeated, observed, identical behavior under varied conditions. The mechanics are fixed and external:

- trust is built by what observers see, not by what the project says
- trust is gated by the lowest unverified rung, not the highest claimed rung
- trust resets when a rung previously cleared is later violated
- trust compounds: a stage held for years is more credible than a stage held for months
- trust is portable only across the surfaces the protocol publishes; trust on undocumented behavior is operator superstition and decays without warning

The project's job is to produce verifiable artifacts at each stage and refuse to claim stages that have not produced artifacts.

---

## 14. Replay As Adoption Surface

Replay is the surface on which most adoption is decided. Before an outside party trusts a system's intelligence, they trust its repeatability. A recorded decision that re-executes bit-identically — on a different host, on a different day, with a different operator — is the most economical proof of trustworthiness the protocol can offer.

Organizations trust replay before they trust intelligence claims because replay is a property they can verify in minutes; intelligence is a property they can only verify by trusting the project. Replay converts trust from a relationship into a measurement.

---

## 15. Refusal Reliability As Trust Surface

A refusal is a positive output. A reliable refusal is deterministic, scoped, recorded, and replayable. The same disallowed input refuses the same way under load, version change, host change, language change, and operator change. The refusal artifact cites the rule, the scope, and the version that produced it.

Stable refusal behavior increases operational predictability more than any capability gain. Organizations adopt systems whose refusals they trust more than they adopt systems whose acceptances they admire — because a refusal that drifts is a hidden allow, and a hidden allow is the failure mode that ends adoption irreversibly.

---

## 16. Audit Continuity As Operational Surface

Audit continuity is replay plus chain. Each decision references the prior decision; the chain is verifiable end-to-end without trusting the runtime that produced it; the chain survives version upgrade, implementation swap, and operator handoff. An audit that requires the originating runtime is a logging feature; an audit that does not is infrastructure.

Operational dependence forms when an organization's audit evidence is anchored in the protocol's chain format. From that point, the audit history is a switching cost — not artificially imposed, but accrued by having built correctly.

---

## 17. Canonicalization As Interoperability Surface

Canonicalization is the byte-level contract that allows two implementations to agree. Every escape, ordering, normalization, and rounding rule is documented; every rule is versioned; every change to a rule is a version bump and a vector update. Bit-equality across implementations is the test; the spec is the resolution.

Interoperability reduces institutional risk because it eliminates vendor lock as a source of dependency. The dependency that remains — on the protocol itself — is on a specification multiple parties have agreed to honor, not on any one party's continued cooperation.

---

## 18. Pressure Testing As Adoption Accelerator

Pressure testing — adversarial validation, load-induced edge cases, version-transition replay, cross-language vector divergence — accelerates adoption by converting unknown failure modes into characterized failure modes. Organizations do not adopt systems with no known failures; they adopt systems whose failures they have already seen, characterized, and rehearsed.

A pressure-tested system gains adoption faster than a theoretical system because the cost of evaluating it is lower. Every documented failure with a documented recovery path is one fewer evaluation an integrator has to perform privately.

---

## 19. Why Stability Beats Feature Velocity

Velocity attracts evaluation. Stability earns dependence. The two are in tension: every breaking change resets the trust accumulation curve for every consumer who had cleared a stage with the prior behavior.

Past v0.1, the correct posture is small surface, stable surface, additive evolution, deprecation with overlap. Inside the surface, velocity is unconstrained; at the surface, velocity is rationed against the cost of forcing every downstream consumer to re-validate. Governance systems become valuable precisely when consequence increases — and consequence increases only on a stable surface, because no organization places consequential workloads on a moving target.

---

## 20. Integration Maturity

Integration maturity progresses on a fixed sequence:

1. local execution by the integrator
2. scripted local integration in a sandbox
3. batch integration in a non-production workflow
4. live integration in a non-consequential workflow
5. live integration in a consequential workflow
6. live integration where the protocol's refusal is the safety boundary
7. live integration where the protocol's audit is the compliance evidence
8. live integration where a counterparty also conforms
9. cross-organization workflow on a shared vector set
10. cross-organization workflow on multi-implementation vectors

Each step requires the prior step to have been operating without unexplained incident. Integration maturity is the per-integrator analogue of the ladder; the ladder is the protocol-wide aggregate.

---

## 21. What Organizations Actually Trust

Organizations trust:

- artifacts they can verify themselves
- behavior they have observed across personnel change
- failures they have already characterized
- contracts written into specifications they can read
- guarantees enforced by determinism, not by reputation
- counterparties who have also adopted the same contract

Organizations do not trust:

- claims unsupported by reproducible artifacts
- behavior that requires the original operator to interpret
- failure modes described only in hypothetical terms
- contracts that exist only as marketing
- guarantees enforced by the project's continued cooperation
- protocols with a single conformant implementation

The first list is what the ladder produces. The second list is what the ladder forecloses.

---

## 22. What Slows Adoption

Adoption slows when:

- the spec is longer than it needs to be, or shorter than it needs to be
- the vectors do not exercise the canonicalization fully
- the reference implementation is read as the spec instead of the spec being read as the spec
- the failure history is not published
- the support matrix is implicit
- the version policy is implicit
- the project speaks faster than it produces artifacts
- adjacent ecosystem actors attach unsupported claims and the project does not correct them

Each of these is recoverable. Sustained patterns are not. Adoption velocity is the second derivative of artifact production: it is set by how reliably the project produces the next verifiable property, not by how loudly it announces the prior one.

---

## 23. What Creates Irreversible Dependency

Irreversible dependency forms when:

- audit evidence is anchored in the protocol's chain format
- compliance attestations cite the protocol's vectors
- governance policies are expressed in the protocol's authorization vocabulary
- downstream correctness statements assume the protocol's refusal semantics
- counterparty integrations conform to the same vectors
- disaster-recovery plans treat the protocol as a dependency to be restored, not a tool to be replaced

These dependencies are irreversible not because escape is forbidden, but because escape requires reconstructing the same guarantee somewhere else, and the protocol is the cheapest place to host it.

---

## 24. Adoption Failure Conditions

Adoption fails when any of the following occur and are not corrected within a credible window:

- a recorded decision no longer replays bit-identically
- a refusal silently becomes an allow without a version bump
- canonicalization changes without a documented version transition
- the vector suite passes in one release and fails in the next without spec change
- a failure mode is discovered by a consumer rather than disclosed by the project
- a public claim contradicts an observable behavior
- a second implementation diverges on a vector and the divergence is resolved by adjusting the vector to match one implementation rather than amending the spec

Any single occurrence is recoverable with a public correction. Two simultaneously, or a pattern, end the adoption curve for the affected stage. The ladder resets to the last stage whose property is still demonstrably true.

---

## 25. Premature Scaling Risks

Premature scaling is the attempt to occupy a higher rung than the protocol has actually cleared. Specific risks, in order of severity:

- **Premature surface freeze.** Declaring the surface stable before it is correct locks in error and forces every later correction to be a breaking change.
- **Premature claim of cross-language conformance.** Announcing a second implementation before its vectors pass forces a public retraction and resets cross-language trust to zero.
- **Premature claim of organizational dependency.** Citing a dependent organization before the dependency has survived personnel change misrepresents the trust stage and is contradicted the moment the operator who built the integration leaves.
- **Premature ecosystem framing.** Speaking as if the protocol has gravity it has not yet earned attracts evaluators who measure the gap and propagate the gap as the protocol's defining property.
- **Premature consequence loading.** Placing high-consequence workloads on a stage that has not survived adversarial validation is the failure mode that produces the irrecoverable incident — the one that ends adoption permanently for the affected class of consumer.

The most dangerous of these is premature consequence loading, because it is the only one whose failure cannot be corrected by retraction. The other premature claims damage credibility; premature consequence loading damages a counterparty.

---

## 26. Anti-Hype Constraints

The ladder is incompatible with:

- AGI rhetoric
- consciousness claims
- mythology framing in technical documents
- speculative market sizing
- enterprise claims unsupported by named, contactable references
- adoption numbers without methodology
- benchmarks without reproducibility instructions
- comparisons without runnable evidence
- futurism in any document the protocol publishes as authoritative

Hype is a trust failure, not a marketing failure. Every unsupported claim reduces the credibility of every supported claim. The anti-hype posture is the protocol's primary defense of its own artifacts.

---

## 27. Known Unknowns

- The cadence at which a second-language implementation can be produced and kept in lockstep with the reference implementation under spec evolution.
- The class of canonicalization edge cases the current vector suite under-exercises.
- The behavior of the protocol under sustained load that exceeds the conditions of the published pressure tests.
- The failure modes that emerge only after multiple consecutive version transitions on a long-lived audit chain.
- The failure modes that emerge only across multiple independent implementations operating concurrently on a shared workflow.
- The operator-handoff failure modes that will only surface the first time the original operator is unavailable during an incident.

Each of these is a stage the ladder will encounter. None of them can be claimed cleared until they have been encountered.

---

## 28. Non-Goals

This document does not:

- redesign architecture
- introduce new primitives
- introduce new runtime semantics
- introduce speculative enterprise features
- specify business model, pricing, or go-to-market
- claim adoption, integration, or dependency that has not occurred
- forecast scale, market share, or organizational uptake
- describe customer relationships that do not exist

The ladder is a description of the operational stages by which adoption occurs. It is not an adoption plan. It does not promise that the stages will be reached; it specifies the order in which they must be reached if they are reached.

---

## What Must Exist Before Public Dependence?

- stable vectors — a vector suite that does not silently change between releases, with every change tied to a documented spec or canonicalization version transition
- reproducible replay — a recorded decision re-executes bit-identically on any conformant runtime within the supported matrix
- deterministic refusal — the same disallowed input refuses the same way under load, version change, host change, and operator change
- canonicalization continuity — every escape, ordering, normalization, and rounding rule documented and versioned; bit-equality preserved across implementations
- cross-machine verification — the vector suite passes on at least three independent host configurations spanning the documented support matrix
- stable release semantics — every release carries a version policy that lets a downstream consumer predict whether their integration will continue to function
- documented failure boundaries — the support matrix is explicit; behavior outside it is out-of-scope, not silently tolerated

Public dependence is responsible only when each of these is demonstrably true. Inviting dependence before they are true is the failure mode that ends an adoption curve.

---

## What Creates Operational Trust?

- same replay on multiple hosts — bit-identical canonical output across the documented support matrix
- deterministic audits — the same artifact produces the same audit finding on any conformant verifier
- reproducible failures — a failure can be re-triggered from its recorded artifact and characterized without access to the originating runtime
- stable refusal semantics — refusals that do not drift across versions, hosts, languages, or operators
- pressure-tested transitions — version upgrades, implementation swaps, and operator handoffs preserve replay across the transition boundary
- transparent limitations — the support matrix, the known failure modes, and the un-cleared stages are published, not implied

Operational trust is the absence of surprise across the surfaces an operator must cross to use the system. Each item above eliminates a class of surprise.

---

## What Prevents Adoption?

- semantic drift — outputs change meaning across versions without a documented spec change
- unstable releases — the version number does not predict whether downstream integrations will survive the upgrade
- unverifiable outputs — artifacts whose correctness requires the originating runtime
- hidden runtime behavior — observable behavior not described in the spec
- undocumented canonicalization changes — byte-level output changes without a documented canonicalization version bump
- replay instability — recorded decisions that do not reproduce on re-execution
- inconsistent refusal behavior — the same disallowed input refuses differently across versions, hosts, languages, or operators

Each of these reads, to an outside evaluator, as evidence that the protocol cannot yet hold the rung it claims. Evaluators do not file objections; they exit the evaluation. The cost of these failure modes is invisible — adoption that did not occur, and that the project will not be told about.

---

## What Creates Infrastructure Dependency?

- audit workflows built on replay — the audit's correctness assumes the protocol's replay holds
- compliance systems anchored to verification — regulatory or contractual evidence is produced as protocol artifacts and verified by conformant verifiers
- governance pipelines — workflows whose authorization vocabulary is the protocol's
- deterministic evidence trails — chains of decisions that survive operator and version change without re-derivation
- interoperable runtime guarantees — the protocol's behavior is the same on every conformant implementation in the integrator's environment
- operational predictability — the system behaves the same way today, tomorrow, and after the next upgrade, on every host in the matrix

Infrastructure dependency forms when the integrator's correctness, compliance, or operational continuity contains a clause that begins "assuming the protocol …". From that point, removal is no longer a swap; it is a rebuild.

---

## Exact Progressions

### Trust progression
1. it ran
2. it ran twice the same way in one process
3. it ran the same way across processes on one host
4. it ran the same way across hosts in the support matrix
5. it ran the same way across implementations in different languages
6. it ran the same way under adversarial conditions
7. it failed the same way twice
8. it refused the same way twice
9. it survived an external audit
10. an institution staked a regulated process on it

### Operational progression
1. one operator can run it
2. two operators can run it without consulting each other
3. handoff between operators requires only the artifacts
4. on-call rotation can recover from a failure using only recorded artifacts
5. version upgrades preserve replay across the upgrade boundary
6. implementation swaps preserve replay across the swap boundary
7. failure characterization is published and not silently rewritten
8. audit cadence is external, not self-administered
9. the protocol is cited in postmortems by parties who do not maintain it
10. the protocol is treated as a dependency in disaster-recovery planning

### Integration progression
1. local execution by the integrator
2. scripted local integration in a sandbox
3. batch integration in a non-production workflow
4. live integration in a non-consequential workflow
5. live integration in a consequential workflow
6. live integration where the protocol's refusal is the safety boundary
7. live integration where the protocol's audit is the compliance evidence
8. live integration where a counterparty also conforms
9. cross-organization workflow on a shared vector set
10. cross-organization workflow on multi-implementation vectors

### Dependency progression
1. the integrator uses the protocol because it is convenient
2. the integrator uses the protocol because its alternatives are more expensive
3. the integrator's workflow contains a clause assuming the protocol's behavior
4. the integrator's audit history is anchored in the protocol's chain format
5. the integrator's compliance evidence is produced as protocol artifacts
6. the integrator's governance policy is expressed in the protocol's authorization vocabulary
7. the integrator's counterparty also conforms
8. the integrator's organization treats the protocol as a budgeted dependency
9. the integrator's industry references the protocol in shared workflows
10. the protocol is treated as a property of the operating environment, not a vendor relationship

### Maturity progression
1. internal determinism
2. local reproducibility
3. external reproduction
4. cross-machine stability
5. cross-language stability
6. adversarial validation
7. operational utility
8. workflow embedding
9. organizational dependency
10. ecosystem gravity

---

## 29. Final Law

> A protocol is not infrastructure because people believe in it. It becomes infrastructure because organizations operationalize around it.
>
> The ladder is climbed in order. Skipping a rung does not raise the protocol; it lowers the credibility of every rung above it. The lowest unverified rung is the protocol's actual stage, regardless of what is claimed.

— END v0.1 —
