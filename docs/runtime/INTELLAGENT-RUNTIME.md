# INTELLAGENT Runtime v0.1

## Legitimate Transition Search Engine

**Status:** Runtime specification, draft.
**Companion to:** [`INTELLAGENT.md`](./INTELLAGENT.md) (architecture proposal) and [`SPEC.md`](./SPEC.md) (governance kernel).
**Position:** *First buildable Intellagent prototype. No AI model required for v0.1.*

> Inference is not next-token prediction.
> Inference is **legitimate transition search**.

---

## 1. Purpose

This document specifies the first buildable Intellagent runtime: a governed epistemic state transition engine that proves the architecture's central claim — that cognition can be implemented as a state machine over a governance kernel, separate from any specific proposer (transformer or otherwise).

The v0.1 runtime answers four questions, mechanically:

1. **Can a typed transition between epistemic states be checked for legitimacy by the existing WiseOrder kernel?** Yes — the runtime uses the kernel already on disk.
2. **Can legitimate transitions be sealed into an append-only audit memory whose commit chain detects tampering?** Yes — the runtime's `AuditMemory` is a content-addressed commit chain.
3. **Can an action-bearing transition be refused for missing authorization, independently of its verification status?** Yes — the runtime's `AuthorizationGate` enforces `AG1`–`AG3` separately from kernel verdicts.
4. **Can refusal itself be a structured, auditable artifact?** Yes — the runtime emits a `RefusalRecord` with the full challenge surface every time no legitimate transition extends the state toward the query.

The runtime does NOT yet answer:

- Whether learned proposers (transformers) can be plugged in usefully.
- Whether the runtime scales beyond toy-state working volumes.
- Whether the kernel's class structure is sufficient for production cognition.

Those questions are deferred to v0.2 and beyond. The point of v0.1 is to prove the architecture's claims are mechanizable, end-to-end, with hand-written proposals only.

---

## 2. Runtime Scope

### In scope (v0.1)

- A Python package, `intellagent_runtime/`, sitting alongside `tools/` and `interop/` in this repository.
- A CLI, `intellagent`, exposing six commands: `init`, `state`, `propose`, `transition`, `audit`, `refuse`.
- A `WiseOrderKernel` adapter that calls the existing conformance tooling (`tools/validate_*.py`, `vectors/`, `schemas/`) to verify transitions.
- An append-only `AuditMemory` backed by a directory of canonical JSON files, commit-chained by SHA-256.
- An `AuthorizationGate` that enforces `AG1`–`AG3` for any transition that declares an `action`.
- A static / manual `Proposer` interface — proposals authored by hand or read from disk.
- A pytest test suite alongside the existing `tests/`, asserting determinism, append-chain integrity, refusal sealing, and authorization gating.

### Out of scope (deferred)

- Any learned proposer (transformer, planner, retrieval).
- Distributed / multi-party audit memory.
- Cross-version migration of audit memories.
- Performance optimization beyond correctness.
- A graphical interface.
- A network protocol.
- Persistence across machines (local single-host only).

---

## 3. Non-Goals

The v0.1 runtime is explicitly **not**:

1. An AI model. There is no neural network in v0.1. The proposer is human-authored or static.
2. A replacement for the kernel. The kernel is WiseOrder Protocol v0.1.0, in [`SPEC.md`](./SPEC.md). The runtime is a thin shell *around* the kernel, not a competing one.
3. A capability demonstration. The runtime does no useful task. Its only claim is *the architecture's primitives compose correctly*.
4. A consensus engine. Class C transitions are admitted by the runtime, but multi-party consensus protocols are out of scope.
5. A general-purpose knowledge representation system. Epistemic objects are minimally structured — enough for the kernel to verify them, no more.
6. A proof of intelligence. Nothing about v0.1 implies the system is intelligent. It implies that *if* an intelligent proposer were plugged in, the architecture's guarantees would still hold.

What v0.1 *does* claim: governed transitions, append-only audit, separately-authorized action, and structured refusal — composed end-to-end, testable end-to-end, with no hidden state.

---

## 4. Runtime Components

Seven components, each a single Python module:

| Component | Module | Responsibility |
| --- | --- | --- |
| **StateStore** | `intellagent_runtime/state.py` | Holds the working epistemic state. Loads/saves canonical JSON. Computes content-addressed `state_id`. |
| **AuditMemory** | `intellagent_runtime/memory.py` | Append-only commit chain of `AuditEntry` records. Verifies chain integrity on read. Refuses non-append writes. |
| **Transition** | `intellagent_runtime/transitions.py` | Pure data type. `EpistemicTransition`, `TransitionResult`. No I/O. |
| **Proposer** | `intellagent_runtime/proposer.py` | Interface + v0.1 implementations: `StaticProposer` (reads from a file), `ManualProposer` (reads from stdin). |
| **WiseOrderKernel** | `intellagent_runtime/kernel.py` | Adapter over the existing conformance tooling. Single API: `verify(transition, prior_state) → (passed, failures)`. |
| **AuthorizationGate** | `intellagent_runtime/authorization.py` | Enforces `AG1`–`AG3`. Resolves declared `authorization_source`, applies its policy, returns `AuthorizationDecision`. |
| **RuntimeLoop** | `intellagent_runtime/runtime.py` | Orchestrates: query → propose → kernel verify → authorization gate → audit append (or refusal). |

A `cli.py` module wires components to the `intellagent` command. Nothing in any other component module touches `argparse` or `sys.argv`.

The boundary is strict: **no component except `RuntimeLoop` knows about more than its own neighbors.** `StateStore` does not call `AuditMemory`. `Kernel` does not write. `AuthorizationGate` does not propose.

---

## 5. Core Data Types

All types are JSON-serializable and have a deterministic canonical form (sorted keys, compact separators, UTF-8). Canonical forms are reproducible across runs and machines.

### 5.1 EpistemicObject

A structured assertion plus the metadata required to evaluate it.

