#!/usr/bin/env python3
"""WiseOrder/Intellagent — OS ISOLATION RUNTIME v0.1.

Kernel-backed containment for executor subprocesses on macOS via
``/usr/bin/sandbox-exec``. The classifier still runs first; the kernel
runs *also*.

Spec: OS-ISOLATION-RUNTIME-v0.1.md (top-level).
Companion: REAL-AGENT-RUNTIME-v0.2.md.

CLI:
  os_isolation_runtime.py self-check
      Run the nine self-check fixtures end-to-end and refresh
      reports/os_isolation_runtime/os_isolation_runtime_v0.1.{md,json}.
      Exit 0 iff all nine pass, 1 otherwise.

  os_isolation_runtime.py run-fixture
      Run the canonical valid fixture (`pwd` under isolation) and
      print the result dict for ad-hoc inspection.

Stdlib + the v0.2 runtime's already-tested classifier and fingerprint
helpers only. No networking, no daemon, no model.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from real_agent_runtime import (  # noqa: E402
    EXECUTE_OUTPUT_BYTE_CAP,
    EXECUTE_TIMEOUT_DEFAULT_S,
    EXECUTE_TIMEOUT_HARD_CAP_S,
    REPO_ROOT,
    classify_execute_command,
    repo_fingerprint,
)

REPORTS_DIR = REPO_ROOT / "reports" / "os_isolation_runtime"
PROFILES_DIR = REPORTS_DIR / "profiles"
RUNS_DIR = REPORTS_DIR / "runs"
RUNTIME_VERSION = "v0.1"
ISOLATION_MODE = "sandbox-exec"
SANDBOX_EXEC_BIN = "/usr/bin/sandbox-exec"

# macOS routes /bin/sh through /bin/bash; the kernel checks the resolved
# variant and refuses if /bin/bash is not on the per-run binary allowlist.
SHELL_VARIANT_GROUPS: dict[str, tuple[str, ...]] = {
    "/bin/sh": ("/bin/sh", "/bin/bash"),
    "/bin/bash": ("/bin/sh", "/bin/bash"),
}


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------


def _allowlist_binaries(binary: str) -> tuple[str, ...]:
    return SHELL_VARIANT_GROUPS.get(binary, (binary,))


def generate_profile(binary: str, sandbox_path: Path) -> str:
    """Return the deterministic sandbox-exec profile for the given inputs."""
    sandbox = str(Path(sandbox_path).resolve())
    binaries = sorted(set(_allowlist_binaries(binary)))
    binary_clauses = "\n".join(
        f'(allow process-exec (literal "{b}"))' for b in binaries
    )
    return (
        '(version 1)\n'
        '(deny default)\n'
        '(deny process-exec*)\n'
        f'{binary_clauses}\n'
        '(allow mach-lookup)\n'
        '(deny mach-lookup (global-name "com.apple.coreservices.launchservicesd"))\n'
        '(deny mach-lookup (global-name "com.apple.lsd.mapdb"))\n'
        '(deny mach-lookup (global-name "com.apple.lsd.modifydb"))\n'
        '(deny mach-lookup (global-name "com.apple.lsd.openurls"))\n'
        '(allow file-read*)\n'
        '(allow file-read-metadata)\n'
        '(deny file-write*)\n'
        f'(allow file-write* (subpath "{sandbox}"))\n'
        '(allow file-write-data (literal "/dev/null"))\n'
        '(allow file-write-data (literal "/dev/dtracehelper"))\n'
        '(allow sysctl-read)\n'
        '(allow ipc-posix-shm)\n'
        '(allow iokit-open)\n'
        '(allow signal (target self))\n'
        '(deny network*)\n'
    )


def generate_profile_multi(binaries: list[str], sandbox_path: Path) -> str:
    """Profile variant for callers that need a small set of binaries.

    Used by higher layers (e.g. RESOURCE-LIMIT-RUNTIME-v0.1.md fixtures
    that need shell + sleep + echo simultaneously). Variant-group
    expansion still applies. All other clauses are identical to
    ``generate_profile`` (single-binary form).
    """
    sandbox = str(Path(sandbox_path).resolve())
    expanded: set[str] = set()
    for b in binaries:
        expanded.update(_allowlist_binaries(b))
    binary_clauses = "\n".join(
        f'(allow process-exec (literal "{b}"))' for b in sorted(expanded)
    )
    return (
        '(version 1)\n'
        '(deny default)\n'
        '(deny process-exec*)\n'
        f'{binary_clauses}\n'
        '(allow mach-lookup)\n'
        '(deny mach-lookup (global-name "com.apple.coreservices.launchservicesd"))\n'
        '(deny mach-lookup (global-name "com.apple.lsd.mapdb"))\n'
        '(deny mach-lookup (global-name "com.apple.lsd.modifydb"))\n'
        '(deny mach-lookup (global-name "com.apple.lsd.openurls"))\n'
        '(allow file-read*)\n'
        '(allow file-read-metadata)\n'
        '(deny file-write*)\n'
        f'(allow file-write* (subpath "{sandbox}"))\n'
        '(allow file-write-data (literal "/dev/null"))\n'
        '(allow file-write-data (literal "/dev/dtracehelper"))\n'
        '(allow sysctl-read)\n'
        '(allow ipc-posix-shm)\n'
        '(allow iokit-open)\n'
        '(allow signal (target self))\n'
        '(deny network*)\n'
    )


def hash_profile(profile: str) -> str:
    return "sha256:" + hashlib.sha256(profile.encode("utf-8")).hexdigest()


def write_profile(profile: str) -> Path:
    """Write the profile to a content-keyed file. Idempotent."""
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    h = hash_profile(profile)
    short = h.split(":", 1)[1][:16]
    path = PROFILES_DIR / f"profile_{short}.sb"
    if not path.exists():
        path.write_text(profile, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Subprocess helpers
# ---------------------------------------------------------------------------


def _now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _minimal_env() -> dict[str, str]:
    return {
        "PATH": os.environ.get("PATH", ""),
        "LC_ALL": "C",
        "LANG": "C",
    }


def _truncate(data: bytes, cap: int) -> tuple[str, bool]:
    if len(data) <= cap:
        return data.decode("utf-8", errors="replace"), False
    return data[:cap].decode("utf-8", errors="replace"), True


def _resolve_argv(command: str) -> list[str]:
    argv = shlex.split(command)
    if not argv:
        return [command]
    head = argv[0]
    if head.startswith("/"):
        return argv
    if head in SHELL_VARIANT_GROUPS:
        return argv
    resolved = shutil.which(head)
    if resolved:
        argv[0] = resolved
    return argv


# ---------------------------------------------------------------------------
# Execute paths
# ---------------------------------------------------------------------------


def _run_under_sandbox(
    argv: list[str],
    sandbox_path: Path,
    profile: str,
    timeout: float,
) -> dict:
    profile_path = write_profile(profile)
    h = hash_profile(profile)
    sandbox_argv = [SANDBOX_EXEC_BIN, "-f", str(profile_path)] + argv
    started = time.monotonic()
    started_iso = _now_iso()
    bounded_timeout = min(max(timeout, 0.001), EXECUTE_TIMEOUT_HARD_CAP_S)
    result: dict = {
        "command": " ".join(shlex.quote(a) for a in argv),
        "argv": argv,
        "cwd": str(sandbox_path),
        "env_keys": sorted(_minimal_env().keys()),
        "timeout_s": bounded_timeout,
        "timestamp_start": started_iso,
        "status": "ok",
        "exit_code": None,
        "stdout": "",
        "stdout_truncated": False,
        "stderr": "",
        "stderr_truncated": False,
        "duration_ms": 0,
        "timed_out": False,
        "error": None,
        "isolation_mode": ISOLATION_MODE,
        "sandbox_profile_hash": h,
        "sandbox_profile_path": str(profile_path),
        "kernel_enforced": True,
        "denied_syscalls": [],
        "timestamp_end": "",
    }
    try:
        proc = subprocess.run(
            sandbox_argv,
            cwd=str(sandbox_path),
            env=_minimal_env(),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=bounded_timeout,
            shell=False,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        elapsed_ms = int((time.monotonic() - started) * 1000)
        out_data = exc.output if exc.output else b""
        err_data = exc.stderr if exc.stderr else b""
        out_text, out_trunc = _truncate(out_data, EXECUTE_OUTPUT_BYTE_CAP)
        err_text, err_trunc = _truncate(err_data, EXECUTE_OUTPUT_BYTE_CAP)
        result.update({
            "status": "timed_out",
            "stdout": out_text,
            "stdout_truncated": out_trunc,
            "stderr": err_text,
            "stderr_truncated": err_trunc,
            "duration_ms": elapsed_ms,
            "timed_out": True,
            "error": f"command exceeded {bounded_timeout}s wall-clock cap",
            "timestamp_end": _now_iso(),
        })
        return result
    except (FileNotFoundError, OSError) as exc:
        elapsed_ms = int((time.monotonic() - started) * 1000)
        result.update({
            "status": "error",
            "duration_ms": elapsed_ms,
            "error": f"{type(exc).__name__}: {exc}",
            "timestamp_end": _now_iso(),
        })
        return result

    elapsed_ms = int((time.monotonic() - started) * 1000)
    out_text, out_trunc = _truncate(proc.stdout or b"", EXECUTE_OUTPUT_BYTE_CAP)
    err_text, err_trunc = _truncate(proc.stderr or b"", EXECUTE_OUTPUT_BYTE_CAP)
    result.update({
        "status": "ok" if proc.returncode == 0 else "nonzero_exit",
        "exit_code": proc.returncode,
        "stdout": out_text,
        "stdout_truncated": out_trunc,
        "stderr": err_text,
        "stderr_truncated": err_trunc,
        "duration_ms": elapsed_ms,
        "timestamp_end": _now_iso(),
    })
    return result


def execute_isolated_raw(
    argv: list[str],
    sandbox_path: Path,
    timeout: float = EXECUTE_TIMEOUT_DEFAULT_S,
) -> dict:
    """Run argv via sandbox-exec WITHOUT classifier checks.

    Used by self-check fixtures that exercise kernel-only behavior. Production
    callers should use ``execute_command_isolated`` so the classifier remains
    the first line of defense.
    """
    binary = argv[0] if argv else ""
    profile = generate_profile(binary, sandbox_path)
    return _run_under_sandbox(argv, sandbox_path, profile, timeout)


def execute_command_isolated(
    command: str,
    sandbox_path: Path,
    timeout: float = EXECUTE_TIMEOUT_DEFAULT_S,
) -> dict:
    """Full-stack: classifier deny-first, then kernel-backed sandbox-exec.

    Commands rejected by the v0.1 / v0.2 classifier never reach
    sandbox-exec; the result dict records ``status="blocked_by_classifier"``
    and ``kernel_enforced=False``.
    """
    verdict = classify_execute_command(command)
    if not verdict.allowed:
        return {
            "command": command,
            "argv": [],
            "cwd": str(sandbox_path),
            "env_keys": sorted(_minimal_env().keys()),
            "timeout_s": timeout,
            "timestamp_start": _now_iso(),
            "status": "blocked_by_classifier",
            "exit_code": None,
            "stdout": "",
            "stdout_truncated": False,
            "stderr": "",
            "stderr_truncated": False,
            "duration_ms": 0,
            "timed_out": False,
            "error": verdict.reason,
            "isolation_mode": ISOLATION_MODE,
            "sandbox_profile_hash": "",
            "sandbox_profile_path": "",
            "kernel_enforced": False,
            "denied_syscalls": [],
            "timestamp_end": _now_iso(),
        }
    argv = _resolve_argv(command)
    binary = argv[0]
    profile = generate_profile(binary, sandbox_path)
    return _run_under_sandbox(argv, sandbox_path, profile, timeout)


# ---------------------------------------------------------------------------
# Per-run manifest writer
# ---------------------------------------------------------------------------


def _write_run_manifest(result: dict, fixture_name: str) -> Path:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    safe_ts = (
        result["timestamp_start"]
        .replace(":", "")
        .replace("-", "")
        .replace(".", "")
        .replace("Z", "")
    )
    run_id = f"run-{safe_ts}Z-{fixture_name}"
    record = dict(result)
    record["run_id"] = run_id
    record["runtime_version"] = RUNTIME_VERSION
    record["fixture_name"] = fixture_name
    path = RUNS_DIR / f"{run_id}.json"
    path.write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


# ---------------------------------------------------------------------------
# Self-check fixtures
# ---------------------------------------------------------------------------


@dataclass
class FixtureResult:
    name: str
    passed: bool
    detail: str
    run_manifest: str | None = None


def _make_sandbox(prefix: str) -> Path:
    return Path(tempfile.mkdtemp(prefix=f"osisol-{prefix}-"))


def _cleanup(path: Path) -> None:
    shutil.rmtree(path, ignore_errors=True)


def _check_1_pwd_succeeds() -> FixtureResult:
    name = "allowed_pwd_command_succeeds_inside_isolation"
    sandbox = _make_sandbox("pwd")
    try:
        result = execute_command_isolated("pwd", sandbox, timeout=10.0)
        ok = (
            result["status"] == "ok"
            and result["exit_code"] == 0
            and result["kernel_enforced"] is True
            and result["isolation_mode"] == ISOLATION_MODE
            and result["sandbox_profile_hash"].startswith("sha256:")
            and result["stdout"].strip() == str(sandbox.resolve())
        )
        manifest_path = _write_run_manifest(result, name)
    finally:
        _cleanup(sandbox)
    detail = (
        f"status={result['status']}, exit={result['exit_code']}, "
        f"kernel={result['kernel_enforced']}, hash={result['sandbox_profile_hash'][:24]}…"
    )
    return FixtureResult(name, ok, detail, str(manifest_path))


def _check_2_curl_blocked() -> FixtureResult:
    name = "forbidden_curl_blocked_before_spawn"
    sandbox = _make_sandbox("curl")
    try:
        result = execute_command_isolated(
            "curl https://example.com", sandbox, timeout=10.0,
        )
        ok = (
            result["status"] == "blocked_by_classifier"
            and result["exit_code"] is None
            and result["kernel_enforced"] is False
            and result["sandbox_profile_path"] == ""
            and result["sandbox_profile_hash"] == ""
        )
        manifest_path = _write_run_manifest(result, name)
    finally:
        _cleanup(sandbox)
    detail = (
        f"status={result['status']}, kernel={result['kernel_enforced']}, "
        f"reason={result['error']}"
    )
    return FixtureResult(name, ok, detail, str(manifest_path))


def _check_3_write_outside_denied() -> FixtureResult:
    name = "write_outside_sandbox_denied_by_kernel_policy"
    sandbox = _make_sandbox("writeout")
    target = Path(tempfile.gettempdir()) / f"_osisol_write_outside_{os.getpid()}_{int(time.time()*1000)}"
    try:
        result = execute_isolated_raw(
            ["/usr/bin/touch", str(target)],
            sandbox,
            timeout=10.0,
        )
        ok = (
            result["status"] in ("nonzero_exit", "error")
            and result["exit_code"] != 0
            and not target.exists()
            and result["kernel_enforced"] is True
        )
        manifest_path = _write_run_manifest(result, name)
    finally:
        try:
            target.unlink()
        except OSError:
            pass
        _cleanup(sandbox)
    detail = (
        f"status={result['status']}, exit={result['exit_code']}, "
        f"target_exists={target.exists()}, "
        f"stderr_head={result['stderr'].splitlines()[0] if result['stderr'] else ''}"
    )
    return FixtureResult(name, ok, detail, str(manifest_path))


def _check_4_open_calculator() -> FixtureResult:
    name = "open_calculator_app_denied"
    sandbox = _make_sandbox("open")
    try:
        result = execute_isolated_raw(
            ["/usr/bin/open", "-a", "Calculator"],
            sandbox,
            timeout=10.0,
        )
        # /usr/bin/open exits nonzero when LaunchServices mach-lookup is
        # denied (it cannot resolve the app and reports an error).
        ok = (
            result["status"] in ("nonzero_exit", "error")
            and result["exit_code"] != 0
            and result["kernel_enforced"] is True
        )
        manifest_path = _write_run_manifest(result, name)
    finally:
        _cleanup(sandbox)
    detail = (
        f"status={result['status']}, exit={result['exit_code']}, "
        f"stderr_head={(result['stderr'] or result['stdout']).splitlines()[0] if (result['stderr'] or result['stdout']) else ''}"
    )
    return FixtureResult(name, ok, detail, str(manifest_path))


def _check_5_nested_spawn_denied() -> FixtureResult:
    name = "nested_subprocess_spawn_denied"
    sandbox = _make_sandbox("nested")
    try:
        # Allow /bin/sh + /bin/bash via the variant group; do NOT allow
        # /bin/ls. The inner exec of /bin/ls must be denied by the kernel.
        result = execute_isolated_raw(
            ["/bin/sh", "-c", "/bin/ls /usr"],
            sandbox,
            timeout=10.0,
        )
        denied_marker = (
            "Operation not permitted" in (result["stderr"] or "")
            or "Operation not permitted" in (result["stdout"] or "")
        )
        ok = (
            result["kernel_enforced"] is True
            and (result["exit_code"] != 0 or denied_marker)
        )
        manifest_path = _write_run_manifest(result, name)
    finally:
        _cleanup(sandbox)
    detail = (
        f"status={result['status']}, exit={result['exit_code']}, "
        f"denied_marker={denied_marker}, "
        f"stderr_head={result['stderr'].splitlines()[0] if result['stderr'] else ''}"
    )
    return FixtureResult(name, ok, detail, str(manifest_path))


def _check_6_repo_fingerprint() -> FixtureResult:
    name = "repo_fingerprint_unchanged"
    sandbox = _make_sandbox("fp")
    try:
        before = repo_fingerprint(REPO_ROOT)
        result = execute_command_isolated("pwd", sandbox, timeout=10.0)
        after = repo_fingerprint(REPO_ROOT)
        ok = (
            result["status"] == "ok"
            and before == after
        )
        manifest_path = _write_run_manifest(result, name)
    finally:
        _cleanup(sandbox)
    detail = f"before==after: {before == after}, status={result['status']}"
    return FixtureResult(name, ok, detail, str(manifest_path))


def _check_7_timeout_enforced() -> FixtureResult:
    name = "timeout_still_enforced"
    sandbox = _make_sandbox("timeout")
    try:
        result = execute_isolated_raw(
            ["/bin/sleep", "5"],
            sandbox,
            timeout=0.5,
        )
        ok = (
            result["status"] == "timed_out"
            and result["timed_out"] is True
            and result["duration_ms"] >= 400
            and result["duration_ms"] < 5000
            and result["kernel_enforced"] is True
        )
        manifest_path = _write_run_manifest(result, name)
    finally:
        _cleanup(sandbox)
    detail = (
        f"status={result['status']}, timed_out={result['timed_out']}, "
        f"duration_ms={result['duration_ms']}"
    )
    return FixtureResult(name, ok, detail, str(manifest_path))


def _check_8_manifest_fields() -> FixtureResult:
    name = "manifest_isolation_fields_populated"
    sandbox = _make_sandbox("fields")
    try:
        result = execute_command_isolated("pwd", sandbox, timeout=10.0)
        profile_path = result.get("sandbox_profile_path", "")
        ok = (
            result.get("isolation_mode") == ISOLATION_MODE
            and isinstance(result.get("sandbox_profile_hash"), str)
            and result["sandbox_profile_hash"].startswith("sha256:")
            and isinstance(profile_path, str)
            and bool(profile_path)
            and Path(profile_path).exists()
            and result.get("kernel_enforced") is True
            and isinstance(result.get("denied_syscalls"), list)
        )
        manifest_path = _write_run_manifest(result, name)
    finally:
        _cleanup(sandbox)
    detail = (
        f"isolation_mode={result.get('isolation_mode')}, "
        f"hash_prefix={result.get('sandbox_profile_hash', '')[:24]}…, "
        f"path_exists={Path(result.get('sandbox_profile_path', '/nonexistent')).exists()}, "
        f"kernel={result.get('kernel_enforced')}"
    )
    return FixtureResult(name, ok, detail, str(manifest_path))


def _check_9_profile_hash_stable() -> FixtureResult:
    name = "sandbox_profile_hash_stable"
    sandbox = _make_sandbox("hash")
    try:
        p1 = generate_profile("/bin/pwd", sandbox)
        p2 = generate_profile("/bin/pwd", sandbox)
        h1 = hash_profile(p1)
        h2 = hash_profile(p2)
        ok = (
            h1 == h2
            and p1 == p2
            and h1.startswith("sha256:")
            and h1 != hash_profile(generate_profile("/bin/ls", sandbox))
        )
    finally:
        _cleanup(sandbox)
    detail = f"h1={h1[:24]}…, h2={h2[:24]}…, equal={h1 == h2}"
    return FixtureResult(name, ok, detail, None)


_FIXTURES: tuple = (
    _check_1_pwd_succeeds,
    _check_2_curl_blocked,
    _check_3_write_outside_denied,
    _check_4_open_calculator,
    _check_5_nested_spawn_denied,
    _check_6_repo_fingerprint,
    _check_7_timeout_enforced,
    _check_8_manifest_fields,
    _check_9_profile_hash_stable,
)


def self_check() -> int:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    results: list[FixtureResult] = [fn() for fn in _FIXTURES]
    all_ok = all(r.passed for r in results)

    summary = {
        "runtime": "os_isolation_runtime",
        "runtime_version": RUNTIME_VERSION,
        "isolation_mode": ISOLATION_MODE,
        "platform": "darwin",
        "sandbox_exec_bin": SANDBOX_EXEC_BIN,
        "timestamp": _now_iso(),
        "all_passed": all_ok,
        "fixtures": [
            {
                "name": r.name,
                "passed": r.passed,
                "detail": r.detail,
                "run_manifest": r.run_manifest,
            }
            for r in results
        ],
    }
    (REPORTS_DIR / f"os_isolation_runtime_{RUNTIME_VERSION}.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    md_lines: list[str] = []
    md_lines.append(f"# OS Isolation Runtime {RUNTIME_VERSION} self-check")
    md_lines.append("")
    md_lines.append(f"- timestamp: `{summary['timestamp']}`")
    md_lines.append(f"- isolation_mode: `{summary['isolation_mode']}`")
    md_lines.append(f"- sandbox-exec binary: `{SANDBOX_EXEC_BIN}`")
    md_lines.append(f"- all_passed: `{all_ok}`")
    md_lines.append("")
    md_lines.append("## Fixtures")
    md_lines.append("")
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        md_lines.append(f"- `{r.name}` — **{status}**")
        if r.run_manifest:
            md_lines.append(f"  - run_manifest: `{r.run_manifest}`")
        md_lines.append(f"  - detail: {r.detail}")
    md_lines.append("")
    md_lines.append("## Isolation boundary law")
    md_lines.append("")
    md_lines.append(
        "> The kernel enforces the sandbox; the runtime enforces the "
        "policy. Governance determines admissibility; kernel isolation "
        "constrains damage radius."
    )
    md_lines.append("")
    (REPORTS_DIR / f"os_isolation_runtime_{RUNTIME_VERSION}.md").write_text(
        "\n".join(md_lines), encoding="utf-8",
    )

    print(f"OS-ISOLATION-RUNTIME {RUNTIME_VERSION} self-check: {len(results)} fixtures")
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


def _cli_self_check(_args: argparse.Namespace) -> int:
    return self_check()


def _cli_run_fixture(_args: argparse.Namespace) -> int:
    sandbox = _make_sandbox("runfixture")
    try:
        result = execute_command_isolated("pwd", sandbox, timeout=10.0)
        manifest_path = _write_run_manifest(result, "run_fixture")
    finally:
        _cleanup(sandbox)
    print(f"OS-ISOLATION run-fixture status={result['status']} exit={result['exit_code']}")
    print(f"  isolation_mode:        {result['isolation_mode']}")
    print(f"  kernel_enforced:       {result['kernel_enforced']}")
    print(f"  sandbox_profile_hash:  {result['sandbox_profile_hash']}")
    print(f"  sandbox_profile_path:  {result['sandbox_profile_path']}")
    print(f"  manifest:              {manifest_path}")
    print(f"  stdout:                {result['stdout'].strip()}")
    return 0 if result["status"] == "ok" else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="os_isolation_runtime",
        description="WiseOrder OS Isolation Runtime v0.1 — kernel-backed containment.",
    )
    sub = parser.add_subparsers(dest="verb", required=True)

    p_check = sub.add_parser("self-check", help="run the nine self-check fixtures")
    p_check.set_defaults(func=_cli_self_check)

    p_fixture = sub.add_parser(
        "run-fixture",
        help="run the canonical valid fixture (`pwd`) under isolation",
    )
    p_fixture.set_defaults(func=_cli_run_fixture)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
