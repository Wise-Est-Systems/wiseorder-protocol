# INTELLAGENT + WISEORDER — Part 2: Mechanics

*Formal primitives, invariants, threat model, runtime semantics, data structures.*

**Conformant to:** [`INTELLAGENT-MASTER-SPEC-STANDARD-v1.0.md`](./INTELLAGENT-MASTER-SPEC-STANDARD-v1.0.md).
**Document type:** Normative specification — split form.
**Subject release:** v0.1.0.
**Date:** 2026-05-10.

**Parts:**
- Part 1 — Foundations: [`WISEORDER-WHITEPAPER-PART-1-FOUNDATIONS.md`](./WISEORDER-WHITEPAPER-PART-1-FOUNDATIONS.md) (§2.1 TITLE → §2.6 DEFINITIONS)
- Part 2 — Mechanics: [`WISEORDER-WHITEPAPER-PART-2-MECHANICS.md`](./WISEORDER-WHITEPAPER-PART-2-MECHANICS.md) (§2.7 PRIMITIVES → §2.11 DATA STRUCTURES)
- Part 3 — Layers: [`WISEORDER-WHITEPAPER-PART-3-LAYERS.md`](./WISEORDER-WHITEPAPER-PART-3-LAYERS.md) (§2.12 CANONICALIZATION → §2.16 REFUSAL)
- Part 4 — Conformance & Release: [`WISEORDER-WHITEPAPER-PART-4-CONFORMANCE.md`](./WISEORDER-WHITEPAPER-PART-4-CONFORMANCE.md) (§2.17 CONFORMANCE → §3 STATUS)

The four parts together constitute the complete normative specification. No part is independently sufficient; each cites terms defined in others (DEFINITIONS in Part 1; INVARIANTS in Part 2). Read in order on first pass; reference any part directly thereafter.

---

## 2.7 FORMAL PRIMITIVES

The stack defines nine primary computational objects. Each names its creation, mutation, invalidation, replay, and persistence rules.

### 2.7.1 EpistemicState

**Creation.** Constructed by `RuntimeLoop.__init__` with empty `objects`, `audit_head = null`, `refusal_head = null`. Persisted to disk on the first transition.

**Mutation.** Only via `apply_transition` after kernel verification + (if action-bearing) gate authorization. Mutation is structural: `objects` are added or replaced; `audit_head` is updated to the new entry's `this_entry_sha256`; `refusal_head` advances on refusal.

**Invalidation.** A reload that detects `state_id != compute_state_id(loaded_objects)` raises `StateTampered`. The runtime fails closed.

**Replay.** Reconstructable from `state.json` + the audit memory directory. Loading the head pointer and verifying the chain produces the same `EpistemicState` byte-for-byte.

**Persistence.** Single file `state.json` written via atomic `os.replace`. The file is the canonical persistence form; no other surface holds state.

**Invariant.** `state_id` is content-addressed over `objects` only (not over `audit_head`), avoiding the audit-state circularity that arises when `state_id` references `audit_head` and `audit_head` references `state_id`.

---

### 2.7.2 EpistemicTransition

**Creation.** Constructed by a proposer. Required fields: `transition_id` (deterministic from canonical body), `delta` (object additions/modifications), `class_` (A/B/C/D), `proposer_id`, `metadata`. Optional: `authorization` (required for action-bearing transitions).

**Mutation.** Frozen dataclass; immutable post-construction. Modification requires producing a new transition with a new `transition_id`.

**Invalidation.** A transition is rejected by the kernel if any class invariant fails (A1–A3, B1–B3, C1–C4, D1–D5, CC1–CC4, CS1–CS3). An action-bearing transition without `authorization` is rejected by AG3 regardless of kernel verdict.

**Replay.** Reconstructable from the audit entry that recorded its acceptance, or from the refusal record that recorded its rejection.

**Persistence.** Not persisted directly. The transition's canonical bytes are absorbed into the audit entry (`AuditEntry.transition_canonical_bytes_sha256`) or the refusal record (`RefusalRecord.challenge_surface_sha256`).

---

### 2.7.3 Authorization

