---
canonical-name: wiseorder-protocol
layer: kernel
parent: Wise-Est-Systems
license: Apache-2.0
canon: https://github.com/Wise-Est-Systems/wiseorder-protocol/blob/main/STRUCTURE.md
---

# Role: Governance Kernel

`wiseorder-protocol` is the **governance kernel** of the Wise.Est Systems stack.

## What this repo IS

- The specification (`SPEC.md`, `SPEC_LOCK_v0.1.md`, `SPEC_LOCK_v0.2.0.md`) for class-scoped artifact verification across regimes A, B, C, and D.
- The append-only hash-chained audit memory and the `.win` triple chain anchored at a `NULLASIGN` genesis.
- The Python runtime (`intellagent_runtime/`) plus reference Go and Rust verifiers (`go_verifier/`, `rust_verifier/`).
- The conformance vectors (`vectors/`) that any implementation must pass to claim conformance.
- The canonical [`STRUCTURE.md`](./STRUCTURE.md) that names every public repo's layer and role.

## What this repo IS NOT

- A model. There is no neural network. Transformers serve as proposers under the kernel.
- A network service. The runtime is single-host with no outbound HTTP in the core path.
- A claim of externally validated cryptography. Verifier tracks are first-party; external audit status is published per release in `audit_bundle_v0.1/`.
- A general workflow engine.

## Drift policy

Any change to this file MUST be accompanied by an update to the `wiseorder-protocol` row in [`STRUCTURE.md`](./STRUCTURE.md). CI verifies the fingerprint on every push.
