# Canonicalization Readiness Audit v0.1

**Work order:** `WO-2026-05-07-001`
**Agent role:** `reviewer`
**Agent identity:** `reviewer-01`
**Date of audit:** 2026-05-07
**Scope:** Canonicalization layer of WiseOrder Protocol v0.1.0 / Intellagent Runtime v0.1.
**Authority:** Reviewer agent only. No implementation patches. No runtime edits. No vector regeneration.
**Companions:** `CROSS-LANGUAGE-CANONICALIZATION-v0.1.md`, `ARCHITECTURE-PRESSURE-TESTS-v0.1.md`, `SPEC-EVOLUTION-POLICY-v0.1.md`, `RELEASE-STATUS-v0.1.md`.

> Two implementations that disagree on canonical bytes do not implement the same protocol. This audit records what is verified, what is unverified, and what must exist before any external party may rely on canonical bytes produced by this repository.

---

## 1. Purpose

This audit inventories the cross-language drift surfaces of the v0.1 canonicalization layer and produces a readiness report against the requirements in `CROSS-LANGUAGE-CANONICALIZATION-v0.1.md`. It modifies no runtime behavior, regenerates no vectors, and proposes no SPEC changes. Its product is observation: every claim is grounded in a file, a digest, a test, or a stated absence.

The audit answers four operative questions:

- What does the repository actually verify about canonical bytes today?
- What does the repository assume but not verify?
- Where would a non-Python implementation diverge from the v0.1 baseline?
- What enforcement must exist before any external party hashes, signs, or replays bytes produced by this canonicalizer?

Findings are scoped to inform a future implementation-readiness work order. They authorize nothing.

---

## 2. Current Canonicalization Scope

The canonicalizer under audit is `intellagent_runtime.canonical.canonical_json_bytes`. Its operative form is the call:

```text
canonical_json_bytes(obj) =
    json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
```

Scheme identifier emitted in `canonicalization/golden/golden-digests.json`:

```text
"canonicalization": "python-json-sortkeys-compact-utf8"
```

The corpus under `canonicalization/corpus/` is exactly 10 entries (`001-simple-object.json` through `010-wiseorder-class-a.json`), each targeting at least one of the M1–M5 drift modes defined in `CROSS-LANGUAGE-CANONICALIZATION-v0.1.md` §5. The committed `corpus_sha256` is:

```text
sha256:c95685bff48c15abc313c462908b05ac309250bc660c2d802ae51af5a8038b09
```

The verifier `canonicalization/tools/verify_golden.py` is the only enforcement target for canonical bytes; it is invoked by `make canonicalization-check`, which is included in `make ci`.

---

## 3. Current Guarantees

The following guarantees are currently *verified* by tests in `tests/test_canonicalization_golden.py` and the verifier under CI. Each is grounded in a named test or named file.

- **G1. Determinism on the same Python interpreter.** `test_generate_golden_is_deterministic` proves two consecutive runs of `generate_golden.py` produce byte-identical `golden-canonical.json` and `golden-digests.json`.
- **G2. Verifier matches committed golden.** `test_verify_golden_passes_against_committed` proves `verify_golden.py` exits 0 on the committed state.
- **G3. Per-entry digest stability.** `test_per_entry_digest_matches_committed` (parametrised over all 10 entries) proves each entry's SHA-256 matches the committed digest.
- **G4. Corpus-wide digest stability.** `test_corpus_sha256_matches_independent_recomputation` proves an independently computed `corpus_sha256` equals the committed value.
- **G5. Key-order normalization.** `test_key_order_normalizes` proves `{"b":2,"a":1}` and `{"a":1,"b":2}` canonicalize to the identical byte string `b'{"a":1,"b":2}'`.
- **G6. Whitespace normalization.** `test_whitespace_normalizes_against_corpus_009` proves no spaces, newlines, or tabs survive in canonical bytes for corpus entry 009.
- **G7. UTF-8 emission for non-ASCII.** `test_unicode_is_stable` proves `café`, `日本語`, and `🌍` survive as raw UTF-8 bytes (not `\uXXXX` escapes) in corpus entry 004.
- **G8. Numeric digest stability.** `test_number_formatting_is_stable` proves digests for entries 005 and 006 match the committed values.
- **G9. Class A artifact digest stability.** `test_class_a_artifact_digest_is_stable` proves entry 010 (realistic Class A shape) matches its committed digest.
- **G10. Mutation detection.** `test_verify_golden_fails_on_corpus_mutation` proves the verifier exits non-zero when any corpus file is altered.
- **G11. Hex/UTF-8 round-trip in committed golden.** `test_canonical_hex_decodes_to_canonical_utf8` proves the hex form decodes to the UTF-8 form for every entry in the committed file.
- **G12. CI inclusion.** `make canonicalization-check` is an explicit dependency of `make ci` per the repository `Makefile`.

