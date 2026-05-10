# Artifact Schemas

> Focused extract of `SPEC.md` §10. In case of any discrepancy with `SPEC.md`, **`SPEC.md` governs.**

Every WiseOrder artifact MUST declare its `class`. The schema below is the canonical shape per class. Implementations MAY add fields but MUST NOT omit required ones.

---

## Class A Artifact — Deterministic Verification

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

**Required fields:** `class`, `regime`, `claim`, `canonicalization`, `algorithm`, `expected_digest`, `observed_digest`, `status`, `proof`.

**Notes:**

- `canonicalization` MUST be a registered scheme (v0.1.0 registers only `RFC8785-JCS`).
- `algorithm` MUST be declared explicitly. SHA-256 is the v0.1.0 default.
- Verification MUST operate on canonicalized bytes only (A3).

---

## Class B Artifact — Instrumented Empirical Verification

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

**Required fields:** `class`, `regime`, `claim`, `sources`, `timestamps`, `observations`, `structural_diff`, `status`, `proof`.

**Notes:**

- All evidence sources MUST be declared explicitly (B1).
- Contradictory evidence MUST be preserved, not pruned (B2). When present, status is `CONFLICTED`.
- Evidence ordering MUST remain auditable (B3).

---

## Class C Artifact — Protocol-Bound Consensus

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

**Required fields:** `class`, `regime`, `claim`, `protocol`, `evidence`, `status`, `action_policy`, `proof`.

**Notes:**

- `protocol.name` and `protocol.required_quorum` MUST be declared **before** attestation collection begins (C1).
- Attestations from outside `eligible_attesters` MUST be rejected (C2).
- `CONSENSUS_VALID` MUST NOT imply execution authorization (C3, AG1). The separate `action_policy` block governs execution.
- Quorum semantics MUST be preserved as auditable metadata (C4).

---

## Class D Conduct Artifact — Interpretive Governance

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

**Required fields:** `class`, `regime`, `claim`, `values_frame` (with both `optimizing_for` and `not_optimizing_for`), `alternatives` (≥1, D2), `reasoning_trace`, `recommended_action`, `reversibility_score`, `challenge_surface` (D3), `calibration`, `commit_chain`, `meta_proof`, `status`.

**Commit-chain stage shape:**

```json
{
  "stage": <integer ≥ 1>,
  "name": "<stage_name>",
  "hash": "sha256:<hex>",
  "content": { ... preimage required, never null ... },
  "depends_on": "sha256:<hex of prior stage>" | null,
  "created_at": "ISO-8601 UTC"
}
```

**Notes:**

- `values_frame` MUST expose both what was optimized for AND what was explicitly refused (D1).
- At least one defensible alternative MUST appear in `alternatives` (D2).
- `challenge_surface` MUST contain self-generated counterarguments (D3).
- A Class D artifact MUST NOT receive `VERIFIED` status (D4).
- Every stage in `commit_chain` MUST include preimage `content` — a hash without its preimage is unauditable (D5, CC1).
- Every stage after stage 1 MUST set `depends_on` to the prior stage's hash (CC2).
- Missing commit stages invalidate process proof (CC3).
