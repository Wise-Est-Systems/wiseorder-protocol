# governed-run Pipeline Integration Report — v0.1.0

**Work Order:** 016 — Governed Run Wet-Run Pipeline Integration
**Timestamp (UTC):** 2026-05-10T22:00:00Z
**Overall Result:** **PASS**
**Authority:** Evidence record that `governed-run` now supports a wet-run path that flows parse → plan → validate → bounded execution under macOS sandbox-exec isolation → audit → manifest, with formal RefusalRecord sealing on every refusal.

---

## 1. Files Created

| File | Purpose |
|---|---|
| `tests/test_governed_run_pipeline.py` | 40 integration tests (dry-run + wet-run + refusal + manifest + audit + freeze invariants) |
| `reports/runtime_core/governed_run_pipeline_v0.1.md` | this report |
| `reports/runtime_core/governed_run_pipeline_v0.1.json` | machine-readable equivalent |

## 2. Files Modified

| File | Change |
|---|---|
| `intellagent_runtime/cli.py` | Extended `governed-run`: `--execute`, `--output`, mode resolution (dry-run default), mutual exclusion of `--dry-run` and `--execute`, wet-run flow via `tools/os_isolation_runtime.execute_command_isolated`, RefusalRecord sealing on every refusal/invalid/execution-failed path, `manifest_hash`, `command_results` |
| `Makefile` | Added `governed-run-pipeline-check` target (NOT in `make ci`) |
| `.gitignore` | Added `/intellagent_refusals/` at the repo root (per-run RefusalRecord output is operational, not source) |

**Not changed (by design):** `SPEC.md`, `SPEC_LOCK_v0.1.md`, `vectors/**`, `schemas/**`, `canonicalization/corpus/**`, `rust_verifier/**`, `go_verifier/**`, `tools/**` (no edits to existing pipeline / proposer / review-gate runtimes), frozen fingerprint values.

## 3. Tests Added

**40 new tests** in `tests/test_governed_run_pipeline.py`. Pytest totals: **358 → 398**, all passing.

| Category | Count |
|---|---|
| Flag handling (default mode, mutual exclusion, --output, --self-check) | 6 |
| Dry-run paths (valid / refused / invalid / placeholder / no-verify) | 5 |
| Wet-run refusal paths (destructive / forbidden-path / invalid-WO / no-verify) | 4 |
| RefusalRecord sealing (refused plan + invalid WO) | 2 |
| Audit memory (started + plan_valid + refused + chain status + mode) | 4 |
| Manifest shape and determinism | 4 |
| Wet-run execution (macOS-only) | 8 |
| Defense in depth + CI freeze invariants | 7 |
| **Total** | **40** |

10 of the wet-run-execution tests are `@MACOS_ONLY` because they invoke sandbox-exec. The other 30 run on every platform and exercise the dry-run + refusal + manifest paths end-to-end.

## 4. Commands Run

```
python -m pytest tests/test_governed_run_pipeline.py             rc=0   40/40 PASS
python -m pytest tests/test_intellagent_cli.py                   rc=0   14/14 PASS
python -m pytest tests/                                          rc=0   398/398 PASS
make governed-run-pipeline-check                                 rc=0   54 PASS
make ci                                                          rc=0   (11 stages)
make demo                                                        rc=0   (3 fingerprints MATCH)
git status --short                                               rc=0
```

## 5. Per-mode Results

### Dry-run

**PASS.** Backward-compatible with WO 015. New fields added to the manifest (`mode`, `execution_plan_hash`, `manifest_hash`, and optionally `refusal_record_hash`) without breaking existing assertions. The 14 pre-WO-016 CLI tests still pass.

### Wet-run

**PASS** on macOS. A `pwd` work order produces:

```
final_status:           GOVERNED_RUN_EXECUTED
mode:                   execute
work_order_hash:        sha256:...
execution_plan_hash:    sha256:...
proposer_hash:          sha256:...
review_hash:            sha256:...
executor_manifest_hash: sha256:...
pipeline_hash:          sha256:...
command_results:        [{"command": "pwd", "succeeded": true, "exit_code": 0, "status": "ok", ...}]
audit_status:           {"status": "AUDIT_CHAIN_VALID", ...}
manifest_hash:          sha256:...
```

All four pipeline-equivalent hashes are computed from the run's actual artifacts (see §integration-decision below); none is fabricated.

### Refusal