The 22 tests in `tests/test_canonicalization_golden.py` collectively underwrite G1–G12. Aggregate test count is reported as **22 / 22 passing** in `RELEASE-STATUS-v0.1.md` §3.

---

## 4. Current Non-Guarantees

The following are *not* guaranteed today. Each is a known absence, recorded explicitly so it is not mistaken for a guarantee by silence.

- **N1. Cross-machine determinism.** No test in this repository proves the canonicalizer produces byte-identical output on two different machines. Determinism is verified within one Python interpreter on one machine per CI run.
- **N2. Cross-Python-version determinism.** The golden corpus is pinned against the Python interpreter that produced it. Determinism across CPython minor versions, across PyPy, and across any future Python 3.x is unverified.
- **N3. Cross-language byte equivalence.** No Rust, TypeScript, Go, or any non-Python implementation produces output verified against the committed golden. The harness contract in §9 of `CROSS-LANGUAGE-CANONICALIZATION-v0.1.md` is defined; no second-language implementation exists in or referenced from this repository.
- **N4. RFC 8785 JCS conformance.** The canonicalizer is documented in its own module docstring as *not* a strict JCS implementation. No test asserts JCS conformance for any input.
- **N5. Number-format compliance with ECMA-262 ToString.** Python `json.dumps` emits `1.0` as `1.0`; ECMA-262 emits `1`. No test proves the canonicalizer produces ECMA-262 number forms.
- **N6. UTF-16 code-unit key ordering.** `sort_keys=True` orders by Unicode code point (Python `str` ordering), which agrees with UTF-16 code-unit order across the BMP only. No test exercises supplementary-plane keys (code points above U+FFFF) where the two orderings diverge.
- **N7. Escape parity with ECMA-262.** No test asserts behavior on U+2028 / U+2029, on the forward-slash escape (`/` vs `\/`), or on the full set of ECMA control-character escapes.
- **N8. NFC / NFD normalization stance.** The canonicalizer does not normalize Unicode. No test proves whether two distinct normal forms of the same logical string canonicalize equivalently or not.
- **N9. Round-trip through external parsers.** No test proves that an external parser (a non-Python JSON library) reads the canonical bytes back into an equivalent value before comparison.
- **N10. Floating-point edge cases.** `-0.0`, subnormals, very large magnitudes near `±1.7e308`, and the exponent threshold at which scientific notation engages are not exercised by the current corpus.
- **N11. Non-JSON content.** Canonicalization is JSON-only. No claim is made about CBOR, MessagePack, or other formats.

N1–N11 are the surface across which any cross-language port will diverge if the divergence is not coordinated.

---

## 5. Cross-Language Drift Surfaces

The surfaces below are the concrete bytes where a non-Python implementation will most likely differ from the v0.1 Python baseline. Each is grounded in the canonicalizer specification as defined in §3 of `CROSS-LANGUAGE-CANONICALIZATION-v0.1.md`.

- **D1. Object key ordering on supplementary-plane characters.** Python orders by Unicode code point; UTF-16 surrogate-pair encoding reorders U+10000+ keys. Two keys differing only above the BMP will sort to different positions across implementations that follow the two rules. Corpus entry 004 contains the emoji `🌍` (U+1F30D) but only as a *value*, not as a key, so this surface is unexercised.
- **D2. Number formatting.** Trailing-zero collapse (`1.0` vs `1`), exponent-threshold rules, and `-0` handling diverge between Python `json.dumps` and ECMA-262 `ToString`. Corpus entries 005 and 006 pin the Python output; an ECMA-faithful port will produce different bytes for these entries.
- **D3. Non-ASCII escape policy.** Python with `ensure_ascii=False` emits raw UTF-8; default `JSON.stringify` in JavaScript emits raw UTF-8 for most code points but escapes ` ` / ` ` in some configurations. A non-Python port that follows the latter will diverge on any string containing these characters.
- **D4. Forward-slash escape.** The JSON spec permits both `/` and `\/`; some libraries emit `\/` by default (notably for HTML safety in JavaScript and Go). The Python canonicalizer emits `/`. A port that does not disable `\/` will diverge.
- **D5. Default HTML-escaping in Go.** `encoding/json` HTML-escapes `<`, `>`, `&` by default; the Python canonicalizer does not. A Go port that does not call `SetEscapeHTML(false)` will diverge.
- **D6. Default insertion-order key emission in JavaScript.** `JSON.stringify` orders keys by insertion order, not lexicographic order. A TypeScript port using `JSON.stringify` directly will diverge for any object with multiple keys.
- **D7. Float-precision rounding.** Languages disagree on the minimum number of digits required to round-trip a `double`. Python uses repr-shortest (PEP 3101); ECMA-262 uses ToString(x); Rust's `serde_json` uses Ryu. The three may produce different decimal forms for the same `f64`.
- **D8. Encoding preamble.** A port that emits a UTF-8 BOM (`EF BB BF`) prepends bytes the Python canonicalizer never emits.

