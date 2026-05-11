.PHONY: validate-vectors validate-implementations conformance interop test ci verify-drift no-pseudocode canonicalization-golden canonicalization-check workforce-check workforce-stress real-agent-check real-agent-dry-run real-agent-execute real-agent-execute-check proposer-check proposer-propose review-gate-check review-gate-review pipeline-check pipeline-run-fixture os-isolation-check os-isolation-fixture resource-limit-check resource-limit-fixture replay-diff-check minimal-verifier-check binary-fixture-check sandbox-escape-check demo repo-health report-inventory archive-reports-dry-run rust-verifier-check rust-verifier-fingerprints go-verifier-check go-verifier-fingerprints work-order-parser-check workflow-grammar-check execution-plan-check audit-memory-check governed-run-check governed-run-pipeline-check chain-check

# Prefer the repo's .venv (which has pytest + jsonschema pinned in
# requirements.txt) when present; fall back to system python3 otherwise.
# Override explicitly with `make ci PYTHON=/path/to/python`.
PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)

validate-vectors:
	$(PYTHON) tools/validate_vectors.py

validate-implementations:
	$(PYTHON) tools/validate_implementations.py

conformance:
	$(PYTHON) tools/run_conformance.py

interop:
	$(PYTHON) interop/scripts/generate_fixture_manifest.py
	$(PYTHON) interop/scripts/run_interop_checks.py

test:
	$(PYTHON) -m pytest tests/ -v

no-pseudocode:
	$(PYTHON) tools/check_no_pseudocode.py

canonicalization-golden:
	$(PYTHON) canonicalization/tools/generate_golden.py

canonicalization-check:
	$(PYTHON) canonicalization/tools/verify_golden.py

workforce-check:
	$(PYTHON) tools/check_workforce.py

workforce-stress:
	$(PYTHON) tools/workforce_sandbox_stress.py

real-agent-check:
	$(PYTHON) tools/real_agent_runtime.py check

real-agent-dry-run:
	@if [ -n "$(WO)" ] && [ -n "$(AGENT)" ]; then \
	    $(PYTHON) tools/real_agent_runtime.py dry-run --work-order $(WO) --agent-id $(AGENT); \
	else \
	    $(PYTHON) tools/real_agent_runtime.py built-in-dry-run; \
	fi

# v0.2 execute mode — run admitted commands inside a sandbox copy.
# WO and AGENT are required. Optional REPLAY=1 admits a closed work order.
# Optional CMD repeats. Optional TIMEOUT overrides the per-command timeout.
real-agent-execute:
	@if [ -z "$(WO)" ] || [ -z "$(AGENT)" ]; then \
	    echo "usage: make real-agent-execute WO=<path> AGENT=<id> [TIMEOUT=<seconds>] [REPLAY=1] [CMD=<command>] ..."; \
	    exit 2; \
	fi
	$(PYTHON) tools/real_agent_runtime.py execute \
	    --work-order $(WO) \
	    --agent-id $(AGENT) \
	    $(if $(TIMEOUT),--timeout $(TIMEOUT),) \
	    $(if $(REPLAY),--replay,) \
	    $(if $(CMD),--command "$(CMD)",)

# v0.2 execute-mode self-check fixtures. NOT included in `make ci`.
real-agent-execute-check:
	$(PYTHON) tools/real_agent_runtime.py execute-check

# v0.1 proposer runtime self-check. NOT included in `make ci`. Bounded
# candidate-command generation under governance, with zero execution
# authority. Spec: PROPOSER-RUNTIME-v0.1.md.
proposer-check:
	$(PYTHON) tools/proposer_runtime.py self-check

# v0.1 proposer runtime propose verb. NOT included in `make ci`. WO and
# AGENT are required.
proposer-propose:
	@if [ -z "$(WO)" ] || [ -z "$(AGENT)" ]; then \
	    echo "usage: make proposer-propose WO=<path> AGENT=<id>"; \
	    exit 2; \
	fi
	$(PYTHON) tools/proposer_runtime.py propose --work-order $(WO) --agent-id $(AGENT)

# v0.1 review gate runtime self-check. NOT included in `make ci`.
# Deterministic admission of proposer output, with zero execution authority.
# Spec: REVIEW-GATE-RUNTIME-v0.1.md.
review-gate-check:
	$(PYTHON) tools/review_gate_runtime.py self-check

