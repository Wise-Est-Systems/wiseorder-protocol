# INTELLAGENT + WISEORDER — Part 1: Foundations

*Front matter, abstract, scope, non-goals, core thesis, definitions.*

**Conformant to:** [`INTELLAGENT-MASTER-SPEC-STANDARD-v1.0.md`](./INTELLAGENT-MASTER-SPEC-STANDARD-v1.0.md).
**Document type:** Normative specification — split form.
**Subject release:** v0.1.0.
**Date:** 2026-05-10.

**Parts:**
- Part 1 — Foundations: [`WISEORDER-WHITEPAPER-PART-1-FOUNDATIONS.md`](./WISEORDER-WHITEPAPER-PART-1-FOUNDATIONS.md) (§2.1 TITLE → §2.6 DEFINITIONS)
- Part 2 — Mechanics: [`WISEORDER-WHITEPAPER-PART-2-MECHANICS.md`](./WISEORDER-WHITEPAPER-PART-2-MECHANICS.md) (§2.7 PRIMITIVES → §2.11 DATA STRUCTURES)
- Part 3 — Layers: [`WISEORDER-WHITEPAPER-PART-3-LAYERS.md`](./WISEORDER-WHITEPAPER-PART-3-LAYERS.md) (§2.12 CANONICALIZATION → §2.16 REFUSAL)
- Part 4 — Conformance & Release: [`WISEORDER-WHITEPAPER-PART-4-CONFORMANCE.md`](./WISEORDER-WHITEPAPER-PART-4-CONFORMANCE.md) (§2.17 CONFORMANCE → §3 STATUS)

The four parts together constitute the complete normative specification. No part is independently sufficient; each cites terms defined in others (DEFINITIONS in Part 1; INVARIANTS in Part 2). Read in order on first pass; reference any part directly thereafter.

---

# INTELLAGENT + WISEORDER

A Governed Cognition + Deterministic Verification Stack for Bounded Machine Reasoning

---

**Conformant to:** [`INTELLAGENT-MASTER-SPEC-STANDARD-v1.0.md`](./INTELLAGENT-MASTER-SPEC-STANDARD-v1.0.md).
**Document type:** Normative specification.
**State:** v1.0 — written against the v0.1.0 release of the WiseOrder Protocol and the Intellagent runtime.
**Date:** 2026-05-10.

This specification is the unified normative reference for the WiseOrder Protocol kernel, the Intellagent cognition runtime, the transformer-proposer integration layer, the governed-execution stack, the meta-laws (Trust, Replay, Validation, Authority, Correction, Forbidden Surfaces, Spec Evolution, Waiver), the grammar surface (Input, Workflow, Translation), the workforce surface (Agent Governance Workforce, Workforce Execution, Hardening, Sandbox Stress), and the conformance/interop/canonicalization surfaces.

Every claim below is reconstructable from the public release artifact bundle alone. No claim relies on private state. No claim asserts properties outside the bundle's verification surface.

---

## 2.1 TITLE

```
INTELLAGENT + WISEORDER
A Governed Cognition + Deterministic Verification Stack for Bounded Machine Reasoning
```

The system has two concentric components:

- **WiseOrder Protocol v0.1.0** — a four-class deterministic verification kernel with content-addressed audit memory and action-governance separation.
- **Intellagent v0.1** — a cognition runtime that produces transitions for the kernel to verify, with proposer/kernel/gate separation enforced at module level.

The composite is a stack, not a model. It does not generate intelligence; it bounds reasoning into verifiable transitions.

---

## 2.2 ABSTRACT

Modern machine reasoning systems produce outputs whose justification cannot be reconstructed from their record. They conflate proposal, verification, authorization, execution, and memory mutation into a single forward pass. They claim safety, alignment, and correctness without naming validators, fingerprints, or replay paths. They drift between releases without observable boundaries. They make trust claims that no reviewer can falsify mechanically.

