# OS ISOLATION RUNTIME v0.1
## Kernel-Backed Containment for Executor Subprocesses on macOS via `sandbox-exec`

**Status:** v0.1 — operational specification, normative for the kernel-isolation surface in `tools/os_isolation_runtime.py` and the `reports/os_isolation_runtime/` tree. The runtime adds an OS-enforced confinement layer over an already-governed executor subprocess. It does not introduce any new policy. It does not replace, weaken, or bypass any v0.1 / v0.2 admission, command, or filesystem policy. It does not add networking, daemons, retries, or model calls. It adds exactly one new property: subprocesses now execute under a macOS sandbox profile that the kernel enforces, so that *even if the policy classifier is wrong, the kernel still says no*.

**Companion documents:** `REAL-AGENT-RUNTIME-v0.2.md` (executor base), `REAL-AGENT-RUNTIME-v0.1.md` (admission base), `PROPOSER-RUNTIME-v0.1.md`, `REVIEW-GATE-RUNTIME-v0.1.md`, `PIPELINE-RUNTIME-v0.1.md`, `FORBIDDEN-SURFACES-v0.1.md`, `VALIDATION-LAW-v0.1.md`, `REPLAY-LAW-v0.1.md`.

> **Core thesis.** The v0.2 executor relied on directory-copy "sandboxing" for filesystem containment and on the policy classifier for command containment. Both are policy-only — a kernel that respects neither would still let a misclassified command run unconstrained. The v0.1 OS Isolation Runtime closes that gap by wrapping every isolated subprocess in `/usr/bin/sandbox-exec` under a deterministically-generated, content-hashed profile that the macOS kernel evaluates on every syscall. The classifier still runs first; the kernel runs *also*.

> **Explicitly stated.**
>
> - **This does not create autonomy.**
> - **This adds kernel-backed containment to already-governed execution.**
> - **Governance determines admissibility; kernel isolation constrains damage radius.**

---

## 1. Purpose

The proposer/reviewer/executor stack established in earlier runtime documents is governance-complete: every subprocess invocation has a work-order admission, a deny-first command classifier, an allowlist verdict, a reviewer decision, and a manifest record. None of it is *kernel-backed*. A misclassified command, a smuggled allowlist entry, or a future hardening regression that loosens command policy would all execute uncontrolled subprocess on the host.

This document defines v0.1 of the OS Isolation Runtime: the smallest possible addition that places executor subprocesses under macOS kernel sandbox enforcement, while preserving every existing governance invariant. It targets the current machine (macOS 26.x). It uses only `/usr/bin/sandbox-exec` and the Python standard library. It does not require root, Docker, virtualization, external dependencies, or persistent daemons.

The priority is **containment over capability**. A minimally capable but kernel-contained executor is preferred over a more powerful uncontained one. Commands that are not on the per-run binary allowlist do not run, full stop, even if the policy classifier would have accepted them.

## 2. Architecture

```
work order → proposer → review gate → executor admission
                                            │
                                            ▼
                                    classify_execute_command   (v0.2 policy)
                                            │
                                            ├─ blocked → return without spawn
                                            │
                                            ▼
                                    generate sandbox profile   (this doc, §8)
                                    write profile to disk      (sha256-keyed)
                                            │
                                            ▼
                                    /usr/bin/sandbox-exec -f <profile> <argv>
                                            │
                                            ▼ kernel evaluates every syscall
                                    subprocess.run capture
                                            │
                                            ▼
                                    isolation-tagged manifest
```

The classifier still fires first. An admitted command is then wrapped under a profile generated from its target binary path and the per-run sandbox directory. The wrapper is exec'd via `subprocess.run` with the same minimal environment, the same timeout discipline, and the same stdout/stderr capture as v0.2 — plus an outer `/usr/bin/sandbox-exec -f <profile_path>` argv prefix that brings the kernel into the loop.

## 3. What Becomes Real In v0.1

The single property v0.1 adds: subprocesses now execute under a macOS sandbox profile that the kernel enforces.