**Creation.** Constructed by the proposer (carrying a hint of which authority the transition expects) or by the gate (recording the actual decision). Required fields: `source_id`, `decision`, `reason` (optional). The proposer-supplied authorization is a *hint*; the gate-resolved authorization is *binding*.

**Mutation.** Frozen.

**Invalidation.** An authorization with `source_id` not registered in the active policy → AG3 refusal.

**Replay.** Recorded inside the transition; replays with the transition.

**Persistence.** Inside the transition.

---

### 2.7.4 KernelVerdict

**Creation.** Returned by `WiseOrderKernel.verify(transition, prior_state)`. Fields: `passed: bool`, `class_: str`, `failure_codes: tuple[str, ...]`, `details: dict`.

**Mutation.** Frozen.

**Invalidation.** A verdict is invalidated only by re-running `verify` on the same `(transition, prior_state)` and observing a different result. Determinism contract guarantees the result is identical given identical inputs (CS1–CS3).

**Replay.** Recorded inside the audit entry's `kernel_verdict` field.

**Persistence.** Inside the audit entry.

---

### 2.7.5 AuthorizationDecision

**Creation.** Returned by `AuthorizationGate.evaluate(transition)`. Fields: `authorized: bool`, `policy_id: str`, `source_id: str | null`, `reason_codes: tuple[str, ...]`.

**Mutation.** Frozen.

**Invalidation.** A decision is invalidated only by re-running `evaluate` against an updated policy state. v0.1 policies are static (file-loaded); a new policy is a new file with a new `policy_id`.

**Replay.** Recorded inside the audit entry's `gate_decision` field.

**Persistence.** Inside the audit entry.

---

### 2.7.6 AuditEntry

**Creation.** Constructed by `AuditMemory.append` from an accepted (or refused) transition. Fields: `entry_id`, `prev_entry_sha256`, `transition_canonical_bytes_sha256`, `kernel_verdict`, `gate_decision`, `state_id_after`, `timestamp`, `this_entry_sha256` (computed last with the self-field omitted from the body).

**Mutation.** Append-only. No in-place modification.

**Invalidation.** Any modification breaks `verify_chain`. A break is detected at the position of the tampering, not silently.

**Replay.** The chain is the replay surface. Re-loading the entries from disk in order produces identical bytes.

**Persistence.** One JSON file per entry under `intellagent_audit/entries/`. The head pointer is in `intellagent_audit/head.json`.

---

### 2.7.7 AuditMemory

**Creation.** Constructed by `RuntimeLoop.__init__` pointing at a directory. Initial state: empty entries, `head == null`.

**Mutation.** Only via `append(entry)`. Append computes `this_entry_sha256` over the canonical body with the self-field omitted, then writes the entry file via atomic `os.replace`, then updates `head.json` via atomic `os.replace`.

**Invalidation.** `verify_chain()` walks the chain from head backward, recomputing `this_entry_sha256` at each step. Mismatch → `ChainCorrupt`. Missing predecessor → `ChainCorrupt`. Missing self-field on a non-head entry → `ChainCorrupt`.

**Replay.** Full chain reconstructable from disk. Tampering at any position is detected.

**Persistence.** Directory of per-entry files + head pointer file. Atomic writes throughout.

---

### 2.7.8 RefusalRecord

**Creation.** Constructed by the runtime when `kernel.verify().passed == False` OR `gate.evaluate().authorized == False` OR a proposer returns no candidates. Fields: `transition_id`, `class_`, `kernel_verdict`, `gate_decision`, `candidates_rejected`, `challenge_surface_sha256`, `timestamp`, `reason_codes`, optional `provenance`.

**Mutation.** Frozen.

**Invalidation.** Refusal records are not invalidated; a refused transition can be re-proposed (with the same or different proposer), but the original refusal record stands.

**Replay.** Recorded in `intellagent_audit/refusals/`. Each record is content-addressed via `refusal_sha256`.

**Persistence.** One JSON file per refusal record. The refusal head is recorded in the parent audit entry.

---

### 2.7.9 ProposalCandidate

**Creation.** Constructed by a proposer's `propose` method. Fields: `transition: EpistemicTransition`, `provenance: ProposalProvenance` (which proposer, which provider, which prompt sha256, which seed, which timestamp).

