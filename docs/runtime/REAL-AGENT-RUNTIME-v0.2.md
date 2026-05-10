# REAL AGENT RUNTIME v0.2
## Bounded Local Subprocess Execution For Governed Work Orders

**Status:** v0.2 — operational specification, normative for the execute-mode surface in `tools/real_agent_runtime.py` and the `workforce/real_agents/` tree. Strict superset of v0.1: every v0.1 admission rule, command-policy verdict, filesystem-policy verdict, refusal code, and manifest field is preserved unchanged. v0.2 adds a single new path — real local subprocess invocation of allowlisted commands inside a sandbox copy — without modifying any v0.1 surface.

**Companion documents:** `REAL-AGENT-RUNTIME-v0.1.md` (the dry-run base; preserved verbatim), `WORKFORCE-EXECUTION-RUNTIME-v0.1.md` (lifecycle + records), `AGENT-GOVERNANCE-WORKFORCE-v0.1.md` (roles + authority), `WORKFORCE-HARDENING-v0.2.md` (validator hardening), `WORKFORCE-SANDBOX-STRESS-v0.1.md` (record-level pressure suite), `WAIVER-MECHANISM-v0.1.md` (sanctioned exception class), `FORBIDDEN-SURFACES-v0.1.md`, `VALIDATION-LAW-v0.1.md`, `REPLAY-LAW-v0.1.md`, `TRUST-LAW-v0.1.md`.

> **Core thesis.** Agents become real only as bounded worker processes executing approved work orders in sandbox copies. v0.2 converts the v0.1 "would-execute" placeholder into a real `subprocess.run` invocation with cwd inside the sandbox, a minimal environment, a wall-clock timeout, and a manifest entry that captures stdout, stderr, exit code, duration, and cwd for every attempt.

