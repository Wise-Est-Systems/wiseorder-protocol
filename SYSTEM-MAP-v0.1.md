# SYSTEM MAP — WiseOrder Protocol / Intellagent Runtime v0.1.0

**Work Order:** 020 — Full System Map
**Document version:** v0.1
**Timestamp (UTC):** 2026-05-11T18:30:00Z
**Status:** Factual system map. No hype. No overclaims. Every claim is backed by a path, command, test count, or fingerprint.

---

## 1. One-Sentence Definition

WiseOrder Protocol is a draft specification for governing how AI-produced cognition becomes consequence, accompanied by an Intellagent reference runtime that parses bounded work orders, validates execution plans, runs admitted commands inside a kernel-backed macOS sandbox, hash-chains an audit log, seals refusals as first-class artifacts, and is independently re-verified against frozen conformance vectors by three cross-language verifier binaries (Python, Rust, Go).

## 2. Plain-English Definition

WiseOrder says: an AI is not allowed to *act* on what it concludes until the action has been written down, classified, planned, reviewed, and the reasons for any refusal have been recorded in a way that anyone else can replay byte-for-byte. Intellagent is the working program that implements this rulebook. You hand it a written instruction ("work order"); it parses the instruction into a plan; it checks the plan against rules; if approved, it runs only the planned commands inside a Mac sandbox; if it cannot run them, it writes down *why* in a sealed file; and three separate verifier programs — one in Python, one in Rust, one in Go — re-check the rulebook's frozen test cases and have to agree on the same byte-identical answers.

It is not artificial general intelligence. It is not a chatbot. It is not a production security boundary. It is not yet validated by anyone outside this project.

## 3. Technical Definition

WiseOrder is an epistemic governance protocol. It defines:

- four claim **classes** (A: cryptographic, B: empirical, C: consensus, D: conduct) and a verdict per class,
- a **canonicalization scheme** (JCS-style) producing byte-deterministic JSON bytes for hashing,
- **conformance vectors** (33 frozen inputs with expected verdicts) whose suite sha256 anchors v0.1.0,
- a **canonicalization corpus** (10 frozen inputs with expected digests) whose suite sha256 anchors canonicalization parity across languages,
- **interop fixture manifests** (3 frozen fixtures: Winstack class A, Winstack class B, WISEATA class B) whose manifests suite sha256 anchors implementation parity.

Intellagent is the v0.1 reference runtime kernel:

- a Python work-order parser → workflow grammar → execution-plan validator pipeline,
- a `governed-run` CLI verb that admits a work order, plans commands, optionally executes them in a sandboxed temp directory, emits a manifest, and seals a `RefusalRecord` on refusal,
- a hash-chained audit memory (`prev_hash` → `hash` over canonical event bytes),
- a `.win` chain layer (v0.2.0) sealing a genesis block under the III digest and appending tamper-detectable records.

Three independent verifier binaries — Python `minimal_verifier`, Rust `rust_verifier`, Go `go_verifier` — each re-derive the 33 class verdicts and 10 corpus digests without importing each other, and produce identical frozen fingerprint values.

## 4. Layer Map

