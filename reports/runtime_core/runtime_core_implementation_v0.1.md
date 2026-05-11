# Runtime Core Implementation Report — v0.1.0

**Work Order:** 015 — Implement the Missing Runtime Core
**Timestamp (UTC):** 2026-05-10T21:00:00Z
**Overall Result:** **PASS**
**Authority:** Evidence record that the highest-value missing runtime behavior has been implemented end-to-end without modifying frozen protocol surfaces.

---

## 1. Files Created

| File | Purpose |
|---|---|
| `intellagent_runtime/work_order_parser.py` | Markdown WO → typed `WorkOrder` |
| `intellagent_runtime/workflow_grammar.py` | Stage enum + ordering rules |
| `intellagent_runtime/execution_plan.py` | WO → `ExecutionPlan` + validator |
| `intellagent_runtime/audit_memory.py` | Append-only hash-chained JSONL audit |
| `tests/test_work_order_parser.py` | 22 tests |
| `tests/test_workflow_grammar.py` | 21 tests |
| `tests/test_execution_plan.py` | 20 tests |
| `tests/test_audit_memory.py` | 17 tests |
| `reports/runtime_core/runtime_core_implementation_v0.1.md` | this report |
| `reports/runtime_core/runtime_core_implementation_v0.1.json` | machine-readable |

## 2. Files Modified

| File | Change |
|---|---|
| `intellagent_runtime/cli.py` | Added `governed-run` subcommand + `cmd_governed_run` + `_governed_run_self_check` + `_governed_run_manifest` |
| `tests/test_intellagent_cli.py` | Added 7 governed-run tests |
| `Makefile` | Added 5 new targets (`work-order-parser-check`, `workflow-grammar-check`, `execution-plan-check`, `audit-memory-check`, `governed-run-check`); **NOT** added to `make ci` |

**Not changed (by design):** `SPEC.md`, `SPEC_LOCK_v0.1.md`, `vectors/**`, `schemas/**`, `canonicalization/corpus/**`, the Python/Rust/Go verifier behavior, frozen fingerprint values.

## 3. Tests Added

| Test file | Count |
|---|---|
| `test_work_order_parser.py` | 22 |
| `test_workflow_grammar.py` | 21 |
| `test_execution_plan.py` | 20 |
| `test_audit_memory.py` | 17 |
| `test_intellagent_cli.py` (additions) | 7 |
| **Total new** | **87** |

Minimum required: 50. **Exceeded by 37.**

Pytest totals: **271 → 358** tests, all passing.

## 4. Commands Run

```
python -m pytest tests/test_work_order_parser.py            rc=0   22/22 PASS
python -m pytest tests/test_workflow_grammar.py             rc=0   21/21 PASS
python -m pytest tests/test_execution_plan.py               rc=0   20/20 PASS
python -m pytest tests/test_audit_memory.py                 rc=0   17/17 PASS
python -m pytest tests/test_intellagent_cli.py              rc=0   14/14 PASS (7 new + 7 existing)
python -m pytest tests/                                     rc=0   358/358 PASS
make work-order-parser-check                                rc=0
make workflow-grammar-check                                 rc=0
make execution-plan-check                                   rc=0
make audit-memory-check                                     rc=0
make governed-run-check                                     rc=0
make ci                                                     rc=0   (11 stages, unchanged)
make demo                                                   rc=0   (3 frozen fingerprints MATCH)
git status --short                                          rc=0
```

## 5. Per-component Results

| Component | Tests | Self-check | JSON output valid? |
|---|---|---|---|
| Work-order parser | 22 / 22 | PASS | n/a |
| Workflow grammar | 21 / 21 | PASS | n/a |
| Execution plan | 20 / 20 | PASS | n/a |
| Audit memory | 17 / 17 | PASS | n/a |
| governed-run CLI | 7 / 7 | PASS | YES (all required fields present) |

## 6. What Is Now Real

- **Markdown work-order parser** that rejects: missing objective, missing stop condition, empty input, protected-and-mutable contradiction without explicit permission, placeholder-only deliverables.
- **Workflow grammar** with 8 stages (`inspect`, `propose`, `review`, `execute`, `verify`, `report`, `stop`, `refuse`) and ordering enforcement: execute-after-review, verify-after-execute (unless verifying existing artifact), report-before-stop, stop/refuse terminal.
- **Execution-plan validator** that refuses: forbidden-path touch, missing required command, unbounded shell, destructive command without permission, plan without verify step, plan without report step.
- **Append-only audit memory** with SHA-256 hash chain and four-status verification: `AUDIT_CHAIN_VALID`, `AUDIT_CHAIN_TAMPERED`, `AUDIT_CHAIN_EMPTY`, `AUDIT_CHAIN_INVALID`.
- **`governed-run` CLI subcommand**: parse WO → build plan → validate → audit-append → emit manifest JSON → final status (`GOVERNED_RUN_VALID` / `GOVERNED_RUN_REFUSED` / `GOVERNED_RUN_INVALID`).
- **5 Makefile targets**, intentionally NOT in `make ci` until cold-stable in a follow-up work order.