```json
{
  "object_id":   "<sha256: of canonical body>",
  "class":       "A | B | C | D",
  "regime":      "<regime label per SPEC.md §3>",
  "claim":       "<structured claim>",
  "evidence":    "<regime-appropriate>",
  "provenance":  { "witness": "<name>", "at": "<ISO-8601 UTC>" },
  "lineage":     [ "<prior object_id>", ... ],
  "status":      "<status from STATUS-REGISTRY.md>"
}
```

`object_id` is the SHA-256 of the canonical JSON of the object with `object_id` itself omitted. This makes objects content-addressed.

### 5.2 EpistemicState

```json
{
  "state_id":          "<sha256: of canonical body>",
  "objects":           [ "<object_id>", ... ],
  "audit_head_sha256": "<sha256: of last audit entry, or null if empty>",
  "sealed_at":         "<ISO-8601 UTC>"
}
```

`state_id` is the SHA-256 of the canonical JSON of the state with `state_id` omitted. The state is also content-addressed; identical object sets with identical audit history yield identical `state_id`.

### 5.3 EpistemicTransition

```json
{
  "transition_id":  "<stable id, e.g. ULID or sha256: of canonical body>",
  "from_state":     "<state_id>",
  "regime":         "A | B | C | D",
  "object_added":   "<EpistemicObject>",
  "objects_removed": [ "<object_id>", ... ],
  "action":         "<Action> | null",
  "authorization":  "<Authorization> | null",
  "proposer":       "<name>",
  "proposed_at":    "<ISO-8601 UTC>"
}
```

A transition is **action-bearing** iff `action` is non-null. An action-bearing transition without a non-null `authorization` is rejected by the kernel before ever reaching the gate (`AG1` enforced at proposal time).

`Action` shape:

```json
{ "kind": "<verb>", "target": "<resource>", "payload": { ... } }
```

`Authorization` shape:

```json
{ "source_id": "<named authorization source>", "rationale": "<text>" }
```

### 5.4 TransitionResult

```json
{
  "transition_id":     "<id>",
  "legitimate":        true | false,
  "failures":          [ "<reason>", ... ],
  "resulting_state":   "<state_id> | null",
  "committed_to":      "<audit_entry index> | null",
  "checked_at":        "<ISO-8601 UTC>"
}
```

### 5.5 AuditEntry

```json
{
  "index":              "<integer ≥ 0>",
  "transition":         "<EpistemicTransition>",
  "prior_state_id":     "<state_id>",
  "resulting_state_id": "<state_id>",
  "prev_entry_sha256":  "<sha256: of prior entry, or null for index 0>",
  "this_entry_sha256":  "<sha256: of this entry's canonical body without this field>",
  "sealed_at":          "<ISO-8601 UTC>"
}
```

`this_entry_sha256` is computed over the canonical JSON of the entry with `this_entry_sha256` itself omitted. The chain links entry *n* to entry *n−1* via `prev_entry_sha256` matching the prior `this_entry_sha256`.

### 5.6 RefusalRecord

```json
{
  "refusal_id":               "<stable id>",
  "query":                    "<serialized query>",
  "from_state":               "<state_id>",
  "candidates_rejected":      [
    {
      "candidate_id":         "<transition_id>",
      "regime":               "A | B | C | D",
      "legitimacy_failures":  [ "<reason>", ... ]
    }
  ],
  "challenge_surface_sha256": "<sha256: of canonical candidates_rejected>",
  "refused_at":               "<ISO-8601 UTC>"
}
```

Refusal is a sealed artifact, not a side effect. An empty `candidates_rejected` is invalid (`D3`: no challenge surface = invalid conduct).

### 5.7 AuthorizationDecision

```json
{
  "decision_id":          "<stable id>",
  "transition_id":        "<the action-bearing transition>",
  "authorized":           true | false,
  "authorization_source": "<source_id> | null",
  "rationale":            "<text, mandatory>",
  "decided_at":           "<ISO-8601 UTC>"
}
```

`AG3` is structurally enforced: every decision carries `authorization_source` (or null with explicit `rationale` explaining why) and `rationale`.

---

## 6. Epistemic State Model

### 6.1 State as content-addressed ledger view

The state is the multiset of currently-held epistemic objects, expressed as their `object_id`s. Object bodies live in a separate content-addressed object store (a directory keyed by `object_id`).

This separation matters for two reasons:

1. **State diffs are cheap.** Two states differ iff their object-id sets differ; pointer comparison rather than value comparison.
2. **Object reuse is structural.** The same epistemic object referenced from many states exists once on disk and once in memory.

### 6.2 Sealing

A state is **sealed** by computing its `state_id` (SHA-256 of canonical body, with `state_id` itself omitted). Once sealed, the state is immutable; any modification produces a new state with a new `state_id`.

### 6.3 Initial state

`intellagent init` creates a state with no objects, no audit history:

```json
{ "objects": [], "audit_head_sha256": null, "sealed_at": "<now>" }
```

Whose `state_id` is fixed (modulo the timestamp; if `sealed_at` is also pinned by the init seed, the initial `state_id` is fully reproducible across machines).

### 6.4 Loading and persistence

`StateStore` reads the current state from `intellagent_state/current.json` and writes to it atomically (write-temp + rename). Loading verifies the on-disk `state_id` matches the recomputed one; mismatches fail-closed.

---

## 7. Transition Model

### 7.1 What a transition encodes

Each transition records exactly three things, plus envelope metadata:

1. **One epistemic object added** to the state (`object_added`). May be null if the transition only removes.
2. **Zero or more objects removed** from the state (`objects_removed`). Removal of a never-held object fails-closed.
3. **Optional action** with mandatory authorization. Pure state transitions have `action: null` and `authorization: null`.

### 7.2 Why one-object-added per transition

A multi-object transition can always be decomposed into a sequence of single-object transitions, and each step is then individually verifiable by the kernel. This keeps the kernel's per-step check unambiguous and the audit memory granular. v0.2 may relax this if measured cost of granularity proves prohibitive.

### 7.3 Forgetting is a transition

A transition with non-empty `objects_removed` is the only way to remove objects from state. The transition itself is recorded in audit memory; the *fact* that the system used to know X is preserved even after X is no longer in the working state. This honors `CC1`: removing an object from working state does not erase its audit record.