- A per-run sandbox profile is generated from the target binary and the resolved per-run sandbox directory. The profile is deterministic (same inputs → same bytes) and content-hashed.
- The profile denies by default, allows process-exec **only** for the explicit target binary (and `/bin/bash` when `/bin/sh` is the target, for macOS variant routing), allows reads broadly (so dyld can resolve), denies all writes outside the sandbox subpath, denies the `LaunchServices` mach-lookup family (so `open -a <App>` cannot reach the app launcher), and denies `network*`.
- `/usr/bin/sandbox-exec -f <profile_path> <argv>` is the new outer wrapper for every isolated subprocess. The wrapper is invoked with the same stdin=DEVNULL, stdout/stderr=PIPE, cwd=sandbox, env=minimal, timeout, and shell=False discipline that v0.2 uses.
- The manifest record carries five new fields: `isolation_mode`, `sandbox_profile_hash`, `sandbox_profile_path`, `kernel_enforced`, `denied_syscalls`. Existing manifest fields (`stdout`, `stderr`, `exit_code`, `duration_ms`, `timed_out`, `cwd`, `env_keys`, `argv`, `command`, `timeout_s`, `timestamp_start`, `timestamp_end`) are preserved unchanged.

## 4. What Remains Not Real

- **No new authority.** The classifier remains the first line of defense. The reviewer remains the gate. The executor's existing admission is unchanged. Kernel isolation is a *second* line.
- **No process tree containment beyond the immediate target.** v0.1 denies `process-exec*` and explicitly allows only the target binary, so nested `exec` of other binaries is denied. It does *not* try to defeat fork-without-exec; on modern macOS, `posix_spawn` collapses fork+exec into a single operation that the binary allowlist already covers.
- **No CPU / memory / fd limits.** Resource limits beyond wall-clock timeout are deferred.
- **No replacement of the v0.2 dry-run / execute-mode runtime.** v0.2 remains as a backward-compatible path; v0.1 of os-isolation is a parallel, opt-in surface that future executor revisions will route through.
- **No daemon, no scheduler, no background loop, no `make ci` inclusion.** v0.1's targets are opt-in.
- **No network access, no model call.** The runtime cannot reach a remote host even if it wanted to.

## 5. Constraints

| Constraint | Enforcement |
| --- | --- |
| Single command per invocation | One argv list per `execute_command_isolated()` call |
| Deny-first policy preserved | `classify_execute_command` runs *before* sandbox-exec; classifier-rejected commands never reach the kernel layer |
| No new networking | Profile contains `(deny network*)`; module imports no HTTP / socket |
| No persistence beyond run + profile | Profiles are sha256-keyed under `reports/os_isolation_runtime/profiles/`; per-run manifests under `reports/os_isolation_runtime/runs/`; no state carried between invocations |
| No daemon, cron, or background loop | Module is single-shot; no `while True`; no scheduler registration |
| No model calls | No LLM, no embedding |
| Profile hash is deterministic | Same `(binary, sandbox_path)` → byte-identical profile → identical sha256 |
| Repo fingerprint invariance | The runtime never writes outside the per-run sandbox; the protocol-canon fingerprint (`SPEC.md`, `STATUS-REGISTRY.md`, `ARTIFACTS.md`, `CONFORMANCE.md`, `Makefile`, `tools/check_workforce.py`, `tools/check_no_pseudocode.py`) is byte-identical pre/post any isolated run |
| No new attack surface | The module imports only stdlib + `real_agent_runtime`'s already-tested classifier and fingerprint helpers |

## 6. Sandbox Profile

The profile generator emits the following deterministic content (sample for `binary="/bin/pwd"`, `sandbox_path="/tmp/sb"`):

```
(version 1)
(deny default)
(deny process-exec*)
(allow process-exec (literal "/bin/pwd"))
(allow mach-lookup)
(deny mach-lookup (global-name "com.apple.coreservices.launchservicesd"))
(deny mach-lookup (global-name "com.apple.lsd.mapdb"))
(deny mach-lookup (global-name "com.apple.lsd.modifydb"))
(deny mach-lookup (global-name "com.apple.lsd.openurls"))
(allow file-read*)
(allow file-read-metadata)
(deny file-write*)
(allow file-write* (subpath "/tmp/sb"))
(allow file-write-data (literal "/dev/null"))
(allow file-write-data (literal "/dev/dtracehelper"))
(allow sysctl-read)
(allow ipc-posix-shm)
(allow iokit-open)
(allow signal (target self))
(deny network*)
```

Variant routing: when `binary` is `/bin/sh` or `/bin/bash`, both `(allow process-exec (literal "/bin/sh"))` and `(allow process-exec (literal "/bin/bash"))` are emitted, because macOS rewrites `/bin/sh` to `/bin/bash` internally and the kernel checks the resolved variant.

## 7. Manifest Schema (Per-Run Result)

Every isolated run produces a result dict suitable for inclusion in an executor `RunManifest`'s `command_results` list. New fields (additive over v0.2):