| Layer | Authoritative artifact(s) | Implemented |
|---|---|---|
| Protocol / spec | `SPEC.md`, `SPEC_LOCK_v0.1.md`, `SPEC_LOCK_v0.2.0.md`, `docs/specs/`, `docs/laws/` | yes |
| Runtime / kernel | `intellagent_runtime/kernel.py` (321 LOC), `intellagent_runtime/runtime.py` (203 LOC), `intellagent_runtime/transitions.py` (111 LOC) | yes |
| Work-order parser | `intellagent_runtime/work_order_parser.py` (525 LOC) | yes |
| Workflow grammar | `intellagent_runtime/workflow_grammar.py` (343 LOC) | yes |
| Execution-plan validator | `intellagent_runtime/execution_plan.py` (417 LOC) | yes |
| Governed-run CLI | `intellagent_runtime/cli.py` (859 LOC) — verbs: `init`, `state`, `propose`, `transition`, `audit`, `refuse`, `governed-run` | yes |
| Audit memory | `intellagent_runtime/audit_memory.py` (382 LOC) — hash-chained `prev_hash`→`hash` events, statuses `AUDIT_CHAIN_VALID` / `AUDIT_CHAIN_TAMPERED` | yes |
| RefusalRecord | `intellagent_runtime/refusal.py` (98 LOC) — sealed JSON artifact when transition search cannot satisfy query | yes |
| Chain (v0.2.0) | `intellagent_runtime/chain.py` (355 LOC), `intellagent_runtime/iii.py` (240 LOC), `chain/genesis.win`, `chain/2026-05-11T063325_563754Z-75e813e9.win` | yes |
| Sandbox / isolation | `tools/os_isolation_runtime.py` (753 LOC, macOS `sandbox-exec`), `tools/resource_limit_runtime.py` (1177 LOC), `tools/real_agent_runtime.py` (3055 LOC — probes Linux `bwrap`) | partial (macOS wet, Linux probe only) |
| Verifier — Python reference | `tools/run_conformance.py` (196 LOC) + runtime imports | yes |
| Verifier — Python minimal | `tools/minimal_verifier.py` (562 LOC) — independent of `intellagent_runtime` | yes |
| Verifier — Rust | `rust_verifier/` (1616 LOC across `src/{main,vectors,jcs,fingerprints}.rs` + `tests/integration.rs`) | yes |
| Verifier — Go | `go_verifier/` (1952 LOC across `main.go`, `internal/{vectors,jcs,fingerprints}/`, `tests/`) | yes |
| Vector / conformance | `vectors/` (33 JSON files), `schemas/vector.schema.json`, `tools/validate_vectors.py`, `tools/run_conformance.py` | yes |
| Canonicalization | `canonicalization/corpus/` (10 JSON files), `canonicalization/golden/golden-digests.json`, `canonicalization/tools/verify_golden.py`, `intellagent_runtime/canonical.py` | yes |
| Interop | `interop/fixtures/{winstack,wiseata}/`, `interop/scripts/{generate_fixture_manifest,run_interop_checks}.py`, `interop/reports/` | yes |
| CI | `Makefile` (`ci` target: 18 stages), `reports/conformance-*`, `interop/reports/interop-*`, `.venv/` deps | yes |
| Docs / release | `docs/{specs,laws,runtime,whitepapers,release,strategy,audits}/`, `CONFORMANCE.md`, `IMPLEMENTATIONS.md`, `ARTIFACTS.md`, `STATUS-REGISTRY.md`, `TOOLS.md`, `site/index.html` | yes |
| Unimplemented / future | YAML pipeline adapter, Linux wet execution, concurrent audit locking, full stdout/stderr lift-up, external verifier, market layer | no |

## 5. End-to-End Flow

```
work order (Markdown/JSON)
    │
    ▼
intellagent_runtime/work_order_parser.py
    │   parses → structured WorkOrder dataclass
    ▼
intellagent_runtime/workflow_grammar.py
    │   validates grammar (verbs, scopes, sequencing)
    ▼
intellagent_runtime/execution_plan.py
    │   compiles → ExecutionPlan (bounded command list)
    ▼
review (deterministic admission)
    │   tools/review_gate_runtime.py (NOT in CI)
    │   or governed-run --self-check (in CI)
    ▼
intellagent_runtime/cli.py — governed-run
    │   --self-check          → built-in fixtures
    │   --dry-run             → plan-only, emits manifest, no sandbox call
    │   --execute (macOS)     → tempfile.TemporaryDirectory("governed-run-")
    │                           sandbox-exec confinement
    │                           per-command timeout
    ▼
intellagent_runtime/audit_memory.py
    │   appends hash-chained event(s)
    │   prev_hash → hash over canonical bytes
    ▼
intellagent_runtime/refusal.py
    │   if transition search yielded no satisfying path
    │   → seals RefusalRecord JSON artifact
    ▼
manifest (governed-run output)
    │   includes: work-order digest, plan, exit codes, audit chain head
    ▼
verification
    │   minimal_verifier.py / rust_verifier / go_verifier each re-derive
    │   the 33 vector verdicts + 10 corpus digests independently
    ▼
CI (make ci)
    │   18 stages, exit 0 required, regenerates frozen fingerprints
    │   compares: vectors_suite_sha256, manifests_suite_sha256, corpus_sha256
```

