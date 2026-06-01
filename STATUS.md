# STATUS — Live Numbers

> A receipts-only page. Every number here is reproducible from the head commit by running `make ci`. If you find a number on this page that you cannot reproduce, that is itself a bug under [`SECURITY.md`](./SECURITY.md) — open an advisory.

**Last reproduced:** 2026-06-01 04:24:43 UTC (from a fresh clone, against commit `b87fda2`).
**Reproduction recipe:** `git clone https://github.com/Wise-Est-Systems/wiseorder-protocol && cd wiseorder-protocol && python3.12 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && make ci`

---

## Gates

| Gate                                  | Command                                          | Result      |
|---------------------------------------|--------------------------------------------------|-------------|
| Documentation code standard           | `make no-pseudocode`                             | exit 0      |
| Tooling tests                         | `pytest tests/`                                  | 135 / 135 passed |
| Protocol conformance                  | `make conformance`                               | 33 / 33 vectors passed |
| Interoperability                      | `make interop`                                   | 3 / 3 fixtures passed |
| Canonicalization golden corpus        | `make canonicalization-check`                    | 10 / 10 entries verified |
| Independent Rust verifier             | `cargo test` (in `rust_verifier/`)               | agrees on all 3 frozen fingerprints |
| Independent Go verifier               | `go run ./go_verifier verify-corpus`             | agrees on all 3 frozen fingerprints |
| Full CI chain                         | `make ci`                                        | exit 0      |
| Drift verification                    | `make verify-drift`                              | no drift    |
| Cross-stack structure check (daily)   | `python tools/verify_stack.py`                   | 4 / 4 STACK_ROLE fingerprints matched |
| Demo run                              | `python3 tools/demo_transformer_proposer.py`     | overall PASS, exit 0 |

---

## Stable fingerprints

These values are byte-identical across runs at the head commit. A fresh `make conformance` MUST reproduce them; if it does not, drift detection has failed.

| Field                                                    | Value |
|----------------------------------------------------------|---|
| `vectors_suite_sha256`                                   | `sha256:37d3ec45ecca12d256b7df1c02ac0f0d1474f71b68510e9475fa449b8eb1331b` |
| `manifests_suite_sha256`                                 | `sha256:74eaaa62271f23172232bda43ba3340543e66c46ba1e2f5e6da18d3447a6ba29` |
| `canonicalization corpus_sha256`                         | `sha256:c95685bff48c15abc313c462908b05ac309250bc660c2d802ae51af5a8038b09` |
| Determinism cross-run audit-bytes hash                   | `sha256:b71c7134ef2c33ea5fcc9a3eb723efe6294ba18759ed91d1f64bdfe826107ba5` |

---

## External validation

| Status         | What it means | Current |
|----------------|---------------|---------|
| `NOT_COMPLETE` | No third party has independently published a conformance verdict against this codebase yet. | **current** |
| `COMPLETE`     | At least one named third party has run `make conformance` against a published commit SHA and published their result, pass or fail. | not yet |

The commitment: **first external conformance run by a non-Wise.Est party by 2026-10-01** (see the dated roadmap on the [org page](https://github.com/Wise-Est-Systems)). Misses become public misses.

If you would consider being the first external party: see [`SECURITY.md`](./SECURITY.md) for the contact paths, or open a [GitHub Discussion](https://github.com/Wise-Est-Systems/wiseorder-protocol/discussions). We will publish your result verbatim regardless of outcome.

---

## CI badges

| Workflow            | Badge                                                                                                                                              |
|---------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| Tests               | [![tests](https://github.com/Wise-Est-Systems/wiseorder-protocol/actions/workflows/test.yml/badge.svg)](https://github.com/Wise-Est-Systems/wiseorder-protocol/actions/workflows/test.yml) |
| Conformance         | [![conformance](https://github.com/Wise-Est-Systems/wiseorder-protocol/actions/workflows/conformance.yml/badge.svg)](https://github.com/Wise-Est-Systems/wiseorder-protocol/actions/workflows/conformance.yml) |
| Verify-chain        | [![verify-chain](https://github.com/Wise-Est-Systems/wiseorder-protocol/actions/workflows/verify-chain.yml/badge.svg)](https://github.com/Wise-Est-Systems/wiseorder-protocol/actions/workflows/verify-chain.yml) |
| Verify-stack        | [![verify-stack](https://github.com/Wise-Est-Systems/wiseorder-protocol/actions/workflows/verify-stack.yml/badge.svg)](https://github.com/Wise-Est-Systems/wiseorder-protocol/actions/workflows/verify-stack.yml) |
| Lint                | [![lint](https://github.com/Wise-Est-Systems/wiseorder-protocol/actions/workflows/lint.yml/badge.svg)](https://github.com/Wise-Est-Systems/wiseorder-protocol/actions/workflows/lint.yml) |

---

## Maintenance note

This file is the **most volatile document in the repo**. Numbers are point-in-time. The "Last reproduced" timestamp at the top tells you how stale the snapshot is. The fingerprints below it are stable across runs at the same commit — they only change when the spec or vectors change, and any change to vector bytes is itself a coordinated event (see [`RELEASE-CHECKLIST-v0.1.md`](./docs/release/RELEASE-CHECKLIST-v0.1.md)).

If you are an external reviewer and your fresh `make ci` produces different numbers than this page lists at the same commit SHA, please open a [GitHub Discussion](https://github.com/Wise-Est-Systems/wiseorder-protocol/discussions) or a private [Security Advisory](https://github.com/Wise-Est-Systems/wiseorder-protocol/security/advisories/new). That divergence is the kind of finding the conformance suite exists to surface.
