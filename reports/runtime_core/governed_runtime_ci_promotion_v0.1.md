# Governed Runtime CI Promotion Report — v0.1.0

**Work Order:** 017 — Promote Governed Runtime Into CI
**Timestamp (UTC):** 2026-05-10T23:00:00Z
**Overall Result:** **PASS**
**Authority:** Evidence record that the WO-015 + WO-016 governed-runtime checks have been promoted into the permanent `make ci` gate and the repository passes cold on macOS with **17 CI stages**.

---

## 1. Cold Confirmation (12 commands)

| # | Command | Exit code | Result |
|---|---|---|---|
| 1 | `python -m pytest tests/test_work_order_parser.py` | 0 | 22 / 22 PASS |
| 2 | `python -m pytest tests/test_workflow_grammar.py` | 0 | 21 / 21 PASS |
| 3 | `python -m pytest tests/test_execution_plan.py` | 0 | 20 / 20 PASS |
| 4 | `python -m pytest tests/test_audit_memory.py` | 0 | 17 / 17 PASS |
| 5 | `python -m pytest tests/test_governed_run_pipeline.py` | 0 | 40 / 40 PASS |
| 6 | `python -m pytest tests/test_intellagent_cli.py` | 0 | 14 / 14 PASS |
| 7 | `make work-order-parser-check` | 0 | PASS |
| 8 | `make workflow-grammar-check` | 0 | PASS |
| 9 | `make execution-plan-check` | 0 | PASS |
| 10 | `make audit-memory-check` | 0 | PASS |
| 11 | `make governed-run-check` | 0 | PASS |
| 12 | `make governed-run-pipeline-check` | 0 | PASS — 54 tests |

## 2. Files Modified

| File | Change |
|---|---|
| `Makefile` | `ci` target now lists `work-order-parser-check`, `workflow-grammar-check`, `execution-plan-check`, `audit-memory-check`, `governed-run-check`, `governed-run-pipeline-check` between `test` and `conformance`; summary message updated to mention the governed-runtime core. |

**Files created:**

| File | Purpose |
|---|---|
| `reports/runtime_core/governed_runtime_ci_promotion_v0.1.md` | this report |
| `reports/runtime_core/governed_runtime_ci_promotion_v0.1.json` | machine-readable equivalent |

**Not changed (by design):** `SPEC.md`, `SPEC_LOCK_v0.1.md`, `vectors/**`, `schemas/**`, `canonicalization/corpus/**`, `intellagent_runtime/**`, `tools/**`, `rust_verifier/**`, `go_verifier/**`, `tests/**` (no new tests, no test weakened), frozen fingerprint values.

## 3. CI Stages After Promotion (17 total)

| # | Stage | Result |
|---|---|---|
| 1 | `no-pseudocode` | PASS — 69 markdown files scanned, 0 markers |
| 2 | `test` | PASS — **398 tests** |
| 3 | **`work-order-parser-check`** | **PASS — 22 unit tests + self-check** |
| 4 | **`workflow-grammar-check`** | **PASS — 21 unit tests + self-check** |
| 5 | **`execution-plan-check`** | **PASS — 20 unit tests + self-check** |
| 6 | **`audit-memory-check`** | **PASS — 17 unit tests + self-check** |
| 7 | **`governed-run-check`** | **PASS — governed-run --self-check** |
| 8 | **`governed-run-pipeline-check`** | **PASS — 54 tests (40 pipeline + 14 CLI)** |
| 9 | `conformance` | PASS — 33 vectors |
| 10 | `interop` | PASS — 3 fixtures |
| 11 | `canonicalization-check` | PASS — 10 corpus entries |
| 12 | `minimal-verifier-check` | PASS — 33 vectors via Python independent re-derivation |
| 13 | `replay-diff-check` | PASS — 9 self-check fixtures |
| 14 | `binary-fixture-check` | PASS — 4 fixtures |
| 15 | `sandbox-escape-check` | PASS — 29 attempts (25 hostile refused, 4 controls allowed) |
| 16 | `rust-verifier-check` | PASS — cargo test (26), verify-vectors (33/33), verify-corpus (10/10) |
| 17 | `go-verifier-check` | PASS — go test (38), verify-vectors (33/33), verify-corpus (10/10) |

The governance gates run **before** the protocol/canonicalization layers — a meaningful semantic statement: a contributor breaking the governance kernel is caught before any vector-related noise can mask it.

## 4. `make ci` Result

**PASS** (`rc=0`). 17 stages. Final summary line:

> CI: documentation code standard + tooling tests + governed-runtime core (parser + grammar + plan + audit + governed-run self-check + pipeline-integration tests) + protocol conformance + interoperability + canonicalization golden + minimal-verifier + replay-diff + binary-fixture + sandbox-escape + rust-verifier + go-verifier (first-party independent tracks; cargo test and go test each cover all 3 frozen fingerprints) all passed.

## 5. `make demo` Result

**PASS** (`rc=0`). All three frozen fingerprints reproduced byte-for-byte:

| Fingerprint | Match |
|---|---|
| `vectors_suite_sha256` (`sha256:6168d2…1bb0f`) | YES |
| `manifests_suite_sha256` (`sha256:74eaaa…ba29`) | YES |
| `corpus_sha256` (`sha256:c95685…3b09`) | YES |

## 6. Test Counts

| Field | Value |
|---|---|
| Total pytest tests | **398** |
| All passing | yes |
| Tests added in this work order | 0 (CI promotion only — no new behavior, no weakened tests) |

## 7. Platform Behavior

| Field | Value |
|---|---|
| Host OS | macOS (darwin) |
| sandbox-exec available | YES |
| macOS-only tests inside CI | 10 (all run) |
| Linux wet-run supported | **NO** (explicitly not claimed) |
| Behavior on a Linux-hosted CI run | The 10 macOS-only tests are skipped with the explicit pytest reason `"sandbox-exec is macOS only"`. The other 30 platform-agnostic pipeline tests still run. `make ci` would still PASS because pytest treats skipped tests as passing — this is documented and intentional, not a silent gap. |

## 8. Frozen Fingerprint Status

**Unchanged.** All three v0.1.0 lock anchors continue to be reproduced byte-for-byte across all four verifier tracks (Python reference, Python minimal, Rust, Go) — now running inside the same CI gate that also exercises the governed-runtime core.

## 9. Third-Party Validation Status

**`false`** — unchanged. All seventeen CI stages remain owned by Wise.Est Systems. The cross-language implementability question is closed across four languages plus the full governed-runtime kernel; the ownership / accountability question that defines third-party validation per `docs/release/THIRD_PARTY_VERIFIER_BRIEF_v0.1.md` is unchanged.

## 10. What Is Now Mandatory in CI

A `make ci` run from a clean macOS checkout MUST now also pass:

- **Work-order parsing rules** — rejection of malformed / missing-objective / missing-stop / placeholder-only / protected-and-mutable-without-permission work orders.
- **Workflow grammar rules** — execute-after-review, verify-after-execute (unless verifying existing artifact), report-before-stop, stop/refuse terminal.
- **Execution-plan validation** — forbidden-path touch, missing-required-command, unbounded-shell, destructive-without-permission, no-verify, no-report.
- **Audit memory integrity** — JSONL hash chain with four statuses (`AUDIT_CHAIN_VALID` / `TAMPERED` / `EMPTY` / `INVALID`); tamper detection on both payload edits and prev_hash edits.
- **governed-run self-check** — synthetic valid + refused work orders flow through the full kernel end-to-end.
- **governed-run wet-run pipeline integration** — every refusal path seals a `RefusalRecord`; every successful execute path captures the four pipeline-equivalent hashes; the audit chain stays `AUDIT_CHAIN_VALID` throughout.

A contributor cannot land a change that silently breaks any of those properties.

## 11. Known Limitations

1. **Wet-run is macOS-only.** No Linux equivalent of `tools/os_isolation_runtime`'s sandbox-exec wrapper is implemented in v0.1.
2. **Wet-run does not route through `tools/pipeline_runtime.run()`.** It calls `os_isolation_runtime.execute_command_isolated` directly — see `reports/runtime_core/governed_run_pipeline_v0.1.md §9 Decision 1` for the rationale.
3. **Workflow grammar parser uses a keyword heuristic.** WOs with stage synonyms in prose (outside the workflow list) can be misclassified.
4. **CI on a Linux host** would skip the 10 macOS-only tests with explicit reason; `make ci` would still PASS via pytest skip semantics. Documented, not silent.

## 12. Remaining Risks

| Risk | Severity | Mitigation |
|---|---|---|
| Every `make ci` run on macOS now spawns real subprocesses under sandbox-exec | medium | Three-layer gate: WO-015 plan validator → os_isolation_runtime classifier deny-first → macOS sandbox-exec kernel profile; output cap, network deny, fork deny, per-command timeout enforced. |
| RefusalRecord files accumulate under `<cwd>/intellagent_refusals/` during wet-run tests | low | Test harness uses pytest tmp_path so test artifacts are isolated; `/intellagent_refusals/` at the repo root is `.gitignore`d. |
| Sandbox profile files (`reports/os_isolation_runtime/profiles/*.sb`) grow over time as CI runs produce new profile hashes | low | Consistent with canonical-vs-archived policy in `reports/canonical/README.md`; periodic archive sweep is the standing mitigation. |

## 13. Exact Next Build Task

Prepare and publish the external verifier recruitment packet to a non-first-party audience.

The packet is already drafted in:
- `docs/release/EXTERNAL_REVIEW_PACKET_v0.1.md`
- `docs/release/REVIEW_QUICKSTART.md`
- `docs/release/THIRD_PARTY_VERIFIER_BRIEF_v0.1.md`

The in-repo CI gate is now 17 stages strong across Python reference + Python minimal + Rust + Go verifier tracks AND the full governed-runtime kernel. The remaining external-validation gap is **ownership, not coverage**. The next move belongs to an external party.
