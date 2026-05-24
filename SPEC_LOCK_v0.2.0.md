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

### 2.5 Class D commit-stage preimage size cap

v0.1.0 invariant D5 (`SPEC.md §3 Class D`) requires Class D commit-chain stages to carry preimage `content`. v0.2.0 narrows D5 with an explicit resource bound to remove the denial-of-service surface created by an unbounded preimage requirement.

**Invariant D6 (v0.2.0):**

A conformant v0.2.0 verifier MUST reject as `CONDUCT_INVALID` any Class D artifact whose `commit_chain` violates either of the following bounds:

1. **Per-stage cap.** The canonical JSON serialization (sorted keys, compact separators `(',', ':')`, UTF-8) of any single stage's `content` field MUST NOT exceed **1,048,576 bytes (1 MiB)**.

2. **Per-artifact cap.** The sum of canonical JSON serialization sizes across every stage's `content` field in a single artifact's `commit_chain` MUST NOT exceed **4,194,304 bytes (4 MiB)**.

Both bounds are measured in bytes of the canonical serialization, not in source-text bytes or Unicode code points. The serialization rules are the same as those used for III hashing in §2.2.

Verifiers MUST include the stable reason code `PREIMAGE_OVERSIZED` in their per-verdict reasons output when emitting `CONDUCT_INVALID` for a D6 violation, to distinguish the size-cap rejection from generic D5 / CC1 preimage-missing rejections.

D6 does NOT introduce a new top-level status token. The Class D status registry remains `{CONDUCT_VALID, CONDUCT_INVALID}` (`STATUS-REGISTRY.md`).

**Threat model entry T-D6-1 (DoS via unbounded preimage):**

Without D6, a producer can attach a preimage of arbitrary size (e.g. an entire LLM context window) to a single stage, forcing every conformant verifier to materialize, canonicalize, and hash it. The verifier has no spec authority to reject on size, so it must either exhaust memory or violate D5. D6 removes this surface by giving the verifier explicit authority to reject oversized preimages while still honoring the preimage requirement.

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