**Mutation.** Frozen.

**Invalidation.** A candidate that fails kernel verification or gate authorization is invalidated; the runtime accumulates the rejection in the search's `candidates_rejected` list and seals it into the resulting `RefusalRecord` if the search ends without acceptance.

**Replay.** Replayable when the proposer + provider + seed are pinned. The `DeterministicMockProvider` is the in-contract replay path.

**Persistence.** Not persisted directly. The candidate's canonical bytes are absorbed into either the audit entry (if accepted) or the refusal record (if rejected).

---

## 2.8 INVARIANTS

The stack defines 32 invariants across nine groups. Each invariant has an ID, a statement, a violation condition, and an expected runtime response.

### 2.8.1 Class A Invariants

**A1 — Canonicalization required.**
Statement: A Class A artifact MUST canonicalize under the registered scheme (RFC 8785 JCS in v0.1.0).
Violation: Artifact bytes do not equal `canonicalize(artifact_object)`.
Response: Kernel returns `passed=False`, `failure_codes=("A1",)`. `RefusalRecord` sealed.

**A2 — Provenance signature required.**
Statement: A Class A artifact MUST include `provenance.signature_sha256` resolving to a non-empty 64-hex string.
Violation: Field missing or malformed.
Response: `passed=False`, `failure_codes=("A2",)`.

**A3 — Status discipline.**
Statement: A Class A artifact's `status` MUST be one of `VERIFIED`, `TAMPERED`, `INVALID`. Telemetry tokens (`CALIBRATION_*`) are forbidden.
Violation: `status` outside the registry or matches `CALIBRATION_*`.
Response: `passed=False`, `failure_codes=("A3",)`.

---

### 2.8.2 Class B Invariants

**B1 — Sources required.**
Statement: A Class B artifact MUST include a non-empty `sources` array; each source carries a URI plus a citation surface.
Violation: Empty or missing.
Response: `passed=False`, `failure_codes=("B1",)`.

**B2 — Contradictory evidence handling (unidirectional at v0.1).**
Statement: A Class B artifact whose evidence contradicts MUST set `status` to `CONFLICTED`. The reverse direction (rejecting `SUPPORTED` with contradictions) is deferred to v0.2.
Violation (v0.1 surface): `status == CONFLICTED` without contradicting evidence — kernel returns `passed=False`.
Response: `passed=False`, `failure_codes=("B2",)`. Note: the bidirectional form is deferred (see §2.21).

**B3 — Status discipline.**
Statement: A Class B artifact's `status` MUST be one of `SUPPORTED`, `CONFLICTED`, `INSUFFICIENT_EVIDENCE`, `INVALID`. Telemetry tokens forbidden.
Violation: `status` outside the registry or matches `CALIBRATION_*`.
Response: `passed=False`, `failure_codes=("B3",)`.

---

### 2.8.3 Class C Invariants

**C1 — Authorized attesters required.**
Statement: A Class C artifact MUST list its `authorized_attesters` and every entry in `agreement.attesters` MUST appear in `authorized_attesters`.
Violation: An attester signed who is not authorized.
Response: `passed=False`, `failure_codes=("C1",)`.

**C2 — Signature collection.**
Statement: Each attester in `agreement.attesters` MUST contribute a signature resolving to a non-empty 64-hex SHA-256.
Violation: Missing or malformed signature.
Response: `passed=False`, `failure_codes=("C2",)`.

**C3 — Threshold semantics.**
Statement: An artifact with `status: CONSENSUS_VALID` MUST have `count(agreement.attesters) >= consensus_threshold`. An artifact with `status: CONSENSUS_PENDING` MUST have `count < consensus_threshold`.
Violation: Threshold and status mismatch.
Response: `passed=False`, `failure_codes=("C3",)`.

**C4 — Status discipline.**
Statement: Class C `status` MUST be one of `CONSENSUS_PENDING`, `CONSENSUS_VALID`, `CONSENSUS_FAILED`, `INVALID`.
Violation: Outside registry.
Response: `passed=False`, `failure_codes=("C4",)`.

---

### 2.8.4 Class D Invariants