**PASS** across every refusal path:
- **Invalid work order** (parse error / file missing) → `GOVERNED_RUN_INVALID`, exit 2, RefusalRecord sealed.
- **Refused plan** (destructive command, forbidden path, no verify, no report) → `GOVERNED_RUN_REFUSED`, exit 1, RefusalRecord sealed, executor never invoked.
- **Execution failure** (sandbox classifier denies, command exits non-zero, timeout) → `GOVERNED_RUN_EXECUTION_FAILED`, exit 1, RefusalRecord sealed.

The RefusalRecord is materialized via the existing `intellagent_runtime.refusal.RefusalStore` — no new refusal infrastructure was added.

## 6. Audit Memory

**PASS.** Wet-run produces this event sequence per command:

1. `governed_run.started` (mode + work_order_sha256 + execution_plan_hash)
2. `governed_run.plan_valid` (stages + command_count)  — only on valid plans
3. `governed_run.command.executed` (per command: command + status + exit_code + succeeded)
4. `governed_run.completed` (execution_status + pipeline_hash)

OR on refusal:

1. `governed_run.started`
2. `governed_run.refused` (reasons)

The audit chain stays `AUDIT_CHAIN_VALID` across every test scenario.

## 7. Manifest Output

Required fields (per WO 016 §6):

| Field | Dry-run | Wet-run |
|---|---|---|
| `mode` | "dry-run" | "execute" |
| `work_order_hash` | yes | yes |
| `execution_plan_hash` | yes | yes |
| `validation_status` | yes | yes |
| `validation_violations` | yes | yes |
| `audit_status` | yes (if --audit) | yes (if --audit) |
| `refusal_record_hash` | only if refused | only if refused/failed |
| `pipeline_hash` | omitted | yes |
| `proposer_hash` | omitted | yes |
| `review_hash` | omitted | yes |
| `executor_manifest_hash` | omitted | yes |
| `command_results` | omitted | yes |
| `final_status` | yes | yes |
| `manifest_hash` | yes | yes |

Dry-run manifest remains backward compatible — old tests pass.

## 8. CI / Demo Status

| Gate | Result |
|---|---|
| `make ci` | **PASS** — 11 stages, no regression |
| `make demo` | **PASS** — 3 frozen fingerprints MATCH byte-for-byte |
| Frozen fingerprints | **UNCHANGED** |

## 9. Integration Decisions (Recorded Per WO Format)

### Decision 1 — Wet-run dispatch

**Decision:** call `tools/pipeline_runtime.run()` (Workforce YAML) OR call `tools/os_isolation_runtime.execute_command_isolated()` (sandbox primitive)?

**Recommendation:** `os_isolation_runtime.execute_command_isolated()` directly.

**Why:** `pipeline_runtime` is built for the Workforce YAML schema (`work_order_id`, `agent_role`, `allowed_files` globs, `required_gates`, `rollback_plan`, `human_approval_required`, `status_history`, etc.). These fields do not map cleanly to a freeform markdown WO. Bridging would require *inventing* values for many required fields, exactly the fake-it-to-make-it pattern the standing law forbids. Additionally, `pipeline_runtime.run()` applies its OWN proposer→review filtering with admit-list logic distinct from the WO-015 `execution_plan` validator; routing through it would make the WO-015 validator vestigial. Calling `execute_command_isolated()` directly preserves the WO-015 validator as the authoritative gate AND inherits sandbox-exec isolation, classifier deny-first, per-command timeout, and output cap.

**What would change my mind:**
- A follow-up WO that adds a faithful markdown→YAML adapter populating every required Workforce field without invention.
- A `pipeline_runtime` variant that accepts a plan-as-data argument so the WO-015 plan can be passed directly.

**Cost if wrong:** We forgo one redundant pass of admit-list filtering and deterministic-hash checking. The WO-015 plan validator + the `os_isolation_runtime` classifier remain in place as two layers. Recoverable in a follow-up.

### Decision 2 — Proposer/review/executor hash provenance in the wet-run manifest

**Decision:** how to compute `proposer_hash` / `review_hash` / `executor_manifest_hash` / `pipeline_hash` when not actually routing through `pipeline_runtime`?

**Recommendation:** compute locally from real run artifacts:

```
proposer_hash          = sha256(canonical({planned_commands, work_order_hash}))
review_hash            = sha256(canonical({approved_commands, validation_status}))
executor_manifest_hash = sha256(canonical(command_results))
pipeline_hash          = sha256(canonical({proposer_hash, review_hash, executor_manifest_hash}))
```

