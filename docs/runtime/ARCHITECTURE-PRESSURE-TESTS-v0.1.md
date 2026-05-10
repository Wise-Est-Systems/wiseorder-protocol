# ARCHITECTURE PRESSURE TESTS v0.1

**Failure-Oriented Validation for Governed Cognition Systems**

---

**Status:** Draft Canon
**Owner:** Wise.Est Systems
**Adopted:** 2026-05-06
**Scope:** WiseOrder Protocol v0.1.0 + Intellagent Runtime v0.1
**Architecture status:** Locked. This document does not extend it.
**Reference baseline:** `CANONICAL-RELEASE-v0.1.md`, `SPEC.md`, `INTELLAGENT-RUNTIME.md`, `CONFORMANCE.md`

---

## Core Thesis

A cognition architecture is not validated by successful demos alone.
It is validated by surviving adversarial runtime pressure without semantic collapse.

This document is not a roadmap.
It is the falsification surface.

---

## 1. Purpose

This document defines how WiseOrder Protocol v0.1.0 and Intellagent Runtime v0.1 are intentionally stressed, attacked, and falsified.

It does not expand the architecture.
It does not introduce new primitives, classes, statuses, or runtime components.
It defines the failure regime under which the existing architecture is to be tested.

The pressure-test corpus described here is a peer artifact to the conformance vector corpus. Conformance vectors define what an implementation must accept. Pressure tests define what an implementation must reject, refuse, or audibly fail under.

A v0.1 implementation that passes every vector in `vectors/` and fails the pressure tests in this document is **not** validated. It is unvalidated under adversarial conditions.

---

## 2. Pressure Testing Philosophy

The protocol is governance.
The runtime is a search engine over governed transitions.
Both are only as strong as the worst input they continue to behave correctly under.

Pressure testing here is not chaos engineering. It is not fuzzing for crash discovery. It is structured falsification: every pressure test targets a specific invariant, a specific status semantic, or a specific authorization boundary, and predicts a specific outcome (refusal, rejection, `INVALID`, `TAMPERED`, kernel-level error, exit code 1).

Three rules govern this regime:

1. **Every pressure test names the invariant it attacks.** A test that only "tries to break things" is not a pressure test; it is unstructured noise.
2. **Every pressure test predicts a deterministic failure signature.** Either a status, an exception type, an exit code, an audit-chain divergence, or a refusal classification. If the predicted signature does not appear, the test itself is broken or the architecture has regressed.
3. **No pressure test is permitted to silently pass.** Silence under attack is the strongest possible failure signal.

---

## 3. Why Successful Demos Are Insufficient

A successful demo proves only that a cooperating proposer, a clean state graph, and an unhostile environment produced an artifact that satisfied the kernel.

It does not prove that:

- the kernel rejects malformed transitions in the same way across machines;
- the runtime refuses, rather than degrades, under adversarial proposer output;
- the audit memory is non-forgeable across replay;
- two implementations agree on canonical bytes for the same conceptual artifact;
- the authorization boundary holds when an attacker controls the proposer;
- determinism holds under perturbation of process, host, locale, or filesystem ordering.

The v0.1 canonical release reports `113/113` tests passing and a deterministic demo audit of `sha256:b71c7134…` across two runs. That is a baseline. It is not validation under pressure. Pressure tests are what move the runtime from "works" to "survives."

---

## 4. Failure-Oriented Engineering

Failure-oriented engineering inverts the development question.

Standard question: *what must this system do to succeed?*
Failure-oriented question: *what is the smallest perturbation under which this system stops being itself?*

The cognition architecture is "itself" only while every kernel law, class invariant, authorization invariant, and refusal semantic continues to hold. The moment any of those silently relax, the architecture has collapsed regardless of test counts.

Engineering work in this regime is:

- writing a pressure case;
- predicting the exact failure signature;
- running it;
- comparing observed signature to predicted signature;
- recording the divergence (or its absence) in `reports/` peer artifacts.

A passing pressure test is a successful refusal. A failing pressure test is a successful execution that should have refused.

---

## 5. Runtime Stress Categories

The pressure surface is partitioned into eleven runtime stress categories. Each maps to one or more SPEC invariants and one or more runtime modules. Categories are non-disjoint by design — a single adversarial input may exercise several at once, and the test must declare which signature it predicts as primary.

