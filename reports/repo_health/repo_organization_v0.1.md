# Repo Organization Report — v0.1

**Work Order:** 011 — Repo Organization and Version-Control Baseline
**Timestamp (UTC):** 2026-05-10T18:30:00Z
**Overall Result:** **PASS**
**Authority:** This document is the evidence record that the workbench has been organized into an inspectable engineering repo without changing protocol semantics, runtime behavior, or canonical evidence.

---

## 1. Files Moved (49 total)

| Target directory | Count | Files |
|---|---|---|
| `docs/specs/` | 7 | `INTELLAGENT-MASTER-SPEC-STANDARD-v1.0.md`, `CANONICAL-RELEASE-v0.1.md`, `CROSS-LANGUAGE-CANONICALIZATION-v0.1.md`, `SPEC-EVOLUTION-POLICY-v0.1.md`, `INPUT-GRAMMAR-v0.1.md`, `WORKFLOW-GRAMMAR-v0.1.md`, `TRANSLATION-LAYER-v0.1.md` |
| `docs/laws/` | 8 | `AUTHORITY-LAW-v0.1.md`, `CORRECTION-LAW-v0.1.md`, `REPLAY-LAW-v0.1.md`, `TRUST-LAW-v0.1.md`, `VALIDATION-LAW-v0.1.md`, `FORBIDDEN-SURFACES-v0.1.md`, `WAIVER-MECHANISM-v0.1.md`, `STATUS-LABELING-RULE.md` |
| `docs/runtime/` | 19 | `INTELLAGENT.md`, `INTELLAGENT-RUNTIME.md`, `INTELLAGENT-PROPOSERS.md`, `INTELLAGENT-DEMOS.md`, `INTELLAGENT-EVALUATION.md`, `TRANSFORMER-PROPOSER-v0.1.md`, `PIPELINE-RUNTIME-v0.1.md`, `PROPOSER-RUNTIME-v0.1.md`, `REVIEW-GATE-RUNTIME-v0.1.md`, `REAL-AGENT-RUNTIME-v0.1.md`, `REAL-AGENT-RUNTIME-v0.2.md`, `OS-ISOLATION-RUNTIME-v0.1.md`, `RESOURCE-LIMIT-RUNTIME-v0.1.md`, `WORKFORCE-EXECUTION-RUNTIME-v0.1.md`, `WORKFORCE-HARDENING-v0.2.md`, `WORKFORCE-SANDBOX-STRESS-v0.1.md`, `AGENT-GOVERNANCE-WORKFORCE-v0.1.md`, `ARCHITECTURE-PRESSURE-TESTS-v0.1.md`, `OPERATIONAL_DEMO_v0.1.md` |
| `docs/whitepapers/` | 6 | `WISEORDER-WHITEPAPER-PART-{1..4}-*.md`, `WISEORDER-INTELLAGENT-WHITEPAPER-v1.md`, `WISEORDER-SYSTEMS-ARCHITECTURE-v1.md` |
| `docs/release/` | 5 | `RELEASE-CHECKLIST-v0.1.md`, `RELEASE-STATUS-v0.1.md`, `CROSS_MACHINE_REPLAY_REPORT.md`, `IMPLEMENTATION_TRACKER.md`, `REPO-ORGANIZATION-PLAN-v0.1.md` |
| `docs/strategy/` | 3 | `ADOPTION-LADDER-v0.1.md`, `DEPENDENCY-GRADIENT-v0.1.md`, `MASTER-ROADMAP-v0.1.md` |
| `docs/audits/` | 1 | `AUDIT_SCOPE_v0.1.md` |

No files renamed. No content modified during the move.

## 2. Directories Created

```
docs/{specs,laws,runtime,whitepapers,release,strategy,audits}/
reports/canonical/
reports/repo_health/
reports/archive/{pipeline_runtime,proposer_runtime,review_gate_runtime}/
reports/archive/os_isolation_runtime/runs/
reports/archive/resource_limit_runtime/runs/
```

## 3. Reports Archived (566 total, 0 deleted)

| Source | Archive target | Files moved |
|---|---|---|
| `reports/pipeline_runtime/pipeline-*T*Z.{json,md}` | `reports/archive/pipeline_runtime/` | 114 |
| `reports/proposer_runtime/proposal-*T*Z.{json,md}` | `reports/archive/proposer_runtime/` | 194 |
| `reports/review_gate_runtime/review-*T*Z*.{json,md}` | `reports/archive/review_gate_runtime/` | 204 |
| `reports/os_isolation_runtime/runs/run-*Z*.json` | `reports/archive/os_isolation_runtime/runs/` | 24 |
| `reports/resource_limit_runtime/runs/run-*Z*.json` | `reports/archive/resource_limit_runtime/runs/` | 30 |

Each runtime directory retains its canonical `<runtime>_v0.{1,2}.{json,md}` summary plus any `_fixtures/` and `profiles/` subdirectories. See [`../canonical/README.md`](../canonical/README.md) for the canonical-vs-archived rule.

## 4. Root Files Remaining

| Markdown (8) | Build/manifest (4) | Top-level directories (13) |
|---|---|---|
| `README.md` | `Makefile` | `.github/`, `binary_fixtures/`, `canonicalization/`, `docs/`, `intellagent_runtime/`, `interop/`, `reports/`, `schemas/`, `site/`, `tests/`, `tools/`, `vectors/`, `workforce/` |
| `SPEC.md` | `pyproject.toml` | |
| `SPEC_LOCK_v0.1.md` | `requirements.txt` | |
| `CONFORMANCE.md` | `.gitignore` | |
| `IMPLEMENTATIONS.md` | | |
| `ARTIFACTS.md` | | |
| `STATUS-REGISTRY.md` | | |
| `TOOLS.md` | | |

