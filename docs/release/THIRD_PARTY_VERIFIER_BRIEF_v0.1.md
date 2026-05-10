# Third-Party Verifier Brief — WiseOrder Protocol v0.1.0

**Audience:** A party other than Wise.Est Systems intending to build a verifier that the WiseOrder project will accept as **third-party validation** of v0.1.0.
**Adopted:** 2026-05-10
**Authority:** `IMPLEMENTATION_TRACKER.md §1` defines what "independent" means. This brief is the operational version of that rule.

---

## 1. Objective

Produce a verifier that:

- is authored, owned, and operated by a party that is not Wise.Est Systems,
- derives its verdict logic and canonicalization rules from the v0.1.0 published sources of truth (no copying of first-party verifier code),
- reproduces the three frozen fingerprints byte-for-byte,
- emits per-vector and per-corpus-entry verdicts matching the v0.1.0 expectations,
- is reproducible by a fourth party from a published commit.

If you can do all five, your submission externally validates v0.1.0 for the class(es) you implement, per `IMPLEMENTATION_TRACKER.md §4–§6`.

## 2. Forbidden Shortcuts

You **MUST NOT**:

- Import, link against, or shell out to the Python `intellagent_runtime` package.
- Copy or transliterate (line-for-line) any of the first-party verifier code, including but not limited to:
  - `intellagent_runtime/*`
  - `tools/minimal_verifier.py`
  - `tools/run_conformance.py`
  - `rust_verifier/src/*`
  - `canonicalization/tools/*`
- Read `reports/conformance-report.json` or `interop/reports/interop-report.json` as your *source of truth* for verdicts (you may use them to compare your output against, but not as input you copy from).
- Modify any file under `vectors/`, `schemas/`, `canonicalization/corpus/`, or `canonicalization/golden/`.
- Modify the frozen fingerprint values.
- Add yourself to `IMPLEMENTATIONS.md` without a working build whose output is reproducible by a fourth party.

You **MAY**:

- Read `SPEC.md`, `SPEC_LOCK_v0.1.md`, schemas, and vector / corpus JSON files for the *definition* of verdict rules.
- Read `tools/run_conformance.py`, `interop/scripts/run_interop_checks.py`, and `canonicalization/tools/generate_golden.py` to understand the **contract** of the three fingerprint formulas (the rule of how they compose). You may not copy their implementations; you must re-implement the rule from understanding.

## 3. Allowed Sources of Truth

| File / directory | What you use it for |
|---|---|
| `SPEC.md` | Verdict rules (Class A/B/C/D), commit-chain invariants, action-governance separation, telemetry-rejection rule |
| `SPEC_LOCK_v0.1.md` | The set of frozen surfaces and the version-increment rule |
| `schemas/*.json` | Vector / fixture / manifest / implementation declaration schemas |
| `vectors/*.json` | Input artifacts and expected `expected_status` per vector |
| `canonicalization/corpus/*.json` | Inputs for canonicalization parity |
| `canonicalization/golden/golden-digests.json` | Expected per-entry SHA-256 digests (you compare against these; you do not copy from them) |
| `interop/fixtures/*/*.manifest.json` | Committed manifest disk bytes that feed `manifests_suite_sha256` |
| `docs/release/EXTERNAL_REVIEW_PACKET_v0.1.md` | Reviewer-facing summary; this brief is its formal companion |
| RFC 8785 | The canonicalization scheme declared for Class A artifacts |

## 4. Required Outputs

Your verifier MUST emit, in any format you choose, at minimum:

1. **Vector verdicts**: a per-vector record showing `vector_id`, declared `expected_status`, derived verdict, and pass/fail.
2. **Canonicalization corpus verdicts**: per-entry observed digest and pass/fail against the golden file.
3. **Fingerprint trio**: the three SHA-256 values computed by your implementation.
4. **A run log or report** that captures the above plus your toolchain version and dependencies.
5. **An implementation declaration** suitable for inclusion in `IMPLEMENTATIONS.md` (`schemas/implementation.schema.json`).

## 5. Required Fingerprints

Your verifier MUST reproduce the v0.1.0 lock anchors exactly:

```
vectors_suite_sha256    sha256:6168d2075931baa98bba763f9cd537142554aae7b26f19e3e93a60de2ee5bb0f
manifests_suite_sha256  sha256:74eaaa62271f23172232bda43ba3340543e66c46ba1e2f5e6da18d3447a6ba29
corpus_sha256           sha256:c95685bff48c15abc313c462908b05ac309250bc660c2d802ae51af5a8038b09
```

Formulas (the *rule*, not the implementation):

