# SPEC_LOCK v0.1

**Status:** Frozen reference semantics for WiseOrder Protocol v0.1.0.
**Adopted:** 2026-05-10
**Authority:** This document, together with `SPEC.md` v0.1.0 and the published vector suite at `vectors/`, defines the immutable reference semantics for protocol version `0.1.0`.
**Successor policy:** Any change that alters semantics under this lock REQUIRES a protocol version increment. Implementations declaring `version: "0.1.0"` MUST satisfy this lock unchanged.

---

## 1. Purpose

This document freezes WiseOrder Protocol v0.1.0 against semantic drift. After this date, the surfaces enumerated below MUST NOT be re-interpreted, re-defined, or re-scoped under the version label `0.1.0`. Any semantic-breaking change to a frozen surface REQUIRES a new version label (`0.2.0`, `1.0.0`, etc.) and a corresponding new lock document.

The lock is structural: it names what is frozen, where the canonical text lives, and how the vector suite proves the freeze.

---

## 2. Frozen Surfaces

The following surfaces are immutable under version `0.1.0`:

### 2.1 Primitives
- **Canonicalization scheme:** RFC 8785 JSON Canonicalization Scheme (JCS), declared as `"canonicalization": "RFC8785-JCS"`.
- **Hash algorithm:** SHA-256, declared as `"algorithm": "SHA-256"`.
- **Digest format:** `sha256:<lowercase-hex>` (64 hex characters).
- **Timestamp format:** ISO 8601 with explicit `Z` UTC suffix.
- **Vector ID format:** `^[a-z0-9][a-z0-9-]*$` matching filename stem under `vectors/`.

Reference: `SPEC.md` §4 (Canonical Serialization), `schemas/vector.schema.json`.

### 2.2 Invariants
All invariants enumerated in `SPEC.md` v0.1.0 are frozen. By identifier:

- **A1, A2, A3** — Class A deterministic verification.
- **B1, B2, B3** — Class B evidence preservation and ordering.
- **C1, C2, C3, C4** — Class C consensus rules and quorum semantics.
- **D1, D2, D3, D4, D5** — Class D conduct artifact requirements.
- **CS1, CS2, CS3** — Canonicalization scheme declaration.
- **CC1, CC2, CC3, CC4** — Commit-chain semantics (preimage requirement, dependency ordering, completeness, audit ordering).
- **AG1, AG2, AG3** — Action governance separation.
- **ID1, ID2, ID3** — Implementation declaration semantics.

Each invariant is referenced verbatim in `SPEC.md` and exercised by at least one vector in `vectors/` whose `vector_id` is recorded in `reports/conformance-report.json` under `vectors_suite_sha256`.

### 2.3 Class Taxonomy
The four-class epistemic taxonomy is frozen. No fifth class MAY be added under v0.1.0.

- **Class A** — Deterministic Verification.
- **Class B** — Instrumented Empirical Verification.
- **Class C** — Protocol-Bound Consensus.
- **Class D** — Interpretive Governance.

Per-class allowed statuses are frozen in `STATUS-REGISTRY.md` and enforced structurally by `schemas/vector.schema.json`. Telemetry tokens (`CALIBRATION_IMPROVED`, `CALIBRATION_DEGRADED`) are NOT per-claim statuses and MUST be rejected when used as such.

### 2.4 Replay Semantics
A conformant implementation MUST satisfy the following replay properties for v0.1.0:

- **Determinism:** Identical canonicalized input MUST produce identical verdict and identical artifact bytes (mod implementation-declared non-content fields).
- **Suite fingerprint:** The vector suite fingerprint at the moment of this lock is `sha256:6168d2075931baa98bba763f9cd537142554aae7b26f19e3e93a60de2ee5bb0f` over 33 vectors (23 baseline + 10 adversarial).
- **Canonicalization corpus fingerprint:** `sha256:c95685bff48c15abc313c462908b05ac309250bc660c2d802ae51af5a8038b09` over 10 corpus entries.
- **Interop manifests fingerprint:** `sha256:74eaaa62271f23172232bda43ba3340543e66c46ba1e2f5e6da18d3447a6ba29` over 3 manifests.

Any future v0.1.0 implementation MUST reproduce these fingerprints byte-for-byte. A divergence is a non-conformance, not a version bump.