### 7.4 Action-bearing transitions

A transition with `action` non-null is action-bearing. The kernel rejects any action-bearing transition without `authorization` non-null. The `AuthorizationGate` then evaluates `authorization` against the named source's policy. Both gates must pass for the transition to commit.

---

## 8. Proposer Interface

### 8.1 Protocol

```python
class Proposer(Protocol):
    name: str

    def propose(
        self,
        state: EpistemicState,
        query: Query,
        rejected: list[tuple[EpistemicTransition, list[str]]],
    ) -> list[EpistemicTransition]:
        """Return zero or more candidate transitions that might extend `state`
        toward `query`. The runtime will verify each candidate against the
        kernel; rejected candidates from prior iterations are passed in so a
        learning proposer can adapt. Pure-static proposers may ignore them."""
```

### 8.2 v0.1 implementations

**`StaticProposer`** — reads candidates from a file given at construction:

```python
StaticProposer(name="static", path="proposals/winstack-class-a-1.json")
```

The file is a JSON array of transition objects. The proposer returns all of them on the first call and an empty list thereafter (one-shot).

**`ManualProposer`** — reads a single candidate from stdin per `propose` call:

```python
ManualProposer(name="manual")
```

The user pastes a JSON transition object into the terminal. EOF returns an empty candidate list (terminating the search loop).

### 8.3 Future implementations (out of scope for v0.1)

- `RetrievalProposer` — looks up similar prior states in audit memory.
- `TransformerProposer` — wraps an LLM, prompts with the serialized state and query, parses transitions from the output.
- `EnsembleProposer` — combines the above.

The interface does not change between v0.1 and v0.2+. This is the architectural promise: **the proposer is replaceable; the kernel is not**.

---

## 9. Verifier / Kernel Interface

### 9.1 Adapter shape

The kernel adapter is a small class with two public entry points: a
constructor that accepts an optional `repo_root` for resolving schemas, and
`verify(transition, prior_state) -> KernelVerdict`. The full implementation
lives at [`intellagent_runtime/kernel.py`](./intellagent_runtime/kernel.py).
Public surface:

```python
# interface example
from pathlib import Path
from typing import Protocol


class KernelInterface(Protocol):
    def verify(
        self,
        transition: EpistemicTransition,
        prior_state: EpistemicState,
    ) -> KernelVerdict:
        """Run all WiseOrder invariants for transition.regime against
        transition.object_added, plus cross-checks involving prior_state
        (lineage validity, removed-object presence, AG1 at proposal time).
        Returns a verdict with an explicit failure list."""
        ...
```

The concrete class registered with the runtime is
`intellagent_runtime.kernel.WiseOrderKernel`, which constructs as
`WiseOrderKernel(repo_root: Path | None = None)` and dispatches `verify` to
per-class internal verifiers (`_verify_class_a_object`, `_verify_class_b_object`,
`_verify_class_c_object`, `_verify_class_d_object`) plus the cross-cutting
checks for AG1, regime/class match, and `objects_removed` presence.

### 9.2 What the adapter calls

The kernel adapter does **not** reimplement the WiseOrder validators. It reuses what's already in this repository:

| Regime | Reuses | Action |
| --- | --- | --- |
| **A** | `schemas/vector.schema.json` (Class A invariants), patterns from `vectors/class-a-*.json` | Validate `object_added` as a Class A artifact: required fields, RFC8785-JCS canonicalization, status compatible with digest comparison. |
| **B** | Patterns from `vectors/class-b-*.json` | Validate sources declared, contradiction preservation, ordering auditability. |
| **C** | Patterns from `vectors/class-c-*.json`, plus `tools/validate_implementations.py`'s rule machinery for action-policy semantics | Validate consensus rules declared before collection, eligible attesters, action_policy structure. |
| **D** | Patterns from `vectors/class-d-*.json` | Validate values_frame, alternatives, challenge_surface, commit-chain integrity, preimage presence. |
| **All** | `schemas/vector.schema.json` enum logic | Reject telemetry tokens (`CALIBRATION_*`) used as artifact statuses. |

In v0.1 the adapter is allowed to inline simple structural checks rather than dispatching to vector-driven test runners. The constraint is correctness, not architecture-purity. v0.2 may unify all of this through a single `verify_artifact_against_class.py` module under `tools/`.

### 9.3 KernelVerdict

```python
@dataclass
class KernelVerdict:
    passed: bool
    failures: list[str]   # each item: "<rule_id>: <message>"
    checked_at: str
```

A verdict's `failures` are stable strings; the runtime treats them as opaque text to display in `RefusalRecord`s and as keys for higher-layer learning loops in v0.2.

---

## 10. Legitimate Transition Search Loop

The core inference primitive of the runtime. The implementation lives in
[`intellagent_runtime/runtime.py`](./intellagent_runtime/runtime.py) as
`RuntimeLoop.search`. Reproduced here verbatim:

