#!/usr/bin/env python3
"""WiseOrder/Intellagent — PIPELINE RUNTIME v0.1.

End-to-end governed handoff: ``proposer -> review gate -> executor``.

Composes three previously independent runtimes (PROPOSER-RUNTIME-v0.1,
REVIEW-GATE-RUNTIME-v0.1, REAL-AGENT-RUNTIME-v0.2 execute mode) into a
single deterministic orchestrator. The pipeline does not introduce any
new policy. It does not add execution authority beyond the executor's.
It does not add networking, daemons, retries, or model calls. It adds
exactly one capability: the conversion of an admitted work order into
either a manifest-backed executed command or a refusal-coded aggregate
manifest, depending on which gate fires first.

Spec: PIPELINE-RUNTIME-v0.1.md (top-level).

CLI:
  pipeline_runtime.py run --work-order PATH \
                          --proposer-agent-id ID \
                          --reviewer-id ID \
                          --executor-agent-id ID \
                          [--expected-work-order-id ID] \
                          [--timeout SECONDS]
      Run all three stages and write an aggregate manifest under
      reports/pipeline_runtime/. Exit 0 on final_status=executed,
      1 otherwise.

  pipeline_runtime.py self-check
      Run the eight self-check fixtures end-to-end. Refresh
      reports/pipeline_runtime/pipeline_runtime_v0.1.{md,json}.
      Exit 0 iff all eight pass, 1 otherwise.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

# Sibling-module imports. Each runtime is reused verbatim; the pipeline
# never reaches into private state.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from real_agent_runtime import (  # noqa: E402
    RUNS_DIR as EXECUTOR_RUNS_DIR,
    EXECUTE_TIMEOUT_DEFAULT_S,
    REPO_ROOT,
    execute_run,
    repo_fingerprint,
)
from proposer_runtime import (  # noqa: E402
    REPORTS_DIR as PROPOSER_REPORTS_DIR,
    propose,
)
from review_gate_runtime import (  # noqa: E402
    DEFAULT_REVIEWER_ID,
    REPORTS_DIR as REVIEW_REPORTS_DIR,
    recompute_proposer_hash,
    review,
)

REPORTS_DIR = REPO_ROOT / "reports" / "pipeline_runtime"
FIXTURES_DIR = REPORTS_DIR / "_fixtures"
RUNTIME_VERSION = "v0.1"


# ---------------------------------------------------------------------------
# Aggregate manifest
# ---------------------------------------------------------------------------


@dataclass
class AggregateManifest:
    pipeline_id: str = ""
    work_order_id: str = ""
    proposer_artifact: str | None = None
    review_artifact: str | None = None
    executor_manifest: str | None = None
    proposer_hash: str = ""
    review_hash: str = ""
    review_decision: str = ""
    review_rejection_reasons: list[str] = field(default_factory=list)
    executor_manifest_hash: str | None = None
    final_status: str = ""
    refusal_reason: str = ""
    commands_proposed: list[str] = field(default_factory=list)
    commands_approved: list[str] = field(default_factory=list)
    commands_executed: list[str] = field(default_factory=list)
    timestamps: dict[str, str] = field(default_factory=dict)
    repo_fingerprint_before: str = ""
    repo_fingerprint_after: str = ""
    policy_violations: list[dict] = field(default_factory=list)
    pipeline_hash: str = ""
    runtime_version: str = RUNTIME_VERSION
    exit_status: int = 1


def _now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _make_pipeline_id(timestamp: str) -> str:
    safe = (
        timestamp.replace(":", "")
        .replace("-", "")
        .replace(".", "")
        .replace("Z", "")
    )
    return f"pipeline-{safe}Z"


def _compute_pipeline_hash(manifest: AggregateManifest) -> str:
    """Hash the audit-stable subset of the aggregate.

    Excludes path-bearing fields (which embed timestamps and run ids),
    timestamps themselves, the executor manifest hash (a sha256 of a
    JSON containing run-specific timestamps, durations, and sandbox
    paths), the reviewer's review_hash (which itself includes the
    proposer's proposal_id timestamp), the pipeline id, the pipeline
    hash itself, and the derived exit_status.

    Includes the reviewer's decision and sorted rejection_reasons
    instead of review_hash, preserving the audit signal of "what did
    the reviewer say" without inheriting the timestamp non-determinism.
    """
    payload = {
        "commands_approved": sorted(manifest.commands_approved),
        "commands_executed": sorted(manifest.commands_executed),
        "commands_proposed": sorted(manifest.commands_proposed),
        "final_status": manifest.final_status,
        "policy_violations": manifest.policy_violations,
        "proposer_hash": manifest.proposer_hash,
        "refusal_reason": manifest.refusal_reason,
        "repo_fingerprint_after": manifest.repo_fingerprint_after,
        "repo_fingerprint_before": manifest.repo_fingerprint_before,
        "review_decision": manifest.review_decision,
        "review_rejection_reasons": sorted(manifest.review_rejection_reasons),
        "runtime_version": manifest.runtime_version,
        "work_order_id": manifest.work_order_id,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(canonical).hexdigest()


def _hash_executor_manifest(path: Path | None) -> str | None:
    if path is None or not path.exists():
        return None
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------


def run(
    work_order_path: Path,
    *,
    proposer_agent_id: str,
    reviewer_id: str = DEFAULT_REVIEWER_ID,
    executor_agent_id: str,
    expected_work_order_id: str | None = None,
    timeout: float = EXECUTE_TIMEOUT_DEFAULT_S,
    reports_dir: Path | None = None,
) -> AggregateManifest:
    """Run proposer → review gate → executor and write the aggregate.

    Returns the in-memory manifest. Always writes to ``reports_dir``
    (default ``reports/pipeline_runtime/``).
    """
    out_dir = reports_dir if reports_dir is not None else REPORTS_DIR
    timestamps: dict[str, str] = {"start": _now_iso()}
    fp_before = repo_fingerprint(REPO_ROOT)
    manifest = AggregateManifest(
        pipeline_id=_make_pipeline_id(timestamps["start"]),
        repo_fingerprint_before=fp_before,
        timestamps=timestamps,
    )

    # Stage 1: proposer.
    proposal_record = propose(work_order_path, proposer_agent_id)
    timestamps["proposer_done"] = _now_iso()
    proposal_path = PROPOSER_REPORTS_DIR / f"{proposal_record.proposal_id}.json"
    manifest.proposer_artifact = str(proposal_path)
    manifest.proposer_hash = proposal_record.deterministic_hash
    manifest.work_order_id = proposal_record.work_order_id
    manifest.commands_proposed = sorted(
        entry.get("command", "")
        for entry in proposal_record.commands_proposed
    )

    # Stage 2: reviewer.
    review_artifact = review(
        proposal_path,
        expected_work_order_id=expected_work_order_id,
        reviewer_id=reviewer_id,
    )
    timestamps["review_done"] = _now_iso()
    review_path = REVIEW_REPORTS_DIR / f"{review_artifact.review_id}.json"
    manifest.review_artifact = str(review_path)
    manifest.review_hash = review_artifact.review_hash
    manifest.review_decision = review_artifact.decision
    manifest.review_rejection_reasons = list(review_artifact.rejection_reasons)
    manifest.commands_approved = sorted(
        entry.get("command", "")
        for entry in review_artifact.approval_scope
    )

    if review_artifact.decision != "approved":
        manifest.final_status = "refused_at_review"
        manifest.refusal_reason = (
            review_artifact.rejection_reasons[0]
            if review_artifact.rejection_reasons
            else "rejected_no_reason_recorded"
        )
        manifest.policy_violations.append({
            "stage": "review_gate",
            "code": manifest.refusal_reason,
            "detail": [
                {"code": entry.get("code"), "command": entry.get("command")}
                for entry in review_artifact.rejected_commands
            ],
        })
        manifest.executor_manifest = None
        manifest.executor_manifest_hash = None
        manifest.commands_executed = []
        timestamps["executor_done"] = ""
        timestamps["end"] = _now_iso()
        manifest.repo_fingerprint_after = repo_fingerprint(REPO_ROOT)
        manifest.pipeline_hash = _compute_pipeline_hash(manifest)
        manifest.exit_status = 1
        _write_aggregate(manifest, out_dir)
        return manifest

    # Stage 3: executor (only reached when review.decision == "approved").
    approved_cmds = list(manifest.commands_approved)
    run_manifest = execute_run(
        work_order_path,
        executor_agent_id,
        commands=approved_cmds,
        timeout=timeout,
    )
    timestamps["executor_done"] = _now_iso()
    executor_manifest_path = EXECUTOR_RUNS_DIR / f"{run_manifest.run_id}.json"
    manifest.executor_manifest = str(executor_manifest_path)
    manifest.executor_manifest_hash = _hash_executor_manifest(executor_manifest_path)
    manifest.commands_executed = sorted(run_manifest.commands_allowed)
    for violation in run_manifest.policy_violations:
        entry = dict(violation)
        entry.setdefault("stage", "executor")
        manifest.policy_violations.append(entry)

    if run_manifest.exit_status != 0:
        if run_manifest.commands_allowed:
            manifest.final_status = "executed_with_violations"
        else:
            manifest.final_status = "refused_at_executor"
        manifest.refusal_reason = (
            manifest.policy_violations[0].get("code", "executor_refused")
            if manifest.policy_violations
            else "executor_refused"
        )
        manifest.exit_status = 1
    else:
        manifest.final_status = "executed"
        manifest.refusal_reason = ""
        manifest.exit_status = 0

    timestamps["end"] = _now_iso()
    manifest.repo_fingerprint_after = repo_fingerprint(REPO_ROOT)
    if manifest.repo_fingerprint_before != manifest.repo_fingerprint_after:
        manifest.policy_violations.append({
            "stage": "pipeline",
            "code": "repo_fingerprint_drift",
            "reason": "repo_fingerprint changed across pipeline run; source repo must not mutate",
        })
        manifest.exit_status = 1
        if manifest.final_status == "executed":
            manifest.final_status = "executed_with_violations"
            manifest.refusal_reason = "repo_fingerprint_drift"

    manifest.pipeline_hash = _compute_pipeline_hash(manifest)
    _write_aggregate(manifest, out_dir)
    return manifest


# ---------------------------------------------------------------------------
# Output writers
# ---------------------------------------------------------------------------


def _write_aggregate(manifest: AggregateManifest, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / f"{manifest.pipeline_id}.json"
    md_path = out_dir / f"{manifest.pipeline_id}.md"
    json_path.write_text(
        json.dumps(asdict(manifest), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    md_path.write_text(_render_markdown(manifest), encoding="utf-8")


def _render_markdown(m: AggregateManifest) -> str:
    lines: list[str] = []
    lines.append(f"# {m.pipeline_id}")
    lines.append("")
    lines.append(f"- work_order_id: `{m.work_order_id}`")
    lines.append(f"- runtime_version: `{m.runtime_version}`")
    lines.append(f"- final_status: **{m.final_status}**")
    lines.append(f"- refusal_reason: `{m.refusal_reason}`")
    lines.append(f"- exit_status: `{m.exit_status}`")
    lines.append(f"- pipeline_hash: `{m.pipeline_hash}`")
    lines.append("")
    lines.append("## Stage hashes")
    lines.append("")
    lines.append(f"- proposer_hash: `{m.proposer_hash}`")
    lines.append(f"- review_hash: `{m.review_hash}`")
    lines.append(f"- executor_manifest_hash: `{m.executor_manifest_hash}`")
    lines.append("")
    lines.append("## Stage artifacts")
    lines.append("")
    lines.append(f"- proposer_artifact: `{m.proposer_artifact}`")
    lines.append(f"- review_artifact: `{m.review_artifact}`")
    lines.append(f"- executor_manifest: `{m.executor_manifest}`")
    lines.append("")
    lines.append("## Commands")
    lines.append("")
    lines.append(f"- proposed: `{m.commands_proposed}`")
    lines.append(f"- approved: `{m.commands_approved}`")
    lines.append(f"- executed: `{m.commands_executed}`")
    lines.append("")
    lines.append("## Repo fingerprint")
    lines.append("")
    lines.append(f"- before: `{m.repo_fingerprint_before}`")
    lines.append(f"- after:  `{m.repo_fingerprint_after}`")
    lines.append("")
    lines.append("## Timestamps")
    lines.append("")
    for k, v in m.timestamps.items():
        lines.append(f"- {k}: `{v}`")
    lines.append("")
    lines.append(f"## Policy violations ({len(m.policy_violations)})")
    lines.append("")
    if m.policy_violations:
        for v in m.policy_violations:
            stage = v.get("stage", "unknown")
            code = v.get("code", "unknown")
            lines.append(f"- `[{stage}]` `{code}` — {v}")
    else:
        lines.append("_(none)_")
    lines.append("")
    lines.append("## Pipeline boundary law")
    lines.append("")
    lines.append(
        "> The pipeline does not create autonomy. The pipeline creates "
        "deterministic governed handoff between proposal, review, and "
        "execution. Execution remains bounded by real-agent runtime "
        "policy. Reviewer approval is necessary but not sufficient; "
        "executor admission still governs execution."
    )
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Self-check fixtures
# ---------------------------------------------------------------------------


def _emit_wo_fixture(
    name: str,
    *,
    work_order_id: str,
    assigned_to: str,
    required_gates: list[str],
    objective: str = "Pipeline self-check fixture: run an allowlisted command inside an executor sandbox.",
    status: str = "approved",
) -> Path:
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIXTURES_DIR / f"wo_{name}.yaml"
    lines: list[str] = [
        f'work_order_id: "{work_order_id}"',
        'agent_role: "builder"',
        f'assigned_to: "{assigned_to}"',
        f'objective: "{objective}"',
        "",
        "allowed_files:",
        '  - "*.md"',
        '  - "workforce/**"',
        '  - "reports/**"',
        "",
        "forbidden_files:",
        '  - "runtime/**"',
        '  - "intellagent_runtime/**"',
        '  - "vectors/**"',
        '  - "canonicalization/**"',
        '  - "SPEC.md"',
        "",
        f'status: "{status}"',
        "",
        "required_gates:",
    ]
    for gate in required_gates:
        lines.append(f'  - "{gate}"')
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


@dataclass
class FixtureResult:
    name: str
    passed: bool
    detail: str
    pipeline_id: str
    pipeline_hash: str
    final_status: str
    executor_invoked: bool


def _check_fixture_1_valid_executes() -> FixtureResult:
    name = "valid_pipeline_executes_allowed_command"
    wo = _emit_wo_fixture(
        name,
        work_order_id="WO-FIX-PIPELINE-VALID-001",
        assigned_to="builder-01",
        required_gates=["pwd"],
    )
    fp_before = repo_fingerprint(REPO_ROOT)
    m = run(
        wo,
        proposer_agent_id="builder-01",
        reviewer_id=DEFAULT_REVIEWER_ID,
        executor_agent_id="builder-01",
        timeout=30.0,
    )
    fp_after = repo_fingerprint(REPO_ROOT)
    ok = (
        m.final_status == "executed"
        and m.exit_status == 0
        and m.commands_proposed == ["pwd"]
        and m.commands_approved == ["pwd"]
        and m.commands_executed == ["pwd"]
        and m.executor_manifest is not None
        and Path(m.executor_manifest).exists()
        and m.repo_fingerprint_before == m.repo_fingerprint_after
        and fp_before == fp_after
    )
    detail = (
        f"final_status={m.final_status}, executed={m.commands_executed}, "
        f"executor_manifest={'present' if m.executor_manifest else 'absent'}"
    )
    return FixtureResult(
        name, ok, detail, m.pipeline_id, m.pipeline_hash, m.final_status,
        executor_invoked=m.executor_manifest is not None,
    )


def _check_fixture_2_review_blocks() -> FixtureResult:
    name = "reviewer_rejection_prevents_executor_call"
    wo = _emit_wo_fixture(
        name,
        work_order_id="WO-FIX-PIPELINE-REVIEWBLOCK-002",
        assigned_to="builder-01",
        required_gates=["pwd"],
    )
    m = run(
        wo,
        proposer_agent_id="builder-01",
        reviewer_id=DEFAULT_REVIEWER_ID,
        executor_agent_id="builder-01",
        expected_work_order_id="WO-MISMATCH-EXPECTED-XYZ",
        timeout=30.0,
    )
    ok = (
        m.final_status == "refused_at_review"
        and m.exit_status == 1
        and m.executor_manifest is None
        and m.executor_manifest_hash is None
        and m.commands_executed == []
        and m.refusal_reason == "wrong_work_order_id"
    )
    detail = (
        f"final_status={m.final_status}, refusal={m.refusal_reason}, "
        f"executor_invoked={m.executor_manifest is not None}"
    )
    return FixtureResult(
        name, ok, detail, m.pipeline_id, m.pipeline_hash, m.final_status,
        executor_invoked=m.executor_manifest is not None,
    )


def _check_fixture_3_mutated_hash() -> FixtureResult:
    """Run proposer normally, mutate its JSON deterministic_hash, then
    invoke the reviewer against the mutated file. The executor must NOT
    be invoked. We construct a partial aggregate manifest by hand to
    record what happened so this fixture's report matches the others.
    """
    name = "mutated_proposal_hash_rejected"
    wo = _emit_wo_fixture(
        name,
        work_order_id="WO-FIX-PIPELINE-MUTATEDHASH-003",
        assigned_to="builder-01",
        required_gates=["pwd"],
    )
    timestamps: dict[str, str] = {"start": _now_iso()}
    fp_before = repo_fingerprint(REPO_ROOT)
    proposal_record = propose(wo, "builder-01")
    timestamps["proposer_done"] = _now_iso()
    proposal_path = PROPOSER_REPORTS_DIR / f"{proposal_record.proposal_id}.json"

    proposal_text = proposal_path.read_text(encoding="utf-8")
    proposal_dict = json.loads(proposal_text)
    proposal_dict["deterministic_hash"] = "sha256:" + "0" * 64
    proposal_path.write_text(
        json.dumps(proposal_dict, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    review_artifact = review(proposal_path, reviewer_id=DEFAULT_REVIEWER_ID)
    timestamps["review_done"] = _now_iso()
    timestamps["executor_done"] = ""
    timestamps["end"] = _now_iso()

    aggregate = AggregateManifest(
        pipeline_id=_make_pipeline_id(timestamps["start"]),
        work_order_id=proposal_record.work_order_id,
        proposer_artifact=str(proposal_path),
        review_artifact=str(REVIEW_REPORTS_DIR / f"{review_artifact.review_id}.json"),
        executor_manifest=None,
        proposer_hash=proposal_record.deterministic_hash,
        review_hash=review_artifact.review_hash,
        review_decision=review_artifact.decision,
        review_rejection_reasons=list(review_artifact.rejection_reasons),
        executor_manifest_hash=None,
        final_status="refused_at_review",
        refusal_reason=(
            review_artifact.rejection_reasons[0]
            if review_artifact.rejection_reasons else ""
        ),
        commands_proposed=sorted(
            e.get("command", "") for e in proposal_record.commands_proposed
        ),
        commands_approved=[],
        commands_executed=[],
        timestamps=timestamps,
        repo_fingerprint_before=fp_before,
        repo_fingerprint_after=repo_fingerprint(REPO_ROOT),
        policy_violations=[{
            "stage": "review_gate",
            "code": "deterministic_hash_mismatch",
            "detail": "proposer JSON was hand-mutated between propose() and review()",
        }],
        exit_status=1,
    )
    aggregate.pipeline_hash = _compute_pipeline_hash(aggregate)
    _write_aggregate(aggregate, REPORTS_DIR)

    ok = (
        review_artifact.decision == "rejected"
        and review_artifact.deterministic_hash_verified is False
        and "deterministic_hash_mismatch" in review_artifact.rejection_reasons
        and aggregate.executor_manifest is None
        and aggregate.commands_executed == []
        and aggregate.final_status == "refused_at_review"
    )
    detail = (
        f"review_decision={review_artifact.decision}, "
        f"hash_verified={review_artifact.deterministic_hash_verified}, "
        f"reasons={review_artifact.rejection_reasons}"
    )
    return FixtureResult(
        name, ok, detail, aggregate.pipeline_id, aggregate.pipeline_hash,
        aggregate.final_status, executor_invoked=False,
    )


def _check_fixture_4_forbidden_command() -> FixtureResult:
    name = "forbidden_command_proposal_rejected"
    wo = _emit_wo_fixture(
        name,
        work_order_id="WO-FIX-PIPELINE-FORBIDDEN-004",
        assigned_to="builder-01",
        required_gates=["curl https://example.com"],
    )
    m = run(
        wo,
        proposer_agent_id="builder-01",
        reviewer_id=DEFAULT_REVIEWER_ID,
        executor_agent_id="builder-01",
        timeout=10.0,
    )
    ok = (
        m.final_status == "refused_at_review"
        and m.exit_status == 1
        and m.executor_manifest is None
        and m.commands_executed == []
        and m.commands_proposed == []
    )
    detail = (
        f"final_status={m.final_status}, refusal={m.refusal_reason}, "
        f"proposed={m.commands_proposed}, "
        f"executor_invoked={m.executor_manifest is not None}"
    )
    return FixtureResult(
        name, ok, detail, m.pipeline_id, m.pipeline_hash, m.final_status,
        executor_invoked=m.executor_manifest is not None,
    )


def _check_fixture_5_wrong_executor() -> FixtureResult:
    name = "wrong_executor_identity_refused"
    wo = _emit_wo_fixture(
        name,
        work_order_id="WO-FIX-PIPELINE-WRONGEXEC-005",
        assigned_to="builder-01",
        required_gates=["pwd"],
    )
    m = run(
        wo,
        proposer_agent_id="builder-01",
        reviewer_id=DEFAULT_REVIEWER_ID,
        executor_agent_id="release-01",
        timeout=10.0,
    )
    ok = (
        m.final_status == "refused_at_executor"
        and m.exit_status == 1
        and m.executor_manifest is not None
        and m.commands_executed == []
        and "assigned_to_mismatch" in (
            v.get("code", "") for v in m.policy_violations
        )
    )
    detail = (
        f"final_status={m.final_status}, "
        f"executed={m.commands_executed}, "
        f"violations={[v.get('code') for v in m.policy_violations]}"
    )
    return FixtureResult(
        name, ok, detail, m.pipeline_id, m.pipeline_hash, m.final_status,
        executor_invoked=m.executor_manifest is not None,
    )


def _check_fixture_6_repo_unchanged() -> FixtureResult:
    name = "source_repo_unchanged_after_pipeline"
    wo = _emit_wo_fixture(
        name,
        work_order_id="WO-FIX-PIPELINE-REPOSAFE-006",
        assigned_to="builder-01",
        required_gates=["pwd"],
    )
    fp_before = repo_fingerprint(REPO_ROOT)
    m = run(
        wo,
        proposer_agent_id="builder-01",
        reviewer_id=DEFAULT_REVIEWER_ID,
        executor_agent_id="builder-01",
        timeout=30.0,
    )
    fp_after = repo_fingerprint(REPO_ROOT)
    drift_codes = {v.get("code") for v in m.policy_violations}
    ok = (
        fp_before == fp_after
        and m.repo_fingerprint_before == m.repo_fingerprint_after
        and "repo_fingerprint_drift" not in drift_codes
        and m.final_status == "executed"
    )
    detail = (
        f"fp_pipeline_match={m.repo_fingerprint_before == m.repo_fingerprint_after}, "
        f"fp_outer_match={fp_before == fp_after}, "
        f"final_status={m.final_status}"
    )
    return FixtureResult(
        name, ok, detail, m.pipeline_id, m.pipeline_hash, m.final_status,
        executor_invoked=m.executor_manifest is not None,
    )


def _check_fixture_7_hash_stable() -> FixtureResult:
    name = "aggregate_manifest_hash_stable"
    wo = _emit_wo_fixture(
        name,
        work_order_id="WO-FIX-PIPELINE-STABLE-007",
        assigned_to="builder-01",
        required_gates=["pwd"],
    )
    first = run(
        wo,
        proposer_agent_id="builder-01",
        reviewer_id=DEFAULT_REVIEWER_ID,
        executor_agent_id="builder-01",
        timeout=30.0,
    )
    second = run(
        wo,
        proposer_agent_id="builder-01",
        reviewer_id=DEFAULT_REVIEWER_ID,
        executor_agent_id="builder-01",
        timeout=30.0,
    )
    ok = (
        first.pipeline_hash == second.pipeline_hash
        and first.pipeline_id != second.pipeline_id
        and first.timestamps != second.timestamps
        and first.final_status == "executed"
        and second.final_status == "executed"
        and first.exit_status == 0
        and second.exit_status == 0
    )
    detail = (
        f"first_hash={first.pipeline_hash}, "
        f"second_hash={second.pipeline_hash}, "
        f"ids_differ={first.pipeline_id != second.pipeline_id}"
    )
    return FixtureResult(
        name, ok, detail, first.pipeline_id, first.pipeline_hash,
        first.final_status, executor_invoked=first.executor_manifest is not None,
    )


def _check_fixture_8_no_exec_without_review(
    earlier_results: list[FixtureResult],
) -> FixtureResult:
    """Fixture 8 is a structural assertion across the rejection fixtures.

    Reads the aggregate manifests written by fixtures 2, 3, and 4 (every
    case where the reviewer rejected). For each, asserts:
      - executor_manifest is None
      - commands_executed == []
      - executor_invoked == False
    """
    name = "no_execution_occurs_without_approved_review_artifact"
    target_names = {
        "reviewer_rejection_prevents_executor_call",
        "mutated_proposal_hash_rejected",
        "forbidden_command_proposal_rejected",
    }
    target_results = [r for r in earlier_results if r.name in target_names]

    bad: list[str] = []
    for r in target_results:
        agg_path = REPORTS_DIR / f"{r.pipeline_id}.json"
        if not agg_path.exists():
            bad.append(f"{r.name}: aggregate file missing")
            continue
        agg = json.loads(agg_path.read_text(encoding="utf-8"))
        if agg.get("executor_manifest") is not None:
            bad.append(f"{r.name}: executor_manifest is not null")
        if agg.get("commands_executed") != []:
            bad.append(f"{r.name}: commands_executed is non-empty")
        if r.executor_invoked:
            bad.append(f"{r.name}: pipeline reported executor was invoked")

    ok = (
        len(target_results) == len(target_names)
        and not bad
    )
    detail = (
        f"checked={len(target_results)}/{len(target_names)} rejection fixtures, "
        f"violations={bad}"
    )
    return FixtureResult(
        name, ok, detail, "(structural)", "(structural)",
        "n/a", executor_invoked=False,
    )


def self_check() -> int:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    results: list[FixtureResult] = []
    results.append(_check_fixture_1_valid_executes())
    results.append(_check_fixture_2_review_blocks())
    results.append(_check_fixture_3_mutated_hash())
    results.append(_check_fixture_4_forbidden_command())
    results.append(_check_fixture_5_wrong_executor())
    results.append(_check_fixture_6_repo_unchanged())
    results.append(_check_fixture_7_hash_stable())
    results.append(_check_fixture_8_no_exec_without_review(results))

    all_ok = all(r.passed for r in results)

    summary = {
        "runtime": "pipeline_runtime",
        "runtime_version": RUNTIME_VERSION,
        "timestamp": _now_iso(),
        "all_passed": all_ok,
        "fixtures": [
            {
                "name": r.name,
                "passed": r.passed,
                "final_status": r.final_status,
                "executor_invoked": r.executor_invoked,
                "pipeline_id": r.pipeline_id,
                "pipeline_hash": r.pipeline_hash,
                "detail": r.detail,
            }
            for r in results
        ],
    }
    (REPORTS_DIR / f"pipeline_runtime_{RUNTIME_VERSION}.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    md_lines: list[str] = []
    md_lines.append(f"# Pipeline Runtime {RUNTIME_VERSION} self-check")
    md_lines.append("")
    md_lines.append(f"- timestamp: `{summary['timestamp']}`")
    md_lines.append(f"- all_passed: `{all_ok}`")
    md_lines.append("")
    md_lines.append("## Fixtures")
    md_lines.append("")
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        md_lines.append(
            f"- `{r.name}` — **{status}** — final_status=`{r.final_status}` — "
            f"executor_invoked=`{r.executor_invoked}`"
        )
        md_lines.append(f"  - pipeline_id: `{r.pipeline_id}`")
        md_lines.append(f"  - pipeline_hash: `{r.pipeline_hash}`")
        md_lines.append(f"  - detail: {r.detail}")
    md_lines.append("")
    md_lines.append("## Pipeline boundary law")
    md_lines.append("")
    md_lines.append(
        "> The pipeline does not create autonomy. The pipeline creates "
        "deterministic governed handoff between proposal, review, and "
        "execution. Execution remains bounded by real-agent runtime "
        "policy. Reviewer approval is necessary but not sufficient; "
        "executor admission still governs execution."
    )
    md_lines.append("")
    (REPORTS_DIR / f"pipeline_runtime_{RUNTIME_VERSION}.md").write_text(
        "\n".join(md_lines), encoding="utf-8",
    )

    print(f"PIPELINE-RUNTIME {RUNTIME_VERSION} self-check: {len(results)} fixtures")
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        marker = "(executor ran)" if r.executor_invoked else "(no executor)"
        print(f"  [{status}] {r.name} {marker} final_status={r.final_status}")
        if not r.passed:
            print(f"         detail: {r.detail}")
    print(f"all_passed={all_ok}")
    return 0 if all_ok else 1


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _cli_run(args: argparse.Namespace) -> int:
    wo_path = Path(args.work_order).resolve()
    m = run(
        wo_path,
        proposer_agent_id=args.proposer_agent_id,
        reviewer_id=args.reviewer_id,
        executor_agent_id=args.executor_agent_id,
        expected_work_order_id=args.expected_work_order_id,
        timeout=args.timeout,
    )
    print(f"PIPELINE {m.pipeline_id} final_status={m.final_status} exit_status={m.exit_status}")
    print(f"  proposer_hash:           {m.proposer_hash}")
    print(f"  review_hash:             {m.review_hash}")
    print(f"  executor_manifest_hash:  {m.executor_manifest_hash}")
    print(f"  pipeline_hash:           {m.pipeline_hash}")
    print(f"  commands_proposed: {m.commands_proposed}")
    print(f"  commands_approved: {m.commands_approved}")
    print(f"  commands_executed: {m.commands_executed}")
    if m.refusal_reason:
        print(f"  refusal_reason: {m.refusal_reason}")
    return m.exit_status


def _cli_self_check(_args: argparse.Namespace) -> int:
    return self_check()


def _cli_run_fixture(args: argparse.Namespace) -> int:
    """Convenience: run() against the canonical valid fixture.

    Used by ``make pipeline-run-fixture``. Emits a fresh fixture work
    order under ``reports/pipeline_runtime/_fixtures/`` so the target
    is reproducible without external state.
    """
    wo = _emit_wo_fixture(
        "fixture_run",
        work_order_id="WO-FIX-PIPELINE-RUN-FIXTURE",
        assigned_to="builder-01",
        required_gates=["pwd"],
    )
    args.work_order = str(wo)
    args.proposer_agent_id = "builder-01"
    args.reviewer_id = DEFAULT_REVIEWER_ID
    args.executor_agent_id = "builder-01"
    args.expected_work_order_id = None
    args.timeout = 30.0
    return _cli_run(args)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="pipeline_runtime",
        description="WiseOrder Pipeline Runtime v0.1 — proposer → review → executor.",
    )
    sub = parser.add_subparsers(dest="verb", required=True)

    p_run = sub.add_parser("run", help="run all three stages on one work order")
    p_run.add_argument("--work-order", required=True)
    p_run.add_argument("--proposer-agent-id", required=True)
    p_run.add_argument("--reviewer-id", default=DEFAULT_REVIEWER_ID)
    p_run.add_argument("--executor-agent-id", required=True)
    p_run.add_argument("--expected-work-order-id", default=None)
    p_run.add_argument("--timeout", type=float, default=EXECUTE_TIMEOUT_DEFAULT_S)
    p_run.set_defaults(func=_cli_run)

    p_check = sub.add_parser("self-check", help="run the eight self-check fixtures")
    p_check.set_defaults(func=_cli_self_check)

    p_fixture = sub.add_parser(
        "run-fixture",
        help="run() against the canonical valid pipeline fixture",
    )
    p_fixture.set_defaults(func=_cli_run_fixture)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
