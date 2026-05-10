# Real Agent Runtime v0.2 — Execute-Mode Self-Check Report

**Timestamp (UTC):** `2026-05-09T00:48:06Z`
**Cases:** 10 (10 passed / 0 failed)
**Overall:** PASS

## Execute-Mode Allowlist

- `pwd`
- `ls`
- `find`
- `cat`
- `.venv/bin/python tools/check_no_pseudocode.py`
- `.venv/bin/python tools/check_workforce.py`
- `.venv/bin/python tools/real_agent_runtime.py check`
- `make no-pseudocode`
- `make workforce-check`
- `make real-agent-check`

## Forbidden Command Patterns (deny-first; identical to v0.1)

- `sudo`
- `curl`
- `wget`
- `ssh`
- `scp`
- `git push`
- `git reset --hard`
- `git clean`
- `rm -rf`
- `chmod`
- `chown`
- `open `
- `http://`
- `https://`

## Timeout Policy

- default per-command timeout: `60.0s`
- hard cap: `300.0s`
- output byte cap (per stream): `65536`

## Self-Check Results

| # | Case | Result |
| -: | --- | :-: |
| 1 | `execute_allowed_command_succeeds` | **PASS** |
| 2 | `forbidden_command_blocked_before_subprocess` | **PASS** |
| 3 | `command_timeout_recorded` | **PASS** |
| 4 | `wrong_agent_identity_refused` | **PASS** |
| 5 | `drafted_work_order_refused` | **PASS** |
| 6 | `closed_refused_unless_replay_mode` | **PASS** |
| 7 | `missing_allowed_files_refused` | **PASS** |
| 8 | `missing_forbidden_files_refused` | **PASS** |
| 9 | `source_repo_unchanged_after_execute` | **PASS** |
| 10 | `manifest_records_stdout_stderr_exit_duration_cwd` | **PASS** |

## Detail

### `execute_allowed_command_succeeds`

```json
{
  "case": "execute_allowed_command_succeeds",
  "command_results_len": 1,
  "exit_status": 0,
  "first_exit": 0,
  "first_status": "ok",
  "pass": true,
  "repo_unchanged": true
}
```

### `forbidden_command_blocked_before_subprocess`

```json
{
  "blocked_count": 3,
  "case": "forbidden_command_blocked_before_subprocess",
  "pass": true,
  "repo_unchanged": true,
  "statuses": [
    "blocked",
    "blocked",
    "blocked"
  ]
}
```

### `command_timeout_recorded`

```json
{
  "case": "command_timeout_recorded",
  "duration_ms": 2,
  "pass": true,
  "repo_unchanged": true,
  "status": "timed_out",
  "timed_out": true
}
```

### `wrong_agent_identity_refused`

```json
{
  "case": "wrong_agent_identity_refused",
  "codes": [
    "assigned_to_mismatch"
  ],
  "pass": true
}
```

### `drafted_work_order_refused`

```json
{
  "case": "drafted_work_order_refused",
  "codes": [
    "status_not_admissible"
  ],
  "pass": true
}
```

### `closed_refused_unless_replay_mode`

```json
{
  "case": "closed_refused_unless_replay_mode",
  "pass": true,
  "refused_codes": [
    "status_not_admissible"
  ],
  "replay_mode_set": true,
  "replay_status": "ok"
}
```

### `missing_allowed_files_refused`

```json
{
  "case": "missing_allowed_files_refused",
  "codes": [
    "missing_allowed_files"
  ],
  "pass": true
}
```

### `missing_forbidden_files_refused`

```json
{
  "case": "missing_forbidden_files_refused",
  "codes": [
    "missing_forbidden_files"
  ],
  "pass": true
}
```

### `source_repo_unchanged_after_execute`

```json
{
  "case": "source_repo_unchanged_after_execute",
  "pass": true,
  "repo_fp_after": "sha256:59638ebdc51fa8d14667eeafdf193e52a83099f22cce0e85ae8c93c8a9574e8e",
  "repo_fp_before": "sha256:59638ebdc51fa8d14667eeafdf193e52a83099f22cce0e85ae8c93c8a9574e8e"
}
```

### `manifest_records_stdout_stderr_exit_duration_cwd`

```json
{
  "case": "manifest_records_stdout_stderr_exit_duration_cwd",
  "keys_present": [
    "cwd",
    "duration_ms",
    "exit_code",
    "stderr",
    "stdout"
  ],
  "pass": true
}
```

---

**End of Real Agent Runtime execute-mode self-check report.**
