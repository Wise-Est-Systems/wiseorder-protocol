# INTELLAGENT + WISEORDER — Part 4: Conformance & Release

*Conformance model, vectors, interop, implementation status, limitations, future work, security, reproducibility, testing, release.*

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

## 2.17 CONFORMANCE MODEL

Conformance is validator-mediated, vector-driven, and class-scoped.

### 2.17.1 Conformance requirements

An implementation is conformant for a declared class if it satisfies every kernel invariant for that class against every conformance vector targeting that class. v0.1.0 mappings:

- **Class A conformance** ⇒ A1, A2, A3, CS1, CS2, CS3, telemetry discipline.
- **Class B conformance** ⇒ B1, B2 (unidirectional), B3, telemetry discipline.
- **Class C conformance** ⇒ C1, C2, C3, C4, AG2, telemetry discipline.
- **Class D conformance** ⇒ D1, D2, D3, D4, D5, CC1–CC4, telemetry discipline.

An implementation that declares a class but fails any vector for that class is non-conformant. An implementation that produces artifacts in a class it has not declared is registered as a TR-3 hidden-authority-expansion event.

### 2.17.2 Implementation declarations

An implementation registration in `IMPLEMENTATIONS.md` declares:

```json
{
  "implementation_id": "<stable id>",
  "protocol": "wiseorder",
  "version": "0.1.0",
  "classes_supported": ["A", "B"],
  "audit_status": "NOT_AUDITED" | "CONFORMANT" | "FAILED",
  "evidence": {
    "conformance_report": "<path>",
    "interop_report": "<path>",
    "report_sha256": "sha256:<64hex>"
  },
  "notes": "<optional text>"
}
```

ID1, ID2, ID3 govern the validity of the registration (per §2.8.8). v0.1.0 registrations:

- **Winstack**: `classes_supported: ["A", "B"]`; `audit_status: NOT_AUDITED`.
- **WISEATA**: `classes_supported: ["B"]`; `audit_status: NOT_AUDITED`; `notes: "F-1 canonicalization incompatibility with WiseOrder v0.1.0 JCS requirement."`

### 2.17.3 Vector requirements

The 23 conformance vectors at v0.1.0 are the law. Per `vectors/README.md` and §2.18 below:

- Every Class A invariant (A1, A2, A3) has at least one passing vector and at least one rejecting vector.
- Every Class B invariant has at least one passing and one rejecting vector.
- Every Class C invariant (C1, C2, C3, C4) has at least one passing and one rejecting vector.
- Every Class D invariant (D1–D5, CC1–CC4) has at least one passing and one rejecting vector.
- Action governance (AG1, AG3) has at least one rejecting vector each.
- Telemetry rejection has at least one vector.
- Canonicalization (CS1) has at least one vector exercising F-1.

### 2.17.4 Interoperability expectations

Three interop fixtures at v0.1.0:

- `winstack-class-a-valid-001` — Winstack producing a Class A artifact aligned with `class-a-valid-wiseproof.json`.
- `winstack-class-b-valid-001` — Winstack producing a Class B artifact aligned with `class-b-valid-wiseexp.json`.
- `wiseata-class-b-valid-001` — WISEATA producing a Class B artifact aligned with `class-b-valid-wiseexp.json` (F-1: no Class A from WISEATA).

Each fixture is exercised by 7 cross-layer checks (per §2.19).

### 2.17.5 Class-scoped support

An implementation registers exactly the classes it implements. Registration of a class without conformance evidence is permitted only at `audit_status: NOT_AUDITED`. Promotion to `CONFORMANT` requires evidence (ID3).

### 2.17.6 Suite fingerprints

| Suite | Fingerprint |
| --- | --- |
| `vectors_suite_sha256` | `sha256:37d3ec45ecca12d256b7df1c02ac0f0d1474f71b68510e9475fa449b8eb1331b` |
| `manifests_suite_sha256` | `sha256:74eaaa62271f23172232bda43ba3340543e66c46ba1e2f5e6da18d3447a6ba29` |
| `corpus_sha256` | `sha256:c95685bff48c15abc313c462908b05ac309250bc660c2d802ae51af5a8038b09` |

