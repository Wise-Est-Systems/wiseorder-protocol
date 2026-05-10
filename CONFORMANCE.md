# Conformance

> Focused extract of `SPEC.md` §11–§13. In case of any discrepancy with `SPEC.md`, **`SPEC.md` governs.**

---

## Principle

> The prose explains the protocol.
> **The vectors determine conformance.**

Conformance is determined through **vectors, schemas, invariants, and deterministic protocol behavior** — not by prose interpretation. If a reading of `SPEC.md` would pass an invariant but fail a published vector, the implementation is non-conformant.

Vectors live in [`vectors/`](./vectors/), grouped by class.

---

## Conformance is class-scoped

WiseOrder v0.1.0 has no global binary conformance requirement. An implementation declares which classes it supports and is conformant **for those classes** if and only if every invariant, schema, status, and vector for those classes passes.

Acceptable declarations:

- Class A conformant
- Classes A/B conformant
- Classes A/B/C conformant
- Classes A/B/C/D conformant

The term **`PARTIALLY CONFORMANT` is not a protocol status** and MUST NOT be used in implementation declarations.

---

## Implementation Declaration

Every conformant implementation MUST publish a declaration matching:

```json
{
  "protocol": "wiseorder",
  "version": "0.1.0",
  "classes_supported": ["A", "B"]
}
```

Invariants:

- **ID1** — Implementations MUST declare protocol version and supported classes.
- **ID2** — Conformance is class-scoped; an implementation MAY support one or more classes without implementing the full protocol.
- **ID3** — Implementations MUST NOT claim support for a class unless all invariants for that class are satisfied.

### Declaration discipline

**Implementations failing invariants for a class MUST NOT declare support for that class.**

This applies whether or not the implementation has been audited. Known invariant failure (for example: a canonicalization scheme other than RFC 8785 JCS for Class A under v0.1.0) excludes the class from `classes_supported` regardless of `audit_status`. The contrapositive of ID3 is enforceable on declaration, not only at audit time.

---

## Definition of class conformance

An implementation is conformant for a given class if **all** of the following hold:

1. Every invariant declared for that class in `SPEC.md` is satisfied.
2. Every required artifact field for that class (per `ARTIFACTS.md`) is emitted.
3. Every status semantic for that class (per `STATUS-REGISTRY.md`) is honored.
4. Every published conformance vector for that class passes.

If any of (1)–(4) fails, the implementation is **not conformant for that class** and MUST NOT declare it.

---

## What conformance does NOT imply

Per Law 2 and the AG-series invariants:

- Conformance does NOT imply execution authorization.
- A `VERIFIED`, `CONSENSUS_VALID`, or `CONDUCT_VALID` artifact emitted by a conformant implementation does NOT, by itself, authorize action.
- Authorization is a separately-governed concern (AG1–AG3).

---

## Vector index

The current vector index lives at [`vectors/README.md`](./vectors/README.md). Each vector MUST include:

- `vector_id`
- `protocol_version`
- `class`
- `description`
- `input`
- `expected_status`
- `expected_artifact_fields`
- `why`

Until vectors land, no implementation can be declared conformant for any class. Architecture is locked; vectors are the next phase.