## 6. Real Code Inventory

| Path | Purpose | Code | Tests | Make target | In CI | Status |
|---|---|---|---|---|---|---|
| `intellagent_runtime/work_order_parser.py` | Parse work-order text → WorkOrder | 525 LOC | `tests/test_work_order_parser.py` (22) | `work-order-parser-check` | yes | green |
| `intellagent_runtime/workflow_grammar.py` | Validate workflow grammar | 343 LOC | `tests/test_workflow_grammar.py` (21) | `workflow-grammar-check` | yes | green |
| `intellagent_runtime/execution_plan.py` | Compile/validate execution plan | 417 LOC | `tests/test_execution_plan.py` (20) | `execution-plan-check` | yes | green |
| `intellagent_runtime/audit_memory.py` | Hash-chained audit log | 382 LOC | `tests/test_audit_memory.py` (17) | `audit-memory-check` | yes | green |
| `intellagent_runtime/cli.py` | `intellagent` CLI w/ `governed-run` | 859 LOC | `tests/test_intellagent_cli.py` (14), `tests/test_governed_run_pipeline.py` (40) | `governed-run-check`, `governed-run-pipeline-check` | yes | green |
| `intellagent_runtime/refusal.py` | Seal RefusalRecord | 98 LOC | exercised via `tests/test_governed_run_pipeline.py` | (via CLI) | yes | green |
| `intellagent_runtime/chain.py` | v0.2.0 `.win` chain | 355 LOC | `tests/test_chain.py` (23) | `chain-check` | yes | green |
| `intellagent_runtime/iii.py` | III digest | 240 LOC | `tests/test_iii.py` (16) | `chain-check` (bundled) | yes | green |
| `intellagent_runtime/kernel.py` | Class A/B/C/D kernel | 321 LOC | `tests/test_intellagent_kernel.py` (19) | (covered by `test`) | yes | green |
| `intellagent_runtime/runtime.py` | Runtime glue | 203 LOC | `tests/test_intellagent_runtime.py` (7) | (covered by `test`) | yes | green |
| `intellagent_runtime/authorization.py` | Authorization gate | 177 LOC | `tests/test_intellagent_authorization.py` (6) | (covered by `test`) | yes | green |
| `intellagent_runtime/proposer_transformer.py` | Transformer proposer | 773 LOC | `tests/test_intellagent_proposer_transformer.py` (21) | (covered by `test`) | yes | green |
| `intellagent_runtime/memory.py` | In-memory state | 166 LOC | `tests/test_intellagent_memory.py` (6) | (covered by `test`) | yes | green |
| `intellagent_runtime/state.py` | Runtime state | 165 LOC | `tests/test_intellagent_state.py` (9) | (covered by `test`) | yes | green |
| `intellagent_runtime/transitions.py` | EpistemicTransition | 111 LOC | (covered by `test`) | (covered by `test`) | yes | green |
| `intellagent_runtime/canonical.py` | JCS canonical bytes / sha256 | 124 LOC | (covered by `test`) | (covered by `test`) | yes | green |
| `intellagent_runtime/proposer.py` | Base proposer | 111 LOC | (covered by `test`) | (covered by `test`) | yes | green |
| `tools/minimal_verifier.py` | Independent Python verifier | 562 LOC | `tests/test_minimal_verifier.py` (34) | `minimal-verifier-check` | yes | green |
| `tools/replay_diff.py` | Replay diff engine | 270 LOC | `tests/test_replay_diff.py` (26) | `replay-diff-check` | yes | green |
| `tools/binary_fixture_check.py` | Binary fixture digest check | 195 LOC | `tests/test_binary_fixture_check.py` (17) | `binary-fixture-check` | yes | green |
| `tools/sandbox_escape_check.py` | Policy guard refusal check (6 hostile categories) | 401 LOC | `tests/test_sandbox_escape_check.py` (59) | `sandbox-escape-check` | yes | green |
| `tools/run_conformance.py` | Run all 33 vectors through runtime | 196 LOC | `tests/test_run_conformance.py` (4) | `conformance` | yes | green |
| `tools/validate_vectors.py` | Validate vectors against schema | 246 LOC | `tests/test_validate_vectors.py` (6) | `validate-vectors` (not in ci) | partial | green |
| `tools/validate_implementations.py` | Validate IMPLEMENTATIONS.md | 405 LOC | `tests/test_validate_implementations.py` (13) | `validate-implementations` (not in ci) | partial | green |
| `tools/os_isolation_runtime.py` | macOS `sandbox-exec` runner | 753 LOC | exercised via `os-isolation-check` | `os-isolation-check` | **no** | green (not in ci) |
| `tools/resource_limit_runtime.py` | Bounded resource enforcement | 1177 LOC | exercised via `resource-limit-check` | `resource-limit-check` | **no** | green (not in ci) |
| `tools/pipeline_runtime.py` | proposer → review → executor pipeline | 936 LOC | exercised via `pipeline-check` | `pipeline-check` | **no** | green (not in ci) |
| `tools/proposer_runtime.py` | Bounded candidate generation | 801 LOC | exercised via `proposer-check` | `proposer-check` | **no** | green (not in ci) |
| `tools/review_gate_runtime.py` | Deterministic admission | 823 LOC | exercised via `review-gate-check` | `review-gate-check` | **no** | green (not in ci) |
| `tools/real_agent_runtime.py` | v0.2 sandboxed execute | 3055 LOC | exercised via `real-agent-check`, `real-agent-execute-check` | `real-agent-*` | **no** | green (not in ci) |
| `tools/signature_runtime.py` | HMAC signature runtime | 1271 LOC | (not in ci) | (no Makefile target) | **no** | unverified-in-ci |
| `tools/workforce_sandbox_stress.py` | Stress harness | 2167 LOC | exercised via `workforce-stress` | `workforce-stress` | **no** | green (not in ci) |
| `tools/check_workforce.py` | Workforce check | 1058 LOC | exercised via `workforce-check` | `workforce-check` | **no** | green (not in ci) |
| `tools/check_no_pseudocode.py` | Documentation pseudocode guard | 196 LOC | (none) | `no-pseudocode` | yes | green |
| `tools/demo_runner.py` | E2E demo orchestrator | 165 LOC | (none) | `demo` | **no** (separate target) | green |
| `rust_verifier/` | Independent Rust verifier | 1616 LOC Rust | `cargo test` (14 + 13 = 27) | `rust-verifier-check` | yes | green (3 dead-code warnings) |
| `go_verifier/` | Independent Go verifier | 1952 LOC Go | `go test ./go_verifier/...` (4 packages) | `go-verifier-check` | yes | green |
| `vectors/` | 33 frozen conformance vectors | 33 JSON | exercised by every verifier | (via `conformance`) | yes | frozen |
| `schemas/` | JSON schemas for vector/fixture/manifest/impl | 4 schemas | exercised by validators | (via `validate-*`) | partial | frozen |
| `canonicalization/` | Corpus + golden digests | 10 JSON + manifest | `tests/test_canonicalization_golden.py` (22) | `canonicalization-check`, `canonicalization-golden` | yes | frozen |
| `interop/` | Fixture manifests + interop checks | 3 fixtures | `tests/test_interop.py` (15) | `interop` | yes | green |
| `tests/` | 23 test files | 437 tests total | — | `test` | yes | 437 passed |

