# Repo Organization Plan — v0.1

**Status:** Plan for WORK ORDER 011. Defines the target shape of the repository before any files are moved.
**Adopted:** 2026-05-10
**Authority:** This plan is the classification record. Once executed, the result is captured in `reports/repo_health/repo_organization_v0.1.md`.

---

## 1. Rules

- Preserve evidence. Nothing is deleted; noisy reports are archived.
- Preserve reproducibility. Frozen v0.1.0 fingerprints MUST still match after the move.
- Preserve code behavior. `make ci` and `make demo` MUST stay green.
- Do not rename files. Move only.
- Do not change `SPEC.md`, vectors, schemas, canonicalization corpus, or runtime semantics.

## 2. Root After Organization

The repository root SHALL contain only these markdown documents:

- `README.md`
- `SPEC.md`
- `SPEC_LOCK_v0.1.md`
- `CONFORMANCE.md`
- `IMPLEMENTATIONS.md`
- `ARTIFACTS.md`
- `STATUS-REGISTRY.md`
- `TOOLS.md`

Plus build/manifest files:

- `Makefile`
- `pyproject.toml`
- `requirements.txt`
- `.gitignore` (created during execution)

Plus the top-level code/data directories (unchanged):

- `intellagent_runtime/`, `tools/`, `tests/`
- `vectors/`, `schemas/`, `canonicalization/`, `binary_fixtures/`, `interop/`, `workforce/`, `site/`
- `reports/`
- `.venv/`, `.github/`, `.pytest_cache/`, `intellagent_wiseorder.egg-info/` (build/env)

## 3. Doc Classification

### docs/specs/
- `INTELLAGENT-MASTER-SPEC-STANDARD-v1.0.md`
- `CANONICAL-RELEASE-v0.1.md`
- `CROSS-LANGUAGE-CANONICALIZATION-v0.1.md`
- `SPEC-EVOLUTION-POLICY-v0.1.md`
- `INPUT-GRAMMAR-v0.1.md`
- `WORKFLOW-GRAMMAR-v0.1.md`
- `TRANSLATION-LAYER-v0.1.md`

### docs/laws/
- `AUTHORITY-LAW-v0.1.md`
- `CORRECTION-LAW-v0.1.md`
- `REPLAY-LAW-v0.1.md`
- `TRUST-LAW-v0.1.md`
- `VALIDATION-LAW-v0.1.md`
- `FORBIDDEN-SURFACES-v0.1.md`
- `WAIVER-MECHANISM-v0.1.md`
- `STATUS-LABELING-RULE.md`

### docs/runtime/
- `INTELLAGENT.md`
- `INTELLAGENT-RUNTIME.md`
- `INTELLAGENT-PROPOSERS.md`
- `INTELLAGENT-DEMOS.md`
- `INTELLAGENT-EVALUATION.md`
- `TRANSFORMER-PROPOSER-v0.1.md`
- `PIPELINE-RUNTIME-v0.1.md`
- `PROPOSER-RUNTIME-v0.1.md`
- `REVIEW-GATE-RUNTIME-v0.1.md`
- `REAL-AGENT-RUNTIME-v0.1.md`
- `REAL-AGENT-RUNTIME-v0.2.md`
- `OS-ISOLATION-RUNTIME-v0.1.md`
- `RESOURCE-LIMIT-RUNTIME-v0.1.md`
- `WORKFORCE-EXECUTION-RUNTIME-v0.1.md`
- `WORKFORCE-HARDENING-v0.2.md`
- `WORKFORCE-SANDBOX-STRESS-v0.1.md`
- `AGENT-GOVERNANCE-WORKFORCE-v0.1.md`
- `ARCHITECTURE-PRESSURE-TESTS-v0.1.md`
- `OPERATIONAL_DEMO_v0.1.md`

### docs/whitepapers/
- `WISEORDER-WHITEPAPER-PART-1-FOUNDATIONS.md`
- `WISEORDER-WHITEPAPER-PART-2-MECHANICS.md`
- `WISEORDER-WHITEPAPER-PART-3-LAYERS.md`
- `WISEORDER-WHITEPAPER-PART-4-CONFORMANCE.md`
- `WISEORDER-INTELLAGENT-WHITEPAPER-v1.md`
- `WISEORDER-SYSTEMS-ARCHITECTURE-v1.md`