| # | Category | Primary invariants | Primary modules |
| - | - | - | - |
| 1 | Determinism Pressure | A1, A3 | `canonical.py`, `runtime.py` |
| 2 | Replay Pressure | A1, B3, audit-chain laws | `memory.py`, `kernel.py` |
| 3 | Authorization Pressure | AG1, AG2, AG3 | `authorization.py`, `kernel.py` |
| 4 | Contradiction Pressure | B2, D2, D3 | `state.py`, `transitions.py` |
| 5 | Provenance Pressure | A2, B1, C-series, D5 | `kernel.py`, `proposer.py` |
| 6 | Refusal Pressure | refusal semantics §12 | `refusal.py` |
| 7 | Audit-Memory Pressure | audit-chain laws, B3 | `memory.py` |
| 8 | Multi-Proposer Pressure | proposer interface §8 | `proposer.py`, `proposer_transformer.py` |
| 9 | Adversarial Proposal Injection | refusal §12, AG-series | `proposer.py`, `kernel.py` |
| 10 | Canonicalization Drift | A1, A2, A3 | `canonical.py` |
| 11 | Semantic / Interop / Cross-Version Drift | ID1–ID3, conformance laws | `interop/`, `tools/run_conformance.py` |

Sections 6–18 describe each category and the human and provider failures that surround them.

---

## 6. Determinism Pressure

Determinism is a covenant. Identical canonical inputs MUST produce identical verification results (A1) and identical canonical bytes (A3). Determinism pressure attacks that covenant from the runtime side, not the protocol side.

**Attack surface.** Process identity, working directory, locale, timezone, filesystem inode order, hash randomization, dictionary ordering, floating-point summation order, parallel scheduling, and host architecture.

**Pressure cases.**

- Run `make ci` twice and diff `reports/conformance-report.json`. Bytes MUST match.
- Run `make ci` under `LC_ALL=C`, `LC_ALL=en_US.UTF-8`, `LC_ALL=C.UTF-8`. Bytes MUST match.
- Run `make ci` under `TZ=UTC` and `TZ=Pacific/Auckland`. Bytes MUST match.
- Run `make ci` with `PYTHONHASHSEED=0` and `PYTHONHASHSEED=random`. Bytes MUST match.
- Run `python3 tools/demo_transformer_proposer.py` twice; SHA-256 the captured stdout from each run. Hashes MUST match the published demo audit.

**Predicted failure signature.** Any byte-level divergence in `reports/conformance-report.json`, `reports/conformance-summary.txt`, `interop/reports/`, or the demo audit is a determinism failure. `make verify-drift` MUST exit non-zero in that case.

**Architectural meaning.** Determinism collapse invalidates Class A conformance for the implementation, regardless of vector pass count.

---

## 7. Replay Pressure

Replay is the property that a sealed audit chain re-verifies under a separate process, on a separate machine, with no shared state beyond the bytes themselves. If replay is unstable, the architecture's claim to auditability is rhetorical.

**Pressure cases.**

- **Round-trip replay.** Run `make conformance` to produce `reports/conformance-report.json`. Move the report to a temp directory. Re-run conformance against the existing artifacts and compare.
- **Cross-machine replay.** Generate `interop/fixtures/` and `interop/reports/` on machine M1. Copy to M2. Run `python3 interop/scripts/run_interop_checks.py` on M2. Outputs MUST match byte-for-byte.
- **Cross-process replay.** Run conformance, kill the process, re-run from a clean process. Compare. Bytes MUST match.
- **Cold-cache replay.** Clear OS page cache between runs. Bytes MUST match.
- **Reordered-input replay.** Reorder proposer input streams to the runtime in a way that does not change canonical content. Final canonical bytes MUST match.

**Predicted failure signature.** `make verify-drift` exits 1 with the standard drift message, *or* the interop manifest hash recorded in `interop/reports/` diverges across machines.

**Catastrophic failure mode.** Bytes match across two runs on the same machine but diverge across machines. This indicates implicit dependence on machine-local state — a silent A3 violation.

---

## 8. Authorization Pressure

Authorization is the most abused boundary in cognition systems. The most dangerous failure mode of any verification system is an implementation that treats `VERIFIED`, `CONSENSUS_VALID`, or `CONDUCT_VALID` as automatic execution authorization. AG1 forbids this. Pressure tests must hunt for implicit AG1 violations.

