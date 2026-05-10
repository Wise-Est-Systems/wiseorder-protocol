#!/usr/bin/env python3
"""TransformerProposer v0.1 — structured heuristic proposal generation.

Implements the existing intellagent_runtime.proposer.Proposer protocol so a
TransformerProposer drops into RuntimeLoop alongside StaticProposer and
ManualProposer with no runtime change.

Provider abstraction: any class conforming to the Provider Protocol works
(OpenAICompatibleProvider, AnthropicProvider, LocalOpenAICompatibleProvider,
DeterministicMockProvider). The proposer never trusts provider output;
every candidate flows through the kernel before it can affect anything.

Spec: TRANSFORMER-PROPOSER-v0.1.md.
"""

from __future__ import annotations

import dataclasses
import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from intellagent_runtime.canonical import (
    canonical_json_bytes,
    sha256_hex,
    utcnow_iso8601,
)
from intellagent_runtime.transitions import EpistemicTransition


# ---------------------------------------------------------------------------
# Provider abstraction
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GenerationParams:
    """Sampling configuration passed to a Provider on every call."""
    temperature:     float = 0.0
    top_p:           float = 1.0
    max_tokens:      int = 2048
    seed:            int | None = None
    response_format: dict[str, Any] | None = None


@dataclass(frozen=True)
class CompletionResult:
    """Provider-agnostic completion record. The text is what the proposer parses."""
    text:           str
    input_tokens:   int
    output_tokens:  int
    elapsed_ms:     int
    finish_reason:  str
    model_id:       str
    provider:       str


@runtime_checkable
class Provider(Protocol):
    """The single interface every model backend must satisfy."""
    name:     str
    model_id: str

    def generate(self, prompt: str, params: GenerationParams) -> CompletionResult:
        ...

    def supports_structured_output(self) -> bool:
        ...

    def supports_seeded_sampling(self) -> bool:
        ...


# ---------------------------------------------------------------------------
# ProposalCandidate — internal richer record; runtime sees only .transition
# ---------------------------------------------------------------------------


@dataclass
class ProposalCandidate:
    proposer_id:         str
    proposal_id:         str
    transition:          EpistemicTransition
    confidence:          float
    retrieval_refs:      list[str]
    heuristic_reasoning: str
    estimated_regime:    str
    proposal_cost:       dict[str, Any]
    proposal_time_ms:    int
    parse_path:          str  # native | fence_stripped | regex_fallback_arr | regex_fallback_obj | failed


# ---------------------------------------------------------------------------
# Prompt fragment loading
# ---------------------------------------------------------------------------


_PROMPT_DIR_DEFAULT = Path(__file__).resolve().parent / "prompts"


def _load_prompt_fragments(prompt_dir: Path) -> dict[str, str]:
    fragments: dict[str, str] = {}
    for name in (
        "system_preamble",
        "class_a_fragment",
        "class_b_fragment",
        "class_c_fragment",
        "class_d_fragment",
    ):
        fragments[name] = (prompt_dir / f"{name}.md").read_text(encoding="utf-8")
    return fragments


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------


_CODE_FENCE_RE = re.compile(
    r"^```(?:json)?\s*\n?(?P<body>.*?)\s*```\s*$",
    re.DOTALL | re.IGNORECASE,
)
_JSON_ARRAY_RE = re.compile(r"\[\s*[\{\[].*[\}\]]\s*\]", re.DOTALL)
_JSON_OBJECT_RE = re.compile(r"\{.*\}", re.DOTALL)


# ---------------------------------------------------------------------------
# TransformerProposer
# ---------------------------------------------------------------------------