> **Explicitly stated.**
>
> - **v0.2 creates real local subprocess execution.** A previously dry-run-only runtime now runs commands.
> - **v0.2 does not create autonomous AI planning.** The runtime executes only commands it is told to execute (from the work order's `required_gates` or via an explicit `--command` argument); it does not select, schedule, or invent steps.
> - **v0.2 does not create background agents.** The runtime is a one-shot CLI; no daemon, no long-lived process, no scheduler.
> - **v0.2 does not provide kernel-level isolation.** The sandbox is `shutil.copytree`, not a UNIX user namespace, jail, or container.
> - **v0.2 is still policy-layer containment, not OS-level containment.** A process with sufficient operator privilege could still escape the sandbox. Boundary enforcement is by Python policy plus subprocess parameters (`cwd`, `env`, `timeout`, `shell=False`), not by the kernel.
> - **Agents become real only as bounded worker processes executing approved work orders in sandbox copies.** A role label in YAML is not an agent. A subprocess that ran an admitted command, in a sandbox, under a minimal environment, with a captured manifest, is.

---

## 1. Purpose

This document defines the v0.2 upgrade of the Real Agent Runtime. v0.1 established the local process boundary: admission, sandbox, command policy, filesystem policy, manifest, and refusal mode. v0.1 was dry-run only — the runtime classified commands but did not invoke them. v0.2 closes the gap between classifier and process: an allowlisted command is now actually invoked, inside the sandbox copy, under a minimal environment, with a wall-clock timeout, and with stdout/stderr/exit_code/duration_ms/cwd captured into the per-run manifest.

v0.2 is bounded. It is the smallest possible upgrade from v0.1 that converts "would-execute" into "executed." It does not introduce autonomy, model calls, network access, persistent daemons, or any new authority. It does not modify v0.1 admission rules, v0.1 command-policy semantics, v0.1 filesystem-policy semantics, v0.1 manifest fields, or v0.1 refusal codes — those are imported verbatim. The only surface added is the v0.2 execute-mode allowlist (a strict superset of the v0.1 dry-run allowlist in the script-call dimension), the subprocess invocation function, the sandbox tree fingerprint, and the v0.2 self-check fixture suite.

The runtime remains governance-anchored. It refuses to admit any work order whose status, assignment, or scope fields are inconsistent with the rules in `WORKFORCE-EXECUTION-RUNTIME-v0.1.md`. It refuses any command outside the v0.2 execute allowlist. It refuses any write outside the sandbox or `reports/real_agent_runtime/`. It produces a manifest that records every attempted command, every blocked command, every executed command (with full output capture), every gate verdict, every fingerprint, and every policy violation, with an exit status of zero if and only if all admission, command-policy, filesystem-policy, and execution checks pass.

## 2. Difference Between v0.1 Dry-Run And v0.2 Execute Mode

| Property | v0.1 dry-run | v0.2 execute mode |
| --- | --- | --- |
| Admission | parses WO yaml; admits if approved/assigned + assigned_to matches + fields present | identical, plus optional `replay_mode` flag that admits a `closed` WO for forensic re-run |
| Command classification | `classify_command` against ALLOWED_COMMANDS | `classify_execute_command` against EXECUTE_ALLOWED_COMMANDS (script-call superset of v0.1) |
| Forbidden command patterns | v0.1 set | identical v0.1 set, unchanged |
| Sandbox | created on admission accept; deleted on exit | created on admission accept; deleted on exit |
| Subprocess invocation | NONE | `subprocess.run(argv, cwd=sandbox, env=minimal, timeout=…, shell=False)` |
| Output capture | none | stdout, stderr, exit_code, duration_ms, cwd, status, timed_out, error |
| Source-repo fingerprint | computed before/after for fingerprint-drift detection | identical, plus an additional sandbox tree fingerprint pre/post |
| Sandbox tree fingerprint | not computed | sha256 of sorted (relpath, file-sha256) tuples; before and after |
| Manifest fields | 16 v0.1 fields | 16 v0.1 fields + `mode`, `replay_mode`, `command_results`, `sandbox_fingerprint_before`, `sandbox_fingerprint_after`, `sandbox_files_changed`, `env_keys` |
| `mode` value | `"dry-run"` (default) | `"execute"` |
| Inclusion in `make ci` | excluded | excluded |
| New Makefile targets | (none beyond v0.1) | `real-agent-execute`, `real-agent-execute-check` |
| Timeout | n/a (dry-run did not invoke) | every command bounded by per-call `timeout`, hard cap `EXECUTE_TIMEOUT_HARD_CAP_S` |

The v0.1 surface is preserved unchanged. A v0.1 dry-run today produces a manifest whose v0.1 fields are byte-stable against the v0.1 manifest schema; the v0.2 fields default to empty/zero values that v0.1 readers may ignore.

## 3. What Becomes Real In v0.2

The single property v0.2 adds: an allowlisted command inside a sandbox copy is now *executed*, not merely *classified*. Concretely:

- An approved-and-assigned (or, under explicit replay mode, closed) work order is admitted under `canon_guardian-01`, `reviewer-01`, `builder-01`, or `release-01`.
- The repository is copied to `workforce/real_agents/sandboxes/real-agent-<run_id>-<temp>/` via `shutil.copytree` (with the v0.1 ignore filter that excludes `.venv`, `.git`, `__pycache__`, `.pytest_cache`, `.mypy_cache`, `node_modules`, plus the runtime's own sandbox/runs/reports directories).
- For each command from the work order's `required_gates` (or the operator's `--command` argument), `classify_execute_command` runs deny-first on the v0.1 forbidden-pattern set, then allowlist-second on `EXECUTE_ALLOWED_COMMANDS`. If the command is denied, no subprocess is spawned and a `command_blocked` policy violation is recorded.
- If the command is admitted, `subprocess.run(argv, cwd=sandbox_path, env=_minimal_env(), stdin=DEVNULL, stdout=PIPE, stderr=PIPE, timeout=<T>, shell=False, check=False)` is called. The runtime captures stdout (truncated to `EXECUTE_OUTPUT_BYTE_CAP` bytes), stderr (same cap), exit_code, duration_ms, cwd, status (`ok` / `nonzero_exit` / `timed_out` / `error`), and the truncation flags.
- The sandbox is fingerprinted before and after the command run. Any added/modified/removed file is recorded in `sandbox_files_changed`.
- The source repository is fingerprinted before and after the entire run. Any drift records a `repo_fingerprint_drift` policy violation; the v0.2 invariant is that source repo fingerprint must be byte-identical pre/post.
- The sandbox is deleted unless `--preserve-sandbox` was passed. The manifest is the durable record.

This is what becomes real: a single bounded subprocess invocation per command, captured to a manifest, run inside a sandbox copy. Nothing else.

## 4. What Remains Not Real

- **Autonomy.** The runtime never selects what to run. Commands come from the work order's `required_gates` or from the operator's explicit `--command` argument. There is no planner, no model, no policy proposer.
- **Background processing.** No daemon, no scheduler, no event loop. Each invocation is a single-shot CLI command that exits.
- **Network access.** No `urllib.request`, no `socket.connect` to remote hosts, no HTTP, no SSH. The minimal environment does not propagate proxy variables. Forbidden command patterns include `curl`, `wget`, `ssh`, `scp`, `http://`, `https://`.
- **Model calls.** No LLM, no classifier, no embedding service, no RPC.
- **Secret access.** The runtime does not read `.env` files, `~/.aws/`, `~/.ssh/`, credentials.json, or any other secret store. The minimal environment passes only PATH, LC_ALL=C, LANG=C, and (when explicitly required) PYTHONPATH.
- **Kernel isolation.** No `unshare`, no `chroot`, no Docker, no Firecracker, no namespace, no jail.
- **Cryptographic attestation.** Manifests are plain JSON. They are not signed. An attacker with write access to `workforce/real_agents/runs/` can edit a manifest after the fact.
- **Hardware-rooted identity.** Identities are strings in a Python dict; they are not bound to any TPM, key, or enclave.
- **Resource limits beyond wall-clock.** The runtime does not bound memory, CPU, file-descriptor count, or process count. It bounds time only.
- **Anti-replay across runs.** Two runs of the same work order produce two manifests; neither chains to the other.
- **Inclusion in `make ci`.** v0.2's targets remain opt-in.

These are the same boundary lines v0.1 drew, kept where v0.1 left them.

## 5. Work Order Admission

Admission semantics are inherited verbatim from `REAL-AGENT-RUNTIME-v0.1.md` §6, with one bounded extension: an explicit `replay_mode` flag.

The v0.1 admission rule set (applied in order, first-match denies):

1. `unknown_agent_identity`
2. `missing_required_field` (work_order_id, status)
3. `status_not_admissible` (status not in identity's `allowed_statuses`)
4. `assigned_to_mismatch` (empty or wrong identity)
5. `missing_allowed_files`
6. `missing_forbidden_files`

In v0.2 execute mode, the rule set is unchanged. The optional `replay_mode=True` parameter (CLI flag `--replay`) admits a single bounded exception: when the only refusal would be `status_not_admissible` AND the WO's status is exactly `"closed"`, admission is re-evaluated as if status were `"approved"`. Every other refusal still applies. The manifest records `replay_mode: true` so the audit trail makes the bypass explicit. Replay mode is a forensic re-run capability, not a closure-undo capability: the work order's lifecycle remains terminated and the action log is not appended.

The four v0.1 identities (`canon_guardian-01`, `reviewer-01`, `builder-01`, `release-01`) and their per-identity `allowed_statuses`, `default_denied_paths`, `allowed_commands`, and `forbidden_commands` are preserved unchanged. The execute-mode allowlist (§8) is a separate, broader allowlist that applies to v0.2 execute mode only; it does not modify the v0.1 dry-run allowlist.

## 6. Subprocess Execution Boundary

Every v0.2 subprocess invocation is constrained by the following parameters:

- **Library.** `subprocess.run` from the Python standard library. No third-party process manager. No `os.exec*`, no `os.spawn*`, no `os.popen`.
- **Argument form.** List form (`argv`) only. `shell=False` is mandatory. No string command line is passed to the shell. The single transformation v0.2 applies is replacing a leading `.venv/bin/python` token with the absolute path to `<repo>/.venv/bin/python` if it exists, else `sys.executable` — to keep the command portable across machines whose source repo may or may not ship a venv.
- **Working directory.** `cwd=<sandbox_path>`. The subprocess runs with the sandbox copy as its current working directory. Relative script paths (e.g., `tools/check_no_pseudocode.py`) resolve against the sandbox, never against the canonical repository.
- **Standard input.** `stdin=subprocess.DEVNULL`. The subprocess cannot read from the operator's terminal.
- **Standard output / standard error.** Captured via `stdout=subprocess.PIPE` / `stderr=subprocess.PIPE`. Both streams are truncated at `EXECUTE_OUTPUT_BYTE_CAP` (64 KiB) bytes; truncation is recorded as `stdout_truncated` / `stderr_truncated` in the manifest entry.
- **Timeout.** Every call passes a `timeout=<float seconds>` argument. The default is `EXECUTE_TIMEOUT_DEFAULT_S` (60.0 s). The hard cap is `EXECUTE_TIMEOUT_HARD_CAP_S` (300.0 s). On `subprocess.TimeoutExpired`, the manifest entry's `status` is `timed_out`, `timed_out: true`, `exit_code: null`, and any partial output is captured.
- **Exit handling.** `check=False`. The runtime never raises on non-zero exit; it records the exit code. Whether a non-zero exit is a policy violation is the orchestrator's decision (gate failures escalate; non-gate failures don't).
- **Process tree.** No `Popen.wait` polling; no manual `kill` signaling beyond what `subprocess.run` already does on timeout. No shell expansion, no globbing, no environment substitution beyond what `argv` provides directly.

The boundary is not a kernel boundary. It is a Python-policy boundary plus a subprocess-parameter boundary. A subprocess that escapes its `cwd` (e.g., by reading via absolute paths) is not prevented by this layer; it is bounded by the command policy (§8), which is the only authoritative scope check for what can run.

## 7. Sandbox Boundary

A sandbox is a fresh per-run directory copy of the canonical repository, created via `shutil.copytree(REPO_ROOT, sandbox_path, ignore=…)` with the v0.1 ignore filter unchanged: `.venv`, `venv`, `.git`, `__pycache__`, `.pytest_cache`, `.mypy_cache`, `node_modules`, plus the runtime's own `workforce/real_agents/sandboxes/`, `workforce/real_agents/runs/`, and `reports/real_agent_runtime/` subtrees.

v0.2 adds two new fingerprint operations against the sandbox:

- **`tree_fingerprint(sandbox_path)` before execution.** Walks the sandbox tree, computes per-file sha256, and produces an aggregate sha256 over sorted `(relpath \\x00 file_sha256 \\x00)` tuples. Recorded in the manifest as `sandbox_fingerprint_before`. The same per-file map is retained in memory for diffing.
- **`tree_fingerprint(sandbox_path)` after execution.** Same operation. Recorded as `sandbox_fingerprint_after`. The diff against the before-map produces `sandbox_files_changed` (added + modified + removed, sorted alphabetically).

Sandboxes are isolated per run. No two runs share a sandbox. A run that mutates the sandbox does not mutate the canonical repository because the sandbox is a copy, not a reference. v0.2's invariant is the same v0.1 invariant: the source repository fingerprint (computed via `repo_fingerprint(REPO_ROOT)` over the v0.1 fixed file set: `SPEC.md`, `STATUS-REGISTRY.md`, `ARTIFACTS.md`, `CONFORMANCE.md`, `Makefile`, `tools/check_workforce.py`, `tools/check_no_pseudocode.py`) MUST be byte-identical pre and post execution. Any drift records a `repo_fingerprint_drift` policy violation.

The fingerprint walk skips `.git`, `.venv`, `venv`, `__pycache__`, `.pytest_cache`, `.mypy_cache`, `node_modules`, the runtime's own sandbox / runs directories, and `reports/real_agent_runtime/`. This is so that running `make real-agent-check` inside the sandbox (which writes `reports/real_agent_runtime/real_agent_runtime_v0.1.{md,json}` to the sandbox's report tree) does not register as a policy violation — those output paths are explicitly recognized as runtime-internal output, not arbitrary writes.

