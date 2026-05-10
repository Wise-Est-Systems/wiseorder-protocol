# Vectors

> The prose in `SPEC.md` explains the protocol.
> **The vectors in this directory determine conformance.**

A WiseOrder implementation is conformant for a class **only if every published vector for that class passes**.

---

## Layout (planned)

```
vectors/
├── README.md           ← this file
├── class-a/            ← deterministic verification vectors
├── class-b/            ← instrumented empirical verification vectors
├── class-c/            ← protocol-bound consensus vectors
└── class-d/            ← interpretive governance vectors
```

Per-class subdirectories will be added as vectors are written. None exist at v0.1.0 draft adoption (2026-05-06).

---

## Vector format

Each vector is a single JSON file. Required fields:

```json
{
  "vector_id": "<stable, unique within protocol_version>",
  "protocol_version": "0.1.0",
  "class": "A" | "B" | "C" | "D",
  "description": "<one-sentence human description>",
  "input": { ... class-specific input ... },
  "expected_status": "<one of the class's allowed statuses>",
  "expected_artifact_fields": [ "<field>", "..." ],
  "why": "<which invariant or threat this vector exists to enforce>"
}
```

`vector_id` MUST be stable across protocol revisions of the same intent so regression tracking is meaningful. Renumbering is a vector breakage.

---

## Categories of vectors needed (not exhaustive)

**Class A** — JCS canonicalization round-trip, expected/observed digest match, expected/observed mismatch (`TAMPERED`), missing canonicalization scheme (`INVALID`), missing algorithm (`INVALID`).

**Class B** — single-source affirmation (`SUPPORTED`), multi-source agreement (`SUPPORTED`), multi-source contradiction (`CONFLICTED` with both records preserved), evidence below threshold (`INSUFFICIENT_EVIDENCE`), missing source declaration (`INVALID`).

**Class C** — quorum reached with eligible attesters only (`CONSENSUS_VALID`), quorum reached but `action_policy.action_allowed` still false (AG1 enforcement), attestation from ineligible attester rejected, quorum rules changed mid-collection rejected, sub-quorum closed (`CONSENSUS_FAILED`).

**Class D** — full conduct artifact with intact commit-chain (`CONDUCT_VALID`), missing preimage in stage (`CONDUCT_INVALID`, CC1/D5), missing `not_optimizing_for` field (`CONDUCT_INVALID`, D1), missing alternatives (`CONDUCT_INVALID`, D2), empty challenge surface (`CONDUCT_INVALID`, D3), Class D artifact attempting `VERIFIED` status (`CONDUCT_INVALID`, D4).

**Cross-cutting** — verification status not auto-authorizing execution (AG1), action policy preserved as auditable metadata (AG3), telemetry status (`CALIBRATION_*`) rejected as artifact `status` value.

---

## Status

No vectors are published at v0.1.0 draft adoption. Until they land, no implementation can be declared conformant for any class — see `CONFORMANCE.md` and `IMPLEMENTATIONS.md`.
