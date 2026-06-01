# STRUCTURE.md — Wise.Est Systems Canonical Stack

**Status:** canonical. This file is the authoritative map of the Wise.Est Systems public repository structure.

> **Drift control:** every public repo in the stack carries a `STACK_ROLE.md` declaring its layer and non-goals. The SHA-256 fingerprint of each `STACK_ROLE.md` is recorded below. CI in each repo verifies that its local `STACK_ROLE.md` matches the fingerprint here. Any change to a repo's role is a pull request against this file.

## Layers

The public stack has four layers and four canonical repos. Internal tooling and pre-canonical experiments are not part of the public stack and are not listed here.

| layer | repo | role | license |
|---|---|---|---|
| kernel | [wiseorder-protocol](https://github.com/Wise-Est-Systems/wiseorder-protocol) | governance kernel: spec, audit chain, conformance vectors, reference verifiers | Apache-2.0 |
| runtime | [wiseorder](https://github.com/Wise-Est-Systems/wiseorder) | operational runtime: commit → summarize → approve | Apache-2.0 |
| implementation | [winstack-network](https://github.com/Wise-Est-Systems/winstack-network) | `.win` production implementation: Rust crates, WASM verifier, desktop drop | MIT |
| research | [wop](https://github.com/Wise-Est-Systems/wop) | WISEATA primitives + WiseDigest-3 + cryptanalysis fleet | Apache-2.0 |

## Fingerprints

Each row below is the canonical SHA-256 of the named `STACK_ROLE.md` file. The verifier in `tools/verify_stack.py` checks every published `STACK_ROLE.md` against these values.

| repo | path | sha256 |
|---|---|---|
| wiseorder-protocol | `STACK_ROLE.md` | `3e47a4390ac898e8e099d28a14d785f33363c2b7bb5ec9ad7641f23c61363e7f` |
| wiseorder | `STACK_ROLE.md` | `74f57e74f04156d498412fde13203b81c0578aee57ba1819a928d092716391e2` |
| winstack-network | `STACK_ROLE.md` | `4b2064b9bca1a8a9fe850d563929801290457338297582d4db3b2afa1c7db9c9` |
| wop | `STACK_ROLE.md` | `21c81afd243c77ed7b1804e581ca28c0ebf72238a490dbf1401378789592b182` |

## Non-canonical repos

Every other repo under `Wise-Est-Systems` is one of:

- **Archived predecessor** — carries an explicit `archive: superseded by ...` commit; not part of the canonical stack. Current examples (May 2026): `winstack`, `winstack-integrity`, `win`.
- **Pre-canonical experiment** — predates the v0.1 stack lock; not maintained. Current examples: `wisernance`, `winstack-truthlock`, `win-proof-feed` (Feb 2026), `wisest-systems` (Apr 2026).
- **Org profile** — `Wise-Est-Systems/.github`, holds the organization-level README.

Implementations under construction in private repos or local-only directories are not part of the public stack and are not listed.

## Drift control mechanism

1. Each canonical repo carries `STACK_ROLE.md` at its root.
2. Each canonical repo runs `.github/workflows/verify-stack-role.yml` on every push.
3. The workflow fetches the canonical fingerprint from this file (via GitHub raw) and compares it against the local `STACK_ROLE.md` hash.
4. Mismatch fails CI. Resolution is either reverting the local change or opening a pull request against this file updating the fingerprint.
5. `tools/verify_stack.py` runs the same check across all canonical repos in one pass — used in this repo's CI and ad-hoc.

This is the kernel pattern applied to organizational structure: spec + fingerprint + verifier.

---

**Last updated:** 2026-06-01
**Spec rev:** v1.0
