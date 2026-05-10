# Implementations

> Registry of known implementations of WiseOrder Protocol v0.1.0.
>
> An entry in this file is **not** a conformance certification. It is a declared *intent* to conform. Conformance is established only by passing the vectors in [`vectors/`](./vectors/).
>
> Per `CONFORMANCE.md` Declaration discipline: an implementation MUST NOT declare support for a class whose invariants it is known to fail, regardless of `audit_status`.

---

## Stack position

WiseOrder is the governance/spec/conformance layer. Implementations sit below it as proof substrate, and applications/models sit above:

```
                  reasoning
                      ↓
              ┌───────────────┐
              │   WiseOrder   │   ← governance / spec / conformance
              └───────────────┘
                      ↓
       ┌────────────────────────────┐
       │   Winstack    │   WISEATA  │   ← proof substrate
       └────────────────────────────┘
                      ↓
                  execution systems
```

`Wisest` sits as the broader ecosystem / company layer enclosing the stack.

---

## Registered implementations

### Winstack — production implementation

**Repo:** `~/Desktop/WinStack_Network_v1`
**Languages:** Rust (workspace) / TypeScript
**Role:** Production implementation, AI-provenance wedge
**Constitution (impl-internal):** `spec/grammar.md`

**Declaration:**

```json
{
  "implementation": "Winstack",
  "protocol": "wiseorder",
  "version": "0.1.0",
  "classes_supported": ["A", "B"],
  "audit_status": "NOT_AUDITED"
}
```

**Notes:** Candidate Class A + Class B support. Conformance pending vector pass. Single-ritual UX (drop). Win tag must self-verify (P12).

---

### WISEATA — research implementation

**Repo:** `~/Desktop/wop`
**Languages:** Python
**Role:** Research implementation, WOP runtime
**Constitution (impl-internal):** `spec/WISEATA-v0.1.1.md`

**Declaration:**

```json
{
  "implementation": "WISEATA",
  "protocol": "wiseorder",
  "version": "0.1.0",
  "classes_supported": ["B"],
  "audit_status": "NOT_AUDITED",
  "notes": "F-1 canonicalization incompatibility with WiseOrder v0.1.0 JCS requirement."
}
```

**Notes:** Class A is **not** declared — see F-1 below. Class B declared as candidate; conformance pending vector pass. WISEATA runtime is unchanged by this entry — this is a governance/conformance correction only.

---

## Open architecture friction

Per the user directive, the architecture is locked **unless implementation reality breaks it**. The following items are tracked.

### F-1 — Canonicalization Incompatibility

**Status:** Resolved within WiseOrder v0.1.0 (governance-only correction; no spec weakening, no escape hatch).

- WiseOrder v0.1.0 mandates RFC 8785 JCS for all Class A integrity operations.
- WISEATA-v0.1.1 currently uses a line-oriented `key=value` canonicalization format.
- Therefore WISEATA is not currently Class A conformant under WiseOrder v0.1.0.
- Future versions MAY define additional canonicalization scheme registries.
- v0.1.0 remains JCS-only.

**Action taken:** WISEATA's `classes_supported` reduced to `["B"]`. Winstack retains candidate support for `["A", "B"]`. WiseOrder v0.1.0 SPEC.md is unmodified. No alternate canonicalization scheme registered. No protocol negotiation introduced.

**Vector backstop:** [`vectors/class-a-non-jcs-invalid.json`](./vectors/class-a-non-jcs-invalid.json) pins the rule that any Class A artifact declaring a non-JCS canonicalization scheme MUST receive `INVALID` status under v0.1.0.

### F-2 — None at this time

Reserved.

---

## Status legend

| Status         | Meaning                                                                                                                       |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `NOT_AUDITED`  | Implementation registered with declared intent; no vectors run. Default starting state.                                       |
| `CONFORMANT`   | All vectors for every declared class pass. Requires `evidence.report_path` referencing a passing conformance report. Class scope MUST be enumerated. |
| `FAILED`       | One or more required vectors fail for a declared class. Requires non-empty `notes` describing the failure.                    |

`PARTIALLY CONFORMANT`, `IN_AUDIT`, and `NON_CONFORMANT` are **not** valid statuses (see `CONFORMANCE.md` and `tools/validate_implementations.py`).

---

## Schema notes

The JSON declaration blocks above extend the SPEC §12 minimum schema (`{"protocol", "version", "classes_supported"}`) with registry-level metadata fields: `implementation`, `audit_status`, and optional `notes`. These extensions are properties of the registry entry, not the protocol — they do not modify SPEC §12.