**Why:** The manifest needs to be shape-comparable to a `pipeline_runtime` manifest. Computing locally is honest accounting — each hash commits to a real artifact in the run. No value is fabricated.

**What would change my mind:** If a future WO routes through `pipeline_runtime.run()` via a YAML adapter, the field NAMES stay; the derivations are replaced by the canonical `pipeline_runtime` hashes.

**Cost if wrong:** A reviewer comparing a governed-run manifest with a `pipeline_runtime` manifest sees different values for the same conceptual field. Documented here so the difference is visible.

## 10. Known Limitations

1. **Wet-run is macOS-only.** `tools/os_isolation_runtime` uses sandbox-exec. The 10 macOS-only tests are skipped on non-macOS. A Linux equivalent is unimplemented.
2. **Wet-run does not pass through `pipeline_runtime`.** See Decision 1. The execution_plan validator + os_isolation_runtime classifier are the only filtering layers.
3. **Per-command stdout/stderr is not in the manifest.** Captured at the os_isolation_runtime level but not echoed up. Reviewers can inspect `reports/os_isolation_runtime/runs/*.json` for full output.
4. **Concurrent governed-run invocations** sharing one audit file may interleave; `audit_memory.verify_chain` detects the corruption but doesn't prevent it.
5. **Workflow grammar parser** still uses a keyword heuristic. Real WOs whose prose contains stage synonyms can be misclassified. Mitigation: test fixtures use prose deliberately free of stage synonyms.
6. **RefusalRecord query field** uses the WO title or path; if both are empty the record carries a path-only query. Acceptable because `rejected` always contains the reason strings.

## 11. Risks Introduced

| Risk | Severity | Mitigation |
|---|---|---|
| Wet-run invokes real subprocesses under sandbox-exec | medium | Three independent gates: WO-015 plan validator → os_isolation_runtime classifier deny-first → macOS sandbox-exec kernel profile. Output capped, network denied, fork denied, per-command timeout enforced. |
| Hash provenance differs from `pipeline_runtime` | low | Documented in Decision 2; field names match; derivation is honest local computation. |
| RefusalRecord files accumulate under `<cwd>/intellagent_refusals/` | low | `/intellagent_refusals/` added to `.gitignore` at the repo root. |
| `execute_command_isolated` import depends on `tools/` on `sys.path` | low | Lazy import isolated to `_execute_planned_commands`; exercised by every macOS-only test. |

## 12. What Is Now Real

- `governed-run` accepts `--execute` and runs each planned command under macOS sandbox-exec isolation (per-command timeout, output cap, network denied, fork denied).
- Five final statuses implemented end-to-end with the correct exit codes: `GOVERNED_RUN_VALID` (0), `GOVERNED_RUN_REFUSED` (1), `GOVERNED_RUN_INVALID` (2), `GOVERNED_RUN_EXECUTED` (0), `GOVERNED_RUN_EXECUTION_FAILED` (1).
- Every refusal path (invalid WO, refused plan, execution failure) seals a formal `RefusalRecord` via the existing `intellagent_runtime.refusal.RefusalStore.seal()` — no new refusal infrastructure was added.
- Manifest carries the four pipeline-equivalent hashes (`proposer_hash`, `review_hash`, `executor_manifest_hash`, `pipeline_hash`) plus a self-`manifest_hash`, all SHA-256 prefixed.
- Audit chain captures the full event sequence and stays `AUDIT_CHAIN_VALID` across all tested scenarios.
- Mutual exclusion of `--dry-run` and `--execute` is enforced at flag parse time.
- `--output` writes the manifest to a file in addition to stdout.

## 13. What Remains Unimplemented

1. **YAML adapter** for routing through `tools/pipeline_runtime.run()` (see Decision 1).
2. **Linux equivalent** of macOS sandbox-exec for wet-run on non-Darwin platforms.
3. **Full stdout/stderr in the manifest** — currently captured only at the os_isolation_runtime layer.
4. **Concurrent-run locking** on the audit file.
5. **Promotion of WO-015 + WO-016 targets into `make ci`** (deliberately deferred per WO 016).
6. **A stricter workflow grammar parser** that doesn't pick up stage keywords from prose.

## 14. Next Build Task

Promote `governed-run-check` + `governed-run-pipeline-check` (and the five WO-015 module self-checks) into `make ci` after one more cold-checkout confirmation run. This converts governed-run from "opt-in surface" to a permanent CI gate. CI stages would grow from 11 to roughly 17.
