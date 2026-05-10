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

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