Ignored directories (`.venv/`, `__pycache__/`, `.pytest_cache/`, `intellagent_wiseorder.egg-info/`, `reports/archive/`) remain on disk but are not tracked.

## 5. Code/Path Reference Fixes

Five files updated to keep references valid after the doc moves. No semantic changes.

| File | Change | Reason |
|---|---|---|
| `tools/check_no_pseudocode.py` | Added `docs/**/*.md`, `reports/canonical/**/*.md`, `reports/repo_health/**/*.md` to `DOCS_GLOBS` | Moved docs MUST still be scanned by the pseudocode standard |
| `tools/real_agent_runtime.py` | `spec_path = REPO_ROOT / "docs" / "runtime" / "REAL-AGENT-RUNTIME-v0.1.md"` | Self-check spec_path updated to match new location |
| `README.md` | Updated relative links for `INTELLAGENT*`, `TRANSFORMER-PROPOSER-v0.1`, `CROSS_MACHINE_REPLAY_REPORT`, `IMPLEMENTATION_TRACKER`, `AUDIT_SCOPE_v0.1`, `OPERATIONAL_DEMO_v0.1`, `RELEASE-CHECKLIST-v0.1`, `RELEASE-STATUS-v0.1` to point under `docs/<sub>/` | Moved docs MUST be linkable from the README |
| `site/index.html` | Updated three `href` values for `OPERATIONAL_DEMO_v0.1.md`, `IMPLEMENTATION_TRACKER.md`, `AUDIT_SCOPE_v0.1.md` to point under `../docs/<sub>/` | Static site links MUST resolve after the move |
| `Makefile` | Added `.PHONY` entries and recipes for `repo-health`, `report-inventory`, `archive-reports-dry-run` | WORK ORDER 011 §5 — non-destructive cleanup affordances |

## 6. Makefile Targets Added

| Target | Purpose | Destructive? |
|---|---|---|
| `repo-health` | Print one-shot summary of root files, docs/* counts, reports/* counts, current frozen fingerprints | NO |
| `report-inventory` | List canonical vs archived report files | NO |
| `archive-reports-dry-run` | Print what `archive-reports` would move | NO (read-only) |

No destructive `make clean` was added. The work order explicitly forbids it at this stage.

## 7. .gitignore Status

**Created/updated.** Excludes (matching WORK ORDER 011 §6):

```
.venv/, __pycache__/, *.pyc, .DS_Store,
.wiseorder_keys/, intellagent_wiseorder.egg-info/,
reports/archive/, build/, dist/, .pytest_cache/
```

Explicitly NOT ignored (must remain tracked):

```
vectors/, schemas/, canonicalization/, binary_fixtures/,
reports/ci/, reports/canonical/, reports/repo_health/,
reports/conformance-summary.txt, reports/conformance-report.json
```

## 8. Git Status

| Field | Value |
|---|---|
| Repository initialized | YES |
| Branch | `main` (post-init rename, see §9) |
| `.gitignore` present | YES |
| Identity configured | `Henry Wayne Wise III <wise.est.systems@proton.me>` |
| First commit | see §9 |

## 9. Verification Results

| Command | Exit code | Result |
|---|---|---|
| `make ci` | 0 | PASS — 9 stages green |
| `make demo` | 0 | PASS — 6 steps, 3 fingerprints MATCH |
| `python -m pytest` | 0 | PASS — 271 tests |

### CI stages (all unchanged after move)

| Stage | Result |
|---|---|
| `no-pseudocode` | PASS (scans moved docs via updated `DOCS_GLOBS`) |
| `test` | PASS — 271 tests |
| `conformance` | PASS — 33 vectors |
| `interop` | PASS — 3 fixtures |
| `canonicalization-check` | PASS — 10 corpus entries |
| `minimal-verifier-check` | PASS — 33 vectors via independent re-derivation |
| `replay-diff-check` | PASS — 9 self-check fixtures |
| `binary-fixture-check` | PASS — 4 fixtures (1 VERIFIED, 3 TAMPERED) |
| `sandbox-escape-check` | PASS — 29 attempts (25 hostile refused, 4 controls allowed) |

### Frozen fingerprint match (all three)

| Fingerprint | Match |
|---|---|
| `vectors_suite_sha256` (`sha256:6168d2…1bb0f`) | YES |
| `manifests_suite_sha256` (`sha256:74eaaa…ba29`) | YES |
| `corpus_sha256` (`sha256:c95685…3b09`) | YES |

The move preserved all three frozen v0.1.0 fingerprints byte-for-byte. The SPEC_LOCK §2.4 invariant holds.

## 10. Failures

**None.**

No target failed. No file was deleted. No semantic change was required. The one transient signal during the run was a hook false-positive on a pre-existing docstring line in `tools/check_no_pseudocode.py` (the scanner's own description of which markers it bans contains the literal word `NotImplementedError`); the file content was not modified to dodge the token because doing so would degrade the scanner's self-documentation.

## 11. Files Left Unclassified

**None.** Every top-level markdown was either kept as root-critical (per §4) or moved into a `docs/<sub>/` category. No `.md` file remains uncategorized.

## 12. Next Code Task

Begin the **first independent verifier implementation track in Rust** per [`../../docs/release/IMPLEMENTATION_TRACKER.md`](../../docs/release/IMPLEMENTATION_TRACKER.md) §2.1.

- MUST NOT import or translate `intellagent_runtime`.
- MUST be derived from `SPEC.md` + `SPEC_LOCK_v0.1.md` + `schemas/` + the vector and canonicalization corpora.
- Acceptance: reproduces all three frozen fingerprints byte-for-byte.

This task is the largest remaining gap blocking v0.1.0's external-validation claim.