class TransformerProposer:
    """Proposer that wraps any Provider conforming to the Provider Protocol.

    Implements the intellagent_runtime.proposer.Proposer contract (returns
    list[EpistemicTransition]). Internally tracks ProposalCandidate records
    with cost and parse-path metadata; the most recent batch is available
    via the `last_candidates` property for benchmark hooks.
    """

    name: str

    def __init__(
        self,
        name: str,
        provider: Provider,
        params: GenerationParams = GenerationParams(),
        *,
        max_internal_retries: int = 1,
        max_rejected_in_prompt: int = 4,
        max_state_objects_in_prompt: int = 32,
        deterministic: bool = False,
        prompt_dir: Path | None = None,
    ) -> None:
        if deterministic:
            if params.temperature != 0.0:
                raise ValueError(
                    "deterministic=True requires GenerationParams.temperature == 0.0"
                )
            if not provider.supports_seeded_sampling():
                raise ValueError(
                    f"deterministic=True but provider {provider.name!r} does "
                    "not support seeded sampling"
                )
            if params.seed is None:
                raise ValueError(
                    "deterministic=True requires GenerationParams.seed to be set"
                )

        # Default to JSON-mode response_format if the provider supports it.
        if provider.supports_structured_output() and params.response_format is None:
            params = dataclasses.replace(params, response_format={"type": "json_object"})

        self.name = name
        self.provider = provider
        self.params = params
        self.max_internal_retries = max_internal_retries
        self.max_rejected_in_prompt = max_rejected_in_prompt
        self.max_state_objects_in_prompt = max_state_objects_in_prompt
        self.deterministic = deterministic
        self._prompt_dir = prompt_dir or _PROMPT_DIR_DEFAULT
        self._fragments = _load_prompt_fragments(self._prompt_dir)
        self._last_candidates: list[ProposalCandidate] = []

    # ---- Proposer protocol ---------------------------------------------

    def propose(
        self,
        state,
        query,
        rejected: list[tuple[EpistemicTransition, list[str]]],
    ) -> list[EpistemicTransition]:
        candidates = self._generate(state, query, rejected)
        self._last_candidates = candidates
        return [c.transition for c in candidates]

    # ---- Inspection / benchmark surface --------------------------------

    @property
    def last_candidates(self) -> list[ProposalCandidate]:
        return list(self._last_candidates)

    # ---- Generation pipeline -------------------------------------------

    def _generate(
        self,
        state,
        query,
        rejected: list[tuple[EpistemicTransition, list[str]]],
    ) -> list[ProposalCandidate]:
        attempts = 0
        while attempts <= self.max_internal_retries:
            attempts += 1
            prompt = self.build_prompt(state, query, rejected, attempt=attempts)
            try:
                completion = self.provider.generate(prompt, self.params)
            except Exception:
                # Provider-side failure for this iteration; treat as no candidates.
                return []
            transitions, parse_path = self.parse_candidates(completion, state)
            if transitions:
                return self._wrap(transitions, completion, prompt, parse_path)
        return []

    # ---- Prompt construction -------------------------------------------

    def build_prompt(
        self,
        state,
        query,
        rejected: list[tuple[EpistemicTransition, list[str]]],
        *,
        attempt: int = 1,
    ) -> str:
        sections = [
            self._section_system_preamble(),
            self._section_state(state),
            self._section_query(query),
            self._section_rejected(rejected),
            self._section_schema(),
            self._section_output_instructions(attempt=attempt),
        ]
        return "\n\n".join(s for s in sections if s)

    def _section_system_preamble(self) -> str:
        return self._fragments["system_preamble"].rstrip()

    def _section_state(self, state) -> str:
        summary = {
            "state_id":          state.state_id,
            "audit_head_sha256": state.audit_head_sha256,
            "object_count":      len(state.objects),
            "object_ids":        list(state.objects[: self.max_state_objects_in_prompt]),
        }
        return f"# Current epistemic state\n\n```json\n{json.dumps(summary, indent=2)}\n```"

    def _section_query(self, query) -> str:
        return f"# Query\n\n{query.serialize()}"

    def _section_rejected(
        self, rejected: list[tuple[EpistemicTransition, list[str]]]
    ) -> str:
        if not rejected:
            return "# Rejected candidates from this search\n\n(none)"
        items: list[dict[str, Any]] = []
        for tau, failures in rejected[-self.max_rejected_in_prompt:]:
            if tau is None:
                items.append({"candidate": None, "failures": list(failures)})
            else:
                items.append({
                    "candidate_id": tau.transition_id,
                    "regime":       tau.regime,
                    "failures":     list(failures),
                })
        return (
            "# Rejected candidates from this search\n\n"
            f"```json\n{json.dumps(items, indent=2)}\n```\n\n"
            "Do not propose candidates that repeat any of the above failures. "
            "If you cannot avoid them, return an empty JSON array `[]`."
        )

    def _section_schema(self) -> str:
        return (
            "# Transition schema\n\n"
            "Every candidate is a JSON object of this shape:\n\n"
            "```json\n"
            "{\n"
            '  "transition_id":  "<unique stable id>",\n'
            '  "from_state":     "<the state_id above, verbatim>",\n'
            '  "regime":         "A" | "B" | "C" | "D",\n'
            '  "object_added":   <object body matching the regime fragment below>,\n'
            '  "objects_removed": [],\n'
            '  "action":         null,\n'
            '  "authorization":  null,\n'
            f'  "proposer":       "{self.name}",\n'
            '  "proposed_at":    "<ISO-8601 UTC>"\n'
            "}\n"
            "```\n\n"
            "## Class A — deterministic verification\n\n"
            f"{self._fragments['class_a_fragment']}\n\n"
            "## Class B — instrumented empirical verification\n\n"
            f"{self._fragments['class_b_fragment']}\n\n"
            "## Class C — protocol-bound consensus\n\n"
            f"{self._fragments['class_c_fragment']}\n\n"
            "## Class D — interpretive governance\n\n"
            f"{self._fragments['class_d_fragment']}"
        )

    def _section_output_instructions(self, *, attempt: int) -> str:
        retry_note = ""
        if attempt > 1:
            retry_note = (
                f"\n\nThis is internal retry attempt {attempt}. The previous "
                "output failed to parse as JSON. Emit ONLY a JSON array. "
                "No code fences. No prose. Start with `[` and end with `]`."
            )
        return (
            "# Output\n\n"
            "Return a JSON array of zero or more transition objects. "
            "Use the schema and class fragments above. Emit nothing else."
            + retry_note
        )

    # ---- Parsing -------------------------------------------------------

    def parse_candidates(
        self,
        completion: CompletionResult,
        state,
    ) -> tuple[list[EpistemicTransition], str]:
        text = completion.text.strip()
        parse_path = "native"

        fence = _CODE_FENCE_RE.match(text)
        if fence is not None:
            text = fence.group("body").strip()
            parse_path = "fence_stripped"

        parsed = self._try_json(text)
        if parsed is None:
            m = _JSON_ARRAY_RE.search(text)
            if m is not None:
                parsed = self._try_json(m.group(0))
                if parsed is not None:
                    parse_path = "regex_fallback_arr"
        if parsed is None:
            m = _JSON_OBJECT_RE.search(text)
            if m is not None:
                parsed = self._try_json(m.group(0))
                if parsed is not None:
                    parse_path = "regex_fallback_obj"

        if parsed is None:
            return [], "failed"

        if isinstance(parsed, dict):
            for wrapper_key in ("transitions", "candidates"):
                inner = parsed.get(wrapper_key)
                if isinstance(inner, list):
                    parsed = inner
                    break
            else:
                parsed = [parsed]
        if not isinstance(parsed, list):
            return [], "failed"

        out: list[EpistemicTransition] = []
        for body in parsed:
            tau = self._validate_one(body, state)
            if tau is not None:
                out.append(tau)
        return out, parse_path

    def _try_json(self, s: str) -> Any:
        try:
            return json.loads(s)
        except json.JSONDecodeError:
            return None

    def _validate_one(
        self,
        body: Any,
        state,
    ) -> EpistemicTransition | None:
        if not isinstance(body, dict):
            return None
        body.setdefault("from_state",      state.state_id)
        body.setdefault("objects_removed", [])
        body.setdefault("action",          None)
        body.setdefault("authorization",   None)
        body.setdefault("proposer",        self.name)
        body.setdefault("proposed_at",     utcnow_iso8601())
        if "transition_id" not in body:
            body["transition_id"] = self._derive_transition_id(body)
        try:
            return EpistemicTransition.from_dict(body)
        except (KeyError, ValueError, TypeError):
            return None

    def _derive_transition_id(self, body: dict[str, Any]) -> str:
        canonical = canonical_json_bytes(
            {k: v for k, v in body.items() if k != "transition_id"}
        )
        hex_part = sha256_hex(canonical).split(":", 1)[1][:16]
        return f"prop-{self.name}-{hex_part}"

    # ---- Wrapping & cost metadata --------------------------------------

    def _wrap(
        self,
        transitions: list[EpistemicTransition],
        completion: CompletionResult,
        prompt: str,
        parse_path: str,
    ) -> list[ProposalCandidate]:
        prompt_sha     = sha256_hex(prompt.encode("utf-8"))
        completion_sha = sha256_hex(completion.text.encode("utf-8"))
        cost           = self._cost_metadata(completion, prompt_sha, completion_sha)
        out: list[ProposalCandidate] = []
        for tau in transitions:
            out.append(ProposalCandidate(
                proposer_id=self.name,
                proposal_id=tau.transition_id,
                transition=tau,
                confidence=self._estimate_confidence(tau),
                retrieval_refs=[],
                heuristic_reasoning=completion.text,
                estimated_regime=tau.regime,
                proposal_cost=cost,
                proposal_time_ms=completion.elapsed_ms,
                parse_path=parse_path,
            ))
        return out

    def _estimate_confidence(self, tau: EpistemicTransition) -> float:
        if tau.object_added is not None:
            supplied = tau.object_added.get("_proposer_confidence")
            if isinstance(supplied, (int, float)):
                return max(0.0, min(1.0, float(supplied)))
        score = 0.5
        if tau.regime in {"A", "B", "C", "D"}:
            score += 0.05
        if isinstance(tau.object_added, dict):
            score += 0.05
        return min(1.0, score)

    def _cost_metadata(
        self,
        completion: CompletionResult,
        prompt_sha: str,
        completion_sha: str,
    ) -> dict[str, Any]:
        return {
            "tokens_in":         completion.input_tokens,
            "tokens_out":        completion.output_tokens,
            "tokens_total":      completion.input_tokens + completion.output_tokens,
            "model_id":          completion.model_id,
            "provider":          completion.provider,
            "elapsed_ms":        completion.elapsed_ms,
            "finish_reason":     completion.finish_reason,
            "prompt_sha256":     prompt_sha,
            "completion_sha256": completion_sha,
            "deterministic":     self.deterministic,
            "seed":              self.params.seed,
            "temperature":       self.params.temperature,
        }

    # ---- Determinism replay capture ------------------------------------

    def deterministic_replay_capture(
        self,
        completion: CompletionResult,
        prompt: str,
    ) -> dict[str, Any]:
        return {
            "provider":          self.provider.name,
            "model_id":          self.provider.model_id,
            "deterministic":     self.deterministic,
            "seed":              self.params.seed,
            "temperature":       self.params.temperature,
            "top_p":             self.params.top_p,
            "max_tokens":        self.params.max_tokens,
            "response_format":   self.params.response_format,
            "prompt_sha256":     sha256_hex(prompt.encode("utf-8")),
            "completion_sha256": sha256_hex(completion.text.encode("utf-8")),
            "input_tokens":      completion.input_tokens,
            "output_tokens":     completion.output_tokens,
            "elapsed_ms":        completion.elapsed_ms,
            "finish_reason":     completion.finish_reason,
        }