This specification defines a stack that inverts those defaults. The WiseOrder Protocol (`SPEC.md`) is a deterministic verification kernel covering four epistemic classes: A (deterministic verification under RFC 8785 JCS canonicalization), B (instrumented empirical claims), C (protocol-bound consensus across registered attesters), and D (interpretive governance with commit-chain ordering). The kernel enforces 24 invariants across the four classes plus action governance (AG1–AG3), commit-chain semantics (CC1–CC4), canonicalization scheme (CS1–CS3), and implementation declarations (ID1–ID3). Refusal is a sealed first-class artifact, not an error.

The Intellagent runtime (`intellagent_runtime/`) is the cognition layer above the kernel. It separates proposer (which generates candidate transitions but holds no execution authority), kernel (which verifies but does not authorize), gate (which authorizes but does not execute), and audit memory (which records but does not interpret). The runtime ships at approximately 2,100 lines of standard-library Python, deterministic under pinned clock + ID source + seed + provider + prompt, with byte-identical cross-run audit memory verified live (`sha256:b71c7134…`).

The composite stack changes the primitive: from "generate output and trust the model" to "propose candidate, verify against deterministic invariants, gate against declared authority, execute under sandboxed identity, record byte-stably, refuse by default."

The system does not claim AGI, consciousness, universal correctness, or unconditional safety. It claims that every refusal is sealed, every acceptance is auditable, every authority is declared, every transition is replayable, and every claim is reconstructable from the public release bundle alone. Trust accumulates only through pressure-tested replayable continuity across time. There is no faster path.

---

## 2.3 SCOPE

This specification covers:

- The WiseOrder Protocol v0.1.0 kernel: four epistemic classes, status registry, artifact schemas, conformance vectors, implementation declarations, audit-status gating.
- The Intellagent runtime v0.1: epistemic state, audit memory, refusal store, kernel adapter, authorization gate, proposer/kernel split, runtime loop, CLI surface.
- The transformer proposer v0.1: provider abstraction (OpenAI, Anthropic, Local OpenAI-compatible, DeterministicMock), prompt construction, parsing pipeline, internal retry, refusal-aware behavior, determinism mode, replay capture, cost metadata.
- The governed-execution stack: work-order lifecycle, proposer runtime, review gate, real-agent runtime (executor), pipeline composition, OS isolation (`sandbox-exec`), resource limits (`setrlimit`), identity model.
- The meta-law surface: Trust Law (TR-1..TR-10, TP1–TP10), Replay Law, Validation Law, Authority Law, Correction Law, Forbidden Surfaces, Spec Evolution Policy, Waiver Mechanism.
- The grammar surface: Input Grammar, Workflow Grammar, Translation Layer.
- The workforce surface: Agent Governance Workforce (one-agent-one-duty), Workforce Execution Runtime, Workforce Hardening v0.2, Workforce Sandbox Stress (900 checks).
- The conformance/interop/canonicalization surfaces: 23 conformance vectors, 3 interop fixtures, 10-entry canonicalization golden corpus, three suite fingerprints, drift detection.
- The release surface: gates, reproducibility checks, artifact bundle, audit-status declarations.

This specification does NOT cover:

- Model-training procedures, model architectures, or model weights.
- Specific transformer model implementations (the Provider abstraction is the boundary).
- Hardware specifications, operating-system internals beyond the documented `sandbox-exec` and `setrlimit` interfaces, or filesystem semantics beyond POSIX.
- Network protocols, RPC, or distributed-system primitives. The runtime's default surface is single-host, single-writer, no-network.
- Multi-tenant deployment, federation, distributed audit memory, or cross-machine real-provider determinism. These are explicit deferrals.
- Cryptographic primitive design (SHA-256, RFC 8785 JCS) — these are taken as given.
- User-interface design beyond CLI subcommand surface.
- Training data, evaluation datasets, or benchmark suites beyond the in-tree conformance/evaluation/demonstration suites.
- Legal, policy, or regulatory interpretation of the trust account.

Implementation boundaries:

- The reference implementation is Python 3.10+ standard-library-only in the default path. Optional real-provider integrations require their respective SDKs.
- The OS isolation layer is macOS-`sandbox-exec`-specific in v0.1; Linux `bwrap`/seccomp parity is future work.
- Canonicalization at v0.1 is `sort_keys=True` + compact JSON UTF-8, near-equivalent to RFC 8785 JCS but not strict-JCS-conformant; the 10-entry golden corpus is the canonical implementation, not the Python encoder.

Operational assumptions:

- The host is trusted at the OS level; physical compromise is out of threat model.
- Reviewers are independent; the trust model assumes some reviewers exist.
- The release artifact bundle is published over a path the reviewer can verify (TLS, signed tags, etc. — out of this spec's scope).

Deployment assumptions:

- Single-host, single-writer at v0.1.
- No production deployment is claimed; the v0.1.0 release is for first external engineering scrutiny.
- A v0.1 deployment must include its own operator-side threat model for surfaces outside this spec (network egress if added, multi-user access if added, etc.).

---

## 2.4 NON-GOALS

This stack does NOT claim:

- Artificial general intelligence.
- Consciousness, sentience, qualia, or any first-person experiential property.
- Universal correctness across arbitrary inputs.
- Safety in arbitrary deployment contexts.
- Replacement of human judgment.
- Truth determination beyond the named classes (deterministic verification, instrumented empirical, protocol-bound consensus, interpretive governance).
- Alignment with arbitrary value systems.
- Robustness against compromise of the underlying host or cryptographic primitives.
- Cross-machine real-provider determinism. Real-provider runs are explicitly out-of-contract for byte-identical replay across hosts.
- Cross-language canonicalization at v0.1. The Python canonicalizer is internal tooling; the golden corpus is the canonical implementation; second-language ports are future work.
- Distributed audit memory, multi-writer state synchronization, or protocol federation. v0.1 is single-host, single-writer.
- Multi-tenant context scoping. v0.1 is single-tenant.
- Production deployment readiness. v0.1.0 is a first-external-engineering-scrutiny release.
- Quality of generated transitions. The proposer layer's job is to *propose*; the kernel's job is to *verify*. Transition legitimacy is mechanical; transition quality is out-of-scope.
- Resistance to adversarial proposers designed to slip past kernel verification. Adversarial-proposer detection is a research direction, not a v0.1 feature.
- Replay across versions. v0.1 trust does not auto-promote to v0.2 (TP8).
- Replay across implementations. Cross-implementation interop is class-scoped and vector-bounded; full equivalence is not claimed.
- Calibration of model confidence. Telemetry tokens (`CALIBRATION_*`) are explicitly never valid `status` values.
- Detection of every possible TR-event. The trust law surface defines ten failure classes; a TR-event outside the ten is, by construction, a failure of the trust law itself, requiring spec evolution.

These non-goals are normative. A future version that claims any of the listed forbidden properties is ipso facto a TR-7 unsupported-claim-surface event regardless of accumulated evidence (TP10).

---

## 2.5 CORE THESIS

> Modern machine-reasoning systems collapse five distinct computational responsibilities — proposal, verification, authorization, execution, and memory mutation — into a single opaque forward pass. Their outputs cannot be replayed, their refusals cannot be sealed, their authority cannot be audited, and their trust cannot be falsified.
>
> The INTELLAGENT + WISEORDER stack separates the five responsibilities into five distinct computational layers, each with declared inputs, declared outputs, declared invariants, and declared validators. A transition reaches the audit memory only if the kernel verifies it. An action executes only if the gate authorizes it. A refusal is sealed with the bytes that produced it. A run is replayable from its record alone.
>
> The primitive shift: from probabilistic continuation to *governed consequence formation*.
>
> A consequence forms only when a proposer generated it, a kernel verified it, a gate authorized it, an executor ran it under sandboxed identity, and an audit memory recorded the outcome with a content-addressed fingerprint. Anything that fails any of those gates fails closed and seals a refusal. The stack does not generate intelligence; it bounds reasoning into verifiable transitions.

The thesis is falsifiable: any reviewer who finds a transition in `intellagent_audit/` whose corresponding `RuntimeLoop.search` invocation did not pass `kernel.verify().passed == True`, OR an action without `gate.evaluate().authorized == True`, OR a refusal whose `challenge_surface_sha256` does not equal SHA-256 of the rejected transition's canonical bytes, has falsified the thesis.

The thesis is technically meaningful: it names five separations, each enforced by a named module (`proposer.py`, `kernel.py`, `authorization.py`, `runtime.py`, `memory.py`) and exercised by named tests.

The thesis is concise: thirty-one words at the primitive shift, with the rest being the construction that makes the shift verifiable.

---

## 2.6 DEFINITIONS

All terms appearing in normative sections of this specification are defined here. Definitions are operational, not metaphorical. Circular definitions are forbidden.

**Action.** A transition that mutates state outside the audit memory (e.g., spawns a subprocess, writes a file outside `intellagent_audit/`, sends a network request). An action requires both `kernel.verify().passed == True` AND `gate.evaluate().authorized == True`. Authority implications: requires registered `authorization.source_id`. Determinism implications: actions are deterministic only when their executor is deterministic; in v0.1 this is the case for the in-tree fixtures but not for arbitrary executor commands.

**Action Governance (AG).** The set of three invariants (AG1, AG2, AG3) enforcing that every action carries declared authority, that no transition self-authorizes, and that no transition is actioned without a registered source.

**Action-bearing transition.** A transition where `action != null`. Distinct from a pure cognitive transition where `action == null`.

**Audit-status.** A per-implementation declaration: `NOT_AUDITED`, `CONFORMANT`, or `FAILED`. Default `NOT_AUDITED` requires no evidence. `CONFORMANT` requires both a conformance report and an interop report, both with `overall_status: PASS`, both naming the same `protocol` and `version`. `FAILED` requires non-empty `notes`.

**Audit chain.** The hash-chained sequence of audit entries linking each `this_entry_sha256` to its predecessor's `prev_entry_sha256`. Tampering at any position is detected by `verify_chain`.

**Audit memory.** The append-only, content-addressed, commit-chained record of every transition the runtime accepts (or refuses). Implementation: `intellagent_runtime/memory.py::AuditMemory`. Mutation semantics: append-only; no in-place modification permitted. Replay semantics: the entire chain is reconstructable from the on-disk JSON entries plus the head pointer. Tamper semantics: any modification raises `ChainCorrupt`.

**Authorization.** A specific instance of authority applied to a specific action. Carries `source_id` (the policy or work order that authorized), the resolved `decision` (`authorized` / `denied`), and the optional `reason`. Verification implication: `authorization == null` on an action-bearing transition is an AG3 refusal regardless of kernel verdict.

**Authorization Gate.** The `AuthorizationGate` class in `intellagent_runtime/authorization.py`. Implements `evaluate(transition) -> AuthorizationDecision`. The gate is the only path by which an action becomes executable.

**Authority.** A declared scope under which an action is permissible. Authority is bounded (always names its scope), declared (no implicit grants), revocable (declaration creates revocation surface), auditable (every action carries its source), and never auto-promoted to trust.

**Canon.** The closed set of normative documents in the repository (SPEC.md, vectors, IMPLEMENTATIONS.md, schema files, etc.). Modification of canon outside spec-evolution-policy authorization is a forbidden surface.

**Canonicalization.** The process by which a structured artifact is reduced to a byte-stable representation. v0.1 implementation: `sort_keys=True` + `separators=(',', ':')` + UTF-8 + `ensure_ascii=False`. The canonical scheme registered for v0.1.0 is RFC 8785 JCS; the v0.1 Python encoder is a near-equivalent (the golden corpus is the canonical implementation).

**Challenge surface.** The bytes the kernel was asked to verify when it produced a refusal. Sealed in the `RefusalRecord` as `challenge_surface_sha256`.

**Class A / B / C / D.** The four epistemic regimes of WiseOrder. A: deterministic verification (kernel-recomputable). B: instrumented empirical (sources cited, contradictions surfaced). C: protocol-bound consensus (registered attesters, signature collection, threshold semantics). D: interpretive governance (alternatives + counterarguments + commit chain).

**Commit chain (CC).** The four invariants (CC1–CC4) governing Class D conduct ordering: each stage names its predecessor; the chain is connected; no stage is missing; stage order is enforced.

**Conformance.** Validator-mediated demonstration that an implementation satisfies the kernel for its declared classes. Driven by 23 vectors at v0.1.0; suite fingerprint `sha256:37d3ec45…`.

**Corpus.** The 10-entry canonicalization golden corpus pinning expected canonical bytes for v0.1.0. Fingerprint: `sha256:c95685bf…`.

**Determinism.** Byte-identical replay under pinned inputs. The v0.1 contract: pinned clock + pinned ID source + pinned seed + same Provider + same prompt → byte-identical audit memory. Live-verified cross-run hash: `sha256:b71c7134…`.

**DeterministicMockProvider.** The in-contract Provider for replay scenarios. Returns scripted responses; no network. Implementation: `intellagent_runtime/proposer_transformer.py::DeterministicMockProvider`.

**Drift.** Unexplained change in artifact bytes between commit time and review time. Categorized as TR-1 (silent drift), TR-6 (canonicalization drift), or TR-8 (release inconsistency).

**Epistemic State.** A runtime-representable cognition state containing claims (objects), uncertainty conditions (status fields), provenance references (signature SHA-256s, source URIs), and authorization constraints (the prior-state authorization head). Implementation: `intellagent_runtime/state.py::EpistemicState`.

**Epistemic Transition.** A typed object encoding a proposed change: `delta` (object additions/modifications), `authorization` (optional Authorization), `class_` (Class A/B/C/D), `proposer_id`, `metadata`. Implementation: `intellagent_runtime/transitions.py::EpistemicTransition`.

**Evidence bundle.** The corpus of reports (conformance report, interop report) attached to an implementation registration to support a `CONFORMANT` audit-status declaration.

**F-1.** The WISEATA non-JCS canonicalization friction. Resolved at v0.1.0 by class-scoped declaration: WISEATA registers Class B only.

**Fingerprint.** A SHA-256 digest over a sorted canonical representation of a suite, corpus, or artifact.

**Forbidden surface.** A behavior or modification path that is not permissible regardless of declared authority. Examples: modifying canon without spec-evolution authorization; bypassing the kernel; bypassing the gate; adding network egress to the default runtime.

**Gate.** Synonym for Authorization Gate.

**Golden corpus.** The 10-entry canonicalization test corpus shipped at v0.1.0, with pinned input + expected canonical bytes + expected SHA-256 per entry.

**Implementation declaration.** A registration in `IMPLEMENTATIONS.md` naming an implementation, its supported classes, and its audit-status. Validated by `tools/validate_implementations.py` against `schemas/implementation.schema.json` plus per-rule cross-checks.

**Interop fixture.** A typed input/output pair declaring an implementation's expected canonical artifact for a given conformance vector. v0.1 ships 3 fixtures.

**Interop manifest.** The deterministic output produced by `interop/scripts/generate_fixture_manifest.py` from a fixture. Content-addressed; suite fingerprint `sha256:74eaaa62…`.

**Intellagent.** The architectural proposal layered above WiseOrder. Defines the proposer/kernel/gate/audit/refusal separation and the runtime that enforces it.

**JCS.** JSON Canonicalization Scheme (RFC 8785). The canonical scheme registered for WiseOrder v0.1.0 (semantically; v0.1 ships sort_keys+compact as a near-equivalent).

**Kernel.** The `WiseOrderKernel` adapter class implementing per-class A/B/C/D verification. Implementation: `intellagent_runtime/kernel.py`. Contract: `verify(transition, prior_state) -> KernelVerdict`.

**Manifest.** Generated output from a fixture or executor; deterministic; content-addressed via `manifest_sha256`.

**Object store.** The state-side store of objects referenced by `EpistemicState.objects`. Implementation: `intellagent_runtime/state.py::ObjectStore`.

**Pipeline.** The end-to-end runtime: proposer → review gate → executor. Implementation: `tools/pipeline_runtime.py`.

**Proposal.** The output of a proposer; a list of candidate transitions plus per-candidate metadata.

**Proposer.** A component that generates candidate transitions. Holds no execution authority. May produce zero, one, or many candidates per call. Examples: `StaticProposer`, `ManualProposer`, `InMemoryProposer`, `TransformerProposer`.

**ProposalCandidate.** A single transition produced by a proposer plus its `provenance` (which proposer, which provider, which prompt, which seed, which timestamp).

**Provenance.** The signed origin record attached to a Class A artifact. Required field: `provenance.signature_sha256`.

**Provider.** The Transformer Proposer's underlying model interface. Four shipped at v0.1: `OpenAICompatibleProvider`, `AnthropicProvider`, `LocalOpenAICompatibleProvider`, `DeterministicMockProvider`. Implementation: `intellagent_runtime/proposer_transformer.py::Provider` (Protocol).

**Refusal.** A sealed first-class artifact recording a refused transition plus the bytes that produced it. Implementation: `intellagent_runtime/refusal.py::RefusalRecord`. Refusal is a legitimate runtime outcome, not an error.

**RefusalRecord.** The dataclass capturing a refusal: `transition_id`, `class_`, `kernel_verdict`, `gate_decision`, `candidates_rejected`, `challenge_surface_sha256`, `timestamp`, `reason_codes`, optional `provenance`.

**Replay.** Re-derivation of a run's outcome (audit memory bytes, refusal records, state files) from its record alone. Replay is binary; partial replay is not replay.

**Review Gate.** The gate runtime between proposer and executor. Implementation: `tools/review_gate_runtime.py`. Distinct from the Authorization Gate: the Review Gate is the *governed-execution layer*; the Authorization Gate is the *runtime-internal layer*.

**RuntimeLoop.** The entry-point class for the in-process runtime. Implementation: `intellagent_runtime/runtime.py::RuntimeLoop`. Contract: `search(query) -> SearchResult`.

**SPEC.md.** The WiseOrder Protocol v0.1.0 normative document. Locks the kernel invariants, the status registry, the artifact schemas, and the canonicalization scheme.

**Status registry.** The closed enumeration of valid status tokens per class. v0.1.0 lock: A: VERIFIED / TAMPERED / INVALID; B: SUPPORTED / CONFLICTED / INSUFFICIENT_EVIDENCE / INVALID; C: CONSENSUS_PENDING / VALID / FAILED / INVALID; D: CONDUCT_VALID / CONDUCT_INVALID. Telemetry tokens (`CALIBRATION_*`) are never valid `status` values.

**Suite fingerprint.** A SHA-256 over the sorted concatenation of per-entry fingerprints in a suite.

**Telemetry token.** Strings of the form `CALIBRATION_*`. Used for proposer-side calibration metrics; never valid as `status` (per SPEC.md §9).

**Transformer Proposer.** A proposer using a transformer-based Provider. v0.1 implementation: `intellagent_runtime/proposer_transformer.py::TransformerProposer`.

**Transition.** Synonym for Epistemic Transition.

**Trust account.** The accumulated operational credibility of an implementation; resets at every version boundary (TP8). Deposits are TR-event-free intervals; withdrawals are TR-events.

**TR-1..TR-10.** The ten trust failure classes. See `TRUST-LAW-v0.1.md` §10.

**TP1..TP10.** The ten immutable trust principles. See `TRUST-LAW-v0.1.md` §3.

**Vectors.** The 23 conformance test cases at v0.1.0. Each vector pins input, expected status, expected artifact fields, and the invariant the vector exercises.

**WISEATA.** A registered implementation; Class B only at v0.1 due to F-1.

**Winstack.** A registered implementation; Classes A and B at v0.1.

**WiseOrder Protocol.** The four-class deterministic verification kernel. v0.1.0 normative reference: `SPEC.md`.

**Work order.** The scoped admission unit for workforce execution. YAML-defined; identity-scoped; expiry-bounded.

**Workforce.** The `agent-governance-workforce` layer. One-agent-one-duty admission. Implementation: `tools/check_workforce.py`.

---