A Class B artifact whose `status` differs from a prior state MUST declare `prior_status`, `transition_reason` (with `code` + `narrative`), and `prior_artifact_hash` (III hex of the prior artifact's canonical body, per §2.2). `prior_status` MAY be absent only when the artifact is the first in its lineage.

#### 2.6.3 Invariants

- **B4** — `INVALID` is terminal. A Class B artifact whose `prior_status == "INVALID"` MUST be rejected as `INVALID` with reason `INVALID_TERMINAL_TRANSITION`.
- **B5** — Any Class B artifact whose `status != prior_status` MUST declare both `prior_status` and `transition_reason`. Absence is `INVALID` with reason `PRIOR_STATUS_MISSING` or `TRANSITION_REASON_MISSING`.
- **B6** — The set of allowed `(prior_status, status)` pairs is the four `yes` rows of §2.6.1 plus any pair whose `status` is `INVALID`. Any pair outside this set is `INVALID` with reason `DISALLOWED_STATE_TRANSITION`.
- **B7** — Transition artifacts MUST declare `prior_artifact_hash`. Severed lineage is `INVALID` with reason `PRIOR_ARTIFACT_HASH_MISSING`.

#### 2.6.4 Reason codes

Positive (allowed-transition codes, written by artifact author):

| Positive code                       | Triggered when                                                                       |
| ----------------------------------- | ------------------------------------------------------------------------------------ |
| `NEW_EVIDENCE_REACHED_THRESHOLD`    | `INSUFFICIENT_EVIDENCE → SUPPORTED`                                                  |
| `NEW_EVIDENCE_INTRODUCED_CONFLICT`  | `INSUFFICIENT_EVIDENCE → CONFLICTED`, `SUPPORTED → CONFLICTED`                       |
| `CONTRADICTING_SOURCE_RETRACTED`    | `CONFLICTED → SUPPORTED`                                                             |

Rejection (emitted by verifier):

| Code                            | Triggered when                                                                       |
| ------------------------------- | ------------------------------------------------------------------------------------ |
| `INVALID_TERMINAL_TRANSITION`   | An artifact declares `prior_status == "INVALID"`.                                    |
| `TRANSITION_REASON_MISSING`     | `status != prior_status` but `transition_reason` is absent or `transition_reason.code` is empty. |
| `PRIOR_STATUS_MISSING`          | `status` was derived from a prior state but `prior_status` is absent.                |
| `DISALLOWED_STATE_TRANSITION`   | `(prior_status, status)` is not in the §2.6.1 allowed set and `status != "INVALID"`. |
| `PRIOR_ARTIFACT_HASH_MISSING`   | Transition artifact omits `prior_artifact_hash`.                                     |

#### 2.6.5 Evidence preservation (B2 extension)

B2 (preserve contradictory evidence) extends across transitions. A transitioning artifact MUST NOT delete or rewrite the evidence of its predecessor; the predecessor is recoverable via `prior_artifact_hash`. Mutation of prior evidence is `INVALID` with reason `DISALLOWED_STATE_TRANSITION`.

#### 2.6.6 v0.1.0 unaffected

This subsection applies to v0.2.0 only. v0.1.0 Class B artifacts continue to operate under `SPEC.md` v0.1.0 §3 without transition fields; `SPEC_LOCK_v0.1.md` is unchanged.

### 2.7 Attester identity and signature binding (v0.2.0)

Under v0.1.0, Class C declared `eligible_attesters` and rejected unauthorized participants (C2) without defining what an attester IS. v0.2.0 makes identity canonical.

#### 2.7.1 Attester identity object

A v0.2.0 attester is declared as:

```json
{
  "kid": "<URL-safe base64 no-padding, 22 chars (16 bytes of SHA-256(pubkey))>",
  "pubkey": "<URL-safe base64 no-padding, 43 chars (32-byte Ed25519 public key)>",
  "label": "<optional, cosmetic display string; MUST NOT be used as identity>"
}
```

- `pubkey` is the raw 32-byte Ed25519 public key (RFC 8032), URL-safe base64 no-padding encoded.
- `kid` is the first 16 bytes of `SHA-256(pubkey_raw_bytes)`, URL-safe base64 no-padding encoded. Deterministic from `pubkey`.
- A conformant v0.2.0 verifier MUST recompute `SHA-256(pubkey_raw_bytes)[:16]` and compare to the declared `kid`. Mismatch is `INVALID` with reason `KID_MISMATCH`.

`protocol.eligible_attesters` in a v0.2.0 Class C artifact is a list of Attester identity objects (not bare strings as in v0.1.0).

#### 2.7.2 Signature scheme

v0.2.0 Class C uses **Ed25519** (RFC 8032). No alternative scheme is permitted. There is no negotiation; signature size is fixed at 64 bytes.

The signature is URL-safe base64 no-padding encoded (88 chars). The signed payload is the canonical JSON serialization (sort_keys, compact separators `(",", ":")`, UTF-8 encoding) of the evidence entry with the `signature` field excluded.

#### 2.7.3 Evidence binding

Every entry in `evidence[*]` in a v0.2.0 Class C artifact MUST declare `attester_kid` (referencing one of `protocol.eligible_attesters[*].kid`), `attestation`, `attested_at` (ISO-8601 UTC), and `signature` (Ed25519, URL-safe base64 no-padding, over the canonical body with `signature` excluded).

#### 2.7.4 Invariants

- **C5** — Every evidence entry MUST carry a valid Ed25519 signature that verifies under the declared `attester_kid`'s pubkey, computed over the canonical JSON serialization of the evidence body with the `signature` field excluded. Failure → `INVALID` with reason `SIGNATURE_VERIFY_FAILED`.
- **C6** — `evidence[*].attester_kid` MUST exactly equal one of `protocol.eligible_attesters[*].kid`. Mismatch → `INVALID` with reason `UNAUTHORIZED_ATTESTER_KID`.
- **C7** — `kid` MUST equal the first 16 bytes of `SHA-256(pubkey_raw_bytes)`, URL-safe base64 no-padding. Mismatch → `INVALID` with reason `KID_MISMATCH`.

#### 2.7.5 Reason codes (stable v0.2.0 strings)

| Code                          | Triggered when                                                            |
| ----------------------------- | ------------------------------------------------------------------------- |
| `SIGNATURE_VERIFY_FAILED`     | Ed25519 verification of `signature` against canonical body fails.         |
| `UNAUTHORIZED_ATTESTER_KID`   | `attester_kid` does not match any declared `eligible_attesters[*].kid`.   |
| `KID_MISMATCH`                | Declared `kid` does not equal `SHA-256(pubkey)[:16]` base64url.           |

#### 2.7.6 Out of scope for v0.2.0

Key rotation, revocation, expiry/freshness, PKI/certificate chains, DIDs — all future work. A successor protocol version MAY register any of these. v0.2.0 implementations MUST NOT silently honor successor-version constructs.

#### 2.7.7 v0.1.0 unaffected

This subsection applies to v0.2.0 only. v0.1.0 Class C artifacts continue to declare `eligible_attesters` as bare strings without signatures; `SPEC_LOCK_v0.1.md` is unchanged.

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