**D1 — Conduct status discipline.**
Statement: Class D `status` MUST be one of `CONDUCT_VALID`, `CONDUCT_INVALID`.
Violation: Outside registry.
Response: `passed=False`, `failure_codes=("D1",)`.

**D2 — Alternatives required.**
Statement: A `CONDUCT_VALID` artifact MUST include `alternatives` with at least two entries, each with a name + rationale.
Violation: Missing or count < 2.
Response: `passed=False`, `failure_codes=("D2",)`.

**D3 — Counterarguments required.**
Statement: A `CONDUCT_VALID` artifact MUST include `counterarguments` with at least one entry.
Violation: Missing or empty.
Response: `passed=False`, `failure_codes=("D3",)`.

**D4 — Verified status rejected for D.**
Statement: A Class D artifact MUST NOT carry a Class A `status: VERIFIED` token. Class D is interpretive governance, not deterministic verification.
Violation: `status == VERIFIED` on a Class D artifact.
Response: `passed=False`, `failure_codes=("D4",)`.

**D5 — Commit chain integrity.**
Statement: A `CONDUCT_VALID` artifact's commit chain MUST satisfy CC1–CC4 (see §2.8.5).
Violation: Any CC violation.
Response: `passed=False`, `failure_codes=("D5", "CC*",)`.

---

### 2.8.5 Commit Chain Invariants

**CC1 — Stage predecessor named.**
Statement: Each conduct stage (except the first) MUST name its `depends_on` predecessor stage.
Violation: Missing.
Response: `passed=False`, `failure_codes=("CC1",)`.

**CC2 — Predecessor exists.**
Statement: A stage's `depends_on` MUST reference an actual prior stage in the same chain.
Violation: Dangling reference.
Response: `passed=False`, `failure_codes=("CC2",)`.

**CC3 — No missing stages.**
Statement: A chain MUST be connected from first to last with no gaps.
Violation: Discontinuity.
Response: `passed=False`, `failure_codes=("CC3",)`.

**CC4 — Stage order enforced.**
Statement: Stages MUST be ordered such that every `depends_on` references an earlier-indexed stage.
Violation: Out-of-order.
Response: `passed=False`, `failure_codes=("CC4",)`.

---

### 2.8.6 Canonicalization Scheme Invariants

**CS1 — Registered scheme.**
Statement: The canonical serialization scheme is registered at the protocol level. v0.1.0: RFC 8785 JCS.
Violation: Use of unregistered scheme.
Response: Kernel rejects on canonicalization mismatch (`passed=False`, `failure_codes=("CS1",)`).

**CS2 — Byte stability.**
Statement: Canonicalize(canonicalize(x)) == canonicalize(x) for any artifact x. Idempotent.
Violation: Output instability.
Response: Drift event (TR-6).

**CS3 — Single-scheme lock at v0.1.0.**
Statement: v0.1.0 ships exactly one canonicalization scheme. Adding a second is a protocol-level event (v0.2+).
Violation: Implementation declares Class A under a different scheme.
Response: Implementation registry rejects the declaration.

---

### 2.8.7 Action Governance Invariants

**AG1 — No auto-authorization.**
Statement: A transition MUST NOT authorize itself. The `authorization.source_id` MUST NOT equal the transition's own `transition_id` or proposer-identity.
Violation: Self-quoted authorization.
Response: `gate.evaluate().authorized=False`, `reason_codes=("AG1",)`. `RefusalRecord` sealed.

**AG2 — No unauthorized attesters (Class C cross-rule).**
Statement: For Class C transitions, every attester in `agreement.attesters` MUST appear in the prior state's authorized-attester registry.
Violation: Unauthorized attester signed.
Response: Kernel rejects (C1 also fires).

**AG3 — Source ID required for action-bearing.**
Statement: An action-bearing transition (`action != null`) MUST carry a non-null `authorization.source_id`.
Violation: Missing.
Response: `gate.evaluate().authorized=False`, `reason_codes=("AG3",)`.

---

### 2.8.8 Implementation Declaration Invariants

**ID1 — Classes declared.**
Statement: An implementation registration MUST list `classes_supported` as a subset of `{A, B, C, D}`.
Violation: Empty or invalid class.
Response: `validate_implementations.py` rejects.