D1–D8 are unexercised in the v0.1 corpus to varying degrees: D2 partially exercised (entries 005 and 006 only), D3–D8 unexercised. A non-Python port that passes the v0.1 golden on entries 001–010 still does not prove parity across D1–D8 in general.

---

## 6. Python vs RFC 8785 JCS Risk Matrix

| Surface | Python v0.1 behavior | RFC 8785 JCS behavior | Risk if relied on across implementations |
| --- | --- | --- | --- |
| Key sort | Unicode code-point | UTF-16 code-unit | Divergence on supplementary-plane keys (D1) |
| Number format | Python `repr` rules | ECMA-262 `ToString` | Divergence on every non-integer-valued float (D2, D7) |
| Trailing zero | preserved (`1.0` → `1.0`) | collapsed (`1.0` → `1`) | Guaranteed divergence on `1.0`, `2.0`, … (D2) |
| `-0.0` | `-0.0` | `0` | Divergence on signed zero (D2) |
| Non-ASCII | raw UTF-8 (`ensure_ascii=False`) | raw UTF-8 | Agreement |
| `U+2028` / `U+2029` | raw UTF-8 | raw UTF-8 | Agreement, but JS environments often diverge (D3) |
| Forward slash | `/` | `/` | Agreement, but Go/JS often diverge (D4) |
| Whitespace | none | none | Agreement |
| Array order | preserved | preserved | Agreement |
| Nested order | recursive `sort_keys` | recursive sort | Agreement on BMP keys (D1 caveat) |
| BOM | absent | absent | Agreement |
| Unicode normalization | none | none | Agreement |

The divergence rows (key sort on supplementary-plane keys; every float-format row) are guaranteed to surface the moment a strict-JCS port runs against the v0.1 golden. This is the controlled-drift event anticipated in §16 of `CROSS-LANGUAGE-CANONICALIZATION-v0.1.md`.

---

## 7. Float Representation Risks

The float surface is the highest-yield divergence surface and the least exercised by the current corpus.

- **F1. Trailing-zero collapse.** Python: `1.0` → `1.0`. ECMA: `1.0` → `1`. Rust serde_json (Ryu): `1.0` → `1.0` (configurable). Three implementations, three plausible outputs.
- **F2. Negative zero.** Python: `-0.0` → `-0.0`. ECMA: `-0` → `0`. Rust Ryu: `-0.0` → `-0.0`. The sign-of-zero handling is a one-byte difference but a one-bit semantic difference.
- **F3. Exponent threshold.** Python switches to scientific notation around `1e16`; ECMA-262 specifies the exact threshold (`1e21` for positive, `1e-6` for negative). The threshold disagreement creates byte divergence for many magnitudes.
- **F4. Round-trip precision.** Python prints the shortest repr that round-trips to the same `double`; Ryu does the same; ECMA-262 ToString does the same — but the three algorithms can produce different shortest representations for the same `double`.
- **F5. Subnormal handling.** `5e-324` (smallest positive double) is implementation-sensitive across languages.
- **F6. NaN and Infinity.** RFC 8259 forbids `NaN` and `±Infinity` in JSON; Python `json.dumps` accepts them and emits `NaN` / `Infinity` literals by default. The current canonicalizer relies on `json.dumps` defaults; an input containing a NaN would emit non-portable bytes.

The current corpus exercises F1 (entry 006 contains `0.5`, `1.5`, `100.25`, etc.) but does not exercise F2–F6. The v0.2 strict-JCS migration must add corpus entries for each.

---

## 8. Unicode Ordering Risks