| Field | Type | Meaning |
| --- | --- | --- |
| `isolation_mode` | string | `"sandbox-exec"` for v0.1; future modes (e.g., `"docker"`) will use other tags |
| `sandbox_profile_hash` | string | sha256 of the profile bytes; identical inputs → identical hash |
| `sandbox_profile_path` | string | absolute path to the profile file under `reports/os_isolation_runtime/profiles/` |
| `kernel_enforced` | bool | `true` iff the kernel actually saw the run; `false` only when the classifier blocked the command before sandbox-exec was invoked |
| `denied_syscalls` | list of strings | empty in v0.1 (sandbox-exec does not surface per-syscall denials in stdout/stderr); reserved for future modes |

The status code now also includes `"blocked_by_classifier"` for commands rejected before sandbox-exec was invoked. All other v0.2 status values (`ok`, `nonzero_exit`, `timed_out`, `error`, `blocked`) remain.

## 8. Self-Check Fixtures

The runtime self-check fixture suite (`run_self_check`, exposed via `make os-isolation-check`) covers the nine cases below. All nine MUST pass at v0.1 closure time.

1. **`allowed_pwd_command_succeeds_inside_isolation`** — `execute_command_isolated("pwd", sandbox)` returns `status="ok"`, `exit_code=0`, `kernel_enforced=true`, `isolation_mode="sandbox-exec"`, `sandbox_profile_hash` populated.
2. **`forbidden_curl_blocked_before_spawn`** — `execute_command_isolated("curl https://example.com", sandbox)` returns `status="blocked_by_classifier"`, `kernel_enforced=false`, `exit_code=null`. sandbox-exec is never invoked.
3. **`write_outside_sandbox_denied_by_kernel_policy`** — `execute_isolated_raw(["/usr/bin/touch", "/private/tmp/<random>"], sandbox)` returns nonzero exit; the target file does NOT exist on disk afterward.
4. **`open_calculator_app_denied`** — `execute_isolated_raw(["/usr/bin/open", "-a", "Calculator"], sandbox)` returns nonzero exit; LaunchServices mach-lookup is denied.
5. **`nested_subprocess_spawn_denied`** — `execute_isolated_raw(["/bin/sh", "-c", "/bin/ls /usr"], sandbox)` returns nonzero exit OR stderr contains `Operation not permitted`; the inner `/bin/ls` exec is blocked because `/bin/ls` is not on the per-run binary allowlist.
6. **`repo_fingerprint_unchanged`** — `repo_fingerprint(REPO_ROOT)` is byte-identical before and after fixture 1.
7. **`timeout_still_enforced`** — `execute_isolated_raw(["/bin/sleep", "5"], sandbox, timeout=0.5)` returns `status="timed_out"`, `timed_out=true`, `duration_ms >= 400`.
8. **`manifest_isolation_fields_populated`** — fixture 1's result dict carries `isolation_mode`, `sandbox_profile_hash`, `sandbox_profile_path` (and the path exists on disk), `kernel_enforced`, `denied_syscalls`.
9. **`sandbox_profile_hash_stable`** — `generate_profile("/bin/pwd", sandbox)` called twice produces byte-identical strings and identical sha256 hashes.

The harness writes per-run manifests to `reports/os_isolation_runtime/runs/`, profile files to `reports/os_isolation_runtime/profiles/`, and a self-check report at `reports/os_isolation_runtime/os_isolation_runtime_v0.1.{md,json}`.

## 9. Isolation Boundary Law

> **The kernel enforces the sandbox; the runtime enforces the policy. Governance determines admissibility; kernel isolation constrains damage radius.**

The runtime claims exactly one new property over v0.2: a misclassified, smuggled, or buggy-allowlisted command will still be denied at syscall time by the kernel. It does not claim to have removed the need for the classifier. It does not claim that approved commands are safe. It claims that *unapproved*, *misapproved*, or *post-approval-mutated* commands now have a second wall to cross.

## 10. Required Analysis

### 10.1 What is now kernel-enforced

- **Process-exec allowlist.** Only the explicit target binary (plus `/bin/bash` when `/bin/sh` is the target) may be exec'd. Every other `execve` returns `EPERM` from the kernel.
- **Filesystem write boundary.** Writes outside the resolved sandbox subpath (and `/dev/null`, `/dev/dtracehelper`) return `EPERM` from the kernel. The classifier's filesystem policy was advisory; this is enforced.
- **LaunchServices denial.** `mach-lookup` of `com.apple.coreservices.launchservicesd` (and the `lsd.mapdb` / `lsd.modifydb` / `lsd.openurls` family) is denied by the kernel, so `open -a <App>` cannot reach the app launcher.
- **Outbound networking.** `network*` is denied by the kernel; the classifier's `https://` / `curl` / `wget` deny set was a classifier check, this is a syscall check.
- **Default deny.** Any operation not explicitly allowed returns `EPERM`.