**ID2 — Class-canonicalization compatibility.**
Statement: An implementation declaring Class A MUST satisfy CS1–CS3 (canonicalization conformance). F-1: WISEATA does not satisfy this and registers Class B only.
Violation: Class A declared without canonicalization conformance.
Response: Registration rejected.

**ID3 — Audit-status evidence.**
Statement: `audit_status: CONFORMANT` requires `evidence.conformance_report` AND `evidence.interop_report`, each with `overall_status: PASS` and matching protocol/version.
Violation: Missing or failing evidence.
Response: Registration rejected; defaults to `NOT_AUDITED`.

---

### 2.8.9 Telemetry Discipline (cross-class)

**TEL1 — Telemetry tokens never valid as status.**
Statement: Strings of the form `CALIBRATION_*` MUST NOT appear as the `status` field on any class A/B/C/D artifact.
Violation: Telemetry token in `status`.
Response: Kernel rejects (`passed=False`, `failure_codes=("A3"|"B3"|"C4"|"D1",)` per class).

---

## 2.9 THREAT MODEL

The stack defends against nine adversary classes. Each is named, bounded, and mapped to its kernel response.

### 2.9.1 In-Boundary Adversaries

**T-1 — Careless operator.**
Threat: Honest operator mistake — missing `source_id`, malformed authorization, telemetry token in `status`, missing provenance.
Mitigation: Kernel refuses; `RefusalRecord` sealed; chain intact.
Detection: Class invariant failure (A1–A3, B1–B3, C1–C4, D1–D5).

**T-2 — Misinformed proposer.**
Threat: Proposer generates malformed candidates due to faulty model output (hallucinated provenance, fabricated attesters, contradictory evidence claimed as `SUPPORTED`).
Mitigation: Kernel refuses each malformed candidate; refusal corpus accumulates for proposer evaluation; the proposer can be replaced.
Detection: Repeated kernel rejections recorded in `RefusalRecord.candidates_rejected`.

**T-3 — Implementation drifter.**
Threat: An implementation modifies its behavior between releases without declaration (silent canonicalization change, silent invariant interpretation change).
Mitigation: Suite fingerprints; `make verify-drift`; drift event surfaces as TR-1 / TR-6 / TR-8.
Detection: Reviewer reproduction of `vectors_suite_sha256`, `manifests_suite_sha256`, `corpus_sha256` against published values.

**T-4 — Unauthorized actor.**
Threat: An actor attempts to action a transition without registered authority.
Mitigation: AG3 — gate refuses; `RefusalRecord` sealed.
Detection: `gate.evaluate().authorized=False`, `reason_codes=("AG3",)`.

**T-5 — Auto-authorizer.**
Threat: A transition self-quotes its `authorization.source_id` to bypass the gate.
Mitigation: AG1 — gate refuses self-authorization at evaluation.
Detection: `reason_codes=("AG1",)`.

**T-6 — Audit tamperer.**
Threat: An actor modifies an audit entry after acceptance to alter the historical record.
Mitigation: `verify_chain` walks the chain and recomputes each `this_entry_sha256`; tampering at any position raises `ChainCorrupt`.
Detection: Chain verification failure at the tampered position.

**T-7 — State tamperer.**
Threat: An actor modifies `state.json` to alter `state_id` without going through a transition.
Mitigation: `state_id` is content-addressed over `objects`; load-time recomputation detects mismatch and raises `StateTampered`.
Detection: Mismatch on `RuntimeLoop.__init__` reload.

**T-8 — Cross-class scoper.**
Threat: An implementation (e.g., WISEATA) attempts Class A despite incompatible canonicalization (F-1).
Mitigation: Implementation registry rejects the declaration (ID2); interop checks reject any Class A claim from such implementations.
Detection: Validator failure at `tools/validate_implementations.py` and `interop/scripts/run_interop_checks.py::_rule_wiseata_no_class_a`.

**T-9 — Forbidden-claim spreader.**
Threat: An actor asserts AGI / consciousness / universal correctness on top of the stack as if the stack endorsed those properties.
Mitigation: Forbidden trust claims are spec-forbidden (TP10); the stack's narrowest claim is the only legitimate one.
Detection: Trust law disclosure surface; reviewer challenge.