## 7. Verification Tracks

| Track | Language | Verifies | Imports runtime? | In CI | First/third party | Limitations |
|---|---|---|---|---|---|---|
| Python reference | Python 3.12+ | All 33 vectors via full runtime | yes (`intellagent_runtime.*`) | yes (`conformance`) | first | Uses production code — not a true second source. |
| Python minimal | Python 3.12+ | 33 vector verdicts + class A/B/C/D logic | no (re-derives from spec) | yes (`minimal-verifier-check`) | first | Same author/repo as runtime; same language. |
| Rust | Rust 1.x | 33 vector verdicts + 10 corpus digests + 3 fingerprints | no (Rust binary, no Python deps) | yes (`rust-verifier-check`) | first | Same author/repo; second language. |
| Go | Go 1.x | 33 vector verdicts + 10 corpus digests + 3 fingerprints | no (Go binary, no Python or Rust deps) | yes (`go-verifier-check`) | first | Same author/repo; third language. |

Cross-language status: Python reference, Python minimal, Rust, and Go all derive the same 33 vector verdicts and the same `corpus_sha256`. No third party has independently produced or audited any of these binaries.

## 8. Current CI Truth

| Metric | Value | Evidence |
|---|---|---|
| `make ci` stages | 18 | `Makefile` `ci:` rule |
| pytest tests collected | 437 | `.venv/bin/python -m pytest tests/ --collect-only` |
| pytest result | 437 passed | `.venv/bin/python -m pytest tests/` |
| Rust `cargo test` result | 27 passed (14 unit + 13 integration) | `cargo test --manifest-path rust_verifier/Cargo.toml` |
| Go `go test ./go_verifier/...` result | 4 packages ok, 0 failed | `go test ./go_verifier/...` |
| Vector count | 33 | `ls vectors/*.json \| wc -l` |
| Corpus count | 10 | `ls canonicalization/corpus/*.json \| wc -l` |
| `make ci` overall | PASS, exit 0, ~8.7s wall | this run |
| `make demo` overall | OVERALL PASS, fingerprints MATCH | this run |
| `vectors_suite_sha256` | `sha256:6168d2075931baa98bba763f9cd537142554aae7b26f19e3e93a60de2ee5bb0f` | `reports/conformance-report.json` |
| `manifests_suite_sha256` | `sha256:74eaaa62271f23172232bda43ba3340543e66c46ba1e2f5e6da18d3447a6ba29` | `interop/reports/interop-report.json` |
| `corpus_sha256` | `sha256:c95685bff48c15abc313c462908b05ac309250bc660c2d802ae51af5a8038b09` | `canonicalization/golden/golden-digests.json` |
| `.win` chain files | 2 (genesis + 1 sealed) | `chain/` |

