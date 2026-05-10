# INTELLAGENT v0.1
## Canonical Release

**Release tag:** `v0.1.0`
**Date of freeze:** 2026-05-06.
**Repository:** [`wiseorder-protocol`](.)
**Prerequisite reading:** [`SPEC.md`](./SPEC.md), [`INTELLAGENT-RUNTIME.md`](./INTELLAGENT-RUNTIME.md), [`INTELLAGENT-PROPOSERS.md`](./INTELLAGENT-PROPOSERS.md), [`RELEASE-STATUS-v0.1.md`](./RELEASE-STATUS-v0.1.md), [`RELEASE-CHECKLIST-v0.1.md`](./RELEASE-CHECKLIST-v0.1.md).

This is the canonical public technical release statement for Intellagent v0.1. Read this first.

---

## 1. Release Statement

Intellagent v0.1 is released under tag `v0.1.0` on 2026-05-06.

The release contains:

- WiseOrder Protocol v0.1.0 ([`SPEC.md`](./SPEC.md)) — the governance kernel.
- Intellagent Runtime v0.1 ([`intellagent_runtime/`](./intellagent_runtime/)) — a single-host Python state machine over the kernel.
- 23 conformance vectors ([`vectors/`](./vectors/)) — the law set the kernel implements.
- 3 interoperability fixtures ([`interop/fixtures/`](./interop/fixtures/)) — fixture-level F-1 enforcement.
- A reference transformer proposer integration ([`intellagent_runtime/proposer_transformer.py`](./intellagent_runtime/proposer_transformer.py)) with four provider implementations.
- 113 pytest tests covering protocol, runtime, proposer, CLI, conformance, and interoperability.
- A 10-demo public demonstration suite ([`INTELLAGENT-DEMOS.md`](./INTELLAGENT-DEMOS.md)).

Architecture is locked. Vectors are sealed. Reports are byte-deterministic. The release is offered for first external engineering scrutiny.

---

## 2. What Intellagent Is

Intellagent is a governed cognition runtime architecture that separates **proposal**, **verification**, **authorization**, **execution**, and **memory** into distinct computational layers:

- **Proposal.** A proposer (static, manual, transformer, retrieval, symbolic, ensemble) emits zero or more candidate epistemic transitions. Proposers have no authority. Their output is disposable.
- **Verification.** A kernel checks each proposed transition against the regime-specific invariants of WiseOrder Protocol v0.1.0. The kernel is deterministic, narrow, and immutable within a protocol version.
- **Authorization.** An authorization gate evaluates action-bearing transitions against a separately-declared `authorization_source` policy. Verification verdicts do not auto-authorize execution.
- **Execution.** Crossing the consequence boundary requires a transition that has both passed verification and received authorization. v0.1 is single-host.
- **Memory.** An append-only audit memory seals every committed transition under a SHA-256 commit chain. Forgetting is itself a transition. Tampering is detected on read.

Each layer is replaceable except the kernel. The kernel is the architectural floor.

---

## 3. What Problem It Addresses

Intellagent v0.1 addresses a narrow set of problems associated with deploying systems whose outputs affect reality:

1. **Confident wrong outputs reach downstream consumers** because no boundary distinguishes "this is verified" from "this is fluent."
2. **Generation and action are conflated** in transformer-driven pipelines: the same operation that produces a comment can produce a tool call.
3. **Cognitive trajectories are not auditable.** Post-hoc interpretability is the only available reading.
4. **Systems lose continuity across model updates.** Past decisions are not separable from the model that produced them.
5. **Refusal has no architectural status.** Saying "I cannot legitimately answer this" is a stylistic property of generated text, not a property of the system.

v0.1 does not claim to solve these problems for all systems. It addresses each within a specific scope: state-machine cognition over a finite kernel, on a single host, with hand-authored or transformer-emitted candidates flowing through deterministic verification.

---

## 4. Why Prediction Alone Is Insufficient

A transformer is a probabilistic continuation engine. Given a context, it samples a plausible next token. This operation is well-suited to fluent generation. It is not, by construction, suited to:

- Refusal on principled grounds.
- Preservation of contradictions as structured artifacts.
- Distinguishing "this is the next likely sentence" from "this is the next legitimate move."
- Producing an output whose verification path is itself inspectable.
- Maintaining identity across model updates.

The architectural mismatch is not a shortcoming of the transformer; it is a category mismatch. Prediction is the wrong primitive for the layer of cognition that has to be answered for. Intellagent reframes the primitive as a typed, governed, audited transition between epistemic states.

---

## 5. The Proposal / Governance Split

The runtime separates two roles by interface:

- A **proposer** suggests transitions. Proposers may be probabilistic, learned, fluent, fast, slow, expensive, cheap, or adversarial. Proposers have no authority. The same `Proposer` Protocol is satisfied by `StaticProposer`, `ManualProposer`, `InMemoryProposer`, and `TransformerProposer`.
- The **kernel** governs legitimacy. The kernel is deterministic, narrow, and class-scoped. It is the only mechanism that can extend audit memory.

Proposers are replaceable. Kernels are not. A runtime that loses its proposer entirely retains all architectural guarantees: it returns a sealed `RefusalRecord`, audit memory remains valid, no action is authorized.

Transformers operate as **bounded heuristic proposers under deterministic governance constraints.** Their fluency, confidence, and self-narrative carry zero governance authority.

---

## 6. WiseOrder Protocol

The kernel implements WiseOrder Protocol v0.1.0. The protocol classifies claims into four epistemic regimes:

- **Class A — Deterministic verification.** Statuses: `VERIFIED`, `TAMPERED`, `INVALID`. Canonicalization: RFC 8785 JCS only under v0.1.0.
- **Class B — Instrumented empirical verification.** Statuses: `SUPPORTED`, `CONFLICTED`, `INSUFFICIENT_EVIDENCE`, `INVALID`. Contradiction preservation required (`B2`).
- **Class C — Protocol-bound consensus.** Statuses: `CONSENSUS_PENDING`, `CONSENSUS_VALID`, `CONSENSUS_FAILED`, `INVALID`. Quorum semantics auditable (`C1`–`C4`).
- **Class D — Interpretive governance.** Statuses: `CONDUCT_VALID`, `CONDUCT_INVALID`. Conduct artifacts require values frame, alternatives, challenge surface, commit chain with preimages (`D1`–`D5`, `CC1`–`CC4`).

Cross-cutting invariants govern action: `AG1` (verification status MUST NOT auto-authorize execution), `AG2` (execution authorization separately governable), `AG3` (authorization source preserved as auditable metadata).

The protocol is class-scoped: implementations declare which classes they support and are conformant for those classes if every invariant, status semantic, and published vector for those classes passes. There is no global binary conformance.

---

## 7. Runtime Guarantees

Under the documented input conditions, the runtime guarantees:

1. **Kernel verification precedes every commit.** No transition reaches audit memory without `kernel.verify(transition, prior_state).passed == True`.
2. **AG1 separation between verification and authorization.** An action-bearing transition without a non-null `authorization` is rejected by the kernel. An authorized action requires the authorization gate's `evaluate(transition, prior_state).authorized == True` independently of the kernel verdict.
3. **Audit memory append-only and content-addressed.** Each entry's `this_entry_sha256` is computed over the canonical body with the self-field omitted; `prev_entry_sha256` links to the previous entry's `this_entry_sha256`.
4. **Tamper detection on read.** `AuditMemory.verify_chain` raises `ChainCorrupt` on any mismatch; the runtime fails closed.
5. **Refusal is structured.** Every search that does not satisfy the query produces a `RefusalRecord` with a non-empty challenge surface and a `challenge_surface_sha256`.
6. **State integrity on load.** `StateStore.load` recomputes `state_id` from `objects` and refuses to operate on a tampered state file.
7. **Determinism under fixed conditions.** With fixed clock, fixed ID source, and deterministic provider, two runs produce byte-identical audit memory and refusal records.

---

## 8. Deterministic Replay

The runtime is deterministic when the following are pinned:

