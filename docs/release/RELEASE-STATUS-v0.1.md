# RELEASE-STATUS v0.1

**Status:** Pre-release status report.
**Date of run:** 2026-05-06.
**Companion:** [`RELEASE-CHECKLIST-v0.1.md`](./RELEASE-CHECKLIST-v0.1.md) — operational gate definitions.
**Recommendation:** **Ready for first external engineering scrutiny.** All hard gates green; documented limitations deferred to v0.2+.

---

## 1. Architecture status

| Layer | Status |
| --- | --- |
| WiseOrder Protocol v0.1.0 (`SPEC.md`) | **LOCKED** unless implementation reality breaks it |
| Intellagent architecture proposal (`INTELLAGENT.md`) | Draft canon; 16 sections; 9 formal primitives; non-goals explicit |
| Runtime specification (`INTELLAGENT-RUNTIME.md`) | Implementation-faithful; cross-checked against `intellagent_runtime/` |
| Proposer architecture (`INTELLAGENT-PROPOSERS.md`) | Implementation-realistic Python throughout (no pseudocode) |
| Transformer proposer spec (`TRANSFORMER-PROPOSER-v0.1.md`) | Mapped 1:1 to `intellagent_runtime/proposer_transformer.py` |
| Evaluation framework (`INTELLAGENT-EVALUATION.md`) | 9 axes, 10 scenarios, 8 metrics, fixture format defined |
| Demonstration suite (`INTELLAGENT-DEMOS.md`) | 10 demos; 8 runnable today, 2 marked v0.2+ targets |
| Documentation Code Standard (`TOOLS.md`) | Enforced by `tools/check_no_pseudocode.py` and `make no-pseudocode` |

**Summary:** Architecture phase complete. No further protocol changes scheduled for v0.1.

---

## 2. Runtime status

| Module | Lines | Purpose |
| --- | ---: | --- |
| `intellagent_runtime/canonical.py` | ~120 | Deterministic JSON, SHA-256, atomic writes, clock + ID injection |
| `intellagent_runtime/transitions.py` | ~95 | `Action`, `Authorization`, `EpistemicTransition`, `TransitionResult` |
| `intellagent_runtime/refusal.py` | ~85 | `RefusalRecord`, `RefusalStore`, challenge-surface hashing |
| `intellagent_runtime/state.py` | ~145 | `EpistemicState`, `ObjectStore`, `StateStore`, tampering detection |
| `intellagent_runtime/memory.py` | ~135 | `AuditEntry`, `AuditMemory`, `ChainCorrupt`, append + `verify_chain` |
| `intellagent_runtime/kernel.py` | ~310 | `WiseOrderKernel` adapter; per-class A/B/C/D verifiers |
| `intellagent_runtime/authorization.py` | ~165 | `AuthorizationGate`, `AlwaysDenyPolicy`, `AllowlistPolicy` |
| `intellagent_runtime/proposer.py` | ~95 | `Proposer` Protocol + `StaticProposer` + `ManualProposer` + `InMemoryProposer` |
| `intellagent_runtime/proposer_transformer.py` | ~520 | `Provider` Protocol + 4 providers + `TransformerProposer` + benchmark hook |
| `intellagent_runtime/runtime.py` | ~160 | `Query`, `SearchResult`, `RuntimeLoop`, `apply_transition`, `validate_transition` |
| `intellagent_runtime/cli.py` | ~265 | `intellagent` CLI: `init` `state` `propose` `transition` `audit` `refuse` |
| `intellagent_runtime/policies/` | 2 files + README | `always_deny.json`, `test_allowlist.json` |
| `intellagent_runtime/prompts/` | 5 files | System preamble + Class A/B/C/D fragments |

**Total runtime:** roughly 2,100 lines of Python, plus 7 prompt + policy support files. Single-host, no network, no GUI.

**CLI surface:** 6 subcommands, all with `--help`, all match documented behavior.

**Determinism contract:** byte-identical audit memory under (fixed clock + fixed ID source + fixed seed + same provider + same prompt) — verified.

