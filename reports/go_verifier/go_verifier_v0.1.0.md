# Go Verifier Track Report — v0.1.0

**Work Order:** 013 — Option C (Go track as fourth FIRST_PARTY_INDEPENDENT_IMPLEMENTATION_TRACK)
**Timestamp (UTC):** 2026-05-10T20:00:00Z
**Overall Result:** **PASS** (all three frozen fingerprints reproduced byte-for-byte)
**Independence classification:** `FIRST_PARTY_INDEPENDENT_IMPLEMENTATION_TRACK`
**Third-party validation:** **NO** (same repo, same owner)

---

## 1. Go Toolchain

```
go version go1.26.3 darwin/arm64
```

Module: `wiseorder/go_verifier`, Go directive `1.26`.

## 2. Dependencies

**Standard library only.** Used packages:
- `encoding/json` (with `Decoder.UseNumber()` for lossless number pass-through)
- `crypto/sha256`
- `encoding/hex`
- `bytes`, `os`, `path/filepath`, `sort`, `strings`, `fmt`, `flag`, `io/fs`
- `testing` (tests)
- `os/exec` (integration tests only — to drive the binary; never used in production code paths)

**No third-party Go modules. No Python imports. No Rust imports.** Statically enforced by integration test `TestDoesNotImportOrDependOnPythonOrRust`.

## 3. Files Created / Modified

**Created:**

| File | Purpose |
|---|---|
| `go.work` | Workspace at repo root so `go run ./go_verifier ...` resolves from there |
| `go_verifier/go.mod` | Module declaration; stdlib-only |
| `go_verifier/main.go` | CLI dispatch (`verify-vectors`, `verify-corpus`, `fingerprints`, `help`) |
| `go_verifier/internal/jcs/jcs.go` | Canonicalization + SHA-256 helpers |
| `go_verifier/internal/jcs/jcs_test.go` | 11 unit tests |
| `go_verifier/internal/vectors/vectors.go` | Class A/B/C/D verdict logic (re-derived from SPEC.md) |
| `go_verifier/internal/vectors/vectors_test.go` | 14 unit tests |
| `go_verifier/internal/fingerprints/fingerprints.go` | Three fingerprint formulas |
| `go_verifier/internal/fingerprints/fingerprints_test.go` | 4 unit tests |
| `go_verifier/tests/integration_test.go` | 9 integration tests |
| `reports/go_verifier/go_verifier_v0.1.0.md` (this file) | Evidence report |
| `reports/go_verifier/go_verifier_v0.1.0.json` | Machine-readable equivalent |

**Modified:**
- `Makefile` — added `go-verifier-check` and `go-verifier-fingerprints` targets. **NOT added to `make ci`** per WO 013.
- `.gitignore` — added `go.work.sum` exclusion (Go workspace lock file).

**Not changed (by design):** `SPEC.md`, `SPEC_LOCK_v0.1.md`, `vectors/**`, `schemas/**`, `canonicalization/corpus/**`, `intellagent_runtime/**`, `tools/**` (Python verifier), `rust_verifier/**` (Rust verifier), frozen fingerprint values.

## 4. Vectors

| Field | Value |
|---|---|
| Discovered | 33 |
| Passed | 33 |
| Failed | 0 |

All 33 vectors (23 baseline + 10 adversarial) had their `expected_status` re-derived correctly by the Go verifier from Class A/B/C/D rules in `SPEC.md` §3.

## 5. Canonicalization Corpus

| Field | Value |
|---|---|
| Discovered | 10 |
| Passed | 10 |
| Failed | 0 |

For each corpus entry under `canonicalization/corpus/*.json`, the Go verifier:
1. Parses the JSON via `encoding/json` with `Decoder.UseNumber()`.
2. Re-emits canonical UTF-8 bytes via `encoding/json` with `Encoder.SetEscapeHTML(false)`. Go's default JSON encoder sorts `map[string]interface{}` keys, uses compact separators, and emits raw UTF-8 strings — matching the tooling-internal scheme.
3. Computes SHA-256 over those bytes.
4. Compares against `canonicalization/golden/golden-digests.json`.