### 10.2 What is still only policy-enforced

- **Work-order admission.** `assigned_to == agent_id`, `status` validity, `allowed_files` / `forbidden_files` glob lists — all classifier-only.
- **Command allowlist.** `EXECUTE_ALLOWED_COMMANDS` matching (the v0.2 deny-first-then-allowlist) is still classifier-only at the *string* level. The kernel allowlist is at the *binary path* level after argv resolution, which is strictly finer-grained but a different surface.
- **Rationale, hash, reviewer decision.** Proposer / reviewer / pipeline gates are entirely policy-level.
- **Repo fingerprint invariance.** The protocol-canon fingerprint check is verified by the runtime, not the kernel.
- **Sandbox-internal write semantics.** The kernel allows any write *inside* the sandbox subpath; the work order's `allowed_files` glob is not consulted at syscall time.

### 10.3 What attacks now fail at OS level

- A misclassified or smuggled `/usr/bin/curl` (if it ever reached the executor) cannot complete: it cannot exec because `/usr/bin/curl` is not on the per-run binary allowlist *and* it cannot open a network socket because `network*` is denied.
- A command that tries to write outside the per-run sandbox (e.g., a `find -fprint /tmp/exfil` variant if such a thing reached the executor) fails: the kernel denies the write.
- A command that tries to launch another app via `/usr/bin/open` fails: LaunchServices is unreachable.
- A command that tries to spawn a child binary not on the allowlist (e.g., `/bin/sh -c '/bin/ls'` when only `/bin/sh` is allowed) fails at the inner `execve`.
- A command that tries to read a *device* not in the allowlist (e.g., `/dev/audio`, raw network interfaces) fails at `iokit-open` (selectively allowed) or at the implicit deny default.

### 10.4 What attacks still remain possible

- **In-sandbox harm.** Anything the target binary itself does *inside* the sandbox subpath is unrestricted by the kernel: it can fill the sandbox with garbage, write files of arbitrary names, create symlinks (subject to macOS symlink semantics).
- **Disclosure via stdout.** The target binary can read any file the profile permits (broad `file-read*`) and exfiltrate via stdout, which the harness captures and writes to a manifest. There is no read-side allowlist enforced by the kernel here. (See §10.6 for hardening.)
- **CPU exhaustion within timeout.** Until wall-clock timeout fires, the binary may fully utilize a CPU core.
- **Misuse of allowed mach services.** `(allow mach-lookup)` is broad; specific abusable services beyond the LaunchServices family are not individually denied. (See §10.6.)
- **Profile generation bugs.** A malformed profile string (e.g., a sandbox path with embedded quotes) could break the profile and either fail closed (sandbox-exec rejects) or, in worst case, fail open. v0.1 mitigates by accepting only resolved absolute paths from `Path.resolve()`, but the kernel-trusts-the-profile-text invariant remains a property of the profile generator's correctness.
- **Sandbox-exec deprecation.** Apple has marked `sandbox-exec` deprecated. It still works on macOS 26.x. Its long-term availability is not guaranteed; a future macOS may require Endpoint Security or containerization.
- **Side channels.** Process timing, scheduler observation, page-fault patterns — none of these are addressed.
- **Sandbox.kext bugs.** A kernel bug in the sandbox enforcement layer would defeat all of the above.

### 10.5 Why this is materially stronger than v0.2

v0.2 had two containment claims:

1. *"The subprocess runs in a sandbox directory."* True at the cwd level only. The kernel saw a normal process. A `cd /` (or any absolute path) sidestepped the sandbox.
2. *"The classifier denies forbidden patterns."* True at the *string-match* level only. A command that escaped the classifier ran with full user privileges.

v0.1 of OS Isolation:

- **Has the kernel as a co-enforcer.** Even if the classifier is wrong, the kernel says no.
- **Is binary-allowlist-keyed, not string-keyed.** The kernel does not look at the command string; it looks at the resolved binary path on `execve`. A future smuggling attack via classifier-string-confusion (e.g., shell-quoting tricks) is independently caught at the kernel layer because the resolved binary still has to match the profile.
- **Denies networking at syscall time, not just at command-string time.**
- **Denies app-launching at syscall time, not just at command-string time.**
- **Surfaces a content-hashed profile artifact.** The profile is now an audit object; a future replay can check whether the same profile was used.
- **Adds an explicit `kernel_enforced` flag to the manifest.** A reader can mechanically distinguish kernel-contained runs from policy-only runs.

