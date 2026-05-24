# Proposed patch to `SPEC_LOCK_v0.2.0.md`

**Insert as new subsection §2.6, immediately after §2.5 (Class D commit-stage preimage size cap) and before §3 (v0.1.0 Coexistence).**
**Reviewer applies; this file is a proposal only.**

---

### 2.6 Class B status transition rules (v0.2.0)

Under v0.1.0, Class B statuses (`SUPPORTED`, `CONFLICTED`, `INSUFFICIENT_EVIDENCE`, `INVALID`) were enumerated without a transition diagram. v0.2.0 closes this gap.

#### 2.6.1 Allowed transitions

| FROM                    | TO                      | Allowed? | Trigger                                                                                  |
| ----------------------- | ----------------------- | -------- | ---------------------------------------------------------------------------------------- |
| `INSUFFICIENT_EVIDENCE` | `SUPPORTED`             | yes      | New affirming evidence reaches threshold AND no source contradicts the claim.            |
| `INSUFFICIENT_EVIDENCE` | `CONFLICTED`            | yes      | New evidence introduces a contradiction with existing observations.                      |
| `CONFLICTED`            | `SUPPORTED`             | yes      | Contradicting source retracted with recorded `transition_reason`; retraction preserved.   |
| `SUPPORTED`             | `CONFLICTED`            | yes      | New contradicting evidence arrives.                                                       |
| `SUPPORTED`             | `INSUFFICIENT_EVIDENCE` | no       | Evidence cannot un-arrive; prior support remains audit-visible.                          |
| `CONFLICTED`            | `INSUFFICIENT_EVIDENCE` | no       | Reframes evidence-suppression as recovery; rejected.                                     |
| `INVALID`               | (any)                   | no       | Terminal. Re-issue under a new `vector_id`/`artifact_id`.                                |
| (any)                   | `INVALID`               | yes      | Structural failure of the new artifact (missing fields, broken lineage, forbidden transition). |

#### 2.6.2 Required transition fields

A Class B artifact whose `status` differs from a prior state MUST declare:

```json
{
  "prior_status": "<one of: SUPPORTED, CONFLICTED, INSUFFICIENT_EVIDENCE>",
  "transition_reason": {
    "code": "<one of the v0.2.0 reason codes>",
    "narrative": "<short prose explaining the trigger>"
  },
  "prior_artifact_hash": "<III hex of the prior artifact's canonical body>"
}
```

- `prior_status` MAY be `null` (or absent) if and only if the artifact is the first in its lineage. In that case `status` is derived solely from current evidence per `SPEC.md` §3 Class B, not from a transition.
- `transition_reason.code` MUST be one of the v0.2.0 reason codes (§2.6.4).
- `prior_artifact_hash` MUST be reproducible by re-canonicalizing the referenced prior artifact under §2.2.

#### 2.6.3 Invariants

- **B4** — `INVALID` is terminal. A Class B artifact whose `prior_status == "INVALID"` MUST be rejected as `INVALID` with reason `INVALID_TERMINAL_TRANSITION`.
- **B5** — Any Class B artifact whose `status != prior_status` MUST declare both `prior_status` and `transition_reason`. Absence is `INVALID` with reason `PRIOR_STATUS_MISSING` or `TRANSITION_REASON_MISSING`.
- **B6** — The set of allowed `(prior_status, status)` pairs is the four `yes` rows of §2.6.1 plus any pair whose `status` is `INVALID`. Any pair outside this set is `INVALID` with reason `DISALLOWED_STATE_TRANSITION`.
- **B7** — Transition artifacts MUST declare `prior_artifact_hash`. Severed lineage is `INVALID` with reason `PRIOR_ARTIFACT_HASH_MISSING`.

#### 2.6.4 Reason codes

These reason codes are stable v0.2.0 strings. Conformant verifiers MUST emit the rejection codes verbatim. Artifact authors MUST write one of the positive codes in `transition_reason.code` on any allowed transition.

Positive (allowed-transition codes, written by artifact author):

| Positive code                       | Triggered when                                          |
| ----------------------------------- | ------------------------------------------------------- |
| `NEW_EVIDENCE_REACHED_THRESHOLD`    | `INSUFFICIENT_EVIDENCE → SUPPORTED`                     |
| `NEW_EVIDENCE_INTRODUCED_CONFLICT`  | `INSUFFICIENT_EVIDENCE → CONFLICTED`, `SUPPORTED → CONFLICTED` |
| `CONTRADICTING_SOURCE_RETRACTED`    | `CONFLICTED → SUPPORTED`                                |

Rejection (emitted by verifier on rejection):

| Code                            | Triggered when                                                                       |
| ------------------------------- | ------------------------------------------------------------------------------------ |
| `INVALID_TERMINAL_TRANSITION`   | An artifact declares `prior_status == "INVALID"`.                                    |
| `TRANSITION_REASON_MISSING`     | `status != prior_status` but `transition_reason` is absent or `transition_reason.code` is empty. |
| `PRIOR_STATUS_MISSING`          | `status` was derived from a prior state but `prior_status` is absent.                |
| `DISALLOWED_STATE_TRANSITION`   | `(prior_status, status)` is not in the §2.6.1 allowed set and `status != "INVALID"`. |
| `PRIOR_ARTIFACT_HASH_MISSING`   | Transition artifact omits `prior_artifact_hash`.                                     |

#### 2.6.5 Evidence preservation (B2 extension)

B2 (preserve contradictory evidence) extends across transitions. A transitioning artifact MUST NOT delete or rewrite the evidence of its predecessor; the predecessor is recoverable via `prior_artifact_hash`. Mutation of prior evidence is `INVALID` with reason `DISALLOWED_STATE_TRANSITION` (treated as a transition the diagram does not allow: from an authentic prior state to a forged one).

#### 2.6.6 v0.1.0 unaffected

This subsection applies to v0.2.0 only. v0.1.0 Class B artifacts continue to operate under `SPEC.md` v0.1.0 §3 without transition fields; `SPEC_LOCK_v0.1.md` is unchanged.