---

### 2.9.2 Out-of-Boundary Adversaries (operator responsibility)

**T-10 — Physical compromise of the host.**
Out of scope. If the operator's machine is compromised, audit memory and refusal records are compromised.

**T-11 — Network adversaries.**
Out of scope. The default runtime has no network surface; deployments adding network must include their own threat model.

**T-12 — Hardware backdoors.**
Out of scope.

**T-13 — Cryptographic primitive breaks.**
SHA-256 collision resistance and RFC 8785 JCS canonicalization correctness are taken as given. Out of scope.

**T-14 — Compromise of all reviewers.**
Trust model assumes some independent reviewers exist. Universal collusion is out of scope.

---

### 2.9.3 Containment Procedure

When any in-boundary adversary class is encountered, containment proceeds:

1. **Refusal.** Kernel or gate refuses the malformed transition.
2. **Sealing.** `RefusalRecord` written with `challenge_surface_sha256` set to the SHA-256 of the rejected transition's canonical bytes.
3. **Chain extension.** Audit chain extends with the refusal entry; `prev_entry_sha256` links to the previous head.
4. **Operator notification.** Runtime returns `TransitionResult(accepted=False, reason=..., refusal_id=...)`.
5. **Replay.** Reviewer can reconstruct the refusal from the sealed record alone.

Containment is operational normality. Refusal is success.

---

## 2.10 RUNTIME SEMANTICS

This section defines the execution flow of the runtime in sequentially-explainable form. Every step names its module, its inputs, its outputs, and its failure conditions.

### 2.10.1 Initialization

Entry point: `RuntimeLoop(state_dir, audit_dir, proposers, kernel, gate, policies)`.

Steps:

1. Load `state_dir/state.json` if it exists. Compute `state_id_loaded = compute_state_id(loaded.objects)`. Compare against `loaded.state_id`. Mismatch → `StateTampered` (T-7).
2. Load `audit_dir/head.json`. Walk the chain backward, recomputing `this_entry_sha256` at each step. Mismatch → `ChainCorrupt` (T-6).
3. Bind the proposer list, kernel adapter, gate, and policies. v0.1: gate carries `AlwaysDenyPolicy` plus `AllowlistPolicy` per registered policy file.
4. Return ready runtime.

Failure conditions: any of `StateTampered`, `ChainCorrupt`, `PolicyLoadError`, `MissingProposerError`. All are fail-closed.

---

### 2.10.2 Search

Entry point: `RuntimeLoop.search(query: Query) -> SearchResult`.

Steps:

1. For each proposer in order, call `propose(query, current_state) -> list[ProposalCandidate]`.
2. For each candidate:
   - Compute `transition.canonical_bytes_sha256`.
   - Call `kernel.verify(candidate.transition, current_state) -> KernelVerdict`. If `passed == False`, accumulate into `candidates_rejected` and continue.
   - If `candidate.transition.action != null`, call `gate.evaluate(candidate.transition) -> AuthorizationDecision`. If `authorized == False`, accumulate into `candidates_rejected` and continue.
   - Acceptance: call `apply_transition(candidate.transition, kernel_verdict, gate_decision)`.
3. If any candidate was accepted, return `SearchResult(accepted=True, transition=..., audit_entry=...)`.
4. If all candidates were rejected, seal a `RefusalRecord` with `challenge_surface_sha256` set to the SHA-256 over the canonical bytes of the *initial query* (or the last-rejected candidate, per `RefusalRecord.challenge_surface_source` field) and return `SearchResult(accepted=False, refusal=...)`.

Failure conditions: any `KernelError`, `GateError`, or `MemoryError` is fail-closed.

---

### 2.10.3 apply_transition

Entry point: `RuntimeLoop.apply_transition(transition, kernel_verdict, gate_decision)`.

Steps:

