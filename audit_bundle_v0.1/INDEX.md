# AUDIT_BUNDLE_v0.1

A curated entry path for a skeptical protocol engineer or infrastructure reviewer. Every artifact referenced here lives in this repository at a stable path; nothing is generated specifically for this bundle. The bundle is the index, not new content.

## Reading order (~45 minutes total)

| # | document | minutes | what it tells you |
|---|---|---|---|
| 1 | [`docs/REVIEWER_GUIDE.md`](../docs/REVIEWER_GUIDE.md) | 30 | clone → tests → chain verify → SIGKILL replay → cross-language verifier parity → boundary docs |
| 2 | [`SPEC.md`](../SPEC.md) | 10 | the v0.1.0 protocol contract |
| 3 | [`docs/runtime/INTELLAGENT-RUNTIME.md`](../docs/runtime/INTELLAGENT-RUNTIME.md) | 5 | the runtime specification |

If you have 15 minutes, read items 1 and 3 only. If you have 5 minutes, run `make ci` from a fresh clone and read the head of `docs/REVIEWER_GUIDE.md` "what should concern you" section.

## The bundle's contents

### Architecture
- [`docs/ORG_STRUCTURE.md`](../docs/ORG_STRUCTURE.md) — canonical repo map, trust boundaries, maturity matrix
- [`SYSTEM-MAP-v0.1.md`](../SYSTEM-MAP-v0.1.md) — protocol-level system map
- [`docs/runtime/INTELLAGENT.md`](../docs/runtime/INTELLAGENT.md) — architecture proposal
- [`docs/runtime/INTELLAGENT-RUNTIME.md`](../docs/runtime/INTELLAGENT-RUNTIME.md) — runtime spec

### Invariants
- [`intellagent_runtime/chain.py`](../intellagent_runtime/chain.py) — INVARIANT TS-1 (timestamp precision) documented inline in module docstring
- [`intellagent_runtime/canonical.py`](../intellagent_runtime/canonical.py) — pair of TS-1
- [`intellagent_runtime/memory.py`](../intellagent_runtime/memory.py) — staged-commit + reconcile + verify_state_consistency
- [`intellagent_runtime/runtime.py`](../intellagent_runtime/runtime.py) — apply_transition's crash-safe ordering, documented in the docstring

### Failure model
- [`docs/runtime/INTELLAGENT-EVALUATION.md`](../docs/runtime/INTELLAGENT-EVALUATION.md) — 10 adversarial scenarios for governed-cognition
- [`vectors/v0.1.0/`](../vectors/v0.1.0/) — 23 baseline + 10 adversarial conformance vectors
- [`vectors/v0.2.0/`](../vectors/v0.2.0/) — 6 v0.2.0 vectors (Class B state machine, Class C signed attestation, Class D preimage cap)

### Threat model
- [`SECURITY.md`](../SECURITY.md) (if present) — security-disclosure path
- [`README.md`](../README.md) §12 — protocol-layer security posture
- [`docs/ADOPTION_REALITY.md`](../docs/ADOPTION_REALITY.md) — "what assumptions are unsafe at scale"

### Reproducibility
- [`docs/CROSS_PLATFORM.md`](../docs/CROSS_PLATFORM.md) — what's tested on which platform, replay invariants
- [`docs/RELEASE_CHECKLIST.md`](../docs/RELEASE_CHECKLIST.md) — what must be true before any `v0.x.y` tag
- [`docs/RELEASE_VERIFICATION.md`](../docs/RELEASE_VERIFICATION.md) — how a third party verifies a release
- [`docs/release/REVIEW_QUICKSTART.md`](../docs/release/REVIEW_QUICKSTART.md) — commands-only reproduction
- [`docs/release/CROSS_MACHINE_REPLAY_REPORT.md`](../docs/release/CROSS_MACHINE_REPLAY_REPORT.md) — pre-existing replay evidence

### CI workflows
- [`.github/workflows/conformance.yml`](../.github/workflows/conformance.yml) — heavy `make ci`
- [`.github/workflows/test.yml`](../.github/workflows/test.yml) — matrix tests (ubuntu/macos × py3.11/py3.12)
- [`.github/workflows/verify-chain.yml`](../.github/workflows/verify-chain.yml) — standalone chain integrity
- [`.github/workflows/lint.yml`](../.github/workflows/lint.yml) — ruff (informational)

### SIGKILL recovery evidence
- [`tests/test_sigkill_recovery.py`](../tests/test_sigkill_recovery.py) — 3 real-process SIGKILL tests
- [`tests/test_apply_transition_crash_safety.py`](../tests/test_apply_transition_crash_safety.py) — 7 synthetic crash-injection tests
- [`tests/_sigkill_helper.py`](../tests/_sigkill_helper.py) — the helper subprocess that pauses at known checkpoints