## 8. Command Policy

Command policy in v0.2 has the same two-stage shape as v0.1: forbidden-pattern deny-first, then allowlist-match.

**Forbidden patterns (deny-first; identical to v0.1):**

```
sudo, curl, wget, ssh, scp, git push, git reset --hard, git clean,
rm -rf, chmod, chown, open<space>, http://, https://
```

A command whose text contains any of these patterns is blocked, regardless of any other property, with reason `matches forbidden pattern '<P>'`. No subprocess is spawned.

**v0.2 execute-mode allowlist (`EXECUTE_ALLOWED_COMMANDS`):**

```
pwd
ls
find
cat
.venv/bin/python tools/check_no_pseudocode.py
.venv/bin/python tools/check_workforce.py
.venv/bin/python tools/real_agent_runtime.py check
make no-pseudocode
make workforce-check
make real-agent-check
```

A command not blocked by the forbidden-pattern stage is admitted only if it matches an entry in this allowlist. Match means exact equality or starts-with the allowed entry followed by a space (e.g., `find . -name '*.md'` matches `find`, `make no-pseudocode -j 1` matches `make no-pseudocode`). A command that fails both stages is recorded in the manifest's `commands_blocked` list with the failing reason and contributes a `command_blocked` entry to `policy_violations`.

The v0.2 allowlist is a script-call superset of the v0.1 dry-run allowlist (`pwd`, `ls`, `find`, `cat`, `python3`, `.venv/bin/python`, `make no-pseudocode`, `make workforce-check`). v0.2 adds three explicit script-call forms (`.venv/bin/python tools/check_no_pseudocode.py`, `.venv/bin/python tools/check_workforce.py`, `.venv/bin/python tools/real_agent_runtime.py check`) and one new gate (`make real-agent-check`). It does NOT include `python3` or `.venv/bin/python` as bare entries — bare interpreter invocations could run arbitrary scripts, so they are dropped from execute mode. The v0.1 dry-run allowlist remains unchanged for v0.1 dry-run callers.