Reviewer reproduction of these three fingerprints is the canonical conformance verification.

---

## 2.18 CONFORMANCE VECTORS

Vectors are the law. Each vector pins input, expected status, expected artifact fields, and the invariant it exercises.

### 2.18.1 Vector format

Per-vector schema (validated against `schemas/vector.schema.json`):

```json
{
  "vector_id": "<stable id>",
  "protocol_version": "0.1.0",
  "class": "A | B | C | D",
  "description": "<text>",
  "input": { },
  "expected_status": "<status>",
  "expected_artifact_fields": [],
  "why": "<text citing the invariant being exercised>"
}
```

### 2.18.2 The 23 vectors at v0.1.0

| Vector | Class | Expected Status | Invariant |
| --- | --- | --- | --- |
| `class-a-valid-wiseproof` | A | VERIFIED | A1+A2+A3 pass |
| `class-a-tampered` | A | TAMPERED | A1 fail (canonicalization mismatch) |
| `class-a-missing-field` | A | INVALID | A2 fail (provenance.signature_sha256 missing) |
| `class-a-non-jcs-invalid` | A | INVALID | F-1 backstop (non-JCS canonicalization) |
| `class-any-telemetry-status-rejected` | A | INVALID | TEL1 (CALIBRATION_ token in status) |
| `class-b-valid-wiseexp` | B | SUPPORTED | B1+B3 pass |
| `class-b-conflicted` | B | CONFLICTED | B2 (contradictory evidence surfaced) |
| `class-b-insufficient-evidence` | B | INSUFFICIENT_EVIDENCE | B-status-discipline |
| `class-b-missing-sources` | B | INVALID | B1 fail |
| `class-c-consensus-pending` | C | CONSENSUS_PENDING | C3 (count < threshold) |
| `class-c-consensus-valid` | C | CONSENSUS_VALID | C1+C2+C3 pass |
| `class-c-consensus-failed` | C | CONSENSUS_FAILED | C-status-discipline |
| `class-c-unauthorized-attester` | C | INVALID | C2 + AG2 |
| `class-c-auto-authorize-rejected` | C | INVALID | AG1 contrapositive |
| `class-c-authorization-source-required` | C | INVALID | AG3 |
| `class-c-same-consensus-different-action-policy` | C | CONSENSUS_VALID with denied action | C accepted; gate denies |
| `class-d-conduct-valid` | D | CONDUCT_VALID | D1-D5 + CC1-CC4 pass |
| `class-d-no-alternatives` | D | CONDUCT_INVALID | D2 fail |
| `class-d-no-counterarguments` | D | CONDUCT_INVALID | D3 fail |
| `class-d-verified-status-rejected` | D | CONDUCT_INVALID | D4 fail |
| `class-d-partial-commit-chain` | D | CONDUCT_INVALID | CC1/D5 |
| `class-d-broken-depends-on` | D | CONDUCT_INVALID | CC2 |
| `class-d-out-of-order-stages` | D | CONDUCT_INVALID | CC4 |

### 2.18.3 Vector edge-case coverage

The 23 vectors include:

- Edge cases (empty fields, boundary thresholds, single-element arrays).
- Malformed inputs (telemetry token in status; missing required fields; tampered canonical bytes).
- Invalid transitions (out-of-order stages; broken chains; unauthorized attesters).
- Authorization failures (AG1, AG3 surfaces).
- Tampering conditions (`class-a-tampered`).

### 2.18.4 Vector replay

Each vector is deterministic. `make conformance` runs each vector through `WiseOrderKernel.verify` and asserts the verdict matches the vector's `expected_status`. Output: `reports/conformance-report.json`. Suite fingerprint stable across runs.

### 2.18.5 Vector validation

`tools/validate_vectors.py` validates each vector against the schema before any kernel run. Schema violations are reported as `VECTOR_SCHEMA_INVALID` and prevent the conformance run from starting.

---

## 2.19 INTEROPERABILITY

Interoperability is the requirement that artifacts produced by one implementation be verifiable by another implementation that declares the same class.

### 2.19.1 Interoperability assumptions