All 10 entries match byte-for-byte. The `Decoder.UseNumber()` approach makes number formatting strictly correct: number literals survive as `json.Number` (a string type) and round-trip verbatim, sidestepping any divergence between Python's `repr(float)` and Go's `strconv.FormatFloat`.

## 6. Frozen Fingerprint Match

| Fingerprint | Expected | Observed | Match |
|---|---|---|---|
| `vectors_suite_sha256` | `sha256:6168d2…1bb0f` | `sha256:6168d2…1bb0f` | **YES** |
| `manifests_suite_sha256` | `sha256:74eaaa…ba29` | `sha256:74eaaa…ba29` | **YES** |
| `corpus_sha256` | `sha256:c95685…3b09` | `sha256:c95685…3b09` | **YES** |

**OVERALL: MATCH** on first cold run. All three v0.1.0 lock anchors reproduced byte-for-byte by an independent Go implementation.

### Computation notes (re-derived from spec, not ported)

- **`vectors_suite_sha256`** — per-file SHA-256 of raw vector bytes (bare lowercase hex, no `sha256:` prefix), sorted by `vector_id`, joined with `\n` (no trailing newline), then SHA-256 of that UTF-8 string.
- **`manifests_suite_sha256`** — per-file SHA-256 of raw manifest bytes (in `sha256:<hex>` prefixed form — this is the one place where the suite-aggregation input uses the prefixed form, distinct from `vectors_suite_sha256`), sorted by `fixture_id`, joined with `\n`, then SHA-256.
- **`corpus_sha256`** — single running SHA-256 fed with `file_id_utf8 || 0x00 || canonical_bytes || 0x00` for each corpus entry in lexicographic filename order.

## 7. Tests

| Suite | Count | Passing |
|---|---|---|
| Unit tests (`internal/jcs`) | 11 | 11 |
| Unit tests (`internal/vectors`) | 14 | 14 |
| Unit tests (`internal/fingerprints`) | 4 | 4 |
| Integration tests (`go_verifier/tests`) | 9 | 9 |
| **Total** | **38** | **38** |

All required behaviors covered:

1. reads all vectors → `TestReadsAllVectors`
2. rejects malformed vector structure → `TestRejectsMalformedVectorStructure`
3. rejects unsupported protocol version → `TestRejectsUnsupportedProtocolVersion`
4. reproduces all vector verdicts → `TestReproducesAllVectorVerdicts`
5. reads all canonicalization corpus entries → `TestReadsAllCanonicalizationCorpusEntries`
6. reproduces corpus hashes → `TestReproducesCorpusHashes`
7. reproduces all three frozen fingerprints → `TestReproducesAllThreeFingerprints`
8. deterministic across two runs → `TestDeterministicOutputAcrossTwoRuns`
9. no Python or Rust import → `TestDoesNotImportOrDependOnPythonOrRust`

## 8. Determinism

The integration test `TestDeterministicOutputAcrossTwoRuns` runs each of the three subcommands twice and asserts the stdout is byte-identical. All three pass.

## 9. Commands Run

```
go test ./go_verifier/...                          rc=0   38 tests
go run  ./go_verifier verify-vectors               rc=0   33/33 PASS
go run  ./go_verifier verify-corpus                rc=0   10/10 PASS
go run  ./go_verifier fingerprints                 rc=0   OVERALL: MATCH
make go-verifier-check                             rc=0
make go-verifier-fingerprints                      rc=0
make ci                                            rc=0   (10 stages, Go not in ci yet)
make demo                                          rc=0   (3 fingerprints MATCH)
git status --short                                 rc=0
```

`make ci` and `make demo` were re-run after all Go additions to confirm no regression in the Python or Rust verifier tracks.

## 10. Independence Statement

