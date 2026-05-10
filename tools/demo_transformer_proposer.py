#!/usr/bin/env python3
"""End-to-end demo: TransformerProposer + RuntimeLoop, no real model.

Runs two searches in a fresh temporary runtime:

  1. The mock provider returns a structurally-valid Class A transition.
     The kernel verifies it; the runtime commits an audit entry; the
     query is satisfied.

  2. The mock provider returns a structurally-malformed Class D conduct
     artifact (empty alternatives, empty challenge_surface, empty
     commit_chain). The kernel rejects it on D2/D3/CC3 invariants. The
     runtime emits a sealed RefusalRecord. No audit entry is written.

After both searches, the audit chain integrity is verified.

Run from the repository root:

    python3 tools/demo_transformer_proposer.py
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from intellagent_runtime.authorization import AuthorizationGate
from intellagent_runtime.kernel import WiseOrderKernel
from intellagent_runtime.proposer_transformer import (
    DeterministicMockProvider,
    GenerationParams,
    TransformerProposer,
    measured_search,
)
from intellagent_runtime.runtime import Query, RuntimeLoop
from intellagent_runtime.state import StateStore


HEX64_A = "a" * 64


def _good_class_a_body(state_id: str) -> dict:
    return {
        "transition_id": "prop-demo-a-001",
        "from_state": state_id,
        "regime": "A",
        "object_added": {
            "class": "A",
            "regime": "deterministic_verification",
            "claim": "demo Class A artifact aligned with class-a-valid-wiseproof",
            "canonicalization": "RFC8785-JCS",
            "algorithm": "SHA-256",
            "expected_digest": f"sha256:{HEX64_A}",
            "observed_digest": f"sha256:{HEX64_A}",
            "status": "VERIFIED",
            "provenance": {"witness": "demo", "at": "2026-05-06T12:00:00Z"},
        },
        "objects_removed": [],
        "action": None,
        "authorization": None,
        "proposer": "transformer-mock",
        "proposed_at": "2026-05-06T12:00:00Z",
    }


def _bad_class_d_body(state_id: str) -> dict:
    return {
        "transition_id": "prop-demo-d-001",
        "from_state": state_id,
        "regime": "D",
        "object_added": {
            "class": "D",
            "regime": "interpretive_governance",
            "claim": "deliberately malformed Class D conduct artifact for demo",
            "values_frame": {
                "optimizing_for": ["x"],
                "not_optimizing_for": ["y"],
            },
            "alternatives": [],          # D2 violation
            "challenge_surface": [],     # D3 violation
            "commit_chain": [],          # CC3 violation
            "status": "CONDUCT_VALID",
        },
        "objects_removed": [],
        "action": None,
        "authorization": None,
        "proposer": "transformer-mock",
        "proposed_at": "2026-05-06T12:01:00Z",
    }


def _heading(text: str) -> None:
    bar = "=" * 60
    print(f"\n{bar}\n{text}\n{bar}")


def main() -> int:
    work = Path(tempfile.mkdtemp(prefix="intellagent-demo-"))
    try:
        # ---- Setup runtime --------------------------------------------
        _heading("1. Runtime setup")
        store = StateStore(work)
        store.init()
        (work / "policies").mkdir(exist_ok=True)
        runtime = RuntimeLoop(
            base_dir=work,
            kernel=WiseOrderKernel(),
            gate=AuthorizationGate(work / "policies"),
        )
        initial = runtime.store.load()
        print(f"runtime working directory: {work}")
        print(f"initial state_id:          {initial.state_id}")
        print(f"audit head (pre-run):      {runtime.audit.head_sha256()}")

        # ---- Search 1: legitimate Class A transition -------------------
        _heading("2. Search 1 — legitimate Class A transition (expected: COMMIT)")
        good_body = _good_class_a_body(initial.state_id)
        provider_a = DeterministicMockProvider(
            "demo-model-id",
            [json.dumps([good_body])],
        )
        proposer_a = TransformerProposer(
            name="transformer-mock",
            provider=provider_a,
            params=GenerationParams(temperature=0.0, seed=42),
            deterministic=True,
        )
        query_a = Query(
            "state has at least one object",
            lambda s: len(s.objects) > 0,
        )
        result_a, metrics_a = measured_search(runtime, query_a, proposer_a)

        print(f"satisfied:                 {result_a.satisfied}")
        print(f"refusal:                   {result_a.refusal}")
        print(f"audit head (post-search):  {runtime.audit.head_sha256()}")
        print(f"audit entries committed:   {len(runtime.audit.list_entries())}")

        if result_a.satisfied:
            entry = runtime.audit.list_entries()[0]
            print("\n# Accepted transition artifact (audit entry 0000):\n")
            print(json.dumps(entry.to_dict(), indent=2, sort_keys=True))

        # ---- Verify chain integrity after committed entry --------------
        try:
            runtime.audit.verify_chain()
            print("\nchain integrity: OK after legitimate transition")
        except Exception as exc:
            print(f"\nchain integrity: FAIL — {exc}")
            return 1

        # ---- Search 2: malformed Class D — expect refusal --------------
        _heading("3. Search 2 — malformed Class D conduct artifact (expected: REFUSE)")
        # Reload state — the runtime advanced after search 1.
        state2 = runtime.store.load()
        bad_body = _bad_class_d_body(state2.state_id)
        provider_d = DeterministicMockProvider(
            "demo-model-id",
            [json.dumps([bad_body])],
        )
        proposer_d = TransformerProposer(
            name="transformer-mock",
            provider=provider_d,
            params=GenerationParams(temperature=0.0, seed=43),
            deterministic=True,
        )
        query_d = Query("never satisfied (forces refusal)", lambda s: False)
        result_d, metrics_d = measured_search(runtime, query_d, proposer_d)

        print(f"satisfied:                 {result_d.satisfied}")
        print(f"refusal sealed:            {result_d.refusal is not None}")
        print(f"audit head (post-search):  {runtime.audit.head_sha256()}")
        print(f"audit entries committed:   {len(runtime.audit.list_entries())}")

        if result_d.refusal is not None:
            print("\n# Refusal artifact:\n")
            print(json.dumps(result_d.refusal.to_dict(), indent=2, sort_keys=True))

        # ---- Verify chain integrity after refusal ----------------------
        try:
            runtime.audit.verify_chain()
            print("\nchain integrity: OK after refusal")
        except Exception as exc:
            print(f"\nchain integrity: FAIL — {exc}")
            return 1

        # ---- Benchmark metrics -----------------------------------------
        _heading("4. Benchmark metrics (ProposerRunMetrics)")
        print("Search 1 (legitimate):")
        print(f"  proposals_emitted:  {metrics_a.proposals_emitted}")
        print(f"  parse_failures:     {metrics_a.parse_failures}")
        print(f"  kernel_passes:      {metrics_a.kernel_passes}")
        print(f"  kernel_rejections:  {metrics_a.kernel_rejections}")
        print(f"  auth_denials:       {metrics_a.auth_denials}")
        print(f"  committed:          {metrics_a.committed}")
        print(f"  refused:            {metrics_a.refused}")
        print(f"  total_tokens_in:    {metrics_a.total_tokens_in}")
        print(f"  total_tokens_out:   {metrics_a.total_tokens_out}")
        print(f"  total_elapsed_ms:   {metrics_a.total_elapsed_ms}")
        print()
        print("Search 2 (refusal):")
        print(f"  proposals_emitted:  {metrics_d.proposals_emitted}")
        print(f"  parse_failures:     {metrics_d.parse_failures}")
        print(f"  kernel_passes:      {metrics_d.kernel_passes}")
        print(f"  kernel_rejections:  {metrics_d.kernel_rejections}")
        print(f"  auth_denials:       {metrics_d.auth_denials}")
        print(f"  committed:          {metrics_d.committed}")
        print(f"  refused:            {metrics_d.refused}")
        print(f"  total_tokens_in:    {metrics_d.total_tokens_in}")
        print(f"  total_tokens_out:   {metrics_d.total_tokens_out}")
        print(f"  total_elapsed_ms:   {metrics_d.total_elapsed_ms}")

        # ---- Final pass/fail summary -----------------------------------
        _heading("5. Final pass/fail summary")
        ok_search1 = result_a.satisfied is True and result_a.refusal is None
        ok_search2 = result_d.satisfied is False and result_d.refusal is not None
        ok_chain = True
        try:
            runtime.audit.verify_chain()
        except Exception:
            ok_chain = False

        print(f"search 1 (legitimate accepted): {'PASS' if ok_search1 else 'FAIL'}")
        print(f"search 2 (illegitimate refused): {'PASS' if ok_search2 else 'FAIL'}")
        print(f"audit chain integrity:           {'PASS' if ok_chain else 'FAIL'}")
        all_ok = ok_search1 and ok_search2 and ok_chain
        print(f"overall:                         {'PASS' if all_ok else 'FAIL'}")
        return 0 if all_ok else 1
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