- Two implementations declaring the same protocol and version produce mutually-verifiable artifacts within their declared classes.
- Class-scoped: an implementation declaring only Class B does not produce or verify Class A artifacts (F-1 pattern).
- Canonicalization-locked: at v0.1.0, all implementations claiming Class A must produce byte-identical canonical output for any given artifact.

### 2.19.2 Canonical compatibility rules

- Both implementations canonicalize using the registered scheme.
- Both produce SHA-256 over canonical bytes.
- Both yield byte-identical fingerprints for any artifact they both declare a class for.

### 2.19.3 Replay compatibility rules

- Class A artifacts: an artifact produced by implementation X is verifiable by implementation Y under identical canonicalization.
- Class B artifacts: an artifact produced by X is verifiable by Y given Y has access to the cited sources (or Y trusts X's source declarations).
- Class C artifacts: an artifact produced by X with attesters {a, b, c} is verifiable by Y if Y recognizes those attesters.
- Class D artifacts: an artifact produced by X is verifiable by Y given Y understands the commit-chain semantics.

### 2.19.4 Artifact portability expectations

- A Class A artifact's canonical bytes are portable across any v0.1.0 Class-A-conformant implementation.
- A Class B artifact's portability depends on shared source registry; the artifact's `sources` field carries URIs.
- A Class C artifact's portability depends on shared attester registry.
- A Class D artifact's portability is bounded by shared interpretation of commit-chain ordering.

### 2.19.5 The 7 cross-layer checks

For each interop fixture, `interop/scripts/run_interop_checks.py` runs:

1. **`protocol_version_match`** — `protocol == "wiseorder"`, `version == "0.1.0"`.
2. **`class_in_implementation_classes`** — manifest's class is in implementation's `classes_supported`.
3. **`aligned_vectors_exist`** — every aligned vector resolves to a published vector.
4. **`aligned_vectors_class_match`** — aligned vectors share the same class as the manifest.
5. **`wiseata_class_a_prohibition`** — WISEATA never claims Class A (F-1).
6. **`artifact_sha256_format`** — `sha256:<64hex>`.
7. **`manifest_serialization_stable`** — disk bytes equal a fresh canonical-pretty re-rendering.

### 2.19.6 Independent testability

Interoperability is independently testable: a reviewer clones the bundle, runs `make interop`, and observes:

```
make interop
  → fixtures: 3/3 passed; overall_status: PASS
  → manifests_suite_sha256: sha256:74eaaa62271f23172232bda43ba3340543e66c46ba1e2f5e6da18d3447a6ba29
```

A mismatch between the reviewer's reproduced fingerprint and the published value is a TR-1 silent-drift event.

---

## 2.20 IMPLEMENTATION STATUS

The stack distinguishes implemented, planned, deferred, and future-work behaviors.

### 2.20.1 Implemented behaviors at v0.1.0

| Surface | Status |
| --- | --- |
| WiseOrder Protocol kernel | **[IMPLEMENTED]** in `intellagent_runtime/kernel.py` |
| Class A/B/C/D verifiers | **[IMPLEMENTED]** |
| Action governance (AG1, AG3) | **[IMPLEMENTED]** |
| Commit chain (CC1–CC4) | **[IMPLEMENTED]** |
| Audit memory + verify_chain | **[IMPLEMENTED]** in `memory.py` |
| Refusal store + sealing | **[IMPLEMENTED]** in `refusal.py` |
| Authorization gate | **[IMPLEMENTED]** in `authorization.py` |
| RuntimeLoop + search | **[IMPLEMENTED]** in `runtime.py` |
| CLI: `init`, `state`, `propose`, `transition`, `audit`, `refuse` | **[IMPLEMENTED]** in `cli.py` |
| Static / Manual / InMemory proposers | **[IMPLEMENTED]** in `proposer.py` |
| Transformer proposer + 4 providers | **[IMPLEMENTED]** in `proposer_transformer.py` |
| 23 conformance vectors | **[IMPLEMENTED]** in `vectors/` |
| 3 interop fixtures + manifests + reports | **[IMPLEMENTED]** in `interop/` |
| 10-entry canonicalization golden corpus | **[IMPLEMENTED]** in `canonicalization/` |
| Workforce admission validator | **[IMPLEMENTED]** in `tools/check_workforce.py` |
| Workforce sandbox stress (900 checks) | **[IMPLEMENTED]** in `tools/workforce_sandbox_stress.py` |
| Documentation Code Standard enforcer | **[IMPLEMENTED]** in `tools/check_no_pseudocode.py` |
| Determinism contract | **[IMPLEMENTED]** + live-verified |
| 135 pytest tests | **[IMPLEMENTED]** in `tests/` |

### 2.20.2 Partially-implemented behaviors

| Surface | Status |
| --- | --- |
| B2 enforcement (bidirectional) | **[PARTIALLY IMPLEMENTED]**: unidirectional only at v0.1 (`CONFLICTED` enforced; rejecting `SUPPORTED`-with-contradictions deferred to v0.2) |
| Object-level provenance enforcement | **[PARTIALLY IMPLEMENTED]**: transition-level enforced; object-level deferred |
| Workforce hardening v0.2 | **[PARTIALLY IMPLEMENTED]**: stress harness identifies validator gaps; native validator migration in progress |
| Demo suite | **[PARTIALLY IMPLEMENTED]**: 8 of 10 demos runnable; demos 3 and 10 are v0.2+ targets |

### 2.20.3 Policy-only behaviors

| Surface | Status |
| --- | --- |
| Workforce admission rules | **[POLICY-ONLY]** at the validator layer; not host-kernel-enforced |
| Canon protection (no canon modification) | **[POLICY-ONLY]** in workforce checker |
| One-agent-one-duty | **[POLICY-ONLY]** in agent governance workforce |
| Real-agent dry-run | **[POLICY-ONLY]** at v0.1 |

### 2.20.4 Kernel-enforced behaviors

| Surface | Status |
| --- | --- |
| OS isolation via `sandbox-exec` | **[KERNEL-ENFORCED]** on macOS in `os_isolation_runtime.py` |
| Resource limits via `setrlimit` on `execve` | **[KERNEL-ENFORCED]** in `resource_limit_runtime.py` |
| Three concentric containment rings | **[KERNEL-ENFORCED]** for ring 2 (sandbox-exec) and ring 3 (setrlimit); ring 1 (policy) is **[POLICY-ONLY]** |

### 2.20.5 Future-work behaviors

| Surface | Status |
| --- | --- |
| `EnsembleProposer` | **[FUTURE WORK]** v0.2+ |
| `RetrievalProposer` | **[FUTURE WORK]** v0.2+ |
| `RefusalAwareTransformerProposer` | **[FUTURE WORK]** v0.2+ |
| Second-language canonicalizer (Rust, TypeScript, Go) | **[FUTURE WORK]** v0.2+ |
| Linux `bwrap`/seccomp parity for OS isolation | **[FUTURE WORK]** v0.2+ |
| Multi-tenant context scoping | **[FUTURE WORK]** v0.3+ |
| Distributed audit memory | **[FUTURE WORK]** v0.3+ |
| Cross-machine real-provider determinism | **[FUTURE WORK]** v0.3+ (requires provider-side cooperation) |
| Strict RFC 8785 JCS Python implementation | **[FUTURE WORK]** v0.2+ (coordinated drift event from sort_keys+compact) |

### 2.20.6 Explicitly-unsupported behaviors

| Surface | Status |
| --- | --- |
| AGI claims | **[EXPLICITLY UNSUPPORTED]** (TP10) |
| Consciousness claims | **[EXPLICITLY UNSUPPORTED]** (TP10) |
| Universal correctness | **[EXPLICITLY UNSUPPORTED]** (TP10) |
| Production deployment readiness | **[EXPLICITLY UNSUPPORTED]** at v0.1 |
| Network egress in default runtime | **[EXPLICITLY UNSUPPORTED]** |
| Cross-version trust auto-promotion | **[EXPLICITLY UNSUPPORTED]** (TP8) |

Unimplemented behaviors are NOT represented as operational. Every audit-posture label is enforceable via the corresponding test or validator (or, for explicitly-unsupported items, by the absence of any code path).

---

## 2.21 KNOWN LIMITATIONS

The stack publishes its limitations explicitly. None is a defect; each is a documented scope boundary with a defined v0.2+ resolution path.

1. **Provenance enforcement is unidirectional at v0.1.** Object-level provenance is not enforced. Transition-level captured. v0.2 target.
2. **No `EnsembleProposer` in v0.1.** Single-proposer search ships; multi-proposer fan-in deferred. Architecture pinned in `INTELLAGENT-PROPOSERS.md` §10.
3. **B2 enforcement is unidirectional.** `CONFLICTED` enforced; `SUPPORTED`-with-contradictions not yet rejected. v0.2 target.
4. **No replay across providers.** Per-provider determinism only. Cross-machine real-provider determinism is out of contract.
5. **No multi-tenant scoping.** v0.1 is single-tenant. v0.3+ target.
6. **No distributed audit memory.** v0.1 is single-host, single-writer. v0.3+ target.
7. **WISEATA F-1 unresolved.** WISEATA registered as Class B only due to canonicalization incompatibility with v0.1.0 JCS requirement. Resolution requires either WISEATA canonicalization migration or v0.2 multi-scheme registration.
8. **Optional `evidence.report_sha256` helper not shipped.** Operators currently compute the combined report digest manually. v0.2 target (`tools/compute_evidence_sha.py`).
9. **Real-provider runs are not byte-deterministic across machines.** Per §2.13. Mitigation: capture full provider metadata in `proposal_cost`.
10. **No GUI.** CLI-only at v0.1.
11. **Canonicalization is Python-only.** v0.1 ships `sort_keys=True` + compact JSON, not strict RFC 8785 JCS. Cross-language ports (Rust, TypeScript, Go) do not yet exist. The 10-entry golden corpus makes the gap mechanically detectable. Full treatment: `CROSS-LANGUAGE-CANONICALIZATION-v0.1.md`.

These eleven limitations constitute the published scope boundary of v0.1.0. Each is enforceable at the audit-posture-label level (via §2.20).

---

## 2.22 FUTURE WORK

Future work is clearly separated from normative semantics. No future-work item contaminates v0.1.0 conformance or redefines an implemented guarantee.

### 2.22.1 v0.2 architecture slate

Pinned items for the next version event:

- Bidirectional B2 enforcement (rejecting `SUPPORTED`-with-contradictions).
- Object-level provenance enforcement (Class A).
- `EnsembleProposer` with multi-Provider backing.
- `RetrievalProposer` against audit memory.
- `RefusalAwareTransformerProposer` (refusal-corpus prompt injection).
- Second-language canonicalizer (Rust-first port; must reproduce the 10-entry golden corpus byte-identically).
- Multi-tenant context scoping (foundation work).
- Workforce hardening v0.2 native validator migration (in progress).

### 2.22.2 v0.3+ horizon

Long-horizon items not yet on a version slate:

- Distributed audit memory (Class C consensus across writers).
- Cross-machine real-provider determinism (requires provider-side cooperation).
- Protocol federation (multi-WiseOrder-implementation interop).
- Strict RFC 8785 JCS Python implementation (coordinated migration from sort_keys+compact).
- TypeScript and Go canonicalizers matching the golden corpus.

### 2.22.3 Research directions (not promised)

- Embedding-based retrieval over audit memory (determinism vs semantic search tension).
- Probabilistic refusal calibration.
- Adversarial-proposer detection.
- Verifier-side machine learning.
- Cross-protocol bridging.

These are research directions, not features. They may inform future architecture work but carry no v0.x commitment.

### 2.22.4 Separation discipline

No future-work item:
- Is documented in normative-section bodies.
- Is exercised by any test in v0.1.0.
- Is referenced by any conformance vector.
- Is required by any implementation declaration.

Future work lives in §2.22 only. Contamination of normative sections with future-work claims is itself a TR-7 unsupported-claim-surface event.

---

## 2.23 SECURITY CONSIDERATIONS

Security claims are bounded. The stack does not claim arbitrary safety.

### 2.23.1 Trust assumptions

- The host OS is trusted at the kernel level. Compromise of the host invalidates all in-tree audit memory.
- SHA-256 collision resistance is taken as given.
- RFC 8785 JCS canonicalization correctness is taken as given.
- Independent reviewers are assumed to exist and to have access to the published bundle.
- No assumption is made about provider security; real-provider runs are out-of-contract for byte-deterministic replay.

### 2.23.2 Attack surfaces

- **Input surface.** Operator inputs (queries, work orders, configurations). Defended by input grammar (§§ in INPUT-GRAMMAR-v0.1.md) and workforce admission.
- **Proposer surface.** Untrusted proposer outputs. Defended by kernel verification.
- **Authority surface.** Authorization claims. Defended by gate evaluation + AG1/AG3 enforcement.
- **State surface.** On-disk state files. Defended by `state_id` content-addressing + tamper detection.
- **Audit surface.** On-disk audit memory. Defended by `verify_chain` + tamper detection.
- **Canon surface.** Repository canon paths. Defended by workforce admission rules.

### 2.23.3 Tampering risks

- **Audit tampering.** Detected by `verify_chain`. Mitigation: chain integrity check on every initialization.
- **State tampering.** Detected by `state_id` recomputation. Mitigation: load-time validation.
- **Refusal tampering.** A modified refusal record breaks its `refusal_sha256`. Detected on read.
- **Canon tampering.** A modification of canon paths is detected by `tools/check_workforce.py` and by drift checks (`make verify-drift`).

### 2.23.4 Privilege risks

- **Privilege escalation via authorization forgery.** Mitigation: AG1 (no auto-authorization), AG3 (source_id required).
- **Cross-role action.** Mitigation: one-agent-one-duty in workforce; identity-scoped admission.
- **Work-order expansion.** Mitigation: per-work-order `allowed_commands`, `allowed_files`, `expiry`. Expired work orders refuse admission.

### 2.23.5 Execution risks

- **Sandbox escape.** Mitigation: defense-in-depth via three concentric containment rings (policy + sandbox-exec + setrlimit).
- **Resource exhaustion.** Mitigation: setrlimit on `execve`.
- **Filesystem boundary violation.** Mitigation: sandbox-exec profile + workforce `allowed_files` admission.
- **Network egress.** Mitigation: sandbox-exec profile denies network by default.

### 2.23.6 Replay risks

- **Replay forgery.** A reviewer cannot trust a claimed replay without reproducing it. Mitigation: published canonical inputs (clock, ID source, seed, provider, prompt) + reviewer reproduction.
- **Provider-side replay drift.** Real-provider runs are non-deterministic across machines. Mitigation: deterministic-mock-provider replay path; full provider metadata captured.

### 2.23.7 Provider risks

- **Provider compromise.** A compromised provider may return malicious candidates. Mitigation: kernel rejects malformed candidates; refusal corpus accumulates.
- **Provider exfiltration.** A network-using provider may leak prompts. Mitigation: `DeterministicMockProvider` for replay scenarios; `LocalOpenAICompatibleProvider` for air-gapped operation; real providers used only when network egress is acceptable.
- **Provider determinism breaks.** Real providers do not guarantee determinism. Mitigation: provider metadata captured; replay uses deterministic mock.

### 2.23.8 Bounded security claims

The stack claims:

- Tamper-evident audit memory.
- Tamper-evident state.
- Sealed refusal records.
- Defense-in-depth containment for action execution.
- Mechanical drift detection.

The stack does NOT claim:

- Resistance to host compromise.
- Resistance to cryptographic primitive breaks.
- Resistance to compromise of all reviewers.
- Resistance to physical attack.
- Resistance to network adversaries (in deployments that add network).

---

## 2.24 REPRODUCIBILITY

A reviewer must be able to reproduce every claim from the published bundle alone.

### 2.24.1 Reproduction steps

1. Clone the repository at the release tag:
   ```
   git clone <repo> wiseorder-protocol
   cd wiseorder-protocol
   git checkout v0.1.0
   ```
2. Set up the environment:
   ```
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```
3. Run the full trust surface:
   ```
   make ci
   ```
4. Verify suite fingerprints:
   ```
   grep vectors_suite_sha256 reports/conformance-report.json
   grep manifests_suite_sha256 interop/reports/interop-report.json
   grep corpus_sha256 canonicalization/reports/golden-report.json
   ```
   Compare each value against the published values in `RELEASE-STATUS-v0.1.md` §6.

5. Reproduce the determinism cross-run hash:
   ```
   tools/demo_transformer_proposer.py --state-dir /tmp/demoA
   tools/demo_transformer_proposer.py --state-dir /tmp/demoB
   sha256sum /tmp/demoA/intellagent_audit/entries/*.json
   sha256sum /tmp/demoB/intellagent_audit/entries/*.json
   # both must equal sha256:b71c7134…
   ```

### 2.24.2 Deterministic replay instructions

For replay scenarios:

- Pin the clock via `set_clock(ClockSource(lambda: "2026-05-10T00:00:00Z"))`.
- Pin the ID source via `set_id_source(IDSource(lambda: f"id-{counter()}"))`.
- Pin the seed in any RNG used by proposers.
- Use `DeterministicMockProvider` for transformer proposers.
- Pin the prompt and query input.

Under these conditions, `make replay` (where applicable) produces byte-identical outputs.

### 2.24.3 Environment assumptions

- macOS 12+ or Linux (sandbox-exec features are macOS-specific; Linux equivalent is future work).
- Python 3.10+.
- Standard POSIX filesystem.
- `make`, `git`, `sha256sum` available.
- ~50 MB disk space for full bundle + working state.

### 2.24.4 Dependency expectations

- No third-party Python packages required for the default runtime path.
- Pytest required for `make test`.
- Optional real-provider integrations require respective SDKs (OpenAI, Anthropic).
- All dependencies pinned in `pyproject.toml`.

### 2.24.5 Seed behavior

- Where RNG is used (proposer-side ranking, etc.), the seed is captured in `ProposalProvenance.seed`.
- Replay reproduces the seed; the RNG produces identical sequences; the proposer produces identical candidates.

### 2.24.6 Hashing verification

A reviewer who runs `make ci` and reproduces the three suite fingerprints + the determinism cross-run hash has verified the entire v0.1.0 trust surface.

A mismatch is a TR-1 silent-drift event and triggers the disclosure procedure (`TRUST-LAW-v0.1.md` §24).

---

## 2.25 TESTING REQUIREMENTS

The test suite is the operational ground truth of the spec.

### 2.25.1 Required test categories

- **Replay tests.** Two independent runs under pinned inputs produce byte-identical outputs. Implementation: `tests/test_intellagent_runtime.py::test_deterministic_replay`.
- **Conformance tests.** Every vector produces the expected status. Implementation: `tests/test_run_conformance.py`.
- **Interoperability tests.** Every fixture passes all 7 cross-layer checks. Implementation: `tests/test_interop.py`.
- **Determinism tests.** Cross-run hash equality. Verified live in `RELEASE-STATUS-v0.1.md` §6.
- **Authorization tests.** AG1, AG3 surfaces produce refusals. Implementation: `tests/test_intellagent_authorization.py`.
- **Refusal tests.** Refusal records carry non-empty `challenge_surface_sha256`. Implementation: `tests/test_intellagent_kernel.py` and `test_intellagent_runtime.py`.
- **Chain integrity tests.** Tampering at any position is detected. Implementation: `tests/test_intellagent_memory.py`.
- **Canonicalization tests.** 10-entry golden corpus + edge cases. Implementation: `tests/test_canonicalization_golden.py`.

### 2.25.2 Test count at v0.1.0

| Module | Count |
| --- | ---: |
| `test_validate_vectors.py` | 6 |
| `test_validate_implementations.py` | 13 |
| `test_run_conformance.py` | 4 |
| `test_interop.py` | 11 |
| `test_intellagent_state.py` | 9 |
| `test_intellagent_memory.py` | 6 |
| `test_intellagent_kernel.py` | 19 |
| `test_intellagent_authorization.py` | 6 |
| `test_intellagent_runtime.py` | 7 |
| `test_intellagent_cli.py` | 7 |
| `test_intellagent_proposer_transformer.py` | 21 |
| `test_canonicalization_golden.py` | 22 |
| **Total** | **135** |

All passing in approximately 1.30 seconds. No xfails, no skips, no flakes.

### 2.25.3 Coverage requirements

- Every kernel invariant (§2.8) is exercised by at least one passing and one failing case.
- Every action-governance invariant (AG1, AG3) is exercised by at least one rejecting test.
- Every refusal condition (§2.16.1) is exercised.
- Every chain-tampering position is exercised.

### 2.25.4 CI integration

`make ci` chains:

```
make no-pseudocode → make test → make conformance → make interop → make canonicalization-check
```

Pass on this chain = the v0.1.0 trust surface holds on this commit.

### 2.25.5 Drift verification

`make verify-drift` runs `make conformance` + `make interop` + `git diff --exit-code -- reports/ interop/`. Non-zero exit = drift.

---

## 2.26 RELEASE REQUIREMENTS

Release gates govern the boundary between development and tagged release.

### 2.26.1 Release gates

Per `RELEASE-CHECKLIST-v0.1.md` §1:

1. **Architecture lock.** SPEC.md, vectors, status registry, interop fixtures, canonicalization scheme are immutable within the version.
2. **Test suite.** All tests pass; no skips, no flakes; ~1.3s end-to-end.
3. **Conformance.** All vectors pass; suite fingerprint stable.
4. **Interoperability.** All fixtures pass; suite fingerprint stable.
5. **Documentation Code Standard.** Zero pseudocode violations across all markdown.
6. **Determinism.** Live-verified cross-run hash equality.
7. **Drift.** `make verify-drift` clean.

All seven gates green at the release commit.

### 2.26.2 CI requirements

- `make ci` is the canonical CI entry point.
- Exit non-zero on any failure.
- Output the three suite fingerprints + determinism cross-run hash.

### 2.26.3 Vector requirements

- Vectors are sealed within a version.
- Adding a vector that exercises a new invariant is permissible within a version (additive).
- Modifying an existing vector is a protocol-level event (v0.x → v0.x+1).
- Removing a vector is a protocol-level event.

### 2.26.4 Replay requirements

- Cross-run hash equality verified live before tagging.
- Determinism contract documented + tested.
- `DeterministicMockProvider` available as the in-contract replay path.

### 2.26.5 Documentation requirements

- Every normative claim cites the canon doc that governs it.
- Every audit-posture label is enforceable via test or validator.
- Documentation Code Standard enforced via `make no-pseudocode`.
- Release notes published alongside the tag, pointing at this spec + `RELEASE-STATUS-v0.1.md` + `RELEASE-CHECKLIST-v0.1.md`.

### 2.26.6 Reproducibility requirements

- Reviewer can clone the bundle and reproduce all claims via the steps in §2.24.
- Suite fingerprints match published values byte-identically.
- Cross-run hash matches published value byte-identically.

### 2.26.7 Audit-status requirements at release

At v0.1.0 release commit:

- Winstack: `audit_status: NOT_AUDITED`.
- WISEATA: `audit_status: NOT_AUDITED`.

Promotion to `CONFORMANT` requires evidence (ID3) and is a post-release event.

### 2.26.8 Trust account state at release

- New trust account opens at the v0.1.0 tag (TP6 — observable trust reset).
- v0.1 trust does not auto-promote to v0.2 (TP8).
- TR-event-free intervals begin from the tag.
- First independent reviewer reproduction is the first deposit.

---

## 3. STATUS

| Field | Value |
| --- | --- |
| Document | INTELLAGENT + WISEORDER unified normative specification |
| Version | v1.0 |
| Conformant to | INTELLAGENT-MASTER-SPEC-STANDARD-v1.0 |
| Subject release | v0.1.0 |
| Classification | Normative |
| State | LOCKED (architecture) — trust accumulation begins at v0.1.0 tag |
| Date | 2026-05-10 |

---

A specification that cannot be tested, replayed, inspected, challenged, or independently implemented is documentation theater. This specification can be tested (`make ci`), replayed (cross-run hash live-verified), inspected (every claim cites its canon doc), challenged (the threat model and trust law surface every disclosure path), and independently implemented (`Winstack` and `WISEATA` are registered, with `audit_status: NOT_AUDITED` until evidence accumulates). Refusal is success.
