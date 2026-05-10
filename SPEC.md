# WiseOrder Protocol v0.1.0

**Status:** Draft Canon
**Owner:** Wise.Est Systems
**Adopted:** 2026-05-06
**Architecture status:** Locked unless implementation reality breaks it.

> **Governance Kernel for Epistemic Systems**
>
> **Core sentence:** WiseOrder governs how cognition becomes consequence.

---

## Abstract

WiseOrder Protocol defines a protocol layer for classifying claims, assigning verification regimes, governing action, producing auditable epistemic artifacts, and preserving uncertainty before cognition affects reality.

WiseOrder is not a model, chatbot, or runtime. It is an epistemic protocol.

WiseOrder separates:

- reasoning
- verification
- authorization
- execution

---

## 1. Kernel Laws

**Law 1 — Truth Governance**
When truth can be verified, verify it.
When truth cannot be verified, govern the conduct that produced the judgment.

**Law 2 — Action Governance**
Verification permits action.
Action is always governed.
A conformant implementation MUST NOT treat `VERIFIED`, `CONSENSUS_VALID`, `CONDUCT_VALID`, valid hashes, valid signatures, or valid attestations as automatic execution authorization.

---

## 2. Terminology

**Claim** — A structured assertion regarding state, provenance, interpretation, authorization, consequence, execution, policy, or reality.

**Verification Regime** — A protocol-defined method for evaluating claims belonging to a specific epistemic class.

**Integrity Proof** — Cryptographic proof that an artifact has not changed since sealing. Integrity proof does NOT imply process correctness, authorization, strategic correctness, or conduct validity.

**Process Proof** — Protocol evidence that an artifact was produced according to required governance constraints and ordering semantics. Process proof does NOT imply truth.

**Conduct Artifact** — A Class D artifact containing values commitments, excluded optimizations, alternatives, reasoning lineage, challenge surfaces, reversibility analysis, calibration references, and commit-chain proof. A conduct artifact MAY receive `CONDUCT_VALID`. A conduct artifact MUST NOT receive `VERIFIED`.

---

## 3. Epistemic Classes

### Class A — Deterministic Verification

Claims whose truth value can be mechanically reproduced under identical inputs.

Examples:

- file integrity
- canonical serialization validation
- signature validity
- append-only lineage

Allowed statuses:

- `VERIFIED`
- `TAMPERED`
- `INVALID`

Invariants:

- **A1:** A conformant implementation MUST produce identical verification results under identical canonical byte inputs.
- **A2:** A Class A artifact MUST contain canonicalization scheme, hash algorithm, expected digest, and observed digest.
- **A3:** Class A verification MUST operate on canonicalized bytes only.

---

### Class B — Instrumented Empirical Verification

Claims supported through logs, receipts, APIs, timestamps, execution traces, structural observations, or instrumentation.

Truth MAY remain uncertain.
Evidence MUST remain inspectable.

Allowed statuses:

- `SUPPORTED`
- `CONFLICTED`
- `INSUFFICIENT_EVIDENCE`
- `INVALID`

Invariants:

- **B1:** A Class B artifact MUST declare all evidence sources explicitly.
- **B2:** A conformant implementation MUST preserve contradictory evidence if encountered.
- **B3:** Class B evidence ordering MUST remain auditable.

---

### Class C — Protocol-Bound Consensus

Claims whose validity depends on a protocol-defined attestation process.

A conformant implementation MUST NOT interpret "consensus" as informal agreement among parties. A claim achieves Class C validity if and only if the required attesters, the declared quorum, the declared attestation semantics, and the declared protocol rules are all satisfied.

Allowed statuses:

- `CONSENSUS_PENDING`
- `CONSENSUS_VALID`
- `CONSENSUS_FAILED`
- `INVALID`

Invariants:

- **C1:** Consensus rules MUST be declared before attestation collection begins.
- **C2:** A conformant implementation MUST reject attestations from unauthorized participants.
- **C3:** Consensus validity MUST NOT imply execution authorization.
- **C4:** Consensus artifacts MUST preserve quorum semantics as auditable metadata.

---

### Class D — Interpretive Governance

Claims whose truth cannot be mechanically or empirically verified.

Examples:

- strategy
- ethics
- prioritization
- aesthetics
- interpretation
- political judgment

A conformant implementation MUST NOT emit `VERIFIED` for a Class D claim. A conformant implementation MUST govern such claims via the conduct-artifact requirements below; a Class D claim is admissible only if the artifact satisfies the required conduct fields and invariants.

Allowed statuses:

- `CONDUCT_VALID`
- `CONDUCT_INVALID`

Required conduct fields:

- `values_frame`
- `excluded_optimizations`
- `alternatives_considered`
- `reasoning_lineage`
- `challenge_surface`
- `reversibility_analysis`
- `calibration_reference`
- `commit_chain_proof`