`make ci` is intentionally NOT in the v0.2 allowlist. v0.2's targets are not added to `make ci`. A future hardening cycle may evaluate whether to extend the allowlist or include the runtime in CI; v0.2 does neither.

## 9. Filesystem Policy

Filesystem policy is unchanged from v0.1. `classify_read` and `classify_write` retain their v0.1 semantics:

**Reads:** denied if the path matches the work order's `forbidden_files` (fnmatch glob) or the identity's `default_denied_paths` (prefix match); admitted otherwise.

**Writes:** denied if the path is outside the sandbox path AND outside `reports/real_agent_runtime/`; denied if the path matches `forbidden_files`; admitted only if the path matches `allowed_files`; otherwise denied with `write target not in allowed_files`.

v0.2 adds tree-level fingerprint enforcement on top of these per-path classifiers:

- **Sandbox change recording.** `sandbox_files_changed` is computed from the diff of the before/after sandbox fingerprints. Every change that occurred during the run is enumerated by relative path. The runtime does not retroactively re-classify each changed path against `allowed_files` (the per-path classifier already governed any write the runtime performed); the change set is the audit trail of what subprocess execution did.
- **Source-repo invariance.** `repo_fingerprint_before == repo_fingerprint_after` is the v0.2 invariant on the canonical repository. Any drift records a `repo_fingerprint_drift` policy violation. Subprocesses run with `cwd=sandbox_path`, so this invariant should hold by construction; the fingerprint check is the runtime's belt-and-suspenders verification.

