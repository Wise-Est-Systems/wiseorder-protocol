# AUDIT_SCOPE v0.1

**Status:** Audit-ready scope statement for WiseOrder Protocol v0.1.0.
**Adopted:** 2026-05-10
**Target audience:** External technical reviewers, hostile auditors, security researchers, independent implementers.
**Authority:** This document is the authoritative answer to "what is in scope, what is implemented, what is policy-only, and what is missing?" An auditor MUST treat this document as the definitive boundary statement; if a surface is not enumerated here, it is out of scope for v0.1.0.

---

## 1. Purpose

This document exists so that a hostile technical reviewer can scope an audit without semantic confusion. It refuses to blur:

- **implemented** — code exists, executes, has tests
- **partially implemented** — code exists, fails to cover the documented surface
- **policy-only** — specification text exists, no executing code
- **future work** — declared as deferred in spec
- **unsupported** — explicitly out of scope

A reviewer who finds a behavior not described here SHOULD report it as either an undocumented surface (a finding) or a mislabeled scope item (also a finding).

---

## 2. Implemented Surfaces

The following surfaces are covered by executing code with passing tests under `make ci`.

### 2.1 Kernel
| Surface | Code path | Test path |
|---|---|---|
| Class A deterministic verification | `intellagent_runtime/kernel.py`, `intellagent_runtime/canonical.py` | `tests/test_intellagent_kernel.py`, `tests/test_canonicalization_golden.py` |
| Class B instrumented empirical verification | `intellagent_runtime/kernel.py` | `tests/test_intellagent_kernel.py` |
| Class C protocol-bound consensus | `intellagent_runtime/kernel.py` | `tests/test_intellagent_kernel.py` |
| Class D interpretive governance | `intellagent_runtime/kernel.py`, `intellagent_runtime/state.py` | `tests/test_intellagent_kernel.py`, `tests/test_intellagent_state.py` |
| RFC 8785 JCS canonicalization | `intellagent_runtime/canonical.py`, `canonicalization/tools/` | `tests/test_canonicalization_golden.py` |
| Commit-chain verification (CC1–CC4) | `intellagent_runtime/kernel.py` | `tests/test_intellagent_kernel.py` |
| Refusal sealing (`RefusalRecord`) | `intellagent_runtime/refusal.py` | `tests/test_intellagent_runtime.py` |
| Authorization gate (AG1–AG3) | `intellagent_runtime/authorization.py` | `tests/test_intellagent_authorization.py` |
| Audit memory (append-only) | `intellagent_runtime/memory.py` | `tests/test_intellagent_memory.py` |
| State / transitions | `intellagent_runtime/state.py`, `intellagent_runtime/transitions.py` | `tests/test_intellagent_state.py`, `tests/test_intellagent_runtime.py` |
| CLI | `intellagent_runtime/cli.py` | `tests/test_intellagent_cli.py` |
| Proposer (deterministic) | `intellagent_runtime/proposer.py` | `tests/test_intellagent_runtime.py` |
| Transformer proposer (governed) | `intellagent_runtime/proposer_transformer.py` | `tests/test_intellagent_proposer_transformer.py` |

### 2.2 Conformance harness
| Surface | Code path |
|---|---|
| Vector validation | `tools/validate_vectors.py` |
| Implementation-declaration validation | `tools/validate_implementations.py` |
| Conformance runner | `tools/run_conformance.py` |
| Documentation code standard | `tools/check_no_pseudocode.py` |
| Canonicalization golden generation | `canonicalization/tools/generate_golden.py` |
| Canonicalization golden verification | `canonicalization/tools/verify_golden.py` |
| Interop fixture manifest generation | `interop/scripts/generate_fixture_manifest.py` |
| Interop checks | `interop/scripts/run_interop_checks.py` |

### 2.3 Bounded execution runtimes (self-check level)
| Runtime | Code path | Status |
|---|---|---|
| Pipeline runtime | `tools/pipeline_runtime.py` | self-check + run-fixture |
| Proposer runtime | `tools/proposer_runtime.py` | self-check + propose verb |
| Real-agent runtime | `tools/real_agent_runtime.py` | self-check + dry-run + execute (sandboxed) |
| Review-gate runtime | `tools/review_gate_runtime.py` | self-check + review verb |
| OS isolation runtime | `tools/os_isolation_runtime.py` | self-check + run-fixture (macOS sandbox-exec) |
| Resource-limit runtime | `tools/resource_limit_runtime.py` | self-check + run-fixture |
| Workforce sandbox stress | `tools/workforce_sandbox_stress.py` | runs |
| Signature runtime | `tools/signature_runtime.py` | runs |