Invariants:

- **D1:** A Class D artifact MUST expose what it optimized for and what it explicitly refused to optimize for.
- **D2:** A conformant implementation MUST generate at least one defensible alternative.
- **D3:** A conformant implementation MUST include explicit self-generated counterarguments.
- **D4:** A Class D artifact MUST NOT receive `VERIFIED` status.
- **D5:** Class D commit stages MUST include preimage content.

---

## 4. Canonical Serialization

WiseOrder Protocol v0.1.0 adopts **RFC 8785 JSON Canonicalization Scheme (JCS)** for all Class A integrity operations. A v0.1.0 implementation MUST declare canonicalization as the literal string `"RFC8785-JCS"` and MUST reject any other declared scheme as `INVALID`.

A successor protocol version MAY register additional canonicalization schemes. v0.1.0 implementations MUST NOT honor schemes registered by successor versions.

Invariants:

- **CS1:** Class A artifacts MUST declare canonicalization scheme and hash algorithm.
- **CS2:** Digest generation MUST operate on canonicalized bytes.
- **CS3:** Verification MUST use the artifact-declared canonicalization scheme.

Required declaration:

```json
{
  "canonicalization": "RFC8785-JCS",
  "algorithm": "SHA-256"
}
```

---

## 5. Commit-Chain Semantics

**Purpose:** prevent post-hoc rationalization.

Each conduct stage MUST cryptographically commit to prior stages.

Stage format:

```json
{
  "stage": 1,
  "name": "values_frame_commit",
  "hash": "sha256:<hex>",
  "content": {},
  "depends_on": null,
  "created_at": "ISO-8601 UTC"
}
```

Invariants:

- **CC1:** A hash without its preimage MUST be treated as unauditable.
- **CC2:** Later stages MUST declare dependency on prior stage hashes.
- **CC3:** Missing commit stages MUST invalidate process proof.
- **CC4:** Commit ordering MUST remain externally auditable.

---

## 6. Proof Separation

WiseOrder separates **process proof** from **integrity proof**.

**Process Proof** demonstrates:

- governance ordering
- protocol adherence
- conduct structure
- commitment sequencing

**Integrity Proof** demonstrates:

- artifact immutability
- post-seal integrity
- byte preservation

Neither proof type implies the other.

---

## 7. Action Governance

Invariants:

- **AG1:** Verification status MUST NOT automatically authorize execution.
- **AG2:** Execution authorization MUST remain separately governable.
- **AG3:** A conformant implementation MUST preserve execution policy, execution rationale, and authorization source as auditable metadata.

---

## 8. Threat Model

**Threat D-1 — Post-Hoc Rationalization**
A system generates conclusions first and fabricates values afterward.
*Mitigation:* commit-chain dependency ordering with preimage inclusion.

**Threat D-2 — Performative Challenge Surfaces**
A system generates weak counterarguments purely for compliance appearance.
*Mitigation:* sampled external audits.

**Threat C-1 — Unauthorized Consensus Participation**
Unauthorized entities contribute attestations.
*Mitigation:* role-bound attestation validation.

**Threat B-1 — Contradictory Evidence Suppression**
A system suppresses conflicting instrumentation or evidence.
*Mitigation:* mandatory contradiction preservation.

**Threat AG-1 — Auto-Authorization**
A conformant implementation incorrectly treats `VERIFIED`, `CONSENSUS_VALID`, or `CONDUCT_VALID` as automatic execution authorization.
*Mitigation:* AG1–AG3 enforce separation between verification, authorization, and execution. Conformant implementations SHOULD support sampled audits of execution decisions against declared authorization sources.

---

## 9. Status Registry

**Class A**

- `VERIFIED`
- `TAMPERED`
- `INVALID`

**Class B**

- `SUPPORTED`
- `CONFLICTED`
- `INSUFFICIENT_EVIDENCE`
- `INVALID`

**Class C**

- `CONSENSUS_PENDING`
- `CONSENSUS_VALID`
- `CONSENSUS_FAILED`
- `INVALID`

**Class D**

- `CONDUCT_VALID`
- `CONDUCT_INVALID`

`CALIBRATION_IMPROVED` and `CALIBRATION_DEGRADED` are system telemetry tokens. A conformant implementation MUST NOT emit them as per-claim status. A conformant implementation MUST reject any artifact whose declared `status` is a telemetry token as `INVALID`.

---

## 10. Artifact Schemas

### Class A Artifact

```json
{
  "class": "A",
  "regime": "deterministic_verification",
  "claim": "this artifact matches its declared origin digest",
  "canonicalization": "RFC8785-JCS",
  "algorithm": "SHA-256",
  "expected_digest": "sha256:<hex>",
  "observed_digest": "sha256:<hex>",
  "status": "VERIFIED",
  "proof": {
    "type": "integrity_proof",
    "created_at": "ISO-8601 UTC"
  }
}
```

