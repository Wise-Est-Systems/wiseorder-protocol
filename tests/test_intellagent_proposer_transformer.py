"""Tests for intellagent_runtime.proposer_transformer."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from intellagent_runtime.authorization import AuthorizationGate
from intellagent_runtime.kernel import WiseOrderKernel
from intellagent_runtime.memory import AuditMemory
from intellagent_runtime.proposer_transformer import (
    CompletionResult,
    DeterministicMockProvider,
    GenerationParams,
    ProposalCandidate,
    Provider,
    TransformerProposer,
    measured_search,
)
from intellagent_runtime.runtime import Query, RuntimeLoop
from intellagent_runtime.state import StateStore, compute_state_id


HEX64_A = "a" * 64


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _good_class_a_body(state_id: str, *, claim: str = "test") -> dict:
    return {
        "transition_id": "prop-test-001",
        "from_state": state_id,
        "regime": "A",
        "object_added": {
            "class": "A",
            "regime": "deterministic_verification",
            "claim": claim,
            "canonicalization": "RFC8785-JCS",
            "algorithm": "SHA-256",
            "expected_digest": f"sha256:{HEX64_A}",
            "observed_digest": f"sha256:{HEX64_A}",
            "status": "VERIFIED",
        },
        "objects_removed": [],
        "action": None,
        "authorization": None,
        "proposer": "test",
        "proposed_at": "2026-05-06T12:00:00Z",
    }


def _bad_class_d_body(state_id: str) -> dict:
    return {
        "transition_id": "prop-test-bad-d",
        "from_state": state_id,
        "regime": "D",
        "object_added": {
            "class": "D",
            "regime": "interpretive_governance",
            "claim": "deliberately malformed",
            "values_frame": {"optimizing_for": ["x"], "not_optimizing_for": ["y"]},
            "alternatives": [],          # D2 violation
            "challenge_surface": [],     # D3 violation
            "commit_chain": [],          # CC3 violation
            "status": "CONDUCT_VALID",
        },
        "objects_removed": [],
        "action": None,
        "authorization": None,
        "proposer": "test",
        "proposed_at": "2026-05-06T12:00:00Z",
    }


def _make_runtime(tmp_path: Path) -> RuntimeLoop:
    store = StateStore(tmp_path)
    store.init()
    pol = tmp_path / "policies"
    pol.mkdir()
    return RuntimeLoop(
        base_dir=tmp_path,
        kernel=WiseOrderKernel(),
        gate=AuthorizationGate(pol),
    )


# ---------------------------------------------------------------------------
# Provider protocol conformance
# ---------------------------------------------------------------------------


def test_deterministic_mock_provider_basic_completion() -> None:
    provider = DeterministicMockProvider("mock-id", ["[]"])
    completion = provider.generate("test prompt", GenerationParams())
    assert completion.text == "[]"
    assert completion.provider == "mock"
    assert completion.model_id == "mock-id"
    assert completion.finish_reason == "stop"
    assert completion.input_tokens > 0


def test_deterministic_mock_provider_exhausts_completions() -> None:
    provider = DeterministicMockProvider("mock-id", ["[]"])
    provider.generate("p", GenerationParams())
    second = provider.generate("p", GenerationParams())
    assert second.text == ""
    assert second.output_tokens == 0


def test_provider_protocol_satisfied_by_mock() -> None:
    provider = DeterministicMockProvider("mock", [])
    assert isinstance(provider, Provider)
    assert provider.supports_structured_output() is True
    assert provider.supports_seeded_sampling() is True


# ---------------------------------------------------------------------------
# Construction / determinism gating
# ---------------------------------------------------------------------------


def test_basic_construction() -> None:
    provider = DeterministicMockProvider("m", [])
    proposer = TransformerProposer(name="test", provider=provider)
    assert proposer.name == "test"
    assert proposer.last_candidates == []


def test_deterministic_requires_seed() -> None:
    provider = DeterministicMockProvider("m", [])
    with pytest.raises(ValueError, match="seed"):
        TransformerProposer(
            name="test",
            provider=provider,
            params=GenerationParams(temperature=0.0),
            deterministic=True,
        )


def test_deterministic_requires_zero_temperature() -> None:
    provider = DeterministicMockProvider("m", [])
    with pytest.raises(ValueError, match="temperature"):
        TransformerProposer(
            name="test",
            provider=provider,
            params=GenerationParams(temperature=0.5, seed=1),
            deterministic=True,
        )


class _ProviderWithoutSeed:
    name = "no-seed"
    model_id = "x"

    def generate(self, prompt: str, params: GenerationParams) -> CompletionResult:
        return CompletionResult("", 0, 0, 0, "stop", self.model_id, self.name)

    def supports_structured_output(self) -> bool:
        return True

    def supports_seeded_sampling(self) -> bool:
        return False


def test_deterministic_requires_seeded_provider() -> None:
    with pytest.raises(ValueError, match="seeded sampling"):
        TransformerProposer(
            name="test",
            provider=_ProviderWithoutSeed(),
            params=GenerationParams(temperature=0.0, seed=1),
            deterministic=True,
        )


# ---------------------------------------------------------------------------
# Parsing pipeline
# ---------------------------------------------------------------------------


def test_parse_native_json(tmp_path: Path) -> None:
    state_id = compute_state_id([])
    body = _good_class_a_body(state_id)
    provider = DeterministicMockProvider("m", [json.dumps([body])])
    proposer = TransformerProposer(name="t", provider=provider)
    completion = provider.generate("p", GenerationParams())
    state = StateStore(tmp_path)._fake_state_for_parse_test = None  # noqa
    # Fabricate a minimal state object with state_id attribute.
    class _S:
        def __init__(self, sid: str) -> None:
            self.state_id = sid
    transitions, parse_path = proposer.parse_candidates(completion, _S(state_id))
    assert parse_path == "native"
    assert len(transitions) == 1
    assert transitions[0].regime == "A"


def test_parse_fence_stripped(tmp_path: Path) -> None:
    state_id = compute_state_id([])
    body = _good_class_a_body(state_id)
    fenced = "```json\n" + json.dumps([body]) + "\n```"
    provider = DeterministicMockProvider("m", [fenced])
    proposer = TransformerProposer(name="t", provider=provider)
    completion = provider.generate("p", GenerationParams())
    class _S:
        def __init__(self, sid: str) -> None:
            self.state_id = sid
    transitions, parse_path = proposer.parse_candidates(completion, _S(state_id))
    assert parse_path == "fence_stripped"
    assert len(transitions) == 1


def test_parse_failed_returns_empty(tmp_path: Path) -> None:
    state_id = compute_state_id([])
    provider = DeterministicMockProvider("m", ["I cannot help with that."])
    proposer = TransformerProposer(name="t", provider=provider)
    completion = provider.generate("p", GenerationParams())
    class _S:
        def __init__(self, sid: str) -> None:
            self.state_id = sid
    transitions, parse_path = proposer.parse_candidates(completion, _S(state_id))
    assert parse_path == "failed"
    assert transitions == []


def test_parse_object_normalized_to_array(tmp_path: Path) -> None:
    state_id = compute_state_id([])
    body = _good_class_a_body(state_id)
    provider = DeterministicMockProvider("m", [json.dumps(body)])
    proposer = TransformerProposer(name="t", provider=provider)
    completion = provider.generate("p", GenerationParams())
    class _S:
        def __init__(self, sid: str) -> None:
            self.state_id = sid
    transitions, _ = proposer.parse_candidates(completion, _S(state_id))
    assert len(transitions) == 1


def test_parse_wrapped_transitions_key(tmp_path: Path) -> None:
    state_id = compute_state_id([])
    body = _good_class_a_body(state_id)
    wrapped = {"transitions": [body]}
    provider = DeterministicMockProvider("m", [json.dumps(wrapped)])
    proposer = TransformerProposer(name="t", provider=provider)
    completion = provider.generate("p", GenerationParams())
    class _S:
        def __init__(self, sid: str) -> None:
            self.state_id = sid
    transitions, _ = proposer.parse_candidates(completion, _S(state_id))
    assert len(transitions) == 1


def test_parse_drops_invalid_keeps_valid(tmp_path: Path) -> None:
    state_id = compute_state_id([])
    body = _good_class_a_body(state_id)
    invalid = {"junk": True}  # missing required transition fields
    provider = DeterministicMockProvider("m", [json.dumps([invalid, body])])
    proposer = TransformerProposer(name="t", provider=provider)
    completion = provider.generate("p", GenerationParams())
    class _S:
        def __init__(self, sid: str) -> None:
            self.state_id = sid
    transitions, _ = proposer.parse_candidates(completion, _S(state_id))
    assert len(transitions) == 1
    assert transitions[0].regime == "A"


# ---------------------------------------------------------------------------
# End-to-end via RuntimeLoop
# ---------------------------------------------------------------------------


def test_runtime_loop_legitimate_transition_committed(tmp_path: Path) -> None:
    runtime = _make_runtime(tmp_path)
    state_id = runtime.store.load().state_id
    body = _good_class_a_body(state_id)
    provider = DeterministicMockProvider("m", [json.dumps([body])])
    proposer = TransformerProposer(name="demo", provider=provider)
    query = Query("state has at least one object", lambda s: len(s.objects) > 0)

    result = runtime.search(query, proposer)
    assert result.satisfied is True
    assert result.refusal is None
    assert len(runtime.audit.list_entries()) == 1
    runtime.audit.verify_chain()  # raises ChainCorrupt on failure


def test_runtime_loop_illegitimate_transition_refused(tmp_path: Path) -> None:
    runtime = _make_runtime(tmp_path)
    state_id = runtime.store.load().state_id
    body = _bad_class_d_body(state_id)
    provider = DeterministicMockProvider("m", [json.dumps([body])])
    proposer = TransformerProposer(name="demo", provider=provider)
    query = Query("never satisfied", lambda s: False)

    result = runtime.search(query, proposer)
    assert result.satisfied is False
    assert result.refusal is not None
    failures = [
        f
        for entry in result.refusal.candidates_rejected
        for f in entry["legitimacy_failures"]
    ]
    assert any("D2" in f for f in failures)
    assert any("D3" in f for f in failures)
    runtime.audit.verify_chain()  # untouched chain still verifies
    assert len(runtime.audit.list_entries()) == 0


def test_runtime_loop_parse_failure_yields_refusal(tmp_path: Path) -> None:
    runtime = _make_runtime(tmp_path)
    provider = DeterministicMockProvider("m", ["I refuse to help."])
    proposer = TransformerProposer(name="demo", provider=provider)
    query = Query("never satisfied", lambda s: False)
    result = runtime.search(query, proposer)
    assert result.satisfied is False
    assert result.refusal is not None


def test_two_proposes_with_same_input_byte_identical(tmp_path: Path) -> None:
    state_id = compute_state_id([])
    body = _good_class_a_body(state_id)
    completion_text = json.dumps([body])

    class _S:
        def __init__(self, sid: str) -> None:
            self.state_id = sid

    state = _S(state_id)

    p1 = DeterministicMockProvider("m", [completion_text])
    proposer1 = TransformerProposer(name="t", provider=p1)
    out1 = proposer1.parse_candidates(p1.generate("p", GenerationParams()), state)[0]

    p2 = DeterministicMockProvider("m", [completion_text])
    proposer2 = TransformerProposer(name="t", provider=p2)
    out2 = proposer2.parse_candidates(p2.generate("p", GenerationParams()), state)[0]

    assert out1[0].to_dict() == out2[0].to_dict()


# ---------------------------------------------------------------------------
# Proposer Run Metrics (benchmark hook)
# ---------------------------------------------------------------------------


def test_measured_search_records_metrics_on_committed(tmp_path: Path) -> None:
    runtime = _make_runtime(tmp_path)
    state_id = runtime.store.load().state_id
    body = _good_class_a_body(state_id)
    provider = DeterministicMockProvider("m", [json.dumps([body])])
    proposer = TransformerProposer(name="demo", provider=provider)
    query = Query("state has at least one object", lambda s: len(s.objects) > 0)

    result, metrics = measured_search(runtime, query, proposer)
    assert result.satisfied is True
    assert metrics.committed == 1
    assert metrics.refused is False
    assert metrics.proposals_emitted >= 1
    assert metrics.total_tokens_out >= 0


def test_measured_search_records_refusal(tmp_path: Path) -> None:
    runtime = _make_runtime(tmp_path)
    state_id = runtime.store.load().state_id
    body = _bad_class_d_body(state_id)
    provider = DeterministicMockProvider("m", [json.dumps([body])])
    proposer = TransformerProposer(name="demo", provider=provider)
    query = Query("never sat", lambda s: False)
    result, metrics = measured_search(runtime, query, proposer)
    assert result.satisfied is False
    assert metrics.refused is True
    assert metrics.kernel_rejections >= 1


# ---------------------------------------------------------------------------
# Determinism replay capture
# ---------------------------------------------------------------------------


def test_replay_capture_contains_all_required_fields(tmp_path: Path) -> None:
    provider = DeterministicMockProvider("m", ["[]"])
    proposer = TransformerProposer(
        name="d",
        provider=provider,
        params=GenerationParams(temperature=0.0, seed=42),
        deterministic=True,
    )
    completion = provider.generate("test prompt", proposer.params)
    capture = proposer.deterministic_replay_capture(completion, "test prompt")
    for key in (
        "provider",
        "model_id",
        "deterministic",
        "seed",
        "temperature",
        "top_p",
        "max_tokens",
        "response_format",
        "prompt_sha256",
        "completion_sha256",
        "input_tokens",
        "output_tokens",
        "elapsed_ms",
        "finish_reason",
    ):
        assert key in capture
    assert capture["seed"] == 42
    assert capture["temperature"] == 0.0
    assert capture["deterministic"] is True


# ---------------------------------------------------------------------------
# Cost metadata population
# ---------------------------------------------------------------------------


def test_last_candidates_carry_cost_metadata(tmp_path: Path) -> None:
    runtime = _make_runtime(tmp_path)
    state_id = runtime.store.load().state_id
    body = _good_class_a_body(state_id)
    provider = DeterministicMockProvider("model-x", [json.dumps([body])])
    proposer = TransformerProposer(name="demo", provider=provider)
    query = Query("state has at least one object", lambda s: len(s.objects) > 0)
    runtime.search(query, proposer)
    cands = proposer.last_candidates
    assert len(cands) == 1
    cost = cands[0].proposal_cost
    assert cost["provider"] == "mock"
    assert cost["model_id"] == "model-x"
    assert "tokens_in" in cost
    assert "tokens_out" in cost
    assert "prompt_sha256" in cost
    assert cands[0].parse_path == "native"
