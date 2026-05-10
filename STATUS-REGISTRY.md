# Status Registry

> Focused extract of `SPEC.md` §9. In case of any discrepancy with `SPEC.md`, **`SPEC.md` governs.**

WiseOrder statuses are **class-scoped**. The same token (e.g. `INVALID`) may be reachable from multiple classes, but its semantics are determined by the class of the artifact emitting it. Every artifact MUST declare its class; consumers MUST resolve status meaning through class context.

---

## Class A — Deterministic Verification

| Status     | Meaning                                                                  |
| ---------- | ------------------------------------------------------------------------ |
| `VERIFIED` | Canonicalized bytes reproduced the declared digest.                       |
| `TAMPERED` | Canonicalized bytes did not reproduce the declared digest.                |
| `INVALID`  | The artifact itself is structurally invalid (missing fields, bad scheme). |

---

## Class B — Instrumented Empirical Verification

| Status                  | Meaning                                                                  |
| ----------------------- | ------------------------------------------------------------------------ |
| `SUPPORTED`             | Declared evidence sources affirm the claim with no contradicting record. |
| `CONFLICTED`            | Evidence sources disagree; contradiction MUST be preserved.              |
| `INSUFFICIENT_EVIDENCE` | Available evidence does not reach the threshold to support or refute.    |
| `INVALID`               | The artifact itself is structurally invalid.                             |

---

## Class C — Protocol-Bound Consensus

| Status              | Meaning                                                                                |
| ------------------- | -------------------------------------------------------------------------------------- |
| `CONSENSUS_PENDING` | Quorum not yet met, but the consensus process is open and proceeding.                  |
| `CONSENSUS_VALID`   | Required quorum was reached under declared rules with eligible attesters.              |
| `CONSENSUS_FAILED`  | The consensus process closed without reaching the required quorum.                     |
| `INVALID`           | The artifact itself is structurally invalid (missing protocol declaration, etc).       |

---

## Class D — Interpretive Governance

| Status            | Meaning                                                                                            |
| ----------------- | -------------------------------------------------------------------------------------------------- |
| `CONDUCT_VALID`   | All required conduct fields present, commit-chain intact, preimages included, alternatives surfaced. |
| `CONDUCT_INVALID` | Conduct artifact missing required fields, broken commit-chain, or missing preimages.               |

A Class D artifact MUST NOT receive `VERIFIED` status (D4).

---

## Telemetry (NOT per-claim status)

The following are system-level telemetry and MUST NOT be emitted as artifact `status` values:

- `CALIBRATION_IMPROVED`
- `CALIBRATION_DEGRADED`

These describe the implementation's calibration trajectory over time, not the truth state of any single claim.

---

## What is NOT a status

- `PARTIALLY CONFORMANT` is **not** a protocol status. Conformance is class-scoped and declared via Implementation Declaration. See `CONFORMANCE.md`.
- "Authorized" / "permitted" / "executable" are **not** statuses. Verification status MUST NOT automatically authorize execution (AG1).
