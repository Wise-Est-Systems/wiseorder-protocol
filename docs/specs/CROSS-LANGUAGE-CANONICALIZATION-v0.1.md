# CROSS-LANGUAGE CANONICALIZATION v0.1

**Pressure surface for canonical-byte agreement across implementations.**

---

**Status:** Draft Canon
**Owner:** Wise.Est Systems
**Adopted:** 2026-05-06
**Scope:** WiseOrder Protocol v0.1.0 + Intellagent Runtime v0.1
**Companion:** [`ARCHITECTURE-PRESSURE-TESTS-v0.1.md`](./ARCHITECTURE-PRESSURE-TESTS-v0.1.md) §15 (Canonicalization Drift), §17 (Interoperability Drift), §27.5 (Cross-language canonicalization gap)

---

## 1. Purpose

This document defines the cross-language canonicalization pressure surface for WiseOrder Protocol v0.1.0 and Intellagent Runtime v0.1.

It does not redesign the architecture, modify WiseOrder semantics, add cognition classes, or weaken the RFC 8785 JCS requirement defined in `SPEC.md` §4.

It defines:

- the canonicalization function the v0.1 Python runtime actually uses;
- the SPEC-required canonicalization for Class A (RFC 8785 JCS);
- the gap between those two facts;
- a frozen golden corpus of inputs, canonical bytes, and SHA-256 digests against which every future implementation in any language MUST match byte-for-byte before being declared interoperable;
- the v0.2 resolution path that closes the gap.

The corpus and tooling that land alongside this document make canonicalization drift mechanically detectable, not merely narratively warned against.

---

## 2. Why Cross-Language Drift Is Critical

WiseOrder is an interoperability protocol. Its conformance corpus is JSON. Its audit chains are JSON. Its proofs reference canonical bytes by SHA-256 digest. If two conformant implementations canonicalize the same conceptual artifact to two different byte sequences, every downstream property of the protocol breaks at once:

- **Digests diverge.** Two implementations cannot agree on whether a given Class A artifact is `VERIFIED` because they hash different bytes.
- **Vectors stop pinning meaning.** A vector is a frozen JSON document with an expected status. If two canonicalizers produce different bytes from that document, the vector is implementation-scoped, not protocol-scoped.
- **Audit chains stop replaying across implementations.** Replay is a byte-level claim. Different bytes, different chain.
- **Refusal artifacts diverge.** A refusal cites canonical input bytes. If those bytes are not portable, the refusal cannot be replayed by a third party.
- **Class C consensus collapses.** Eligible-attester sets sign canonical bytes. Different canonical bytes, different signatures, different consensus outcome.

The four operative claims of this document:

1. **If two implementations canonicalize the same artifact differently, conformance is not portable.**
2. **Vectors are insufficient without byte-identical canonicalization.**
3. **Cross-language drift invalidates interoperability claims.**
4. **Python-only canonicalization is acceptable for v0.1 but not sufficient for protocol maturity.**

The canonicalization layer is the foundation under every other invariant. A single-byte canonicalization bug in one language port silently invalidates every other property of the protocol for that port. There is no "close enough" for canonical bytes.

---

## 3. Current Python Canonicalizer

The v0.1 Python runtime canonicalizer lives at `intellagent_runtime/canonical.py` and is reproduced here verbatim from the function that the runtime actually calls:

```text
canonical_json_bytes(obj) =
    json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
```

Behavioral properties:

- Object keys are emitted in Python `sort_keys=True` order, which is Unicode code-point order on the keys' Python string values.
- Inter-element separators are `,` and `:` with no whitespace.
- Non-ASCII characters are emitted as raw UTF-8 bytes, not `\uXXXX` escapes.
- The output is bytes, suitable for direct hashing with `sha256_hex` (also in `canonical.py`).

The module's own docstring is explicit about the gap:

> Canonical JSON here is *tooling-internal* canonicalization for fingerprinting and content-addressing. It is NOT a Class A canonicalization scheme; that remains RFC 8785 JCS only, per SPEC.md §4.

In other words: the runtime ships with a deterministic, content-addressing canonicalizer that is sufficient for v0.1's single-implementation, single-language reality. It is not a strict RFC 8785 JCS implementation, and `canonical.py` does not claim to be one.

This is the gap the present document closes mechanically: the golden corpus pins the actual byte output of this Python function so any future port — or any future replacement of this function with a true JCS library — is detectable as drift the moment it lands.

---

## 4. RFC 8785 JCS Requirement

`SPEC.md` §4 fixes RFC 8785 JCS as the canonicalization scheme for Class A v0.1.0. RFC 8785 is the IETF specification for JSON Canonicalization Scheme. Its operative rules:

- UTF-8 output, no BOM, no insignificant whitespace.
- Object keys sorted by UTF-16 code-unit lexicographic order.
- Numbers formatted per ECMA-262 7.1.12.1 (`Number.prototype.toString`), which collapses values like `1.0` to `1`, omits trailing zeros, and uses a specific exponent threshold.
- Strings escaped per ECMA-262 minimal-escaping rules.
- Arrays preserve declaration order; only object keys are reordered.

Areas where the v0.1 Python canonicalizer is *not* strict JCS:

- **Key ordering.** Python `sort_keys=True` orders by Python `str` (Unicode code point). This agrees with UTF-16 code-unit order across the entire Basic Multilingual Plane (BMP) but diverges on supplementary-plane characters (code points above U+FFFF), where UTF-16 surrogate-pair encoding reorders relative to code points.
- **Number formatting.** Python's `json.dumps` emits `1.0` as `1.0`, while ECMA-262 `ToString` emits `1`. Float edge cases (`-0.0`, very small/large magnitudes, exponent thresholds) follow Python's `repr` rules, not ECMA's.
- **String escaping.** Python emits the same escape set as ECMA in nearly all cases, but the two specs differ on a handful of control characters and on whether to escape the line/paragraph separators U+2028 / U+2029 (Python: no; ECMA-262 in some configurations: yes).

The SPEC requirement remains RFC 8785 JCS. This document does not weaken that. It records, in machine-checkable form, the byte output of the current Python implementation so that:

- the gap is observable in concrete digests;
- a v0.2 strict-JCS replacement is detectable as drift against the v0.1 baseline (and the drift is the intended event, gated on coordinated update across ports);
- non-Python implementations can self-test against the v0.1 baseline before claiming JCS compliance.

---

## 5. Drift Failure Modes

Cross-language canonicalization drift manifests in five concrete failure modes. Each is a class of bug that the golden corpus is designed to surface.

**M1. Key-order drift.** Two implementations sort object keys differently, often visible only on supplementary-plane Unicode keys, or on keys differing only in case under a non-default collation.

**M2. Numeric-format drift.** One implementation emits `1`, another emits `1.0`. One emits `1e+20`, another emits `100000000000000000000`. One preserves `-0`, another collapses it to `0`.

**M3. String-escape drift.** One implementation emits a literal forward slash; another emits `\/`. One escapes U+2028 as ` `; another emits the raw bytes. One emits raw UTF-8 for non-ASCII; another emits `\uXXXX`.

**M4. Whitespace and separator drift.** One implementation emits `, ` between array elements; another emits `,`. One emits `: ` between key and value; another emits `:`.

**M5. Encoding drift.** One implementation emits a UTF-8 BOM; another does not. One implementation re-normalizes Unicode (NFC); another preserves the input form.

Every entry in the golden corpus is constructed to exercise at least one of M1–M5.

---

## 6. Test Corpus Requirements

The golden corpus lives at `canonicalization/corpus/`. It is a flat directory of JSON files. Each file:

- MUST be valid JSON parseable by any RFC 8259 conformant parser.
- MUST exercise at least one of the drift failure modes M1–M5.
- MUST be small enough to inline in audit reports (target: under 1 KB each).
- MUST be hand-readable and stable across protocol revisions of the same intent.

The corpus is intentionally finite and frozen. Adding entries is a corpus version event, not a casual change.

The v0.1 corpus has 10 entries:

| File | Drift mode targeted | Purpose |
| --- | --- | --- |
| `001-simple-object.json` | M1, M4 | Baseline two-key object; key sort + separator handling |
| `002-nested-object.json` | M1, M4 | Nested objects + arrays of objects |
| `003-array-order.json` | M4 | Arrays preserve order; only object keys sort |
| `004-unicode.json` | M3, M5 | Non-ASCII strings, multi-byte UTF-8, emoji |
| `005-number-integer.json` | M2 | Signed integers, zero, ±2^53−1 |
| `006-number-float.json` | M2 | Decimals; baseline float emission |
| `007-bool-null.json` | M3 | Literals `true`, `false`, `null` |
| `008-key-order.json` | M1 | Deliberately scrambled keys |
| `009-whitespace.json` | M4 | Whitespace in source must not appear in canonical bytes |
| `010-wiseorder-class-a.json` | all | Realistic Class A artifact shape |

Entry `010` is the load-bearing case: it is the actual artifact shape the runtime sees in production, and it is the first place a real-world drift bug would manifest.

---

## 7. Golden Canonical Bytes

The golden canonical bytes for the v0.1 corpus are committed at `canonicalization/golden/golden-canonical.json`. Each entry stores both the hex-encoded canonical byte sequence (authoritative) and a UTF-8 decoded form (human-readable convenience). The hex form is the source of truth; any conflict is a generation bug.