---

## 3. Test counts

| Test module | Count |
| --- | ---: |
| `tests/test_validate_vectors.py` | 6 |
| `tests/test_validate_implementations.py` | 13 |
| `tests/test_run_conformance.py` | 4 |
| `tests/test_interop.py` | 11 |
| `tests/test_intellagent_state.py` | 9 |
| `tests/test_intellagent_memory.py` | 6 |
| `tests/test_intellagent_kernel.py` | 19 |
| `tests/test_intellagent_authorization.py` | 6 |
| `tests/test_intellagent_runtime.py` | 7 |
| `tests/test_intellagent_cli.py` | 7 |
| `tests/test_intellagent_proposer_transformer.py` | 21 |
| `tests/test_intellagent_*.py` (intellagent runtime subtotal) | 75 |
| `tests/test_canonicalization_golden.py` | 22 |
| **Repo total** | **135 / 135 passing** |

Run time: **~1.30s** end-to-end. No xfails, no skips, no flakes.

---

## 4. Conformance status

| Field | Value |
| --- | --- |
| Vectors | **23 / 23** passing |
| Implementations | **2 / 2** passing (`Winstack`, `WISEATA`; both `NOT_AUDITED`) |
| `vectors_suite_sha256` | `sha256:37d3ec45ecca12d256b7df1c02ac0f0d1474f71b68510e9475fa449b8eb1331b` |
| Status registry coverage | **complete** for all 4 classes |
| Per-class invariant coverage | A1–A3, CS1–CS3, B1–B3, C1–C4, D1–D5, CC1–CC4, AG1–AG3, §9 telemetry — **all** exercised |
| Overall | `PASS` |

`make conformance` regenerates `reports/conformance-report.json` byte-stably. Drift detection via `git diff --exit-code -- reports/` is part of CI.

---

## 5. Interop status

| Field | Value |
| --- | --- |
| Fixtures | **3 / 3** passing |
| `manifests_suite_sha256` | `sha256:74eaaa62271f23172232bda43ba3340543e66c46ba1e2f5e6da18d3447a6ba29` |
| Per-fixture checks | All 7 cross-layer checks PASS for each fixture |
| F-1 enforcement | **active** at both layers (generation refuses WISEATA-Class-A; check rejects same) |
| Overall | `PASS` |

`make interop` regenerates `interop/reports/interop-report.json` byte-stably.

---

## 6. Determinism status

