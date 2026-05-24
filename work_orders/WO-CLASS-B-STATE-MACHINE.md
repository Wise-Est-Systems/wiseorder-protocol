# WO-CLASS-B-STATE-MACHINE

**Scope:** WiseOrder Protocol v0.2.0 only. v0.1.0 is frozen and is NOT touched.
**Status:** Draft. Spec patch proposed; applied to SPEC_LOCK_v0.2.0.md as §2.6.
**Authority requested:** Add subsection §2.6 to `SPEC_LOCK_v0.2.0.md`; declare invariants B4–B7; register reason codes; emit three v0.2.0 vectors and one pytest module.

## Problem

`SPEC.md` §3 Class B and `STATUS-REGISTRY.md` enumerate four statuses (`SUPPORTED`, `CONFLICTED`, `INSUFFICIENT_EVIDENCE`, `INVALID`) but the spec is silent on transitions. An external reviewer flagged that two conformant implementations could legally disagree on:

1. Whether `INSUFFICIENT_EVIDENCE` can upgrade to `SUPPORTED` when new evidence arrives.
2. Whether `CONFLICTED` can return to `SUPPORTED` once a contradiction is resolved.
3. Whether `INVALID` is terminal or merely a temporary state.

Silence here is a real conformance hole. Class B is the evidence-mutating class; without a transition rule, evidence-suppression attacks can be reframed as "the artifact moved to a different state."

## Proposed transition rules

Allowed:
- `INSUFFICIENT_EVIDENCE → SUPPORTED` when new affirming evidence raises the artifact above threshold AND no source contradicts the claim.
- `INSUFFICIENT_EVIDENCE → CONFLICTED` when new evidence introduces a contradiction with existing observations.
- `CONFLICTED → SUPPORTED` when the contradicting source is retracted with a recorded `transition_reason` AND the retraction itself is preserved (not deleted) in the artifact's prior-evidence chain.
- `SUPPORTED → CONFLICTED` when new contradicting evidence arrives.

Forbidden:
- Any transition out of `INVALID`. `INVALID` is terminal. The artifact MUST be re-issued under a new `vector_id`/`artifact_id`.
- `SUPPORTED → INSUFFICIENT_EVIDENCE` (evidence cannot un-arrive).
- Silent transitions (no `prior_status` and no `transition_reason`).
- `CONFLICTED → INSUFFICIENT_EVIDENCE` (resolution by deletion, not retraction; this would be an evidence-suppression attack).

## Artifact-version bump rule

Every state transition produces a new artifact carrying:
- `prior_status` — required for any artifact whose `status` was derived from a prior state.
- `transition_reason` — required, free-text PLUS a stable reason code.
- `prior_artifact_hash` — III hex of the prior artifact's canonical body (mirrors `consequence_proof` semantics from §2.2).

B2 (preserve contradictory evidence) extends to transitions: the prior state's evidence MUST remain inspectable through `prior_artifact_hash`, never overwritten.

## Terminal states

`INVALID` is terminal for v0.2.0 Class B. Consistent with `INVALID` in Classes A and C: structural failure, not a recoverable evidence state.

## New invariants

- **B4** — `INVALID` is terminal. A Class B artifact whose `prior_status` is `INVALID` MUST be rejected as `INVALID`.
- **B5** — Any Class B artifact whose `status != prior_status` MUST declare both `prior_status` and `transition_reason`. Absence is `INVALID`.
- **B6** — The set of allowed `(prior_status, status)` pairs is closed (enumerated in §2.6). Any pair outside the set is `INVALID`.
- **B7** — Transition artifacts MUST link to the prior artifact's canonical hash via `prior_artifact_hash`. Severed lineage is `INVALID`.

## Reason codes (stable strings)

Positive (allowed-transition codes, written by artifact author):
- `NEW_EVIDENCE_REACHED_THRESHOLD`
- `NEW_EVIDENCE_INTRODUCED_CONFLICT`
- `CONTRADICTING_SOURCE_RETRACTED`

Rejection (emitted by verifier on rejection):
- `INVALID_TERMINAL_TRANSITION`
- `TRANSITION_REASON_MISSING`
- `PRIOR_STATUS_MISSING`
- `DISALLOWED_STATE_TRANSITION`
- `PRIOR_ARTIFACT_HASH_MISSING`

## Deliverables

1. This document.
2. `work_orders/CLASS-B-STATE-MACHINE-spec-patch.md`.
3. `vectors/v0.2.0/class-b-transition-insufficient-to-supported.json`
4. `vectors/v0.2.0/class-b-transition-conflicted-to-supported.json`
5. `vectors/v0.2.0/class-b-transition-invalid-is-terminal.json`
6. `tests/test_class_b_state_machine.py`.

## Out of scope

- Implementing the new rules in `tools/minimal_verifier.py`. Verifier enforcement is xfail-gated until a follow-up work order.
- Authoring `schemas/vector.v0.2.0.schema.json`. UNKNOWN whether a separate schema lives in this work order or the next; flagged.