## 9. What Is Actually Proven

Each item below is backed by a passing command/test on commit `b1bb16f` of branch `main` at 2026-05-11.

1. The 33 frozen conformance vectors produce the expected verdicts under four independent code paths (Python reference, Python minimal, Rust, Go). Evidence: `make ci` stages `conformance`, `minimal-verifier-check`, `rust-verifier-check`, `go-verifier-check`.
2. The 10 canonicalization corpus entries produce byte-identical digests under JCS canonicalization in Python, Rust, and Go. Evidence: `canonicalization-check`, `rust-verifier-check verify-corpus`, `go-verifier-check verify-corpus`.
3. The three frozen fingerprints (`vectors_suite_sha256`, `manifests_suite_sha256`, `corpus_sha256`) regenerate identically to their committed values. Evidence: `make demo` OVERALL PASS with MATCH lines.
4. 437 Python tests pass in 3.3s on this commit. Evidence: `.venv/bin/python -m pytest tests/`.
5. 27 Rust tests + 4 Go test packages pass. Evidence: `cargo test`, `go test`.
6. `make verify-drift` reports "OK: regenerated artifacts match committed state." Evidence: WO 019 evidence record.
7. The work-order parser, workflow grammar, execution-plan validator, audit memory, governed-run CLI self-check, and governed-run pipeline integration tests pass individually as Makefile targets. Evidence: stages 3–8 of `make ci`.
8. The v0.2.0 chain layer (III digest + `.win` seal/append/verify + tamper-detection) passes its self-check and pytest suite. Evidence: stage 9 of `make ci` (`chain-check`).
9. The audit memory verifies `AUDIT_CHAIN_VALID` and detects tampering, returning `AUDIT_CHAIN_TAMPERED` on mutated event hashes. Evidence: `tests/test_audit_memory.py` (17 passing).
10. The sandbox-escape policy guard refuses 6 categories of hostile inputs *without executing them*. Evidence: `sandbox-escape-check` (59 passing tests).
11. The `no-pseudocode` documentation guard scans 70 markdown files and reports zero pseudocode markers in Python code blocks. Evidence: stage 1 of `make ci`.
12. The macOS sandbox-exec runner (`os_isolation_runtime.py`) materializes a deterministic profile and runs `/bin/pwd` under confinement. Evidence: `os-isolation-fixture` (not in CI, manually invokable).