```python
from intellagent_runtime.refusal import RefusalRecord, RefusalStore
from intellagent_runtime.kernel import WiseOrderKernel
from intellagent_runtime.authorization import AuthorizationGate
from intellagent_runtime.memory import AuditMemory
from intellagent_runtime.state import EpistemicState, StateStore
from intellagent_runtime.transitions import EpistemicTransition


class RuntimeLoop:
    def __init__(
        self,
        base_dir: Path,
        kernel: WiseOrderKernel,
        gate: AuthorizationGate,
    ) -> None:
        self.base = Path(base_dir)
        self.store = StateStore(self.base)
        self.audit = AuditMemory(self.base / "intellagent_audit")
        self.refusals = RefusalStore(self.base / "intellagent_refusals")
        self.kernel = kernel
        self.gate = gate

    def search(
        self,
        query: Query,
        proposer,
        max_iters: int = 64,
    ) -> SearchResult:
        # Re-verify the chain on entry; fail closed if corrupt.
        self.audit.verify_chain()
        state = self.store.load()
        rejected: list[tuple[EpistemicTransition | None, list[str]]] = []

        if max_iters <= 0:
            refusal = self.refusals.seal(
                query=query.serialize(),
                from_state_id=state.state_id,
                rejected=[(None, ["budget_exhausted"])],
            )
            return SearchResult(False, state, self.audit.head_sha256(), refusal)

        for _ in range(max_iters):
            if query.satisfied_by(state):
                return SearchResult(True, state, self.audit.head_sha256(), None)

            candidates = proposer.propose(state, query, rejected)
            if not candidates:
                refusal = self.refusals.seal(
                    query=query.serialize(),
                    from_state_id=state.state_id,
                    rejected=rejected,
                )
                return SearchResult(False, state, self.audit.head_sha256(), refusal)

            committed_this_iter = False
            for tau in candidates:
                verdict = validate_transition(tau, state, self.kernel)
                if not verdict.passed:
                    rejected.append((tau, verdict.failures))
                    continue
                if tau.is_action_bearing:
                    decision = self.gate.evaluate(tau, state)
                    if not decision.authorized:
                        rejected.append((tau, [f"AG: {decision.rationale}"]))
                        continue
                state, _ = apply_transition(tau, state, self.store, self.audit)
                committed_this_iter = True
                break

            if not committed_this_iter:
                refusal = self.refusals.seal(
                    query=query.serialize(),
                    from_state_id=state.state_id,
                    rejected=rejected,
                )
                return SearchResult(False, state, self.audit.head_sha256(), refusal)

        # Exhausted iteration budget without satisfying.
        refusal = self.refusals.seal(
            query=query.serialize(),
            from_state_id=state.state_id,
            rejected=rejected if rejected else [(None, ["budget_exhausted"])],
        )
        return SearchResult(False, state, self.audit.head_sha256(), refusal)
```

Key properties:

1. **The proposer is queried repeatedly until satisfaction or refusal.** Each iteration may yield zero, one, or many candidates.
2. **The first legitimate (and authorized, if action-bearing) candidate wins.** No backtracking in v0.1; v0.2 may add it.
3. **Rejected candidates accumulate.** They are passed back to the proposer (so a learning proposer can adapt) and ultimately into the `RefusalRecord` if the search terminates without satisfaction.
4. **Refusal is the same shape regardless of why.** Empty proposer output, all-rejected proposals, exceeded budget — all produce a `RefusalRecord` with the full challenge surface.
5. **Audit memory grows monotonically inside the loop.** Even partial paths that terminate in refusal leave their committed transitions sealed.

---

## 11. Audit Memory Model

### 11.1 On-disk shape

`intellagent_audit/` is a directory of canonical JSON files, one per entry:

```
intellagent_audit/
├── 0000.entry.json
├── 0001.entry.json
├── 0002.entry.json
└── ...
```

Filenames are zero-padded indices. Each file is the canonical JSON of one `AuditEntry`.

### 11.2 Append (implementation)

The implementation lives in
[`intellagent_runtime/memory.py`](./intellagent_runtime/memory.py) as
`AuditMemory.append`. Reproduced here verbatim:

```python
from intellagent_runtime.canonical import (
    canonical_json_bytes,
    canonical_pretty,
    sha256_hex,
    utcnow_iso8601,
    write_atomic,
)
from intellagent_runtime.transitions import EpistemicTransition


def _filename_for(index: int) -> str:
    return f"{index:04d}.entry.json"


class AuditMemory:
    def append(
        self,
        transition: EpistemicTransition,
        prior_state_id: str,
        resulting_state_id: str,
    ) -> AuditEntry:
        index = self.next_index()
        prev = self.head_sha256()
        body_without_self = {
            "index":              index,
            "transition":         transition.to_dict(),
            "prior_state_id":     prior_state_id,
            "resulting_state_id": resulting_state_id,
            "prev_entry_sha256":  prev,
            "sealed_at":          utcnow_iso8601(),
        }
        this_sha = sha256_hex(canonical_json_bytes(body_without_self))
        full_body = {**body_without_self, "this_entry_sha256": this_sha}

        self.dir.mkdir(parents=True, exist_ok=True)
        path = self.dir / _filename_for(index)
        write_atomic(path, canonical_pretty(full_body))
        return AuditEntry(**full_body)
```

`write_atomic` writes to a temp file then renames. Crash mid-write does not leave a half-written entry visible to readers.

### 11.3 Chain verification

On every read of `AuditMemory`, the runtime verifies the chain via
`AuditMemory.verify_chain` in
[`intellagent_runtime/memory.py`](./intellagent_runtime/memory.py).
Reproduced here verbatim:

```python
import json
from intellagent_runtime.canonical import canonical_json_bytes, sha256_hex


class ChainCorrupt(Exception):
    """The audit memory chain has been tampered with or otherwise broken."""


class AuditMemory:
    def verify_chain(self) -> None:
        """Walk the chain, recomputing each entry's hash and checking links.

        Raises ChainCorrupt if any entry's recomputed hash mismatches its
        declared one or if any prev pointer fails to link.
        """
        prev_hash: str | None = None
        for i, path in enumerate(self._entry_paths()):
            try:
                body = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise ChainCorrupt(f"{path}: cannot parse entry: {exc}") from exc

            if body.get("index") != i:
                raise ChainCorrupt(
                    f"{path}: entry.index={body.get('index')!r} does not "
                    f"match position {i}"
                )

            declared_self = body.get("this_entry_sha256")
            without_self = {
                k: v for k, v in body.items() if k != "this_entry_sha256"
            }
            recomputed = sha256_hex(canonical_json_bytes(without_self))
            if declared_self != recomputed:
                raise ChainCorrupt(
                    f"{path}: this_entry_sha256 mismatch "
                    f"(declared {declared_self}, recomputed {recomputed})"
                )

            declared_prev = body.get("prev_entry_sha256")
            if declared_prev != prev_hash:
                raise ChainCorrupt(
                    f"{path}: prev_entry_sha256={declared_prev!r} does not "
                    f"link to prior entry's hash {prev_hash!r}"
                )

            prev_hash = declared_self
```

A corrupt or tampered chain fails-closed: the runtime refuses to operate on it without explicit operator override.

### 11.4 What audit memory does not do