Generation is deterministic and idempotent:

```bash
make canonicalization-golden
```

The generator (`canonicalization/tools/generate_golden.py`) reads every file in `canonicalization/corpus/` in lexicographic filename order, calls `canonical_json_bytes` from `intellagent_runtime.canonical`, and writes the golden JSON files using `canonical_pretty` (sorted keys, 2-space indent) so the committed files themselves are byte-stable.

Re-running `make canonicalization-golden` on the same corpus on the same Python interpreter MUST produce a byte-identical `golden-canonical.json`. Drift in this file under those conditions is a determinism failure in the canonicalizer itself.

---

## 8. Golden SHA-256 Digests

The golden digests file `canonicalization/golden/golden-digests.json` is the human- and machine-readable summary of the corpus state. It pins:

- the schema version (`0.1.0`);
- the canonicalization scheme identifier currently in use (`python-json-sortkeys-compact-utf8`);
- the digest algorithm (`SHA-256`);
- a per-file SHA-256 digest in `sha256:<64 hex>` form;
- a corpus-wide `corpus_sha256` over the deterministic concatenation of `(filename, canonical_bytes)` pairs in filename-sorted order, providing a single hash for cross-implementation comparison.

The digests file is the artifact a non-Python implementation reproduces. A Rust, TypeScript, or Go canonicalizer is interoperable for v0.1 if and only if it produces a `golden-digests.json` byte-identical to the committed file.

---

## 9. Cross-Language Harness

The canonicalization harness is intentionally minimal. The contract is:

1. Read all files under `canonicalization/corpus/` in lexicographic filename order.
2. Parse each as JSON.
3. Canonicalize each JSON value to bytes per the implementation's canonicalization scheme.
4. SHA-256 each canonical byte sequence.
5. Emit the same `golden-canonical.json` and `golden-digests.json` shape, byte-identical to the committed files.

A non-Python implementation does NOT need to reimplement the runtime, the kernel, or any other module. It only needs to reproduce the canonical bytes for the corpus.

The harness verifier (`canonicalization/tools/verify_golden.py`) re-runs steps 1–5 against the committed golden files and exits non-zero on any mismatch, with a per-file diff so the offending entry is identifiable.

CI invokes the verifier on every push:

```bash
make canonicalization-check
```

---

## 10. Rust Target

A Rust implementation of the canonicalizer is the highest-priority v0.2 deliverable. The minimal Rust harness:

- depends on `serde_json` for parsing only;
- implements canonical emission directly (does not delegate to a JSON serializer with adjustable settings, since serializer settings are precisely the drift surface);
- emits bytes equivalent to the v0.1 Python output for the entire `canonicalization/corpus/`;
- generates `golden-canonical.json` and `golden-digests.json` byte-identical to the committed files.

A Rust implementation that produces a divergent `corpus_sha256` is not interoperable with v0.1, regardless of what its tests claim internally. The Rust target is the first cross-language drift detector and therefore the highest-yield investment.

The Rust harness lives outside this repository at v0.1; the integration point in this repository is a CI step that fetches the Rust harness, runs it against `canonicalization/corpus/`, and diffs its output against `canonicalization/golden/`. That step is not yet wired at v0.1.

---

## 11. TypeScript Target

A TypeScript implementation is the second cross-language target. TypeScript is included specifically because:

- the JCS reference implementation is JavaScript-rooted (RFC 8785 references ECMA-262 explicitly);
- a TypeScript port is the most likely first divergence point on numeric formatting (ECMA-262 `ToString` is the JCS number rule);
- a TypeScript port that matches the v0.1 Python output reveals exactly where Python's `json.dumps` diverges from ECMA-262, since the TypeScript port will naturally emit ECMA-style numbers.

The TypeScript harness:

- runs under Node.js LTS;
- avoids `JSON.stringify` for canonical output (its key order is insertion order, not sorted);
- emits the same artifact format as the Python golden files.

A TypeScript port that does NOT match the v0.1 golden bytes is the expected outcome for some entries (notably `005-number-integer.json` and `006-number-float.json`). That divergence is the v0.2 work item: align canonicalization across both ports, by either upgrading the Python canonicalizer to strict JCS or relaxing the Python output expectation. The choice is a SPEC matter, not an implementation matter.

---

## 12. Go Target

A Go implementation is the third cross-language target. Go is included because:

- Go's standard `encoding/json` library has its own canonicalization quirks (HTML-escaping by default, struct-tag-driven key order);
- a Go port forces explicit confrontation with default-on safety features that subtly mutate canonical output;
- Go is a common host language for trust and audit infrastructure, which is the long-term home of WiseOrder.

