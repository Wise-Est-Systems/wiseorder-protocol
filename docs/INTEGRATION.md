# INTEGRATION

How an external system integrates with `wiseorder-protocol`. What guarantees the protocol offers, what trust boundaries it crosses, what reproducibility it requires.

## What the protocol exposes

Three surfaces. Pick the one that matches your role.

### 1. CLI (`intellagent`) — for operators

The `intellagent` command is a self-contained state machine. Initialize a runtime directory, propose transitions, commit them, audit history, seal refusals.

```bash
intellagent init                                # create a runtime root
intellagent state --json                        # print current state
intellagent propose --file transition.json      # queue a proposal
intellagent transition <proposal_id>            # verify + (if action-bearing) authorize + commit
intellagent audit --json                        # walk the audit chain
intellagent refuse --query "..."                # seal an operator-initiated refusal
intellagent governed-run --work-order WO.md --dry-run    # parse + plan + validate a work order
```

Exit codes are stable:
- `0` — OK or REFUSED (both are legitimate outputs; per `INTELLAGENT-RUNTIME §14`).
- `1` — user error (e.g., not initialized).
- `2` — runtime in a bad state (`CHAIN_CORRUPT`, `STATE_TAMPERED`, `STATE_AUDIT_DIVERGENCE`).

### 2. Chain verifier — for external auditors

Any consumer who has a `.win` chain directory and the `intellagent_runtime` package (or the equivalent in Rust / Go) can verify the chain offline:

```bash
PYTHONPATH=/path/to/wiseorder-protocol python3 -c \
  "from pathlib import Path; from intellagent_runtime.chain import verify_chain; \
   print(verify_chain(Path('/path/to/chain')).status)"
```

Expected: `CHAIN_VALID`.

This is the **public-facing artifact**: a third-party verifier can carry the package + the `.win` files on a USB drive and re-derive every hash without network access. See `/Volumes/T7/2026-05-24/verify.sh` for the canonical example.

### 3. Conformance vector contract — for implementers

A second implementation that wants to claim conformance with WiseOrder v0.1.0 must pass every vector in `vectors/v0.1.0/`. Vectors are JSON files declaring an artifact + an expected status. An implementation:

1. Reads the JSON.
2. Computes the artifact's status per the protocol.
3. Reports `PASS` iff its computed status matches the vector's declared status.

Conformance is **class-scoped** (A/B/C/D). An implementation can claim conformance for a subset of classes; declare which in your `IMPLEMENTATIONS.md` registration.

The conformance harness is in `tools/run_conformance.py`. Implementations declare themselves in `IMPLEMENTATIONS.md` and provide a fixture manifest under `interop/`. The reference Python implementation reports `PASS` on 100% of v0.1.0 vectors.

## Trust boundaries

| boundary | guarantee |
|---|---|
| **The chain itself** | Content-addressed. Every triple's `consequence_proof` is `III(canonical_json(body \ {consequence_proof}))`. Every triple's `previous_action` is `III(canonical_json(prior triple body))`. Tampering with any byte of any triple breaks the chain on the next `verify_chain` call. |
| **The verifier source code** | Open. The Python verifier in this repo is the reference. The Rust + Go verifiers (`rust_verifier/`, `go_verifier/`) are first-party independent tracks — different language, different team-time, same algorithm. They must produce byte-identical output for any input. |
| **The signing key** | Not yet a concept. The chain is integrity-protected by hash, not by signature. Identity-bound signing (Ed25519 attester KIDs in Class C) is a separate boundary in `vectors/v0.2.0/class-c-*.json`; it does not cover the chain triples themselves. |
| **The runtime root** | An attacker with file-system access to `intellagent_state/`, `intellagent_audit/`, or `intellagent_objects/` can tamper. Detection is at next read (`StateTampered`, `ChainCorrupt`). Recovery requires a known-good snapshot. |
| **Untrusted JSON input** | Validated by typed schemas at load time. `TransitionSchemaError` and `PolicySchemaError` are raised loudly, not swallowed. Unknown fields are tolerated (forward-compatible); known fields with wrong types are rejected. |

## Reproducibility expectations

A conformant implementation MUST:

1. Produce **byte-identical canonical JSON** for any input. Canonical JSON in this protocol = sorted keys + compact separators (`","` and `":"`) + UTF-8 + no extra whitespace + non-ASCII preserved.
2. Produce **byte-identical III (= WiseDigest-3) hashes** for any input. The reference implementation is in `wop/src/wise/digest_v3.py`; this repo's `intellagent_runtime/iii.py` is a byte-identical mirror.
3. Match the **3 frozen v0.1.0 fingerprints** (vectors_suite, manifests_suite, corpus). Divergence on any of the three is a non-conformance.
4. Replay the audit chain deterministically given a fixed clock + fixed ID generator. See `intellagent_runtime/canonical.set_clock(...)` and `canonical.set_id_fn(...)`.

## Failure semantics an integrator must accept

- **Refusals are sealed, not retried.** A kernel-failed or gate-denied transition becomes part of the next refusal's `challenge_surface`. There is no automatic retry path; the operator re-proposes after fixing the underlying issue.
- **No rollback.** A sealed triple cannot be deleted, edited, or reordered. Withdrawing a prior statement is by appending a new triple whose `statement` documents the withdrawal.
- **`apply_transition` is crash-safe.** Process death between `stage_entry` and `store.save` leaves an orphan staging file that is discarded on next startup; process death between `store.save` and `finalize_staged` leaves a stageable entry that the reconciler renames. State and audit cannot diverge across crash boundaries. Proven by 3 SIGKILL tests.
- **External-validation status is `NOT_COMPLETE`.** The Rust + Go verifiers are first-party independent tracks. A third party submitting a verifier per `docs/release/THIRD_PARTY_VERIFIER_BRIEF_v0.1.md` would change this status.

## Operational assumptions

The protocol assumes:
- Python 3.11+ for the reference implementation (the same applies to the operational runtime).
- A POSIX-compatible file system for `os.rename` to be atomic on the same volume (used by the staging→finalize rename).
- WiseDigest-3 collision resistance is **assumed but not externally validated**. The math is in `wop/research/WiseDigest-3.md`; cryptanalysis is `not yet complete`. Production use against an adversary with multi-year compute budgets requires that analysis.
- `tools/os_isolation_runtime/` (used by `governed-run --execute`) relies on macOS `sandbox-exec` semantics. Linux users get a stricter `bwrap` equivalent if available; bare-Linux without bubblewrap falls back to a no-isolation warning.

## What this protocol does NOT provide for integration

- **No network endpoint.** The runtime is a CLI + filesystem state. Wrap it yourself if you need an HTTP surface (the `wiseorder` operational runtime is one such wrapper).
- **No SDK.** The CLI is the surface. Library use is allowed (`from intellagent_runtime.chain import verify_chain`) but the import path is not a stable API contract; the CLI is.
- **No authentication on the chain.** Anyone who can read the `.win` files can verify them. There is no authorization to *read*; there is also no authorization to *write* without runtime root access.
- **No multi-tenancy.** One runtime root directory = one independent chain. Two runtimes in two directories have two independent chains with two `NULLASIGN` geneses.
- **No registry of conforming implementations on the public internet.** `IMPLEMENTATIONS.md` is the local registry. Cross-implementation trust depends on each party verifying each other's chain offline.

If your integration needs any of those, build them on top — the protocol surface is stable enough to wrap.