- It does not encrypt entries. v0.1 is single-host and trusts disk.
- It does not sign entries. v0.2 may add per-entry signatures from a witness key.
- It does not support deletion or rewrite. The only legitimate way to "forget" is a removal-transition that itself becomes a new entry.

---

## 12. Refusal Semantics

### 12.1 When refusal fires

The runtime emits a `RefusalRecord` whenever:

1. The proposer returns an empty candidate list.
2. Every candidate the proposer returns fails the kernel verifier.
3. Every candidate that passes the kernel verifier fails the authorization gate.
4. The maximum iteration budget is reached without satisfaction.

In all four cases, the structure is identical: a record with the query, the from-state, and the full list of rejected candidates with their failure reasons.

### 12.2 Refusal sealing (implementation)

The implementation lives in
[`intellagent_runtime/refusal.py`](./intellagent_runtime/refusal.py) as
`RefusalStore.seal` plus the `_challenge_surface` helper. Reproduced here
verbatim:

```python
from typing import Any
from intellagent_runtime.canonical import (
    canonical_json_bytes,
    canonical_pretty,
    sha256_hex,
    short_id,
    utcnow_iso8601,
    write_atomic,
)
from intellagent_runtime.transitions import EpistemicTransition


def _challenge_surface(
    rejected: list[tuple[EpistemicTransition | None, list[str]]],
) -> tuple[list[dict[str, Any]], str]:
    entries: list[dict[str, Any]] = []
    for tau, failures in rejected:
        entries.append({
            "candidate_id": (tau.transition_id if tau else "no-candidate"),
            "regime":       (tau.regime if tau else None),
            "legitimacy_failures": list(failures),
        })
    canonical = canonical_json_bytes(entries)
    return entries, sha256_hex(canonical)


class RefusalStore:
    def seal(
        self,
        query: str,
        from_state_id: str,
        rejected: list[tuple[EpistemicTransition | None, list[str]]],
    ) -> RefusalRecord:
        # D3: a refusal with no challenge surface is malformed.
        if not rejected:
            rejected = [(None, ["proposer_returned_no_candidates"])]
        entries, challenge_sha = _challenge_surface(rejected)
        refusal = RefusalRecord(
            refusal_id="refusal-" + short_id(),
            query=query,
            from_state=from_state_id,
            candidates_rejected=entries,
            challenge_surface_sha256=challenge_sha,
            refused_at=utcnow_iso8601(),
        )
        self.dir.mkdir(parents=True, exist_ok=True)
        path = self.dir / f"{refusal.refusal_id}.json"
        write_atomic(path, canonical_pretty(refusal.to_dict()))
        return refusal
```

### 12.3 Refusal as first-class output

Refusal is **not an error.** The runtime returns a `RefusalRecord` from `search()` exactly as it returns a satisfied state. Callers that need a hard error must opt in via a flag; by default, refusal is a normal return value.

This is the architectural inversion that makes Intellagent useful: a system that distinguishes "I cannot legitimately produce an answer" from "the answer is X" is a system that can be relied on. Transformers cannot make that distinction by construction.

---

## 13. Authorization Boundary

### 13.1 Who calls the gate

Only `RuntimeLoop` calls `AuthorizationGate.evaluate`. The gate is invoked **after** the kernel has accepted a transition's verification but **before** the transition is committed to audit memory.

### 13.2 Gate evaluation (implementation)

The implementation lives in
[`intellagent_runtime/authorization.py`](./intellagent_runtime/authorization.py)
as `AuthorizationGate.evaluate`. Reproduced here verbatim:

```python
from intellagent_runtime.canonical import short_id, utcnow_iso8601
from intellagent_runtime.transitions import EpistemicTransition


class AuthorizationGate:
    def evaluate(
        self,
        transition: EpistemicTransition,
        prior_state,
    ) -> AuthorizationDecision:
        if not transition.is_action_bearing:
            return AuthorizationDecision(
                decision_id=short_id(),
                transition_id=transition.transition_id,
                authorized=True,
                authorization_source="not-action-bearing",
                rationale=(
                    "Pure state transition; no external action; "
                    "AG1 not engaged."
                ),
                decided_at=utcnow_iso8601(),
            )

        if transition.authorization is None:
            return AuthorizationDecision(
                decision_id=short_id(),
                transition_id=transition.transition_id,
                authorized=False,
                authorization_source=None,
                rationale=(
                    "AG1: action-bearing transition without declared "
                    "authorization. Refused before policy lookup."
                ),
                decided_at=utcnow_iso8601(),
            )

        source_id = transition.authorization.source_id
        if not source_id:
            return AuthorizationDecision(
                decision_id=short_id(),
                transition_id=transition.transition_id,
                authorized=False,
                authorization_source=None,
                rationale="AG3: authorization object missing source_id.",
                decided_at=utcnow_iso8601(),
            )

        policy = self.resolve_policy(source_id)  # local lookup; no network
        if policy is None:
            return AuthorizationDecision(
                decision_id=short_id(),
                transition_id=transition.transition_id,
                authorized=False,
                authorization_source=source_id,
                rationale=(
                    f"AG2: authorization_source {source_id!r} has no "
                    "resolvable policy."
                ),
                decided_at=utcnow_iso8601(),
            )

        allow, rationale = policy.evaluate(transition)
        return AuthorizationDecision(
            decision_id=short_id(),
            transition_id=transition.transition_id,
            authorized=allow,
            authorization_source=source_id,
            rationale=rationale,
            decided_at=utcnow_iso8601(),
        )
```

### 13.3 Policy registry

A simple JSON file at `intellagent_runtime/policies/<source_id>.json` describes the policy a source enforces. v0.1 supports two policy kinds:

1. **`always_deny`** — useful for testing; the source exists but never authorizes anything.
2. **`allowlist`** — a list of `(action.kind, action.target)` pairs the source authorizes.

v0.2 may add programmable policies. v0.1 keeps the surface small and deterministic.

### 13.4 What the gate refuses to do

- The gate does **not** call into the kernel. Authorization is independent of verification (`AG1`).
- The gate does **not** consult the proposer.
- The gate does **not** decide based on the transition's `regime`. Regime governs verification; authorization governs action. The two channels are independent by design.

