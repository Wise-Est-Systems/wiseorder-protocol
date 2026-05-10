# RELEASE-CHECKLIST v0.1

**Status:** Pre-release hardening checklist for first external engineering scrutiny.
**Scope:** WiseOrder Protocol v0.1.0 + Intellagent Runtime v0.1 + Transformer Proposer v0.1 + Demos v0.1 + Evaluation v0.1.
**Companion:** [`RELEASE-STATUS-v0.1.md`](./RELEASE-STATUS-v0.1.md) — current pass/fail state across every gate.

This checklist is the operational gate. Everything below MUST be green before tagging `v0.1.0` and inviting external review.

---

## 1. Final gates (in execution order)

| # | Gate | Command | Pass condition |
| - | --- | --- | --- |
| 1 | Documentation code standard | `make no-pseudocode` | Exit 0; "no pseudocode markers found in Python code blocks." |
| 2 | Tooling self-tests | `pytest tests/ -v` | All tests pass (`113 passed` as of v0.1 freeze) |
| 3 | Protocol conformance | `make conformance` | `overall_status: PASS` in `reports/conformance-report.json`; 23/23 vectors pass; 2/2 implementations pass |
| 4 | Interoperability | `make interop` | `overall_status: PASS` in `interop/reports/interop-report.json`; 3/3 fixtures pass |
| 5 | CI chain | `make ci` | "CI: documentation code standard + tooling tests + protocol conformance + interoperability all passed." |
| 6 | Drift verification | `make verify-drift` | "OK: regenerated artifacts match committed state." |
| 7 | Demo runner | `python3 tools/demo_transformer_proposer.py` | `overall: PASS`; exit 0 |

A single gate failure blocks release. There is no partial credit. The gates are designed so that a green run is byte-reproducible against the committed reports.

---

## 2. Reproducibility checks

| Check | How to verify |
| --- | --- |
| **Conformance suite fingerprint stable** | `python3 -c "import json; print(json.load(open('reports/conformance-report.json'))['vectors_suite_sha256'])"` matches the value committed in the report after a fresh `make conformance` run. |
| **Interop manifests suite fingerprint stable** | Same idea, against `interop/reports/interop-report.json`'s `manifests_suite_sha256`. |
| **Audit chain verifies** | After any local runtime use: `python3 -m intellagent_runtime.cli --dir <runtime-dir> audit --verify` returns exit 0. |
| **Deterministic replay** | `pytest tests/test_intellagent_runtime.py::test_deterministic_replay -v` passes. |
| **Demo determinism** | Two runs of `tools/demo_transformer_proposer.py` produce identical SHA-256 digests over the audit-entry bytes (under fixed clock + seed; the demo runner already pins these). |

A reviewer cloning the repo, running `make ci`, and comparing the produced fingerprints against the committed reports MUST get byte-identical agreement.

---

## 3. Required artifacts (must be committed in the release tag)

```
SPEC.md
STATUS-REGISTRY.md
ARTIFACTS.md
CONFORMANCE.md
IMPLEMENTATIONS.md
INTELLAGENT.md
INTELLAGENT-RUNTIME.md
INTELLAGENT-PROPOSERS.md
INTELLAGENT-EVALUATION.md
INTELLAGENT-DEMOS.md
TRANSFORMER-PROPOSER-v0.1.md
TOOLS.md
README.md
RELEASE-CHECKLIST-v0.1.md
RELEASE-STATUS-v0.1.md

vectors/                          # 23 vectors + README + schemas
schemas/                          # vector / manifest / fixture / implementation schemas
intellagent_runtime/              # full runtime package
tools/                            # validators + demo runner + pseudocode scanner
tests/                            # 113 pytest tests
interop/                          # 3 fixtures + manifests + reports
reports/                          # conformance-report.json + summary

Makefile
pyproject.toml
requirements.txt
.gitignore
.github/workflows/conformance.yml
```

`reports/conformance-report.json`, `reports/conformance-summary.txt`,
`interop/reports/interop-report.json`, `interop/reports/interop-summary.txt`,
and every `interop/fixtures/*/*.manifest.json` are **committed**, not regenerated on demand. They are evidence artifacts.

---

## 4. Public demo checklist

Before each public demo run (recorded or live):