# v0.1 review gate runtime review verb. NOT included in `make ci`. PROPOSAL
# is required. EXPECTED_WO and REVIEWER are optional.
review-gate-review:
	@if [ -z "$(PROPOSAL)" ]; then \
	    echo "usage: make review-gate-review PROPOSAL=<path> [EXPECTED_WO=<id>] [REVIEWER=<id>]"; \
	    exit 2; \
	fi
	$(PYTHON) tools/review_gate_runtime.py review \
	    --proposal $(PROPOSAL) \
	    $(if $(EXPECTED_WO),--expected-work-order-id $(EXPECTED_WO),) \
	    $(if $(REVIEWER),--reviewer-id $(REVIEWER),)

# v0.1 pipeline runtime self-check. NOT included in `make ci`.
# End-to-end governed handoff: proposer → review gate → executor.
# Spec: PIPELINE-RUNTIME-v0.1.md.
pipeline-check:
	$(PYTHON) tools/pipeline_runtime.py self-check

# v0.1 pipeline runtime run against the canonical fixture work order.
# NOT included in `make ci`.
pipeline-run-fixture:
	$(PYTHON) tools/pipeline_runtime.py run-fixture

# v0.1 OS isolation runtime self-check. NOT included in `make ci`.
# Kernel-backed containment via macOS sandbox-exec.
# Spec: OS-ISOLATION-RUNTIME-v0.1.md.
os-isolation-check:
	$(PYTHON) tools/os_isolation_runtime.py self-check

# v0.1 OS isolation runtime run-fixture. Runs the canonical valid
# fixture (`pwd`) under kernel-backed sandbox-exec confinement.
# NOT included in `make ci`.
os-isolation-fixture:
	$(PYTHON) tools/os_isolation_runtime.py run-fixture

# v0.1 resource limit runtime self-check. NOT included in `make ci`.
# Hard bounded-resource enforcement on top of OS isolation.
# Spec: RESOURCE-LIMIT-RUNTIME-v0.1.md.
resource-limit-check:
	$(PYTHON) tools/resource_limit_runtime.py self-check

# v0.1 resource limit runtime run-fixture. Runs `pwd` under bounded
# isolation. NOT included in `make ci`.
resource-limit-fixture:
	$(PYTHON) tools/resource_limit_runtime.py run-fixture

verify-drift: conformance interop
	@if ! git diff --exit-code -- reports/ interop/; then \
		echo ""; \
		echo "ERROR: regenerated artifacts drift from committed state."; \
		echo "Re-run 'make conformance && make interop' and commit the result."; \
		exit 1; \
	fi
	@echo "OK: regenerated artifacts match committed state."

# v0.1 replay diff engine self-check. NOT included in `make ci` until stable.
# Spec: WORK ORDER 007. Tool: tools/replay_diff.py.
replay-diff-check:
	$(PYTHON) tools/replay_diff.py self-check

# v0.1 minimal independent verifier. NOT included in `make ci` until stable.
# Re-derives Class A/B/C/D verdicts from spec without importing
# intellagent_runtime. Tool: tools/minimal_verifier.py.
minimal-verifier-check:
	$(PYTHON) tools/minimal_verifier.py check

# v0.1 binary fixture check. NOT included in `make ci` until stable.
# Computes SHA-256 of binary_fixtures/*.bin against manifest expected_digest.
# Tool: tools/binary_fixture_check.py.
binary-fixture-check:
	$(PYTHON) tools/binary_fixture_check.py check

# v0.1 sandbox escape check. NOT included in `make ci` until stable.
# Asserts policy guard refuses 6 categories of hostile inputs.
# Tool: tools/sandbox_escape_check.py. Does NOT execute hostile commands.
sandbox-escape-check:
	$(PYTHON) tools/sandbox_escape_check.py check --quiet

# v0.1 demo orchestrator. Runs conformance + interop + canonicalization-check
# + minimal-verifier-check + replay-diff-check + binary-fixture-check, then
# verifies the three frozen v0.1.0 fingerprints. NOT included in `make ci`.
demo:
	$(PYTHON) tools/demo_runner.py