---

## 14. Error States

The runtime distinguishes seven error states. Each has a stable name, an exit code (for the CLI), and an audited record.

| Name | When | Exit code | Recorded as |
| --- | --- | --- | --- |
| `OK` | Search satisfied the query. | 0 | Audit entry |
| `REFUSED` | Search returned a `RefusalRecord`. | 0 | Refusal record |
| `KERNEL_INVALID` | A proposed transition violates schema or invariants. | (per-candidate, internal) | Refusal candidate-failure entry |
| `AUTHORIZATION_DENIED` | Action-bearing transition rejected by the gate. | (per-candidate, internal) | Refusal candidate-failure entry |
| `CHAIN_CORRUPT` | Audit memory chain integrity check failed on read. | 2 | Stderr; runtime refuses to extend the chain |
| `STATE_TAMPERED` | Working state's recomputed `state_id` does not match disk. | 2 | Stderr; runtime refuses to load |
| `BUDGET_EXHAUSTED` | Search hit `max_iters` without satisfaction. | 0 | Refusal record (`reason: budget_exhausted`) |

`OK` and `REFUSED` are both exit-code 0 because both are **legitimate runtime outputs**. A non-zero CLI exit means the runtime itself is in a bad state, not that the cognition concluded a refusal.

---

## 15. CLI Prototype

The `intellagent` command. All commands operate on the current working directory's `intellagent_state/`, `intellagent_audit/`, and `intellagent_refusals/` directories.

### 15.1 `intellagent init`

Initialize a runtime in the current directory.

```
$ intellagent init
Initialized:
  intellagent_state/      (working state)
  intellagent_audit/      (append-only audit memory)
  intellagent_refusals/   (refusal records)
  intellagent_objects/    (content-addressed object store)

State id: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

Refuses to overwrite an existing runtime; requires `--force` to re-init (which itself emits a refusal record explaining why the prior runtime was discarded).

### 15.2 `intellagent state`

Print the current state.

```
$ intellagent state
state_id:          sha256:e3b0c4...
objects:           []
audit_head_sha256: null
sealed_at:         2026-05-06T12:00:00Z
```

Flags: `--json` (machine readable), `--objects` (resolve object_ids to bodies), `--history N` (show last N audit entries inline).

### 15.3 `intellagent propose`

Submit a proposed transition for verification. Does not commit.

```
$ intellagent propose --file transition.json
proposal_id: prop-87a3f1
regime:      A
will_check:  Class A invariants (A1, A2, A3, CS1, CS2, CS3)
status:      QUEUED
```

The proposal is staged in `intellagent_state/queue/<proposal_id>.json`. Multiple proposals can be queued; `intellagent transition` consumes one at a time.

Flags: `--stdin` (read transition body from stdin), `--regime A|B|C|D` (declare upfront; must match the body), `--proposer NAME`.

### 15.4 `intellagent transition`

Run the kernel verifier (and gate, if action-bearing) on a queued proposal. Commit on success; refuse on failure.

```
$ intellagent transition prop-87a3f1
verifying:        prop-87a3f1
regime:           A
kernel:           PASSED (A1, A2, A3, CS1, CS2, CS3)
authorization:    NOT_APPLICABLE (transition is not action-bearing)
result:           LEGITIMATE
committed:        audit entry 0000
new state id:     sha256:7a9d2f...
```

On failure:

```
$ intellagent transition prop-99cd...
verifying:     prop-99cd...
regime:        D
kernel:        FAILED
  ↳ D3: challenge_surface is empty
  ↳ CC1: stage 2 hash without preimage content