- Clock: `intellagent_runtime.canonical.set_clock(lambda: T)` for some Unix timestamp `T`.
- ID source: `intellagent_runtime.canonical.set_id_fn(...)`.
- Proposer determinism: `TransformerProposer(..., deterministic=True)` with fixed `GenerationParams.seed` and a provider that returns `supports_seeded_sampling() == True`.

A live cross-run check on the freeze commit, with two clean tmp directories under identical inputs:

```
/tmp/demoA  audit_sha: sha256:b71c7134ef2c33ea5fcc9a3eb723efe6294ba18759ed91d1f64bdfe826107ba5
/tmp/demoB  audit_sha: sha256:b71c7134ef2c33ea5fcc9a3eb723efe6294ba18759ed91d1f64bdfe826107ba5
```

Replay is per-provider. Cross-provider replay is impossible by design and is not claimed.

---

## 9. Governed Refusal

A refusal is a sealed `RefusalRecord`:

```json
{
  "refusal_id":               "refusal-<deterministic id>",
  "query":                    "<operator text>",
  "from_state":               "sha256:<state_id>",
  "candidates_rejected": [
    {
      "candidate_id":         "<transition_id or no-candidate>",
      "regime":               "A | B | C | D | null",
      "legitimacy_failures":  ["<kernel failure string>", ...]
    }
  ],
  "challenge_surface_sha256": "sha256:<hex>",
  "refused_at":               "<ISO-8601 UTC>"
}
```

A refusal records the kernel invariants that fired, in their canonical string form. The challenge surface is content-addressed; two runs produce the same `challenge_surface_sha256` if the rejected candidates and their failure strings are identical.

Refusal is a legitimate runtime output. The CLI and `RuntimeLoop.search` exit with code `0` on refusal. A non-zero exit code indicates the runtime itself is in a bad state (`ChainCorrupt`, `StateTampered`), not that the search concluded a refusal.

---

## 10. Audit Memory

Layout:

```
intellagent_audit/
├── 0000.entry.json
├── 0001.entry.json
└── ...
```

Each entry contains: `index`, `transition`, `prior_state_id`, `resulting_state_id`, `prev_entry_sha256`, `this_entry_sha256`, `sealed_at`. The chain is verified on every read by recomputing each entry's hash and asserting `entry[i].prev_entry_sha256 == entry[i-1].this_entry_sha256`.

Audit memory is not encrypted, is not signed, and does not support deletion or rewrite in v0.1. Forgetting is achieved by a removal-transition that itself becomes a new audit entry. The full audit history is preserved.

---

## 11. Transformer Integration Boundary

The runtime's transformer integration is `intellagent_runtime/proposer_transformer.py`. It implements the existing `Proposer` Protocol; no runtime change is required to use it. Four provider implementations are included:

- `OpenAICompatibleProvider` — works with OpenAI's API and any OpenAI-compatible server.
- `AnthropicProvider` — wraps the `anthropic` SDK with assistant-message prefill.
- `LocalOpenAICompatibleProvider` — subclass for local OpenAI-compatible servers.
- `DeterministicMockProvider` — returns canned completions for tests and demos.

The integration's contract:

1. Transformer output is JSON. The proposer parses with native parsing, fenced-block stripping, and regex fallback in that order.
2. Each parsed candidate is constructed via `EpistemicTransition.from_dict`. Construction failures drop the candidate.
3. Surviving candidates are wrapped in `ProposalCandidate` records and returned to the runtime as `EpistemicTransition` objects.
4. The kernel verifies each transition independently of the proposer's identity, confidence, or self-narrative.

A transformer that produces a fluent Class A artifact with `status: VERIFIED` and `expected_digest != observed_digest` produces a candidate. The kernel computes the digest comparison and rejects on `A1`. The hallucinated transition does not reach audit memory; it appears as a recorded entry in a `RefusalRecord` if the search terminates without a legitimate alternative.

Hallucinations become **rejected transitions**, not entries in audit memory.

---

## 12. Conformance + Interoperability