### docs/release/
- `RELEASE-CHECKLIST-v0.1.md`
- `RELEASE-STATUS-v0.1.md`
- `CROSS_MACHINE_REPLAY_REPORT.md`
- `IMPLEMENTATION_TRACKER.md`

### docs/strategy/
- `ADOPTION-LADDER-v0.1.md`
- `DEPENDENCY-GRADIENT-v0.1.md`
- `MASTER-ROADMAP-v0.1.md`

### docs/audits/
- `AUDIT_SCOPE_v0.1.md`

### Root (unmoved — see §2)
The eight root-critical markdown documents listed in §2.

## 4. Reports Classification

### reports/canonical/ (visible canonical evidence)
- `reports/conformance-report.json`
- `reports/conformance-summary.txt`
- `reports/ci/` (entire directory)
- Top-level `reports/*.md` summary docs (`MILESTONE-FOUNDATION-v0.1.md`, `DOC-COMPLETION-AUDIT-v0.1.md`, etc.)
- `reports/canonical/README.md` (new — names what is canonical)

### reports/<runtime>/ (kept in place; canonical per-runtime evidence)
- `reports/<runtime>/<runtime>_v0.{1,2}.{json,md}` — self-check summaries
- `reports/<runtime>/_fixtures/` — fixture inputs

### reports/archive/<runtime>/ (timestamped per-run noise)
- `reports/pipeline_runtime/pipeline-*T*Z.{json,md}`
- `reports/proposer_runtime/proposal-*T*Z.{json,md}`
- `reports/review_gate_runtime/review-*T*Z*.{json,md}`
- `reports/os_isolation_runtime/runs/run-*.json`
- `reports/resource_limit_runtime/runs/run-*.json`

## 5. Code Layout (unchanged)

- `intellagent_runtime/` — reference kernel (Python)
- `tools/` — validators, runtimes, demo, replay-diff, minimal-verifier, binary-fixture-check, sandbox-escape-check
- `tests/` — pytest suite
- `vectors/`, `schemas/`, `canonicalization/`, `binary_fixtures/`, `interop/`, `workforce/`, `site/` — corpora, fixtures, governed-execution scaffolding, public-facing site

## 6. Path-Reference Fixes Required After Move

Moves break four references that must be updated minimally:

1. `tools/check_no_pseudocode.py` `DOCS_GLOBS` — add `docs/**/*.md` so the scanner still sees moved docs.
2. `tools/real_agent_runtime.py:2803` — `REPO_ROOT / "REAL-AGENT-RUNTIME-v0.1.md"` → `REPO_ROOT / "docs" / "runtime" / "REAL-AGENT-RUNTIME-v0.1.md"`.
3. `README.md` — relative doc links updated to `./docs/<sub>/<file>.md`.
4. `site/index.html` — `<a href="../X.md">` updated to `<a href="../docs/<sub>/X.md">` for moved files.

No semantic changes. No other code changes. Vectors, schemas, runtime kernel, and canonicalization corpus are not touched.

## 7. Makefile Additions (non-destructive)

- `make repo-health` — emit a one-shot summary of the repo organization state.
- `make report-inventory` — list canonical vs archived report files.
- `make archive-reports-dry-run` — print what `make archive-reports` would move; modify nothing.

No destructive `make clean` target. No deletion is performed.

## 8. .gitignore Required Entries

Excluded:
- `.venv/`, `__pycache__/`, `*.pyc`, `.DS_Store`
- `.wiseorder_keys/`, `intellagent_wiseorder.egg-info/`
- `reports/archive/`
- `build/`, `dist/`
- `.pytest_cache/`

NOT excluded (must remain tracked):
- `vectors/`, `schemas/`, `canonicalization/`, `binary_fixtures/`
- `reports/ci/`, `reports/canonical/`
- `reports/conformance-summary.txt`, `reports/conformance-report.json`

## 9. Verification After Execution

- `make ci` MUST exit 0.
- `make demo` MUST exit 0 with all three frozen fingerprints MATCH.
- `git status --short` after `git init` MUST show only the expected baseline.
- 271 tests MUST still pass.
- 33 vectors MUST still pass.

If `make ci` fails for path reasons, fix the smallest reference required and rerun. If it fails for semantic reasons, the move was wrong and is reverted.