result:        REJECTED (added to next refusal's challenge surface)
```

Flags: `--all` (process every queued proposal), `--dry-run` (verify but do not commit).

### 15.5 `intellagent audit`

Print audit memory entries.

```
$ intellagent audit --range 0:5
[
  { "index": 0, "regime": "A", "from": "sha256:e3b0c4...", "to": "sha256:7a9d2f...", ... },
  { "index": 1, "regime": "B", ... },
  ...
]
```

Flags: `--range FROM:TO`, `--json`, `--verify` (recompute the chain on the fly and report integrity).

### 15.6 `intellagent refuse`

Seal an explicit refusal for a query whose proposer queue is empty or fully rejected.

```
$ intellagent refuse --query "verify provenance of artifact X"
refusal_id:                refusal-c1e2a4
candidates_rejected:       3
challenge_surface_sha256:  sha256:b81f0c...
refused_at:                2026-05-06T12:30:42Z
sealed_to:                 intellagent_refusals/refusal-c1e2a4.json
```

This is the *manual* refusal command, used when an operator wants to emit a sealed refusal without running a full search. The `RuntimeLoop` produces refusals automatically when search terminates without satisfaction.

---

## 16. Minimal File Layout

```
wiseorder-protocol/                            (existing; unchanged)
├── INTELLAGENT.md                              (existing; unchanged)
├── INTELLAGENT-RUNTIME.md                      (this file)
├── SPEC.md                                     (existing; unchanged)
├── tools/                                      (existing; unchanged)
├── vectors/                                    (existing; unchanged)
├── interop/                                    (existing; unchanged)
├── reports/                                    (existing; unchanged)
├── tests/                                      (existing; new tests added under tests/)
│   ├── test_intellagent_state.py               (NEW; v0.1)
│   ├── test_intellagent_memory.py              (NEW; v0.1)
│   ├── test_intellagent_kernel.py              (NEW; v0.1)
│   ├── test_intellagent_authorization.py       (NEW; v0.1)
│   ├── test_intellagent_runtime.py             (NEW; v0.1)
│   └── test_intellagent_cli.py                 (NEW; v0.1)
└── intellagent_runtime/                        (NEW; v0.1 lives here)
    ├── __init__.py
    ├── state.py                                (StateStore, EpistemicState, EpistemicObject)
    ├── transitions.py                          (EpistemicTransition, TransitionResult, Action, Authorization)
    ├── memory.py                               (AuditMemory, AuditEntry)
    ├── kernel.py                               (WiseOrderKernel adapter)
    ├── proposer.py                             (Proposer protocol, StaticProposer, ManualProposer)
    ├── authorization.py                        (AuthorizationGate, AuthorizationDecision)
    ├── refusal.py                              (RefusalRecord)
    ├── runtime.py                              (RuntimeLoop, search())
    ├── cli.py                                  (intellagent CLI entry point)
    ├── canonical.py                            (canonical_json_bytes, sha256_hex, write_atomic)
    └── policies/                               (authorization-source policy registry)
        ├── README.md
        └── always_deny.json                    (sample policy)

# Runtime working directories, created by `intellagent init`:
intellagent_state/                              (gitignored)
intellagent_audit/                              (gitignored or committed, per use case)
intellagent_refusals/                           (gitignored or committed)
intellagent_objects/                            (content-addressed; gitignored)
```

The runtime adds **one new top-level package** (`intellagent_runtime/`) and **six new test files** under the existing `tests/`. It does not modify any existing file.

`pyproject.toml` is not added in v0.1; the runtime is invoked as `python3 -m intellagent_runtime.cli ...` or via a `Makefile` target. v0.2 may add proper packaging.

---

## 17. Test Plan

The runtime adds 6 test modules. Coverage requirement: every component module's public API, plus end-to-end integration through the CLI.

### 17.1 `test_intellagent_state.py`

- StateStore round-trip: write state, read back, `state_id` matches.
- Mutated on-disk state file is rejected on load (`STATE_TAMPERED`).
- Initial state is fully deterministic given a fixed `sealed_at` seed.
- Object content-addressing: same body → same `object_id`.

### 17.2 `test_intellagent_memory.py`

- Append N entries; chain verifies.
- Hand-edit one entry's body; chain verification fails (`CHAIN_CORRUPT`).
- Hand-edit one entry's `prev_entry_sha256`; chain verification fails.
- Empty memory returns `head_sha256() == null`.
- Concurrent append protection (file lock or write-temp-rename).

### 17.3 `test_intellagent_kernel.py`

- Class A: a fixture artifact passes; mutated artifact (digest mismatch) fails with `A1`/`CS2` failures.
- Class A: missing canonicalization fails with `A2`/`CS1`.
- Class A: non-JCS canonicalization fails (F-1 surface).
- Class B: contradictory observations preserved → `CONFLICTED` is admissible; suppression is rejected.
- Class C: unauthorized attester fails `C2`.
- Class D: empty alternatives fails `D2`; empty challenge_surface fails `D3`; broken commit chain fails `CC1`/`CC3`.
- Telemetry status (`CALIBRATION_*`) used as artifact status fails.

These mirror the existing 23 conformance vectors; the runtime's kernel adapter must reach the same verdicts.

### 17.4 `test_intellagent_authorization.py`

- Pure state transition: gate returns `authorized=True` with rationale `not-action-bearing`.
- Action-bearing transition with no `authorization`: rejected with `AG1` rationale.
- Action-bearing transition with `authorization` but unknown source: rejected with `AG2` rationale.
- Action-bearing transition with valid source allowlisting the action: authorized.
- Action-bearing transition with valid source disallowlisting the action: rejected.
- `always_deny` policy: every action denied with explicit rationale.

### 17.5 `test_intellagent_runtime.py`

- `search()` with a satisfiable query and a static proposer returning the satisfying transition: returns satisfied state and one audit entry.
- `search()` with an unsatisfiable query and a static proposer returning only kernel-rejected candidates: returns `RefusalRecord` with all rejections in challenge surface.
- `search()` with proposer returning empty list immediately: returns `RefusalRecord` with the explicit `proposer_returned_no_candidates` failure.
- `search()` with budget=0: returns `RefusalRecord` with `budget_exhausted`.
- Mixed: first proposed transition rejected by kernel; second accepted and committed; assertion that the rejection appears in *no* later refusal (rejections are per-search, not persisted).
- Action-bearing transition with allowlist policy that permits it: committed; audit entry has `action` populated.

### 17.6 `test_intellagent_cli.py`

End-to-end through subprocess invocations:

- `intellagent init` in tmp dir; verify three subdirs created and initial state file present.
- `intellagent propose --file <fixture>` → stdout shows `proposal_id`; queue file present.
- `intellagent transition <id>` (legitimate Class A): stdout shows `LEGITIMATE`; audit entry 0000 present; new state id reported.
- `intellagent transition <id>` (illegitimate Class D): stdout shows `REJECTED`; no new audit entry; rejection captured.
- `intellagent audit`: prints all sealed entries.
- `intellagent refuse --query <text>`: prints `refusal_id`; refusal file sealed.

### 17.7 Determinism gate

A meta-test that runs `init → propose → transition → audit` twice from a fixed seed and asserts byte-identical outputs from both runs. The runtime's claim of determinism is testable.

---

## 18. First Demo Flow

The minimum sequence that exercises every component end-to-end. Designed to run in under 10 seconds on a laptop.

### 18.1 Setup

```
$ cd /tmp/intellagent-demo
$ intellagent init
Initialized:
  intellagent_state/
  intellagent_audit/
  intellagent_refusals/
  intellagent_objects/
State id: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

### 18.2 Propose a Class A transition

```
$ cat > /tmp/winstack-class-a.transition.json <<'EOF'
{
  "transition_id":   "prop-demo-001",
  "from_state":      "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "regime":          "A",
  "object_added": {
    "class":            "A",
    "regime":           "deterministic_verification",
    "claim":            "demo Class A artifact aligned with class-a-valid-wiseproof",
    "canonicalization": "RFC8785-JCS",
    "algorithm":        "SHA-256",
    "expected_digest":  "sha256:1111111111111111111111111111111111111111111111111111111111111111",
    "observed_digest":  "sha256:1111111111111111111111111111111111111111111111111111111111111111",
    "status":           "VERIFIED",
    "provenance":       { "witness": "demo", "at": "2026-05-06T12:00:00Z" },
    "lineage":          []
  },
  "objects_removed": [],
  "action":          null,
  "authorization":   null,
  "proposer":        "manual",
  "proposed_at":     "2026-05-06T12:00:00Z"
}
EOF

$ intellagent propose --file /tmp/winstack-class-a.transition.json
proposal_id: prop-demo-001
regime:      A
status:      QUEUED
```

### 18.3 Run the verifier; commit on legitimacy

```
$ intellagent transition prop-demo-001
verifying:      prop-demo-001
regime:         A
kernel:         PASSED (A1, A2, A3, CS1, CS2, CS3)
authorization:  NOT_APPLICABLE (transition is not action-bearing)
result:         LEGITIMATE
committed:      audit entry 0000
new state id:   sha256:7a9d2f<...>
```

### 18.4 Inspect audit memory

```
$ intellagent audit --range 0:1
[
  {
    "index": 0,
    "regime": "A",
    "prior_state_id":     "sha256:e3b0c44298fc...",
    "resulting_state_id": "sha256:7a9d2f...",
    "prev_entry_sha256":  null,
    "this_entry_sha256":  "sha256:c6e9b1...",
    "sealed_at":          "2026-05-06T12:00:00Z",
    "transition": { "transition_id": "prop-demo-001", "regime": "A", ... }
  }
]
```

### 18.5 Try an illegitimate Class D transition; observe refusal

```
$ cat > /tmp/bad-class-d.transition.json <<'EOF'
{
  "transition_id":   "prop-demo-002",
  "from_state":      "<the new state id>",
  "regime":          "D",
  "object_added": {
    "class":              "D",
    "regime":             "interpretive_governance",
    "claim":              "deliberately malformed conduct artifact for demo",
    "values_frame":       { "optimizing_for": ["demo"], "not_optimizing_for": ["correctness"] },
    "alternatives":       [],
    "challenge_surface":  [],
    "status":             "CONDUCT_VALID"
  },
  "objects_removed": [],
  "action":          null,
  "authorization":   null,
  "proposer":        "manual",
  "proposed_at":     "2026-05-06T12:01:00Z"
}
EOF

$ intellagent propose --file /tmp/bad-class-d.transition.json
proposal_id: prop-demo-002

$ intellagent transition prop-demo-002
verifying:  prop-demo-002
regime:     D
kernel:     FAILED
  ↳ D2: alternatives must be non-empty
  ↳ D3: challenge_surface must be non-empty
result:     REJECTED (added to next refusal's challenge surface)
```

### 18.6 Seal the refusal

```
$ intellagent refuse --query "demo: produce a Class D conduct artifact"
refusal_id:                 refusal-demo-1
candidates_rejected:        1
challenge_surface_sha256:   sha256:b81f0c...
refused_at:                 2026-05-06T12:01:30Z
sealed_to:                  intellagent_refusals/refusal-demo-1.json
```

### 18.7 What this demo proves

1. **The kernel verified an arbitrary, hand-authored Class A transition** using the same invariants as the existing conformance vectors.
2. **The audit memory committed it** under a content-addressed commit chain, with `prev_entry_sha256` = null (genesis) and `this_entry_sha256` computed deterministically.
3. **A malformed Class D transition was refused before commit**, with explicit citation of `D2` and `D3` failures.
4. **The refusal is itself a sealed artifact** with a stable `refusal_id` and a `challenge_surface_sha256` that can be referenced from later audits.
5. **No AI model was involved.** The proposer was a JSON file. The architecture's claims hold without any learned component.

When a transformer is plugged in as proposer in v0.2, **none of the above changes**. The kernel still verifies. The audit memory still seals. The authorization gate still gates. That invariance is the architectural property the v0.1 demo exists to demonstrate.

---

## 19. Open Questions

1. **What canonical form does an `EpistemicObject` take?** v0.1 freezes a minimal shape (class, regime, claim, evidence, provenance, lineage, status). The right structure for production cognition will likely require richer typing (per-class object schemas?). Out of scope for v0.1.
2. **How are queries represented?** v0.1 treats `Query` as opaque text. A real query language — predicates over states — is needed before the runtime can decide *automatically* whether a state satisfies a query. v0.1 sidesteps this by making the operator decide.
3. **Does the proposer see the audit memory?** v0.1 says no — proposers see only the current state and the rejected candidates from the current search. v0.2 may grant audit-memory read access to learning proposers, raising privacy and amplification questions.
4. **What are the policy semantics of authorization sources?** v0.1 supports `always_deny` and `allowlist`. Real systems will need richer policies (rate limits, conditional approvals, expirations). Adding these without re-introducing implicit trust is non-trivial.
5. **How does the runtime handle recovery from `CHAIN_CORRUPT`?** v0.1 fails closed. A real system needs a documented recovery procedure that does not silently rewrite history.
6. **Is the search loop amenable to speculative execution?** v0.1 is strictly serial: propose → verify → commit. A speculative variant — propose many, verify in parallel, commit the first legitimate one — would help latency at the cost of wasted verification. Open empirical question.
7. **What is the cost of a kernel verify per transition?** v0.1 does not benchmark. Production deployment requires measurements; if Class D commit-chain verification proves dominant, caching or incremental verification becomes necessary.
8. **How do `EpistemicObject` lineages compose across transitions?** v0.1 records lineage as a list of prior `object_id`s. The semantics of "object X derives from object Y" under different class boundaries (Class A integrity proofs anchoring Class B observations, etc.) need formalization.
9. **What happens when two action-bearing transitions race?** v0.1 is single-host single-process; concurrency is not a concern. v0.2's distributed audit memory will need to address this directly.
10. **How is the runtime's own correctness audited?** v0.1 has pytest. Production deployment may want each runtime release to publish its own conformance report, signed by a trusted witness, so downstream audits can pin which runtime version produced which audit entries.

These are open questions, not blockers. v0.1 ships without resolving them; the architecture's claims are valid in v0.1's restricted scope, and v0.2+ work tightens the scope incrementally.

---

*Runtime specification, draft. WiseOrder Protocol v0.1.0 governs the kernel. INTELLAGENT.md proposes the architecture. INTELLAGENT-RUNTIME.md specifies the first buildable prototype. The implementation begins where this document ends.*
