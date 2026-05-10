# Real Agent Runtime v0.1 — Self-Check Report

**Timestamp (UTC):** `2026-05-09T00:48:05Z`
**Cases:** 10 (10 passed / 0 failed)
**Overall:** PASS

## Identities

- `builder-01`
- `canon_guardian-01`
- `release-01`
- `reviewer-01`

## Policy

**Allowed commands:**
- `pwd`
- `ls`
- `find`
- `cat`
- `python3`
- `.venv/bin/python`
- `make no-pseudocode`
- `make workforce-check`

**Forbidden command patterns:**
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

**Default-denied paths (before per-WO forbidden_files):**
- `runtime/`
- `intellagent_runtime/`
- `vectors/`
- `canonicalization/corpus/`
- `tools/`

## Self-Check Results

| # | Case | Expected | Actual | Refusal Code | Result |
| -: | --- | --- | --- | --- | :-: |
| 1 | `approved_assigned_wo_passes_admission` | accepted | accepted | `—` | **PASS** |
| 2 | `drafted_wo_refused` | refused | refused | `status_not_admissible` | **PASS** |
| 3 | `unassigned_wo_refused` | refused | refused | `assigned_to_mismatch` | **PASS** |
| 4 | `wrong_agent_identity_refused` | refused | refused | `assigned_to_mismatch` | **PASS** |
| 5 | `forbidden_command_refused` | accepted | accepted | `—` | **PASS** |
| 6 | `forbidden_file_read_refused` | accepted | accepted | `—` | **PASS** |
| 7 | `write_outside_sandbox_refused` | accepted | accepted | `—` | **PASS** |
| 8 | `closed_wo_refused` | refused | refused | `status_not_admissible` | **PASS** |
| 9 | `missing_allowed_files_refused` | refused | refused | `missing_allowed_files` | **PASS** |
| 10 | `missing_forbidden_files_refused` | refused | refused | `missing_forbidden_files` | **PASS** |

## Directories

- `real_agents_dir`: `workforce/real_agents`
- `sandboxes_dir`: `workforce/real_agents/sandboxes`
- `runs_dir`: `workforce/real_agents/runs`
- `reports_dir`: `reports/real_agent_runtime`

---

**End of Real Agent Runtime self-check report.**
