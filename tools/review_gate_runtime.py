#!/usr/bin/env python3
"""WiseOrder/Intellagent — REVIEW GATE RUNTIME v0.1.

Deterministic reviewer admission of proposer output, with zero execution
authority. Reads a proposer JSON file, re-derives the proposer's
deterministic hash, re-classifies every proposed command against the v0.1
deny set and the v0.2 execute allowlist, validates required fields, and
writes an ``approved`` or ``rejected`` review artifact under
``reports/review_gate_runtime/``.

Architecture: ``proposer -> review gate -> executor``. NEVER
``proposer -> executor`` and NEVER ``review gate -> subprocess``. The
gate's strongest verb is a single JSON file write.

Spec: REVIEW-GATE-RUNTIME-v0.1.md (top-level).
Companion: PROPOSER-RUNTIME-v0.1.md, REAL-AGENT-RUNTIME-v0.2.md.

CLI:
  review_gate_runtime.py review --proposal PATH \
                                [--expected-work-order-id ID] \
                                [--reviewer-id ID]
      Read proposer JSON at PATH, validate, write review artifact under
      reports/review_gate_runtime/. Exit 0 on approved, 1 on rejected.
      Default --reviewer-id is "review-gate-01".

  review_gate_runtime.py self-check
      Run the eight self-check fixtures end-to-end. Refresh the runtime
      report at reports/review_gate_runtime/review_gate_runtime_v0.1.
      {md,json}. Exit 0 if all eight pass, 1 otherwise.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

# Reuse v0.1 / v0.2 deny set, allowlist, and identity table verbatim. The
# reviewer never widens these surfaces; it only reads them.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from real_agent_runtime import (  # noqa: E402  (path-injected sibling import)
    EXECUTE_ALLOWED_COMMANDS,
    FORBIDDEN_COMMAND_PATTERNS,
    IDENTITIES,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = REPO_ROOT / "reports" / "review_gate_runtime"
FIXTURES_DIR = REPORTS_DIR / "_fixtures"
RUNTIME_VERSION = "v0.1"
DEFAULT_REVIEWER_ID = "review-gate-01"
PROPOSAL_CAP = 3


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _now_iso_with_micros() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _safe_str(value: object) -> str:
    return value if isinstance(value, str) else ""


def _safe_list(value: object) -> list:
    return value if isinstance(value, list) else []


def _proposer_hash_payload(proposal: dict) -> dict:
    """Return the audit-stable subset of a proposer record.

    Mirrors PROPOSER-RUNTIME-v0.1's ``_compute_deterministic_hash``: excludes
    ``proposal_id``, ``timestamp``, ``deterministic_hash``, ``exit_status``.
    """
    return {
        "agent_id": _safe_str(proposal.get("agent_id")),
        "allowed_command_matches": _safe_list(proposal.get("allowed_command_matches")),
        "commands_proposed": _safe_list(proposal.get("commands_proposed")),
        "commands_rejected": _safe_list(proposal.get("commands_rejected")),
        "policy_rejections": _safe_list(proposal.get("policy_rejections")),
        "rationale": _safe_str(proposal.get("rationale")),
        "runtime_version": _safe_str(proposal.get("runtime_version")),
        "work_order_id": _safe_str(proposal.get("work_order_id")),
    }


def recompute_proposer_hash(proposal: dict) -> str:
    payload = _proposer_hash_payload(proposal)
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(canonical).hexdigest()


# ---------------------------------------------------------------------------
# Review artifact
# ---------------------------------------------------------------------------


@dataclass
class ReviewArtifact:
    review_id: str = ""
    proposal_id: str = ""
    work_order_id: str = ""
    reviewer_id: str = ""
    decision: str = "rejected"
    approval_scope: list[dict] = field(default_factory=list)
    rejected_commands: list[dict] = field(default_factory=list)
    rejection_reasons: list[str] = field(default_factory=list)
    deterministic_hash_verified: bool = False
    timestamp: str = ""
    review_hash: str = ""
    runtime_version: str = RUNTIME_VERSION
    exit_status: int = 1


def _add_reason(artifact: ReviewArtifact, code: str) -> None:
    if code not in artifact.rejection_reasons:
        artifact.rejection_reasons.append(code)


def _record_command_rejection(
    artifact: ReviewArtifact, command: str, code: str, reason: str,
) -> None:
    artifact.rejected_commands.append({
        "command": command,
        "code": code,
        "reason": reason,
    })


def _compute_review_hash(artifact: ReviewArtifact) -> str:
    """Hash the audit-stable subset of the review artifact.

    Excludes ``review_id``, ``timestamp``, ``review_hash``, and
    ``exit_status`` (derived). Two reviews of the same proposal under the
    same reviewer identity MUST produce byte-identical review hashes.
    """
    payload = {
        "approval_scope": artifact.approval_scope,
        "decision": artifact.decision,
        "deterministic_hash_verified": artifact.deterministic_hash_verified,
        "proposal_id": artifact.proposal_id,
        "rejected_commands": artifact.rejected_commands,
        "rejection_reasons": artifact.rejection_reasons,
        "reviewer_id": artifact.reviewer_id,
        "runtime_version": artifact.runtime_version,
        "work_order_id": artifact.work_order_id,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(canonical).hexdigest()


# ---------------------------------------------------------------------------
# Per-command classifier (v0.2 verbatim matcher)
# ---------------------------------------------------------------------------


def _classify_proposed_command(command: str) -> tuple[bool, str, str, str]:
    """Return ``(eligible, allowed_command_match, code, reason)``.

    ``eligible`` is ``True`` only when no forbidden pattern matches and the
    command matches an entry in EXECUTE_ALLOWED_COMMANDS by exact equality
    or starts-with-plus-space (the v0.2 matcher, used verbatim).
    """
    cmd = command.strip()
    for pattern in FORBIDDEN_COMMAND_PATTERNS:
        if pattern in cmd:
            return (False, "", "forbidden_command", f"matches forbidden pattern '{pattern}'")
    for allowed in EXECUTE_ALLOWED_COMMANDS:
        if cmd == allowed or cmd.startswith(allowed + " "):
            return (True, allowed, "", "")
    return (False, "", "not_in_execute_allowlist", "not in v0.2 execute allowlist")


# ---------------------------------------------------------------------------
# Review
# ---------------------------------------------------------------------------


def review(
    proposal_path: Path,
    *,
    expected_work_order_id: str | None = None,
    reviewer_id: str = DEFAULT_REVIEWER_ID,
    reports_dir: Path | None = None,
) -> ReviewArtifact:
    """Read proposer JSON at ``proposal_path``, validate, write review artifact.

    Returns the in-memory artifact. Always writes the artifact to
    ``reports_dir`` (default ``reports/review_gate_runtime/``).
    """
    out_dir = reports_dir if reports_dir is not None else REPORTS_DIR
    timestamp = _now_iso_with_micros()
    artifact = ReviewArtifact(
        reviewer_id=reviewer_id,
        timestamp=timestamp,
        decision="rejected",
        exit_status=1,
    )

    if not proposal_path.exists():
        _add_reason(artifact, "proposal_file_missing")
        _record_command_rejection(
            artifact, "", "proposal_file_missing",
            f"proposal not found at {proposal_path}",
        )
        artifact.review_id = _make_review_id(reviewer_id, "noProposal", timestamp)
        artifact.review_hash = _compute_review_hash(artifact)
        _write_review(artifact, out_dir)
        return artifact

    raw = proposal_path.read_text(encoding="utf-8")
    try:
        proposal = json.loads(raw)
    except json.JSONDecodeError as exc:
        _add_reason(artifact, "proposal_json_invalid")
        _record_command_rejection(
            artifact, "", "proposal_json_invalid",
            f"proposal JSON parse error: {exc}",
        )
        artifact.review_id = _make_review_id(reviewer_id, "badJson", timestamp)
        artifact.review_hash = _compute_review_hash(artifact)
        _write_review(artifact, out_dir)
        return artifact

    if not isinstance(proposal, dict):
        _add_reason(artifact, "proposal_json_invalid")
        _record_command_rejection(
            artifact, "", "proposal_json_invalid",
            "proposal JSON top-level value is not an object",
        )
        artifact.review_id = _make_review_id(reviewer_id, "badJson", timestamp)
        artifact.review_hash = _compute_review_hash(artifact)
        _write_review(artifact, out_dir)
        return artifact

    proposal_id = _safe_str(proposal.get("proposal_id")).strip()
    work_order_id = _safe_str(proposal.get("work_order_id")).strip()
    agent_id = _safe_str(proposal.get("agent_id")).strip()
    rationale = _safe_str(proposal.get("rationale")).strip()
    runtime_version = _safe_str(proposal.get("runtime_version")).strip()
    claimed_hash = _safe_str(proposal.get("deterministic_hash")).strip()
    commands_proposed = _safe_list(proposal.get("commands_proposed"))

    artifact.proposal_id = proposal_id
    artifact.work_order_id = work_order_id
    artifact.review_id = _make_review_id(reviewer_id, proposal_id or "noProposalId", timestamp)

    # Required-field checks.
    if not proposal_id:
        _add_reason(artifact, "missing_proposal_id")
    if not work_order_id:
        _add_reason(artifact, "missing_work_order_id")
    if expected_work_order_id is not None and work_order_id != expected_work_order_id:
        _add_reason(artifact, "wrong_work_order_id")
        _record_command_rejection(
            artifact, "", "wrong_work_order_id",
            f"proposal work_order_id '{work_order_id}' "
            f"does not equal expected '{expected_work_order_id}'",
        )
    if not agent_id:
        _add_reason(artifact, "missing_agent_id")
    elif agent_id not in IDENTITIES:
        _add_reason(artifact, "unknown_proposer")
        _record_command_rejection(
            artifact, "", "unknown_proposer",
            f"proposer agent_id '{agent_id}' is not in v0.1/v0.2 IDENTITIES",
        )
    if runtime_version != "v0.1":
        _add_reason(artifact, "unreadable_proposer_runtime_version")
        _record_command_rejection(
            artifact, "", "unreadable_proposer_runtime_version",
            f"proposer runtime_version '{runtime_version}' is not 'v0.1'",
        )
    if not rationale:
        _add_reason(artifact, "empty_rationale")

    # Hash verification.
    recomputed = recompute_proposer_hash(proposal)
    artifact.deterministic_hash_verified = (recomputed == claimed_hash)
    if not artifact.deterministic_hash_verified:
        _add_reason(artifact, "deterministic_hash_mismatch")
        _record_command_rejection(
            artifact, "", "deterministic_hash_mismatch",
            f"recomputed hash {recomputed} != claimed {claimed_hash}",
        )

    # Command-count cap.
    if not commands_proposed:
        _add_reason(artifact, "no_commands_to_approve")
    elif len(commands_proposed) > PROPOSAL_CAP:
        _add_reason(artifact, "too_many_commands")
        _record_command_rejection(
            artifact, "", "too_many_commands",
            f"commands_proposed length {len(commands_proposed)} > {PROPOSAL_CAP}",
        )

    # Per-command classification (run for every entry, regardless of cap, so
    # the reviewer surface every offending command in its rejection list).
    approval_scope: list[dict] = []
    for entry in commands_proposed:
        if not isinstance(entry, dict):
            _record_command_rejection(
                artifact, "", "proposal_json_invalid",
                "commands_proposed entry is not an object",
            )
            _add_reason(artifact, "proposal_json_invalid")
            continue
        cmd_text = _safe_str(entry.get("command")).strip()
        eligible, match, code, reason = _classify_proposed_command(cmd_text)
        if eligible:
            approval_scope.append({
                "command": cmd_text,
                "allowed_command_match": match,
            })
        else:
            _record_command_rejection(artifact, cmd_text, code, reason)
            _add_reason(artifact, code)

    # Decision.
    if artifact.rejection_reasons:
        artifact.decision = "rejected"
        artifact.approval_scope = []
        artifact.exit_status = 1
    else:
        artifact.decision = "approved"
        artifact.approval_scope = approval_scope
        artifact.exit_status = 0

    artifact.review_hash = _compute_review_hash(artifact)
    _write_review(artifact, out_dir)
    return artifact


def _make_review_id(reviewer_id: str, proposal_id_or_marker: str, timestamp: str) -> str:
    safe_reviewer = reviewer_id.replace("-", "_")
    safe_proposal = (
        proposal_id_or_marker.replace("/", "_").replace(":", "_")
        if proposal_id_or_marker
        else "noProposalId"
    )
    if len(safe_proposal) > 80:
        safe_proposal = safe_proposal[:80]
    safe_ts = (
        timestamp.replace(":", "")
        .replace("-", "")
        .replace(".", "")
        .replace("Z", "")
    )
    return f"review-{safe_reviewer}-{safe_proposal}-{safe_ts}Z"


# ---------------------------------------------------------------------------
# Output writers
# ---------------------------------------------------------------------------


def _write_review(artifact: ReviewArtifact, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / f"{artifact.review_id}.json"
    md_path = out_dir / f"{artifact.review_id}.md"
    json_path.write_text(
        json.dumps(asdict(artifact), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    md_path.write_text(_render_markdown(artifact), encoding="utf-8")


def _render_markdown(artifact: ReviewArtifact) -> str:
    lines: list[str] = []
    lines.append(f"# {artifact.review_id}")
    lines.append("")
    lines.append(f"- proposal_id: `{artifact.proposal_id}`")
    lines.append(f"- work_order_id: `{artifact.work_order_id}`")
    lines.append(f"- reviewer_id: `{artifact.reviewer_id}`")
    lines.append(f"- runtime_version: `{artifact.runtime_version}`")
    lines.append(f"- timestamp: `{artifact.timestamp}`")
    lines.append(f"- decision: **{artifact.decision}**")
    lines.append(f"- deterministic_hash_verified: `{artifact.deterministic_hash_verified}`")
    lines.append(f"- exit_status: `{artifact.exit_status}`")
    lines.append(f"- review_hash: `{artifact.review_hash}`")
    lines.append("")
    lines.append(f"## Approval scope ({len(artifact.approval_scope)})")
    lines.append("")
    if artifact.approval_scope:
        for entry in artifact.approval_scope:
            lines.append(
                f"- `{entry['command']}`  (matches: `{entry['allowed_command_match']}`)"
            )
    else:
        lines.append("_(none)_")
    lines.append("")
    lines.append(f"## Rejected commands ({len(artifact.rejected_commands)})")
    lines.append("")
    if artifact.rejected_commands:
        for entry in artifact.rejected_commands:
            lines.append(
                f"- `{entry['command']}` — `{entry['code']}` — {entry['reason']}"
            )
    else:
        lines.append("_(none)_")
    lines.append("")
    lines.append(f"## Rejection reasons ({len(artifact.rejection_reasons)})")
    lines.append("")
    if artifact.rejection_reasons:
        for code in artifact.rejection_reasons:
            lines.append(f"- `{code}`")
    else:
        lines.append("_(none)_")
    lines.append("")
    lines.append("## Reviewer authority law")
    lines.append("")
    lines.append(
        "> The reviewer gate has approval authority only over proposal "
        "admissibility. It has zero execution authority. Executor admission "
        "remains controlled by the real-agent runtime."
    )
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Self-check fixtures
# ---------------------------------------------------------------------------


def _base_valid_proposal_dict() -> dict:
    proposal = {
        "agent_id": "canon_guardian-01",
        "allowed_command_matches": ["cat", "find", "ls"],
        "commands_proposed": [
            {
                "command": "cat",
                "argv_preview": ["cat"],
                "allowed_command_match": "cat",
                "allowed_files_scope": ["**"],
                "rationale": "Reviewer-gate fixture rationale.",
            },
            {
                "command": "find",
                "argv_preview": ["find"],
                "allowed_command_match": "find",
                "allowed_files_scope": ["**"],
                "rationale": "Reviewer-gate fixture rationale.",
            },
            {
                "command": "ls",
                "argv_preview": ["ls"],
                "allowed_command_match": "ls",
                "allowed_files_scope": ["**"],
                "rationale": "Reviewer-gate fixture rationale.",
            },
        ],
        "commands_rejected": [],
        "policy_rejections": [],
        "proposal_id": "proposal-canon_guardian_01-WO-FIX-REVIEW-VALID-001-FIXED",
        "rationale": "Reviewer-gate fixture rationale.",
        "runtime_version": "v0.1",
        "timestamp": "2026-05-08T22:00:00.000000Z",
        "work_order_id": "WO-FIX-REVIEW-VALID-001",
        "exit_status": 0,
    }
    proposal["deterministic_hash"] = recompute_proposer_hash(proposal)
    return proposal


def _emit_proposal_fixture(name: str, proposal: dict) -> Path:
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIXTURES_DIR / f"proposal_{name}.json"
    path.write_text(
        json.dumps(proposal, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


@dataclass
class FixtureResult:
    name: str
    passed: bool
    detail: str
    review_id: str
    review_hash: str
    decision: str


def _check_fixture_1_approved() -> FixtureResult:
    name = "valid_proposal_approved"
    proposal = _base_valid_proposal_dict()
    path = _emit_proposal_fixture(name, proposal)
    artifact = review(path)
    ok = (
        artifact.decision == "approved"
        and artifact.deterministic_hash_verified is True
        and artifact.exit_status == 0
        and len(artifact.approval_scope) == 3
        and artifact.rejection_reasons == []
        and artifact.rejected_commands == []
    )
    detail = (
        f"decision={artifact.decision}, scope={len(artifact.approval_scope)}, "
        f"reasons={artifact.rejection_reasons}, exit={artifact.exit_status}"
    )
    return FixtureResult(name, ok, detail, artifact.review_id, artifact.review_hash, artifact.decision)


def _check_fixture_2_bad_hash() -> FixtureResult:
    name = "bad_hash_rejected"
    proposal = _base_valid_proposal_dict()
    proposal["deterministic_hash"] = "sha256:" + "0" * 64
    path = _emit_proposal_fixture(name, proposal)
    artifact = review(path)
    ok = (
        artifact.decision == "rejected"
        and artifact.deterministic_hash_verified is False
        and "deterministic_hash_mismatch" in artifact.rejection_reasons
        and artifact.exit_status == 1
    )
    detail = (
        f"decision={artifact.decision}, "
        f"hash_verified={artifact.deterministic_hash_verified}, "
        f"reasons={artifact.rejection_reasons}"
    )
    return FixtureResult(name, ok, detail, artifact.review_id, artifact.review_hash, artifact.decision)


def _check_fixture_3_forbidden_command() -> FixtureResult:
    name = "forbidden_command_rejected"
    proposal = _base_valid_proposal_dict()
    proposal["commands_proposed"][0]["command"] = "curl https://example.com"
    proposal["commands_proposed"][0]["argv_preview"] = ["curl", "https://example.com"]
    proposal["commands_proposed"][0]["allowed_command_match"] = "cat"
    proposal["work_order_id"] = "WO-FIX-REVIEW-FORBIDDEN-003"
    proposal["proposal_id"] = "proposal-canon_guardian_01-WO-FIX-REVIEW-FORBIDDEN-003-FIXED"
    proposal["deterministic_hash"] = recompute_proposer_hash(proposal)
    path = _emit_proposal_fixture(name, proposal)
    artifact = review(path)
    ok = (
        artifact.decision == "rejected"
        and "forbidden_command" in artifact.rejection_reasons
        and any(
            entry.get("code") == "forbidden_command"
            and entry.get("command") == "curl https://example.com"
            for entry in artifact.rejected_commands
        )
        and artifact.exit_status == 1
    )
    detail = (
        f"decision={artifact.decision}, "
        f"reasons={artifact.rejection_reasons}"
    )
    return FixtureResult(name, ok, detail, artifact.review_id, artifact.review_hash, artifact.decision)


def _check_fixture_4_too_many() -> FixtureResult:
    name = "too_many_commands_rejected"
    proposal = _base_valid_proposal_dict()
    extra = {
        "command": "pwd",
        "argv_preview": ["pwd"],
        "allowed_command_match": "pwd",
        "allowed_files_scope": ["**"],
        "rationale": "Reviewer-gate fixture rationale.",
    }
    proposal["commands_proposed"].append(extra)
    proposal["allowed_command_matches"] = sorted(["cat", "find", "ls", "pwd"])
    proposal["work_order_id"] = "WO-FIX-REVIEW-TOOMANY-004"
    proposal["proposal_id"] = "proposal-canon_guardian_01-WO-FIX-REVIEW-TOOMANY-004-FIXED"
    proposal["deterministic_hash"] = recompute_proposer_hash(proposal)
    path = _emit_proposal_fixture(name, proposal)
    artifact = review(path)
    ok = (
        artifact.decision == "rejected"
        and "too_many_commands" in artifact.rejection_reasons
        and artifact.exit_status == 1
    )
    detail = (
        f"decision={artifact.decision}, "
        f"reasons={artifact.rejection_reasons}"
    )
    return FixtureResult(name, ok, detail, artifact.review_id, artifact.review_hash, artifact.decision)


def _check_fixture_5_empty_rationale() -> FixtureResult:
    name = "empty_rationale_rejected"
    proposal = _base_valid_proposal_dict()
    proposal["rationale"] = ""
    for entry in proposal["commands_proposed"]:
        entry["rationale"] = ""
    proposal["work_order_id"] = "WO-FIX-REVIEW-NORATIONALE-005"
    proposal["proposal_id"] = "proposal-canon_guardian_01-WO-FIX-REVIEW-NORATIONALE-005-FIXED"
    proposal["deterministic_hash"] = recompute_proposer_hash(proposal)
    path = _emit_proposal_fixture(name, proposal)
    artifact = review(path)
    ok = (
        artifact.decision == "rejected"
        and "empty_rationale" in artifact.rejection_reasons
        and artifact.exit_status == 1
    )
    detail = (
        f"decision={artifact.decision}, "
        f"reasons={artifact.rejection_reasons}"
    )
    return FixtureResult(name, ok, detail, artifact.review_id, artifact.review_hash, artifact.decision)


def _check_fixture_6_wrong_wo() -> FixtureResult:
    name = "wrong_work_order_id_rejected"
    proposal = _base_valid_proposal_dict()
    proposal["work_order_id"] = "WO-FIX-REVIEW-WRONGWO-006"
    proposal["proposal_id"] = "proposal-canon_guardian_01-WO-FIX-REVIEW-WRONGWO-006-FIXED"
    proposal["deterministic_hash"] = recompute_proposer_hash(proposal)
    path = _emit_proposal_fixture(name, proposal)
    artifact = review(path, expected_work_order_id="WO-DIFFERENT-EXPECTED-XYZ")
    ok = (
        artifact.decision == "rejected"
        and "wrong_work_order_id" in artifact.rejection_reasons
        and artifact.exit_status == 1
    )
    detail = (
        f"decision={artifact.decision}, "
        f"reasons={artifact.rejection_reasons}"
    )
    return FixtureResult(name, ok, detail, artifact.review_id, artifact.review_hash, artifact.decision)


def _check_fixture_7_unknown_proposer() -> FixtureResult:
    name = "unknown_proposer_rejected"
    proposal = _base_valid_proposal_dict()
    proposal["agent_id"] = "unknown-99"
    proposal["work_order_id"] = "WO-FIX-REVIEW-UNKNOWN-007"
    proposal["proposal_id"] = "proposal-unknown_99-WO-FIX-REVIEW-UNKNOWN-007-FIXED"
    proposal["deterministic_hash"] = recompute_proposer_hash(proposal)
    path = _emit_proposal_fixture(name, proposal)
    artifact = review(path)
    ok = (
        artifact.decision == "rejected"
        and "unknown_proposer" in artifact.rejection_reasons
        and artifact.exit_status == 1
    )
    detail = (
        f"decision={artifact.decision}, "
        f"reasons={artifact.rejection_reasons}"
    )
    return FixtureResult(name, ok, detail, artifact.review_id, artifact.review_hash, artifact.decision)


def _check_fixture_8_hash_stable() -> FixtureResult:
    name = "review_artifact_hash_stable"
    proposal = _base_valid_proposal_dict()
    proposal["work_order_id"] = "WO-FIX-REVIEW-STABLE-008"
    proposal["proposal_id"] = "proposal-canon_guardian_01-WO-FIX-REVIEW-STABLE-008-FIXED"
    proposal["deterministic_hash"] = recompute_proposer_hash(proposal)
    path = _emit_proposal_fixture(name, proposal)
    first = review(path)
    second = review(path)
    ok = (
        first.decision == "approved"
        and second.decision == "approved"
        and first.review_hash == second.review_hash
        and first.review_id != second.review_id
        and first.timestamp != second.timestamp
        and first.exit_status == 0
        and second.exit_status == 0
    )
    detail = (
        f"first_hash={first.review_hash}, second_hash={second.review_hash}, "
        f"ids_differ={first.review_id != second.review_id}, "
        f"timestamps_differ={first.timestamp != second.timestamp}"
    )
    return FixtureResult(name, ok, detail, first.review_id, first.review_hash, first.decision)


_FIXTURES: tuple = (
    _check_fixture_1_approved,
    _check_fixture_2_bad_hash,
    _check_fixture_3_forbidden_command,
    _check_fixture_4_too_many,
    _check_fixture_5_empty_rationale,
    _check_fixture_6_wrong_wo,
    _check_fixture_7_unknown_proposer,
    _check_fixture_8_hash_stable,
)


def self_check() -> int:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    results: list[FixtureResult] = [fn() for fn in _FIXTURES]
    all_ok = all(r.passed for r in results)

    summary = {
        "runtime": "review_gate_runtime",
        "runtime_version": RUNTIME_VERSION,
        "timestamp": _now_iso_with_micros(),
        "all_passed": all_ok,
        "fixtures": [
            {
                "name": r.name,
                "passed": r.passed,
                "decision": r.decision,
                "detail": r.detail,
                "review_id": r.review_id,
                "review_hash": r.review_hash,
            }
            for r in results
        ],
    }
    (REPORTS_DIR / f"review_gate_runtime_{RUNTIME_VERSION}.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    md_lines: list[str] = []
    md_lines.append(f"# Review Gate Runtime {RUNTIME_VERSION} self-check")
    md_lines.append("")
    md_lines.append(f"- timestamp: `{summary['timestamp']}`")
    md_lines.append(f"- all_passed: `{all_ok}`")
    md_lines.append("")
    md_lines.append("## Fixtures")
    md_lines.append("")
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        md_lines.append(f"- `{r.name}` — **{status}** — decision=`{r.decision}`")
        md_lines.append(f"  - review_id: `{r.review_id}`")
        md_lines.append(f"  - review_hash: `{r.review_hash}`")
        md_lines.append(f"  - detail: {r.detail}")
    md_lines.append("")
    md_lines.append("## Reviewer authority law")
    md_lines.append("")
    md_lines.append(
        "> The reviewer gate has approval authority only over proposal "
        "admissibility. It has zero execution authority. Executor admission "
        "remains controlled by the real-agent runtime."
    )
    md_lines.append("")
    (REPORTS_DIR / f"review_gate_runtime_{RUNTIME_VERSION}.md").write_text(
        "\n".join(md_lines), encoding="utf-8",
    )

    print(f"REVIEW-GATE-RUNTIME {RUNTIME_VERSION} self-check: {len(results)} fixtures")
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        print(f"  [{status}] {r.name} (decision={r.decision})")
        if not r.passed:
            print(f"         detail: {r.detail}")
    print(f"all_passed={all_ok}")
    return 0 if all_ok else 1


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _cli_review(args: argparse.Namespace) -> int:
    proposal_path = Path(args.proposal).resolve()
    artifact = review(
        proposal_path,
        expected_work_order_id=args.expected_work_order_id,
        reviewer_id=args.reviewer_id,
    )
    print(f"REVIEW {artifact.review_id} decision={artifact.decision} exit_status={artifact.exit_status}")
    if artifact.approval_scope:
        print(f"  approval_scope: {len(artifact.approval_scope)}")
        for entry in artifact.approval_scope:
            print(f"    - {entry['command']}  (matches: {entry['allowed_command_match']})")
    if artifact.rejected_commands:
        print(f"  rejected_commands: {len(artifact.rejected_commands)}")
        for entry in artifact.rejected_commands:
            print(f"    - {entry['command']}  ({entry['code']}: {entry['reason']})")
    if artifact.rejection_reasons:
        print(f"  rejection_reasons: {artifact.rejection_reasons}")
    print(f"  deterministic_hash_verified: {artifact.deterministic_hash_verified}")
    print(f"  review_hash: {artifact.review_hash}")
    return artifact.exit_status


def _cli_self_check(_args: argparse.Namespace) -> int:
    return self_check()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="review_gate_runtime",
        description="WiseOrder Review Gate Runtime v0.1 — deterministic proposal admission.",
    )
    sub = parser.add_subparsers(dest="verb", required=True)

    p_review = sub.add_parser(
        "review",
        help="emit a review artifact for a proposer JSON output",
    )
    p_review.add_argument("--proposal", required=True, help="path to proposer JSON output")
    p_review.add_argument(
        "--expected-work-order-id",
        default=None,
        help="if supplied, reject when proposal.work_order_id != this value",
    )
    p_review.add_argument(
        "--reviewer-id",
        default=DEFAULT_REVIEWER_ID,
        help=f"reviewer identity (default: {DEFAULT_REVIEWER_ID})",
    )
    p_review.set_defaults(func=_cli_review)

    p_check = sub.add_parser(
        "self-check",
        help="run the eight self-check fixtures and refresh the runtime report",
    )
    p_check.set_defaults(func=_cli_self_check)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