- **U1. BMP-only key coverage.** All keys in corpus entries 001–010 are ASCII. No corpus entry exercises non-ASCII keys at all, let alone supplementary-plane keys.
- **U2. Code-point vs code-unit divergence.** Two implementations differ in key order if and only if the keys disagree under the two orderings; this requires at least one supplementary-plane character. Any production artifact that contains user-supplied object keys (e.g., Class A artifacts whose keys derive from external input) is at risk.
- **U3. Combining-character normalization.** `é` (U+00E9) and `e` + `́` (U+0065 U+0301) are distinct strings. The canonicalizer does not normalize. Two artifacts that look identical to a human will have distinct canonical bytes if they were produced under different input pipelines.
- **U4. Locale-sensitive collation.** No language in scope uses locale-sensitive collation for JSON key sort, but documentation should record the prohibition explicitly to forestall a future port that "improves" sorting.

The corpus does not exercise U1–U4. All four are areas where a non-Python port could pass the v0.1 golden and still diverge in production.

---

## 9. Escaping Risks

- **E1. Forward slash.** Python emits `/`; some libraries emit `\/`. The corpus does not contain `/` in any string value (verified by inspection of corpus files).
- **E2. U+2028 / U+2029.** Line separator and paragraph separator. Python emits raw UTF-8; some JS configurations emit ` ` / ` `. The corpus does not contain these characters.
- **E3. Control characters.** ASCII control characters (`\x00`–`\x1F`) have a defined escape policy in JSON; libraries differ on the *form* of escape (`` vs `\b` for backspace, etc.). The corpus does not contain control characters.
- **E4. Surrogate-pair escaping.** Code points above U+FFFF may be emitted as a single 4-byte UTF-8 sequence or as a `\uXXXX\uXXXX` surrogate pair. Python with `ensure_ascii=False` emits the former; default JavaScript `JSON.stringify` may emit the latter for ASCII-safe modes. The corpus contains `🌍` (U+1F30D) only as a string value; the value is in entry 004 and is pinned to UTF-8 emission.
- **E5. Quote and backslash escapes.** Both languages and both specs agree; no expected divergence.

E1–E4 are unexercised at the level required for cross-language certainty.

---

## 10. Cross-Machine Risks

- **X1. Endianness.** SHA-256 output is byte-defined; no endianness sensitivity in canonical bytes themselves. Risk is zero at the canonicalizer; risk could appear in a future C/Rust port that mishandles endianness during streaming hash computation.
- **X2. Filesystem case sensitivity.** Corpus filenames are lowercase; the verifier sorts by lexicographic filename. A case-insensitive filesystem (default macOS HFS+/APFS in some configurations) does not change byte order but could mask a duplicate-by-case file. Low risk.
- **X3. Line-ending normalization on checkout.** `git config core.autocrlf` on Windows can rewrite line endings on checkout. The corpus files end in `\n`; a `\r\n` rewrite would change parsed bytes if the JSON parser preserves whitespace (it does not, since whitespace outside strings is insignificant), but a `\r\n` *inside* a string value would change the parsed string and therefore the canonical bytes. The corpus does not contain string values with `\n`; risk is contingent on future corpus additions.
- **X4. Locale-dependent number parsing.** `json.loads` is locale-independent in CPython; some C/JSON libraries are not. A port that uses a locale-sensitive `strtod` (e.g., a German locale with `,` as decimal separator) could parse `0.5` as `5` and re-emit different bytes. Risk localized to ports.
- **X5. Time zone.** No canonicalization input depends on time zone today; risk zero for the canonicalizer, but a future audit must check whether canonicalized artifacts ever embed locally formatted timestamps.

X1, X3, and X5 are not exercised by the current test suite. X2 and X4 are not applicable to the Python port itself.

---

## 11. Replay Continuity Risks

Replay is a byte-level claim per `CROSS-LANGUAGE-CANONICALIZATION-v0.1.md` §2. A drift in canonical bytes invalidates every audit chain, every refusal artifact, and every Class C consensus that referenced the prior bytes.

- **R1. Replay across the v0.1 → v0.2 canonicalizer migration.** The v0.2 strict-JCS canonicalizer will produce different bytes for at least every float entry. Audit chains produced under v0.1 will not replay under v0.2 unless either (a) the v0.1 canonical bytes are stored alongside the artifact and re-hashed under v0.1 rules, or (b) the migration is documented as a recorded discontinuity per `SPEC-EVOLUTION-POLICY-v0.1.md`. Neither path exists in repository tooling today.
- **R2. Replay across Python interpreter upgrades.** Replay continuity within v0.1 depends on `json.dumps` producing identical bytes across CPython versions. CPython has historically held this stable for the inputs in scope, but no automated check exists in CI.
- **R3. Replay across language ports.** No Python-produced audit chain has been replayed by a non-Python implementation, because no non-Python implementation exists. Cross-language replay continuity is unverified.
- **R4. Replay of refusal artifacts.** Refusals reference canonical input bytes per `SPEC.md` §4 (referenced; not opened by this audit). A port that disagrees on canonical bytes cannot reproduce a refusal's challenge surface.
- **R5. Replay across corpus mutation.** Every corpus mutation changes `corpus_sha256`. The mutation-detection test (G10) catches this; what is not caught is the case where a corpus mutation is committed *together with* a regenerated golden, leaving no audit trail of why the bytes changed. Procedural enforcement is documented in `canonicalization/README.md` but not mechanically enforced.