| Surface | Count | Suite fingerprint |
| --- | ---: | --- |
| Conformance vectors | **23** | `vectors_suite_sha256: sha256:37d3ec45ecca12d256b7df1c02ac0f0d1474f71b68510e9475fa449b8eb1331b` |
| Interop manifests | **3** | `manifests_suite_sha256: sha256:74eaaa62271f23172232bda43ba3340543e66c46ba1e2f5e6da18d3447a6ba29` |
| Implementation declarations | **2** | both `NOT_AUDITED`; `Winstack` declared `["A","B"]`, `WISEATA` declared `["B"]` (F-1) |

Every vector exercises at least one named invariant. Every manifest is content-addressed (`manifest_sha256`). Suite fingerprints are deterministic byte digests over the sorted concatenation of per-item digests; they detect silent suite drift between runs.

Conformance is class-scoped per `CONFORMANCE.md`. **The vectors are the law.** Prose explains the protocol; vectors determine conformance. An implementation is conformant for a class if and only if every invariant, every required artifact field, every status semantic, and every published vector for that class passes.

---

## 13. Reproducibility

The release is reproducible offline on a single host.

```
git clone <repo>
cd wiseorder-protocol
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
make ci
```

Expected output (verbatim):

```
make no-pseudocode
  → OK: scanned 22 markdown file(s); no pseudocode markers found in Python code blocks.
pytest tests/
  → 113 passed in ~1s
make conformance
  → overall_status: PASS  (vectors_suite_sha256 matches committed)
make interop
  → overall_status: PASS  (manifests_suite_sha256 matches committed)
CI: documentation code standard + tooling tests + protocol conformance + interoperability all passed.
```

Editable install:

```
pip install -e .
intellagent --help        # CLI entry point resolves
```

Optional provider extras:

```
pip install -e .[openai]
pip install -e .[anthropic]
pip install -e .[all]
```

Pinned dependencies: `jsonschema==4.26.0`, `pytest>=8,<9`. No outbound network is required for the default test, conformance, interop, and demo paths.

---

## 14. Release Metrics

Live numbers on the release commit, regenerated immediately before this report:

| Metric | Value |
| --- | ---: |
| Tests | **113 / 113** passing |
| Conformance vectors | **23 / 23** passing |
| Implementation declarations | **2 / 2** passing |
| Interop fixtures | **3 / 3** passing |
| Demos runnable today | **8 / 10** (Demos 3 and 10 are documented v0.2+ extension targets) |
| Documentation Code Standard violations | **0** across **22** markdown files |
| Deterministic replay (cross-run audit hash) | **MATCH** (`sha256:b71c7134…` × 2) |
| Editable install | **OK** (`pip install -e .` succeeds; `intellagent_runtime.__version__ == "0.1.0"`) |
| CLI entry point | **OK** (`intellagent --help` resolves to all 6 documented subcommands) |
| Total runtime Python | ~2,100 LoC across 11 modules + 5 prompt fragments + 2 sample policies |
| Total tests | 113 across 12 test modules |

Run time: `make ci` completes in approximately 4 seconds on a 2024-era laptop, including conformance regeneration and interop checks.

---

## 15. Known Limitations

The following are explicit, documented scope boundaries. None are defects under the v0.1 contract.

1. **Provenance enforcement is unidirectional.** The kernel does not currently require object-level `provenance` fields on Class A artifacts. Transition-level provenance (`proposer`, `proposed_at`) is captured automatically.
2. **`B2` enforcement is unidirectional.** The kernel rejects `CONFLICTED` status with single-side observations. It does not yet reject `SUPPORTED` status with present contradictions.
3. **No `EnsembleProposer` in v0.1.** Multi-proposer search is demonstrable today via a single proposer emitting multiple candidates in one completion. First-class ensemble with multiple `Provider` backends is a v0.2+ extension target.
4. **Real-provider runs are not byte-deterministic across machines.** Provider model identity may shift silently. Determinism is per-provider, per-machine.
5. **No multi-tenant scoping.** Audit memory and refusal corpora are single-tenant in v0.1.
6. **No distributed audit memory.** v0.1 is single-host; Class C consensus across multiple writers is described in the spec but not implemented.
7. **WISEATA F-1 unresolved.** WISEATA's line-oriented canonicalization is incompatible with v0.1.0's RFC 8785 JCS lock; WISEATA is registered as Class B only.
8. **`evidence.report_sha256` helper not shipped.** Operators currently compute the combined fingerprint by hand.
9. **No GUI.** All operator interaction is CLI / Python.
10. **No PyPI / Docker publication in v0.1.** The repo ships with a working `pyproject.toml` for `pip install -e .` from a checkout.