# ---------------------------------------------------------------------------
# Provider implementations
# ---------------------------------------------------------------------------


class OpenAICompatibleProvider:
    """Works with OpenAI's API and any OpenAI-compatible server (Azure
    OpenAI, OpenRouter, vLLM, llama.cpp's --api-server, Ollama's OpenAI
    shim). Lazy-imports the openai package on construction so users without
    that SDK installed can still import this module."""

    name = "openai"

    def __init__(
        self,
        model_id: str,
        *,
        base_url: str | None = None,
        api_key: str | None = None,
    ) -> None:
        try:
            from openai import OpenAI  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover
            raise ImportError(
                "OpenAICompatibleProvider requires the `openai` package. "
                "Install with: pip install openai"
            ) from exc
        self._client = OpenAI(base_url=base_url, api_key=api_key)
        self.model_id = model_id

    def generate(
        self,
        prompt: str,
        params: GenerationParams,
    ) -> CompletionResult:
        kwargs: dict[str, Any] = {
            "model":       self.model_id,
            "messages":    [{"role": "user", "content": prompt}],
            "temperature": params.temperature,
            "top_p":       params.top_p,
            "max_tokens":  params.max_tokens,
        }
        if params.seed is not None:
            kwargs["seed"] = params.seed
        if params.response_format is not None:
            kwargs["response_format"] = params.response_format

        t0 = time.monotonic()
        resp = self._client.chat.completions.create(**kwargs)
        elapsed_ms = int((time.monotonic() - t0) * 1000)

        choice = resp.choices[0]
        return CompletionResult(
            text=choice.message.content or "",
            input_tokens=resp.usage.prompt_tokens,
            output_tokens=resp.usage.completion_tokens,
            elapsed_ms=elapsed_ms,
            finish_reason=choice.finish_reason or "stop",
            model_id=self.model_id,
            provider=self.name,
        )

    def supports_structured_output(self) -> bool:
        return True

    def supports_seeded_sampling(self) -> bool:
        return True