## 7. What Remains Unimplemented

1. **Actual shell execution.** `governed-run` is dry-run-only in v0.1.0. The validated plan is not yet wired into a real sandboxed executor. `tools/pipeline_runtime.py` already provides the proposer→review→executor flow; integrating with it is the next work order.
2. **Persistent audit aggregation across runs.** The primitives support persistence, but the CLI does not yet implement multi-run aggregation or rotation.
3. **WO-format coverage.** Workflow-stage parsing is a keyword heuristic. WOs with unusual structure may parse with incomplete stages; the validator catches the consequence (no verify / no report) and refuses the plan.
4. **RefusalRecord integration.** When a plan is refused, the CLI emits `GOVERNED_RUN_REFUSED` and logs reasons in the audit memory, but does not yet seal a `RefusalRecord` artifact via `intellagent_runtime/refusal.py`.
5. **Glob semantics for forbidden paths.** Uses literal-substring + regex matching, which is conservative. True `fnmatch` glob is a follow-up.
6. **Concurrent audit writes.** No file-locking. Concurrent appenders from separate processes may interleave; `verify_chain` detects the corruption but reordering is not prevented.

## 8. Risks Introduced

| Risk | Severity | Mitigation |
|---|---|---|
| Work-order parser is regex-based, not a formal grammar | medium | every required field rejected when absent; parser is conservative |
| Destructive-command detection is a heuristic deny-list | medium | explicit allow-list at the execution surface remains the strongest backstop; this is one layer of several |
| Single-writer audit chain | medium | `verify_chain` reliably detects corruption |
| `governed-run` without `--dry-run` still does not actually execute | low (intentional) | documented in §7; `--dry-run` is the safer mode and the only one tested |

## 9. CI / Demo Status

- **`make ci`** — **PASS** (11 stages, no regression).
- **`make demo`** — **PASS** (three frozen fingerprints MATCH byte-for-byte).
- **Frozen fingerprints unchanged.**

The 5 new targets are intentionally not in `make ci` per WO 015. Promotion is a separate work order, after cold confirmation runs.

## 10. Semantic Decisions Recorded

### Decision 1: audit-memory hash format

**Recommendation:** prefixed (`sha256:<hex>`).
**Why:** consistent with the rest of the WiseOrder repo (Class A artifacts, manifests, `vectors_suite_sha256`). Single-format across the codebase reduces audit-side confusion.
**Cost if wrong:** low; only the audit log is affected. A future migration would be a simple per-line replace.

### Decision 2: `governed-run` without `--dry-run` still does not execute

**Recommendation:** keep it as a no-op (other than audit emission) for v0.1.0.
**Why:** v0.1.0 keeps the governance kernel decoupled from execution dispatch. `tools/pipeline_runtime.py` is the existing executor surface; wiring `governed-run` into it deserves its own work order so the integration is reviewable.
**Cost if wrong:** low; `--dry-run` is the safer mode and is the only one tested.

### Decision 3: keyword-heuristic workflow parsing

**Recommendation:** keyword heuristic for v0.1.0.
**Why:** WOs are author-written prose, not machine-generated. A heuristic that recognizes ~90% of WOs is more useful than a strict grammar that recognizes 30% and rejects the rest. The validator catches the consequences of any parse failure (no-verify / no-report) and refuses the plan, so failures are safe-by-default.
**Cost if wrong:** medium; a misparsed WO becomes a refused plan rather than an unsafe execution.

## 11. Next Build Task

Integrate `governed-run` with `tools/pipeline_runtime.py` so a `GOVERNED_RUN_VALID` plan flows into the existing proposer→review→executor pipeline under macOS sandbox-exec isolation.

**Acceptance criteria:**
- A valid WO can be dry-run AND wet-run (the latter behind an explicit `--execute` flag).
- Execution stays within the planned commands.
- Audit memory captures `pipeline_hash` + `proposer_hash` + `review_hash` + `executor_manifest_hash`.
- Refusal at any pipeline stage seals a `RefusalRecord` using `intellagent_runtime/refusal.py`.

This closes the gap between "validated plan" and "bounded execution with sealed evidence on every refusal."