Each item has a clear v0.2+ resolution path. None blocks the v0.1 release.

---

## 16. Non-Goals

The release explicitly does not claim, demonstrate, or imply:

- **AGI.** No demo, test, vector, or runtime behavior in this release is a demonstration of artificial general intelligence.
- **A chatbot.** The runtime contains no chat surface, no conversational state, no dialog management.
- **A safety wrapper.** v0.1 is not a guardrail layer for an underlying language model. The runtime is a state machine; the language model is one possible proposer.
- **A moderation layer.** The kernel does not classify content, score harm, or filter outputs by topic. It checks structural invariants over typed transitions.
- **A claim of solved truth.** Class D explicitly governs claims that cannot be mechanically verified. The kernel governs *the form of justification* a claim's class requires; substantive correctness lives in conduct artifacts.
- **A capability benchmark.** Intellagent does not score better than transformers on capability benchmarks; that is a different question and is not the question this release answers.
- **A production system.** v0.1 is not production-graded against deployment threats outside the documented scope.
- **A formal verification.** Tests and vectors are empirical. Formal verification of kernel semantics is not in scope.

These are not modesty disclaimers. They are scope boundaries. Reviewers who treat the release as solving any of these will misread it.

---

## 17. Why v0.1 Exists

v0.1 exists for a single reason: to make the architecture's claims **mechanically inspectable** before any further extension is built on top.

Concretely:

- The kernel can be read. `intellagent_runtime/kernel.py` is roughly 310 lines of straight Python implementing per-class invariants that mirror the conformance vectors.
- The runtime can be run. `make ci` executes in ~4 seconds; demos run end-to-end in seconds; cross-run hashes match.
- The vectors can be checked. 23 vectors, each named for the invariant it exercises, each producing a per-vector SHA-256 that rolls up into a deterministic suite fingerprint.
- The transformer integration can be wired. `intellagent_runtime/proposer_transformer.py` ships four providers; the default `DeterministicMockProvider` requires no real model.
- The non-claims can be verified. Every doc has an explicit "Non-Goals" section; the release tag comes with no marketing.

If the architecture is wrong, v0.1 makes the wrongness reproducible. If it is right, v0.1 makes that reproducible too. v0.2 work depends on which.

---

## 18. External Review Expectations

Reviewers are invited to clone the repository, run `make ci`, run the public demos, inspect the suite fingerprints, and compare their results against the values in this document. The release ships with the following invariants intact:

- The `vectors_suite_sha256` matches `sha256:37d3ec45ecca12d256b7df1c02ac0f0d1474f71b68510e9475fa449b8eb1331b` after a fresh `make conformance` run.
- The `manifests_suite_sha256` matches `sha256:74eaaa62271f23172232bda43ba3340543e66c46ba1e2f5e6da18d3447a6ba29` after a fresh `make interop` run.
- `tools/demo_transformer_proposer.py` exits 0 with three `PASS` lines (Search 1, Search 2, audit chain integrity).
- `pytest tests/` reports `113 passed`.
- `make no-pseudocode` reports `0` violations across `22` markdown files.

A reviewer whose local results disagree with these has either found a defect or has not pinned the documented inputs. The next step in either case is to file a reproducer.

### What External Reviewers Should Attack

The release's claims are concentrated in seven areas. Each is the appropriate target for adversarial inspection.

1. **Determinism boundaries.** Verify the cross-run hash stability under fixed clock and seed. Probe non-deterministic surfaces: real providers, omitted clock injection, parallel I/O. Document any case where two runs with documented inputs produce non-identical audit memory or refusal records.