- **`vectors_suite_sha256`** — for each `vectors/*.json` compute the SHA-256 of the raw file bytes (lowercase hex, **no** prefix). Sort by the `vector_id` field. Join with `\n` (no trailing newline). UTF-8 encode. SHA-256. Prefix with `sha256:`.
- **`manifests_suite_sha256`** — same, over `interop/fixtures/<impl>/*.manifest.json`, sorted by `fixture_id`. **Difference:** the per-manifest digests are emitted in `sha256:` *prefixed* form before joining.
- **`corpus_sha256`** — single running SHA-256, fed in lexicographic filename order with `file_id_utf8 || 0x00 || canonical_bytes || 0x00`. `canonical_bytes` follows the tooling-internal canonicalization scheme (sorted keys, compact separators, UTF-8 strings, shortest-roundtrip number formatting). The per-entry expected digests in `canonicalization/golden/golden-digests.json` show exactly what canonical bytes the running hasher consumes.

## 6. Required Failure Handling

If your verifier produces a divergent fingerprint or vector verdict, you MUST:

- Identify the exact divergence (which file, which field, which byte).
- Classify the cause as one of: **verdict-logic mismatch**, **canonicalization mismatch**, **ordering assumption**, **path assumption**, **JSON-parser quirk**, **environmental locale**, **UNKNOWN**.
- File the divergence in your submission's run log.
- NOT silently coerce your output to match. Coercion is disqualifying.

## 7. Submission Requirements

To register as an external-validation implementation, submit:

1. **Source repository URL** under your party's control (not Wise.Est Systems').
2. **Commit hash** of the verified build.
3. **Conformance report** in any structured format, including:
   - per-vector verdicts (33 entries)
   - per-corpus-entry digests (10 entries)
   - the three fingerprint values
   - your toolchain version and dependency list
4. **Implementation declaration** that validates against `schemas/implementation.schema.json`. Attach it to `IMPLEMENTATIONS.md` via PR / patch / equivalent.
5. **Independence statement** signed by the authoring party affirming all of:
   - "I/we are not Wise.Est Systems or its agent."
   - "I/we did not copy first-party verifier source line-for-line."
   - "I/we have read `THIRD_PARTY_VERIFIER_BRIEF_v0.1.md §2` and have not taken any forbidden shortcut."
6. **License** under which your verifier is released.
7. **Reproducibility instructions** sufficient for a fourth party to clone, build, and reproduce your fingerprint output from scratch.

Submission target: open an issue or PR against the WiseOrder repository, or contact the project per channels listed in `IMPLEMENTATIONS.md`.

## 8. Disqualification Conditions

Any of the following invalidates your submission as third-party validation. They are not mistakes to fix; they are categorical disqualifiers:

- **Importing or wrapping the first-party Python runtime.** This includes any of: `import intellagent_runtime`, `from intellagent_runtime …`, FFI bindings via PyO3/CPython that link the package, subprocess invocations of `python3 tools/…`.
- **Line-by-line copying of first-party verifier logic.** This includes `tools/minimal_verifier.py`, `tools/run_conformance.py`, `rust_verifier/src/*`, and `canonicalization/tools/*`. AST-equivalent translation is also disallowed; the rule must be re-derived.
- **Modifying vectors.** Any change to any file under `vectors/`, including reformatting that alters byte content.
- **Modifying fingerprints.** Any change to the three frozen values in `SPEC_LOCK_v0.1.md`, `README.md`, or any other location.
- **Modifying the canonicalization corpus.** Any change under `canonicalization/corpus/` or `canonicalization/golden/`.
- **Claiming validation without publishing reproducible evidence.** Private repos, unverifiable commit hashes, or non-public binaries are not acceptable.
- **First-party masquerade.** A submission by a party employed by, contracting with, or directed by Wise.Est Systems, irrespective of repository ownership.
- **Coercing output to match.** Hard-coding the expected fingerprint values or vector verdicts in your code so the comparison "passes" without actually deriving them.
- **Refusing to disclose dependencies.** A verifier whose dependency list cannot be audited cannot be classified as independent.

A submission tagged with any of these is recorded but is not third-party validation.

---

## Independence Test (Quick Self-Check Before Submitting)

If you can answer "no" to all of the following, you may proceed:

1. Did you `import` or load any module named `intellagent_*`, `wiseata*`, or `winstack*` ?
2. Did you copy any source file from this repository's `intellagent_runtime/`, `tools/minimal_verifier.py`, `tools/run_conformance.py`, `rust_verifier/`, or `canonicalization/tools/` directly into your tree?
3. Did your verdict logic come from reading first-party code rather than from reading `SPEC.md` + `vectors/*.json`?
4. Did you read `reports/conformance-report.json` and use its `vector_results` as your output instead of computing them yourself?
5. Did you hard-code any of the three frozen fingerprint values as the *output* of your computation rather than as an *assertion target*?
6. Are you, or your authoring party, in any contractual or employment relationship with Wise.Est Systems for this work?

"Yes" on any of these means you have not yet produced third-party validation. Fix the cause and retry.