R1, R3, and R5 are the strongest replay risks.

---

## 12. Interoperability Risks

- **I1. Single-language baseline.** The v0.1 canonicalizer is Python-only. The protocol's interoperability claim, per `CROSS-LANGUAGE-CANONICALIZATION-v0.1.md` §17, is explicitly conditional on at least one non-Python port producing byte-identical output. That condition is unmet.
- **I2. No CI integration of non-Python harnesses.** `CROSS-LANGUAGE-CANONICALIZATION-v0.1.md` §10 states the Rust harness lives outside the repository at v0.1 and is not yet wired into CI. Likewise §11 (TypeScript) and §12 (Go).
- **I3. No published interoperability claim.** `RELEASE-STATUS-v0.1.md` does not claim cross-language interoperability; it claims interop *across implementation declarations* (`Winstack`, `WISEATA`), not across language ports of the canonicalizer. The distinction is precise; external readers may conflate the two.
- **I4. No third-party consumer.** No external party currently consumes canonical bytes from this repository in production. The risk surface is bounded today and grows the moment any external party hashes or signs a byte produced here.
- **I5. Vector portability.** Vectors under `vectors/` are JSON; their pass/fail status references behavioral outcomes, not canonical-byte equivalence. A canonicalization drift would not be caught by vector tests directly; it would be caught by `make canonicalization-check` or by a downstream audit-chain verifier.

I1, I2, and I4 jointly mean: every cross-language interoperability claim made today rests on assumption, not evidence.

---

## 13. Current Enforcement Coverage

Mechanical enforcement that exists in the repository today:

- **C-EN-1.** `make canonicalization-check` invokes `canonicalization/tools/verify_golden.py`. Exit code is non-zero on any byte divergence. CI dependency through `make ci`.
- **C-EN-2.** `make canonicalization-golden` regenerates golden files deterministically from the corpus.
- **C-EN-3.** 22 tests in `tests/test_canonicalization_golden.py`, exercising determinism, mutation detection, key-order, whitespace, Unicode, numbers, Class A artifact shape, hex/UTF-8 round-trip, and per-entry digest stability.
- **C-EN-4.** `make no-pseudocode` prevents pseudocode markers from accumulating in markdown, including in this audit.
- **C-EN-5.** `make workforce-check` (added by `WORKFORCE-EXECUTION-RUNTIME-v0.1`) prevents undocumented workflow records.

Each is necessary; none is sufficient against the cross-language drift surfaces in §5.

---

## 14. Missing Enforcement Coverage

Mechanical enforcement that does *not* exist in the repository today:

- **C-MISS-1.** No CI step runs a non-Python canonicalizer against the corpus.
- **C-MISS-2.** No test exercises canonicalization on supplementary-plane Unicode keys (D1).
- **C-MISS-3.** No test exercises ECMA-262 number-format compliance (D2, F1–F6).
- **C-MISS-4.** No test exercises U+2028 / U+2029 in string values (D3, E2).
- **C-MISS-5.** No test exercises forward-slash escape behavior (D4, E1).
- **C-MISS-6.** No test exercises BOM emission absence (D8).
- **C-MISS-7.** No test exercises NaN / Infinity rejection (F6).
- **C-MISS-8.** No test exercises NFC / NFD equivalence (or non-equivalence) (U3).
- **C-MISS-9.** No CI step runs `verify_golden.py` on a second machine (cross-machine determinism N1).
- **C-MISS-10.** No CI step runs `verify_golden.py` under multiple Python interpreter versions (cross-version determinism N2).
- **C-MISS-11.** No mechanical link from corpus mutation to a recorded `RELEASE-STATUS` entry (R5).

Each row is a corpus, a CI step, or a documented procedure away from being enforced. None requires runtime change.

---

## 15. Known Failure Modes

The five drift modes M1–M5 from `CROSS-LANGUAGE-CANONICALIZATION-v0.1.md` §5 plus the implementation-specific risks above produce the following named failure modes for the audit period:

- **F-A. Silent byte drift.** Canonicalizer behavior changes on a Python upgrade; CI on the existing Python version still passes; downstream consumers replaying against new bytes fail.
- **F-B. Undocumented canonicalizer change.** A maintainer edits `canonical.py`, regenerates the golden, and commits both atomically; `make ci` passes; the change is invisible without `git log` review of `canonical.py`.
- **F-C. Replay divergence.** Two consumers replay the same audit chain; one uses v0.1 Python bytes; the other uses a v0.2 strict-JCS port; chains diverge at the first non-integer-valued float.
- **F-D. Cross-language mismatch.** A Rust harness passes 9 of 10 corpus entries and fails on entry 006 (floats); maintainer "fixes" the harness by emitting Python-style numbers; the Rust harness is no longer JCS-conformant.
- **F-E. Nondeterministic serialization.** A future canonicalizer change introduces a dependency on dictionary insertion order or hash randomization; tests on one machine pass; tests on another fail intermittently.
- **F-F. Hidden normalization behavior.** A future canonicalizer change adds NFC normalization "to be safe"; existing audit chains stop replaying for any input that was previously NFD.

F-A, F-B, F-E, and F-F are detectable by mechanical means that do not currently exist (C-MISS-1, C-MISS-9, C-MISS-10, C-MISS-8). F-C and F-D are detectable only with explicit cross-language harness in CI (C-MISS-1).

---

## 16. Catastrophic Failure Conditions

The five conditions C1–C5 from `CROSS-LANGUAGE-CANONICALIZATION-v0.1.md` §14 are reproduced and assessed for current detectability.

| ID | Condition | Detectable today? | Detector |
| --- | --- | --- | --- |
| C1 | Silent acceptance: output produced, digest mismatches golden, no failure emitted | Yes | `verify_golden.py` exits non-zero on per-entry digest mismatch |
| C2 | Cross-machine divergence | No | No second-machine CI step exists |
| C3 | Round-trip instability on the same input | Partial | `test_generate_golden_is_deterministic` covers this within one process; not across processes |
| C4 | Drift of `corpus_sha256` without corpus change | Yes | `test_corpus_sha256_matches_independent_recomputation` plus `verify_golden.py` |
| C5 | Drift across language ports without coordinated SPEC update | No | No second-language CI step exists |

C2 and C5 are undetected. C2 is the harder gap because it requires multi-machine CI infrastructure. C5 requires an external implementation to exist at all.

---

## 17. Release Risk Assessment

Against the criteria recorded in `RELEASE-STATUS-v0.1.md` §1 ("Ready for first external engineering scrutiny"), the canonicalization layer is:

- **Sufficient** for: a single-language v0.1 release where canonical bytes are an internal contract between this repository's runtime and its tests, and where every external claim about "interoperability" is bounded to "implementations that adopt the v0.1 Python canonicalizer byte-for-byte."
- **Insufficient** for: any release that claims cross-language interoperability of canonical bytes; any release that allows third-party consumers to hash, sign, or replay bytes produced by this canonicalizer with the expectation of agreement across language ports; any release that treats `python-json-sortkeys-compact-utf8` as a JCS substitute.

The release risk is therefore one of *claim discipline*, not implementation defect. The implementation behaves exactly as documented; the risk is that external readers may infer guarantees the documentation does not make.

`RELEASE-STATUS-v0.1.md` should be re-read against this audit's §3 (Current Guarantees) and §4 (Current Non-Guarantees) before any external party engages with canonical-byte claims.

---

## 18. Required Future Enforcement

The following enforcement must exist before a v0.2 release that claims cross-language interoperability. Each is one or more discrete work orders, each scoped to a single duty per `AGENT-GOVERNANCE-WORKFORCE-v0.1` §3.