### 2.4 Frozen public artifacts
| Artifact | Path |
|---|---|
| Vectors | `vectors/*.json` (23 + adversarial extension) |
| Schemas | `schemas/*.json` |
| Canonicalization corpus | `canonicalization/corpus/`, `canonicalization/golden/` |
| Conformance report | `reports/conformance-report.json` |
| Interop reports | `interop/reports/*.json` |

---

## 3. Partially Implemented Surfaces

The following surfaces have executing code but do not yet cover the full documented surface.

| Surface | Spec | What is implemented | What is not |
|---|---|---|---|
| Workforce execution | `WORKFORCE-EXECUTION-RUNTIME-v0.1.md`, `AGENT-GOVERNANCE-WORKFORCE-v0.1.md` | sandbox stress harness, work-order templates, action logs | full multi-agent execution kernel |
| OS isolation | `OS-ISOLATION-RUNTIME-v0.1.md` | macOS sandbox-exec self-check + fixture | Linux equivalence (no namespace/cgroups runtime in-tree) |
| Resource limits | `RESOURCE-LIMIT-RUNTIME-v0.1.md` | self-check + fixture | hard memory/cpu budget enforcement under adversarial load |
| Cross-language canonicalization | `CROSS-LANGUAGE-CANONICALIZATION-v0.1.md` | Python reference + corpus | independent Rust/TS/Go verifiers (see `IMPLEMENTATION_TRACKER.md`) |

A reviewer should treat these surfaces as scoped but incomplete. The published code is honest; the gap is in coverage, not in correctness of what runs.

---

## 4. Policy-Only Surfaces

The following surfaces exist as specification text only. No executing code enforces them in v0.1.0.

| Surface | Spec |
|---|---|
| Authority Law | `AUTHORITY-LAW-v0.1.md` |
| Correction Law | `CORRECTION-LAW-v0.1.md` |
| Replay Law | `REPLAY-LAW-v0.1.md` |
| Trust Law | `TRUST-LAW-v0.1.md` |
| Validation Law | `VALIDATION-LAW-v0.1.md` |
| Adoption Ladder | `ADOPTION-LADDER-v0.1.md` |
| Dependency Gradient | `DEPENDENCY-GRADIENT-v0.1.md` |
| Spec Evolution Policy | `SPEC-EVOLUTION-POLICY-v0.1.md` |
| Forbidden Surfaces | `FORBIDDEN-SURFACES-v0.1.md` |
| Waiver Mechanism | `WAIVER-MECHANISM-v0.1.md` |
| Architecture Pressure Tests | `ARCHITECTURE-PRESSURE-TESTS-v0.1.md` |
| Workflow Grammar | `WORKFLOW-GRAMMAR-v0.1.md` |
| Input Grammar | `INPUT-GRAMMAR-v0.1.md` |
| Translation Layer | `TRANSLATION-LAYER-v0.1.md` |

A reviewer SHOULD treat these as written canon, not as enforced behavior. Claims tied to these surfaces are claims about what the specification says, not about what the runtime does.

---

## 5. Future Work

Declared deferred in `SPEC.md` §15:

- Revocation semantics
- Artifact supersession
- Consensus reversal
- Extension governance
- Protocol negotiation
- Distributed audit registries
- Cross-regime calibration exchange

Not promised for any specific date. Not in scope for v0.1.0 review.

---

## 6. Explicitly Unsupported

The following are out of scope for v0.1.0 by design and SHOULD NOT be reviewed against any expectation of support:

- Networked execution (the runtime is single-host, no outbound HTTP).
- Multi-tenant isolation guarantees.
- Real-time or low-latency execution paths.
- Hardware attestation (TPM, SGX, Nitro Enclaves).
- Cryptographic key management (KMS integration, HSM backing).
- Production-grade signing (artifact signatures are out-of-band; the protocol does not specify a signing mechanism for v0.1.0).
- Human-language interpretation of conduct artifacts (Class D conduct is structurally validated; the substantive correctness of strategy / ethics / aesthetics is not adjudicated by the protocol).
- Model evaluation, training, or alignment.
- Any claim of AGI, consciousness, autonomy, or universal trust.