## 10. What Is Not Proven

Each item below either has no commanded evidence or has been explicitly disclaimed in `SPEC.md` / `IMPLEMENTATIONS.md`.

1. **No third-party validation.** All four verifier tracks are first-party (same repo, same author). No external auditor has reproduced any fingerprint.
2. **Not production security.** The macOS sandbox-exec API is described by Apple as deprecated; `tools/real_agent_runtime.py:1883` documents it as "best-effort containment until a hardened replacement … is integrated." Sandbox escape testing is policy-guard refusal only, not adversarial wet-run.
3. **Not an operating system.** No kernel, no process scheduler, no driver model. WiseOrder *runs on* an OS; it does not replace one.
4. **Not an industry standard.** No standards body has reviewed or adopted SPEC.md. The vector/corpus suite is self-issued.
5. **Spec corpus is incomplete.** 33 vectors across 4 classes is enough to anchor v0.1.0 conformance but does not exhaust adversarial cases. The `class-any-telemetry-status-rejected` and `class-c-*` series are narrow.
6. **Not a market or currency.** No economic layer. The .win chain artifacts are local, not networked, not exchanged.
7. **Linux wet-run is not in CI.** `tools/real_agent_runtime.py` *probes* for `bwrap` (line 1895+), but no Linux execution path is exercised by any CI stage. Only the probe code exists; the integration is unverified on Linux.
8. **No concurrent audit locking.** Single-process append. Multi-writer behavior is undefined.
9. **No full stdout/stderr lift-up.** `governed-run` records exit code and a manifest entry per command but does not capture or re-canonicalize full stdout/stderr streams into the manifest at the same fidelity as the work-order plan.
10. **No YAML pipeline adapter.** Pipelines are Python-driven only.
11. **Six runtimes are not in `make ci`.** `pipeline_runtime`, `proposer_runtime`, `review_gate_runtime`, `real_agent_runtime`, `os_isolation_runtime`, `resource_limit_runtime` have self-check Makefile targets but are explicitly excluded from the CI gate pending cold-stability runs.
12. **`signature_runtime.py` has no Makefile target.** 1271 LOC of code present; no CI hook.

## 11. Implemented vs Planned Matrix

