#!/usr/bin/env python3
"""WiseOrder/Intellagent — RESOURCE LIMIT RUNTIME v0.1.

Hard-bounded resource enforcement for isolated executor runs.

Builds on:
  - REAL-AGENT-RUNTIME-v0.2.md  (deny-first command classifier)
  - OS-ISOLATION-RUNTIME-v0.1.md (kernel sandbox-exec profile)

Adds:
  - resource.setrlimit() of CPU, AS, NOFILE, NPROC in preexec_fn
  - os.setsid() + os.killpg(SIGKILL) for whole-process-tree termination
  - deterministic stdout/stderr byte caps with sha256 of truncated bytes
  - post-execution sandbox-disk walk for size violations
  - getrusage(RUSAGE_CHILDREN).ru_maxrss for post-hoc memory overrun
    detection on macOS where RLIMIT_AS is unprivileged-unenforceable
  - pre-execution batch-length cap

Spec: RESOURCE-LIMIT-RUNTIME-v0.1.md.

Stdlib only. No networking. No daemon. No model.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import platform
import resource
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from real_agent_runtime import (  # noqa: E402
    REPO_ROOT,
    classify_execute_command,
    repo_fingerprint,
)
from os_isolation_runtime import (  # noqa: E402
    SANDBOX_EXEC_BIN,
    generate_profile,
    generate_profile_multi,
    hash_profile,
    write_profile,
)

REPORTS_DIR = REPO_ROOT / "reports" / "resource_limit_runtime"
RUNS_DIR = REPORTS_DIR / "runs"
RUNTIME_VERSION = "v0.1"
ISOLATION_MODE = "sandbox-exec+rlimits"


def _detect_python_chain() -> tuple[str, ...]:
    """Return every binary the parent's Python interpreter posix_spawns.

    The macOS stub at ``/usr/bin/python3`` delegates to xcodebuild and
    fails inside the kernel sandbox. The Homebrew Framework layout
    chains a small bin/python wrapper into a
    ``Resources/Python.app/Contents/MacOS/Python`` helper. The kernel
    profile must allow the entire chain.
    """
    real = os.path.realpath(sys.executable)
    candidates: list[str] = [real]
    framework_helper = (
        Path(real).parent.parent / "Resources" / "Python.app" / "Contents" / "MacOS" / "Python"
    )
    if framework_helper.exists():
        candidates.append(str(framework_helper))
    return tuple(dict.fromkeys(candidates))


PYTHON_BINARIES: tuple[str, ...] = _detect_python_chain()
PYTHON_REAL: str = PYTHON_BINARIES[0]

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ResourceLimits:
    cpu_limit_seconds: int = 10
    memory_limit_bytes: int = 512 * 1024 * 1024
    fd_limit: int = 64
    process_limit: int = 100
    stdout_limit_bytes: int = 64 * 1024
    stderr_limit_bytes: int = 64 * 1024
    sandbox_size_limit_bytes: int = 50 * 1024 * 1024
    command_count_limit: int = 3
    wall_clock_timeout_seconds: float = 60.0


DEFAULT_LIMITS = ResourceLimits()

# Extra binaries that the resource-limit fixtures need to invoke under the
# kernel sandbox (shell + sleep + echo + python3). Not used for the v0.1
# pipeline runtime; only for self-check fixtures that must demonstrate
# fork-bombs, fd exhaustion, etc.
DEFAULT_FIXTURE_BINARIES: tuple[str, ...] = (
    "/bin/pwd",
    "/bin/ls",
    "/bin/cat",
    "/bin/echo",
    "/bin/sleep",
    "/bin/sh",
    "/bin/bash",
    "/usr/bin/python3",
    "/usr/bin/touch",
    "/usr/bin/true",
    "/usr/bin/false",
)


# ---------------------------------------------------------------------------
# preexec helpers
# ---------------------------------------------------------------------------


def _make_preexec(limits: ResourceLimits, applied_path: Path) -> "callable":
    """Build a preexec_fn that records which setrlimit calls succeeded.

    Each setrlimit is wrapped in try/except so a kernel that rejects a
    given limit (e.g. macOS unprivileged RLIMIT_AS) does not abort the
    whole spawn. The applied_path file collects per-rlimit success
    booleans so the parent can read them post-spawn.
    """
    cpu = int(limits.cpu_limit_seconds)
    mem = int(limits.memory_limit_bytes)
    nofile = int(limits.fd_limit)
    nproc = int(limits.process_limit)
    target = str(applied_path)

    def _preexec() -> None:
        os.setsid()
        applied: dict[str, bool] = {
            "cpu": False, "memory": False, "fd": False, "nproc": False,
        }
        try:
            resource.setrlimit(resource.RLIMIT_CPU, (cpu, cpu))
            applied["cpu"] = True
        except (ValueError, OSError, resource.error):
            pass
        try:
            resource.setrlimit(resource.RLIMIT_AS, (mem, mem))
            applied["memory"] = True
        except (ValueError, OSError, resource.error):
            pass
        try:
            resource.setrlimit(resource.RLIMIT_NOFILE, (nofile, nofile))
            applied["fd"] = True
        except (ValueError, OSError, resource.error):
            pass
        try:
            resource.setrlimit(resource.RLIMIT_NPROC, (nproc, nproc))
            applied["nproc"] = True
        except (ValueError, OSError, resource.error):
            pass
        try:
            fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
            payload = f'{int(applied["cpu"])}{int(applied["memory"])}{int(applied["fd"])}{int(applied["nproc"])}'
            os.write(fd, payload.encode("ascii"))
            os.close(fd)
        except OSError:
            pass

    return _preexec


def _read_applied(applied_path: Path) -> dict[str, bool]:
    try:
        data = applied_path.read_text(encoding="ascii").strip()
    except OSError:
        return {"cpu": False, "memory": False, "fd": False, "nproc": False}
    while len(data) < 4:
        data = data + "0"
    return {
        "cpu": data[0] == "1",
        "memory": data[1] == "1",
        "fd": data[2] == "1",
        "nproc": data[3] == "1",
    }


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


def _truncate_bytes(data: bytes, cap: int) -> tuple[bytes, bool]:
    if len(data) <= cap:
        return data, False
    return data[:cap], True


def _sha256_hex(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _measure_sandbox_size(sandbox: Path) -> int:
    total = 0
    for root, _dirs, files in os.walk(sandbox):
        for name in files:
            try:
                total += (Path(root) / name).stat().st_size
            except OSError:
                pass
    return total


def _resolve_argv(command: str) -> list[str]:
    argv = shlex.split(command)
    if not argv:
        return [command]
    head = argv[0]
    if head.startswith("/") or head in ("/bin/sh", "/bin/bash"):
        return argv
    resolved = shutil.which(head)
    if resolved:
        argv[0] = resolved
    return argv


def _killpg_safe(pgid: int, sig: int) -> None:
    try:
        os.killpg(pgid, sig)
    except (ProcessLookupError, PermissionError, OSError):
        pass


# ---------------------------------------------------------------------------
# Core run
# ---------------------------------------------------------------------------


def _run_with_limits(
    argv: list[str],
    sandbox: Path,
    profile_path: Path,
    profile_hash_value: str,
    limits: ResourceLimits,
) -> dict:
    """Run one argv under sandbox-exec + setrlimit. Return result dict."""
    sandbox_argv = [SANDBOX_EXEC_BIN, "-f", str(profile_path)] + argv
    started = time.monotonic()
    started_iso = _now_iso()
    bounded_timeout = max(0.001, float(limits.wall_clock_timeout_seconds))

    rusage_before = resource.getrusage(resource.RUSAGE_CHILDREN)
    applied_path = Path(tempfile.mkstemp(prefix="rlim-applied-", dir=str(sandbox))[1])

    process_tree_killed = False
    timed_out_flag = False
    error_str: str | None = None
    proc_exit: int | None = None
    raw_stdout = b""
    raw_stderr = b""
    pgid: int | None = None

    try:
        proc = subprocess.Popen(
            sandbox_argv,
            cwd=str(sandbox),
            env=_minimal_env(),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=_make_preexec(limits, applied_path),
            shell=False,
        )
    except OSError as exc:
        elapsed_ms = int((time.monotonic() - started) * 1000)
        return _make_result_dict(
            argv=argv,
            sandbox=sandbox,
            profile_path=profile_path,
            profile_hash_value=profile_hash_value,
            limits=limits,
            started_iso=started_iso,
            ended_iso=_now_iso(),
            duration_ms=elapsed_ms,
            status="error",
            exit_code=None,
            stdout=b"",
            stderr=b"",
            timed_out=False,
            process_tree_killed=False,
            error=f"{type(exc).__name__}: {exc}",
            applied=_read_applied(applied_path),
            peak_rss_bytes=0,
            sandbox_size_bytes=_measure_sandbox_size(sandbox),
            resource_violations=[],
        )

    try:
        pgid = os.getpgid(proc.pid)
    except (ProcessLookupError, OSError):
        pgid = proc.pid

    try:
        raw_stdout, raw_stderr = proc.communicate(timeout=bounded_timeout)
        proc_exit = proc.returncode
    except subprocess.TimeoutExpired:
        timed_out_flag = True
        if pgid is not None:
            _killpg_safe(pgid, signal.SIGKILL)
            process_tree_killed = True
        try:
            raw_stdout, raw_stderr = proc.communicate(timeout=2.0)
        except subprocess.TimeoutExpired:
            try:
                proc.kill()
            except OSError:
                pass
            try:
                raw_stdout, raw_stderr = proc.communicate(timeout=2.0)
            except subprocess.TimeoutExpired:
                raw_stdout, raw_stderr = b"", b""
        proc_exit = proc.returncode
        error_str = f"command exceeded {bounded_timeout}s wall-clock cap"
    except Exception as exc:
        error_str = f"{type(exc).__name__}: {exc}"
        proc_exit = -1

    elapsed_ms = int((time.monotonic() - started) * 1000)
    rusage_after = resource.getrusage(resource.RUSAGE_CHILDREN)
    peak_rss = _peak_rss_delta(rusage_before, rusage_after)

    applied = _read_applied(applied_path)
    try:
        applied_path.unlink()
    except OSError:
        pass

    sandbox_size = _measure_sandbox_size(sandbox)

    if timed_out_flag:
        status = "timed_out"
    elif proc_exit == 0:
        status = "ok"
    elif proc_exit is None:
        status = "error"
    else:
        status = "nonzero_exit"

    resource_violations: list[str] = []
    if peak_rss > limits.memory_limit_bytes:
        resource_violations.append("memory_overrun")
    if sandbox_size > limits.sandbox_size_limit_bytes:
        resource_violations.append("sandbox_size_overrun")
    if applied["cpu"] and elapsed_ms / 1000.0 >= limits.cpu_limit_seconds:
        # Heuristic: if we ran for at least cpu_limit_seconds wall clock
        # AND CPU rlimit was applied, the run likely terminated by CPU.
        resource_violations.append("cpu_time_exhausted")

    return _make_result_dict(
        argv=argv,
        sandbox=sandbox,
        profile_path=profile_path,
        profile_hash_value=profile_hash_value,
        limits=limits,
        started_iso=started_iso,
        ended_iso=_now_iso(),
        duration_ms=elapsed_ms,
        status=status,
        exit_code=proc_exit,
        stdout=raw_stdout,
        stderr=raw_stderr,
        timed_out=timed_out_flag,
        process_tree_killed=process_tree_killed,
        error=error_str,
        applied=applied,
        peak_rss_bytes=peak_rss,
        sandbox_size_bytes=sandbox_size,
        resource_violations=resource_violations,
    )


def _peak_rss_delta(before, after) -> int:
    """Return peak RSS in BYTES (normalized).

    macOS reports ru_maxrss in BYTES; Linux reports it in KIBIBYTES. We
    compute the increment (after - before) so concurrent prior runs
    don't pollute this value, then normalize to bytes.
    """
    delta_units = max(0, int(after.ru_maxrss) - int(before.ru_maxrss))
    if platform.system() == "Linux":
        return delta_units * 1024
    return delta_units


def _make_result_dict(
    *,
    argv: list[str],
    sandbox: Path,
    profile_path: Path,
    profile_hash_value: str,
    limits: ResourceLimits,
    started_iso: str,
    ended_iso: str,
    duration_ms: int,
    status: str,
    exit_code: int | None,
    stdout: bytes,
    stderr: bytes,
    timed_out: bool,
    process_tree_killed: bool,
    error: str | None,
    applied: dict[str, bool],
    peak_rss_bytes: int,
    sandbox_size_bytes: int,
    resource_violations: list[str],
) -> dict:
    out_bytes, out_trunc = _truncate_bytes(stdout, limits.stdout_limit_bytes)
    err_bytes, err_trunc = _truncate_bytes(stderr, limits.stderr_limit_bytes)
    return {
        "command": " ".join(shlex.quote(a) for a in argv),
        "argv": argv,
        "cwd": str(sandbox),
        "env_keys": sorted(_minimal_env().keys()),
        "timestamp_start": started_iso,
        "timestamp_end": ended_iso,
        "duration_ms": duration_ms,
        "status": status,
        "exit_code": exit_code,
        "stdout": out_bytes.decode("utf-8", errors="replace"),
        "stdout_truncated": out_trunc,
        "stdout_hash": _sha256_hex(out_bytes),
        "stderr": err_bytes.decode("utf-8", errors="replace"),
        "stderr_truncated": err_trunc,
        "stderr_hash": _sha256_hex(err_bytes),
        "timed_out": timed_out,
        "process_tree_killed": process_tree_killed,
        "error": error,
        "isolation_mode": ISOLATION_MODE,
        "kernel_enforced": True,
        "sandbox_profile_hash": profile_hash_value,
        "sandbox_profile_path": str(profile_path),
        "denied_syscalls": [],
        # Resource-limit fields
        "cpu_limit_seconds": limits.cpu_limit_seconds,
        "memory_limit_bytes": limits.memory_limit_bytes,
        "fd_limit": limits.fd_limit,
        "process_limit": limits.process_limit,
        "stdout_limit_bytes": limits.stdout_limit_bytes,
        "stderr_limit_bytes": limits.stderr_limit_bytes,
        "sandbox_size_limit_bytes": limits.sandbox_size_limit_bytes,
        "command_count_limit": limits.command_count_limit,
        "wall_clock_timeout_seconds": limits.wall_clock_timeout_seconds,
        "rlimits_applied": applied,
        "peak_rss_bytes": peak_rss_bytes,
        "sandbox_size_bytes": sandbox_size_bytes,
        "resource_violations": resource_violations,
    }


# ---------------------------------------------------------------------------
# Public execution paths
# ---------------------------------------------------------------------------


def execute_command_bounded(
    command: str,
    sandbox: Path,
    *,
    limits: ResourceLimits = DEFAULT_LIMITS,
    extra_binaries: tuple[str, ...] = (),
) -> dict:
    """Full stack: deny-first classifier → kernel isolation → resource limits.

    Commands rejected by the v0.1 / v0.2 classifier never reach
    sandbox-exec; the result dict records ``status="blocked_by_classifier"``
    and ``kernel_enforced=False``.
    """
    verdict = classify_execute_command(command)
    if not verdict.allowed:
        return _blocked_dict(command, sandbox, limits, verdict.reason)
    argv = _resolve_argv(command)
    binary = argv[0]
    binaries = sorted(set([binary, *extra_binaries]))
    profile = (
        generate_profile_multi(binaries, sandbox)
        if len(binaries) > 1 else generate_profile(binary, sandbox)
    )
    profile_path = write_profile(profile)
    return _run_with_limits(
        argv, sandbox, profile_path, hash_profile(profile), limits,
    )


def execute_bounded_raw(
    argv: list[str],
    sandbox: Path,
    *,
    limits: ResourceLimits = DEFAULT_LIMITS,
    binaries: tuple[str, ...] = (),
    allow_process_fork: bool = False,
) -> dict:
    """Run argv under sandbox-exec + rlimits, WITHOUT the policy classifier.

    Used by self-check fixtures that exercise kernel-and-rlimit behavior
    on commands the classifier would refuse (or that require an extended
    binary allowlist).

    ``allow_process_fork=True`` injects ``(allow process-fork)`` into the
    profile so the wrapped subprocess may call ``fork()``. Without this
    flag, the underlying ``(deny default)`` blocks real ``fork()`` calls
    (note: ``(deny process-exec*)`` blocks ``posix_spawn`` regardless).
    Required for fixtures that test process-tree termination of
    legitimately backgrounded children.
    """
    if not argv:
        raise ValueError("argv is empty")
    binary_list = sorted(set(binaries) or {argv[0]})
    profile = (
        generate_profile_multi(binary_list, sandbox)
        if len(binary_list) > 1 else generate_profile(binary_list[0], sandbox)
    )
    if allow_process_fork:
        profile = profile.replace(
            "(deny default)\n",
            "(deny default)\n(allow process-fork)\n",
            1,
        )
    profile_path = write_profile(profile)
    return _run_with_limits(
        argv, sandbox, profile_path, hash_profile(profile), limits,
    )


def execute_commands_bounded(
    commands: list[str],
    sandbox: Path,
    *,
    limits: ResourceLimits = DEFAULT_LIMITS,
) -> dict:
    """Execute a list of commands sequentially under bounded isolation.

    Pre-execution, refuses if ``len(commands) > limits.command_count_limit``.
    Returns a batch manifest summarizing per-command results.
    """
    started_iso = _now_iso()
    if len(commands) > limits.command_count_limit:
        return {
            "final_status": "rejected_pre_exec",
            "code": "command_count_overflow",
            "reason": (
                f"command count {len(commands)} exceeds "
                f"command_count_limit={limits.command_count_limit}"
            ),
            "commands": list(commands),
            "command_count_limit": limits.command_count_limit,
            "results": [],
            "timestamps": {"start": started_iso, "end": _now_iso()},
            "exit_status": 1,
        }
    results: list[dict] = []
    for cmd in commands:
        results.append(execute_command_bounded(cmd, sandbox, limits=limits))
    final = "ok" if all(r["status"] == "ok" for r in results) else "completed_with_errors"
    return {
        "final_status": final,
        "code": "",
        "reason": "",
        "commands": list(commands),
        "command_count_limit": limits.command_count_limit,
        "results": results,
        "timestamps": {"start": started_iso, "end": _now_iso()},
        "exit_status": 0 if final == "ok" else 1,
    }


def _blocked_dict(command: str, sandbox: Path, limits: ResourceLimits, reason: str) -> dict:
    return {
        "command": command,
        "argv": [],
        "cwd": str(sandbox),
        "env_keys": sorted(_minimal_env().keys()),
        "timestamp_start": _now_iso(),
        "timestamp_end": _now_iso(),
        "duration_ms": 0,
        "status": "blocked_by_classifier",
        "exit_code": None,
        "stdout": "",
        "stdout_truncated": False,
        "stdout_hash": _sha256_hex(b""),
        "stderr": "",
        "stderr_truncated": False,
        "stderr_hash": _sha256_hex(b""),
        "timed_out": False,
        "process_tree_killed": False,
        "error": reason,
        "isolation_mode": ISOLATION_MODE,
        "kernel_enforced": False,
        "sandbox_profile_hash": "",
        "sandbox_profile_path": "",
        "denied_syscalls": [],
        "cpu_limit_seconds": limits.cpu_limit_seconds,
        "memory_limit_bytes": limits.memory_limit_bytes,
        "fd_limit": limits.fd_limit,
        "process_limit": limits.process_limit,
        "stdout_limit_bytes": limits.stdout_limit_bytes,
        "stderr_limit_bytes": limits.stderr_limit_bytes,
        "sandbox_size_limit_bytes": limits.sandbox_size_limit_bytes,
        "command_count_limit": limits.command_count_limit,
        "wall_clock_timeout_seconds": limits.wall_clock_timeout_seconds,
        "rlimits_applied": {"cpu": False, "memory": False, "fd": False, "nproc": False},
        "peak_rss_bytes": 0,
        "sandbox_size_bytes": 0,
        "resource_violations": [],
    }


# ---------------------------------------------------------------------------
# Manifest writer
# ---------------------------------------------------------------------------


def _write_manifest(result: dict, fixture_name: str) -> Path:
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
# Self-check
# ---------------------------------------------------------------------------


@dataclass
class FixtureResult:
    name: str
    passed: bool
    detail: str
    manifest: str | None = None


def _make_sandbox(prefix: str) -> Path:
    return Path(tempfile.mkdtemp(prefix=f"rlim-{prefix}-"))


def _cleanup(path: Path) -> None:
    shutil.rmtree(path, ignore_errors=True)


def _check_1_pwd_succeeds() -> FixtureResult:
    name = "allowed_pwd_succeeds"
    sandbox = _make_sandbox("pwd")
    try:
        result = execute_command_bounded("pwd", sandbox)
        manifest = _write_manifest(result, name)
        ok = (
            result["status"] == "ok"
            and result["exit_code"] == 0
            and result["resource_violations"] == []
            and result["kernel_enforced"] is True
            and result["isolation_mode"] == ISOLATION_MODE
            and result["rlimits_applied"]["cpu"] is True
            and result["rlimits_applied"]["fd"] is True
            and result["rlimits_applied"]["nproc"] is True
        )
        detail = (
            f"status={result['status']}, exit={result['exit_code']}, "
            f"rlimits_applied={result['rlimits_applied']}"
        )
    finally:
        _cleanup(sandbox)
    return FixtureResult(name, ok, detail, str(manifest))


def _check_2_stdout_flood() -> FixtureResult:
    name = "stdout_flood_truncates_deterministically"
    sandbox = _make_sandbox("flood")
    try:
        argv = [PYTHON_REAL, "-c", "import sys; sys.stdout.write('a' * 100000)"]
        result = execute_bounded_raw(argv, sandbox, binaries=PYTHON_BINARIES)
        manifest = _write_manifest(result, name)
        cap = result["stdout_limit_bytes"]
        ok = (
            result["status"] == "ok"
            and result["stdout_truncated"] is True
            and len(result["stdout"].encode("utf-8")) == cap
            and result["stdout"] == "a" * cap
            and result["stdout_hash"] == _sha256_hex(b"a" * cap)
        )
        detail = (
            f"truncated={result['stdout_truncated']}, "
            f"len={len(result['stdout'])}, hash={result['stdout_hash'][:24]}…"
        )
    finally:
        _cleanup(sandbox)
    return FixtureResult(name, ok, detail, str(manifest))


def _check_3_timeout_kills_group() -> FixtureResult:
    name = "sleep_timeout_kills_process_group"
    sandbox = _make_sandbox("timeout")
    try:
        limits = ResourceLimits(wall_clock_timeout_seconds=0.5)
        result = execute_bounded_raw(["/bin/sleep", "5"], sandbox, limits=limits)
        manifest = _write_manifest(result, name)
        ok = (
            result["status"] == "timed_out"
            and result["timed_out"] is True
            and result["process_tree_killed"] is True
            and 400 <= result["duration_ms"] < 5000
        )
        detail = (
            f"status={result['status']}, killed={result['process_tree_killed']}, "
            f"duration={result['duration_ms']}ms"
        )
    finally:
        _cleanup(sandbox)
    return FixtureResult(name, ok, detail, str(manifest))


def _check_4_nested_dies() -> FixtureResult:
    name = "nested_child_must_not_survive_parent_death"
    sandbox = _make_sandbox("nested")
    try:
        # Allow shell + sleep + echo and raise NPROC so the shell can fork
        # the inner sleep. We use a short timeout, then verify the inner
        # sleep PID is dead afterward.
        limits = ResourceLimits(
            process_limit=4096,
            wall_clock_timeout_seconds=0.6,
        )
        cmd_argv = ["/bin/sh", "-c", "/bin/sleep 60 & echo $! >&2 ; wait"]
        result = execute_bounded_raw(
            cmd_argv,
            sandbox,
            limits=limits,
            binaries=("/bin/sh", "/bin/bash", "/bin/sleep", "/bin/echo"),
            allow_process_fork=True,
        )
        manifest = _write_manifest(result, name)
        # Parse inner sleep PID from stderr.
        child_pid: int | None = None
        for line in (result.get("stderr") or "").splitlines():
            line = line.strip()
            if line.isdigit():
                child_pid = int(line)
                break
        # Allow a moment for kill propagation then verify the PID is gone.
        time.sleep(0.5)
        child_alive = False
        if child_pid is not None:
            try:
                os.kill(child_pid, 0)
                child_alive = True
            except ProcessLookupError:
                child_alive = False
            except PermissionError:
                # Different uid would mean a stranger process; treat as dead.
                child_alive = False
        ok = (
            result["timed_out"] is True
            and result["process_tree_killed"] is True
            and child_pid is not None
            and child_alive is False
        )
        detail = (
            f"killed={result['process_tree_killed']}, "
            f"child_pid={child_pid}, child_alive={child_alive}"
        )
    finally:
        _cleanup(sandbox)
    return FixtureResult(name, ok, detail, str(manifest))


def _check_5_fd_exhaustion() -> FixtureResult:
    name = "fd_exhaustion_rejected"
    sandbox = _make_sandbox("fd")
    try:
        limits = ResourceLimits(fd_limit=32)
        code = (
            "import sys\n"
            "fs = []\n"
            "try:\n"
            "    for i in range(200):\n"
            "        fs.append(open(f'fd_{i}.txt', 'w'))\n"
            "except OSError as e:\n"
            "    sys.stderr.write(f'OPEN-FAIL-AT-{len(fs)}: {type(e).__name__}: {e}\\n')\n"
            "    sys.exit(7)\n"
            "sys.exit(0)\n"
        )
        argv = [PYTHON_REAL, "-c", code]
        result = execute_bounded_raw(argv, sandbox, limits=limits, binaries=PYTHON_BINARIES)
        manifest = _write_manifest(result, name)
        ok = (
            result["exit_code"] != 0
            and ("OPEN-FAIL-AT" in result["stderr"]
                 or "Too many open files" in result["stderr"]
                 or "OSError" in result["stderr"])
            and result["rlimits_applied"]["fd"] is True
        )
        detail = (
            f"exit={result['exit_code']}, "
            f"fd_applied={result['rlimits_applied']['fd']}, "
            f"stderr_head={result['stderr'].splitlines()[0] if result['stderr'] else ''}"
        )
    finally:
        _cleanup(sandbox)
    return FixtureResult(name, ok, detail, str(manifest))


def _check_6_memory_handled() -> FixtureResult:
    name = "memory_exhaustion_handled"
    sandbox = _make_sandbox("mem")
    try:
        limits = ResourceLimits(memory_limit_bytes=64 * 1024 * 1024)
        # Allocate ~256 MiB into a bytearray (forces actual page-backing).
        argv = [PYTHON_REAL, "-c", "a = bytearray(256*1024*1024); a[0]=1"]
        result = execute_bounded_raw(argv, sandbox, limits=limits, binaries=PYTHON_BINARIES)
        manifest = _write_manifest(result, name)
        applied = result["rlimits_applied"]["memory"]
        if applied:
            # Linux path: the kernel enforces RLIMIT_AS, so the child
            # must fail (MemoryError or nonzero exit).
            ok = result["exit_code"] != 0 or "MemoryError" in result["stderr"]
            detail = (
                f"linux/enforced path: applied=True, "
                f"exit={result['exit_code']}, stderr_head="
                f"{(result['stderr'] or '').splitlines()[0] if result['stderr'] else ''}"
            )
        else:
            # macOS path: setrlimit failed unprivileged; runtime detected
            # peak RSS post-hoc and recorded a memory_overrun violation.
            ok = (
                "memory_overrun" in result["resource_violations"]
                and result["peak_rss_bytes"] > limits.memory_limit_bytes
            )
            detail = (
                f"macOS/post-hoc path: applied=False, "
                f"peak_rss={result['peak_rss_bytes']}, "
                f"violations={result['resource_violations']}"
            )
    finally:
        _cleanup(sandbox)
    return FixtureResult(name, ok, detail, str(manifest))


def _check_7_fork_rejected() -> FixtureResult:
    name = "fork_attempt_rejected"
    sandbox = _make_sandbox("fork")
    try:
        argv = [
            PYTHON_REAL, "-c",
            "import os, sys\n"
            "try:\n"
            "    pid = os.fork()\n"
            "    sys.stderr.write(f'FORKED pid={pid}\\n')\n"
            "    if pid == 0:\n"
            "        os._exit(0)\n"
            "    sys.exit(0)\n"
            "except BlockingIOError as e:\n"
            "    sys.stderr.write(f'FORK-BLOCKED: {e}\\n')\n"
            "    sys.exit(8)\n"
            "except OSError as e:\n"
            "    sys.stderr.write(f'FORK-OSERR: {e}\\n')\n"
            "    sys.exit(9)\n"
            "except PermissionError as e:\n"
            "    sys.stderr.write(f'FORK-PERM: {e}\\n')\n"
            "    sys.exit(10)\n"
        ]
        # NOTE: process-fork is denied by the os-isolation profile's
        # (deny default), so even without RLIMIT_NPROC bite the kernel
        # blocks the os.fork() call. This is the desired layered defense:
        # the kernel-level deny fires first; if that ever drifted, the
        # rlimit fallback (NPROC<=user's process count) would still bite.
        result = execute_bounded_raw(argv, sandbox, binaries=PYTHON_BINARIES)
        manifest = _write_manifest(result, name)
        marker_present = (
            "FORK-BLOCKED" in result["stderr"]
            or "FORK-OSERR" in result["stderr"]
            or "FORK-PERM" in result["stderr"]
            or "Resource temporarily unavailable" in result["stderr"]
            or "Operation not permitted" in result["stderr"]
        )
        ok = (
            result["exit_code"] != 0
            and marker_present
        )
        detail = (
            f"exit={result['exit_code']}, "
            f"nproc_applied={result['rlimits_applied']['nproc']}, "
            f"stderr_head={result['stderr'].splitlines()[0] if result['stderr'] else ''}"
        )
    finally:
        _cleanup(sandbox)
    return FixtureResult(name, ok, detail, str(manifest))


def _check_8_command_count() -> FixtureResult:
    name = "excessive_command_count_rejected_pre_exec"
    sandbox = _make_sandbox("count")
    try:
        limits = ResourceLimits(command_count_limit=3)
        batch = execute_commands_bounded(
            ["pwd", "pwd", "pwd", "pwd"],
            sandbox,
            limits=limits,
        )
        ok = (
            batch["final_status"] == "rejected_pre_exec"
            and batch["code"] == "command_count_overflow"
            and batch["results"] == []
            and batch["exit_status"] == 1
        )
        detail = (
            f"final_status={batch['final_status']}, code={batch['code']}, "
            f"results_len={len(batch['results'])}"
        )
    finally:
        _cleanup(sandbox)
    return FixtureResult(name, ok, detail, None)


def _check_9_sandbox_size() -> FixtureResult:
    name = "sandbox_size_over_limit_detected"
    sandbox = _make_sandbox("size")
    try:
        limits = ResourceLimits(sandbox_size_limit_bytes=1 * 1024 * 1024)
        argv = [
            PYTHON_REAL, "-c",
            "open('big.bin', 'wb').write(b'x' * (2*1024*1024))",
        ]
        result = execute_bounded_raw(argv, sandbox, limits=limits, binaries=PYTHON_BINARIES)
        manifest = _write_manifest(result, name)
        ok = (
            "sandbox_size_overrun" in result["resource_violations"]
            and result["sandbox_size_bytes"] > limits.sandbox_size_limit_bytes
        )
        detail = (
            f"sandbox_size={result['sandbox_size_bytes']}, "
            f"limit={limits.sandbox_size_limit_bytes}, "
            f"violations={result['resource_violations']}"
        )
    finally:
        _cleanup(sandbox)
    return FixtureResult(name, ok, detail, str(manifest))


def _check_10_repo_fingerprint() -> FixtureResult:
    name = "repo_fingerprint_unchanged"
    sandbox = _make_sandbox("fp")
    try:
        before = repo_fingerprint(REPO_ROOT)
        result = execute_command_bounded("pwd", sandbox)
        after = repo_fingerprint(REPO_ROOT)
        manifest = _write_manifest(result, name)
        ok = result["status"] == "ok" and before == after
        detail = f"before==after: {before == after}, status={result['status']}"
    finally:
        _cleanup(sandbox)
    return FixtureResult(name, ok, detail, str(manifest))


def _check_11_manifest_fields() -> FixtureResult:
    name = "manifest_resource_fields_populated"
    sandbox = _make_sandbox("fields")
    try:
        result = execute_command_bounded("pwd", sandbox)
        manifest = _write_manifest(result, name)
        required = (
            "cpu_limit_seconds", "memory_limit_bytes", "fd_limit",
            "process_limit", "stdout_limit_bytes", "stderr_limit_bytes",
            "sandbox_size_limit_bytes", "resource_violations",
            "process_tree_killed", "stdout_truncated", "stderr_truncated",
            "stdout_hash", "stderr_hash", "rlimits_applied",
            "peak_rss_bytes", "sandbox_size_bytes",
        )
        missing = [k for k in required if k not in result]
        ok = (
            not missing
            and isinstance(result["rlimits_applied"], dict)
            and isinstance(result["resource_violations"], list)
        )
        detail = f"missing_fields={missing}"
    finally:
        _cleanup(sandbox)
    return FixtureResult(name, ok, detail, str(manifest))


def _check_12_truncation_hash_stable() -> FixtureResult:
    name = "deterministic_truncation_hashes_stable"
    sandbox1 = _make_sandbox("trunc1")
    sandbox2 = _make_sandbox("trunc2")
    try:
        argv = [PYTHON_REAL, "-c", "import sys; sys.stdout.write('a' * 100000)"]
        r1 = execute_bounded_raw(argv, sandbox1, binaries=PYTHON_BINARIES)
        r2 = execute_bounded_raw(argv, sandbox2, binaries=PYTHON_BINARIES)
        ok = (
            r1["stdout_truncated"] is True
            and r2["stdout_truncated"] is True
            and r1["stdout_hash"] == r2["stdout_hash"]
            and r1["timestamp_start"] != r2["timestamp_start"]
            and r1["status"] == "ok" and r2["status"] == "ok"
        )
        detail = (
            f"hash1={r1['stdout_hash'][:24]}…, hash2={r2['stdout_hash'][:24]}…, "
            f"equal={r1['stdout_hash'] == r2['stdout_hash']}"
        )
    finally:
        _cleanup(sandbox1)
        _cleanup(sandbox2)
    return FixtureResult(name, ok, detail, None)


_FIXTURES: tuple = (
    _check_1_pwd_succeeds,
    _check_2_stdout_flood,
    _check_3_timeout_kills_group,
    _check_4_nested_dies,
    _check_5_fd_exhaustion,
    _check_6_memory_handled,
    _check_7_fork_rejected,
    _check_8_command_count,
    _check_9_sandbox_size,
    _check_10_repo_fingerprint,
    _check_11_manifest_fields,
    _check_12_truncation_hash_stable,
)


def self_check() -> int:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    results: list[FixtureResult] = [fn() for fn in _FIXTURES]
    all_ok = all(r.passed for r in results)

    summary = {
        "runtime": "resource_limit_runtime",
        "runtime_version": RUNTIME_VERSION,
        "isolation_mode": ISOLATION_MODE,
        "platform": platform.system(),
        "timestamp": _now_iso(),
        "all_passed": all_ok,
        "fixtures": [
            {
                "name": r.name,
                "passed": r.passed,
                "detail": r.detail,
                "manifest": r.manifest,
            }
            for r in results
        ],
    }
    (REPORTS_DIR / f"resource_limit_runtime_{RUNTIME_VERSION}.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    md_lines: list[str] = []
    md_lines.append(f"# Resource Limit Runtime {RUNTIME_VERSION} self-check")
    md_lines.append("")
    md_lines.append(f"- timestamp: `{summary['timestamp']}`")
    md_lines.append(f"- platform: `{summary['platform']}`")
    md_lines.append(f"- isolation_mode: `{summary['isolation_mode']}`")
    md_lines.append(f"- all_passed: `{all_ok}`")
    md_lines.append("")
    md_lines.append("## Fixtures")
    md_lines.append("")
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        md_lines.append(f"- `{r.name}` — **{status}**")
        if r.manifest:
            md_lines.append(f"  - manifest: `{r.manifest}`")
        md_lines.append(f"  - detail: {r.detail}")
    md_lines.append("")
    md_lines.append("## Bounded-runtime law")
    md_lines.append("")
    md_lines.append(
        "> Governance determines admissibility. Kernel isolation "
        "constrains scope. Resource limits constrain survivability."
    )
    md_lines.append("")
    (REPORTS_DIR / f"resource_limit_runtime_{RUNTIME_VERSION}.md").write_text(
        "\n".join(md_lines), encoding="utf-8",
    )

    print(f"RESOURCE-LIMIT-RUNTIME {RUNTIME_VERSION} self-check: {len(results)} fixtures")
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
        result = execute_command_bounded("pwd", sandbox)
        manifest = _write_manifest(result, "run_fixture")
    finally:
        _cleanup(sandbox)
    print(f"RESOURCE-LIMIT run-fixture status={result['status']} exit={result['exit_code']}")
    print(f"  isolation_mode:        {result['isolation_mode']}")
    print(f"  rlimits_applied:       {result['rlimits_applied']}")
    print(f"  resource_violations:   {result['resource_violations']}")
    print(f"  peak_rss_bytes:        {result['peak_rss_bytes']}")
    print(f"  sandbox_size_bytes:    {result['sandbox_size_bytes']}")
    print(f"  process_tree_killed:   {result['process_tree_killed']}")
    print(f"  stdout_hash:           {result['stdout_hash']}")
    print(f"  manifest:              {manifest}")
    return 0 if result["status"] == "ok" else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="resource_limit_runtime",
        description="WiseOrder Resource Limit Runtime v0.1 — bounded isolation.",
    )
    sub = parser.add_subparsers(dest="verb", required=True)

    p_check = sub.add_parser("self-check", help="run all twelve self-check fixtures")
    p_check.set_defaults(func=_cli_self_check)

    p_fixture = sub.add_parser(
        "run-fixture",
        help="run the canonical valid fixture (`pwd`) under bounded isolation",
    )
    p_fixture.set_defaults(func=_cli_run_fixture)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