**Pressure cases.**

- **AG1 saturation.** Submit a fully `VERIFIED` Class A artifact to the kernel and confirm the kernel does NOT auto-execute. The vector `class-c-auto-authorize-rejected.json` already enforces this for Class C; the equivalent must hold across A, B, C, D.
- **Bypassed action policy.** Construct an artifact whose `action_policy` is missing or malformed. Kernel MUST refuse, not infer.
- **Forged action policy.** Construct an artifact with `action_policy.action_allowed = true` but no attester-bound authorization step. Kernel MUST refuse and emit a refusal artifact citing AG1/AG3.
- **Sliding scope.** Authorize action `A` and submit action `A'` that differs only in a non-canonical field. Kernel MUST treat the authorization as scoped to the canonical bytes of `A` and refuse `A'`.
- **Telemetry coercion.** Submit a `CALIBRATION_*` telemetry status as an artifact `status` field. Kernel MUST reject (per the published vector `class-any-telemetry-status-rejected.json`).

**Predicted failure signature.** Refusal artifact emitted by `refusal.py`; non-zero exit code from `intellagent` or `python3 tools/run_conformance.py`; explicit citation of AG1/AG2/AG3.

**Catastrophic failure mode.** Action executes. Any execution under any of these conditions is unconditional architectural failure for that implementation.

---

## 9. Contradiction Pressure

Contradiction handling is a Class B and Class D guarantee. B2 requires that contradictory evidence be preserved. D2/D3 require that alternatives and counterarguments not be silently dropped. A runtime that "resolves" contradictions by deletion has collapsed.

**Pressure cases.**

- **Contradiction saturation.** Feed Class B artifacts where `n` of `n` evidence items disagree pairwise. The artifact MUST emit `CONFLICTED`, not `SUPPORTED`. The vector `class-b-conflicted.json` covers a baseline; pressure tests scale `n` and verify the runtime's memory cost stays bounded and the contradictions remain individually inspectable.
- **Late-arriving contradiction.** A Class B artifact reaches `SUPPORTED` and then a contradicting evidence item arrives. The runtime MUST transition the artifact, not erase the prior trace.
- **Conduct contradiction.** A Class D conduct artifact is constructed with empty `alternatives`, empty `counterarguments`, or self-contradicting `not_optimizing_for`. Each MUST produce `CONDUCT_INVALID` with the relevant invariant cited.
- **Stage-loop contradiction.** A Class D commit-chain that loops or skips a stage. Vector `class-d-out-of-order-stages.json` covers the canonical case.

**Predicted failure signature.** Status `CONFLICTED` or `CONDUCT_INVALID`; full evidence trail still readable; refusal artifact emitted on the conduct cases.

**Catastrophic failure mode.** Contradicting evidence vanishes from the artifact between input and output. This is silent B2 violation.

---

## 10. Provenance Pressure

Provenance pressure attacks the chain that ties an artifact to its sources. A1 demands canonicalization metadata. A2 demands hash algorithm and observed/expected digests. B1 demands declared evidence sources. C-series demands eligible-attester sets. D5/CC1 demand commit-chain linkage.

**Pressure cases.**

- **Stripped canonicalization.** Vector `class-a-non-jcs-invalid.json` covers a missing/non-JCS canonicalization scheme. Pressure tests extend this to non-canonical whitespace, BOM injection, and key-reordering attacks. Status MUST be `INVALID`.
- **Forged digests.** Vector `class-a-tampered.json` covers digest mismatch. Pressure tests vary single-bit mutations across the artifact and confirm `TAMPERED` is reached for each.
- **Phantom sources.** A Class B artifact declares an evidence source that does not resolve. Status MUST be `INVALID` (B1) — never `SUPPORTED`.
- **Ineligible attester.** Vector `class-c-unauthorized-attester.json` covers the canonical case. Pressure tests construct attester-set permutations that share a single ineligible signer in otherwise-valid quorums and confirm rejection.
- **Broken commit-chain.** Vector `class-d-broken-depends-on.json` and `class-d-partial-commit-chain.json` cover the canonical D5/CC1 cases. Pressure tests target chain segments where preimage hashes match adjacent stages but skip the intervening one.

**Predicted failure signature.** Status `INVALID`, `TAMPERED`, `CONSENSUS_FAILED`, or `CONDUCT_INVALID` with the relevant invariant cited in the artifact's reasoning trace.

