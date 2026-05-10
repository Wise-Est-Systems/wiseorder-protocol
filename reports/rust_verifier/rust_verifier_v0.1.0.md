# Rust Verifier Track Report — v0.1.0

**Work Order:** 012 — Rust Independent Verifier Track
**Timestamp (UTC):** 2026-05-10T19:00:00Z
**Overall Result:** **PASS** (all three frozen fingerprints reproduced byte-for-byte)
**Independence classification:** `FIRST_PARTY_INDEPENDENT_IMPLEMENTATION_TRACK`
**Third-party validation:** **NO** (this track is in-repo; ownership is unchanged)

---

## 1. Rust Toolchain

```
cargo 1.94.1 (29ea6fb6a 2026-03-24)
rustc 1.94.1 (e408947bf 2026-03-25)
```

Edition: 2021.

## 2. Dependencies

| Crate | Version | Features | Notes |
|---|---|---|---|
| `serde` | 1 | `derive` | Used for deserializing vector files into a typed `RawVector` shape. |
| `serde_json` | 1 | `std` only (default features disabled) | `preserve_order` is **intentionally not enabled**. The canonicalization scheme requires sorted-key `Map<String, Value>` iteration, which serde_json's default `BTreeMap`-backed `Map` provides. |
| `sha2` | 0.10 | (default features off) | SHA-256 for fingerprints and corpus digests. |

**No Python dependency. No `pyo3` / `cpython` / `rustpython`. No reference to `intellagent_runtime`.** Static guarantee verified by integration test `does_not_import_or_depend_on_python`.

## 3. Files Created / Modified

**Created:**
- `rust_verifier/Cargo.toml`
- `rust_verifier/src/main.rs` (CLI dispatch, 3 subcommands)
- `rust_verifier/src/jcs.rs` (tooling-internal canonicalization)
- `rust_verifier/src/vectors.rs` (Class A/B/C/D verdict logic, re-derived from spec)
- `rust_verifier/src/fingerprints.rs` (3 fingerprint formulas)
- `rust_verifier/tests/integration.rs` (13 integration tests)
- `reports/rust_verifier/rust_verifier_v0.1.0.md` (this report)
- `reports/rust_verifier/rust_verifier_v0.1.0.json` (machine-readable equivalent)

**Modified:**
- `Makefile` — added `rust-verifier-check` and `rust-verifier-fingerprints`; NOT added to `make ci` per WO 012.

**NOT changed (by design):** `SPEC.md`, `SPEC_LOCK_v0.1.md`, `vectors/**`, `schemas/**`, `canonicalization/corpus/**`, `intellagent_runtime/**`, `tools/**`.

## 4. Vectors

| Field | Value |
|---|---|
| Discovered | 33 |
| Passed | 33 |
| Failed | 0 |

All 33 vectors (23 baseline + 10 adversarial) had their `expected_status` re-derived correctly by the Rust verifier from Class A/B/C/D rules in `SPEC.md` §3.

## 5. Canonicalization Corpus

| Field | Value |
|---|---|
| Discovered | 10 |
| Passed | 10 |
| Failed | 0 |

For each corpus entry under `canonicalization/corpus/*.json`, the Rust verifier:
1. Parses the JSON via `serde_json::from_slice`.
2. Re-emits canonical UTF-8 bytes via `serde_json::to_string` on the parsed `Value` (yielding sorted keys + compact separators + UTF-8 directly).
3. Computes SHA-256 over those bytes.
4. Compares against `canonicalization/golden/golden-digests.json`.

All 10 entries match byte-for-byte.

## 6. Frozen Fingerprint Match

| Fingerprint | Expected | Observed | Match |
|---|---|---|---|
| `vectors_suite_sha256` | `sha256:6168d2…1bb0f` | `sha256:6168d2…1bb0f` | **YES** |
| `manifests_suite_sha256` | `sha256:74eaaa…ba29` | `sha256:74eaaa…ba29` | **YES** |
| `corpus_sha256` | `sha256:c95685…3b09` | `sha256:c95685…3b09` | **YES** |

**OVERALL: MATCH.** All three v0.1.0 lock anchors reproduced byte-for-byte by an independent Rust implementation.

### Computation notes (re-derived from spec, not ported)

- **`vectors_suite_sha256`** — per-file SHA-256 of raw vector bytes (bare lowercase hex, no `sha256:` prefix), sorted by `vector_id`, joined with `\n` (no trailing newline), then SHA-256 of that UTF-8 string.
- **`manifests_suite_sha256`** — per-file SHA-256 of raw manifest bytes (with `sha256:` prefix — this is the one place where the suite-aggregation input uses the prefixed form, distinct from `vectors_suite_sha256`), sorted by `fixture_id`, joined with `\n`, then SHA-256 of the result.
- **`corpus_sha256`** — single running SHA-256 fed with `file_id_utf8 || 0x00 || canonical_bytes || 0x00` for each corpus entry in lexicographic filename order.

These formulas were derived by reading the relevant Python entrypoints (`tools/run_conformance.py`, `interop/scripts/run_interop_checks.py`, `canonicalization/tools/generate_golden.py`) for their *contract*, not their implementation, and then re-implemented from scratch in Rust.

## 7. Tests

| Suite | Count | Passing |
|---|---|---|
| Unit tests (`src/jcs.rs`) | 6 | 6 |
| Unit tests (`src/vectors.rs`) | 4 | 4 |
| Unit tests (`src/fingerprints.rs`) | 3 | 3 |
| Integration tests (`tests/integration.rs`) | 13 | 13 |
| **Total** | **26** | **26** |

