# SPEC.md — Reader's Guide

This document is a 60-second guide to [`SPEC.md`](./SPEC.md). It is not normative. [`SPEC.md`](./SPEC.md) is the contract.

## The protocol in two sentences

WiseOrder Protocol classifies any artifact-bearing claim into one of four verification regimes — **A** (deterministic), **B** (statistical), **C** (protocol-bound consensus), **D** (conduct) — and enforces that the claim's *form* matches its declared regime before any committed action can occur. Authorization is a **separate gate** from kernel verification, so the same transition can be kernel-passed and gate-denied; both outcomes — and every refusal — are sealed in the same hash-chained audit memory.

## What the spec covers

| Section | What's inside |
|---|---|
| §1 Kernel Laws | The two non-negotiable laws (Truth Governance, Action Governance). |
| §3 Epistemic Classes | Four classes (A/B/C/D), one verification regime each, fixed status tokens. |
| §4 Canonical Serialization | The byte-deterministic form every implementation must produce. |
| §5 Commit-Chain Semantics | The hash-linked audit chain (commitments + refusals). |
| §6 Proof Separation | Integrity proof ≠ process proof ≠ authorization. Each is required separately. |
| §7 Action Governance | Verification permits action; action is always governed; nothing is automatic. |
| §8 Threat Model | What the kernel is required to detect, and what it explicitly does not. |
| §10 Artifact Schemas | Canonical JSON shape per class. |
| §11 Conformance | The vector set every implementation must pass. |
| §14 Non-Goals | What this protocol is not. Read this before anything else if you are skeptical. |

## What the protocol explicitly does NOT do

- It does not implement cryptography. It consumes SHA-256 + Ed25519 + the WiseDigest family from [`wop`](https://github.com/Wise-Est-Systems/wop). Cryptanalysis of those primitives is published as `NOT_COMPLETE`.
- It does not itself act. The kernel governs the *form* a claim must take; substantive correctness of the claim is a different layer (the proposer's responsibility).
- It does not provide moral judgment. Class D artifacts receive `CONDUCT_VALID` if their structure is admissible. The substance of right conduct lives in policy and in operator review, not in the kernel.
- It does not require a network or a server. The runtime is single-host with no outbound HTTP in the core verification path.
- It does not claim external validation. Verifier tracks are first-party until a third party publishes a verdict.

## Why this might matter to a receiver

A receiver opening an AI-assisted artifact today has two choices: trust the platform showing it, or compare hashes by hand. Neither survives a file moving through email, Slack, or an AI pipeline. WiseOrder gives the receiver a third option — verify the artifact's class-scoped admissibility offline against a published spec, with two independent reference verifiers (Go and Rust) as the agreement baseline. If the verifiers disagree on any fingerprint, the spec itself is the bug, not the implementations.

## Where to go next

| If you want… | Read |
|---|---|
| The full normative text | [`SPEC.md`](./SPEC.md) |
| The conformance vectors | [`vectors/`](./vectors/) and [`CONFORMANCE.md`](./CONFORMANCE.md) |
| The reference verifiers | [`go_verifier/`](./go_verifier/), [`rust_verifier/`](./rust_verifier/) |
| The runtime CLI | [`intellagent_runtime/`](./intellagent_runtime/) |
| The vulnerability path | [`SECURITY.md`](./SECURITY.md) — spec ambiguity is treated as a vulnerability class |
| The structural canon | [`STRUCTURE.md`](./STRUCTURE.md) — the org-wide repo map |
| The org-level overview | [Wise.Est Systems](https://github.com/Wise-Est-Systems) |

## A reading order suggestion

1. **`SPEC.md` §14 (Non-Goals)** — 90 seconds; tells you what this is not before you decide whether to read further.
2. **`SPEC.md` §1 (Kernel Laws)** — 60 seconds; the two laws every conformant implementation must honor.
3. **`SPEC.md` §3 (Epistemic Classes)** — 5 minutes; the four classes are the core abstraction.
4. **`SPEC.md` §8 (Threat Model)** — 3 minutes; what the kernel defends against and what it doesn't.
5. **`vectors/`** — pick any directory, look at the input and the expected output; that is what conformance looks like in practice.

Anything else in `SPEC.md` is supporting material to those four sections plus the vector set.