### 2.5 Refusal Semantics
- A refusal is a structurally valid protocol outcome and MUST be recorded as such.
- A `RefusalRecord` (per `INTELLAGENT-RUNTIME.md` and `intellagent_runtime/refusal.py`) MUST be sealed on emission.
- A refusal MUST NOT be promoted to `VERIFIED`, `CONSENSUS_VALID`, or `CONDUCT_VALID`.
- Refusal evidence MUST be retained in the audit memory chain.

### 2.6 Conformance Semantics
- **Class-scoped:** Conformance is declared per-class via Implementation Declaration. The token `PARTIALLY CONFORMANT` is NOT a protocol status.
- **Vector-determined:** The published vector suite at `vectors/` determines conformance for v0.1.0. Prose explains; vectors decide.
- **Self-declaration limit:** An implementation declaring conformance is not externally validated. External validation REQUIRES a non-first-party implementation reproducing vector outputs (see `IMPLEMENTATION_TRACKER.md`).

### 2.7 Lifecycle Semantics
- **Authorization:** Verification status MUST NOT auto-authorize action. Action requires a separately declared `authorization_source`.
- **Commit chain:** Stages MUST monotonically increase in `stage` and `created_at`; `depends_on` MUST reference the literal prior stage hash; preimage `content` MUST be present (CC1).
- **Process vs integrity:** Process proof and integrity proof are independent. Neither implies the other.

---

## 3. Frozen Artifacts

The following published artifacts are frozen as the v0.1.0 reference set:

| Artifact | Path | Hash anchor |
|---|---|---|
| Specification text | `SPEC.md` | committed to repository |
| Status registry | `STATUS-REGISTRY.md` | committed |
| Schemas | `schemas/*.json` | committed |
| Vector suite | `vectors/*.json` | `vectors_suite_sha256` |
| Canonicalization corpus | `canonicalization/corpus/`, `canonicalization/golden/` | `corpus_sha256` |
| Conformance report | `reports/conformance-report.json` | self-hashed |
| Interop manifests | `interop/fixtures/`, `interop/reports/` | `manifests_suite_sha256` |

The vector suite MAY grow under v0.1.0 ONLY if every existing vector retains its verdict and its `sha256` byte-for-byte. Adding hostile/adversarial vectors is allowed; modifying or removing existing ones is NOT.

---

## 4. Version-Increment Rule

A new protocol version label is REQUIRED if any of the following occur:

1. An invariant is added, removed, or its semantics altered.
2. A status token is added, removed, or redefined.
3. A class is added, removed, or its boundary altered.
4. The canonicalization scheme or hash algorithm is changed.
5. A required artifact field is added, removed, or renamed.
6. The commit-chain dependency rule is altered.
7. The action-governance separation (AG1–AG3) is weakened in any direction.
8. Any existing vector's expected verdict changes.

Editorial corrections that do NOT alter semantics (typos, formatting, clarifying prose that does not change the rule) MAY be applied under v0.1.0 without a version bump, PROVIDED:
- The vector suite fingerprint is unchanged.
- The canonicalization corpus fingerprint is unchanged.
- No structural schema change is required.

If any of those three properties would change, the change is semantic and REQUIRES a version increment.

---

## 5. Successor Document

When a future version (`0.2.0` or higher) is adopted, a new `SPEC_LOCK_v<X.Y>.md` MUST be written. The successor MUST enumerate which v0.1.0 surfaces it preserves, modifies, or removes. v0.1.0 implementations MUST continue to satisfy this lock; they are not retroactively invalidated by a successor.

---

## 6. Limitations of This Lock

This lock does NOT guarantee:

- That the protocol is correct.
- That implementations are honest.
- That the threat model is complete.
- That the surfaces frozen here are sufficient.

It guarantees only that the surfaces named above will not be silently re-interpreted under the label `0.1.0`. The protocol's correctness is established by independent implementation, hostile review, and operational use over time — none of which this lock alone provides.

---

## 7. Authoritative Reference

In case of conflict between this document and `SPEC.md` v0.1.0, `SPEC.md` governs the prose semantics and the vector suite governs the operational semantics. This document is a freeze record; it does not redefine.
