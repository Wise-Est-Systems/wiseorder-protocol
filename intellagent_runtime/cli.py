"""`intellagent` command-line entry point.

Subcommands: init, state, propose, transition, audit, refuse.

Exit codes:
  0  OK or REFUSED (both are legitimate outputs; per INTELLAGENT-RUNTIME §14)
  1  user error / not-yet-initialized
  2  runtime in a bad state (CHAIN_CORRUPT, STATE_TAMPERED)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from intellagent_runtime import canonical
from intellagent_runtime.authorization import AuthorizationGate
from intellagent_runtime.kernel import WiseOrderKernel
from intellagent_runtime.memory import AuditMemory, ChainCorrupt
from intellagent_runtime.refusal import RefusalStore
from intellagent_runtime.runtime import apply_transition
from intellagent_runtime.state import StateStore, StateTampered
from intellagent_runtime.transitions import EpistemicTransition


PACKAGE_DIR = Path(__file__).resolve().parent
DEFAULT_POLICIES_DIR = PACKAGE_DIR / "policies"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _base_dir(args: argparse.Namespace) -> Path:
    return Path(getattr(args, "dir", None) or ".").resolve()


def _make_gate(args: argparse.Namespace) -> AuthorizationGate:
    return AuthorizationGate(
        policies_dir=Path(getattr(args, "policies_dir", None) or DEFAULT_POLICIES_DIR)
    )


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------


def cmd_init(args: argparse.Namespace) -> int:
    base = _base_dir(args)
    store = StateStore(base)
    refusals = RefusalStore(base / "intellagent_refusals")
    refusals.dir.mkdir(parents=True, exist_ok=True)
    AuditMemory(base / "intellagent_audit").dir.mkdir(parents=True, exist_ok=True)

    try:
        state = store.init(force=args.force)
    except FileExistsError:
        sys.stderr.write(
            "ERROR: runtime already initialized. Use --force to re-init.\n"
        )
        return 1

    print("Initialized:")
    print("  intellagent_state/      (working state)")
    print("  intellagent_audit/      (append-only audit memory)")
    print("  intellagent_refusals/   (refusal records)")
    print("  intellagent_objects/    (content-addressed object store)")
    print()
    print(f"State id: {state.state_id}")
    return 0


def cmd_state(args: argparse.Namespace) -> int:
    base = _base_dir(args)
    store = StateStore(base)
    try:
        state = store.load()
    except FileNotFoundError as exc:
        sys.stderr.write(f"ERROR: {exc}\n")
        return 1
    except StateTampered as exc:
        sys.stderr.write(f"STATE_TAMPERED: {exc}\n")
        return 2

    if args.json:
        print(json.dumps(state.to_dict(), sort_keys=True, indent=2))
    else:
        print(f"state_id:          {state.state_id}")
        print(f"objects:           {state.objects}")
        print(f"audit_head_sha256: {state.audit_head_sha256}")
        print(f"sealed_at:         {state.sealed_at}")
    return 0


def cmd_propose(args: argparse.Namespace) -> int:
    base = _base_dir(args)
    queue_dir = base / "intellagent_state" / "queue"
    if not queue_dir.exists():
        sys.stderr.write(
            "ERROR: runtime not initialized. Run `intellagent init` first.\n"
        )
        return 1

    if args.file:
        body = json.loads(Path(args.file).read_text(encoding="utf-8"))
    elif args.stdin:
        body = json.loads(sys.stdin.read())
    else:
        sys.stderr.write("ERROR: --file or --stdin is required.\n")
        return 1

    transition_id = body.get("transition_id")
    if not transition_id or not isinstance(transition_id, str):
        sys.stderr.write("ERROR: transition_id is required and must be a string.\n")
        return 1
    if "/" in transition_id or ".." in transition_id:
        sys.stderr.write("ERROR: transition_id must not contain '/' or '..'.\n")
        return 1

    queue_dir.mkdir(parents=True, exist_ok=True)
    path = queue_dir / f"{transition_id}.json"
    canonical.write_atomic(path, canonical.canonical_pretty(body))

    print(f"proposal_id: {transition_id}")
    print(f"regime:      {body.get('regime', '?')}")
    print(f"status:      QUEUED")
    return 0


def cmd_transition(args: argparse.Namespace) -> int:
    base = _base_dir(args)
    store = StateStore(base)
    audit = AuditMemory(base / "intellagent_audit")
    gate = _make_gate(args)
    kernel = WiseOrderKernel()

    queue_path = base / "intellagent_state" / "queue" / f"{args.proposal_id}.json"
    if not queue_path.is_file():
        sys.stderr.write(f"ERROR: proposal {args.proposal_id!r} not found in queue.\n")
        return 1

    try:
        audit.verify_chain()
    except ChainCorrupt as exc:
        sys.stderr.write(f"CHAIN_CORRUPT: {exc}\n")
        return 2

    try:
        state = store.load()
    except StateTampered as exc:
        sys.stderr.write(f"STATE_TAMPERED: {exc}\n")
        return 2

    body = json.loads(queue_path.read_text(encoding="utf-8"))
    tau = EpistemicTransition.from_dict(body)

    print(f"verifying:      {tau.transition_id}")
    print(f"regime:         {tau.regime}")

    verdict = kernel.verify(tau, state)
    if not verdict.passed:
        print("kernel:         FAILED")
        for f in verdict.failures:
            print(f"  ↳ {f}")
        print("result:         REJECTED (added to next refusal's challenge surface)")
        # Drop the proposal from the queue; per spec, the rejection is captured
        # the next time `intellagent refuse` is called.
        queue_path.unlink()
        return 0
    print(f"kernel:         PASSED ({len(verdict.failures)} failures)")

    if tau.is_action_bearing:
        decision = gate.evaluate(tau, state)
        if not decision.authorized:
            print("authorization:  DENIED")
            print(f"  ↳ {decision.rationale}")
            print("result:         REJECTED (added to next refusal's challenge surface)")
            queue_path.unlink()
            return 0
        print(f"authorization:  AUTHORIZED ({decision.authorization_source})")
    else:
        print("authorization:  NOT_APPLICABLE (transition is not action-bearing)")

    new_state, entry = apply_transition(tau, state, store, audit)
    queue_path.unlink()

    print("result:         LEGITIMATE")
    print(f"committed:      audit entry {entry.index:04d}")
    print(f"new state id:   {new_state.state_id}")
    return 0


def cmd_audit(args: argparse.Namespace) -> int:
    base = _base_dir(args)
    audit = AuditMemory(base / "intellagent_audit")

    if args.verify:
        try:
            audit.verify_chain()
        except ChainCorrupt as exc:
            sys.stderr.write(f"CHAIN_CORRUPT: {exc}\n")
            return 2
        sys.stderr.write("CHAIN OK\n")

    entries = audit.list_entries()
    if args.range:
        try:
            from_idx_str, to_idx_str = args.range.split(":")
            entries = entries[int(from_idx_str): int(to_idx_str)]
        except ValueError:
            sys.stderr.write("ERROR: --range must be FROM:TO with integers.\n")
            return 1

    if args.json or not entries:
        print(json.dumps([e.to_dict() for e in entries], sort_keys=True, indent=2))
    else:
        for e in entries:
            print(
                f"index={e.index:04d} regime={e.transition.get('regime', '?')} "
                f"prior={e.prior_state_id[:18]}... → {e.resulting_state_id[:18]}... "
                f"this={e.this_entry_sha256[:18]}..."
            )
    return 0


def cmd_refuse(args: argparse.Namespace) -> int:
    base = _base_dir(args)
    store = StateStore(base)
    refusals = RefusalStore(base / "intellagent_refusals")
    try:
        state = store.load()
    except FileNotFoundError as exc:
        sys.stderr.write(f"ERROR: {exc}\n")
        return 1
    except StateTampered as exc:
        sys.stderr.write(f"STATE_TAMPERED: {exc}\n")
        return 2

    refusal = refusals.seal(
        query=args.query,
        from_state_id=state.state_id,
        rejected=[(None, ["operator_initiated_refusal"])],
    )
    print(f"refusal_id:                {refusal.refusal_id}")
    print(f"candidates_rejected:       {len(refusal.candidates_rejected)}")
    print(f"challenge_surface_sha256:  {refusal.challenge_surface_sha256}")
    print(f"refused_at:                {refusal.refused_at}")
    print(f"sealed_to:                 intellagent_refusals/{refusal.refusal_id}.json")
    return 0


# ---------------------------------------------------------------------------
# governed-run
# ---------------------------------------------------------------------------


def _governed_run_self_check() -> int:
    """In-memory governance-flow exercise. Builds, validates, audits, and
    reports on a synthetic valid work order plus a synthetic refused one
    — all without touching the filesystem outside a temp directory."""
    import tempfile

    from intellagent_runtime.audit_memory import (
        AUDIT_CHAIN_VALID,
        append_event,
        verify_chain,
    )
    from intellagent_runtime.execution_plan import build_plan
    from intellagent_runtime.work_order_parser import parse_work_order

    valid_wo = """# WORK ORDER X