The asymmetry between read (default-allow within scope) and write (default-deny without explicit allow) is preserved.

## 10. Environment Policy

The minimal environment passed to `subprocess.run` contains exactly:

- `PATH` — inherited from the parent process so common executables (`python3`, `make`, system utilities) resolve. The parent's PATH is the only inherited variable.
- `LC_ALL=C` — pins locale to C so output is deterministic and ASCII-clean.
- `LANG=C` — same, for tools that read LANG instead of LC_ALL.
- `PYTHONPATH` — set ONLY when explicitly required by a caller (current execute callers do not require it). Default is unset.

Nothing else is passed. Specifically, the following are NOT propagated: `HOME`, `USER`, `SHELL`, `SHLVL`, `PWD`, `TMPDIR`, `TERM`, `OLDPWD`, `DISPLAY`, `EDITOR`, `VISUAL`, `XDG_*`, `SSH_*`, `AWS_*`, `GCP_*`, `OPENAI_*`, `ANTHROPIC_*`, `GITHUB_*`, `NPM_*`, `PIP_*`, `PROXY_*`, `HTTP_PROXY`, `HTTPS_PROXY`, `NO_PROXY`, anything else in the operator's shell environment.

The manifest records the keys (not the values) of the minimal environment in `env_keys`. Recording values would risk leaking PATH-embedded tokens; recording keys lets a reviewer verify the minimal-env property without exposing any secret.

This is not isolation. A subprocess could compute its own environment by reading `/proc/<pid>/environ` of another process, or by spawning a shell that re-reads `~/.bashrc`. v0.2 does not prevent that. v0.2 prevents only the runtime from passing additional environment variables to its own subprocess. That is the policy boundary; the kernel boundary is future enforcement (§16).

## 11. Manifest Requirements

A v0.2 execute-mode manifest contains all 16 v0.1 fields (per `REAL-AGENT-RUNTIME-v0.1.md` §11) plus the following v0.2 extensions:

| Field | Type | Meaning |
| --- | --- | --- |
| `mode` | string | `"dry-run"` (v0.1) or `"execute"` (v0.2) |
| `replay_mode` | bool | `true` if admission used the closed-WO replay flag |
| `command_results` | list of dicts | one entry per attempted command (allowed or blocked) |
| `sandbox_fingerprint_before` | `sha256:<hex>` | aggregate sha256 of the sandbox tree before execution |
| `sandbox_fingerprint_after` | `sha256:<hex>` | aggregate sha256 after execution |
| `sandbox_files_changed` | list of relpaths | union of added + modified + removed sandbox paths |
| `env_keys` | list of strings | sorted keys of the minimal env (no values) |

**`command_results` entry shape:**

| Key | Type | Meaning |
| --- | --- | --- |
| `command` | string | the original command text |
| `argv` | list of strings | resolved argv passed to subprocess.run (empty for blocked) |
| `cwd` | string | absolute sandbox path |
| `env_keys` | list of strings | minimal env keys |
| `timeout_s` | float | wall-clock cap for this call |
| `status` | string | `"ok"`, `"nonzero_exit"`, `"timed_out"`, `"error"`, or `"blocked"` |
| `exit_code` | int or null | subprocess return code (null for blocked / timed_out / error) |
| `stdout` | string | captured stdout, decoded utf-8 (replace), truncated to 64 KiB |
| `stdout_truncated` | bool | true if stdout exceeded the cap |
| `stderr` | string | same shape as stdout |
| `stderr_truncated` | bool | true if stderr exceeded the cap |
| `duration_ms` | int | wall-clock duration in milliseconds |
| `timed_out` | bool | true if the call exceeded `timeout_s` |
| `error` | string or null | failure reason for `error` / `blocked` / `timed_out`; null otherwise |
| `timestamp_start` | ISO-8601 UTC | start of the call |
| `timestamp_end` | ISO-8601 UTC | end of the call |

