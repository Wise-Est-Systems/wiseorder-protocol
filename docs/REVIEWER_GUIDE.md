# REVIEWER_GUIDE

A 30-minute path for an external engineer to validate everything this repo claims about its kernel, chain, and crash safety. This is the consolidated view; longer-form documents live at [`docs/release/EXTERNAL_REVIEW_PACKET_v0.1.md`](release/EXTERNAL_REVIEW_PACKET_v0.1.md) and [`docs/release/REVIEW_QUICKSTART.md`](release/REVIEW_QUICKSTART.md).

## Prerequisites

- Python 3.11 or 3.12
- (Optional) Rust toolchain for the Rust verifier track
- (Optional) Go ≥1.21 for the Go verifier track

## Minute 0–5 — Clone + bootstrap

```bash
git clone https://github.com/Wise-Est-Systems/wiseorder-protocol.git
cd wiseorder-protocol

python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Minute 5–10 — Run the full local CI

```bash
make ci
```

What this runs: documentation code standard check (no pseudocode) → all tests → protocol conformance against vectors → interop fixture checks → canonicalization golden → Rust verifier → Go verifier.

Expected: every step prints OK; final line is the long `make ci` summary.

If just the tests:

```bash
make test
```

Expected:
```
480 passed, 9 xfailed in ~3s
```

## Minute 10–15 — Verify the chain end-to-end

```bash
make chain-verify
```

Expected:
```
CHAIN_VALID count=3 head=5964497c48c877946e2c92d15e3116f5991c1d8a4c99dc7eadb477cec558dd81
```

The chain on disk consists of 3 `.win` files under `chain/`. Each file is a JSON triple sealed with WiseDigest-3 (III). `verify_chain` re-derives every `consequence_proof` and every `previous_action` linkage; any tamper raises `CHAIN_TAMPERED`.

You can also run the offline verifier from the T7 evidence drop (if you have access to the drive):
```bash
cd /Volumes/T7/2026-05-24 && bash verify.sh
```
Same output. No network. No GitHub. The drive is self-contained.

## Minute 15–20 — Replay the SIGKILL crash test

This is the missing-piece-from-previous-audits proof.

```bash
.venv/bin/pytest tests/test_sigkill_recovery.py -v
```

Expected:
```
test_sigkill_after_stage_discards_orphan ............... PASSED
test_sigkill_after_state_save_recovers_committed ........ PASSED
test_sigkill_test_skip_marker_on_windows ................ PASSED
```

What this proves: the parent test spawns a subprocess that pauses mid-`apply_transition` at known checkpoints, then `os.kill(pid, SIGKILL)`s it (signal 9 — uncatchable, no cleanup possible). The parent then runs `reconcile_pending(state.audit_head_sha256)` from a fresh process and asserts the invariants hold:
- `audit.verify_chain()` passes
- `state.audit_head_sha256 == audit.head_sha256()`
- no `*.staging` files remain

## Minute 20–25 — Inspect cross-language verifier parity

```bash
make rust-verifier-check
make go-verifier-check
```

Each verifier runs the same 3 frozen v0.1.0 fingerprints (`vectors_suite_sha256`, `manifests_suite_sha256`, `corpus_sha256`) and must report agreement with the Python reference.

If you have Rust + Go installed locally; both are first-party independent tracks. **External-validation status is `NOT_COMPLETE`** until a third party (not Wise-Est-Systems) submits a verifier per [`docs/release/THIRD_PARTY_VERIFIER_BRIEF_v0.1.md`](release/THIRD_PARTY_VERIFIER_BRIEF_v0.1.md).

## Minute 25–28 — Inspect the integrity model

Skim:
- [`intellagent_runtime/memory.py`](../intellagent_runtime/memory.py) — `stage_entry`, `finalize_staged`, `reconcile_pending`, `verify_state_consistency`. The two-phase commit pattern lives here.
- [`intellagent_runtime/runtime.py:apply_transition`](../intellagent_runtime/runtime.py) — the call site. Comment block explains the crash windows.
- [`intellagent_runtime/chain.py`](../intellagent_runtime/chain.py) — `verify_chain`, `seal_genesis`, `append_triple`. `INVARIANT TS-1` block at the top explains why timestamp precision is intentionally divergent from `canonical.py`.

## Minute 28–30 — Read the boundary docs

- [`SPEC.md`](../SPEC.md) — the protocol contract.
- [`SPEC_LOCK_v0.1.md`](../SPEC_LOCK_v0.1.md) / [`SPEC_LOCK_v0.2.0.md`](../SPEC_LOCK_v0.2.0.md) — what's frozen at each version.
- [`docs/release/EXTERNAL_REVIEW_PACKET_v0.1.md`](release/EXTERNAL_REVIEW_PACKET_v0.1.md) — what counts as a successful third-party validation.
- [`docs/BRANCH_PROTECTION.md`](BRANCH_PROTECTION.md) — what `main` is required to look like.

## What should concern you

Brutal honesty for a reviewer:

1. **WiseDigest-3 is novel.** It is not SHA-2, not BLAKE3, not a permutation function with peer-reviewed cryptanalysis. The reference + math is in [`wop/research/WiseDigest-3.md`](https://github.com/Wise-Est-Systems/wop). External cryptanalysis is **deferred**. If your use case requires the audit-trail primitive to be collision-resistant against an adversary with multi-year compute budgets, this is not yet that primitive.
2. **External-validation status is NOT_COMPLETE.** Two language verifiers exist (Rust, Go) but both are first-party tracks. A third-party verifier per the brief would change this status.
3. **Lint runs continue-on-error.** Drift is reported, not blocked. A reviewer should expect this to tighten over the next release cycle.
4. **No license file.** `pyproject.toml` references "see LICENSE" — there isn't one. By default copyright law applies; this is not open source.
5. **Branch protection is documented, not enforced.** Force-push to `main` is technically allowed by the GitHub configuration today.
6. **The Intellagent transformer proposer is opt-in.** The default `DeterministicMockProvider` is for testing. Real-model use is a 5-line change but requires provider keys.
7. **The chain has only 3 triples.** This is real evidence that the system has been used, not just written. It is also small enough that a reviewer could read every triple in full.
8. **`apply_transition` is the only code path that uses the staging-finalize pattern.** Other state-modifying paths (cmd_init, cmd_propose, cmd_refuse) do not — they don't need to (each is atomic via `write_atomic`), but a future code path that mutates state across two stores must adopt the same pattern. There is no central enforcement.
9. **The conformance vectors include synthetic timestamps that are NOT compared.** Determinism is verified by content hash; the `created_at` fields in vectors are illustrative. An auditor should not assume vector timestamps are cryptographically meaningful.
10. **No `governed-run --execute` test that proves sandbox escape resistance.** [`tests/test_sandbox_escape_check.py`](../tests/test_sandbox_escape_check.py) covers known scenarios; adversarial escape research is `not yet complete`.

If any of those would block you, raise them and the project owner can decide whether to action or accept.