The Go harness:

- uses `encoding/json` only for parsing;
- emits canonical bytes through a hand-written serializer;
- disables HTML escaping explicitly;
- emits the same artifact format as the Python golden files.

The Go target is the lowest-priority of the three v0.2 ports because it is the most likely to surface library-default drift rather than canonicalization-spec drift.

---

## 13. Pass/Fail Criteria

A canonicalization implementation (Python, Rust, TypeScript, Go, or any other language) is **interoperable for v0.1** if and only if all of the following hold:

1. It can parse every JSON file in `canonicalization/corpus/` without error.
2. For every file, its canonical byte output matches the committed `golden-canonical.json` entry byte-for-byte.
3. For every file, its SHA-256 of canonical bytes matches the committed `golden-digests.json` entry.
4. Its emitted `corpus_sha256` matches the committed value.

It is **not interoperable for v0.1** if any single byte of any single canonical-bytes entry diverges. There is no partial credit.

Pass/fail is settled by `make canonicalization-check` for Python, and by the corresponding language-specific harness for any other language. Both MUST exit non-zero on any divergence and MUST report the offending entry.

---

## 14. Catastrophic Failure Conditions

The following are catastrophic. Each invalidates the implementation under audit, regardless of other test results.

**C1. Silent acceptance.** A canonicalizer accepts a corpus entry, produces output, but the output's SHA-256 does not match the golden entry, and the implementation does not emit a verification failure.

**C2. Cross-machine divergence.** A canonicalizer produces matching bytes on the development machine but divergent bytes on a CI machine. This is implicit machine-state dependence in canonicalization itself.

**C3. Round-trip instability.** A canonicalizer produces bytes `B` from input `I`, and then produces bytes `B' ≠ B` from input `I` on a second run with no input change.

**C4. Drift of `corpus_sha256` without corpus change.** The corpus content has not changed but the golden `corpus_sha256` has. This is the tightest single signal; it makes any drift one-line-detectable.

**C5. Drift across language ports without a coordinated SPEC update.** Any v0.2+ port introduces a divergence and the divergence is not tied to a documented SPEC bump. This represents an implementation-scoped reinterpretation of the protocol.

C1–C5 are all detectable by the harness defined in §9 plus its language-port equivalents.

---

## 15. Non-Goals

This document does not:

- replace `SPEC.md` §4 or in any way weaken the RFC 8785 JCS requirement for Class A;
- ship a strict-JCS Python canonicalizer at v0.1;
- ship Rust, TypeScript, or Go canonicalizer implementations;
- ship a CI integration that fetches non-Python harnesses;
- bound performance or throughput of the canonicalizer in any language;
- specify a canonicalization for non-JSON formats (CBOR, MessagePack, etc.);
- define a versioning policy for the canonicalizer separate from the protocol version (canonicalization changes are SPEC events).

---

## 16. v0.2 Resolution Path

The v0.1 baseline is "Python-only, sort_keys+compact, golden corpus committed." The v0.2 maturity target is "strict RFC 8785 JCS, multi-language, byte-identical across ports."

The path:

1. **Adopt a strict-JCS Python implementation.** Evaluate the published `rfc8785` and `pyjcs` packages; pick one or vendor a small implementation. Replace `canonical_json_bytes` only after vector regeneration and a coordinated drift event.
2. **Regenerate the golden corpus under the new canonicalizer.** This is a controlled drift event: the old `corpus_sha256` is recorded, the new one is committed, and `RELEASE-STATUS` records the migration.
3. **Bring up the Rust port.** Use the v0.1 corpus as the acceptance test. Diff against the new Python golden files. Land matching.
4. **Bring up the TypeScript port.** Same procedure.
5. **Bring up the Go port.** Same procedure.
6. **Wire all three ports into CI.** Each port's harness runs on every push. Any divergence fails CI.
7. **Declare cross-language interop.** A protocol release (likely v0.2.0) declares interop on the basis of all four implementations producing byte-identical output for the corpus.

The corpus itself is the connective tissue. Steps 3, 4, and 5 are independent; the only ordering constraint is that step 1 precedes them all (the strict-JCS golden is the target, not the v0.1 baseline).

---

## 17. Final Law

> Two implementations that disagree on canonical bytes do not implement the same protocol.

The corpus committed alongside this document makes that disagreement detectable in a single command. Until at least one non-Python implementation produces a byte-identical `corpus_sha256` against the committed golden, the protocol is canonicalization-monolingual, and that fact is recorded as a known limitation in `RELEASE-STATUS-v0.1.md`.

---

**End of CROSS-LANGUAGE CANONICALIZATION v0.1.**
