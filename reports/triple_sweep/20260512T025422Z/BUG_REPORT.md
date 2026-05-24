# Triple-implementation canonicalization disagreement report

**Run:** `reports/triple_sweep/20260512T025422Z/`
**Inputs swept:** 5000
**Implementations:** `intellagent_runtime.canonical` (Python) + `go_verifier/internal/jcs` (Go) + `rust_verifier/src/jcs.rs` (Rust)
**Elapsed:** 37.5 s on M4 (16 GB, 10 cores, 6 workers, safe-max envelope, no thermal warnings)
**Throughput:** 133 inputs/sec

## Headline

3 477 of 5 000 inputs (69.5 %) produced byte-identical canonical output across all three implementations. **1 523 of 5 000 (30.5 %) disagreed.** Disagreements cluster into two clearly-localized implementation bugs, listed below.

`whitespace_key` and `duplicate_like_keys` generators (canned inputs) showed 0 disagreement, confirming the bug surface is on the value side, not on identity-key handling.

## Bug A — Go canonicalizer escapes U+2028 / U+2029 / control characters; Python and Rust emit raw UTF-8

**Disagreements attributed:** 1 390 of 1 523 (91 %)
**Partition:** `agree:python+rust | outlier:go`
**Outlier always writes longer canonical bytes** (escapes expand 3-byte UTF-8 sequences to 6 ASCII bytes).

### Evidence

- Generator breakdown:
  - `object_unicode_keys`: 447
  - `nested`: 418
  - `array_order`: 243
  - `unicode_string`: 193
  - `mixed_object`: 89

- All 1 390 records include at least one of:
  `contains-U+2028`, `contains-U+2029`, `contains-C0-control`, `contains-C1-control`, `contains-DEL`, `contains-BOM`.

### Minimal reproducer

Input:
```json
" "
```

- Python canonical bytes (3): ` ` (raw 3-byte UTF-8 `E2 80 A8`)
- Rust canonical bytes (3): same as Python
- Go canonical bytes (8): `" "` — escaped as ASCII

### Root cause

`go_verifier/internal/jcs/jcs.go` header comment claims:

> Strings emitted as raw UTF-8 bytes (no `\uXXXX` escaping for non-ASCII; the JSON minimum escapes for `"` and `\` and the C0 control range are still applied).

But the implementation uses `json.Encoder` from Go's `encoding/json`, which **always** escapes U+2028 and U+2029 regardless of `SetEscapeHTML(false)` because of legacy JavaScript-compatibility behavior in the stdlib (`json/encode.go`). The header comment does not match the implementation behavior.

### Impact

- v0.1.0 corpus avoids this only because none of the 10 committed corpus entries contain U+2028, U+2029, or stray C0/C1 controls in string values.
- Any future vector containing a non-ASCII separator or control character would produce different fingerprints across the three implementations, breaking the cross-implementation conformance claim.

### Fix shape (NOT IMPLEMENTED in this work order)

Replace `json.Encoder.Encode(v)` in `go_verifier/internal/jcs/jcs.go` with a custom JSON serializer that emits raw UTF-8 bytes for all non-ASCII code points (including U+2028 / U+2029) and applies only the JSON-minimum escape set documented in the header comment. Alternative: update the header comment + spec to declare that U+2028 / U+2029 must be `\u`-escaped in the canonical form, then change Python and Rust to match Go — but Go is the outlier per the **two** other implementations, so updating Go to match the documented behavior is the lower-risk path.

## Bug B — Rust canonicalizer silently downgrades integers > u64 to float64

**Disagreements attributed:** 80 of 1 523 (5.3 %)
**Partition:** `agree:go+python | outlier:rust`
**Outlier always writes longer canonical bytes** (float repr is longer than the integer literal).

### Evidence

- Generator breakdown:
  - `mixed_object`: 30
  - `number_edge`: 19
  - `array_order`: 17
  - `nested`: 14

- All 80 records include at least one of:
  `contains-bigint>=2^64`, `contains-bigint>i64`, `contains-bigint>2^53`.

### Minimal reproducer

Input:
```json
18446744073709551616
```
(this is exactly 2^64)

- Python canonical bytes (20): `18446744073709551616` (preserves exact integer)
- Go canonical bytes (20): `18446744073709551616` (preserves via `json.Number`)
- Rust canonical bytes (22): `1.8446744073709552e+19` (lossy IEEE-754 round-trip)

### Root cause

`rust_verifier/src/jcs.rs` uses `serde_json::from_slice` to parse and `serde_json::to_string` to serialize. `serde_json`'s default JSON parser converts any integer that exceeds `u64::MAX` to `serde_json::Number::from_f64`, which is a lossy conversion to IEEE-754 binary64. The original digit string is discarded.

### Impact

- v0.1.0 corpus avoids this only because none of the 10 committed corpus entries contain integers larger than 2^53.
- A reviewer who pastes any large integer into a vector would observe Rust silently disagreeing with Python+Go and may judge the cross-implementation conformance claim as overstated.
- This is a **correctness** issue in the Rust verifier track, not a cosmetic one — `1.8446744073709552e+19` is **not equal** to `2^64` as an integer.

### Fix shape (NOT IMPLEMENTED in this work order)

Enable the `arbitrary_precision` feature on `serde_json` in `rust_verifier/Cargo.toml` (preserves the original digit string for any JSON number, regardless of magnitude), and ensure the canonicalizer emits the preserved digits verbatim. Alternative: reject inputs containing integers > 2^63 - 1 in the Rust track and document the limitation; this is weaker because it changes the supported input domain.

## Bug C — Combination cases (all three implementations differ)

**Disagreements attributed:** 53 of 1 523 (3.5 %)
**Partition:** `all-three-different`

These are inputs whose value contains BOTH a Bug-A-triggering character (U+2028/U+2029/control) AND a Bug-B-triggering integer (> u64). Each implementation diverges from each of the other two for distinct reasons. There is no separate Bug C; it is `A ∧ B`. Fixing A and B independently is expected to eliminate this bucket.

## Safety envelope (M4)

- 6 concurrent workers; 4 cores reserved for system + interactive use
- `pmset -g therm` polled every 60 s; **no warnings raised at any point during the sweep**
- All output artifacts are under `reports/triple_sweep/<ts>/`; SPEC.md, vectors/, schemas/, and canonicalization/corpus/ were NOT touched
- New CLI surface added: `tools/canonicalize_cli.py`, plus `canonicalize` subcommand on both `go_verifier` and `rust_verifier` (both subcommands documented in `--help`)

## What is now real

- Reproducible 5 000-input cross-implementation sweep tool: `tools/triple_sweep.py`
- Per-signature classifier: `tools/classify_disagreements.py`
- Locked evidence directory: `reports/triple_sweep/20260512T025422Z/` (inputs + jsonl + per-signature .md + this report)
- Two distinct, well-localized bugs in v0.1.0 verifier tracks (above)

## What remains unproven

- Fix shapes proposed for Bug A and Bug B are NOT IMPLEMENTED. No code in `go_verifier/` or `rust_verifier/` was changed for the fix; only the `canonicalize` subcommand was added.
- `make ci` was not re-run after this sweep. Last green run: timestamp `(make ci, 9.93 s)` earlier in this session.
- These findings have not been incorporated into SPEC.md, conformance vectors, or the canonicalization corpus. That is intentional per the do-not-touch-without-permission policy.

## Risks introduced

- None to repo state: all new code is under `tools/` and the two verifier `canonicalize` subcommands. Existing `make ci` targets unchanged.
- New `base64` crate dependency added to `rust_verifier/Cargo.toml`. The Rust verifier independence claim is unchanged (no Python or first-party Rust runtime imports).
- New Go `encoding/base64` import (stdlib) in `go_verifier/main.go`. Independence claim unchanged.

## Exact next build task

Decision point for Henry Wayne Wise III:

  (1) Implement Bug A fix in Go (custom JSON encoder that does not escape U+2028/U+2029/non-ASCII).
  (2) Implement Bug B fix in Rust (`arbitrary_precision` feature + emit preserved digits).
  (3) Re-run 5 000-input sweep against fixed verifiers; expect ≥ 99 % agreement.
  (4) Iterate at 50 000 inputs; lock newly-agreed inputs as candidate vector additions only after Henry approves.

If approved, do (1) and (2) atomically before re-running.