# v0.1 repo health. Emits a one-shot summary of root files, docs/* counts,
# reports/canonical + reports/archive counts. Non-destructive.
repo-health:
	@echo "WiseOrder Protocol — repo health"
	@echo "================================="
	@echo "root .md files:"
	@ls *.md 2>/dev/null | sort | sed 's/^/  /'
	@echo ""
	@echo "docs/ subfolders:"
	@for d in docs/*/; do printf "  %-22s %s files\n" "$$d" "$$(ls "$$d" 2>/dev/null | wc -l | tr -d ' ')"; done
	@echo ""
	@echo "reports/ top-level:"
	@ls reports/ 2>/dev/null | grep -v '^archive$$' | grep -v '^canonical$$' | grep -v '^repo_health$$' | sed 's/^/  /'
	@echo ""
	@echo "reports/canonical: $$(ls reports/canonical 2>/dev/null | wc -l | tr -d ' ') files"
	@echo "reports/repo_health: $$(ls reports/repo_health 2>/dev/null | wc -l | tr -d ' ') files"
	@echo "reports/archive: $$(find reports/archive -type f 2>/dev/null | wc -l | tr -d ' ') files"
	@echo ""
	@echo "frozen fingerprints (from regenerated reports):"
	@$(PYTHON) -c "import json; r=json.load(open('reports/conformance-report.json')); print('  vectors_suite_sha256:   ' + r['vectors_suite_sha256'])" 2>/dev/null || echo "  (reports/conformance-report.json not present — run 'make conformance')"
	@$(PYTHON) -c "import json; r=json.load(open('interop/reports/interop-report.json')); print('  manifests_suite_sha256: ' + r['manifests_suite_sha256'])" 2>/dev/null || echo "  (interop/reports/interop-report.json not present — run 'make interop')"

# v0.1 report inventory. Lists canonical reports vs archived per-run files.
# Non-destructive; read-only.
report-inventory:
	@echo "WiseOrder Protocol — report inventory"
	@echo "====================================="
	@echo "[canonical / live runtime summaries]"
	@for f in reports/conformance-report.json reports/conformance-summary.txt reports/canonical/README.md; do \
	    if [ -f "$$f" ]; then echo "  $$f ($$(wc -c < "$$f" | tr -d ' ') bytes)"; fi; \
	done
	@for d in reports/pipeline_runtime reports/proposer_runtime reports/review_gate_runtime \
	          reports/os_isolation_runtime reports/resource_limit_runtime \
	          reports/real_agent_runtime reports/workforce_sandbox_stress; do \
	    if [ -d "$$d" ]; then \
	        n=$$(ls "$$d" 2>/dev/null | wc -l | tr -d ' '); \
	        echo "  $$d/  ($$n files including _fixtures and canonical summaries)"; \
	    fi; \
	done
	@echo ""
	@echo "[ci evidence]"
	@if [ -d reports/ci ]; then \
	    for f in reports/ci/*; do echo "  $$f"; done; \
	fi
	@echo ""
	@echo "[archived per-run files (not load-bearing)]"
	@for d in reports/archive/pipeline_runtime reports/archive/proposer_runtime \
	          reports/archive/review_gate_runtime reports/archive/os_isolation_runtime/runs \
	          reports/archive/resource_limit_runtime/runs; do \
	    n=$$(find "$$d" -maxdepth 1 -type f 2>/dev/null | wc -l | tr -d ' '); \
	    echo "  $$d/  $$n files"; \
	done
	@echo ""
	@echo "See reports/canonical/README.md for the canonical/archived rule."

# v0.1 first-party independent Rust verifier track. NOT included in
# `make ci` per WORK ORDER 012. Verifies vectors + corpus + the three
# frozen fingerprints via a Rust binary that does not import Python.
# Spec: docs/release/IMPLEMENTATION_TRACKER.md §2.1.
rust-verifier-check:
	cargo test --manifest-path rust_verifier/Cargo.toml --quiet
	cargo run  --manifest-path rust_verifier/Cargo.toml --quiet -- verify-vectors
	cargo run  --manifest-path rust_verifier/Cargo.toml --quiet -- verify-corpus

# v0.1 Rust verifier fingerprint check (subset). NOT in `make ci`.
rust-verifier-fingerprints:
	cargo run --manifest-path rust_verifier/Cargo.toml --quiet -- fingerprints

# v0.1 first-party independent Go verifier track. NOT in `make ci` per
# WORK ORDER 013 (until cold confirmation in a future work order). Verifies
# vectors + corpus + the three frozen fingerprints via a Go binary that
# does not import Python or the Rust verifier.
go-verifier-check:
	go test ./go_verifier/...
	go run  ./go_verifier verify-vectors
	go run  ./go_verifier verify-corpus

# v0.1 Go verifier fingerprint check (subset). NOT in `make ci`.
go-verifier-fingerprints:
	go run ./go_verifier fingerprints

# v0.1 runtime core self-checks (WORK ORDER 015). NOT in `make ci` until
# stable across cold runs. Each target runs the module's self_check()
# function which exits 0 on PASS and 1 on FAIL.
work-order-parser-check:
	$(PYTHON) -m intellagent_runtime.work_order_parser

workflow-grammar-check:
	$(PYTHON) -m intellagent_runtime.workflow_grammar

execution-plan-check:
	$(PYTHON) -m intellagent_runtime.execution_plan

audit-memory-check:
	$(PYTHON) -m intellagent_runtime.audit_memory

governed-run-check:
	$(PYTHON) -m intellagent_runtime.cli governed-run --self-check

# v0.1 governed-run pipeline integration check (WORK ORDER 016). NOT in
# `make ci` until cold-stable. Exercises dry-run + wet-run + refusal paths
# end-to-end through the CLI.
governed-run-pipeline-check:
	$(PYTHON) -m pytest tests/test_governed_run_pipeline.py tests/test_intellagent_cli.py -q

# v0.2.0 chain integrity check (WO-018). Runs the chain module self-check
# (seal/append/verify/tamper-detect) and the pytest suite for chain.py.
# III digest parity vs WOP reference is covered by tests/test_iii.py.
chain-check:
	$(PYTHON) -m intellagent_runtime.chain
	$(PYTHON) -m pytest tests/test_iii.py tests/test_chain.py -q

# v0.1 dry-run archiver. Prints what files would be moved from live runtime
# directories into reports/archive/. Modifies nothing. Useful before periodic
# cleanup. NOT included in `make ci`.
archive-reports-dry-run:
	@echo "WiseOrder Protocol — archive-reports DRY RUN"
	@echo "============================================="
	@echo "(no files are moved by this target)"
	@echo ""
	@for src_glob in "reports/pipeline_runtime/pipeline-*T*Z.*" \
	                 "reports/proposer_runtime/proposal-*T*Z.*" \
	                 "reports/review_gate_runtime/review-*T*Z*.*" \
	                 "reports/os_isolation_runtime/runs/run-*Z*.json" \
	                 "reports/resource_limit_runtime/runs/run-*Z*.json"; do \
	    matches=$$(ls $$src_glob 2>/dev/null); \
	    if [ -n "$$matches" ]; then \
	        count=$$(echo "$$matches" | wc -l | tr -d ' '); \
	        echo "$$count file(s) match: $$src_glob"; \
	        echo "$$matches" | head -3 | sed 's/^/    /'; \
	        if [ "$$count" -gt 3 ]; then echo "    ..."; fi; \
	    fi; \
	done
	@echo ""
	@echo "Would move into: reports/archive/<runtime>/"
	@echo "Run 'make repo-health' to see current archive counts."

ci: no-pseudocode test work-order-parser-check workflow-grammar-check execution-plan-check audit-memory-check governed-run-check governed-run-pipeline-check chain-check conformance interop canonicalization-check minimal-verifier-check replay-diff-check binary-fixture-check sandbox-escape-check rust-verifier-check go-verifier-check
	@echo "CI: documentation code standard + tooling tests + governed-runtime core (parser + grammar + plan + audit + governed-run self-check + pipeline-integration tests) + v0.2.0 chain (III digest + .win chain primitives + tamper detection) + protocol conformance + interoperability + canonicalization golden + minimal-verifier + replay-diff + binary-fixture + sandbox-escape + rust-verifier + go-verifier (first-party independent tracks; cargo test and go test each cover all 3 frozen fingerprints) all passed."
