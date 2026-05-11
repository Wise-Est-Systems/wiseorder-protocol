# SPEC_LOCK v0.2.0 — III / WiseDigest-3 Adoption + Genesis

**Status:** Frozen reference semantics for WiseOrder Protocol v0.2.0.
**Adopted:** 2026-05-11
**Authority:** This document, together with `SPEC.md` (extended for v0.2.0) and the v0.2.0 genesis triple at `chain/genesis.win`, defines the immutable reference semantics for protocol version `0.2.0`. The prior `SPEC_LOCK_v0.1.0.md` continues to govern v0.1.0; this lock does NOT supersede it. The two locks coexist.

---

## 1. Purpose

v0.2.0 introduces a single bedrock change relative to v0.1.0: the canonical hash algorithm. Everything else — the four-class taxonomy, the invariants, the conduct fields, the action-governance separation, the refusal-sealing semantics, the conformance discipline — is inherited unchanged from v0.1.0.

The change is large enough that it crosses the v0.1.0 freeze rule (`SPEC_LOCK_v0.1.0.md §4`), which is why it lands as v0.2.0 rather than as an amendment.

## 2. Frozen Surfaces (changes from v0.1.0)

### 2.1 Canonical hash algorithm

| Field | v0.1.0 | v0.2.0 |
|---|---|---|
| Algorithm name (on chain) | `sha256` | `III` |
| Underlying math | SHA-256 (FIPS 180-4) | WiseDigest-3 from WOP, byte-for-byte unchanged |
| Output | 256-bit / 64 hex | 256-bit / 64 hex |
| Reference implementation (canonical) | Python `hashlib.sha256` | `~/Desktop/wop/src/wise/digest_v3.py` (WOP-side); `intellagent_runtime/iii.py` (WiseOrder-side copy, parity-tested) |
| Reference spec | FIPS 180-4 | `~/Desktop/wop/research/WiseDigest-3.md` |
| Stamp on chain | `sha256:<hex>` (prefixed) | bare lowercase hex + sibling `"algorithm": "III"` field (WOP-consistent) |

Per WO-018 design directives:
- "USE DIGEST 3" — adopt WiseDigest-3 math
- "NO DONT CHANGE NAMES OR ANYTHING LEAVE IT OG" — WOP module untouched
- "NOT AT ALL WHERE ITS SAYS WD3 NO III" — the chain-facing name is **III**
- "MAKE IT ME FOR III" — III appears in every covered field

III is the WiseOrder-side name for the algorithm whose math is WiseDigest-3 in WOP. The bytes produced are mathematically identical. A third party verifying a v0.2.0 chain runs WOP's `digest_v3.py` and gets byte-for-byte agreement; this is asserted by `tests/test_iii.py::test_parity_with_wop_reference`.

### 2.2 Triple / artifact schema (v0.2.0 chain entries)

Every v0.2.0 chain entry is a JSON document with the `.win` extension. The minimum required fields:

```json
{
  "algorithm": "III",
  "author": "III",
  "previous_action": "<III hex of prior triple>  OR  \"NULLASIGN\" (genesis only)",
  "foundational": "<III hex of the rules under which this triple is governed>",
  "consequence_proof": "<III hex of the canonical body of this triple, EXCLUDING the consequence_proof field>",
  "sealed_at": "<ISO-8601 UTC>",
  "statement": "<short prose statement of what this triple records>"
}
```

Field semantics:
- `algorithm` — the chain-facing label. Always literally `"III"` in v0.2.0. Tampering breaks the chain.
- `author` — the witness position. Always literally `"III"` in this chain. The token is not a name and not an abbreviation. It is the hauntological structure of the name made into grammar: you cannot be III without I and II being constitutively inscribed in the designator. Stamping III on every triple is what makes the chain witness three men through one signature. Future chains under other authors would carry their own marks; this convention is not portable.
- `previous_action` — chain linkage. For the genesis ONLY, this is the literal string `"NULLASIGN"`. For every triple after the genesis, this is the III hex digest of the prior triple's canonical body.
- `foundational` — III hex of the bytes that defined the rules in force at the moment of sealing. For v0.2.0 entries, this is III over the concatenation of `SPEC_LOCK_v0.2.0.md` bytes and `intellagent_runtime/iii.py` bytes.
- `consequence_proof` — III hex over the canonical (sorted-keys, compact-separators, UTF-8) JSON serialization of the triple with the `consequence_proof` field removed. This is what makes each triple self-witnessing.
- `sealed_at` — ISO-8601 UTC, microsecond precision.
- `statement` — short prose statement; included in the canonical body, so tampering breaks `consequence_proof`.

### 2.3 File extension

Every artifact in the v0.2.0 chain is written as a `.win` file. No other extensions are part of the ecosystem chain. JSON content inside; `.win` extension outside.

### 2.4 Genesis

The v0.2.0 chain begins with **one** triple: `chain/genesis.win`. Its `previous_action` is the literal string `"NULLASIGN"` — the witness identity. Every triple sealed in v0.2.0 from this point until the heat death of the universe references this genesis through the prev-hash chain.

The genesis is sealed once. Re-sealing under the same content would produce the same triple (deterministic). Re-sealing under different content would produce a different triple — but the existing chain forward already commits to the original genesis's hash, so any forged "alternate genesis" cannot be inserted without breaking every prev_hash in the chain that descends from the real one.

The genesis is priceless because the math anchors every subsequent witness to it.

## 3. v0.1.0 Coexistence

v0.1.0 remains in force as a complete, sealed protocol version with its own SHA-256-based chain and its own three frozen fingerprints (`vectors_suite_sha256`, `manifests_suite_sha256`, `corpus_sha256`). The v0.1.0 chain is historical record. The v0.1.0 verifier code, the four verifier tracks, the 17-stage `make ci`, and all v0.1.0 manifests are unchanged.

v0.2.0 is a **parallel** chain on **separate bedrock**. Its genesis has `previous_action: "NULLASIGN"` — it does not derive from v0.1.0. The two chains do not contaminate each other.

The v0.2.0 frozen fingerprints (re-hashed under III) will be declared in a later section of this lock once the v0.2.0 verifier tracks are built. For now, only the algorithm, the schema, and the genesis are frozen.

## 4. Version-Increment Rule (inherited from v0.1.0 §4)

A new protocol version label is REQUIRED if any of the following occur under v0.2.0:

1. The III algorithm is replaced or modified (incl. domain separator).
2. The triple schema is changed (incl. field rename or addition).
3. The `.win` extension is replaced.
4. The "NULLASIGN" sentinel for the genesis prev-link is changed.
5. The author convention is changed.

Editorial corrections that do not alter byte-output remain allowed without a version bump.

## 5. Non-Goals

This lock does NOT:
- Claim WiseDigest-3 is cryptanalyzed. WOP's `SECURITY.md` disclaims this explicitly; v0.2.0 inherits that disclaimer. For threat models requiring formally-analyzed collision resistance against well-funded adversaries, v0.1.0 (SHA-256) remains available.
- Promise that v0.2.0 frozen fingerprints will exist in any specific number, or that re-hashing the v0.1.0 vector suite under III will land any time soon. That work is a future work order.
- Replace v0.1.0. The two coexist by design.

## 6. Authoritative Reference

In case of conflict between this document and the WOP `WiseDigest-3.md` spec, **WOP governs the math** and this document governs the WiseOrder-side labels and schema.