| Property | Status |
| --- | --- |
| Canonical JSON byte-stability | Verified (sorted keys, compact separators, UTF-8) |
| State `state_id` content-addressed | Verified (`compute_state_id` is a pure function of `objects`) |
| Audit chain `this_entry_sha256` content-addressed | Verified (excludes self field, includes prev pointer) |
| Manifest content-addressed | Verified (each manifest's `manifest_sha256` recomputable from disk bytes) |
| Suite fingerprints stable | `vectors_suite_sha256` and `manifests_suite_sha256` byte-identical across runs |
| Replay test | `test_deterministic_replay` PASS — two runs with same fixed clock + seed produce byte-identical audit memory |
| Live cross-run hash check | Hash over audit-entry bytes from two clean tmp dirs: `sha256:b71c7134ef2c33ea5fcc9a3eb723efe6294ba18759ed91d1f64bdfe826107ba5` (both runs) |
| Canonicalization golden corpus | 10 entries pinned; `corpus_sha256: sha256:c95685bff48c15abc313c462908b05ac309250bc660c2d802ae51af5a8038b09`; verified by `make canonicalization-check` |

**Documented nondeterministic surfaces:**

- Real-provider sampling (OpenAI / Anthropic): non-byte-deterministic across machines even with fixed seeds; mitigated by capturing full provider metadata in `proposal_cost`.
- Wall-clock timestamps (`utcnow_iso8601`) when `set_clock` is not pinned: non-deterministic by design; pinning is opt-in for replay scenarios.

---

## 7. Demo status

| # | Demo | Status (v0.1) | Runnable today |
| - | --- | --- | --- |
| 1 | Missing Authorization | PASS | ✓ |
| 2 | Contradictory Evidence | PASS (unidirectional B2) | ✓ (CONFLICTED-without-preservation form) |
| 3 | Missing Provenance | GAP — v0.2+ target | partial (transition-level captured) |
| 4 | Invalid Class D Conduct | PASS | ✓ |
| 5 | Tampered Audit Chain | PASS | ✓ |
| 6 | Consensus Without Action Permission | PASS | ✓ |
| 7 | Uncertainty Preservation | PASS | ✓ |
| 8 | Hallucination Containment | PASS | ✓ |
| 9 | Deterministic Replay | PASS | ✓ |
| 10 | Multi-Proposer Disagreement | PASS (single-proposer-with-multi-candidate form) — `EnsembleProposer` is v0.2+ | ✓ |

**8 demos runnable today** with full kernel-rejection observable; **2 demos** (3, 10) marked as v0.2+ extension targets and clearly documented in `INTELLAGENT-DEMOS.md`.

`tools/demo_transformer_proposer.py` exercises Demo 4 + Demo 8 + Demo 9 in a single end-to-end run, exit `0`.

---

## 8. Known limitations

Reproduced verbatim from `RELEASE-CHECKLIST-v0.1.md` §9 for visibility:

1. Provenance enforcement is unidirectional at v0.1 (object-level not enforced).
2. No `EnsembleProposer` in v0.1.
3. `B2` enforcement is unidirectional (CONFLICTED enforced; `SUPPORTED` with contradictions not yet rejected).
4. No replay across providers (per-provider determinism only).
5. No multi-tenant scoping.
6. No distributed audit memory.
7. WISEATA F-1 unresolved (WISEATA registered as Class B only).
8. Optional `evidence.report_sha256` helper not shipped.
9. Real-provider runs are not byte-deterministic across machines.
10. No GUI.
11. **Canonicalization is Python-only.** The v0.1 runtime canonicalizer (`intellagent_runtime.canonical.canonical_json_bytes`) is `sort_keys=True` + compact-JSON UTF-8, not strict RFC 8785 JCS. Cross-language ports (Rust, TypeScript, Go) do not yet exist; until at least one non-Python implementation reproduces the committed golden bytes, interoperability claims are canonicalization-monolingual. The 10-entry golden corpus at `canonicalization/` makes this gap mechanically detectable. Full treatment: [`CROSS-LANGUAGE-CANONICALIZATION-v0.1.md`](./CROSS-LANGUAGE-CANONICALIZATION-v0.1.md).

These are documented scope boundaries, not defects. Each has a clear v0.2+ resolution path.

---

## 9. Deferred work

Items intentionally deferred to v0.2 or beyond:

| Area | Deferred item | Rationale |
| --- | --- | --- |
| Kernel | Object-level provenance enforcement (Class A) | F-1-style governance correction; minor schema extension |
| Kernel | Bidirectional `B2` (reject SUPPORTED with contradictions) | Same |
| Proposer | `EnsembleProposer` with multiple Provider backends | Architectural design pinned in `INTELLAGENT-PROPOSERS.md` §10; impl is straightforward |
| Proposer | `RetrievalProposer` against audit memory | Architectural design pinned in `INTELLAGENT-PROPOSERS.md` §8 |
| Proposer | Refusal-corpus prompt injection (v0.1 stores; v0.2+ injects) | `RefusalAwareTransformerProposer` shape already in `TRANSFORMER-PROPOSER-v0.1.md` |
| Tooling | `tools/compute_evidence_sha.py` helper for combined report digest | Eliminates manual sha256sum step |
| Tooling | `tools/new_fixture.py` scaffolder | Reduces fixture authoring friction |
| Runtime | Multi-tenant context scoping | Multi-tenant deployments out of v0.1 scope |
| Runtime | Distributed audit memory (Class C consensus across writers) | Single-host runtime is v0.1 floor |
| Evaluation | `pytest-cov` coverage metric | Reporting refinement |
| Packaging | PyPI publication | Post-v0.1 decision |
| Packaging | Docker image | Post-v0.1 decision |
| Canonicalization | Strict RFC 8785 JCS Python implementation | v0.1 ships sort_keys+compact; strict-JCS migration is a coordinated drift event |
| Canonicalization | Rust canonicalizer matching golden corpus | First non-Python port; highest-priority drift detector |
| Canonicalization | TypeScript canonicalizer matching golden corpus | ECMA-262 number-format reference; surfaces Python ↔ JCS divergence |
| Canonicalization | Go canonicalizer matching golden corpus | Library-default drift surface (`encoding/json` HTML escaping etc.) |

The list is conservative on purpose. v0.1 ships only what is verifiable today.

---

## 10. Live gate run (this report)

Fresh run on the release commit, captured here as evidence:

```
make no-pseudocode
  → OK: scanned 25 markdown file(s); no pseudocode markers found in Python code blocks.
pytest tests/
  → 135 passed in 1.30s
make conformance
  → vectors: 23/23 passed; implementations: 2/2 passed; overall_status: PASS
  → vectors_suite_sha256: sha256:37d3ec45ecca12d256b7df1c02ac0f0d1474f71b68510e9475fa449b8eb1331b
make interop
  → fixtures: 3/3 passed; overall_status: PASS
  → manifests_suite_sha256: sha256:74eaaa62271f23172232bda43ba3340543e66c46ba1e2f5e6da18d3447a6ba29
make canonicalization-check
  → 10 corpus entries verified
  → corpus_sha256: sha256:c95685bff48c15abc313c462908b05ac309250bc660c2d802ae51af5a8038b09
tools/demo_transformer_proposer.py
  → search 1 (legitimate accepted): PASS
  → search 2 (illegitimate refused): PASS
  → audit chain integrity: PASS
  → overall: PASS  (exit 0)
determinism cross-run hash
  → /tmp/demoA audit_sha: b71c7134ef2c33ea5fcc9a3eb723efe6294ba18759ed91d1f64bdfe826107ba5
  → /tmp/demoB audit_sha: b71c7134ef2c33ea5fcc9a3eb723efe6294ba18759ed91d1f64bdfe826107ba5
  → MATCH
```

---

## 11. Release recommendation

**Recommendation: PROCEED to first external engineering scrutiny under tag `v0.1.0`.**

Rationale:

- All 7 gates in `RELEASE-CHECKLIST-v0.1.md` §1 are green on the current commit.
- All 5 reproducibility checks in §2 pass.
- 113 / 113 tests pass with no skips, no flakes, in ~1.3s.
- 23 / 23 vectors pass; 2 / 2 implementations pass; 3 / 3 fixtures pass.
- Determinism is verified by live cross-run hash equality.
- 8 of 10 demos run end-to-end today; the 2 that don't are clearly marked v0.2+ targets, not defects.
- Documentation Code Standard is enforced; 0 pseudocode violations across 20 markdown files.
- Known limitations are documented and bounded; none are surprises.
- The architecture lock holds; no defect requires modifying `SPEC.md`.

What "external engineering scrutiny" means here: independent reviewers can clone the repo, run `make ci`, observe matching fingerprints against the committed reports, run any of the 5 public-launch demos, and compare their bundle SHA-256 against the published values. The whole thing is reproducible offline on a single laptop.

The runtime does not claim to be intelligent, complete, safe in the wider sense, or production-ready in any deployment sense. It claims to be a buildable, testable, deterministic, kernel-governed state machine over WiseOrder Protocol v0.1.0 — and to make that claim mechanically inspectable.

That is what v0.1 is for.

---

*Pre-release status report. Tag the commit, publish the release notes pointing at this document and the checklist, and invite review. Architecture is locked. Tests are green. Demos run. Refusal is success.*
