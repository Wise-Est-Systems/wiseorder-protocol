#!/usr/bin/env python3
"""WiseOrder/Intellagent — PROPOSER RUNTIME v0.1.

Bounded candidate-command generation under governance, with zero execution
authority. Reads an admitted work order, intersects ``required_gates`` with
the v0.1 ``FORBIDDEN_COMMAND_PATTERNS`` deny set, the v0.2
``EXECUTE_ALLOWED_COMMANDS`` allowlist, and the work order's
``allowed_files`` glob list, and emits a deterministically-ordered,
capped-at-three candidate set as a JSON proposal under
``reports/proposer_runtime/``.

Architecture: ``proposer -> reviewer gate -> executor``. NEVER
``proposer -> execute``. The proposer's strongest verb is a single JSON
file write. There is no ``subprocess``, no ``os.exec*``, no ``os.spawn*``,
no shell, no model call, no RPC, no socket. The proposer carries no state
between runs and runs only when explicitly invoked.

Spec: PROPOSER-RUNTIME-v0.1.md (top-level).
Companion: REAL-AGENT-RUNTIME-v0.1.md, REAL-AGENT-RUNTIME-v0.2.md.

CLI:
  proposer_runtime.py propose --work-order PATH --agent-id ID
      Read work order at PATH under identity ID, derive the candidate set,
      write the proposal record and Markdown summary under
      reports/proposer_runtime/. Exit 0 iff admission accepted, rationale
      non-empty, and at least one candidate command was proposed without
      a terminal refusal. Exit 1 otherwise.

  proposer_runtime.py self-check
      Run the seven self-check fixtures end-to-end. Refresh the runtime
      report at reports/proposer_runtime/proposer_runtime_v0.1.{md,json}.
      Exit 0 iff all seven match expected outcome, 1 otherwise.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import fnmatch
import hashlib
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

# Reuse v0.1 / v0.2 admission, classifier, and allowlist verbatim. The
# proposer never widens these surfaces; it only reads them.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from real_agent_runtime import (  # noqa: E402  (path-injected sibling import)
    EXECUTE_ALLOWED_COMMANDS,
    FORBIDDEN_COMMAND_PATTERNS,
    IDENTITIES,
    admit,
    parse_flat_yaml,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = REPO_ROOT / "reports" / "proposer_runtime"
FIXTURES_DIR = REPORTS_DIR / "_fixtures"
RUNTIME_VERSION = "v0.1"
PROPOSAL_CAP = 3

# Paths whose appearance in a candidate's argv constitutes recursive
# self-modification. Matches the proposer's own module, its report tree,
# and its specification document.
SELF_MOD_TOKENS: tuple[str, ...] = (
    "tools/proposer_runtime.py",
    "reports/proposer_runtime/",
    "reports/proposer_runtime",
    "PROPOSER-RUNTIME-v0.1.md",
)

# Stricter subset of FORBIDDEN_COMMAND_PATTERNS, raised under a more
# specific code so a reviewer reading the proposal sees "network" at a
# glance rather than only "forbidden_pattern".
NETWORK_TOKENS: tuple[str, ...] = (
    "http://",
    "https://",
    "://",
    "curl",
    "wget",
    "ssh",
    "scp",
)


# ---------------------------------------------------------------------------
# Helpers (no subprocess; no network; no model)
# ---------------------------------------------------------------------------


def _as_str_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if isinstance(item, str)]
    return []


def _now_iso_with_micros() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _run_id(agent_id: str, work_order_id: str, timestamp: str) -> str:
    safe_ts = (
        timestamp.replace(":", "")
        .replace("-", "")
        .replace(".", "")
        .replace("Z", "")
    )
    safe_wo = (work_order_id or "noWO").replace("/", "_").replace(":", "_")
    safe_agent = agent_id.replace("-", "_")
    return f"{safe_agent}-{safe_wo}-{safe_ts}Z"


def _references_self(cmd: str) -> bool:
    return any(token in cmd for token in SELF_MOD_TOKENS)


def _references_network(cmd: str) -> bool:
    return any(token in cmd for token in NETWORK_TOKENS)


def _path_tokens(cmd: str) -> list[str]:
    """Return whitespace-separated tokens that look like repo-relative paths.

    A path token is any non-flag token containing ``/``. Bare flags
    (``-v``, ``--quiet``) are skipped. Bare command words such as
    ``make``, ``no-pseudocode``, ``cat``, ``ls`` are skipped because they
    contain no ``/``. The check is conservative on purpose: it only
    flags tokens that clearly point at a path so the allowlist
    comparison has something concrete to test.
    """
    tokens: list[str] = []
    for raw in cmd.split():
        if raw.startswith("-"):
            continue
        if "/" in raw:
            tokens.append(raw)
    return tokens


def _path_in_allowed_files(token: str, allowed_globs: list[str]) -> bool:
    return any(fnmatch.fnmatch(token, glob) for glob in allowed_globs)


# ---------------------------------------------------------------------------
# Proposal record
# ---------------------------------------------------------------------------


@dataclass
class ProposalRecord:
    proposal_id: str = ""
    work_order_id: str = ""
    agent_id: str = ""
    rationale: str = ""
    commands_proposed: list[dict] = field(default_factory=list)
    commands_rejected: list[dict] = field(default_factory=list)
    policy_rejections: list[str] = field(default_factory=list)
    allowed_command_matches: list[str] = field(default_factory=list)
    timestamp: str = ""
    deterministic_hash: str = ""
    runtime_version: str = RUNTIME_VERSION
    exit_status: int = 1


# Refusal codes that are recorded but do NOT, on their own, fail the run.
NON_TERMINAL_CODES: frozenset[str] = frozenset({"cap_exceeded"})


def _compute_deterministic_hash(record: ProposalRecord) -> str:
    """Hash the audit-stable subset of the record.

    Excludes ``proposal_id`` (contains a timestamp), ``timestamp``,
    ``deterministic_hash``, and ``exit_status`` (derived). Two runs of the
    same work order under the same proposer version MUST produce
    byte-identical hashes.
    """
    payload = {
        "agent_id": record.agent_id,
        "allowed_command_matches": record.allowed_command_matches,
        "commands_proposed": record.commands_proposed,
        "commands_rejected": record.commands_rejected,
        "policy_rejections": record.policy_rejections,
        "rationale": record.rationale,
        "runtime_version": record.runtime_version,
        "work_order_id": record.work_order_id,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(canonical).hexdigest()


def _add_rejection_code(record: ProposalRecord, code: str) -> None:
    if code not in record.policy_rejections:
        record.policy_rejections.append(code)


def _classify_one(
    command: str,
    allowed_files: list[str],
    record: ProposalRecord,
) -> tuple[bool, str]:
    """Classify a single candidate command.

    Returns ``(eligible, allowed_command_match)``. On rejection, mutates
    ``record.commands_rejected`` and ``record.policy_rejections`` and
    returns ``(False, "")``.

    Order: network -> recursive-self-modification -> forbidden_pattern ->
    execute allowlist -> path-outside-allowed-files. The order is
    deny-first throughout, but more-specific deny codes are raised
    before less-specific ones so reviewer-facing summaries remain
    legible.
    """
    cmd = command.strip()

    # Network refusal (more specific than forbidden_pattern). When a
    # network token also appears in FORBIDDEN_COMMAND_PATTERNS (e.g.
    # ``curl``, ``https://``), both codes are recorded in
    # policy_rejections so the audit trail names both surfaces.
    if _references_network(cmd):
        record.commands_rejected.append({
            "command": cmd,
            "reason": "candidate references a networking token",
            "code": "network_proposal",
        })
        _add_rejection_code(record, "network_proposal")
        for pattern in FORBIDDEN_COMMAND_PATTERNS:
            if pattern in cmd:
                _add_rejection_code(record, "forbidden_pattern")
                break
        return (False, "")

    # Recursive self-modification.
    if _references_self(cmd):
        record.commands_rejected.append({
            "command": cmd,
            "reason": "candidate references the proposer's own module, report tree, or specification",
            "code": "recursive_self_modification",
        })
        _add_rejection_code(record, "recursive_self_modification")
        return (False, "")

    # General forbidden pattern (deny-first, v0.1 verbatim).
    for pattern in FORBIDDEN_COMMAND_PATTERNS:
        if pattern in cmd:
            record.commands_rejected.append({
                "command": cmd,
                "reason": f"matches forbidden pattern '{pattern}'",
                "code": "forbidden_pattern",
            })
            _add_rejection_code(record, "forbidden_pattern")
            return (False, "")

    # Execute allowlist (v0.2 verbatim matcher: exact or starts-with-plus-space).
    match = ""
    for allowed in EXECUTE_ALLOWED_COMMANDS:
        if cmd == allowed or cmd.startswith(allowed + " "):
            match = allowed
            break
    if not match:
        record.commands_rejected.append({
            "command": cmd,
            "reason": "not in v0.2 execute allowlist",
            "code": "not_in_execute_allowlist",
        })
        _add_rejection_code(record, "not_in_execute_allowlist")
        return (False, "")

    # Path-outside-allowed-files. Any path-bearing token must match at
    # least one allowed_files glob.
    for token in _path_tokens(cmd):
        if not _path_in_allowed_files(token, allowed_files):
            record.commands_rejected.append({
                "command": cmd,
                "reason": f"path token '{token}' not matched by any allowed_files glob",
                "code": "path_outside_allowed_files",
            })
            _add_rejection_code(record, "path_outside_allowed_files")
            return (False, "")

    return (True, match)


# ---------------------------------------------------------------------------
# Propose
# ---------------------------------------------------------------------------


def propose(
    wo_path: Path,
    agent_id: str,
    *,
    reports_dir: Path | None = None,
) -> ProposalRecord:
    """Read work order at ``wo_path`` under identity ``agent_id`` and emit a proposal.

    Always writes the record to ``reports_dir`` (default
    ``reports/proposer_runtime/``) as both ``proposal-<run_id>.json`` and
    ``proposal-<run_id>.md``. Returns the in-memory record. Exit status 0
    is set iff: admission accepted, rationale non-empty, at least one
    command proposed, and no terminal refusal code raised.
    """
    out_dir = reports_dir if reports_dir is not None else REPORTS_DIR
    timestamp = _now_iso_with_micros()
    record = ProposalRecord(
        agent_id=agent_id,
        timestamp=timestamp,
        exit_status=1,
    )

    if not wo_path.exists():
        record.commands_rejected.append({
            "command": "",
            "reason": f"work order not found at {wo_path}",
            "code": "missing_required_field",
        })
        _add_rejection_code(record, "missing_required_field")
        record.proposal_id = "proposal-" + _run_id(agent_id, "noWO", timestamp)
        record.deterministic_hash = _compute_deterministic_hash(record)
        _write_proposal(record, out_dir)
        return record

    wo_fields = parse_flat_yaml(wo_path)
    admission = admit(wo_fields, agent_id)
    record.work_order_id = admission.work_order_id
    record.proposal_id = "proposal-" + _run_id(agent_id, admission.work_order_id, timestamp)

    if not admission.accepted:
        record.commands_rejected.append({
            "command": "",
            "reason": admission.reason,
            "code": admission.refusal_code,
        })
        _add_rejection_code(record, admission.refusal_code)
        record.deterministic_hash = _compute_deterministic_hash(record)
        _write_proposal(record, out_dir)
        return record

    if agent_id not in IDENTITIES:
        # Defensive: admit() already enforces this, but be explicit.
        record.commands_rejected.append({
            "command": "",
            "reason": f"unknown agent identity: {agent_id}",
            "code": "unknown_agent_identity",
        })
        _add_rejection_code(record, "unknown_agent_identity")
        record.deterministic_hash = _compute_deterministic_hash(record)
        _write_proposal(record, out_dir)
        return record

    objective_raw = wo_fields.get("objective", "")
    objective = (objective_raw if isinstance(objective_raw, str) else "").strip()
    if not objective:
        record.commands_rejected.append({
            "command": "",
            "reason": "work order objective is empty or whitespace-only",
            "code": "empty_rationale",
        })
        _add_rejection_code(record, "empty_rationale")
        record.deterministic_hash = _compute_deterministic_hash(record)
        _write_proposal(record, out_dir)
        return record

    record.rationale = objective
    allowed_files = _as_str_list(wo_fields.get("allowed_files"))
    required_gates = _as_str_list(wo_fields.get("required_gates"))

    candidate_eligible: list[dict] = []
    for gate in required_gates:
        cmd = gate.strip()
        if not cmd:
            continue
        eligible, match = _classify_one(cmd, allowed_files, record)
        if not eligible:
            continue
        candidate_eligible.append({
            "command": cmd,
            "argv_preview": cmd.split(),
            "allowed_command_match": match,
            "allowed_files_scope": list(allowed_files),
            "rationale": objective,
        })

    candidate_eligible.sort(key=lambda c: c["command"])

    if len(candidate_eligible) > PROPOSAL_CAP:
        _add_rejection_code(record, "cap_exceeded")
        for overflow in candidate_eligible[PROPOSAL_CAP:]:
            record.commands_rejected.append({
                "command": overflow["command"],
                "reason": f"proposal cap of {PROPOSAL_CAP} commands exceeded",
                "code": "cap_exceeded",
            })
        candidate_eligible = candidate_eligible[:PROPOSAL_CAP]

    record.commands_proposed = candidate_eligible
    record.allowed_command_matches = sorted({
        c["allowed_command_match"] for c in candidate_eligible
    })

    if not record.commands_proposed:
        _add_rejection_code(record, "empty_proposal")
        record.exit_status = 1
    else:
        terminal = [c for c in record.policy_rejections if c not in NON_TERMINAL_CODES]
        record.exit_status = 1 if terminal else 0

    record.deterministic_hash = _compute_deterministic_hash(record)
    _write_proposal(record, out_dir)
    return record


# ---------------------------------------------------------------------------
# Output writers
# ---------------------------------------------------------------------------


def _write_proposal(record: ProposalRecord, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / f"{record.proposal_id}.json"
    md_path = out_dir / f"{record.proposal_id}.md"
    json_path.write_text(
        json.dumps(asdict(record), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    md_path.write_text(_render_markdown(record), encoding="utf-8")


def _render_markdown(record: ProposalRecord) -> str:
    lines: list[str] = []
    lines.append(f"# {record.proposal_id}")
    lines.append("")
    lines.append(f"- work_order_id: `{record.work_order_id}`")
    lines.append(f"- agent_id: `{record.agent_id}`")
    lines.append(f"- runtime_version: `{record.runtime_version}`")
    lines.append(f"- timestamp: `{record.timestamp}`")
    lines.append(f"- exit_status: `{record.exit_status}`")
    lines.append(f"- deterministic_hash: `{record.deterministic_hash}`")
    lines.append("")
    lines.append("## Rationale")
    lines.append("")
    lines.append(record.rationale or "_(empty)_")
    lines.append("")
    lines.append(f"## Commands proposed ({len(record.commands_proposed)})")
    lines.append("")
    if record.commands_proposed:
        for idx, entry in enumerate(record.commands_proposed, start=1):
            lines.append(f"{idx}. `{entry['command']}`")
            lines.append(f"   - allowed_command_match: `{entry['allowed_command_match']}`")
            lines.append(f"   - allowed_files_scope: `{entry['allowed_files_scope']}`")
    else:
        lines.append("_(none)_")
    lines.append("")
    lines.append(f"## Commands rejected ({len(record.commands_rejected)})")
    lines.append("")
    if record.commands_rejected:
        for entry in record.commands_rejected:
            lines.append(f"- `{entry['command']}` — `{entry['code']}` — {entry['reason']}")
    else:
        lines.append("_(none)_")
    lines.append("")
    lines.append(f"## Policy rejections ({len(record.policy_rejections)})")
    lines.append("")
    if record.policy_rejections:
        for code in record.policy_rejections:
            lines.append(f"- `{code}`")
    else:
        lines.append("_(none)_")
    lines.append("")
    lines.append("## Execution boundary law")
    lines.append("")
    lines.append(
        "> The proposer may suggest work but possesses zero execution authority. "
        "All execution authority remains exclusively with admitted executor "
        "identities under runtime policy enforcement."
    )
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Self-check fixtures
# ---------------------------------------------------------------------------


_FIXTURE_BASE: dict[str, object] = {
    "work_order_id": "WO-FIX-PROPOSER-001",
    "status": "approved",
    "assigned_to": "canon_guardian-01",
    "objective": "Run the v0.1 documentation conformance gate.",
    "allowed_files": ["*.md", "workforce/**", "reports/**"],
    "forbidden_files": ["runtime/**", "vectors/**", "intellagent_runtime/**"],
    "required_gates": ["make no-pseudocode"],
}


def _emit_fixture_yaml(name: str, overrides: dict[str, object]) -> Path:
    fields: dict[str, object] = dict(_FIXTURE_BASE)
    fields.update(overrides)
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIXTURES_DIR / f"wo_fixture_{name}.yaml"
    lines: list[str] = []
    for key, value in fields.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - \"{item}\"")
        elif isinstance(value, str):
            lines.append(f"{key}: \"{value}\"")
        else:
            lines.append(f"{key}: {value}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


@dataclass
class FixtureResult:
    name: str
    passed: bool
    detail: str
    proposal_id: str
    deterministic_hash: str


def _check_fixture_1_forbidden() -> FixtureResult:
    name = "forbidden_command_proposal_refused"
    wo = _emit_fixture_yaml(name, {
        "work_order_id": "WO-FIX-PROPOSER-FORBIDDEN-001",
        "required_gates": ["curl https://example.com"],
    })
    record = propose(wo, "canon_guardian-01")
    ok = (
        "forbidden_pattern" in record.policy_rejections
        and any(c["command"] == "curl https://example.com" for c in record.commands_rejected)
        and "empty_proposal" in record.policy_rejections
        and record.exit_status == 1
    )
    detail = (
        f"policy_rejections={record.policy_rejections}, "
        f"exit_status={record.exit_status}"
    )
    return FixtureResult(name, ok, detail, record.proposal_id, record.deterministic_hash)


def _check_fixture_2_path_outside() -> FixtureResult:
    name = "proposal_outside_allowed_files_refused"
    wo = _emit_fixture_yaml(name, {
        "work_order_id": "WO-FIX-PROPOSER-PATHOUT-002",
        "allowed_files": ["*.md"],
        "required_gates": ["cat secrets/config.txt"],
    })
    record = propose(wo, "canon_guardian-01")
    ok = (
        "path_outside_allowed_files" in record.policy_rejections
        and any(c["command"] == "cat secrets/config.txt" for c in record.commands_rejected)
        and record.exit_status == 1
    )
    detail = (
        f"policy_rejections={record.policy_rejections}, "
        f"exit_status={record.exit_status}"
    )
    return FixtureResult(name, ok, detail, record.proposal_id, record.deterministic_hash)


def _check_fixture_3_recursive() -> FixtureResult:
    name = "recursive_self_modification_refused"
    wo = _emit_fixture_yaml(name, {
        "work_order_id": "WO-FIX-PROPOSER-SELFMOD-003",
        "allowed_files": ["**"],
        "required_gates": ["cat tools/proposer_runtime.py"],
    })
    record = propose(wo, "canon_guardian-01")
    ok = (
        "recursive_self_modification" in record.policy_rejections
        and any("tools/proposer_runtime.py" in c["command"] for c in record.commands_rejected)
        and record.exit_status == 1
    )
    detail = (
        f"policy_rejections={record.policy_rejections}, "
        f"exit_status={record.exit_status}"
    )
    return FixtureResult(name, ok, detail, record.proposal_id, record.deterministic_hash)


def _check_fixture_4_network() -> FixtureResult:
    name = "network_proposal_refused"
    wo = _emit_fixture_yaml(name, {
        "work_order_id": "WO-FIX-PROPOSER-NETWORK-004",
        "required_gates": ["wget https://example.com/payload"],
    })
    record = propose(wo, "canon_guardian-01")
    ok = (
        "network_proposal" in record.policy_rejections
        and "forbidden_pattern" in record.policy_rejections
        and any(c["command"].startswith("wget ") for c in record.commands_rejected)
        and record.exit_status == 1
    )
    detail = (
        f"policy_rejections={record.policy_rejections}, "
        f"exit_status={record.exit_status}"
    )
    return FixtureResult(name, ok, detail, record.proposal_id, record.deterministic_hash)


def _check_fixture_5_empty_rationale() -> FixtureResult:
    name = "empty_rationale_refused"
    wo = _emit_fixture_yaml(name, {
        "work_order_id": "WO-FIX-PROPOSER-NORATIONALE-005",
        "objective": "",
        "required_gates": ["make no-pseudocode"],
    })
    record = propose(wo, "canon_guardian-01")
    ok = (
        "empty_rationale" in record.policy_rejections
        and record.rationale == ""
        and record.exit_status == 1
    )
    detail = (
        f"policy_rejections={record.policy_rejections}, "
        f"rationale='{record.rationale}', "
        f"exit_status={record.exit_status}"
    )
    return FixtureResult(name, ok, detail, record.proposal_id, record.deterministic_hash)


def _check_fixture_6_cap() -> FixtureResult:
    name = "cap_truncates_to_three"
    wo = _emit_fixture_yaml(name, {
        "work_order_id": "WO-FIX-PROPOSER-CAP-006",
        "allowed_files": ["**"],
        "required_gates": ["pwd", "ls", "cat", "find", "make no-pseudocode"],
    })
    record = propose(wo, "canon_guardian-01")
    proposed_cmds = [c["command"] for c in record.commands_proposed]
    ok = (
        len(record.commands_proposed) == 3
        and proposed_cmds == sorted(proposed_cmds)
        and proposed_cmds == ["cat", "find", "ls"]
        and "cap_exceeded" in record.policy_rejections
        and record.exit_status == 0
    )
    detail = (
        f"proposed={proposed_cmds}, "
        f"policy_rejections={record.policy_rejections}, "
        f"exit_status={record.exit_status}"
    )
    return FixtureResult(name, ok, detail, record.proposal_id, record.deterministic_hash)


def _check_fixture_7_deterministic() -> FixtureResult:
    name = "deterministic_hash_stable"
    wo = _emit_fixture_yaml(name, {
        "work_order_id": "WO-FIX-PROPOSER-DETERM-007",
        "allowed_files": ["**"],
        "required_gates": ["pwd", "ls"],
    })
    first = propose(wo, "canon_guardian-01")
    second = propose(wo, "canon_guardian-01")
    ok = (
        first.deterministic_hash == second.deterministic_hash
        and first.timestamp != second.timestamp
        and first.proposal_id != second.proposal_id
        and first.exit_status == 0
        and second.exit_status == 0
    )
    detail = (
        f"first_hash={first.deterministic_hash}, "
        f"second_hash={second.deterministic_hash}, "
        f"timestamps_differ={first.timestamp != second.timestamp}"
    )
    return FixtureResult(name, ok, detail, first.proposal_id, first.deterministic_hash)


_FIXTURES: tuple = (
    _check_fixture_1_forbidden,
    _check_fixture_2_path_outside,
    _check_fixture_3_recursive,
    _check_fixture_4_network,
    _check_fixture_5_empty_rationale,
    _check_fixture_6_cap,
    _check_fixture_7_deterministic,
)


def self_check() -> int:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    results: list[FixtureResult] = [fn() for fn in _FIXTURES]
    all_ok = all(r.passed for r in results)

    summary = {
        "runtime": "proposer_runtime",
        "runtime_version": RUNTIME_VERSION,
        "timestamp": _now_iso_with_micros(),
        "all_passed": all_ok,
        "fixtures": [
            {
                "name": r.name,
                "passed": r.passed,
                "detail": r.detail,
                "proposal_id": r.proposal_id,
                "deterministic_hash": r.deterministic_hash,
            }
            for r in results
        ],
    }
    (REPORTS_DIR / f"proposer_runtime_{RUNTIME_VERSION}.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    md_lines: list[str] = []
    md_lines.append(f"# Proposer Runtime {RUNTIME_VERSION} self-check")
    md_lines.append("")
    md_lines.append(f"- timestamp: `{summary['timestamp']}`")
    md_lines.append(f"- all_passed: `{all_ok}`")
    md_lines.append("")
    md_lines.append("## Fixtures")
    md_lines.append("")
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        md_lines.append(f"- `{r.name}` — **{status}**")
        md_lines.append(f"  - proposal_id: `{r.proposal_id}`")
        md_lines.append(f"  - deterministic_hash: `{r.deterministic_hash}`")
        md_lines.append(f"  - detail: {r.detail}")
    md_lines.append("")
    md_lines.append("## Execution boundary law")
    md_lines.append("")
    md_lines.append(
        "> The proposer may suggest work but possesses zero execution authority. "
        "All execution authority remains exclusively with admitted executor "
        "identities under runtime policy enforcement."
    )
    md_lines.append("")
    (REPORTS_DIR / f"proposer_runtime_{RUNTIME_VERSION}.md").write_text(
        "\n".join(md_lines), encoding="utf-8",
    )

    print(f"PROPOSER-RUNTIME {RUNTIME_VERSION} self-check: {len(results)} fixtures")
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        print(f"  [{status}] {r.name}")
        if not r.passed:
            print(f"         detail: {r.detail}")
    print(f"all_passed={all_ok}")
    return 0 if all_ok else 1


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _cli_propose(args: argparse.Namespace) -> int:
    wo_path = Path(args.work_order).resolve()
    record = propose(wo_path, args.agent_id)
    print(f"PROPOSAL {record.proposal_id} exit_status={record.exit_status}")
    if record.commands_proposed:
        print(f"  commands_proposed: {len(record.commands_proposed)}")
        for entry in record.commands_proposed:
            print(f"    - {entry['command']}  (matches: {entry['allowed_command_match']})")
    if record.commands_rejected:
        print(f"  commands_rejected: {len(record.commands_rejected)}")
        for entry in record.commands_rejected:
            print(f"    - {entry['command']}  ({entry['code']}: {entry['reason']})")
    if record.policy_rejections:
        print(f"  policy_rejections: {record.policy_rejections}")
    print(f"  deterministic_hash: {record.deterministic_hash}")
    return record.exit_status


def _cli_self_check(_args: argparse.Namespace) -> int:
    return self_check()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="proposer_runtime",
        description="WiseOrder Proposer Runtime v0.1 — bounded candidate-command generation.",
    )
    sub = parser.add_subparsers(dest="verb", required=True)

    p_propose = sub.add_parser(
        "propose",
        help="emit a proposal record for an admitted work order",
    )
    p_propose.add_argument("--work-order", required=True, help="path to work order YAML")
    p_propose.add_argument("--agent-id", required=True, help="proposing identity")
    p_propose.set_defaults(func=_cli_propose)

    p_check = sub.add_parser(
        "self-check",
        help="run the seven self-check fixtures and refresh the runtime report",
    )
    p_check.set_defaults(func=_cli_self_check)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