### Chain verification examples
- [`chain/genesis.win`](../chain/genesis.win) — the chain root
- [`chain/2026-05-11T063325_*.win`](../chain/) — second triple (WO-018: III adopted)
- [`chain/2026-05-23T071437_*.win`](../chain/) — third triple (WO-D5 + WO-CLASS-B + WO-IDENTITY)
- `make chain-verify` — re-derives every `consequence_proof` and every `previous_action` link

### Cross-language verifier parity
- [`rust_verifier/`](../rust_verifier/) — first-party Rust track
- [`go_verifier/`](../go_verifier/) — first-party Go track
- [`tools/minimal_verifier.py`](../tools/minimal_verifier.py) — minimal Python verifier
- All three must agree on `vectors_suite_sha256`, `manifests_suite_sha256`, `corpus_sha256`

### Demo-forge proofs (external repo)
- `~/Desktop/demo-forge/outputs/RELEASE_001_SIGKILL/` — 27-second SIGKILL recovery proof with SHA-256 manifest
- artifact_manifest.json verifies 8 files; integrity round-trip: 8/8

### Known limitations + open risks
- [`docs/ADOPTION_REALITY.md`](../docs/ADOPTION_REALITY.md) — "what would break under scale" + "what remains research-grade"
- [`docs/REVIEWER_GUIDE.md`](../docs/REVIEWER_GUIDE.md) "what should concern you" — 10 honest items
- [`docs/release/EXTERNAL_REVIEW_PACKET_v0.1.md`](../docs/release/EXTERNAL_REVIEW_PACKET_v0.1.md) — what counts as external validation

### Cryptanalysis status
- [`intellagent_runtime/iii.py`](../intellagent_runtime/iii.py) — module docstring documents the WiseDigest-3 lockstep with WOP
- `wop/research/WiseDigest-3.md` (separate repo) — the math
- **Status: `not yet complete`**, documented honestly. Treat as research-grade until external review lands.

## What an auditor should be able to reproduce in 60 minutes

```bash
# 0. Clone fresh
git clone --branch v0.1.0-rc1 https://github.com/Wise-Est-Systems/wiseorder-protocol.git /tmp/audit
cd /tmp/audit

# 1. Bootstrap
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Run the full pre-flight (≈ 2 min)
make ci

# 3. Verify the chain (≈ 1 sec)
make chain-verify

# 4. Replay the SIGKILL crash-recovery tests (≈ 1 sec)
.venv/bin/pytest tests/test_sigkill_recovery.py -v
.venv/bin/pytest tests/test_apply_transition_crash_safety.py -v

# 5. Cross-language verifier parity (≈ 30 sec)
make rust-verifier-check
make go-verifier-check

# 6. Sanity-check the frozen v0.1.0 fingerprints against the README
make conformance && jq '.vectors_suite_sha256' reports/conformance-report.json
make interop && jq '.manifests_suite_sha256' interop/reports/interop-report.json
make canonicalization-check
```

Every step should print `OK` / `PASS` / `CHAIN_VALID`. The three fingerprints should match the values published in README.md.

If any step fails, that is a non-conformance. File an issue with the bug-report template.

## What this bundle does NOT include

- Production deployment recipes — out of scope for protocol audit.
- Marketing copy — does not exist; check `docs/whitepapers/` if you want the longer-form positioning.
- A "yes/no should I adopt this?" recommendation — that depends on your use case. See `docs/ADOPTION_REALITY.md` for the framing.

## Open questions a reviewer is welcome to ask

These are the questions we expect a skeptical engineer to have. Honest acknowledgement, not deflection:

1. **WiseDigest-3 cryptanalysis** — when? Deferred to WOP; tracked separately; no externally-validated answer yet.
2. **Multi-process safety of the CLI** — formally unverified. Single-operator is the design point; concurrent invocations are not the test target.
3. **Sandbox-escape resistance of `governed-run --execute`** — tested via `tests/test_sandbox_escape_check.py` but the test set is illustrative. A determined attacker might find an escape we haven't covered.
4. **External-validation status** — `NOT_COMPLETE`. Two language verifiers exist (Rust, Go) but both are first-party. Real third-party validation per `docs/release/THIRD_PARTY_VERIFIER_BRIEF_v0.1.md` is open.
5. **Tagged release maturity** — `v0.1.0-rc1` (release candidate). `v0.1.0` final is gated on signing infrastructure + branch protection enforcement + this bundle being reviewed by at least one external party.

The honest closing line: **this bundle is enough to evaluate; it is not enough to bet your company on. The gap is the work we are doing.**