| # | Item | How to verify |
| - | --- | --- |
| 1 | Working tree clean | `git status` shows no uncommitted changes |
| 2 | Demo runtime path is `/tmp/...` only | Demo scripts call `tempfile.mkdtemp(prefix=...)` |
| 3 | No real-provider keys in environment unless intentional | `env | grep -iE "OPENAI_API_KEY\|ANTHROPIC_API_KEY"` is empty for default-mode runs |
| 4 | DeterministicMockProvider is the active provider | Demo script source shows `DeterministicMockProvider` constructor |
| 5 | Fixed clock + fixed ID injected | Demo script calls `canonical.set_clock(...)` and `canonical.set_id_fn(...)` before runtime construction |
| 6 | Demo runs successfully twice with identical bundle SHA-256 | Run twice, compare `sha256` of `tar c <bundle> | sha256sum` |
| 7 | Audit chain integrity verified after every search | Demo emits `chain integrity: OK` |
| 8 | Refusal artifact present when expected | The recorded `RefusalRecord` JSON contains the documented `legitimacy_failures` strings |
| 9 | Bundle layout per `INTELLAGENT-DEMOS.md` §21 | `01-runtime-trace.txt`, `02-audit-chain/`, `03-refusals/`, `04-metrics.json`, `05-replay-config.json`, `06-provider-metadata.json` |
| 10 | Audience told upfront: "refusal is success" | Demo introduction script includes the framing |

---

## 5. Fingerprint verification

The release publishes the following fingerprints. A reviewer running `make ci` on the same commit MUST observe the same values.

| Field | Source | How to recompute |
| --- | --- | --- |
| `vectors_suite_sha256` | `reports/conformance-report.json` | `make conformance` then read the field. |
| `manifests_suite_sha256` | `interop/reports/interop-report.json` | `make interop` then read the field. |
| Per-vector `sha256` | `reports/conformance-report.json[].vector_results[].sha256` | Hash of each `vectors/*.json` file's bytes. |
| Per-manifest `manifest_sha256` | `interop/reports/interop-report.json[].interop_results[].manifest_sha256` | Hash of each `interop/fixtures/*/*.manifest.json` bytes. |
| Demo-1 audit shape | (empty audit; one refusal) | Run the Demo 1 CLI sequence and verify `intellagent_audit/` is empty. |
| Demo-4 refusal failure strings | `D2`, `D3`, `CC3` | Run the Demo 4 CLI sequence and verify all three substrings appear in the refusal `legitimacy_failures`. |
| Demo-8 hallucination rejection | `A1: VERIFIED requires expected_digest == observed_digest` | Run the Demo 8 inline script per `INTELLAGENT-DEMOS.md` §16. |
| Determinism replay digest | `b71c7134…` (representative; depends on fixed clock value) | Run the script in `INTELLAGENT-DEMOS.md` §17 with the documented fixed clock. |

If any fingerprint differs from the committed value: do not release. Investigate first; either the runtime's determinism contract has been broken or one of the inputs is not pinned.

---

## 6. CI verification

`.github/workflows/conformance.yml` (committed) executes on every push and pull request:

```
1. checkout
2. setup-python 3.12
3. pip install -r requirements.txt
4. make no-pseudocode
5. pytest tests/ -v
6. make conformance
7. make interop
8. git diff --exit-code -- reports/ interop/   # drift enforcement
```

Verify before tagging:

- The latest CI run on the release commit is green.
- The drift step (#8) shows no diff against committed reports.
- No CI step is skipped, retried, or marked optional.

---

## 7. Release order

The order matters because each step depends on previous steps being green.

1. **Run all gates locally.** `make ci` and `make verify-drift`.
2. **Run all public demo scripts.** `python3 tools/demo_transformer_proposer.py` plus the inline scripts from `INTELLAGENT-DEMOS.md` §§9–18 for the five public-launch demos.
3. **Run the full pytest suite once with `-v`.** Capture the full pass list as evidence.
4. **Recompute and confirm all fingerprints** against the committed reports.
5. **Update `RELEASE-STATUS-v0.1.md`** with the live numbers and the date of the freeze.
6. **Final git status check.** `git status` must show a clean working tree.
7. **Tag the commit:** `git tag v0.1.0 && git push --tags`.
8. **Publish release notes** that link to:
   - `RELEASE-STATUS-v0.1.md`
   - `RELEASE-CHECKLIST-v0.1.md`
   - The five public demos
   - The known-limitations section below.

There is no step 9 in v0.1. No package upload to PyPI, no Docker image, no announcement campaign. Those are post-v0.1 decisions.

---

## 8. Rollback plan

If a defect is discovered post-release:

1. **Mark the v0.1 tag as deprecated** in release notes; do not delete it.
2. **File the defect** with a reproducer (CLI sequence + expected vs. actual).
3. **Bisect** against the committed `vectors_suite_sha256` and `manifests_suite_sha256` to localize whether the defect lives in the protocol, runtime, proposer, or tooling.
4. **Fix the defect** on a hotfix branch; the fix MUST add a regression test.
5. **Run `make ci` on the hotfix branch.** All gates must pass.
6. **Re-run all public demos.** Confirm fingerprints stabilize on the new commit.
7. **Tag `v0.1.1`** (semantic-version-style patch). Update `RELEASE-STATUS-v0.1.md` to point at the patch tag.

For defects in the protocol itself (SPEC.md), the architectural lock applies: a defect that requires changing SPEC.md semantics is a v0.2 conversation, not a v0.1 patch. Document it as an "implementation reality breaks the architecture" trigger and route through the F-series friction log in `IMPLEMENTATIONS.md`.

---

## 9. Known limitations (must be disclosed in release notes)

The following are explicit, documented gaps in v0.1:

1. **Provenance enforcement is unidirectional at v0.1.** The kernel does not currently require object-level `provenance` fields on Class A artifacts. Transition-level provenance (`proposer`, `proposed_at`) is captured automatically. v0.2+ extension target. (See `INTELLAGENT-DEMOS.md` Demo 3.)
2. **No `EnsembleProposer` in v0.1.** Multi-proposer search is demonstrable today via a single proposer emitting multiple candidates in one completion. A first-class ensemble proposer with multiple Provider backends is a v0.2+ extension target. (See Demo 10.)
3. **`B2` enforcement is unidirectional.** The kernel rejects `CONFLICTED` status with single-side observations, but does not yet reject `SUPPORTED` status with present contradictions. v0.2+ extension target. (See Demo 2.)
4. **No replay across providers.** Determinism is per-provider: same `provider` + same `model_id` + same `seed` + same prompt → same completion. Cross-provider replay (e.g., reproducing an OpenAI-generated audit memory on Anthropic) is impossible by design.
5. **No multi-tenant scoping.** Audit memory and refusal corpora are single-tenant in v0.1. Multi-tenant context isolation is a v0.2+ extension target.
6. **No distributed audit memory.** v0.1 is single-host. Class C consensus across multiple writers is described in the spec but not implemented.
7. **WISEATA F-1 unresolved.** WISEATA's line-oriented canonicalization is incompatible with WiseOrder v0.1.0's RFC 8785 JCS lock; WISEATA is registered as Class B only. Resolution path is documented in `IMPLEMENTATIONS.md` F-1.
8. **Optional `evidence.report_sha256` not pre-computed.** A `CONFORMANT` declaration may pin its evidence reports' combined SHA-256, but v0.1 does not ship a helper to compute that fingerprint.
9. **Real-provider runs are not byte-deterministic across machines.** Provider model identity may shift silently. For replay-critical use, pin to local providers (`LocalOpenAICompatibleProvider`) and capture the model fingerprint where the provider exposes one.
10. **No GUI.** All operator interaction is CLI / Python.

These are not defects. They are documented scope boundaries.

---

## 10. Sign-off (operator)

Before tagging:

- [ ] All gates in §1 are green on the release commit.
- [ ] All reproducibility checks in §2 succeed.
- [ ] All required artifacts in §3 are committed.
- [ ] Public demo checklist in §4 has been run end-to-end at least once.
- [ ] All fingerprints in §5 match committed values.
- [ ] CI on the release commit is green.
- [ ] `RELEASE-STATUS-v0.1.md` is updated with live numbers.
- [ ] Known limitations in §9 are disclosed in release notes.
- [ ] Working tree is clean.

Sign-off is the operator's act. The runtime can verify the gates; only an operator can attest that the release has been reviewed.