The manifest is JSON, sorted by key, indented two spaces. It is human-readable and machine-parseable. v0.2 does not yet enforce a manifest schema validator; the candidate hardening work order R-8 from `REAL-AGENT-RUNTIME-v0.1.md` §16 remains open and now applies to the v0.2 schema as well.

## 12. Timeout Requirements

Every subprocess call passes `timeout=<seconds>` to `subprocess.run`. The runtime applies three layers of bound:

1. **Per-call timeout.** The default is `EXECUTE_TIMEOUT_DEFAULT_S = 60.0` seconds. The CLI accepts `--timeout <float>` to override per call.
2. **Hard cap.** `EXECUTE_TIMEOUT_HARD_CAP_S = 300.0` seconds. The runtime clamps any caller-supplied timeout to `min(max(timeout, 0.001), 300.0)`. A caller cannot opt out of the cap.
3. **Floor.** The runtime clamps any caller-supplied timeout to at least `0.001` seconds. A timeout of zero (or negative) would make `subprocess.run` reject the call; the floor prevents that error class.

On `subprocess.TimeoutExpired`:

- The subprocess is killed by `subprocess.run` (SIGTERM, then SIGKILL after a short grace per Python's implementation).
- The manifest entry's `status` is `"timed_out"`, `timed_out: true`, `exit_code: null`, `error: "command exceeded <T>s wall-clock cap"`.
- Partial stdout / stderr are captured up to the moment of the kill, truncated to the byte cap.
- A `command_timed_out` policy-violation entry is added when the timed-out command was not also a declared gate (gate timeouts are recorded under `gate_failed` instead). Either way, `exit_status = 1` because `policy_violations` is non-empty.

The runtime tests its own timeout behavior in the v0.2 self-check fixture suite (case `command_timeout_recorded`).

Timeouts are wall-clock only. The runtime does not bound CPU time, memory, or process count. Future hardening (R-5 in `REAL-AGENT-RUNTIME-v0.1.md` §16) addresses those.

## 13. Failure Modes

The runtime fails closed in the following cases. Each produces `exit_status = 1` and a recorded `policy_violations` entry.

| Failure mode | Source | Manifest record |
| --- | --- | --- |
| Unknown agent identity | CLI / API | `policy_violations: [{code: unknown_agent_identity}]` |
| Missing required WO field | Admission | `policy_violations: [{code: missing_required_field}]` |
| WO status not admissible | Admission | `policy_violations: [{code: status_not_admissible}]` (replay mode admits closed only) |
| `assigned_to` mismatch | Admission | `policy_violations: [{code: assigned_to_mismatch}]` |
| Missing `allowed_files` | Admission | `policy_violations: [{code: missing_allowed_files}]` |
| Missing `forbidden_files` | Admission | `policy_violations: [{code: missing_forbidden_files}]` |
| Forbidden command pattern matched | Command policy (deny-first) | `commands_blocked: [{...}]` + `policy_violations: [{code: command_blocked}]`; status `"blocked"`; no subprocess spawned |
| Command not in execute allowlist | Command policy | same shape |
| Required gate non-zero exit | Execute | `policy_violations: [{code: gate_failed, command, reason}]`; gate appears in `gates_failed` |
| Required gate timed out | Execute | `gates_failed` + `policy_violations: [{code: gate_failed, command, reason="status=timed_out exit_code=None"}]` |
| Non-gate command timed out | Execute | `policy_violations: [{code: command_timed_out, command, reason}]` |
| Non-gate command subprocess error | Execute | `policy_violations: [{code: command_error, command, reason}]` |
| Source-repo fingerprint drift | Post-execute fingerprint | `policy_violations: [{code: repo_fingerprint_drift, reason}]` |
| Self-check fixture mismatch | `execute-check` | non-zero exit; failed cases enumerated in stdout |

The runtime never fails open. Any unexpected condition that the runtime cannot classify produces a Python exception that surfaces to the operator with traceback; the CLI does not swallow exceptions silently.

## 14. Security Non-Guarantees

The same v0.1 security non-guarantees still apply (`REAL-AGENT-RUNTIME-v0.1.md` §14). v0.2 narrows none of them. Specifically v0.2 does NOT yet provide:

- **OS-level sandboxing.** The sandbox is a directory copy. A subprocess with sufficient privilege could read or write outside the sandbox via absolute paths.
- **Process isolation.** The subprocess runs in the operator's user account; any privilege the operator has, the subprocess inherits.
- **Network isolation.** v0.2 forbids network commands by allowlist absence; it does not prevent a subprocess that *was* allowlisted from opening a socket programmatically (though every current allowlist entry is a non-network operation).
- **Cryptographic attestation.** Manifests are unsigned JSON. A post-hoc edit is detectable only by manual review.
- **Hash-chained manifests.** Manifests are independent.
- **Hardware-rooted identity.** Identities are strings.
- **Memory / CPU / FD / process-count limits.** Only wall-clock time is bounded.
- **Anti-replay across runs.** Two manifests of the same WO are both valid records.
- **Audit-chain integrity across runs.** No chain links one manifest to the next.

v0.2 narrows exactly one v0.1 enforcement gap: it converts "the runtime classifies but does not invoke" into "the runtime classifies and invokes under bounded subprocess parameters." Every other v0.1 gap remains.

## 15. Required Tests

The v0.2 self-check fixture suite (`run_execute_self_check`, exposed via `make real-agent-execute-check`) covers the ten cases below. All ten MUST pass at v0.2 closure time and at every subsequent gate run.

1. **`execute_allowed_command_succeeds`** — a `pwd` command admitted, executed, exit_code=0, stdout/stderr/duration_ms/cwd captured, source repo unchanged.
2. **`forbidden_command_blocked_before_subprocess`** — `curl https://example.com`, `git push origin main`, `rm -rf /` all classified as blocked; `argv` is empty for each (no subprocess spawned); `commands_blocked` length 3; source repo unchanged.
3. **`command_timeout_recorded`** — `make no-pseudocode` with `timeout=0.001` produces `status="timed_out"`, `timed_out=true`, `exit_code=null`; source repo unchanged.
4. **`wrong_agent_identity_refused`** — fixture with `assigned_to: release-01`, attempted under `builder-01`, refused with `assigned_to_mismatch`.
5. **`drafted_work_order_refused`** — fixture with `status: drafted`, refused with `status_not_admissible`.
6. **`closed_refused_unless_replay_mode`** — fixture with `status: closed`. Without `replay_mode`: refused with `status_not_admissible`. With `replay_mode=True`: admitted, executed `pwd`, exit_code=0; manifest's `replay_mode` field is `true`.
7. **`missing_allowed_files_refused`** — fixture without `allowed_files`, refused with `missing_allowed_files`.
8. **`missing_forbidden_files_refused`** — fixture without `forbidden_files`, refused with `missing_forbidden_files`.
9. **`source_repo_unchanged_after_execute`** — `pwd` and `ls` executed, `repo_fingerprint_before == repo_fingerprint_after`, both equal to a fingerprint computed by the test harness independently of the manifest.
10. **`manifest_records_stdout_stderr_exit_duration_cwd`** — `pwd` executed, manifest's first command_results entry contains all five required keys with correct types and values; `cwd` equals the manifest's `sandbox_path`.

The test harness writes per-run manifests to `workforce/real_agents/runs/` (each fixture invocation produces one manifest) and a v0.2 report to `reports/real_agent_runtime/real_agent_runtime_v0.2.{md,json}`. Sandbox cleanup is automatic for all ten cases.

## 16. Future OS Isolation

The boundary v0.2 establishes is policy-layer. The next runtime version (R-2 in `REAL-AGENT-RUNTIME-v0.1.md` §16, now retargeted to v0.3+) would migrate to OS-level isolation. Candidate approaches, in increasing strength:

- **Process group + setrlimit.** Wrap the subprocess in `os.setsid` plus `resource.setrlimit` for memory, CPU time, file-descriptor count, address-space size. Cheap; portable to macOS and Linux. Does not isolate filesystem or network.
- **macOS sandbox-exec / Linux seccomp + Landlock / OpenBSD pledge.** Use the host OS's process-confinement primitive to restrict syscalls and filesystem reach. Strong; portable across one OS at a time.
- **User namespaces (Linux only).** `unshare(CLONE_NEWUSER | CLONE_NEWNS | CLONE_NEWNET | CLONE_NEWIPC | CLONE_NEWUTS | CLONE_NEWPID)` for full process namespacing. Strong; Linux-specific.
- **Container.** Bind-mount the sandbox into a minimal container (e.g., `chroot` + `pivot_root` + namespaced kernel). Strongest portable; requires container runtime.
- **Microvm.** Firecracker / cloud-hypervisor with a snapshotted root filesystem. Strongest possible; requires KVM and a bootable image.

None of these is authorized by this document. Each requires its own drafted, approved, and assigned governance work order under `AGENT-GOVERNANCE-WORKFORCE-v0.1.md` and `WORKFORCE-HARDENING-v0.2.md` (or v0.3+).

The v0.2 → v0.3 migration also opens new candidate work items: a manifest schema validator (`tools/check_real_agent_manifests.py`, `R-8` retargeted), cross-validation between `tools/check_workforce.py` and the runtime (`R-6`), an adversarial pressure suite for execute mode (`R-7`), hash-chained manifests (`R-4`), signed manifests under per-identity keys (`R-3`), and resource limits (`R-5`). v0.2 closes none of these; it converts dry-run into real subprocess and stops there.

## 17. Final Law

The runtime is bounded by the following ten law statements. They are this document's terminal commitments; everything above is implementation.

**L-1. v0.2 creates real local subprocess execution.** A previously dry-run-only runtime now invokes admitted commands via `subprocess.run` inside a sandbox copy, under a minimal environment, with a bounded wall-clock timeout, and with stdout / stderr / exit_code / duration_ms / cwd captured into the per-run manifest. The class of artifact a v0.2 manifest is — a record of work that actually occurred — differs from a v0.1 dry-run manifest, which was a record of work that was admitted but not invoked.

**L-2. v0.2 does not create autonomous AI planning.** The runtime executes only commands sourced from the work order's `required_gates` or from an explicit operator `--command` argument. There is no proposer, no model, no scheduler, no policy generator, no autonomous step selection. Autonomy remains out of scope.

**L-3. v0.2 does not create background agents.** The runtime is a one-shot CLI. Each invocation admits, sandboxes, runs, captures, fingerprints, and exits. There is no daemon, no event loop, no resident process, no scheduled task installed.

**L-4. v0.2 does not provide kernel-level isolation.** The sandbox is `shutil.copytree`. A subprocess with sufficient OS privilege could escape the sandbox path. Network isolation is by allowlist absence, not by namespace. Resource limits beyond wall-clock time are not enforced. OS-level confinement is future enforcement (§16).

**L-5. v0.2 is still policy-layer containment, not OS-level containment.** Boundary enforcement is by Python policy (admission, command policy, filesystem policy) plus subprocess parameters (`cwd`, `env`, `timeout`, `shell=False`, `stdin=DEVNULL`). It is not enforced by the kernel. A reviewer who reads the v0.2 manifests can verify policy compliance; a reviewer who needs kernel-grade evidence still has none.

**L-6. Agents become real only as bounded worker processes executing approved work orders in sandbox copies.** A role label in YAML is not an agent. A v0.1 dry-run manifest is the *boundary specification* of an agent. A v0.2 execute manifest is the agent: a real subprocess that ran, in a sandbox, under an admitted work order, with its output captured. Anything less is governance metadata; anything more (autonomy, persistence, model integration) is out of v0.2 scope.

**L-7. v0.2 preserves every v0.1 refusal behavior.** No v0.1 admission rule, no v0.1 command-policy verdict, no v0.1 filesystem-policy verdict, no v0.1 manifest field, no v0.1 refusal code is weakened. v0.2's contribution is strictly additive in code (new functions, new constants, new manifest fields, new self-check cases) and strictly preserving in semantics. A v0.1 dry-run today produces the same admission verdicts and the same v0.1-shaped manifest fields as before.

**L-8. v0.2 fails closed.** Any unknown identity, missing field, inadmissible status, mismatched assignment, missing allowed/forbidden_files list, blocked command, gate non-zero exit, gate timeout, non-gate timeout, subprocess error, or source-repo fingerprint drift produces `exit_status = 1` and a recorded `policy_violations` entry. Silent success is forbidden; partial admission is forbidden; uncaught exceptions surface to the operator.

**L-9. v0.2 is not added to `make ci`.** `make real-agent-execute-check` is opt-in. `make real-agent-check` and `make real-agent-dry-run` from v0.1 also remain opt-in. A future hardening cycle may evaluate inclusion in `make ci`; v0.2 explicitly does not.

**L-10. The runtime's manifest is the per-run audit-trail anchor.** Every command attempted, every block, every policy verdict, every executed subprocess (with full stdout / stderr / exit_code / duration / cwd capture), every gate verdict, every fingerprint pre/post, every sandbox file change, and every refusal code is recorded. Replay continuity per `REPLAY-LAW-v0.1.md` requires that an outside reviewer can reconstruct the run from the manifest alone — for v0.2 that means reconstructing not just admission but also what commands actually ran, with what exit codes, in what wall-clock duration, against what sandbox state.

These ten law statements are the runtime's normative commitments at v0.2. They name what is now real (bounded subprocess execution), what is still not real (autonomy, background processing, kernel isolation), preserve every v0.1 boundary, and establish the smallest local-process surface on which a future hardening cycle can build OS-level containment.

---

**End of REAL AGENT RUNTIME v0.2.**
