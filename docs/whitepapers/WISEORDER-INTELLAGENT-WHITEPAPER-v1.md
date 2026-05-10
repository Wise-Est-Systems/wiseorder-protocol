# INTELLAGENT + WISEORDER — Whitepaper Index

A Governed Cognition + Deterministic Verification Stack for Bounded Machine Reasoning.

**Conformant to:** [`INTELLAGENT-MASTER-SPEC-STANDARD-v1.0.md`](./INTELLAGENT-MASTER-SPEC-STANDARD-v1.0.md).
**Document type:** Normative specification — split form.
**Subject release:** v0.1.0.
**Date:** 2026-05-10.

The whitepaper is delivered in four parts. Each is independently readable but cites terms defined in others. First-pass reading order is 1 → 2 → 3 → 4.

---

## Parts

### [Part 1 — Foundations](./WISEORDER-WHITEPAPER-PART-1-FOUNDATIONS.md)

Front matter, abstract, scope, non-goals, core thesis, definitions.

- §2.1 TITLE
- §2.2 ABSTRACT
- §2.3 SCOPE
- §2.4 NON-GOALS
- §2.5 CORE THESIS
- §2.6 DEFINITIONS

286 lines.

---

### [Part 2 — Mechanics](./WISEORDER-WHITEPAPER-PART-2-MECHANICS.md)

Formal primitives, invariants, threat model, runtime semantics, data structures.

- §2.7 FORMAL PRIMITIVES (9 objects)
- §2.8 INVARIANTS (32 across A/B/C/D + AG + CC + CS + ID + TEL)
- §2.9 THREAT MODEL (T-1..T-14)
- §2.10 RUNTIME SEMANTICS
- §2.11 DATA STRUCTURES (10 dataclasses)

770 lines.

---

### [Part 3 — Layers](./WISEORDER-WHITEPAPER-PART-3-LAYERS.md)

Canonicalization, determinism, authorization, memory, refusal.

- §2.12 CANONICALIZATION
- §2.13 DETERMINISM MODEL
- §2.14 AUTHORIZATION MODEL
- §2.15 MEMORY MODEL
- §2.16 REFUSAL SEMANTICS

311 lines.

---

### [Part 4 — Conformance & Release](./WISEORDER-WHITEPAPER-PART-4-CONFORMANCE.md)

Conformance model, vectors, interop, implementation status, limitations, future work, security, reproducibility, testing, release.

- §2.17 CONFORMANCE MODEL
- §2.18 CONFORMANCE VECTORS (23)
- §2.19 INTEROPERABILITY (3 fixtures, 7 cross-layer checks)
- §2.20 IMPLEMENTATION STATUS
- §2.21 KNOWN LIMITATIONS (11)
- §2.22 FUTURE WORK
- §2.23 SECURITY CONSIDERATIONS
- §2.24 REPRODUCIBILITY
- §2.25 TESTING REQUIREMENTS (135 tests)
- §2.26 RELEASE REQUIREMENTS
- §3 STATUS

666 lines.

---

## Key fingerprints (live at v0.1.0)

| Suite | SHA-256 |
| --- | --- |
| `vectors_suite_sha256` | `sha256:37d3ec45ecca12d256b7df1c02ac0f0d1474f71b68510e9475fa449b8eb1331b` |
| `manifests_suite_sha256` | `sha256:74eaaa62271f23172232bda43ba3340543e66c46ba1e2f5e6da18d3447a6ba29` |
| `corpus_sha256` | `sha256:c95685bff48c15abc313c462908b05ac309250bc660c2d802ae51af5a8038b09` |
| determinism cross-run | `sha256:b71c7134ef2c33ea5fcc9a3eb723efe6294ba18759ed91d1f64bdfe826107ba5` |

Reviewer reproduction of all four is the canonical conformance verification.

---

## Quick start

```
git clone <repo> wiseorder-protocol
cd wiseorder-protocol
git checkout v0.1.0
python3 -m venv .venv && source .venv/bin/activate && pip install -e .
make ci
```

Pass = the v0.1.0 trust surface holds on this commit.

---

*Refusal is success. Architecture is locked. The four parts together are the spec.*