## Objective
governed-run self-check
## Required Commands
```bash
make ci
```
## Workflow
- inspect
- propose
- review
- execute
- verify
- report
- stop
Stop.
"""
    refused_wo = """# WORK ORDER X
## Objective
governed-run refusal self-check
## Required Commands
```bash
rm -rf /
```
## Workflow
- inspect
- propose
- review
- execute
- verify
- report
- stop
Stop.
"""

    with tempfile.TemporaryDirectory() as tmpd:
        audit_path = Path(tmpd) / "selfcheck.jsonl"
        # Valid path.
        wo = parse_work_order(valid_wo)
        plan = build_plan(wo)
        append_event(audit_path, "governed_run.started", {"sha256": wo.source_sha256})
        if not plan.is_valid():
            print(f"FAIL: valid WO did not validate: {plan.validate()}")
            return 1
        append_event(audit_path, "governed_run.plan_valid", {})
        # Refused path.
        wo2 = parse_work_order(refused_wo)
        plan2 = build_plan(wo2)
        append_event(audit_path, "governed_run.started", {"sha256": wo2.source_sha256})
        if plan2.is_valid():
            print("FAIL: refused WO was not refused")
            return 1
        append_event(
            audit_path,
            "governed_run.refused",
            {"reasons": plan2.validate()},
        )
        # Chain still valid.
        status = verify_chain(audit_path)
        if status.status != AUDIT_CHAIN_VALID:
            print(f"FAIL: audit chain {status.status} reason={status.reason}")
            return 1

    print("PASS: governed-run self-check")
    return 0


def cmd_governed_run(args: argparse.Namespace) -> int:
    """``governed-run`` subcommand.

    Modes:
      --dry-run     (default)  parse → plan → validate → audit → emit manifest
      --execute                wet-run: same, then run each planned command
                               under tools/os_isolation_runtime sandbox-exec
                               isolation; refuse safely on any failed gate

    Final statuses:
      GOVERNED_RUN_VALID              dry-run; plan valid; no execution
      GOVERNED_RUN_REFUSED            dry-run OR --execute; plan refused
                                       (no commands run); RefusalRecord sealed
      GOVERNED_RUN_INVALID            work order itself malformed
      GOVERNED_RUN_EXECUTED           --execute; every command completed cleanly
      GOVERNED_RUN_EXECUTION_FAILED   --execute; one or more commands failed
                                       or were blocked at the sandbox classifier

    Exit codes: VALID=0, EXECUTED=0, REFUSED=1, EXECUTION_FAILED=1, INVALID=2.
    """
    if getattr(args, "self_check", False):
        return _governed_run_self_check()

    from intellagent_runtime.audit_memory import (
        append_event,
        verify_chain,
    )
    from intellagent_runtime.execution_plan import build_plan, ExecutionPlanError
    from intellagent_runtime.work_order_parser import (
        WorkOrderError,
        parse_work_order_file,
    )

    # ---- mode resolution ----
    dry_run = bool(getattr(args, "dry_run", False))
    execute = bool(getattr(args, "execute", False))
    if dry_run and execute:
        sys.stderr.write("ERROR: --dry-run and --execute are mutually exclusive\n")
        return 1
    if not dry_run and not execute:
        dry_run = True
    mode = "execute" if execute else "dry-run"

    wo_path = getattr(args, "work_order", None)
    if not wo_path:
        sys.stderr.write("ERROR: governed-run requires --work-order or --self-check\n")
        return 1

    audit_path = Path(args.audit) if getattr(args, "audit", None) else None
    output_path = Path(args.output) if getattr(args, "output", None) else None

    refusals_dir = Path(getattr(args, "dir", None) or ".").resolve() / "intellagent_refusals"

    # ---- parse ----
    try:
        wo = parse_work_order_file(wo_path)
    except (WorkOrderError, FileNotFoundError) as exc:
        refusal_record_hash = _seal_refusal_if_requested(
            refusals_dir=refusals_dir,
            query=f"invalid work order: {wo_path}",
            reasons=[str(exc)],
        )
        manifest = _governed_run_manifest(
            mode=mode,
            work_order_hash=None,
            plan=None,
            validation=[str(exc)],
            audit_status=None,
            final_status="GOVERNED_RUN_INVALID",
            refusal_record_hash=refusal_record_hash,
        )
        _emit_manifest(manifest, output_path)
        return 2

    # ---- plan ----
    try:
        plan = build_plan(wo)
    except ExecutionPlanError as exc:
        refusal_record_hash = _seal_refusal_if_requested(
            refusals_dir=refusals_dir,
            query=f"invalid execution plan from {wo_path}",
            reasons=[str(exc)],
        )
        manifest = _governed_run_manifest(
            mode=mode,
            work_order_hash=wo.source_sha256,
            plan=None,
            validation=[str(exc)],
            audit_status=None,
            final_status="GOVERNED_RUN_INVALID",
            refusal_record_hash=refusal_record_hash,
        )
        _emit_manifest(manifest, output_path)
        return 2

    execution_plan_hash = "sha256:" + canonical.sha256_hex(
        canonical.canonical_json_bytes(plan.to_dict())
    ).split(":", 1)[-1]
    # canonical.sha256_hex already prefixes; canonicalize on its output by
    # dropping the leading "sha256:" before re-prefixing — keeps a single
    # source of truth for the format.
    # (sha256_hex returns "sha256:<hex>"; the split above is defensive.)

    # ---- validate ----
    violations = plan.validate()

    # ---- audit: started + plan_valid/refused ----
    audit_status: dict[str, Any] | None = None
    if audit_path is not None:
        append_event(
            audit_path,
            "governed_run.started",
            {
                "mode": mode,
                "work_order_sha256": wo.source_sha256,
                "execution_plan_hash": execution_plan_hash,
                "title": wo.title,
            },
        )
        if not violations:
            append_event(audit_path, "governed_run.plan_valid", {
                "stages": [s.value for s in plan.workflow.stages],
                "command_count": len(plan.planned_commands),
            })
        else:
            append_event(audit_path, "governed_run.refused", {
                "reasons": violations,
            })
        audit_status = verify_chain(audit_path).to_dict()

    # ---- refusal path (no execution allowed) ----
    if violations:
        refusal_record_hash = _seal_refusal_if_requested(
            refusals_dir=refusals_dir,
            query=f"governed-run refused: {wo.title or wo_path}",
            reasons=violations,
        )
        manifest = _governed_run_manifest(
            mode=mode,
            work_order_hash=wo.source_sha256,
            plan=plan,
            validation=violations,
            audit_status=audit_status,
            final_status="GOVERNED_RUN_REFUSED",
            execution_plan_hash=execution_plan_hash,
            refusal_record_hash=refusal_record_hash,
        )
        _emit_manifest(manifest, output_path)
        return 1

    # ---- dry-run terminal ----
    if dry_run:
        manifest = _governed_run_manifest(
            mode=mode,
            work_order_hash=wo.source_sha256,
            plan=plan,
            validation=[],
            audit_status=audit_status,
            final_status="GOVERNED_RUN_VALID",
            execution_plan_hash=execution_plan_hash,
        )
        _emit_manifest(manifest, output_path)
        return 0

    # ---- wet-run: execute under sandbox isolation ----
    proposer_hash, review_hash, executor_manifest_hash, pipeline_hash, command_results, \
        execution_status = _execute_planned_commands(
            plan=plan,
            audit_path=audit_path,
        )
    if audit_path is not None:
        audit_status = verify_chain(audit_path).to_dict()

    final_status = (
        "GOVERNED_RUN_EXECUTED"
        if execution_status == "OK"
        else "GOVERNED_RUN_EXECUTION_FAILED"
    )
    refusal_record_hash = None
    if final_status == "GOVERNED_RUN_EXECUTION_FAILED":
        refusal_record_hash = _seal_refusal_if_requested(
            refusals_dir=refusals_dir,
            query=f"governed-run execution failed: {wo.title or wo_path}",
            reasons=[
                f"{r['command']}: status={r['status']} exit={r['exit_code']} error={r.get('error') or ''}"
                for r in command_results if not r.get("succeeded")
            ],
        )

    manifest = _governed_run_manifest(
        mode=mode,
        work_order_hash=wo.source_sha256,
        plan=plan,
        validation=[],
        audit_status=audit_status,
        final_status=final_status,
        execution_plan_hash=execution_plan_hash,
        proposer_hash=proposer_hash,
        review_hash=review_hash,
        executor_manifest_hash=executor_manifest_hash,
        pipeline_hash=pipeline_hash,
        command_results=command_results,
        refusal_record_hash=refusal_record_hash,
    )
    _emit_manifest(manifest, output_path)
    return 0 if final_status == "GOVERNED_RUN_EXECUTED" else 1


def _emit_manifest(manifest: dict, output_path: Path | None) -> None:
    """Print the manifest to stdout and, if requested, also to ``output_path``."""
    text = canonical.canonical_pretty(manifest)
    print(text, end="")
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text, encoding="utf-8")


def _seal_refusal_if_requested(
    *,
    refusals_dir: Path,
    query: str,
    reasons: list,
    manifest: dict | None = None,
) -> str | None:
    """Seal a RefusalRecord using the existing intellagent_runtime.refusal
    store. Returns the hash of the canonicalized record (or None if sealing
    failed — which itself is recorded but does not abort)."""
    try:
        store = RefusalStore(refusals_dir)
        rejected = [(None, [str(r) for r in reasons if r])]
        record = store.seal(
            query=query,
            from_state_id="governed_run::no_state",
            rejected=rejected,
        )
        return "sha256:" + canonical.sha256_hex(
            canonical.canonical_json_bytes(record.to_dict())
        ).split(":", 1)[-1]
    except Exception as exc:  # pragma: no cover - defensive
        sys.stderr.write(f"WARN: refusal sealing failed: {exc}\n")
        return None


def _execute_planned_commands(
    *,
    plan,
    audit_path: Path | None,
) -> tuple[str, str, str, str, list[dict], str]:
    """Run each planned command under tools/os_isolation_runtime sandbox.

    Returns ``(proposer_hash, review_hash, executor_manifest_hash,
    pipeline_hash, command_results, execution_status)`` where
    ``execution_status`` is ``"OK"`` if every command succeeded and
    ``"FAILED"`` otherwise.

    Integration note: tools/pipeline_runtime.py operates on the Workforce
    YAML schema and is not used here. Instead we call the lower-level
    isolation primitive directly. The proposer/review/executor hashes are
    derived from our own data so the manifest is comparable in shape to
    a pipeline_runtime manifest. See
    reports/runtime_core/governed_run_pipeline_v0.1.md §integration-decision.
    """
    from intellagent_runtime.audit_memory import append_event
    # Lazy import: the isolation runtime lives under tools/ and depends on
    # the Python path. Importing it at module top would couple package
    # import to the workspace layout. We add tools/ to sys.path and import
    # by name so the module registers in sys.modules — required for the
    # @dataclass decorators inside the module to introspect their own
    # __module__ during class construction.
    import importlib
    repo_root = Path(__file__).resolve().parent.parent
    tools_dir = str(repo_root / "tools")
    if tools_dir not in sys.path:
        sys.path.insert(0, tools_dir)
    iso = importlib.import_module("os_isolation_runtime")

    import tempfile

    proposer_payload = {
        "planned_commands": [c.raw for c in plan.planned_commands],
        "work_order_hash": plan.work_order_sha256,
    }
    proposer_hash = "sha256:" + canonical.sha256_hex(
        canonical.canonical_json_bytes(proposer_payload)
    ).split(":", 1)[-1]

    review_payload = {
        "approved_commands": [c.raw for c in plan.planned_commands],
        "validation_status": "VALID",
    }
    review_hash = "sha256:" + canonical.sha256_hex(
        canonical.canonical_json_bytes(review_payload)
    ).split(":", 1)[-1]

    command_results: list[dict] = []
    execution_status = "OK"
    with tempfile.TemporaryDirectory(prefix="governed-run-") as tmpd:
        sandbox = Path(tmpd)
        for cmd in plan.planned_commands:
            result = iso.execute_command_isolated(cmd.raw, sandbox)
            status = result.get("status", "unknown")
            exit_code = result.get("exit_code")
            # Success criterion: the sandbox ran the command (status=="ok")
            # AND the command itself exited 0. Any other combination is a
            # failure for the whole run.
            command_succeeded = status == "ok" and exit_code == 0
            command_results.append({
                "command": cmd.raw,
                "status": status,
                "exit_code": exit_code,
                "succeeded": command_succeeded,
                "timed_out": result.get("timed_out", False),
                "duration_ms": result.get("duration_ms", 0),
                "stdout_truncated": result.get("stdout_truncated", False),
                "stderr_truncated": result.get("stderr_truncated", False),
                "sandbox_profile_hash": result.get("sandbox_profile_hash", ""),
                "error": result.get("error", ""),
            })
            event_payload = {
                "command": cmd.raw,
                "status": status,
                "exit_code": exit_code,
                "succeeded": command_succeeded,
            }
            if audit_path is not None:
                append_event(audit_path, "governed_run.command.executed", event_payload)
            if not command_succeeded:
                execution_status = "FAILED"

    executor_manifest_hash = "sha256:" + canonical.sha256_hex(
        canonical.canonical_json_bytes(command_results)
    ).split(":", 1)[-1]
    pipeline_payload = {
        "proposer_hash": proposer_hash,
        "review_hash": review_hash,
        "executor_manifest_hash": executor_manifest_hash,
    }
    pipeline_hash = "sha256:" + canonical.sha256_hex(
        canonical.canonical_json_bytes(pipeline_payload)
    ).split(":", 1)[-1]

    if audit_path is not None:
        append_event(audit_path, "governed_run.completed", {
            "execution_status": execution_status,
            "pipeline_hash": pipeline_hash,
        })
    return (
        proposer_hash, review_hash, executor_manifest_hash,
        pipeline_hash, command_results, execution_status,
    )


def _governed_run_manifest(
    *,
    mode: str,
    work_order_hash: str | None,
    plan,  # ExecutionPlan or None
    validation: list[str],
    audit_status: dict | None,
    final_status: str,
    execution_plan_hash: str | None = None,
    proposer_hash: str | None = None,
    review_hash: str | None = None,
    executor_manifest_hash: str | None = None,
    pipeline_hash: str | None = None,
    command_results: list[dict] | None = None,
    refusal_record_hash: str | None = None,
) -> dict:
    if plan is not None:
        parsed_stages = [s.value for s in plan.workflow.stages]
        protected_paths = list(plan.protected_paths)
        allowed_paths = list(plan.allowed_paths)
        forbidden_paths = list(plan.forbidden_paths)
        required_commands = list(plan.required_commands)
    else:
        parsed_stages = []
        protected_paths = []
        allowed_paths = []
        forbidden_paths = []
        required_commands = []

    validation_status = "VALID" if not validation else "REFUSED"
    manifest = {
        "mode": mode,
        "work_order_hash": work_order_hash,
        "execution_plan_hash": execution_plan_hash,
        "parsed_stages": parsed_stages,
        "protected_paths": protected_paths,
        "allowed_paths": allowed_paths,
        "forbidden_paths": forbidden_paths,
        "required_commands": required_commands,
        "validation_status": validation_status,
        "validation_violations": validation,
        "audit_status": audit_status,
        "final_status": final_status,
    }
    if mode == "execute":
        manifest["proposer_hash"] = proposer_hash
        manifest["review_hash"] = review_hash
        manifest["executor_manifest_hash"] = executor_manifest_hash
        manifest["pipeline_hash"] = pipeline_hash
        manifest["command_results"] = command_results or []
        manifest["refusal_record_hash"] = refusal_record_hash
    elif refusal_record_hash is not None:
        manifest["refusal_record_hash"] = refusal_record_hash

    manifest["manifest_hash"] = "sha256:" + canonical.sha256_hex(
        canonical.canonical_json_bytes({k: v for k, v in manifest.items() if k != "manifest_hash"})
    ).split(":", 1)[-1]
    return manifest


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="intellagent",
        description="Intellagent Runtime v0.1 — legitimate transition search engine.",
    )
    parser.add_argument(
        "--dir",
        type=str,
        default=None,
        help="runtime working directory (default: cwd)",
    )
    parser.add_argument(
        "--policies-dir",
        type=str,
        default=None,
        help="authorization policies directory (default: package's policies/)",
    )

    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="initialize an empty runtime")
    p_init.add_argument("--force", action="store_true", help="re-init even if state exists")
    p_init.set_defaults(func=cmd_init)

    p_state = sub.add_parser("state", help="print the current state")
    p_state.add_argument("--json", action="store_true", help="machine-readable JSON output")
    p_state.set_defaults(func=cmd_state)

    p_propose = sub.add_parser("propose", help="queue a proposed transition")
    p_propose.add_argument("--file", type=str, default=None, help="path to a transition JSON")
    p_propose.add_argument("--stdin", action="store_true", help="read transition JSON from stdin")
    p_propose.set_defaults(func=cmd_propose)

    p_transition = sub.add_parser("transition", help="verify and commit a queued proposal")
    p_transition.add_argument("proposal_id", help="proposal id (= transition id)")
    p_transition.set_defaults(func=cmd_transition)

    p_audit = sub.add_parser("audit", help="list audit memory entries")
    p_audit.add_argument("--range", type=str, default=None, help="entry range FROM:TO")
    p_audit.add_argument("--json", action="store_true", help="machine-readable JSON output")
    p_audit.add_argument("--verify", action="store_true", help="recompute chain integrity")
    p_audit.set_defaults(func=cmd_audit)

    p_refuse = sub.add_parser("refuse", help="seal an operator-initiated refusal")
    p_refuse.add_argument("--query", required=True, help="text describing the unanswered query")
    p_refuse.set_defaults(func=cmd_refuse)

    p_governed_run = sub.add_parser(
        "governed-run",
        help="parse a work order, build a plan, validate, and (optionally) execute",
    )
    p_governed_run.add_argument(
        "--work-order",
        required=False,
        help="path to a markdown work order; required unless --self-check",
    )
    p_governed_run.add_argument(
        "--audit",
        required=False,
        help="path to an append-only JSONL audit log",
    )
    p_governed_run.add_argument(
        "--dry-run",
        action="store_true",
        help="parse + plan + validate + audit-append; do not execute commands",
    )
    p_governed_run.add_argument(
        "--execute",
        action="store_true",
        help="wet-run: run each planned command under sandbox isolation; "
             "mutually exclusive with --dry-run",
    )
    p_governed_run.add_argument(
        "--output",
        required=False,
        help="path to write the manifest JSON (in addition to stdout)",
    )
    p_governed_run.add_argument(
        "--self-check",
        action="store_true",
        help="run an in-memory governance-flow self-check and exit",
    )
    p_governed_run.add_argument(
        "--verify-over-existing-artifact",
        action="store_true",
        help="allow verify before execute when verifying a pre-existing artifact",
    )
    p_governed_run.set_defaults(func=cmd_governed_run)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