The 11 required behaviors are all covered:

1. reads all vectors → `reads_all_vectors`
2. rejects malformed vector structure → `rejects_malformed_vector_structure`
3. rejects unsupported protocol version → `rejects_unsupported_protocol_version`
4. reproduces all vector verdicts → `reproduces_all_vector_verdicts`
5. reads all canonicalization corpus entries → `reads_all_canonicalization_corpus_entries`
6. reproduces corpus hashes → `reproduces_corpus_hashes`
7. reproduces vectors suite fingerprint → `reproduces_vectors_suite_fingerprint`
8. reproduces manifests suite fingerprint → `reproduces_manifests_suite_fingerprint`
9. reproduces corpus fingerprint → `reproduces_corpus_fingerprint`
10. produces deterministic output across two runs → `produces_deterministic_output_across_two_runs`
11. does not import / shell out to / depend on Python → `does_not_import_or_depend_on_python` (scans Cargo.toml dependency keys and Rust source `use`/`extern crate` lines)

## 8. Determinism

The integration test `produces_deterministic_output_across_two_runs` runs each of the three subcommands twice and asserts the stdout is byte-identical. All three pass.

## 9. Commands Run

```
cargo test --manifest-path rust_verifier/Cargo.toml                          rc=0
cargo run  --manifest-path rust_verifier/Cargo.toml -- verify-vectors        rc=0
cargo run  --manifest-path rust_verifier/Cargo.toml -- verify-corpus         rc=0
cargo run  --manifest-path rust_verifier/Cargo.toml -- fingerprints          rc=0
make rust-verifier-check                                                     rc=0
make rust-verifier-fingerprints                                              rc=0
make ci                                                                      rc=0
make demo                                                                    rc=0
```

`make ci` and `make demo` were re-run after all Rust additions to confirm no regression in the Python verifier track.

## 10. Independence Statement

- This crate **does not import** the Python `intellagent_runtime` package.
- This crate **does not shell out to** Python or any Python-backed tool.
- This crate **does not translate Python files line-by-line**. The verdict logic and the fingerprint formulas were derived from reading the specification and the relevant entrypoints' contracts, then re-implemented using Rust idioms (typed `enum LoadError`, `Result<_, FpError>`, `BTreeMap`-backed `serde_json::Map`).
- This crate's only third-party dependencies are `serde`, `serde_json`, and `sha2` from the Rust ecosystem.

**Classification: `FIRST_PARTY_INDEPENDENT_IMPLEMENTATION_TRACK`.**

This is **NOT** third-party validation. The Rust crate ships in the same repository under the same first-party owner. Per `IMPLEMENTATION_TRACKER.md §1`, true third-party validation requires a verifier authored, owned, and operated by a party other than Wise.Est Systems.

## 11. Known Limitations

1. **Independence is logical, not organizational.** Same repo, same owner.
2. **Canonicalization parity is exercised against the 10 committed corpus entries** — not every JCS edge case. Out-of-corpus inputs MAY diverge between the Rust and Python canonicalizers; that would be a Rust gap, not a v0.1.0 protocol gap.
3. The CLI **does not yet accept a `--repo-root` flag**; it locates the repo root by walking up from `CARGO_MANIFEST_DIR`.
4. **Number serialization relies on serde_json's default Display** for `serde_json::Number`, which uses Ryu / shortest-roundtrip. For every float in the current corpus this matches Python's `repr`, but the equivalence is not exhaustively proven across all f64 values.
5. **The Rust verifier is intentionally not yet wired into `make ci`** per WO 012 prohibition. Promotion is a separate work order.

## 12. Largest Remaining External-Validation Gap

> **True third-party validation:** a verifier authored, owned, and operated by a party other than the first-party project.

This track demonstrates that v0.1.0 is implementable in a second language from a different module surface, which closes the "is it actually re-implementable?" question for Rust specifically. It does not close the ownership / accountability gap that defines third-party validation in `IMPLEMENTATION_TRACKER.md §1`.

## 13. Failure-Mode Classification

No fingerprint divergence observed. If a future run produces divergence, classification rule:

| Divergence symptom | Classification |
|---|---|
| `vectors_suite_sha256` differs by exactly one digest | Vector file modified or sort-order divergent — investigate the offending `vector_id`. |
| `manifests_suite_sha256` differs | Manifest disk bytes diverge between Python regeneration and what's committed — check `interop/fixtures/<impl>/*.manifest.json`. |
| `corpus_sha256` differs while every per-entry digest in §5 still matches | Rust corpus loop ordering or framing-byte mistake — check the `\0` separators. |
| `corpus_sha256` differs AND one or more per-entry digests differ | **canonicalization mismatch** between Rust and Python on the offending entry. The committed `golden-canonical.json` shows the expected canonical UTF-8 string; compare byte-by-byte to identify the rule the Rust canonicalizer is missing. |
| All three fingerprints differ | Path assumption (wrong `repo_root`) or wrong sort key. |
| One fingerprint differs only when re-run | Non-determinism in the Rust canonicalizer (very unlikely given serde_json's deterministic BTreeMap iteration) — file as **UNKNOWN** and investigate. |

## 14. Next Build Task

Either (a) promote the Rust verifier into `make ci` after one more cold confirmation run, or (b) seed an actual third-party implementation track in TypeScript or Go under an independent repository owned by a non-first-party party (`IMPLEMENTATION_TRACKER.md §2.{2,3}`).
