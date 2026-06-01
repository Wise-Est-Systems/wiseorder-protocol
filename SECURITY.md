# Security policy

## Reporting a vulnerability

Do **not** open a public issue for anything that could let an attacker forge a `VERIFIED` outcome, bypass the audit chain, or evade kernel verification. Use one of:

- **GitHub Security Advisories** — preferred. Open a private advisory at <https://github.com/Wise-Est-Systems/wiseorder-protocol/security/advisories/new>.
- **Email** — `security@truth.systems` (PGP-encrypted preferred; fingerprint published in release notes per major version).

Include enough information to reproduce: version or commit SHA, platform, the minimal artifact set (spec excerpt, conformance vector, audit chain segment, or runtime command), a reproducer, and your impact assessment.

We will:

1. Acknowledge receipt within **two business days**.
2. Assign a severity using CVSS v3.1 and a triage owner within **five business days**.
3. Provide a remediation plan, expected fix window, and disclosure timeline.

## Disclosure window

Default coordinated-disclosure window is **90 days** from the initial report. We will request an extension if (and only if) a fix demands more time, and we will communicate the new date in writing. Reporters may publish at the end of the agreed window.

## Scope

In scope:

- The specification (`SPEC.md`, `SPEC_LOCK_v0.1.md`, `SPEC_LOCK_v0.2.0.md`) — including any ambiguity that admits divergent conforming implementations.
- The conformance vectors (`vectors/`) — including any vector that does not reflect the spec's stated semantics.
- The canonicalization corpus (`canonicalization/`) — including any byte sequence the spec covers ambiguously.
- The audit memory and `.win` chain (`chain/`) — including any way to commit a transition that the spec forbids, or to construct a chain segment that re-verifies as valid after tampering.
- The reference verifiers (`go_verifier/`, `rust_verifier/`, `intellagent_runtime/`) — including any input that causes one verifier to disagree with another on the same fingerprint.
- The CLI (`intellagent`) — including any flag combination that bypasses kernel verification.
- The refusal store — including any way to commit a transition that should have been refused, or to suppress a refusal record.

Out of scope:

- Cryptographic primitives — handled by [`wop`](https://github.com/Wise-Est-Systems/wop) (WiseDigest family) and platform SHA-256. Vulnerabilities in primitives should be reported to those projects.
- The `.win` container format and offline verifier — handled by [`winstack-network`](https://github.com/Wise-Est-Systems/winstack-network).
- Issues that require an already-compromised operator account or already-compromised signing keys.
- Misuse of the local CLI by the operator running it.
- Third-party model providers used as proposers under the kernel.

## Threat model

The kernel MUST detect:

| Attack                                                                          | Expected outcome |
|---------------------------------------------------------------------------------|------------------|
| A proposal that violates a class invariant for its declared regime              | Kernel rejection; refusal sealed |
| A transition that mutates an immutable field declared in the spec               | Kernel rejection; refusal sealed |
| A class-D candidate without `alternatives`, `challenge_surface`, or `commit_chain` | Kernel rejection; refusal sealed |
| Replay of a previously-committed transition                                     | Audit-chain mismatch on the prior-state digest |
| Tampering with any committed transition's fields                                | Audit-chain re-verification fails |
| Forging a chain segment that re-verifies as valid                               | Cross-implementation disagreement (Go ↔ Rust ↔ Python) on the same fingerprint |
| Reordering transitions in the audit chain                                       | Prior-state digest chain breaks at the point of reorder |
| Skipping a refusal record after a kernel rejection                              | Refusal-store / audit-chain consistency check fails |
| Canonicalization disagreement between conforming implementations                | Conformance vector regression in CI |

The kernel does **not** defend against:

- A model proposer that lies about its inputs (the kernel governs the *form* of a proposal; the substantive content's correctness is the proposer's responsibility).
- A operator who runs `intellagent` with `--allow-unsafe` flags that the spec explicitly marks as bypassing kernel checks.
- An attacker who controls both the proposer and the operator (they can commit any spec-conformant transition; that is by design).
- Side-channel attacks on the host running the runtime.
- Filesystem corruption that flips bytes in the audit chain identically to flipping bytes in its prior-state record.
- Resource-exhaustion attacks on the runtime via maliciously large proposal payloads — partially mitigated by per-class size bounds, but not fully out-of-scope-of-host.

## Spec ambiguity is a vulnerability

The spec is the contract. Any ambiguity that admits two conforming implementations producing different `VERIFIED` / refusal outcomes for the same input is a security issue under this policy, not a documentation issue. Report it via the same vulnerability path.

## Conformance vector integrity

The conformance vector set (`vectors/`) is normative. Any change that would alter a published vector requires:

1. A new minor version of the spec.
2. An entry in `CHANGELOG.md`.
3. Updated status in `STATUS-REGISTRY.md`.
4. Re-running both reference verifiers against the new set.

A change to a published vector without these steps is itself a security issue. Conformance drift is a vulnerability class.

## Cryptographic agility

Hashing and canonicalization primitives live in [`wop`](https://github.com/Wise-Est-Systems/wop) and the host platform. The kernel does not itself implement cryptography; it consumes it. Algorithm migration is coordinated across `wop` and this repo via paired releases.

## External validation status

Per `audit_bundle_v0.1/` and the org-level discipline statement: verifier tracks in this repo are **first-party**. External audit status for each release is published as `NOT_COMPLETE` or `COMPLETE` in the release packet. We do not call first-party verification "externally validated."
