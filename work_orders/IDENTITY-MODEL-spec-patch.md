# Proposed patch to `SPEC_LOCK_v0.2.0.md`

**Insert as new subsection §2.7, immediately after §2.6 (Class B status transition rules) and before §3 (v0.1.0 Coexistence).**

---

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

Every entry in `evidence[*]` in a v0.2.0 Class C artifact MUST declare:

```json
{
  "attester_kid": "<must equal one of protocol.eligible_attesters[*].kid>",
  "attestation": "<approve | reject | abstain | ...>",
  "attested_at": "<ISO-8601 UTC>",
  "signature": "<Ed25519 signature, URL-safe base64 no-padding>"
}
```

Additional evidence-body fields are permitted; whatever fields are present (excluding `signature`) form the signed payload.

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

- **Key rotation** — future work for v0.3.0. A v0.2.0 implementation MUST treat each Attester identity as immutable for the lifetime of the artifact.
- **Revocation** — future work for v0.3.0. v0.2.0 has no revocation surface.
- **Expiry / freshness windows** — future work for v0.3.0.
- **PKI / certificate chains / DIDs** — NOT adopted. v0.2.0 binds to raw Ed25519 pubkeys; no certificate authority is invoked.

A successor protocol version MAY register any of these. v0.2.0 implementations MUST NOT silently honor successor-version constructs.

#### 2.7.7 v0.1.0 unaffected

This subsection applies to v0.2.0 only. v0.1.0 Class C artifacts continue to declare `eligible_attesters` as bare strings without signatures; `SPEC_LOCK_v0.1.md` is unchanged.