---

## 7. Threat Model (Explicit)

From `SPEC.md` §8 and the adversarial vector extension:

| ID | Threat | Mitigation | Vector reference |
|---|---|---|---|
| D-1 | Post-hoc rationalization | Commit-chain dependency ordering with preimage (CC1–CC4) | `class-d-broken-depends-on`, `class-d-out-of-order-stages`, `class-d-forged-commit-chain` |
| D-2 | Performative challenge surfaces | Sampled external audit (out-of-band) | `class-d-no-counterarguments` |
| C-1 | Unauthorized consensus participation | Role-bound attestation validation (C2) | `class-c-unauthorized-attester`, `class-c-attestation-replay` |
| B-1 | Contradictory evidence suppression | Mandatory contradiction preservation (B2) | `class-b-conflicted`, `class-b-evidence-suppression-attempt` |
| AG-1 | Auto-authorization | AG1–AG3 separation; reject `*_VALID` → `action_allowed=true` without `authorization_source` | `class-c-auto-authorize-rejected`, `class-c-quorum-inflation` |
| A-1 | Canonicalization corruption | Declared scheme + frozen corpus fingerprint (CS1–CS3) | `class-a-non-jcs-invalid`, `class-a-canonicalization-scheme-corruption` |
| A-2 | Algorithm downgrade | SHA-256 frozen at v0.1.0 lock | `class-a-algorithm-downgrade` |

Threats not in this table are not modeled by v0.1.0. A reviewer who identifies a missing threat SHOULD report it as a scope-extension finding.

---

## 8. Unresolved Gaps

These are known weaknesses, declared up-front so an audit does not present them as discoveries.

1. **No independent implementation.** Both declared implementations (`Winstack`, `WISEATA`) are first-party. Self-declared parity is necessary but not sufficient.
2. **No external audit.** Both implementations carry `audit_status: NOT_AUDITED`.
3. **No production deployment.** No external user, no adversarial load, no operational scars.
4. **Cross-machine replay only verified on macOS.** Linux and second-machine slots are open. See `CROSS_MACHINE_REPLAY_REPORT.md`.
5. **OS isolation is macOS-only.** Linux namespace/cgroups equivalent is partial.
6. **Signing is out-of-band.** v0.1.0 does not specify a signature mechanism; integrity is digest-based.
7. **70% of the spec corpus is policy-only.** See §4 above.
8. **Vector suite is small (33 vectors after adversarial expansion).** Coverage is breadth-oriented, not exhaustive.

A reviewer is expected to weigh findings against this list. A finding that restates one of these gaps is not a new finding.

---

## 9. How to Review

Recommended order:

1. Read `SPEC.md` and `SPEC_LOCK_v0.1.md`.
2. Run `make ci` from a clean checkout under the documented Python venv.
3. Independently re-derive `vectors_suite_sha256` from `vectors/*.json`.
4. Independently re-derive `corpus_sha256` from `canonicalization/corpus/`.
5. Read every vector under `vectors/*.json` and confirm each `expected_status` follows from the cited invariant.
6. Examine `intellagent_runtime/kernel.py` for cases where verification logic could diverge from spec.
7. Examine `intellagent_runtime/authorization.py` for AG1–AG3 enforcement.
8. Attempt to construct a vector that passes structural validation but violates an invariant.
9. Attempt to construct an input artifact that bypasses commit-chain ordering.
10. Report findings against the threat IDs in §7 or as scope-extension findings.

---

## 10. Findings Format

A reviewer SHOULD format findings as:

```
ID: AUDIT-FINDING-<NN>
Severity: [critical | high | medium | low | informational]
Surface: [implemented | partial | policy-only | future | unsupported]
Spec reference: [SPEC.md §X | SPEC_LOCK_v0.1.md §Y | other]
Vector reference: [vector_id | none]
Description: <what>
Reproduction: <how>
Suggested resolution: <what would change>
```

Findings against `policy-only` surfaces SHOULD note that no executing code is responsible; they are spec findings, not runtime findings.
