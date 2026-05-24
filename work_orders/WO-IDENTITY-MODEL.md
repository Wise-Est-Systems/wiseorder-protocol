# WO-IDENTITY-MODEL — Canonical attester identity for Class C (v0.2.0)

**Scope:** WiseOrder Protocol v0.2.0 only. v0.1.0 is frozen and inherits no change.
**Filed:** 2026-05-23
**Status:** Draft — spec patch + vectors + structural test landed. Verifier enforcement (Ed25519 signature check) is a follow-up WO.

## 1. Problem

`SPEC.md §3 Class C` and the v0.1.0 lock reference `eligible_attesters` and "unauthorized attesters" without defining what an attester IS. There is no specified key format, no signature scheme, no trust anchor. Two conformant implementations cannot interoperate on Class C consensus because they don't agree on identity.

`tools/signature_runtime.py` implements an HMAC-SHA256 placeholder (not Ed25519); its own docstring flags public-key signing as future work. v0.2.0 closes this hole by lifting a real identity model into canon.

## 2. Design

**Signature scheme:** Ed25519 (RFC 8032). Reasons: 32-byte keys, 64-byte signatures, fast verify, no key-size negotiation (eliminates downgrade-attack class), IETF-standard, available in Python (`cryptography`), Rust (`ed25519-dalek`), Go (stdlib `crypto/ed25519`).

**Attester identity format:**

```json
{
  "kid": "<URL-safe base64 no-padding, 22 chars>",
  "pubkey": "<URL-safe base64 no-padding, 43 chars = 32 raw bytes>",
  "label": "<optional, human-facing display name>"
}
```

- `pubkey` is the 32-byte Ed25519 public key.
- `kid` is the first 16 bytes of `SHA-256(pubkey)`, URL-safe base64 no-padding. Deterministic from `pubkey`. A v0.2.0 implementation MUST recompute and verify `kid` on every artifact.
- `label` is purely cosmetic; verifiers MUST NOT use it as identity.

**Attestation binding:**

Each entry in `evidence[*]` MUST carry:
- `attester_kid` — string equal to one of the declared `protocol.eligible_attesters[*].kid` values.
- `signature` — Ed25519 signature, URL-safe base64 no-padding (88 chars = 64 raw bytes), over the canonical JSON serialization (sort_keys, compact separators, UTF-8) of the evidence body with the `signature` field excluded.

**New invariants:**

- **C5** — Every evidence entry MUST verify under the declared `attester_kid`'s pubkey, against the canonical body with `signature` excluded. Failure → `INVALID` with reason `SIGNATURE_VERIFY_FAILED`.
- **C6** — `evidence[*].attester_kid` MUST exactly match one of `protocol.eligible_attesters[*].kid`. Mismatch → `INVALID` with reason `UNAUTHORIZED_ATTESTER_KID`.

## 3. Out of scope for v0.2.0

- **Key rotation** — flagged as future work (v0.3.0 candidate).
- **Revocation** — flagged as future work.
- **Expiry / freshness** — flagged as future work.
- **PKI / X.509 / DID** — explicitly NOT adopted. WiseOrder v0.2.0 uses raw Ed25519 pubkeys; no certificate chain.

These are the surfaces a v0.3.0 follow-up would address. v0.2.0 ships with deliberate scope: who can sign, and whether their signature verifies. Nothing else.

## 4. Test-vector provenance

The two v0.2.0 vectors under `vectors/v0.2.0/class-c-*-attestation.json` use a deterministic Ed25519 keypair derived from the RFC 8032 §7.1 Test-1 seed (`9d61b19d...7f60`). The signatures are real, computed over the canonical body of each vector's attestation. The "invalid" vector uses the same valid signature with the first byte XOR'd by `0x01`.

## 5. Deliverables

1. This document.
2. `work_orders/IDENTITY-MODEL-spec-patch.md` — proposed §2.7 for `SPEC_LOCK_v0.2.0.md`.
3. `vectors/v0.2.0/class-c-valid-signed-attestation.json`
4. `vectors/v0.2.0/class-c-invalid-signature.json`
5. `tests/test_identity_model.py` — structural tests pass today; verifier-enforcement tests are `xfail(strict=True)` until the C5/C6 enforcement WO ships.

## 6. Follow-up

- WO: implement Ed25519 verification in all three verifier tracks (Python `tools/minimal_verifier.py`, Rust, Go), emit `SIGNATURE_VERIFY_FAILED` and `UNAUTHORIZED_ATTESTER_KID` reason codes, flip xfail decorators to plain pass.
- WO (later): rotation / revocation / expiry semantics for v0.3.0.
