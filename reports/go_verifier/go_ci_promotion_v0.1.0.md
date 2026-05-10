# Go Verifier CI Promotion Report — v0.1.0

**Work Order:** 014 — Promote Go Verifier into CI
**Timestamp (UTC):** 2026-05-10T20:30:00Z
**Overall Result:** **PASS**
**Authority:** This document is the evidence record that the Go verifier has been promoted into `make ci` and the repository passes cold from a clean state with **all four** first-party independent verification tracks gated.

---

## 1. Go Version

```
go version go1.26.3 darwin/arm64
```

## 2. Cold Confirmation Commands

| # | Command | Exit code | Result |
|---|---|---|---|
| 1 | `go test ./go_verifier/...` | 0 | 38 / 38 tests passing |
| 2 | `go run ./go_verifier verify-vectors` | 0 | 33 / 33 vectors |
| 3 | `go run ./go_verifier verify-corpus` | 0 | 10 / 10 corpus entries |
| 4 | `go run ./go_verifier fingerprints` | 0 | OVERALL: MATCH |
| 5 | `make go-verifier-check` | 0 | PASS |
| 6 | `make go-verifier-fingerprints` | 0 | PASS |
| 7 | `make ci` (with `go-verifier-check` now included) | 0 | 11 stages PASS |
| 8 | `make demo` | 0 | 6 steps PASS, 3 fingerprints MATCH |
| 9 | `git status --short` | 0 | working tree state captured |

## 3. CI Stages After Promotion

| # | Stage | Result |
|---|---|---|
| 1 | `no-pseudocode` | PASS |
| 2 | `test` | PASS — 271 tests |
| 3 | `conformance` | PASS — 33 vectors |
| 4 | `interop` | PASS — 3 fixtures |
| 5 | `canonicalization-check` | PASS — 10 corpus entries |
| 6 | `minimal-verifier-check` | PASS — 33 vectors via Python independent re-derivation |
| 7 | `replay-diff-check` | PASS — 9 self-check fixtures |
| 8 | `binary-fixture-check` | PASS — 4 fixtures |
| 9 | `sandbox-escape-check` | PASS — 29 attempts (25 hostile refused, 4 controls allowed) |
| 10 | `rust-verifier-check` | PASS — cargo test (26), verify-vectors (33/33), verify-corpus (10/10) |
| 11 | **`go-verifier-check`** | **PASS — go test (38), verify-vectors (33/33), verify-corpus (10/10); first-party independent track** |

## 4. Go Test Result

**38 / 38** passing across four packages:
- `internal/jcs` — 11 unit tests (canonicalization + SHA-256 helpers)
- `internal/vectors` — 14 unit tests (Class A/B/C/D verdict logic)
- `internal/fingerprints` — 4 unit tests (count assertions + ComputeAll)
- `tests/integration` — 9 integration tests (binary drive + import-line scan)

The integration test `TestReproducesAllThreeFingerprints` asserts MATCH on all three frozen anchors, so `go-verifier-check` (which runs `go test ./go_verifier/...`) covers the fingerprint requirement implicitly. No separate `go-verifier-fingerprints` target needed in CI.

## 5. Go Vector Parity

**33 / 33** vectors derived correctly. Coverage: 6 Class A + 6 Class B + 10 Class C + 10 Class D + 1 cross-class telemetry. The 10 adversarial vectors (canonicalization-scheme-corruption, algorithm-downgrade, replay-drift, evidence-suppression-attempt, quorum-inflation, attestation-replay, protocol-version-mismatch, forged-commit-chain, stage-skip-attempt, action-compelled-without-quorum) all yield the expected `INVALID` / `CONFLICTED` / `CONDUCT_INVALID` verdicts.

## 6. Go Corpus Parity

**10 / 10** canonicalization corpus entries. Strategy: parse with `Decoder.UseNumber()` so number literals survive verbatim, then re-emit with `Encoder.SetEscapeHTML(false)`. Each entry's SHA-256 matches `canonicalization/golden/golden-digests.json` byte-for-byte.

## 7. Go Fingerprint Parity