| Capability | Implemented | Tested | In CI | External | Status | Evidence path |
|---|---|---|---|---|---|---|
| Protocol conformance (33 vectors) | yes | yes | yes | no | green | `reports/conformance-report.json` |
| Canonicalization (10 corpus) | yes | yes | yes | no | green | `canonicalization/golden/golden-digests.json` |
| Python reference verifier | yes | yes | yes | no | green | `make ci` stage `conformance` |
| Python minimal verifier | yes | yes | yes | no | green | `make ci` stage `minimal-verifier-check` |
| Rust verifier | yes | yes (27) | yes | no | green | `rust_verifier/`, `make ci` stage `rust-verifier-check` |
| Go verifier | yes | yes | yes | no | green | `go_verifier/`, `make ci` stage `go-verifier-check` |
| Work-order parsing | yes | yes (22) | yes | no | green | `intellagent_runtime/work_order_parser.py` |
| Workflow grammar | yes | yes (21) | yes | no | green | `intellagent_runtime/workflow_grammar.py` |
| Execution planning | yes | yes (20) | yes | no | green | `intellagent_runtime/execution_plan.py` |
| governed-run dry-run | yes | yes (40) | yes | no | green | `intellagent_runtime/cli.py:_governed_run_*` |
| governed-run wet-run (macOS) | yes | yes | yes (self-check + pipeline tests) | no | green | `intellagent_runtime/cli.py:_execute_planned_commands` |
| governed-run wet-run (Linux) | probe only | no | no | no | UNVERIFIED | `tools/real_agent_runtime.py:1895` |
| Audit memory (hash-chained) | yes | yes (17) | yes | no | green | `intellagent_runtime/audit_memory.py` |
| Refusal sealing | yes | yes (via pipeline tests) | yes | no | green | `intellagent_runtime/refusal.py` |
| Sandbox execution (macOS sandbox-exec) | yes | yes (manual) | no | no | partial | `tools/os_isolation_runtime.py` |
| Replay diff | yes | yes (26) | yes | no | green | `tools/replay_diff.py` |
| Binary fixtures (sha256 expected_digest) | yes | yes (17) | yes | no | green | `binary_fixtures/`, `tools/binary_fixture_check.py` |
| External (third-party) verifier | no | n/a | n/a | n/a | NOT IMPLEMENTED | — |
| Linux sandbox (wet) | no | n/a | n/a | n/a | NOT IMPLEMENTED | — |
| Concurrent audit locking | no | n/a | n/a | n/a | NOT IMPLEMENTED | — |
| Full stdout/stderr manifest lift-up | no | n/a | n/a | n/a | NOT IMPLEMENTED | — |
| YAML pipeline adapter | no | n/a | n/a | n/a | NOT IMPLEMENTED | — |
| Third-party validation | no | n/a | n/a | n/a | NOT IMPLEMENTED | — |
| v0.2.0 `.win` chain layer | yes | yes (23 + 16 III tests) | yes | no | green | `intellagent_runtime/chain.py`, `chain/`, `make ci` stage `chain-check` |

## 12. What Makes This Different (Technically)

Not marketing. Each point reflects a concrete code artifact.

- **AI action is governed *before* execution.** `intellagent_runtime/cli.py:cmd_governed_run` requires a parsed work order and an admitted execution plan before any subprocess invocation. Bypass requires editing the runtime — not a flag flip.
- **Execution plans are bounded.** `intellagent_runtime/execution_plan.py` enumerates allowed commands; the executor at `cli.py:_execute_planned_commands` only iterates that list. There is no open shell.
- **Refusal is a first-class output.** `intellagent_runtime/refusal.py:RefusalRecord` is a sealed JSON artifact written when transition search terminates without satisfying the query. Refusal carries provenance (work-order digest, search trace, sha256 hash, ISO timestamp) — not an exception/null.
- **Audit memory is hash-chained.** `intellagent_runtime/audit_memory.py` defines `prev_hash → hash` over canonical event bytes; `verify_chain()` returns `AUDIT_CHAIN_VALID` or `AUDIT_CHAIN_TAMPERED`. Tamper detection is enforced, not advisory.
- **Conformance is vector- and fingerprint-based.** v0.1.0 is anchored to three sha256 values (vectors, manifests, corpus). Any code change that perturbs canonicalization, vector evaluation, or interop manifests fails `make demo` immediately because at least one fingerprint stops matching.
- **Cross-language verifiers reproduce the same anchors.** Rust and Go binaries with zero Python dependency derive the same 33 verdicts and the same 10 corpus digests, anchored to the same fingerprints. This is the strongest current defense against "the runtime is right by definition because it's the only implementation."

