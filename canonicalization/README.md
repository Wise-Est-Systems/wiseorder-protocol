# Canonicalization Corpus

> Pressure surface for cross-language canonical-byte agreement.
> Companion to [`../CROSS-LANGUAGE-CANONICALIZATION-v0.1.md`](../CROSS-LANGUAGE-CANONICALIZATION-v0.1.md).

---

## Purpose

This directory pins the byte output of the v0.1 Python canonicalizer for a frozen 10-entry corpus, so that:

- determinism of the Python canonicalizer is mechanically enforced on every push;
- any future port (Rust, TypeScript, Go, …) can self-test against the v0.1 baseline;
- canonicalization drift is detectable in a single `make canonicalization-check` invocation.

The canonicalizer in question is `intellagent_runtime.canonical.canonical_json_bytes`. Per its own docstring, it is *not* a strict RFC 8785 JCS implementation. Strict-JCS adoption is v0.2 work; the corpus committed here is the v0.1 baseline against which that migration will be recorded as a controlled drift event.

---

## Layout

```
canonicalization/
├── README.md
├── corpus/
│   ├── 001-simple-object.json
│   ├── 002-nested-object.json
│   ├── 003-array-order.json
│   ├── 004-unicode.json
│   ├── 005-number-integer.json
│   ├── 006-number-float.json
│   ├── 007-bool-null.json
│   ├── 008-key-order.json
│   ├── 009-whitespace.json
│   └── 010-wiseorder-class-a.json
├── golden/
│   ├── golden-canonical.json
│   └── golden-digests.json
└── tools/
    ├── generate_golden.py
    └── verify_golden.py
```

---

## Workflow

```bash
# regenerate golden files from current corpus + canonicalizer
make canonicalization-golden

# verify committed golden files against current canonicalizer
make canonicalization-check
```

`canonicalization-check` is part of `make ci`. CI fails on any byte-level divergence between the committed golden files and re-derived canonical output.

---

## Corpus contract

Each `corpus/*.json` file is hand-authored, valid JSON. Filenames are zero-padded to keep iteration order stable. Files are intentionally small (target: under 1 KB each).

Each entry exercises one or more drift modes:

| Drift mode | Description |
| --- | --- |
| M1 | Key-order drift |
| M2 | Numeric-format drift |
| M3 | String-escape drift |
| M4 | Whitespace and separator drift |
| M5 | Encoding drift |

See `CROSS-LANGUAGE-CANONICALIZATION-v0.1.md` §5 for definitions and §6 for the per-entry mapping.

---

## Modifying the corpus

The corpus is frozen at v0.1. Changes are SPEC-level events, not casual edits.

If a corpus file is added, removed, renamed, or modified:

1. Re-run `make canonicalization-golden` to regenerate `golden-canonical.json` and `golden-digests.json`.
2. Commit the corpus change and the regenerated golden files in the same commit.
3. Note the new `corpus_sha256` in `RELEASE-STATUS-v0.1.md` (or its successor) as a recorded drift event.

`make ci` enforces consistency: the regenerated golden files MUST equal the committed golden files. Drift fails CI.