- **EN-FUT-1.** Strict-JCS Python canonicalizer (vendored or via `rfc8785` / `pyjcs`); regenerate golden under controlled drift event.
- **EN-FUT-2.** Corpus extension exercising D1 (supplementary-plane keys), D3 (U+2028 / U+2029), D4 (forward slash), D8 (BOM absence), F2–F6 (negative zero, exponent threshold, round-trip precision, subnormals, NaN/Infinity rejection), U3 (NFC vs NFD).
- **EN-FUT-3.** Rust canonicalizer harness checked into CI; runs against `canonicalization/corpus/`; diffs against the strict-JCS golden.
- **EN-FUT-4.** TypeScript canonicalizer harness checked into CI; same contract.
- **EN-FUT-5.** Go canonicalizer harness checked into CI; same contract.
- **EN-FUT-6.** Cross-machine CI: `verify_golden.py` runs on at least two distinct CI runners (e.g., Linux + macOS) and the outputs are compared.
- **EN-FUT-7.** Cross-Python-version CI: `verify_golden.py` runs under at least two CPython minor versions plus PyPy.
- **EN-FUT-8.** Mechanical link between corpus mutation and `RELEASE-STATUS` entry (a check that fails CI when `corpus_sha256` changes without a corresponding `RELEASE-STATUS` diff).
- **EN-FUT-9.** Refusal-replay test: a refusal artifact produced by Python is re-canonicalized by at least one non-Python harness and the refusal challenge surface matches.
- **EN-FUT-10.** Audit-chain replay test: an audit chain produced by Python is verified by at least one non-Python harness end-to-end.

EN-FUT-1 is the gating prerequisite for EN-FUT-3 / EN-FUT-4 / EN-FUT-5; none of the language ports should target the v0.1 baseline as their final target.

---

## 19. Recommended Priority Order

This audit *recommends*; it does not authorize. Each item is a candidate work order subject to drafting, approval, and assignment.

1. **EN-FUT-2 (corpus extension)** — pure data; no runtime change; surfaces existing divergence without committing to a strict-JCS migration. Lowest blast radius.
2. **EN-FUT-1 (strict-JCS Python)** — the v0.2 enabling step. CANON BREAK candidate; requires `SPEC-EVOLUTION-POLICY-v0.1` review.
3. **EN-FUT-3 (Rust harness)** — highest-yield cross-language detector per `CROSS-LANGUAGE-CANONICALIZATION-v0.1` §10.
4. **EN-FUT-8 (corpus-to-RELEASE-STATUS link)** — small enforcement; closes the audit-trail gap (R5).
5. **EN-FUT-6 (cross-machine CI)** — closes C2.
6. **EN-FUT-4 (TypeScript harness)** — exposes ECMA-262 number-format alignment.
7. **EN-FUT-7 (cross-version Python CI)** — closes N2.
8. **EN-FUT-5 (Go harness)** — completes the three-port cross-language matrix.
9. **EN-FUT-9 (refusal-replay)** — first end-to-end cross-language replay.
10. **EN-FUT-10 (audit-chain replay)** — completes interop story.

The ordering is informed by blast radius (1, 4 are minimal), by gating (2 must precede 3, 4, 5), and by detector yield (3 is the single highest-yield investment).

---

## 20. Non-Goals

This audit does not:

- modify the canonicalizer
- modify the corpus
- regenerate `golden-canonical.json` or `golden-digests.json`
- propose SPEC changes
- propose changes to `Makefile` or to any test
- author or modify Rust, TypeScript, or Go code
- author work orders for any of EN-FUT-1 through EN-FUT-10
- claim cross-language interoperability
- claim JCS conformance
- bind the human owner to any particular priority among EN-FUT-1 through EN-FUT-10

This audit is observation. Every action item it suggests is a future work order requiring its own drafting, approval, and assignment.

---

## 21. Final Assessment

The v0.1 canonicalization layer is internally consistent, deterministic on the Python interpreter that produced the golden, and mechanically enforced by 22 tests plus `make canonicalization-check` in CI. It is *not* RFC 8785 JCS, *not* cross-language verified, *not* cross-machine verified, and *not* cross-Python-version verified. Each of those facts is documented in `CROSS-LANGUAGE-CANONICALIZATION-v0.1.md` and reconfirmed by this audit.

The release risk is bounded today by the absence of external consumers and by the explicit non-claims in `RELEASE-STATUS-v0.1.md`. The risk grows the moment any external party hashes, signs, or replays a byte produced by this canonicalizer with a cross-language expectation.

The strongest single signal is `corpus_sha256`. As long as the committed value (`sha256:c95685bff48c15abc313c462908b05ac309250bc660c2d802ae51af5a8038b09`) matches what the verifier produces, the v0.1 baseline is intact. The moment that hash diverges without a documented, approved migration, every claim in §3 is at risk.

---

## What Would Invalidate Canonicalization Trust?

