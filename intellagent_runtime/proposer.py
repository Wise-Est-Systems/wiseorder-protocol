"""Proposer interface and v0.1 implementations.

A proposer suggests candidate transitions given the current state and a query.
The runtime verifies each candidate against the kernel; rejected candidates
from prior iterations are passed back so a learning proposer can adapt.
v0.1 ships with two static implementations: file-based and stdin-based.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from intellagent_runtime.transitions import EpistemicTransition


@runtime_checkable
class Proposer(Protocol):
    """Anything that returns candidate transitions for a state+query.

    Attributes:
        name: identifying string included in audit / refusal records.
    """

    name: str

    def propose(
        self,
        state,                     # EpistemicState
        query,                     # Query
        rejected: list[tuple[EpistemicTransition, list[str]]],
    ) -> list[EpistemicTransition]:
        ...


# ---------------------------------------------------------------------------
# StaticProposer — reads a JSON array of transitions from a file (one-shot).
# ---------------------------------------------------------------------------


class StaticProposer:
    name: str

    def __init__(self, name: str, path: Path | str):
        self.name = name
        self._path = Path(path)
        self._consumed = False

    def _load(self) -> list[EpistemicTransition]:
        body = json.loads(self._path.read_text(encoding="utf-8"))
        if isinstance(body, dict):
            body = [body]
        if not isinstance(body, list):
            raise ValueError(
                f"{self._path}: StaticProposer expects a JSON object or list of objects"
            )
        return [EpistemicTransition.from_dict(b) for b in body]

    def propose(self, state, query, rejected) -> list[EpistemicTransition]:
        if self._consumed:
            return []
        self._consumed = True
        return self._load()


# ---------------------------------------------------------------------------
# ManualProposer — reads a single JSON transition from stdin per call.
# ---------------------------------------------------------------------------


class ManualProposer:
    name: str

    def __init__(self, name: str = "manual", stream=None):
        self.name = name
        self._stream = stream if stream is not None else sys.stdin
        self._exhausted = False

    def propose(self, state, query, rejected) -> list[EpistemicTransition]:
        if self._exhausted:
            return []
        text = self._stream.read()
        if not text or not text.strip():
            self._exhausted = True
            return []
        body = json.loads(text)
        if isinstance(body, list):
            return [EpistemicTransition.from_dict(b) for b in body]
        return [EpistemicTransition.from_dict(body)]


# ---------------------------------------------------------------------------
# InMemoryProposer — tests use this; takes a list directly.
# ---------------------------------------------------------------------------


class InMemoryProposer:
    name: str

    def __init__(self, name: str, transitions: list[EpistemicTransition]):
        self.name = name
        self._transitions = list(transitions)
        self._consumed = False

    def propose(self, state, query, rejected) -> list[EpistemicTransition]:
        if self._consumed:
            return []
        self._consumed = True
        return list(self._transitions)
