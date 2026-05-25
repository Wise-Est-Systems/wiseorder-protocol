"""RuntimeLoop and the legitimate transition search.

This module wires the components together. ``search()`` is the v0.1 inference
primitive: propose → kernel-verify → (if action-bearing) authorization-gate →
commit-or-record-rejection → repeat until satisfied or refused.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from intellagent_runtime.authorization import AuthorizationGate, AuthorizationDecision
from intellagent_runtime.canonical import utcnow_iso8601
from intellagent_runtime.kernel import KernelVerdict, WiseOrderKernel
from intellagent_runtime.memory import AuditEntry, AuditMemory
from intellagent_runtime.refusal import RefusalRecord, RefusalStore
from intellagent_runtime.state import (
    EpistemicState,
    StateStore,
    compute_state_id,
)
from intellagent_runtime.transitions import EpistemicTransition


# ---------------------------------------------------------------------------
# Query (v0.1: opaque text + a Python predicate)
# ---------------------------------------------------------------------------


@dataclass
class Query:
    text: str
    predicate: Callable[[EpistemicState], bool]

    def satisfied_by(self, state: EpistemicState) -> bool:
        return self.predicate(state)

    def serialize(self) -> str:
        return self.text


# ---------------------------------------------------------------------------
# SearchResult
# ---------------------------------------------------------------------------


@dataclass
class SearchResult:
    satisfied: bool
    final_state: EpistemicState
    audit_head: str | None
    refusal: RefusalRecord | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "satisfied":   self.satisfied,
            "final_state": self.final_state.to_dict(),
            "audit_head":  self.audit_head,
            "refusal":     self.refusal.to_dict() if self.refusal else None,
        }


# ---------------------------------------------------------------------------
# Apply transition (pure: produces new state; writes object to store)
# ---------------------------------------------------------------------------


def apply_transition(
    transition: EpistemicTransition,
    prior_state: EpistemicState,
    store: StateStore,
    audit: AuditMemory,
) -> tuple[EpistemicState, AuditEntry]:
    """Apply a (kernel-passed, gate-passed) transition and seal the audit entry.

    Crash-safe commit order (WO-RES-2026-05-24):
      1. stage audit entry to ``<idx>.entry.json.staging``
      2. atomically save new state (which references staged entry's hash)
      3. rename staging file to final ``<idx>.entry.json``

    A crash between (1) and (2) leaves an orphan staging file with no state
    reference; ``audit.reconcile_pending(state.audit_head_sha256)`` discards
    it at next startup. A crash between (2) and (3) leaves state pointing at
    the staged hash; reconciliation finalizes the rename. See memory.py.

    Returns the new state and the audit entry that was just sealed.
    """
    new_object_id: str | None = None
    if transition.object_added is not None:
        new_object_id = store.objects.put(transition.object_added)

    new_objects = [oid for oid in prior_state.objects if oid not in transition.objects_removed]
    if new_object_id is not None and new_object_id not in new_objects:
        new_objects.append(new_object_id)
    new_objects = sorted(new_objects)

    resulting_state_id = compute_state_id(new_objects)

    # (1) stage audit entry (write to .staging path)
    entry = audit.stage_entry(
        transition=transition,
        prior_state_id=prior_state.state_id,
        resulting_state_id=resulting_state_id,
    )

    # (2) commit state — atomically via write_atomic — with audit_head pointing
    # at the staged entry. After this line returns, state.json on disk
    # references the staged hash; the staging file is the only thing whose
    # presence at the wrong filename distinguishes "crashed mid-commit" from
    # "fully committed."
    new_state = EpistemicState(
        state_id=resulting_state_id,
        objects=new_objects,
        audit_head_sha256=entry.this_entry_sha256,
        sealed_at=utcnow_iso8601(),
    )
    store.save(new_state)

    # (3) finalize: rename .staging -> final. Idempotent.
    audit.finalize_staged(entry)
    return new_state, entry


# ---------------------------------------------------------------------------
# Validate (kernel + AG1)
# ---------------------------------------------------------------------------


def validate_transition(
    transition: EpistemicTransition,
    prior_state: EpistemicState,
    kernel: WiseOrderKernel,
) -> KernelVerdict:
    """Thin wrapper around the kernel for symmetry with the runtime loop."""
    return kernel.verify(transition, prior_state)


# ---------------------------------------------------------------------------
# RuntimeLoop
# ---------------------------------------------------------------------------


class RuntimeLoop:
    def __init__(
        self,
        base_dir: Path,
        kernel: WiseOrderKernel,
        gate: AuthorizationGate,
    ):
        self.base = Path(base_dir)
        self.store = StateStore(self.base)
        self.audit = AuditMemory(self.base / "intellagent_audit")
        self.refusals = RefusalStore(self.base / "intellagent_refusals")
        self.kernel = kernel
        self.gate = gate

    def search(
        self,
        query: Query,
        proposer,                 # Proposer
        max_iters: int = 64,
    ) -> SearchResult:
        # Always re-verify the chain on entry; fail closed if corrupt.
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
                    rejected=rejected,  # may be empty → seal() will fill in marker
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