class AnthropicProvider:
    """Wraps the `anthropic` SDK. Uses an assistant-message prefill to
    encourage JSON-array output, since Anthropic does not expose
    OpenAI-style response_format in v0.1."""

    name = "anthropic"

    def __init__(self, model_id: str, *, api_key: str | None = None) -> None:
        try:
            from anthropic import Anthropic  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover
            raise ImportError(
                "AnthropicProvider requires the `anthropic` package. "
                "Install with: pip install anthropic"
            ) from exc
        self._client = Anthropic(api_key=api_key)
        self.model_id = model_id

    def generate(
        self,
        prompt: str,
        params: GenerationParams,
    ) -> CompletionResult:
        kwargs: dict[str, Any] = {
            "model":       self.model_id,
            "max_tokens":  params.max_tokens,
            "temperature": params.temperature,
            "top_p":       params.top_p,
            "messages": [
                {"role": "user",      "content": prompt},
                {"role": "assistant", "content": "["},
            ],
        }

        t0 = time.monotonic()
        resp = self._client.messages.create(**kwargs)
        elapsed_ms = int((time.monotonic() - t0) * 1000)

        body = "".join(b.text for b in resp.content if hasattr(b, "text"))
        text = body if body.lstrip().startswith("[") else "[" + body

        return CompletionResult(
            text=text,
            input_tokens=resp.usage.input_tokens,
            output_tokens=resp.usage.output_tokens,
            elapsed_ms=elapsed_ms,
            finish_reason=resp.stop_reason or "stop",
            model_id=self.model_id,
            provider=self.name,
        )

    def supports_structured_output(self) -> bool:
        return False

    def supports_seeded_sampling(self) -> bool:
        return False