2. **Kernel semantics.** Read `intellagent_runtime/kernel.py` against `SPEC.md` and the vectors. Probe per-class invariants for cases not covered by the 23 published vectors (e.g., adversarial commit chains, exotic regime-status combinations, edge cases in `B2` and `D5`). File a vector for any case the kernel handles incorrectly.

3. **Replay assumptions.** Probe the determinism contract under partial inputs: missing clock pin, missing ID pin, real-provider runs with seeds. Identify the smallest set of pinned inputs sufficient for byte-identical replay. Identify the largest deviation that still produces equivalent (semantically) audit memory.

4. **Proposer/kernel separation.** Construct adversarial proposers that attempt to bypass the kernel by side channels (provider declares it has authority, candidate names itself a kernel artifact, proposer writes directly to audit memory paths). Verify the kernel rejects, the audit memory remains valid, and the architecture's promise holds.

5. **Authorization semantics.** Probe `AG1`, `AG2`, `AG3` enforcement at every touch point: kernel `verify` rejection of action-bearing transitions without authorization, gate evaluation of declared sources, action-policy preservation in audit metadata. Document any path that crosses the consequence boundary without an explicit authorization decision.

6. **Contradiction preservation.** Probe `B2` in both directions. The current kernel rejects `CONFLICTED` status with single-side observations; it does not yet reject `SUPPORTED` status with present contradictions. Confirm or contest this asymmetry, and propose vector additions that would make `B2` bidirectional under v0.2+.

7. **Refusal correctness.** Verify that every search path that should produce a refusal does produce one, and that the refusal records the correct invariants. Probe the four refusal-firing conditions documented in `INTELLAGENT-RUNTIME.md` §12.1: empty proposer output, all-rejected proposals, all action-denied proposals, exhausted iteration budget.

A successful attack against any of the seven areas changes v0.1 — by adding a vector, tightening a kernel rule, refining a determinism boundary, or amending a documented limitation. The release contract is that defects in v0.1 are findable; vectors are the form a finding takes.

---

## 19. Future Directions

Work explicitly deferred to v0.2 or beyond:

- **Bidirectional `B2`.** Reject `SUPPORTED` status with present contradictions.
- **Object-level provenance enforcement.** Require Class A artifacts to declare `provenance: {witness, at}`.
- **`EnsembleProposer`.** Multi-proposer ensembles with cost-tiered scheduling and refusal-feedback adaptation.
- **`RetrievalProposer`.** Retrieval against accumulated audit memory.
- **Refusal-corpus prompt injection.** v0.1 stores refusals; v0.2 injects them into proposer context.
- **Suite-fingerprint pinning in declarations.** `evidence.vectors_suite_sha256` field on `CONFORMANT` declarations.
- **Combined `evidence.report_sha256` helper.** Eliminate manual fingerprint computation.
- **Multi-tenant context scoping.** Per-tenant audit and refusal corpus isolation.
- **Distributed audit memory.** Class C consensus across multiple writers.
- **Adversarial-proposer benchmark suite.** Inverse benchmark: how good a proposer must be at evading the kernel before a kernel-passed but illegitimate transition occurs.

The list is finite and conservative. None of these unblock v0.1; all extend the architecture without modifying the v0.1 floor.

---

## 20. Final Statement

Intellagent v0.1 is a buildable, testable, deterministic, kernel-governed state machine over WiseOrder Protocol v0.1.0. It separates proposal, verification, authorization, execution, and memory into distinct computational layers. It treats refusal as a legitimate runtime output. It treats audit memory as append-only and tamper-evident. It treats verification as separable from authorization. It treats fluency as a ranking heuristic, not as governance authority.

The release ships with all gates green, all fingerprints stable, all demos passing, and all known limitations disclosed. The architecture is locked. The vectors are sealed. The runtime runs.

External review is invited.

---

*Canonical release artifact for Intellagent v0.1.0, frozen 2026-05-06. This document is the authoritative release statement. All other release artifacts in this repository are subordinate.*
