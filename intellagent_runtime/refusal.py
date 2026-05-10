"""Refusal artifacts.

A `RefusalRecord` is sealed whenever legitimate transition search terminates
without satisfying the query. Refusal is a first-class output, not an error.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
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


@dataclass
class RefusalRecord:
    refusal_id: str
    query: str
    from_state: str
    candidates_rejected: list[dict[str, Any]]
    challenge_surface_sha256: str
    refused_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "refusal_id":               self.refusal_id,
            "query":                    self.query,
            "from_state":               self.from_state,
            "candidates_rejected":      list(self.candidates_rejected),
            "challenge_surface_sha256": self.challenge_surface_sha256,
            "refused_at":               self.refused_at,
        }


def _challenge_surface(rejected: list[tuple]) -> tuple[list[dict[str, Any]], str]:
    """Return (canonical entries, sha256) for the challenge surface.

    Each item in ``rejected`` is ``(EpistemicTransition | None, list[str])``.
    """
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
    def __init__(self, refusals_dir: Path):
        self.dir = Path(refusals_dir)

    def seal(
        self,
        query: str,
        from_state_id: str,
        rejected: list[tuple[EpistemicTransition | None, list[str]]],
    ) -> RefusalRecord:
        """Seal a refusal record. D3: an empty challenge surface is malformed,
        so an empty rejected list is replaced with an explicit no-candidates marker.
        """
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

    def list_refusals(self) -> list[RefusalRecord]:
        if not self.dir.is_dir():
            return []
        out: list[RefusalRecord] = []
        for p in sorted(self.dir.glob("refusal-*.json")):
            body = json.loads(p.read_text(encoding="utf-8"))
            out.append(RefusalRecord(**body))
        return out
