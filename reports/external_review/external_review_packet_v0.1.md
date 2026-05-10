# External Review Packet — Evidence Report v0.1.0

**Work Order:** 013 — Rust CI Promotion and External Review Packet
**Timestamp (UTC):** 2026-05-10T19:30:00Z
**Overall Result:** **PASS**
**Authority:** This is the evidence record that the Rust verifier has been promoted into `make ci`, that the cold gate passes, and that the minimum external review packet has been published.

---

## 1. Commands Run

| # | Command | Exit code | Result |
|---|---|---|---|
| 1 | `cargo test --manifest-path rust_verifier/Cargo.toml` | 0 | 26 tests passed |
| 2 | `cargo run --manifest-path rust_verifier/Cargo.toml -- verify-vectors` | 0 | 33/33 vectors PASS |
| 3 | `cargo run --manifest-path rust_verifier/Cargo.toml -- verify-corpus` | 0 | 10/10 corpus entries PASS |
| 4 | `cargo run --manifest-path rust_verifier/Cargo.toml -- fingerprints` | 0 | OVERALL: MATCH |
| 5 | `make rust-verifier-check` | 0 | PASS |
| 6 | `make rust-verifier-fingerprints` | 0 | PASS |
| 7 | `make ci` (with `rust-verifier-check` now included) | 0 | 10 stages PASS |
| 8 | `make demo` | 0 | 6 steps PASS, 3 fingerprints MATCH |
| 9 | `git status --short` | 0 | working tree state captured |

## 2. CI Stages After Promotion

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
| 10 | **`rust-verifier-check`** | **PASS — cargo test (26), verify-vectors (33/33), verify-corpus (10/10); first-party independent track** |

## 3. `make ci` Result

**PASS** (exit code 0). The 10th stage `rust-verifier-check` is now part of the CI gate. The summary line printed at the end of `make ci` reads:

> CI: documentation code standard + tooling tests + protocol conformance + interoperability + canonicalization golden + minimal-verifier + replay-diff + binary-fixture + sandbox-escape + rust-verifier (first-party independent track; cargo test covers all 3 frozen fingerprints) all passed.

## 4. `make demo` Result

**PASS** (exit code 0). All three frozen fingerprints MATCH:

| Fingerprint | Match |
|---|---|
| `vectors_suite_sha256` (`sha256:6168d2…1bb0f`) | YES |
| `manifests_suite_sha256` (`sha256:74eaaa…ba29`) | YES |
| `corpus_sha256` (`sha256:c95685…3b09`) | YES |

## 5. Rust Verifier Result

| Field | Value |
|---|---|
| Toolchain | `cargo 1.94.1`, `rustc 1.94.1` |
| Tests | 26 / 26 passing |
| Vectors | 33 / 33 derived correctly |
| Corpus | 10 / 10 canonicalization parity |
| Fingerprints | all three MATCH |
| Imports Python | **NO** (statically enforced by `does_not_import_or_depend_on_python` integration test) |
| Classification | **FIRST_PARTY_INDEPENDENT_IMPLEMENTATION_TRACK** |
| Constitutes third-party validation | **NO** |

## 6. Frozen Fingerprint Result

All three frozen v0.1.0 lock anchors reproduced byte-for-byte by:
- The Python reference verifier (`make conformance`).
- The Python independent re-derivation (`make minimal-verifier-check`).
- The Rust verifier (`make rust-verifier-check`).

`SPEC_LOCK_v0.1.md §2.4` invariant holds across three independent code paths.

## 7. Files Created / Modified

**Created (this work order):**
- `docs/release/EXTERNAL_REVIEW_PACKET_v0.1.md` — reviewer-facing summary, 15 required sections.
- `docs/release/REVIEW_QUICKSTART.md` — commands-only quickstart for cold reviewers.
- `docs/release/THIRD_PARTY_VERIFIER_BRIEF_v0.1.md` — formal requirements + disqualification conditions for third-party verifier submissions.
- `reports/external_review/external_review_packet_v0.1.md` (this file).
- `reports/external_review/external_review_packet_v0.1.json` (machine-readable).

**Modified:**
- `Makefile` — `ci` target now includes `rust-verifier-check`. Summary message updated.
- `README.md` — added pointers to the three new review docs and the external-validation status line.

**Created but not part of this WO (carried from WO 012, included in this commit):**
- `rust_verifier/` (Cargo.toml, src/*.rs, tests/integration.rs)
- `reports/rust_verifier/rust_verifier_v0.1.0.{md,json}`
- `.gitignore` rust target exclusion.

**NOT changed by design:**
- `SPEC.md`, `SPEC_LOCK_v0.1.md`
- `vectors/**`, `schemas/**`, `canonicalization/corpus/**`
- `intellagent_runtime/**`
- The three frozen fingerprint values

## 8. External Validation Status

> **NOT_COMPLETE.**

Components:

| Component | Status |
|---|---|
| First-party independent track exists | YES (Rust, since WO 012) |
| First-party independent track reproduces all 3 fingerprints | YES |
| Non-first-party verifier exists | **NO** |
| External audit performed | **NO** |
| Production deployment exists | **NO** |

## 9. Remaining Gap

A verifier authored, owned, and operated by a party other than Wise.Est Systems that reproduces all three frozen fingerprints from a public repository under that party's control.

This work order has put in place everything required for that party to begin:

- `docs/release/EXTERNAL_REVIEW_PACKET_v0.1.md` (orientation)
- `docs/release/REVIEW_QUICKSTART.md` (commands)
- `docs/release/THIRD_PARTY_VERIFIER_BRIEF_v0.1.md` (rules + disqualifications)
- `docs/release/IMPLEMENTATION_TRACKER.md` (submission flow)
- `docs/audits/AUDIT_SCOPE_v0.1.md` (findings format)

The first-party project's role from here on is: review submissions, register accepted ones, maintain the brief.

## 10. Next Build Task

Seed a real third-party verifier track. Concretely:

- Identify a non-first-party implementer (TypeScript or Go are the next targets per `IMPLEMENTATION_TRACKER.md §2.{2,3}`).
- Hand them `docs/release/REVIEW_QUICKSTART.md` to confirm the repo passes cold on their machine.
- Hand them `docs/release/THIRD_PARTY_VERIFIER_BRIEF_v0.1.md` for the rules.
- Wait for a submission that satisfies all eight numbered requirements in §7 of the brief, with a passing fingerprint reproduction in their build.

There is no further first-party code to write for this gap. The next move is the external party's.
