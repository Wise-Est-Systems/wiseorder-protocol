# Known cross-implementation canonicalization gaps (as of v0.2.0 seal)

**Recorded:** 2026-05-23
**Status:** Known limitation. Scope: v0.3.0 follow-up. NOT a v0.1.0 or v0.2.0 conformance failure.

## What triple_sweep is

`tools/triple_sweep.py` generates a large stream of fuzz inputs (random / unicode-edge / number-edge / nested / whitespace-key / duplicate-like-key JSON), canonicalizes each input through all three independent verifier tracks (Python `tools/canonicalize_cli.py`, Rust `rust_verifier`, Go `go_verifier`), and records every disagreement byte-for-byte.

## Why this exists

The 33-vector v0.1.0 conformance suite covers a curated set of inputs. The three verifiers all agree on every vector — `make ci` is green. But the *spec text* ("RFC 8785 JCS, SHA-256, UTF-8") does not pin down every edge case in the JCS standard the way a single-implementation reference would. Two conformant implementations can disagree on inputs that the corpus doesn't cover. triple_sweep measures the gap.

## Latest run: 2026-05-23

| Metric | Value |
|---|---|
| Inputs generated | 500 |
| Agreed (Python = Rust = Go) | 353 (70.6%) |
| Disagreed | 147 (29.4%) |
| Errors | 0 |
| Distinct disagreement signatures | 100 |
| Elapsed | 4.823 s |
| Run dir | `reports/triple_sweep/20260523T071041Z/` |
| Seed | `20260523` |

## Disagreement classes

### Class 1 — Go outputs longer canonical bytes on Unicode edge cases

`agree: python+rust | outlier: go | longest: go, shortest: python`

Triggered by inputs containing any of:
- BOM (U+FEFF)
- C0 controls (U+0000–U+001F)
- C1 controls (U+0080–U+009F)
- DEL (U+007F)
- Line separator (U+2028)
- Paragraph separator (U+2029)
- Supplementary Multilingual Plane (SMP) codepoints
- Emoji (SMP-range)

**Root cause (hypothesis):** Go's `json.Encoder` with `SetEscapeHTML(false)` still escapes some control characters and supplementary plane codepoints to `\uXXXX` form where Python/Rust pass them through as raw UTF-8 bytes. The result is the same logical JSON but different byte sequences — and JCS is byte-defined, not value-defined.

### Class 2 — Rust outputs different canonical bytes on big integers

`agree: go+python | outlier: rust | longest: rust, shortest: python`

Triggered by inputs containing integers in any of:
- `> 2^53` (beyond IEEE-754 safe-integer range)
- `>= 2^64` (beyond u64)
- `> i64::MAX`

**Root cause (hypothesis):** Rust's `serde_json` may serialize big integers via different number formatting (decimal vs scientific) or with different precision than Python's `json.dumps` (which preserves Python int width) and Go's `json.Marshal`.

## Why this is NOT a v0.1.0 / v0.2.0 conformance failure

1. The 33-vector conformance suite passes on all three verifiers under `make ci`. None of the corpus inputs trigger these classes.
2. The canonicalization golden corpus (10 entries) passes on all three verifiers byte-for-byte.
3. The disagreements are on FUZZ inputs outside the published corpus. The spec's conformance claim is for the corpus and the vectors, not for arbitrary unicode-edge inputs.

The reviewer's "Logic Gap" critique correctly predicted this surface exists. triple_sweep is the tool that measures it, recorded in canon.

## Scope for v0.3.0 follow-up

Two paths, decided in a separate work order:

**Path A — tighten the canonicalizers to byte-parity.**
- Go: hand-write a JCS encoder that matches Python's `json.dumps` behavior on the marker classes above.
- Rust: pin big-integer serialization to Python-equivalent decimal format.
- Re-run triple_sweep; target zero disagreements on the same generators.

**Path B — narrow the canonicalization scope in spec.**
- Declare regions where canonicalization is NOT guaranteed (e.g., "implementations MAY differ on raw bytes for codepoints in supplementary planes when not Unicode-normalized to NFC first").
- Require pre-normalization (NFC) and integer bounds (max ±2^53) as preconditions for the canonical-byte guarantee.

Path B is faster and arguably the *correct* move: JCS itself is silent on some of these surfaces, and narrowing scope is honest rather than implementation-binding.

This decision is queued as Task #8.

## Reproducing

```bash
# From repo root with .venv active:
.venv/bin/python tools/triple_sweep.py --count 500 --workers 4 --seed 20260523
.venv/bin/python tools/classify_disagreements.py --run reports/triple_sweep/<timestamp>
```

Per-signature bug bundles land in `reports/triple_sweep/<timestamp>/bugs/`.
