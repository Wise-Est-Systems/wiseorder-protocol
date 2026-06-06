# wiseorder-protocol

[![tests](https://github.com/Wise-Est-Systems/wiseorder-protocol/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/Wise-Est-Systems/wiseorder-protocol/actions/workflows/test.yml)
[![conformance](https://github.com/Wise-Est-Systems/wiseorder-protocol/actions/workflows/conformance.yml/badge.svg?branch=main)](https://github.com/Wise-Est-Systems/wiseorder-protocol/actions/workflows/conformance.yml)
[![verify-chain](https://github.com/Wise-Est-Systems/wiseorder-protocol/actions/workflows/verify-chain.yml/badge.svg?branch=main)](https://github.com/Wise-Est-Systems/wiseorder-protocol/actions/workflows/verify-chain.yml)
[![lint](https://github.com/Wise-Est-Systems/wiseorder-protocol/actions/workflows/lint.yml/badge.svg?branch=main)](https://github.com/Wise-Est-Systems/wiseorder-protocol/actions/workflows/lint.yml)
[![python](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue)](pyproject.toml)

> **WiseOrder governs how cognition becomes consequence** — the kernel that decides whether an AI's output is allowed to become an action, and seals every decision. It classifies each claim into a verification regime, runs a separate authorization gate before any action takes effect, and seals the resulting transitions in a hash-chained audit memory you can verify yourself, offline, with no account.
>
> One of three peers under Wise.Est Systems. A judgment can never be recorded as a proven fact, and an AI cannot rubber-stamp its own actions.

---

## 1. Purpose

`wiseorder-protocol` is the **kernel that governs how an AI's output is allowed to become an action** — one of three peers under Wise.Est Systems. It defines:

- four artifact classes (A/B/C/D), each with a typed verification regime and a fixed set of status tokens
- an append-only audit memory that hash-chains every committed transition
- a hash-chained `.win` triple chain anchored at a `NULLASIGN` genesis
- an authorization gate that runs *separately* from kernel verification (the same transition can be kernel-passed and gate-denied; conformance vectors prove this)
- a refusal store that records the structure of every rejected proposal
- a CLI (`intellagent`) that exposes the runtime as a state machine: `init → propose → transition → audit → refuse`

**This repo is NOT:**

- A model. The runtime does not contain a neural network. Transformers serve as proposers under the kernel.
- A network service. The runtime is single-host with no outbound HTTP in the core path.
- A moral system. WiseOrder governs the *form* a claim must take to be admissible under its class; the substantive content of correct judgment lives in conduct artifacts (Class D) and is governed there.
- A claim of AGI. Every "Non-Goals" section in every doc says so explicitly.

---

## 2. Architecture

```
                  AI output
                      ↓
              ┌───────────────┐
              │   WiseOrder   │   ← the kernel that governs what becomes an action (this repo)
              └───────────────┘
                      ↓
       ┌────────────────────────────┐
       │   Intellagent Runtime v0.1 │   ← state machine over the kernel (this repo)
       └────────────────────────────┘
                      ↓
       ┌────────────────────────────┐
       │     WIN       │   WISEATA  │   ← proof substrate: seal + verify, then inspect (separate repos)
       └────────────────────────────┘
                      ↓
                  execution systems
```

The kernel and runtime share a process; the runtime exposes the kernel through the `intellagent` CLI. There is no daemon, no service, no network listener.

| Path | Purpose |
| --- | --- |
| [`SPEC.md`](./SPEC.md) | WiseOrder Protocol v0.1.0 canonical draft. Governs in case of conflict. |
| [`SPEC_LOCK_v0.1.md`](./SPEC_LOCK_v0.1.md) / [`SPEC_LOCK_v0.2.0.md`](./SPEC_LOCK_v0.2.0.md) | Frozen specifications per version. |
| [`STATUS-REGISTRY.md`](./STATUS-REGISTRY.md) | Per-class status tokens and their meanings. |
| [`ARTIFACTS.md`](./ARTIFACTS.md) | JSON schema per artifact class. |
| [`CONFORMANCE.md`](./CONFORMANCE.md) | Conformance is class-scoped; vectors determine conformance, prose explains it. |
| [`IMPLEMENTATIONS.md`](./IMPLEMENTATIONS.md) | Registry of known implementations. |
| [`vectors/`](./vectors/) | Conformance test vectors (29 in `vectors/v0.2.0/` + 23 in v0.1.0 baseline). |
| [`schemas/`](./schemas/) | JSON Schemas for vectors, manifests, fixtures, declarations. |
| [`chain/`](./chain/) | The live v0.2.0 chain: `genesis.win` + 2 follow-up triples, `CHAIN_VALID`. |
| [`intellagent_runtime/`](./intellagent_runtime/) | Kernel, gate, audit memory, refusal store, proposers, chain primitives, CLI. |
| [`tools/`](./tools/) | Conformance + interop validators, pseudocode scanner, demo runner. |
| [`tests/`](./tests/) | **480** pytest tests covering protocol vectors, runtime semantics, chain integrity, transformer proposer, CLI, plus 7 crash-injection + 3 SIGKILL recovery tests. |
| [`interop/`](./interop/) | Fixture manifests + interop checks tying implementations to vectors. |
| [`reports/`](./reports/) | Committed conformance + interop reports (regenerated by `make conformance` / `make interop`). |
| [`rust_verifier/`](./rust_verifier/) | First-party independent verifier track (Rust). |
| [`go_verifier/`](./go_verifier/) | First-party independent verifier track (Go). |
| [`docs/`](./docs/) | Whitepapers, strategy, release packets, audits, runtime architecture. |

---

## 3. Invariants

Core invariants enforced by tests and CI. Documented in spec and code; reproduced here at high level.

- **Kernel ⟂ Gate separation.** Kernel verifies *structure*; the authorization gate verifies *policy*. A transition can pass one and fail the other. See [`intellagent_runtime/kernel.py`](./intellagent_runtime/kernel.py) and [`intellagent_runtime/authorization.py`](./intellagent_runtime/authorization.py).
- **Audit memory is fail-closed.** Loading the chain re-derives every entry's `this_entry_sha256` and verifies every `prev_entry_sha256` link. Any mismatch raises `ChainCorrupt` and the runtime refuses further operation.
- **State is content-addressed.** `state_id = sha256(canonical_json(sorted_objects))`. Loading state re-derives state_id and raises `StateTampered` on mismatch.
- **`apply_transition` is crash-safe.** Two-phase commit (stage → save → finalize) guarantees that after any crash, state and audit cannot diverge. Proven by 7 synthetic crash-injection tests + 3 real-process SIGKILL tests.
- **TS-1 timestamp precision.** Chain triples use microsecond precision; audit memory and conformance vectors use second precision. The two are intentionally NOT unified — chain filenames require sub-second uniqueness; audit/vectors require operator-readable consistency. Both formats are load-bearing.
- **WiseDigest-3 / III parity with WOP.** [`intellagent_runtime/iii.py`](./intellagent_runtime/iii.py) is a byte-identical mirror of [`wop/src/wise/digest_v3.py`](https://github.com/Wise-Est-Systems/wop). Any divergence breaks the cross-repository verifier compatibility claim.

---

## 4. Failure model

The runtime is fail-closed everywhere a sealed claim is at stake.

| failure | response |
|---|---|
| Audit chain corrupt (link broken or hash mismatch) | `ChainCorrupt` raised; CLI exits 2; no further commits |
| State tampered (recomputed state_id differs from declared) | `StateTampered` raised; CLI exits 2 |
| Process killed mid-`apply_transition` | startup `reconcile_pending(state.audit_head_sha256)` either finalizes the staged entry (state already references it) or discards it (state does not) — proven by SIGKILL tests |
| Malformed transition body | `TransitionSchemaError` raised at load time, not at kernel time — bad `regime` or path-traversal `transition_id` is rejected before kernel verification |
| Malformed policy JSON | `PolicySchemaError` raised — known-kind bodies with missing fields fail loudly, not silently |
| State / audit divergence after reconciliation | `StateAuditDivergence` raised; CLI refuses to proceed |

See [`docs/REVIEWER_GUIDE.md`](docs/REVIEWER_GUIDE.md) for a 30-minute path to reproduce each one.

---

## 5. Quick start

```bash
git clone https://github.com/Wise-Est-Systems/wiseorder-protocol.git
cd wiseorder-protocol

python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Full local CI: documentation code standard + tests + protocol conformance + interop.
make ci

# Run the transformer-backed runtime demo (no real model needed).
python3 tools/demo_transformer_proposer.py

# Initialize a runtime, propose a transition, commit, audit.
pip install -e .
intellagent --help
```

---

## 6. Verification commands

```bash
make ci                  # the heavy pre-flight: pseudocode standard + tests + conformance + interop + verifiers
make test                # pytest only (480 tests, ~3s)
make chain-verify        # standalone chain integrity; prints head hash
make conformance         # regenerate + check vector pass rates
make interop             # regenerate + check fixture conformance
make canonicalization-check  # 10 canonical-form corpus entries
make rust-verifier-check # first-party Rust verifier — must agree on all 3 fingerprints
make go-verifier-check   # first-party Go verifier — must agree on all 3 fingerprints
```

Expected output of `make chain-verify`:
```
CHAIN_VALID count=3 head=5964497c48c877946e2c92d15e3116f5991c1d8a4c99dc7eadb477cec558dd81
```

Expected output of `make test`:
```
480 passed, 9 xfailed in ~3s
```

### Frozen v0.1.0 fingerprints

A third party cloning this repo at the `v0.1.0` tag and running the three commands below MUST observe these exact fingerprints. Divergence is a non-conformance.

| Fingerprint | Required value |
|---|---|
| `vectors_suite_sha256` | `sha256:6168d2075931baa98bba763f9cd537142554aae7b26f19e3e93a60de2ee5bb0f` (33 vectors: 23 baseline + 10 adversarial) |
| `manifests_suite_sha256` | `sha256:74eaaa62271f23172232bda43ba3340543e66c46ba1e2f5e6da18d3447a6ba29` (3 fixtures) |
| `corpus_sha256` | `sha256:c95685bff48c15abc313c462908b05ac309250bc660c2d802ae51af5a8038b09` (10 corpus entries) |

The v0.2.0 vector set under `vectors/v0.2.0/` is published but not yet frozen; freezing happens at the next `SPEC_LOCK` cut.

---

## 7. CI status explanation

| workflow | what it gates | matrix |
|---|---|---|
| `tests` | pytest under multiple Pythons and OSes | ubuntu / macos × py3.11 / py3.12 |
| `lint` | ruff check + ruff format check on package + tools | ubuntu × py3.12 |
| `verify-chain` | runs `verify_chain` over `chain/`; emits head hash to job summary | ubuntu × py3.12 |
| `conformance` | full `make ci` (the heavy pre-flight: pseudocode + tests + conformance + interop + verifiers) | ubuntu × py3.12 |

Every push to `main` triggers all four. The `verify-chain` workflow has path filters so it runs only when `chain/`, `chain.py`, or `iii.py` change; the others run on every push.

---

## 8. Recovery guarantees

| event | guarantee |
|---|---|
| Process killed mid-`apply_transition` | `reconcile_pending` at next startup recovers a consistent on-disk state. Proven by 3 real-process SIGKILL tests. |
| Mac power loss between stage and save | `write_atomic` guarantees `current.json` is either old or new, not partial. Staging file (if present) is orphan and discarded. |
| Mac power loss between save and finalize | `current.json` references the staged entry's hash; reconcile renames staging→final. |
| Independent verifier (rust/go) disagrees with python on the same input | Conformance failure. CI fails. Block release. |
| Cross-machine replay produces different bytes | A non-conformance. See [`docs/release/CROSS_MACHINE_REPLAY_REPORT.md`](docs/release/CROSS_MACHINE_REPLAY_REPORT.md) for the determinism evidence. |

There is no rollback of a sealed chain triple. The chain is an audit trail; withdrawing a prior statement is done by appending a new triple whose `statement` documents the withdrawal.

---

## 9. Operational philosophy

- **The chain is the public-facing artifact, not the code.** External verifiers re-derive `consequence_proof` and `previous_action` from a `.win` file alone. The repo is provenance for the verifier; it is not the source of truth.
- **Fail closed at every seam.** `ChainCorrupt`, `StateTampered`, `TransitionSchemaError`, `PolicySchemaError`, `StateAuditDivergence` are not warnings — they halt the runtime.
- **No part of the protocol depends on a network.** Verification works offline from a USB drop. See `/Volumes/T7/2026-05-24/verify.sh` for the canonical "drop the drive, prove the chain" example.
- **Cross-language verifier parity is non-negotiable.** Python, Rust, and Go must all agree on the head hash for any release tag. Single-language verification is single-source assurance.
- **Vectors are the contract; code is one implementation.** A second implementation that passes the vectors is a peer; one that does not is non-conformant.

---

## 10. Current limitations

- **External-validation status: NOT_COMPLETE.** The Rust and Go verifiers in this repo are `FIRST_PARTY_INDEPENDENT_IMPLEMENTATION_TRACKS`, not third-party validation. A real third-party verifier is required for `EXTERNALLY_VALIDATED` status; see [`docs/release/THIRD_PARTY_VERIFIER_BRIEF_v0.1.md`](docs/release/THIRD_PARTY_VERIFIER_BRIEF_v0.1.md).
- **WiseDigest-3 is novel.** It is not SHA-2, not BLAKE3, not a permutation function used in production crypto. The math is in `wop/research/WiseDigest-3.md`; cryptographic analysis is `not yet complete`. Production use as a security-critical primitive requires that analysis.
- **Lint and mypy run with `continue-on-error: true`.** The baselines are not clean. Drift is reported but does not block CI yet.
- **No license file.** `pyproject.toml` references one. Choosing a license is a deliberate decision the project owner has not yet made; the repo is currently effectively closed-source by default copyright law.
- **No `CHANGELOG.md` yet.** Release history is in `git log --oneline`; the changelog template is in `docs/RELEASE_PROCESS.md`.

---

## 11. Roadmap

1. Wire branch protection on GitHub (the policy in `docs/BRANCH_PROTECTION.md` is currently aspirational; the UI does not enforce it).
2. Pick a license.
3. Tighten ruff + mypy baselines; remove `continue-on-error: true`.
4. Freeze `vectors/v0.2.0/` and cut `SPEC_LOCK_v0.2.0` if it is not already (verify against `chain/2026-05-23T071437_...win`).
5. First external engineering scrutiny (see `docs/release/EXTERNAL_REVIEW_PACKET_v0.1.md`).
6. Tag `v0.1.0` once #1, #2, and the audit packet are ready.
7. Cryptanalysis of WiseDigest-3 (deferred to `wop`; tracked there).

---

## 12. Security posture

| boundary | posture |
|---|---|
| Network | No outbound HTTP from the core runtime. Optional LLM providers (OpenAI / Anthropic) are opt-in dependencies; the default `DeterministicMockProvider` requires no network. |
| Filesystem | `intellagent` writes only under `--dir` (default cwd) into `intellagent_state/`, `intellagent_audit/`, `intellagent_refusals/`, `intellagent_objects/`. No writes elsewhere. |
| Untrusted JSON input | All transition + policy JSON is validated by typed schemas at load time. Unknown fields are tolerated (forward-compatible); known-field type mismatches raise. |
| Subprocess execution | `governed-run --execute` runs proposed commands under `tools/os_isolation_runtime` sandbox-exec isolation. Sandbox failures are recorded in the manifest. |
| Authentication | None at the protocol layer. The CLI is a local tool. Third-party verifier authentication is out of scope here (the chain is content-addressed). |

The threat model is: **an attacker with file-system access to the runtime root could tamper with `current.json`, the audit chain, or the queue, and the next invocation would either reject the tamper (StateTampered / ChainCorrupt) or surface it in CI (verify-chain workflow).** No invariant claims to defend against an attacker who can also modify the runtime's source code.

---

## 13. Release discipline

Documented in [`docs/RELEASE_PROCESS.md`](docs/RELEASE_PROCESS.md):

- Semver with explicit MAJOR triggers (new chain root or non-backwards-compatible vector change).
- Pre-release checklist: clean tree → `make ci` → `make chain-verify` → rust + go verifier parity → signed tag → T7 evidence snapshot.
- No retagging. No re-sealing the genesis after a public release.
- Rollback is by *appending* a withdrawal triple, not by editing or removing existing triples.

No releases tagged yet — this repo is `v0.1.0-pre`. The first tag will follow the items in the Roadmap.

---

## Further reading

- [`docs/REVIEWER_GUIDE.md`](docs/REVIEWER_GUIDE.md) — 30-minute path for an external reviewer
- [`docs/INTEGRATION.md`](docs/INTEGRATION.md) — how another system integrates
- [`docs/BRANCH_PROTECTION.md`](docs/BRANCH_PROTECTION.md) — operational policy on `main`
- [`docs/RELEASE_PROCESS.md`](docs/RELEASE_PROCESS.md) — semver, checklist, rollback
- [`docs/release/EXTERNAL_REVIEW_PACKET_v0.1.md`](docs/release/EXTERNAL_REVIEW_PACKET_v0.1.md) — what v0.1.0 is, what it isn't, what counts as successful external validation
- [`docs/release/REVIEW_QUICKSTART.md`](docs/release/REVIEW_QUICKSTART.md) — commands only; reproduce CI from a cold clone
- [`docs/release/THIRD_PARTY_VERIFIER_BRIEF_v0.1.md`](docs/release/THIRD_PARTY_VERIFIER_BRIEF_v0.1.md) — formal requirements for a third-party verifier submission
- [`CHANGELOG.md`](CHANGELOG.md) — release history
