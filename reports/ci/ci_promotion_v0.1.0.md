# CI Promotion Report — v0.1.0

**Work Order:** 009 — CI Promotion and Cold Reproducibility Gate
**Timestamp (UTC):** 2026-05-10T18:09:27Z
**Overall Result:** **PASS**
**Authority:** This document is the evidence record that the four code-first reality checks have been promoted into `make ci` and the repository passes cold from a clean state.

---

## 1. Targets Promoted into `make ci`

| Target | Promoted | Evidence |
|---|---|---|
| `minimal-verifier-check` | YES | 33/33 vectors derived correctly via independent reimplementation |
| `replay-diff-check` | YES | 9/9 self-check fixtures pass |
| `binary-fixture-check` | YES | 4/4 binary fixtures classified correctly |
| `sandbox-escape-check` | YES | 25 hostile attempts refused; 4 controls allowed |

New `ci` target order (`Makefile`):

```
no-pseudocode
test
conformance
interop
canonicalization-check
minimal-verifier-check
replay-diff-check
binary-fixture-check
sandbox-escape-check
```

---

## 2. Cold Verification Commands

| # | Command | Exit code | Result |
|---|---|---|---|
| 1 | `git status --short` | 128 | not_a_git_repository (recorded honestly; see §9) |
| 2 | `make ci` | 0 | PASS |
| 3 | `python -m pytest` | 0 | PASS — 271 tests passed |
| 4 | `make demo` | 0 | PASS — 6 steps + 3 fingerprints MATCH |

---

## 3. CI Stage Results

| Stage | Result | Detail |
|---|---|---|
| `no-pseudocode` | PASS | 62 markdown files scanned; 0 pseudocode markers in Python code blocks |
| `test` | PASS | 271 / 271 tests passed |
| `conformance` | PASS | 33 / 33 vectors; 2 / 2 implementations |
| `interop` | PASS | 3 / 3 fixtures |
| `canonicalization-check` | PASS | 10 corpus entries |
| `minimal-verifier-check` | PASS | 33 / 33 vectors via independent re-derivation |
| `replay-diff-check` | PASS | 9 self-check fixtures |
| `binary-fixture-check` | PASS | 4 / 4 fixtures |
| `sandbox-escape-check` | PASS | 29 attempts (25 hostile refused, 4 controls allowed) |

---

## 4. Test Counts

| Field | Value |
|---|---|
| Total pytest tests | **271** |
| Tests passing | 271 |
| Tests failing | 0 |
| Tests added under WORK ORDER 007 | 136 |

---

## 5. Vector Counts

| Field | Value |
|---|---|
| Total vectors | **33** |
| Baseline vectors | 23 |
| Adversarial vectors | 10 |
| Vectors passing | 33 |
| Vectors failing | 0 |

Adversarial vector identifiers (the 10 hostile vectors added under WORK ORDER 006):

```
class-a-canonicalization-scheme-corruption
class-a-algorithm-downgrade
class-b-replay-drift
class-b-evidence-suppression-attempt
class-c-quorum-inflation
class-c-attestation-replay
class-c-protocol-version-mismatch
class-d-forged-commit-chain
class-d-stage-skip-attempt
class-d-action-compelled-without-quorum
```

---

## 6. Binary Fixture Verdicts

| Fixture | Size | Expected | Derived | Result |
|---|---|---|---|---|
| `valid.bin` | 1056 | VERIFIED | VERIFIED | PASS |
| `corrupted.bin` | 1056 | TAMPERED | TAMPERED | PASS |
| `truncated.bin` | 1040 | TAMPERED | TAMPERED | PASS |
| `byte_mutated.bin` | 1056 | TAMPERED | TAMPERED | PASS |

---

## 7. Sandbox Escape Verdicts

| Category | Hostile attempts | Refused |
|---|---|---|
| `symlink_breakout` | 1 | 1 |
| `path_traversal` | 3 | 3 |
| `forbidden_env` | 6 | 6 |
| `forbidden_network` | 5 | 5 |
| `recursive_subprocess` | 7 | 7 |
| `output_flood` | 3 | 3 |
| `control_allow` (negative controls) | 4 | n/a (4 allowed as expected) |

Total: **29 attempts**, **25 hostile refused**, **4 controls allowed**, all_passed = `true`.