### 10.6 Exact remaining gaps before *"real isolated governed agents"* becomes a technically defensible phrase

The phrase "real isolated governed agents" requires *all* of the following, none of which v0.1 fully delivers:

1. **Read-side allowlist enforced at syscall time.** Today the kernel allows broad reads. A future hardening must either narrow `file-read*` to a per-run subpath set, or move to Endpoint Security / containerization where read mediation is finer.
2. **Fine-grained `mach-lookup` allowlist.** Today the profile allows mach-lookup broadly with an explicit deny on the LaunchServices family. A complete profile must invert this: `(deny mach-lookup)` plus an explicit allow list of the small number of services dyld and libc actually require.
3. **Resource limits.** CPU time, memory, file-descriptor count, max child process count — all enforced by `setrlimit` or cgroups-equivalent. v0.1 has only wall-clock timeout.
4. **Containment of in-sandbox writes.** The work-order `allowed_files` glob list must be enforced at syscall time, not just at the policy layer. This requires either a much more elaborate sandbox profile per work order, or a userspace LSM-like layer.
5. **Replay of the profile.** A future runtime should re-run a recorded profile against the same command and verify the kernel reaches the same denial set. v0.1 records the profile and its hash, but does not yet diff or replay.
6. **Isolation that survives `sandbox-exec` deprecation.** A defensible long-term claim must work on a non-deprecated substrate: macOS Endpoint Security, Linux user namespaces, or `containerd`-based microVMs. v0.1 is macOS-only and uses a deprecated tool.
7. **Removal of the `(allow mach-lookup)` blanket.** Today this is the single largest unconstrained surface in the profile.
8. **Multi-reviewer admission.** Today one reviewer identity is sufficient. A defensible "governed agent" claim probably requires a Class-C-style quorum.
9. **Network egress proof.** Today networking is denied at syscall time, but the manifest does not include a "no network call attempted" proof. A future runtime should record attempted (and denied) network operations.
10. **Cross-host attestation.** The current runtime trusts that the host kernel has not been tampered with. A defensible claim requires either a TPM-backed attestation chain or a known-good substrate (e.g., Apple Silicon Secure Boot logs).

Until at least items 1, 2, 3, and 6 are addressed, "real isolated governed agents" is aspirational — v0.1 is a meaningful step, not a destination.

## 11. CLI

The runtime exposes two CLI verbs:

- `tools/os_isolation_runtime.py self-check` — run the nine self-check fixtures (§8); refresh the runtime report at `reports/os_isolation_runtime/os_isolation_runtime_v0.1.{md,json}`. Exit 0 iff all nine pass.
- `tools/os_isolation_runtime.py run-fixture` — run the canonical valid fixture (`pwd` under isolation) and print the result dict to stdout for ad-hoc inspection.

The Makefile exposes two targets, neither in `make ci`:

- `make os-isolation-check` — invoke `self-check`.
- `make os-isolation-fixture` — invoke `run-fixture`.

## 12. Future Work

- **Drop the blanket `(allow mach-lookup)`.** Replace with an explicit allow list of services dyld / libc require, deny everything else.
- **Per-work-order `allowed_files` enforcement at syscall time.** Generate per-WO profiles whose `(allow file-write*)` clauses match the WO's `allowed_files` globs.
- **Endpoint Security migration.** When Apple deprecates `sandbox-exec` for real, move the runtime to ES; the v0.1 profile semantics translate.
- **Linux backend.** Add `unshare` / `bwrap` paths so the runtime works on CI Linux runners.
- **Replay verification.** Re-run a recorded profile against a recorded argv and confirm the kernel reaches identical denial outcome.
- **Resource limits.** `setrlimit(RLIMIT_CPU, RLIMIT_AS, RLIMIT_NOFILE)` before exec.

## 13. Final Law

**L-1. v0.1 adds kernel-backed containment to already-governed execution.**
**L-2. v0.1 does NOT create autonomy.**
**L-3. v0.1 does NOT execute outside the classifier's deny-first verdict.**
**L-4. v0.1 preserves every v0.2 manifest field, every classifier verdict, and every refusal code.**
**L-5. v0.1 produces a deterministic content-hashed profile per run.**
**L-6. v0.1 fails closed.** Any sandbox-exec failure, any malformed profile, any kernel denial yields a non-zero exit and a refusal-coded manifest.
**L-7. v0.1 is not added to `make ci`.** Targets are opt-in.
**L-8. The kernel enforces the sandbox; the runtime enforces the policy. Governance determines admissibility; kernel isolation constrains damage radius.** This is the runtime's defining boundary.

---

**End of OS ISOLATION RUNTIME v0.1.**