### Class B Artifact

```json
{
  "class": "B",
  "regime": "instrumented_empirical_verification",
  "claim": "this execution occurred with the declared observed result",
  "sources": [],
  "timestamps": [],
  "observations": [],
  "structural_diff": {},
  "status": "SUPPORTED",
  "proof": {
    "type": "empirical_support_record",
    "created_at": "ISO-8601 UTC"
  }
}
```

### Class C Artifact

```json
{
  "class": "C",
  "regime": "protocol_bound_consensus",
  "claim": "this action received the required approvals",
  "protocol": {
    "name": "required_reviewer_quorum",
    "version": "0.1.0",
    "required_quorum": 2,
    "eligible_attesters": []
  },
  "evidence": [],
  "status": "CONSENSUS_PENDING",
  "action_policy": {
    "action_allowed": false,
    "action_compelled": false,
    "reason": "Consensus has not reached the required quorum."
  },
  "proof": {
    "type": "consensus_process_record",
    "created_at": "ISO-8601 UTC"
  }
}
```

### Class D Conduct Artifact

```json
{
  "class": "D",
  "regime": "interpretive_governance",
  "claim": "this is the recommended strategy",
  "values_frame": {
    "optimizing_for": [],
    "not_optimizing_for": []
  },
  "alternatives": [],
  "reasoning_trace": [],
  "recommended_action": {},
  "reversibility_score": 0.0,
  "challenge_surface": [],
  "calibration": {
    "calibration_id": "cal_<id>",
    "review_after": "ISO-8601 UTC",
    "success_signals": [],
    "failure_signals": []
  },
  "commit_chain": [
    {
      "stage": 1,
      "name": "values_frame_commit",
      "hash": "sha256:<hex>",
      "content": {},
      "depends_on": null,
      "created_at": "ISO-8601 UTC"
    }
  ],
  "meta_proof": {
    "process_status": "CONDUCT_VALID",
    "artifact_hash": "sha256:<hex>"
  },
  "status": "CONDUCT_VALID"
}
```

---

## 11. Conformance

Conformance MUST be determined through vectors, schemas, invariants, and deterministic protocol behavior. A conformance claim derived from prose interpretation alone is INVALID.

**Principle (binding):**

> The prose explains the protocol.
> The vectors determine conformance.

Where prose and vectors disagree, the vectors govern.

Each vector MUST include:

- `vector_id`
- `protocol_version`
- `class`
- `description`
- `input`
- `expected_status`
- `expected_artifact_fields`
- `why`

---

## 12. Implementation Declaration

Schema:

```json
{
  "protocol": "wiseorder",
  "version": "0.1.0",
  "classes_supported": ["A", "B"]
}
```

Invariants:

- **ID1:** A conformant implementation MUST declare supported protocol version and supported epistemic classes.
- **ID2:** Conformance is class-scoped. An implementation MAY be conformant for one or more classes without implementing the full protocol.
- **ID3:** Implementations MUST NOT claim support for a class unless all invariants for that class are satisfied.

**Definition:** An implementation is conformant for a class if:

- all invariants for that class are satisfied
- all required artifact fields are emitted
- all required status semantics are honored
- all required conformance vectors pass

---

## 13. Partial Conformance

WiseOrder conformance is class-scoped.

There is no global binary conformance requirement for v0.1.0.

An implementation MAY support only Class A, Classes A/B, or all classes, provided supported classes fully satisfy protocol invariants and vectors.

The term:

> `PARTIALLY CONFORMANT`

is **NOT** a protocol status.

Conformance is declared per-class through Implementation Declaration.

---

## 14. Non-Goals

WiseOrder does NOT guarantee:

- objective truth
- moral correctness
- strategic success
- honest consensus participants
- absence of manipulation
- universal alignment

WiseOrder guarantees only:

- protocol semantics
- governance structure
- artifact integrity requirements
- uncertainty preservation
- process traceability
- auditability constraints

---

## 15. Future Work

The following surfaces are explicitly out of scope for v0.1.0. A v0.1.0 implementation MUST NOT claim to implement any of them under the v0.1.0 label, and MUST NOT rely on their presence in another implementation:

- revocation semantics
- artifact supersession
- consensus reversal
- extension governance
- protocol negotiation
- distributed audit registries
- cross-regime calibration exchange

A successor version MAY introduce any of these surfaces. v0.1.0 implementations MUST NOT silently honor successor-version constructs.

---

## 16. Final Position

Prediction alone is insufficient for reality-affecting systems.

Civilization-scale intelligence requires:

- provenance
- governance
- uncertainty handling
- authorization boundaries
- auditable consequence formation

WiseOrder defines a protocol layer for these concerns.

Not by replacing cognition.

By governing how cognition becomes consequence.