---

## 8. Frozen Fingerprint Match

| Fingerprint | Expected (v0.1.0 lock) | Observed | Match |
|---|---|---|---|
| `vectors_suite_sha256` | `sha256:6168d2075931baa98bba763f9cd537142554aae7b26f19e3e93a60de2ee5bb0f` | `sha256:6168d2075931baa98bba763f9cd537142554aae7b26f19e3e93a60de2ee5bb0f` | YES |
| `manifests_suite_sha256` | `sha256:74eaaa62271f23172232bda43ba3340543e66c46ba1e2f5e6da18d3447a6ba29` | `sha256:74eaaa62271f23172232bda43ba3340543e66c46ba1e2f5e6da18d3447a6ba29` | YES |
| `corpus_sha256` | `sha256:c95685bff48c15abc313c462908b05ac309250bc660c2d802ae51af5a8038b09` | `sha256:c95685bff48c15abc313c462908b05ac309250bc660c2d802ae51af5a8038b09` | YES |

All three frozen fingerprints reproduced byte-for-byte.

---

## 9. Transient Failures

**None during this CI promotion run.** No target was bypassed, removed, or marked known-good.

For audit completeness, prior transient failures fixed during WORK ORDER 007 (already resolved before this report):

- `tests/test_minimal_verifier.py::test_minimal_verifier_does_not_import_intellagent_runtime` — initially used substring matching that flagged the docstring; rewritten as an AST-based check. Also previously asserted on `sys.modules`, which was order-dependent under the full pytest session; that runtime check was removed in favor of the static AST check. Currently passes in isolation and under `make ci`.

---

## 10. Repo Status

The directory `~/Desktop/wiseorder-protocol/` is **not** a git repository. `git status --short` returns exit code 128 (`fatal: not a git repository`).

This is recorded honestly per WORK ORDER 009 §4 (do not bypass, do not mark as known-good). The CI promotion itself does not depend on git state; the four target files (`Makefile`, the two reports under `reports/ci/`) are present on the filesystem and their effect is verified by the command outputs above.

If the user wants the repo under version control, that is a separate task outside this work order's scope.

---

## 11. Files Modified / Created

**Modified:**
- `Makefile` — `ci` target now depends on `minimal-verifier-check replay-diff-check binary-fixture-check sandbox-escape-check`; the trailing `@echo` summary updated to enumerate all nine stages.

**Created:**
- `reports/ci/ci_promotion_v0.1.0.md` (this document)
- `reports/ci/ci_promotion_v0.1.0.json` (machine-readable equivalent)

No code changes. No spec changes. No canon changes.

---

## 12. CI Coverage Status

> **CI now covers the code-first reality layer.**

The nine stages of `make ci` exercise: documentation discipline, the unit-test suite, the protocol vector suite (including 10 adversarial vectors), interop fixtures, byte-identical canonicalization, an independent re-derivation of vector verdicts, replay-diff classification, binary integrity verdicts, and sandbox-escape refusal logic — in a single command, deterministically, with all three frozen fingerprints reproduced.

---

## 13. Next Code Task

Begin the **first independent verifier implementation track in Rust**, per `IMPLEMENTATION_TRACKER.md §2.1`.

**Constraints:**
- MUST NOT import or translate `intellagent_runtime` directly.
- MUST be derived from `SPEC.md`, `SPEC_LOCK_v0.1.md`, `schemas/`, and the published vector and canonicalization corpora.
- MUST emit byte-equivalent verdicts to the published vector suite.

**Acceptance criteria:**
- Reproduces `vectors_suite_sha256 = sha256:6168d2075931baa98bba763f9cd537142554aae7b26f19e3e93a60de2ee5bb0f` byte-for-byte.
- Reproduces `manifests_suite_sha256 = sha256:74eaaa62271f23172232bda43ba3340543e66c46ba1e2f5e6da18d3447a6ba29` byte-for-byte.
- Reproduces `corpus_sha256 = sha256:c95685bff48c15abc313c462908b05ac309250bc660c2d802ae51af5a8038b09` byte-for-byte.
- Submitted via `IMPLEMENTATION_TRACKER.md §4` (independent-implementer submission).

This task is the largest remaining gap blocking v0.1.0's external-validation claim.