---

## 11. Refusal Pressure

Refusal is a first-class output. `refusal.py` and §12 of the runtime spec define the refusal contract. The strongest test of the runtime is whether refusal quality holds under load and adversarial framing.

**Pressure cases.**

- **Refusal under tempting frame.** Submit transitions framed as "test only," "calibration," "internal," or "operator override." None of those frames are protocol-recognized; the runtime MUST refuse on the same grounds it would refuse a hostile transition.
- **Refusal stability.** Submit `n=1000` semantically equivalent transitions that should each produce identical refusal classifications. Refusal text MAY vary in detail; refusal classification MUST NOT vary.
- **Refusal audibility.** Every refusal MUST emit a structured artifact reachable through `memory.py` with classification, cited invariants, and the input fingerprint. A refusal that emits no audit artifact is a refusal failure.
- **Refusal under partial information.** Submit transitions with deliberately incomplete `action_policy`. The runtime MUST refuse rather than infer policy.

**Predicted failure signature.** Structured refusal artifact, non-zero exit code from `intellagent`, classification stable across equivalent inputs.

**Catastrophic failure mode.** Soft answers ("I cannot do this, but here is something similar"). The runtime is not a chatbot. Drift toward chat-style mitigation is refusal collapse.

---

## 12. Audit-Memory Pressure

`memory.py` is the audit ledger. It is the runtime's only persistent claim to history. If it can be silently rewritten, replay collapses and authorization is meaningless.

**Pressure cases.**

- **Tail truncation.** Remove the last `k` audit entries and re-run replay. Replay MUST detect the missing tail.
- **Mid-chain mutation.** Mutate one byte of one entry. Replay MUST detect the divergence and refuse to extend the chain.
- **Reorder.** Swap two entries. Replay MUST detect ordering corruption (B3).
- **Forked-history.** Two divergent chains share a common prefix and diverge at entry `i`. Replay MUST refuse to merge.
- **Stale-schema replay.** A chain written under schema version `s_0` is replayed by a runtime expecting `s_1`. The runtime MUST emit an explicit version mismatch refusal — not a best-effort migration.

**Predicted failure signature.** Replay refusal, audit-chain divergence reported with the offending entry index, runtime exit code non-zero.

**Catastrophic failure mode.** Replay succeeds despite mutation. This is direct audit forgery and invalidates the implementation entirely.

---

## 13. Multi-Proposer Pressure

The proposer interface (§8 of `INTELLAGENT-RUNTIME.md`) defines a contract. Multi-proposer pressure verifies that the kernel treats all proposers as untrusted regardless of identity, and that proposer authority does not leak into the kernel decision.

**Pressure cases.**

- **Identity-swap.** Run the same transitions through `proposer.py` and `proposer_transformer.py`. Final artifacts MUST be byte-identical when canonical inputs match. Kernel decisions MUST NOT depend on proposer identity.
- **Hostile proposer in pool.** Inject a proposer that returns the union of valid and invalid transitions. The kernel MUST refuse the invalid transitions independently of the valid ones; refusing both is also acceptable, accepting either invalid one is a failure.
- **Silent proposer.** A proposer that returns nothing. The runtime MUST surface this as an exhausted-search outcome with audit, not as success.
- **Loud proposer.** A proposer that returns `n=10000` transitions. Kernel decision time MUST scale within bounded constants; runtime MUST not lose audit fidelity at scale.

**Predicted failure signature.** Identical kernel decisions across proposers; structured audit entries naming each proposer and its outcomes.

**Catastrophic failure mode.** A trusted proposer's output is accepted on weaker evidence than an untrusted proposer's output. Proposer authority leakage is the single most dangerous architectural failure of a governed-cognition runtime.

---

## 14. Adversarial Proposal Injection

This category subsumes the threat model where a proposer is actively hostile or compromised. It is the strongest single-component adversarial test.

**Pressure cases.**

