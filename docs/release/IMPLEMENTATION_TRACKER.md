# Implementation Tracker — WiseOrder Protocol v0.1.0

**Status:** Open. No independent implementation has reproduced vector outputs as of 2026-05-10.
**Authority:** This tracker defines the conditions under which an implementation is considered *independent* and the protocol is considered *externally validated*.

---

## 1. The Independence Rule

> **An implementation is considered independent only if it is authored, owned, and operated by a party that is not the first-party project (Wise.Est Systems).**

> **The protocol is not considered externally validated until at least one independent implementation reproduces the published vector outputs and canonicalization corpus byte-for-byte under v0.1.0.**

Self-declared first-party conformance is necessary but not sufficient for external validation. Today, the only declared implementations (`Winstack`, `WISEATA`) are first-party. Their `audit_status` is `NOT_AUDITED`.

---

## 2. Independent Implementation Targets

Three reference targets are declared. Order does not imply priority.

### 2.1 Rust verifier (`wiseorder-verifier-rs`)
- Class A and Class B at minimum; Classes C and D extend.
- Reads vectors from `vectors/*.json`.
- Produces a `conformance-report.json` byte-equivalent in vector verdicts to the first-party verifier.
- Reproduces `vectors_suite_sha256` and `manifests_suite_sha256` over the same inputs.

### 2.2 TypeScript verifier (`wiseorder-verifier-ts`)
- Same surface as the Rust target.
- Targets Node ≥ 20.
- Includes RFC 8785 JCS implementation independent of any first-party JCS code.

### 2.3 Go verifier (`wiseorder-verifier-go`)
- Same surface as the Rust target.
- Independent JCS implementation in pure Go.

---

## 3. Cross-Language Parity Requirements

An independent implementation claiming v0.1.0 conformance MUST satisfy all of the following.

### 3.1 Vector verdict parity
For every vector under `vectors/*.json`:
- The implementation MUST produce the vector's `expected_status`.
- The implementation MUST emit every field listed in `expected_artifact_fields`.
- The implementation MUST reject vectors that violate cross-rules (Class A non-JCS, Class D `VERIFIED`, telemetry token as status).

### 3.2 Canonicalization parity
For every entry under `canonicalization/corpus/`:
- The implementation MUST produce byte-identical canonical bytes.
- The SHA-256 of the produced bytes MUST equal the entry's `golden` digest.
- The aggregate `corpus_sha256` MUST equal `sha256:c95685bff48c15abc313c462908b05ac309250bc660c2d802ae51af5a8038b09` (frozen at v0.1.0 lock).

### 3.3 Replay equivalence
- Re-running the verifier on identical inputs MUST produce identical outputs across runs and across machines.
- The `vectors_suite_sha256` recorded by the implementation MUST equal `sha256:6168d2075931baa98bba763f9cd537142554aae7b26f19e3e93a60de2ee5bb0f` (33 vectors).
- Output ordering MUST be deterministic (sorted by `vector_id`).

### 3.4 Refusal parity
- For each rejecting vector, the implementation MUST emit a structured rejection record with the same rejection reason category as the first-party verifier.
- Refusal MUST NOT be promoted to a positive verdict under any code path.

### 3.5 Authorization parity
- AG1–AG3 MUST be enforced: no implementation may treat `VERIFIED` / `CONSENSUS_VALID` / `CONDUCT_VALID` as automatic execution authorization.
- The vectors `class-c-auto-authorize-rejected` and `class-c-authorization-source-required` MUST be rejected as `INVALID`.

---

## 4. Submission Requirements

An independent implementer claiming conformance MUST submit:

1. **Source repository URL** with a commit hash for the verified build.
2. **Implementation Declaration** (`schemas/implementation.schema.json`) added to `IMPLEMENTATIONS.md`.
3. **Conformance report** produced by the implementation, named `<impl-name>-conformance.json`, with the same structure as `reports/conformance-report.json`.
4. **Canonicalization report** confirming byte-identical corpus output.
5. **Independence statement** declaring the authoring party is not first-party (Wise.Est Systems).
6. **License** under which the implementation is released.

A submission MAY be added to `IMPLEMENTATIONS.md` with `audit_status: NOT_AUDITED` once vectors and canonicalization parity are reproduced. Promotion to `audit_status: AUDITED` requires external review per `AUDIT_SCOPE_v0.1.md`.

---

## 5. Tracker Table

| Implementation | Party | Language | Class coverage | Vector parity | Canonicalization parity | Audit | Status |
|---|---|---|---|---|---|---|---|
| Intellagent Runtime | first-party | Python | A/B/C/D | reference | reference | NOT_AUDITED | reference (in-tree) |
| Winstack | first-party | Rust/TS | A, B | self-declared | self-declared | NOT_AUDITED | declared |
| WISEATA | first-party | Python | B | self-declared | self-declared | NOT_AUDITED | declared |
| `wiseorder-verifier-rs` | independent | Rust | — | — | — | — | **OPEN** |
| `wiseorder-verifier-ts` | independent | TypeScript | — | — | — | — | **OPEN** |
| `wiseorder-verifier-go` | independent | Go | — | — | — | — | **OPEN** |

Until at least one row in the second half flips to `verified` parity, the protocol's external-validation status is **open**.

---

## 6. What Independence Does and Does Not Prove

**Proves:**
- The specification is implementable from prose + vectors alone.
- The canonicalization scheme is portable across runtimes.
- The vector suite is unambiguous.
- The first-party verifier is not silently encoding undocumented behavior.

**Does not prove:**
- That the threat model is complete.
- That the spec is correct.
- That production use is safe.
- That the protocol is adopted at scale.

External validation closes the smallest gap — the implementability gap. The remaining gaps require operational use, hostile audit, and time.

---

## 7. Tracker Maintenance

This tracker is updated when:
- An implementation is added.
- A class is verified by a new implementation.
- An implementation reaches `AUDITED` status.
- The independence rule is materially clarified.

Editorial updates do not require a version bump. Material changes to the rules in §3 require a version increment per `SPEC_LOCK_v0.1.md` §4.