- This module **does not import** the Python `intellagent_runtime` package or any Python-backed tool.
- This module **does not depend on the Rust verifier track** (`rust_verifier/`). It is built from the standard library only.
- This module **does not shell out to** Python or to Rust in any production code path. The integration tests use `os/exec` to drive the Go binary itself; this is allowed only in `_test.go` files and is statically enforced.
- This module **does not translate Python or Rust files line-by-line**. The verdict logic and the fingerprint formulas were derived from reading the specification (`SPEC.md`, `SPEC_LOCK_v0.1.md`) and the contract of the relevant entrypoints (not their implementations), then re-implemented using Go idioms.

**Classification: `FIRST_PARTY_INDEPENDENT_IMPLEMENTATION_TRACK`.**

This is **NOT** third-party validation. The Go module ships in the same repository under the same first-party owner. Per `docs/release/IMPLEMENTATION_TRACKER.md §1` and `docs/release/THIRD_PARTY_VERIFIER_BRIEF_v0.1.md §8`, true third-party validation requires a verifier authored, owned, and operated by a party other than Wise.Est Systems.

## 11. Known Limitations

1. **Independence is logical, not organizational.** Same repo, same owner.
2. **Number canonicalization is pass-through.** Using `Decoder.UseNumber()` means number literals survive as `json.Number` strings; the Go float-formatting code path is not exercised by the corpus. This is strictly correct for v0.1.0, but a future corpus entry that requires emitting numbers in a normalized form would need separate work.
3. **HTML escaping disabled.** `json.Encoder.SetEscapeHTML(false)` matters for `<`, `>`, `&` in strings — but no current corpus entry contains these inside a string value. The behavior is correct; the corpus does not test it.
4. **CLI does not yet accept `--repo-root`.** It walks upward from cwd looking for `vectors/` and `canonicalization/` siblings.
5. **Go verifier is intentionally NOT in `make ci`** per WO 013. Promotion is a separate work order.

## 12. Largest Remaining External-Validation Gap

> **A verifier authored, owned, and operated by a party other than Wise.Est Systems.**

The Go track establishes a **fourth** independent code path that reproduces the three frozen fingerprints. The cross-language implementability question is now closed very strongly:

| Track | Language | Module | Status |
|---|---|---|---|
| 1 | Python | `intellagent_runtime/`, `tools/run_conformance.py` | reference; in `make ci` |
| 2 | Python | `tools/minimal_verifier.py` | independent re-derivation; in `make ci` |
| 3 | Rust 1.94 | `rust_verifier/` | first-party independent; in `make ci` |
| 4 | Go 1.26 | `go_verifier/` | first-party independent; NOT in `make ci` yet |

All four tracks own the same fingerprint values byte-for-byte. The ownership / accountability question that defines third-party validation is unchanged.

## 13. Failure-Mode Classification

No fingerprint divergence observed. If a future run produces divergence, classification rule:

| Divergence symptom | Classification |
|---|---|
| `vectors_suite_sha256` differs by exactly one digest | Vector file modified or sort-order divergent — investigate the offending `vector_id`. |
| `manifests_suite_sha256` differs | Manifest disk bytes diverge between Python regeneration and what's committed — check `interop/fixtures/<impl>/*.manifest.json`. |
| `corpus_sha256` differs while every per-entry digest still matches | Go corpus loop ordering or framing-byte mistake — check the `\0` separators. |
| `corpus_sha256` differs AND one or more per-entry digests differ | **canonicalization mismatch** between Go and Python on the offending entry. Most likely culprit: `encoding/json` HTML escaping re-enabled, or `Decoder.UseNumber()` not applied, or sort order not lexicographic. |
| All three fingerprints differ | Path assumption (wrong `repoRoot`) or wrong sort key. |
| One fingerprint differs only when re-run | Non-determinism — file as **UNKNOWN** and investigate. |

## 14. Next Build Task

Either:

- **(a)** Promote `go-verifier-check` into `make ci` after one more cold confirmation run.
- **(b)** Post the recruitment pitch (already drafted in `docs/release/THIRD_PARTY_VERIFIER_BRIEF_v0.1.md` and `docs/release/EXTERNAL_REVIEW_PACKET_v0.1.md`) to a non-first-party audience and wait for an external submission.

(a) tightens the in-repo gate; (b) is the only path that closes the external-validation gap.