- **Malformed transitions.** Schema-invalid JSON, mistyped fields, unknown statuses, status names that look correct but are not in `STATUS-REGISTRY.md`. The kernel MUST reject at the schema boundary.
- **Type-coerced transitions.** Numeric strings where booleans are expected, lists where scalars are expected, nested null-injection. Kernel MUST reject.
- **Trojan transitions.** Valid-looking transitions whose `action_policy` smuggles authorization that was never granted. AG1/AG3 enforcement MUST refuse.
- **Hallucination pressure.** Proposer fabricates evidence, attesters, prior artifacts, or commit-chain segments that do not exist. Kernel MUST detect via existence checks and provenance verification, not via prose plausibility.
- **Refusal-evasion.** Proposer outputs a sequence designed to slip under refusal classification thresholds (rephrasing, splitting, recombining). Each component MUST be evaluated independently and refused independently when warranted.

**Predicted failure signature.** Kernel-level refusal or `INVALID` status; refusal artifact citing the violated invariant; `intellagent` exit code non-zero.

---

## 15. Canonicalization Drift

A1 binds the implementation to RFC 8785 JCS for v0.1.0. Canonicalization drift is the silent deviation of canonical-byte production across implementations or across releases.

**Pressure cases.**

- **JCS conformance.** Round-trip a corpus of artifacts through `canonical.py`. Output MUST match a reference RFC 8785 implementation byte-for-byte.
- **Unicode normalization drift.** Construct artifacts containing combining characters, surrogate pairs, normalization-equivalent strings (NFC vs NFD). Canonical bytes MUST be deterministic under the published normalization rule and MUST NOT collapse semantically distinct strings.
- **Numeric precision drift.** Construct artifacts containing integers near `2^53`, signed-zero distinctions, and decimal-vs-float boundary cases. Canonical bytes MUST be stable.
- **Key-ordering drift.** Reorder map keys before canonicalization. Output MUST be identical (JCS lexicographic-key requirement).
- **Cross-implementation canonicalization.** Run the canonicalizer in this repo and at least one second implementation against the same input corpus. Bytes MUST match.

**Predicted failure signature.** Canonical-byte divergence; `make verify-drift` non-zero; cross-implementation interop check failure recorded in `interop/reports/`.

---

## 16. Semantic Drift Detection

Semantic drift is the slow, undetected divergence between two valid implementations on the same inputs, where neither implementation is "wrong" by its own internal tests but they no longer agree on what the protocol means.

**Detection mechanism.** The conformance vector corpus + the interop fixture corpus are the canonical bytes that pin protocol meaning. Semantic drift is detected by:

- running `make conformance` against the locked vector set on each candidate implementation;
- running `make interop` against the locked fixture manifest;
- comparing every emitted artifact byte-for-byte across implementations.

**Pressure cases.**

- **Vector-set freezing.** Hash the union of all files under `vectors/` and pin the digest in `reports/`. Any change to that digest without an explicit version bump is a drift event.
- **Fixture-manifest freezing.** Apply the same pinning to `interop/fixtures/`.
- **Two-implementation rotation.** Periodically run the full `make ci` chain on a second, independent implementation. Any byte-divergence is recorded as a semantic-drift incident requiring resolution before the next release.

**Predicted failure signature.** Hash mismatch between two implementations, with the divergent vector or fixture identified; the drift event requires a SPEC clarification or an implementation fix.

**Catastrophic failure mode.** Drift is detected but normalized through ad-hoc tolerances ("close enough"). Tolerance is canonicalization collapse. There is no "close enough" for canonical bytes.

---

## 17. Interoperability Drift

Interoperability drift is semantic drift's external surface: artifacts produced by implementation A are rejected by implementation B (or worse, accepted but reinterpreted).

**Pressure cases.**

- **Cross-implementation acceptance.** Implementation A emits a `VERIFIED` Class A artifact; implementation B replays it. Status MUST be `VERIFIED`. Any other status is interop drift.
- **Cross-implementation refusal.** Implementation A refuses transition `T`; implementation B refuses `T` with the same classification. Refusal text MAY differ.
- **Manifest reciprocity.** `interop/scripts/generate_fixture_manifest.py` produces a manifest. A second implementation consumes the manifest and must produce the same `interop/reports/` byte-for-byte.
- **Schema-version negotiation.** An implementation receives an artifact bound to a schema version it does not support. It MUST refuse with an explicit version-mismatch refusal, never silently coerce.

**Predicted failure signature.** Manifest hash mismatch; non-zero exit from `python3 interop/scripts/run_interop_checks.py`; explicit version-mismatch refusal artifact.

---

## 18. Cross-Version Pressure

Cross-version pressure is the structural test of how v0.1.0 implementations behave when confronted with artifacts from a future v0.x release, and how a future v0.x runtime must behave when replaying v0.1.0 chains.