- **Silent byte drift.** A canonicalizer change that alters the output of `canonical_json_bytes` without a corresponding regeneration of the golden and a recorded `RELEASE-STATUS` entry.
- **Undocumented canonicalizer changes.** Any edit to `intellagent_runtime/canonical.py` that is not accompanied by a SPEC-classified evolution event per `SPEC-EVOLUTION-POLICY-v0.1`.
- **Replay divergence.** Two implementations of the canonicalizer produce different bytes for any single corpus entry.
- **Cross-language mismatch.** Any non-Python implementation produces a divergent `corpus_sha256` and that divergence is not tied to a documented SPEC bump.
- **Nondeterministic serialization.** The canonicalizer's output depends on hash-randomization, dictionary insertion order, locale, time zone, or any other implicit machine state.
- **Hidden normalization behavior.** The canonicalizer normalizes input (NFC, case-folding, whitespace collapsing) without documenting the normalization in `SPEC.md`.

Any one of the above invalidates trust globally. Trust in canonical bytes is binary.

---

## What Is Actually Proven Today?

- The Python canonicalizer is deterministic across consecutive runs of the same generator (`test_generate_golden_is_deterministic`).
- The committed golden matches the canonicalizer's output (G2, `verify_golden.py`).
- All 10 corpus entries produce the expected SHA-256 digests (G3, parametrised over all entries).
- The corpus-wide `corpus_sha256` matches independent recomputation (G4).
- Key-order normalization holds for the simple BMP case (G5).
- Whitespace is stripped from canonical output (G6).
- Non-ASCII characters survive as raw UTF-8, not `\uXXXX` escapes, on entry 004 (G7).
- Number formatting is stable on the corpus's sampled integers and floats (G8).
- The realistic Class A artifact shape canonicalizes stably (G9).
- Mutation detection works: any change to a corpus file fails the verifier (G10).
- The committed hex form decodes to the committed UTF-8 form for every entry (G11).
- `make canonicalization-check` is part of `make ci` (G12, `Makefile`).

These twelve facts are the entire current proof surface.

---

## What Is Merely Assumed Today?

- That `json.dumps` with `sort_keys=True`, `separators=(",", ":")`, and `ensure_ascii=False` will produce identical bytes across CPython 3.x versions (assumption N2).
- That the canonicalizer will produce identical bytes on Linux, macOS, and Windows runners (assumption N1).
- That Python's Unicode code-point key order is acceptable as a substitute for UTF-16 code-unit order (assumption D1, true only across the BMP).
- That number formatting matches consumer expectations (assumption N5, contradicted by ECMA-262 ToString).
- That no consumer relies on JCS-strict bytes (assumption I4, true today, false on first external integration).
- That a future port will adopt the v0.1 baseline rather than RFC 8785 directly (assumption contradicted by §16 of `CROSS-LANGUAGE-CANONICALIZATION-v0.1.md`, which sets strict JCS as the v0.2 target).
- That replay across the v0.1 → v0.2 migration will be handled procedurally (assumption R1; no tooling exists).
- That maintainers will update `RELEASE-STATUS` whenever `corpus_sha256` changes (assumption R5; no mechanical check exists).

Every assumption above is a candidate for mechanical conversion to a guarantee.

---

## What Must Exist Before External Dependence?

Before any external party — auditor, integrator, customer, regulator — may rely on canonical bytes produced by this repository for hashing, signing, replay, or cross-implementation comparison, the following must exist:

- **Pre-1.** A strict RFC 8785 JCS canonicalizer in Python (EN-FUT-1) with the migration recorded as a controlled drift event per `SPEC-EVOLUTION-POLICY-v0.1`.
- **Pre-2.** At least one non-Python canonicalizer (Rust or TypeScript, per the priority in §19) producing byte-identical `corpus_sha256` against the strict-JCS golden, wired into CI (EN-FUT-3 or EN-FUT-4).
- **Pre-3.** Corpus coverage of every drift surface in §5 (EN-FUT-2): supplementary-plane keys, ECMA-262 number formats, U+2028 / U+2029 strings, forward-slash strings, BOM-absence assertion, NaN / Infinity rejection, NFC vs NFD pair.
- **Pre-4.** Cross-machine CI determinism check (EN-FUT-6).
- **Pre-5.** Cross-Python-version CI determinism check (EN-FUT-7).
- **Pre-6.** Mechanical enforcement that any change to `corpus_sha256` is accompanied by a `RELEASE-STATUS` entry (EN-FUT-8).
- **Pre-7.** A documented public statement of which canonicalization scheme is current and what migration path applies, referenced from `RELEASE-STATUS-v0.1.md` and any external-facing material.
- **Pre-8.** A refusal-replay test demonstrating that a Python-produced refusal artifact is reproducible end-to-end by the non-Python implementation (EN-FUT-9).

Pre-1 through Pre-8 are non-optional. External dependence in advance of any one of them is unsupported by the audit evidence.

---

**End of Canonicalization Readiness Audit v0.1.**