## 13. Best Current Name

**Governed execution runtime kernel** for AI-produced commands, with cross-language conformance vectors.

What it is:

- a reference implementation of a draft protocol (`SPEC.md` v0.1.0 + `SPEC_LOCK_v0.2.0.md`),
- a Python runtime with hash-chained audit, sealed refusals, and macOS-sandboxed execution,
- three independent verifier binaries (Python minimal, Rust, Go) that re-derive frozen fingerprints,
- an interop fixture set covering Winstack and WISEATA implementations of the same vectors.

What it is **not**:

- not an operating system,
- not artificial general intelligence,
- not production-hardened security,
- not externally validated,
- not a standard,
- not a market or currency,
- not a Linux wet-execution platform (probe-only).

"Intellagent runtime kernel" is acceptable for the runtime; "WiseOrder Protocol" for the spec. "OS-adjacent governance runtime" overclaims — there is no OS-level integration, only macOS sandbox-exec subprocess confinement.

## 14. Remaining Build Roadmap (Next 10 Code-First Tasks)

1. **Untrack 225 stale sandbox-profile files** — `git rm --cached reports/os_isolation_runtime/profiles/*.sb`; confirm `make ci && make verify-drift` clean; commit. (WO019-RES-1)
2. **Make `python3 → .venv` discovery automatic in Makefile** — fallback to `.venv/bin/python` when present, or document the invocation in `README.md`. (WO019-RES-2)
3. **Remove Rust verifier dead-code warnings** — delete or `#[allow(dead_code)]` `canonical_sha256_hex`, `sha256_prefixed`, `Vector.{file, protocol_version}` if intentional. (WO019-RES-3)
4. **Promote `pipeline-check` into `make ci`** — currently NOT in CI; once cold-stable, gate it. (`Makefile:pipeline-check`)
5. **Promote `os-isolation-check` into `make ci`** — bring kernel-backed containment under the green gate.
6. **Promote `resource-limit-check` into `make ci`** — bring bounded-resource enforcement under the green gate.
7. **Capture full stdout/stderr in governed-run manifest** — extend `cli.py:_execute_planned_commands` to record stream digests, not just exit codes.
8. **Implement Linux wet execution path** — `tools/real_agent_runtime.py:1895` already probes for `bwrap`; wire an `os_isolation_runtime`-equivalent that runs under bwrap and add a CI matrix.
9. **Add a Makefile target for `signature_runtime.py`** — 1271 LOC currently has no CI hook; either gate it or remove it.
10. **Seek one external party to run `rust-verifier-check` and `go-verifier-check` on a fresh clone** — fingerprints will match or won't. This is the cheapest path to a first non-self validation.

## 15. Final Truth Statement

WiseOrder Protocol v0.1.0 and the Intellagent Runtime are a working first-party governance kernel for AI-produced commands on macOS, with a draft protocol specification, 33 frozen conformance vectors, a 10-entry canonicalization corpus, three frozen fingerprints, and three independent verifier binaries (Python minimal, Rust, Go) that produce byte-identical fingerprints under an 18-stage `make ci` gate that passes in roughly nine seconds. 437 Python tests, 27 Rust tests, and 4 Go test packages pass on commit `b1bb16f`. Six runtimes (pipeline, proposer, review-gate, real-agent, os-isolation, resource-limit) exist as Makefile targets but are not yet gated by CI. No third party has independently run any verifier; no Linux wet-execution path exists; no production-grade security claim is supportable. The system is best described as a governed execution runtime kernel with deterministic verification and cross-language conformance — useful, reproducible, and not yet validated by anyone outside this repository.