**Pressure cases.**

- **Forward-rejection.** A v0.1.0 implementation receives an artifact declaring `protocol_version != "0.1.0"`. It MUST refuse with `INVALID` and a version-mismatch citation. It MUST NOT attempt to interpret the artifact.
- **Backward-replay.** A future implementation MUST be able to replay v0.1.0 chains byte-for-byte. The audit hash MUST match.
- **Vector stability.** A v0.1.0 vector ID MUST NOT be reused for a different intent in any subsequent version (per `vectors/README.md`).

**Predicted failure signature.** Version-mismatch refusal artifact; backward-replay hash mismatch; vector-ID collision detected by `tools/validate_vectors.py`.

---

## 19. Human Operator Failure

The human operator is part of the system. Pressure-testing the architecture must include the operator as an attack surface — not because the operator is malicious, but because operator failure is a foreseeable mode.

**Pressure cases.**

- **Misconfigured environment.** Wrong Python, missing JCS dependency, wrong protocol version on disk. `make ci` MUST fail loudly with a citable error.
- **Partial commits.** Operator commits `vectors/` changes without regenerating `reports/`. `make verify-drift` MUST exit 1.
- **Hand-edited artifacts.** Operator opens `reports/conformance-report.json` and hand-edits a status. `make verify-drift` MUST exit 1.
- **Skipped CI.** Operator pushes without running `make ci`. CI in the upstream environment MUST run the full chain (`no-pseudocode test conformance interop`) and reject the push.
- **Ambiguous authorization commands.** Operator issues a command whose authorization scope is unclear. The runtime MUST refuse and require a re-issued, scope-bound command.

**Predicted failure signature.** Loud, reproducible failure with a citable error and a path forward; never a silent pass.

---

## 20. Provider Failure

Where the runtime delegates inference to an external provider (OpenAI, Anthropic, local) via a transformer proposer, the provider is a non-trusted dependency. Provider failure must not become runtime failure.

**Pressure cases.**

- **Provider unavailable.** Network down, API timeout, 5xx. The runtime MUST surface this as an exhausted-search or error state with audit, not as a successful refusal and not as a silent pass.
- **Provider returning garbage.** Non-JSON response, JSON with the wrong shape, JSON with a status not in `STATUS-REGISTRY.md`. `proposer_transformer.py` MUST reject at the proposer boundary.
- **Provider returning plausible but unsupported claims.** Provider output cites attesters that do not exist or evidence URLs that do not resolve. Kernel-level provenance checks MUST refuse.
- **Provider rate-limited.** Backoff and retry MUST be bounded; no infinite loop, no silent skip.
- **Provider model substitution.** Provider silently routes to a different model. Audit MUST record the model identifier returned by the provider; if the runtime cannot obtain a model identifier, it MUST refuse.

**Predicted failure signature.** Structured error or refusal artifact recording the provider response; non-zero exit; model identifier surfaced in `memory.py` for every provider-mediated transition.

---

## 21. Benchmark Corruption

A benchmark that the runtime trains, tunes, or selects against will eventually be optimized for. The pressure-test corpus is itself a benchmark and must be defended.

**Pressure cases.**

- **Vector-leak detection.** No production runtime path may consume `vectors/` directly except `tools/run_conformance.py`. A pressure test scans the import graph of `intellagent_runtime/` to confirm no module imports from `vectors/`.
- **Test-data leakage.** No test under `tests/` may share fixtures with `vectors/` such that a regression in the runtime would still pass `make test`. Pressure test enforces fixture hash separation.
- **Benchmark-only optimizations.** Any code path that behaves differently when a known-vector hash is observed is benchmark corruption. The pressure test mutates vector content by one byte and confirms behavior is unchanged in kind, only in outcome.

**Predicted failure signature.** Pressure test fails when a runtime module references vector paths or fixture hashes; CI MUST exit 1.

---

## 22. CI Drift

CI is the last line of defense. CI drift is the gradual relaxation of CI checks: a flaky check skipped, a new check unmerged, a Makefile target quietly weakened.

**Pressure cases.**