| Fingerprint | Expected | Observed | Match |
|---|---|---|---|
| `vectors_suite_sha256` | `sha256:6168d2…1bb0f` | `sha256:6168d2…1bb0f` | **YES** |
| `manifests_suite_sha256` | `sha256:74eaaa…ba29` | `sha256:74eaaa…ba29` | **YES** |
| `corpus_sha256` | `sha256:c95685…3b09` | `sha256:c95685…3b09` | **YES** |

`OVERALL: MATCH`. All three v0.1.0 lock anchors reproduced byte-for-byte by the Go verifier.

## 8. `make ci` Result

**PASS** (`rc=0`). 11 stages. Summary message printed by the CI recipe:

> CI: documentation code standard + tooling tests + protocol conformance + interoperability + canonicalization golden + minimal-verifier + replay-diff + binary-fixture + sandbox-escape + rust-verifier + go-verifier (first-party independent tracks; cargo test and go test each cover all 3 frozen fingerprints) all passed.

## 9. `make demo` Result

**PASS** (`rc=0`). 6 steps green. All three frozen fingerprints reproduced byte-for-byte by the Python verifier (the Rust and Go tracks also reproduce them inside `make ci`).

## 10. Files Created / Modified

**Created (this work order):**
- `reports/go_verifier/go_ci_promotion_v0.1.0.md` (this file)
- `reports/go_verifier/go_ci_promotion_v0.1.0.json` (machine-readable)

**Modified:**
- `Makefile` — `ci` target now lists `go-verifier-check` as the 11th stage. Summary message updated to reflect both Rust and Go tracks covering all 3 frozen fingerprints.

**Created in prior commits, included in working-tree for this commit:**
- `go.work`, `go_verifier/` (entire module), `reports/go_verifier/go_verifier_v0.1.0.{md,json}` (from Option C / WO 013 final phase) — these were never committed; this commit picks them up.
- `.gitignore` (added `go.work.sum` exclusion in the same prior phase)

**Not changed (by design):** `SPEC.md`, `SPEC_LOCK_v0.1.md`, `vectors/**`, `schemas/**`, `canonicalization/corpus/**`, `intellagent_runtime/**`, `tools/**` (Python verifier), `rust_verifier/**` (Rust verifier), `go_verifier/**` (Go verifier sources), frozen fingerprint values.

## 11. Frozen Fingerprint Match Status

All three reproduced byte-for-byte by **four** independent code paths now wired into a single CI gate:

| # | Track | Language | In `make ci` |
|---|---|---|---|
| 1 | Python reference | Python 3.14 | YES |
| 2 | Python minimal | Python 3.14 | YES |
| 3 | Rust verifier | Rust 1.94 | YES (since WO 013) |
| 4 | **Go verifier** | **Go 1.26** | **YES (this work order)** |

## 12. Classification

**`FIRST_PARTY_INDEPENDENT_IMPLEMENTATION_TRACK`** — unchanged.

**`third_party_validation_status: false`** — unchanged.

All four verification tracks are owned by Wise.Est Systems. The CI gate is now four-language strong, but ownership is unchanged.

## 13. Remaining External-Validation Gap

> **A verifier authored, owned, and operated by a party other than Wise.Est Systems.**

The cross-language implementability question is now closed across four languages and stdlib-only Go (38 tests) + minimal-third-party Rust (26 tests, only `serde`/`serde_json`/`sha2`). The ownership question requires an external party publishing a reproducible verifier per `docs/release/THIRD_PARTY_VERIFIER_BRIEF_v0.1.md`.

## 14. Exact Next Build Task

> **Prepare and publish the external verifier recruitment packet for a true non-first-party implementer.**

The packet exists and is drafted: `docs/release/EXTERNAL_REVIEW_PACKET_v0.1.md`, `docs/release/REVIEW_QUICKSTART.md`, `docs/release/THIRD_PARTY_VERIFIER_BRIEF_v0.1.md`. The next phase is *publication* to a non-first-party audience and *waiting for a submission* that satisfies all eight requirements in the brief. There is no further first-party code or document required to invite external review — only the act of inviting.