1. Compute `new_objects = current_state.objects | transition.delta`.
2. Compute `new_state_id = compute_state_id(new_objects)`.
3. Compute `audit_entry = AuditEntry(...)` with `state_id_after = new_state_id`. Compute `this_entry_sha256` over canonical body with self-field omitted.
4. Atomically write the audit entry file via `os.replace`.
5. Atomically write the new `head.json` pointing to the new entry.
6. Atomically write the updated `state.json`.
7. Return the audit entry.

Atomicity: each write is via temp-file + `os.replace`. Crash between steps 4–6 is detectable on next initialization (chain integrity check).

---

### 2.10.4 Refusal sealing

Entry point: internal to `search`.

Steps:

1. Compute `challenge_surface_sha256 = sha256(canonical_bytes(challenge_surface))`. The challenge surface is the originally-queried transition input (or the last-rejected candidate, per record).
2. Construct `RefusalRecord(transition_id, class_, kernel_verdict, gate_decision, candidates_rejected, challenge_surface_sha256, timestamp, reason_codes)`.
3. Compute `refusal_sha256` over the canonical body.
4. Write the refusal file under `intellagent_audit/refusals/<refusal_sha256>.json` atomically.
5. Append a refusal-marker audit entry to the chain so the refusal participates in chain integrity.

---

### 2.10.5 Chain verification

Entry point: `AuditMemory.verify_chain() -> None`.

Steps:

1. Load head pointer.
2. For each entry from head backward:
   - Load entry from disk.
   - Recompute `this_entry_sha256` over the canonical body with self-field omitted.
   - Compare to recorded `this_entry_sha256`. Mismatch → `ChainCorrupt(entry_id, reason="this_entry_sha256_mismatch")`.
   - Verify `prev_entry_sha256` matches the predecessor's `this_entry_sha256`. Mismatch → `ChainCorrupt(...)`.
3. If walking reaches the genesis (entry with `prev_entry_sha256 == null`) without error, return.

The walk is deterministic and content-addressed at every step.

---

### 2.10.6 Determinism contract

Under (a) pinned clock via `set_clock(...)`, (b) pinned ID source via `set_id_source(...)`, (c) pinned seed for any RNG, (d) the same Provider, and (e) the same prompt + query input:

- Audit memory bytes are byte-identical across runs.
- Refusal records are byte-identical across runs.
- State files are byte-identical across runs.

Live verification: cross-run hash `sha256:b71c7134ef2c33ea5fcc9a3eb723efe6294ba18759ed91d1f64bdfe826107ba5` matches between two clean tmp directories. Documented in `RELEASE-STATUS-v0.1.md` §6.

Out-of-contract surfaces:

- Real-provider sampling (OpenAI, Anthropic) is non-byte-deterministic across machines even under fixed seeds. Mitigation: capture full provider metadata in `proposal_cost`. Replay via `DeterministicMockProvider`.
- Wall-clock timestamps when `set_clock` is not pinned are non-deterministic by design.

---

## 2.11 DATA STRUCTURES

All runtime objects are defined as Python dataclasses. Frozen where mutation is forbidden. Implementation-realistic; no placeholder fields.

### 2.11.1 EpistemicState

```python
from dataclasses import dataclass, field
from typing import Mapping, Any

@dataclass(frozen=True)
class EpistemicState:
    state_id: str
    objects: Mapping[str, Any]
    audit_head: str | None
    refusal_head: str | None
```

Constraints:
- `state_id` is a 64-hex SHA-256 over `canonicalize(objects)`.
- `objects` is an immutable mapping of object-id → object body.
- `audit_head` is `null` for the genesis state, otherwise a 64-hex SHA-256 referencing the latest audit entry.
- `refusal_head` is `null` if no refusal has been sealed yet.

Canonicalization: `state_id` is over `objects` only (not the full struct), avoiding circularity with `audit_head`.

---

### 2.11.2 EpistemicTransition

```python
from dataclasses import dataclass, field
from typing import Mapping, Any

@dataclass(frozen=True)
class EpistemicTransition:
    transition_id: str
    class_: str
    delta: Mapping[str, Any]
    proposer_id: str
    metadata: Mapping[str, Any]
    authorization: "Authorization | None" = None
    action: Mapping[str, Any] | None = None
```