- **Target presence.** `make ci` invokes `no-pseudocode test conformance interop` in that order. A pressure test parses the Makefile and confirms each target is present and has a non-empty body.
- **Target weakening.** A pressure test compares the current `make ci` target body against a hash committed at v0.1.0 release. Any weakening — removed dependency, suppressed exit code, added `|| true` — is detected.
- **Skipped checks.** A pressure test confirms that `make ci` exits non-zero if any of `no-pseudocode`, `test`, `conformance`, or `interop` exits non-zero. A green `make ci` over a red sub-check is CI drift.
- **Drift-detection drift.** `make verify-drift` itself MUST be invoked in CI; its exit must propagate.

**Predicted failure signature.** Hash mismatch on the Makefile, missing target, or successful `make ci` over a deliberately-broken sub-check.

---

## 23. Runtime Collapse Conditions

A runtime collapse is a state in which the runtime continues to execute but is no longer governed. The runtime MUST detect and refuse these states.

**Collapse conditions (each is unconditional refusal grounds):**

1. Audit chain cannot extend (write failure, integrity failure).
2. Canonicalization library mismatched against `pyproject.toml` declared version.
3. Schema version on disk inconsistent with runtime version.
4. Two consecutive proposer outputs collide on canonical bytes for semantically distinct intents.
5. Memory store reports an entry that hashes to a value other than its declared digest.
6. `refusal.py` cannot construct a refusal artifact because of an internal error — the runtime MUST halt rather than continue without refusal capability.

Each condition has a named exception type or status in the runtime and MUST surface in `memory.py` even if the surrounding transition cannot complete.

---

## 24. What Counts As Architectural Failure

Not every test failure invalidates the architecture. The pressure regime distinguishes four severities.

| Severity | Meaning | Action |
| - | - | - |
| **Acceptable** | A pressure test reveals an implementation bug fixable without changing SPEC, vectors, or runtime contract. | File, fix, regress-test, ship. |
| **Conformance-invalidating** | A pressure test reveals a class invariant violation. | Implementation MUST drop that class from `classes_supported` until fixed. |
| **Replay-invalidating** | A pressure test reveals replay instability or audit-chain forgery. | All audit chains produced under the affected runtime version are quarantined. |
| **Architecture-invalidating** | A pressure test reveals a SPEC-level contradiction, an unfalsifiable claim, or a structural impossibility. | Architecture is unlocked. SPEC change required before any further release. |

Architecture-invalidating failures are rare by design. They are also non-negotiable.

---

## 25. Pressure-Test Harness Requirements

The pressure-test harness is a peer to the conformance harness, not an extension of it. v0.1.0 does not require a new module; the harness is a directory layout, a tool, and a Makefile target, each grounded in existing patterns.

**Layout (planned, not yet materialized):**

```
pressure/
├── README.md
├── cases/                   # one JSON per pressure case
├── fixtures/                # corrupted-by-design inputs
└── scripts/
    ├── run_pressure.py
    └── verify_signatures.py
```

**Each pressure case is a JSON document.** Required fields:

```json
{
  "case_id": "<stable, unique within protocol_version>",
  "protocol_version": "0.1.0",
  "category": "<one of the 11 categories in §5>",
  "invariant": "<SPEC invariant id, e.g. A1, AG3, D5>",
  "input": { },
  "predicted_signature": {
    "kind": "<status | refusal | exception | exit_code | audit_divergence>",
    "value": "<INVALID | TAMPERED | non-zero | … >",
    "cite": "<invariant or law reference>"
  },
  "why": "<one sentence: which architectural property this falsifies if it passes>"
}
```

**Required Makefile target (planned):**

```
pressure:
	$(PYTHON) pressure/scripts/run_pressure.py
```

**Required CI integration:** `make ci` is extended to `no-pseudocode test conformance interop pressure` once the harness lands. Until that point, pressure tests run out-of-band and their results are recorded in `reports/pressure-status.txt`.

**Harness invariants:**

- A pressure test MUST declare its predicted signature before running.
- A pressure test that observes a different signature than predicted is a discrepancy event and is recorded as such.
- The harness MUST be deterministic by the same standard as the conformance harness.
- The harness MUST NOT modify the runtime, the SPEC, or the vector corpus.

---

## 26. Long-Term Validation Strategy

Pressure tests do not retire. They accumulate.

**The strategy is monotonic.**

- Every architecture-invalidating event becomes a permanent pressure case.
- Every replay-invalidating event becomes a permanent pressure case.
- Every conformance-invalidating event becomes a permanent pressure case.
- Acceptable bugs become regression tests in `tests/`, not pressure cases.