class LocalOpenAICompatibleProvider(OpenAICompatibleProvider):
    """Most local servers (vLLM, llama.cpp's --api-server, Ollama's OpenAI
    shim, LM Studio) expose an OpenAI-compatible chat-completion endpoint.
    This subclass exists so audit metadata reports `provider: "local"`."""

    name = "local"

    def __init__(
        self,
        model_id: str,
        *,
        base_url: str = "http://localhost:8000/v1",
        api_key: str = "not-needed",
    ) -> None:
        super().__init__(model_id, base_url=base_url, api_key=api_key)


class DeterministicMockProvider:
    """Returns canned completions in fixed order. Used by tests and demos
    to exercise the proposer without invoking a real model."""

    name = "mock"

    def __init__(
        self,
        model_id: str,
        completions: list[str],
        *,
        approximate_token_ratio: int = 4,
    ) -> None:
        self.model_id = model_id
        self._completions = list(completions)
        self._index = 0
        self._approximate_token_ratio = approximate_token_ratio

    def generate(
        self,
        prompt: str,
        params: GenerationParams,
    ) -> CompletionResult:
        if self._index >= len(self._completions):
            text = ""
        else:
            text = self._completions[self._index]
            self._index += 1
        return CompletionResult(
            text=text,
            input_tokens=max(1, len(prompt) // self._approximate_token_ratio),
            output_tokens=max(0, len(text) // self._approximate_token_ratio),
            elapsed_ms=0,
            finish_reason="stop",
            model_id=self.model_id,
            provider=self.name,
        )

    def supports_structured_output(self) -> bool:
        return True

    def supports_seeded_sampling(self) -> bool:
        return True


# ---------------------------------------------------------------------------
# Benchmark hook
# ---------------------------------------------------------------------------


@dataclass
class ProposerRunMetrics:
    proposals_emitted:   int
    parse_failures:      int
    kernel_passes:       int
    kernel_rejections:   int
    auth_denials:        int
    committed:           int
    refused:             bool
    total_tokens_in:     int
    total_tokens_out:    int
    total_elapsed_ms:    int


def measured_search(
    runtime,
    query,
    proposer: TransformerProposer,
    max_iters: int = 64,
):
    """Run runtime.search with proposer and return (result, ProposerRunMetrics).

    Wraps the proposer's propose() method to capture per-batch metadata via
    the ProposalCandidate records on `proposer.last_candidates`. The metrics
    are computed after the search completes by inspecting the search result
    and the proposer's emission record.
    """
    metrics = ProposerRunMetrics(
        proposals_emitted=0,
        parse_failures=0,
        kernel_passes=0,
        kernel_rejections=0,
        auth_denials=0,
        committed=0,
        refused=False,
        total_tokens_in=0,
        total_tokens_out=0,
        total_elapsed_ms=0,
    )
    original_propose = proposer.propose
    parse_failure_iterations = 0

    def observed_propose(state, q, rejected):
        nonlocal parse_failure_iterations
        out = original_propose(state, q, rejected)
        last = proposer.last_candidates
        if last:
            for c in last:
                metrics.proposals_emitted += 1
                metrics.total_tokens_in += c.proposal_cost.get("tokens_in", 0)
                metrics.total_tokens_out += c.proposal_cost.get("tokens_out", 0)
                metrics.total_elapsed_ms += c.proposal_time_ms
                if c.parse_path == "failed":
                    metrics.parse_failures += 1
        else:
            # No candidates returned and no last_candidates record either:
            # the proposer either parse-failed on every retry attempt or the
            # provider returned an empty completion. Count as one parse
            # failure for accounting purposes.
            parse_failure_iterations += 1
        return out

    proposer.propose = observed_propose  # type: ignore[method-assign]
    try:
        result = runtime.search(query, proposer, max_iters=max_iters)
    finally:
        proposer.propose = original_propose  # type: ignore[method-assign]

    metrics.parse_failures += parse_failure_iterations
    metrics.refused = result.refusal is not None
    if result.refusal is not None:
        for entry in result.refusal.candidates_rejected:
            failures = entry.get("legitimacy_failures") or []
            if any("AG: " in f or "AG1" in f or "AG2" in f or "AG3" in f for f in failures):
                metrics.auth_denials += 1
            elif failures and entry.get("candidate_id") not in (None, "no-candidate"):
                metrics.kernel_rejections += 1
    if not metrics.refused:
        metrics.committed = 1
    metrics.kernel_passes = max(
        0,
        metrics.proposals_emitted - metrics.kernel_rejections - metrics.parse_failures,
    )
    return result, metrics