Constraints:
- `transition_id` is content-addressed: SHA-256 over the canonical body with `transition_id` and self-fields excluded.
- `class_` is one of `"A"`, `"B"`, `"C"`, `"D"`.
- `delta` is the object additions/modifications applied by this transition.
- If `action != null`, `authorization` MUST be non-null at gate-time (AG3).

Canonicalization: keys sorted; UTF-8 compact JSON; numbers per RFC 8785.

---

### 2.11.3 Authorization

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Authorization:
    source_id: str
    decision: str  # "authorized" | "denied"
    reason: str | None = None
```

Constraints:
- `source_id` resolves to a registered policy or work order.
- `decision` ∈ `{"authorized", "denied"}`.

---

### 2.11.4 KernelVerdict

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class KernelVerdict:
    passed: bool
    class_: str
    failure_codes: tuple[str, ...]
    details: dict
```

Constraints:
- `failure_codes` is empty when `passed == True`.
- `failure_codes` references invariant IDs from §2.8.

---

### 2.11.5 AuthorizationDecision

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class AuthorizationDecision:
    authorized: bool
    policy_id: str
    source_id: str | None
    reason_codes: tuple[str, ...]
```

Constraints:
- `reason_codes` is empty when `authorized == True`.
- `reason_codes` references AG1, AG2, AG3, or policy-specific codes.

---

### 2.11.6 AuditEntry

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class AuditEntry:
    entry_id: str
    prev_entry_sha256: str | None
    transition_canonical_bytes_sha256: str
    kernel_verdict: KernelVerdict
    gate_decision: AuthorizationDecision | None
    state_id_after: str
    timestamp: str
    this_entry_sha256: str
```

Constraints:
- `entry_id` is sequential within the chain, but the chain integrity does not depend on `entry_id`.
- `prev_entry_sha256` is `null` only on the genesis entry.
- `this_entry_sha256` is SHA-256 over canonical body with `this_entry_sha256` field omitted.

---

### 2.11.7 RefusalRecord

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class RefusalRecord:
    refusal_id: str
    transition_id: str
    class_: str
    kernel_verdict: KernelVerdict | None
    gate_decision: AuthorizationDecision | None
    candidates_rejected: tuple[dict, ...]
    challenge_surface_sha256: str
    timestamp: str
    reason_codes: tuple[str, ...]
    refusal_sha256: str
```

Constraints:
- `refusal_sha256` is content-addressed over the canonical body with `refusal_sha256` excluded.
- `challenge_surface_sha256` MUST be non-empty on every refusal.

---

### 2.11.8 ProposalCandidate

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class ProposalCandidate:
    transition: EpistemicTransition
    provenance: "ProposalProvenance"
```

```python
@dataclass(frozen=True)
class ProposalProvenance:
    proposer_id: str
    provider_id: str | None
    prompt_sha256: str | None
    seed: int | None
    timestamp: str
```

---

### 2.11.9 TransitionResult / SearchResult

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class TransitionResult:
    accepted: bool
    reason: str
    audit_hash: str | None
    refusal_id: str | None

@dataclass(frozen=True)
class SearchResult:
    accepted: bool
    transition: EpistemicTransition | None
    audit_entry: AuditEntry | None
    refusal: RefusalRecord | None
    candidates_rejected: tuple[dict, ...]
```

Constraints:
- `accepted == True` ⇒ `transition` and `audit_entry` non-null; `refusal` null.
- `accepted == False` ⇒ `refusal` non-null; `transition` and `audit_entry` null.

---

### 2.11.10 Provider Protocol

```python
# interface example
from typing import Protocol
from dataclasses import dataclass

@dataclass(frozen=True)
class GenerationParams:
    seed: int | None
    temperature: float
    max_tokens: int
    stop_sequences: tuple[str, ...]

@dataclass(frozen=True)
class CompletionResult:
    text: str
    provider_id: str
    model_id: str
    tokens_in: int
    tokens_out: int
    finish_reason: str
    provider_metadata: dict

class Provider(Protocol):
    def complete(self, prompt: str, params: GenerationParams) -> CompletionResult:
        ...
```

The Provider Protocol is the boundary between transformer-proposer and the underlying model. Four implementations ship at v0.1 (§2.6 Definitions, "Provider").

---