**The strategy is multi-implementation.**

- Conformance is class-scoped. Pressure validity is implementation-scoped.
- A second, independent implementation is recruited as soon as the first stable v0.1.0 implementation declares conformance. The second implementation runs the same pressure-test corpus.
- A pressure case that one implementation passes and another fails is a drift incident.

**The strategy is adversarial.**

- An external party SHOULD attempt to construct a vector or fixture that satisfies all current pressure tests but violates the SPEC. If they succeed, the pressure-test corpus is incomplete.

---

## 27. Known Weaknesses

The current pressure-test surface for v0.1.0 has the following known gaps. Each is a candidate pressure case but not yet materialized.

1. **Side-channel observability.** The runtime currently produces audit and refusal artifacts but does not bound information leakage through timing. Timing-based inference of refusal vs acceptance is unaddressed.
2. **Long-horizon memory.** `memory.py` has no published bound on chain length under sustained load. Behavior at `n > 10^6` audit entries is unverified.
3. **Multi-process audit.** Concurrent writers to the audit ledger are not specified at v0.1.0. The pressure test in §12 covers single-writer corruption only.
4. **Provider attestation.** A provider that signs its responses is not yet a protocol-recognized attester. Until C-series attester eligibility is extended, provider trust is reputational only.
5. **Cross-language canonicalization.** The current canonicalizer is Python-only. Cross-language drift (Rust, Go, TypeScript) is unmeasured.
6. **Pressure-harness self-pressure.** No pressure test exists to falsify the harness itself. The harness is currently trusted by inspection.
7. **Operator-induced silent drift.** A sufficiently knowledgeable operator can tamper with `reports/` and re-commit. Detection currently relies on `make verify-drift` being invoked; out-of-band tampering is not protocol-detectable.

These are documented, not solved.

---

## 28. Non-Goals

This document does not:

- Introduce new epistemic classes, statuses, primitives, or runtime modules.
- Redesign the kernel, the proposer interface, or the audit memory model.
- Replace the conformance vector corpus.
- Bound model capability, latency, or throughput.
- Define security against an attacker who has root on the host running the runtime.
- Define a recovery protocol after architecture-invalidating events. Recovery is SPEC work, not pressure-test work.
- Promise that all pressure cases described here are sufficient. Sufficiency is asymptotic; this document is the floor, not the ceiling.

---

## 29. Final Law

> A runtime that only succeeds under friendly conditions is not validated.

This document is the standing falsification surface for WiseOrder Protocol v0.1.0 and Intellagent Runtime v0.1. Any future release — patch, minor, or major — that ships without first running the pressure-test corpus to deterministic completion is unreleased by the standards of this document.

The purpose of pressure testing is not to prove perfection.
The purpose is to discover collapse boundaries before real deployment pressure does.

---

## What Would Falsify Intellagent?

Any one of the following, demonstrated reproducibly under the pressure-test harness, falsifies Intellagent v0.1 as a governed-cognition runtime:

1. **Proposer authority leakage.** A trusted proposer's output produces a kernel decision that an untrusted proposer's identical output would not produce.
2. **Replay instability.** A sealed audit chain replays differently across two clean processes on the same canonical bytes.
3. **Unverifiable audit memory.** An audit entry can be mutated, removed, or inserted without detection by replay.
4. **Refusal inconsistency.** Two semantically equivalent inputs produce different refusal classifications under identical configuration.
5. **Authorization collapse.** A `VERIFIED`, `CONSENSUS_VALID`, or `CONDUCT_VALID` status produces execution without an explicit, scoped, attester-bound authorization step.
6. **Semantic drift between implementations.** Two implementations declared conformant for the same class produce divergent canonical bytes for the same input.
7. **Contradiction loss under replay.** Class B contradictions present at sealing time are absent at replay time.
8. **Canonicalization collapse.** Two semantically distinct artifacts canonicalize to the same bytes, or one artifact canonicalizes to two distinct byte sequences across runs.
9. **Refusal artifact suppression.** A refusal occurs without producing a structured, replayable refusal artifact.
10. **Vector-ID reuse.** A vector ID is reused across protocol versions for a different intent.

Any of these, demonstrated, unlocks the architecture.

---

**End of ARCHITECTURE PRESSURE TESTS v0.1.**
