# RESOURCE LIMIT RUNTIME v0.1
## Hard-Bounded Resource Enforcement for Isolated Executor Runs

**Status:** v0.1 — operational specification, normative for the bounded-resource surface in `tools/resource_limit_runtime.py` and the `reports/resource_limit_runtime/` tree. The runtime adds wall-clock-grounded process-tree containment, file-descriptor caps, child-process caps, output caps, sandbox-disk caps, command-count caps, and best-effort memory caps on top of the `OS-ISOLATION-RUNTIME-v0.1.md` kernel-isolation layer. It does not introduce any new policy. It does not weaken any v0.1 / v0.2 admission, command, filesystem, or isolation policy. It does not add networking, daemons, retries, or model calls.

**Companion documents:** `OS-ISOLATION-RUNTIME-v0.1.md` (kernel isolation base), `REAL-AGENT-RUNTIME-v0.2.md` (executor base), `REAL-AGENT-RUNTIME-v0.1.md`, `PROPOSER-RUNTIME-v0.1.md`, `REVIEW-GATE-RUNTIME-v0.1.md`, `PIPELINE-RUNTIME-v0.1.md`.

> **Core thesis.** The `OS-ISOLATION-RUNTIME-v0.1.md` runtime delivered "isolated but resource-unbounded": the kernel said no to forbidden syscalls, but a permitted syscall could exhaust CPU, memory, file descriptors, child processes, or output bandwidth without bound. The v0.1 Resource Limit Runtime closes that gap by wrapping every isolated subprocess in `os.setsid()` plus `resource.setrlimit()` calls in a `preexec_fn`, by killing the entire process group on timeout via `os.killpg(SIGKILL)`, by capping captured stdout / stderr at deterministic byte limits, by walking the sandbox post-execution to detect disk overruns, and by refusing pre-execution any batch whose command count exceeds the per-run cap.

> **Explicitly stated.**
>
> - **Governance determines admissibility.** (proposer / reviewer / executor classifier — unchanged)
> - **Kernel isolation constrains scope.** (`OS-ISOLATION-RUNTIME-v0.1.md` — unchanged)
> - **Resource limits constrain survivability.** (this document)

---

## 1. Purpose

After `OS-ISOLATION-RUNTIME-v0.1.md`, an isolated subprocess could not write outside its sandbox, could not reach the network, could not launch apps, and could not exec a binary outside the per-run allowlist. It *could*, however:

- spin a permitted binary on a CPU until the wall-clock timeout fired (waste compute)
- allocate hundreds of gigabytes of address space inside its allowed binary (exhaust memory)
- open thousands of file descriptors against allowed paths (exhaust the kernel fd table for the user)
- emit megabytes of stdout that the harness would dutifully capture into a manifest (exhaust disk via the manifest itself)
- write a 100 GB file inside its sandbox (fill the disk through the allowed write path)
- be passed a list of 1000 commands and execute them in sequence (turn a single approved batch into a long-running session)

This document defines v0.1 of the Resource Limit Runtime: the smallest possible addition that bounds every one of those vectors with a `resource.setrlimit()` call, a process-group kill, a deterministic byte cap, a post-execution sandbox-size walk, or a pre-execution command-count check. Stdlib only. No root. No external dependencies. No persistence beyond per-run manifests.

## 2. Architecture

```
work order → proposer → review → executor admission
                                       │
                                       ▼
                              classify_execute_command   (v0.2 policy — unchanged)
                                       │
                                       ▼
                              os_isolation_runtime
                              .generate_profile_*()      (kernel profile — unchanged)
                                       │
                                       ▼
                              subprocess.Popen(
                                argv = sandbox-exec wrapper + target,
                                preexec_fn = setsid + setrlimit*
                              )                          (THIS DOC)
                                       │
                                       ▼
                              communicate(timeout=…)
                                       │
                                       ├─ TimeoutExpired → killpg(pgid, SIGKILL); record process_tree_killed
                                       │
                                       ▼
                              measure_sandbox_size()     (THIS DOC)
                              record resource_violations (THIS DOC)
                                       │
                                       ▼
                              bounded manifest
```

The classifier still fires first. The kernel profile is still the second wall. This document adds a third wall — the kernel-imposed resource ceilings — and a wall-clock-grounded process-tree kill mechanism on top.

## 3. What Becomes Real In v0.1

The following bounds are now applied to every `execute_command_bounded()` call:

- **CPU time.** `RLIMIT_CPU` is set in `preexec_fn`. A child that exceeds the soft limit receives `SIGXCPU`; exceeding the hard limit is `SIGKILL`.
- **Address space.** `RLIMIT_AS` is *attempted* (best-effort; macOS Tahoe rejects finite values for `RLIMIT_AS` from unprivileged callers — see §10.5). Where the kernel does not enforce, the runtime captures peak RSS via `getrusage(RUSAGE_CHILDREN)` post-execution and records a `memory_overrun` violation if the limit was exceeded.
- **File descriptors.** `RLIMIT_NOFILE` is set in `preexec_fn`. Subsequent `open()` past the cap returns `EMFILE`.
- **Child processes.** `RLIMIT_NPROC` is set in `preexec_fn` to a value below the calling user's current process count. Any subsequent `fork()` returns `EAGAIN`.
- **Process-tree termination.** `os.setsid()` runs in `preexec_fn`; the wrapped subprocess is the leader of a new session/process group. On `subprocess.TimeoutExpired`, the runtime calls `os.killpg(pgid, SIGKILL)` to terminate every member of the group.
- **Stdout / stderr byte cap.** Captured streams are truncated at deterministic byte limits (`stdout_limit_bytes`, `stderr_limit_bytes`); the truncated bytes are sha256-hashed for replay-stability.
- **Sandbox disk usage.** After execution, `os.walk()` over the sandbox sums file sizes; any total above `sandbox_size_limit_bytes` adds a `sandbox_size_overrun` violation.
- **Command count cap.** A list of commands passed to `execute_commands_bounded()` whose length exceeds `command_count_limit` is rejected pre-execution with code `command_count_overflow`. The cap defaults to 3 (matching the proposer / reviewer cap).

## 4. What Remains Not Real

- **Memory enforcement on macOS.** macOS Tahoe (26.x) rejects unprivileged finite `RLIMIT_AS` values. The runtime records this honestly: the `memory_limit_applied` field is `false` when setrlimit failed, and post-execution `ru_maxrss` is compared against the requested limit to record a `memory_overrun` violation. Hard pre-allocation refusal would require `containerization` or `setrlimit` from a privileged context.
- **Disk-write rate limits.** A command can write at any rate inside its sandbox; only the *total* size at completion is checked.
- **Network bandwidth.** Networking is denied at the kernel layer; bandwidth limits are not relevant.
- **Cgroups / containerization.** Linux `cgroups` (v1 or v2) and macOS containerization are not used. Future runtimes may layer them in.
- **Cross-host attestation.** The runtime trusts the local kernel.
- **Daemons, schedulers, background loops, `make ci` inclusion.** v0.1 is opt-in.

## 5. Constraints

| Constraint | Enforcement |
| --- | --- |
| Single command per `execute_command_bounded` call | One argv list per invocation |
| At most `command_count_limit` commands per `execute_commands_bounded` call | Pre-execution cap; rejection produces a refusal-coded manifest |
| Deny-first policy preserved | `classify_execute_command` runs before kernel isolation runs before resource limits |
| Kernel isolation preserved | The bounded run uses `os_isolation_runtime`'s profile generator and `sandbox-exec` wrapper |
| No new networking | `(deny network*)` from the underlying profile is unchanged |
| No daemon, no scheduler | Module is single-shot |
| No persistence beyond per-run manifests | Manifests under `reports/resource_limit_runtime/runs/`; profiles via the os-isolation profile cache |
| Truncation is deterministic | Captured streams are truncated at exactly `*_limit_bytes`; the sha256 of the truncated bytes is recorded for replay-stable comparison |
| Process group is terminated, not just the leader | `os.setsid()` in preexec; `os.killpg(pgid, SIGKILL)` on timeout |

## 6. Default Limits

| Field | Default | Rationale |
| --- | --- | --- |
| `cpu_limit_seconds` | `10` | Most allowed binaries finish in <1s; 10s is a generous ceiling that still bites a runaway loop |
| `memory_limit_bytes` | `512 * 1024 * 1024` (512 MiB) | Best-effort; enforced strictly on Linux, post-hoc detected on macOS |
| `fd_limit` | `64` | Above the ~10 fds Python's interpreter uses at steady state, well below the kernel default of 256–1024 |
| `process_limit` | `100` | Below the typical user's existing process count; any `fork()` fails immediately with `EAGAIN` |
| `stdout_limit_bytes` | `65 536` (64 KiB) | Matches `EXECUTE_OUTPUT_BYTE_CAP` from `REAL-AGENT-RUNTIME-v0.2.md` |
| `stderr_limit_bytes` | `65 536` (64 KiB) | Same |
| `sandbox_size_limit_bytes` | `52 428 800` (50 MiB) | Above what a manifest-shaped run normally produces, well below disk pressure |
| `command_count_limit` | `3` | Matches the proposer / reviewer cap |
| `wall_clock_timeout_seconds` | `60` | Above CPU limit, below the 5-minute hard cap of `REAL-AGENT-RUNTIME-v0.2.md` |

These defaults are CLI- and self-check-overridable via the `ResourceLimits` dataclass.

## 7. Manifest Schema (Per-Run Result)

Every bounded run produces a result dict with the v0.1 OS-isolation fields *plus* the following:

| Field | Type | Meaning |
| --- | --- | --- |
| `cpu_limit_seconds` | int | Configured CPU time cap |
| `memory_limit_bytes` | int | Configured address-space cap |
| `fd_limit` | int | Configured fd cap |
| `process_limit` | int | Configured fork cap |
| `stdout_limit_bytes` | int | Stdout capture cap |
| `stderr_limit_bytes` | int | Stderr capture cap |
| `sandbox_size_limit_bytes` | int | Per-run sandbox disk cap |
| `command_count_limit` | int | Pre-execution batch cap |
| `process_tree_killed` | bool | `true` iff `killpg(pgid, SIGKILL)` was invoked on timeout |
| `stdout_truncated` | bool | `true` iff captured stdout exceeded `stdout_limit_bytes` |
| `stderr_truncated` | bool | `true` iff captured stderr exceeded `stderr_limit_bytes` |
| `stdout_hash` | string | sha256 of the (possibly truncated) captured stdout bytes |
| `stderr_hash` | string | sha256 of the (possibly truncated) captured stderr bytes |
| `sandbox_size_bytes` | int | Total bytes under the sandbox subpath at completion |
| `peak_rss_bytes` | int | `ru_maxrss` for the child (bytes on macOS, normalized from KiB on Linux) |
| `rlimits_applied` | object | Per-rlimit `{cpu: bool, memory: bool, fd: bool, nproc: bool}` indicating which `setrlimit` calls succeeded |
| `resource_violations` | list of strings | Violation codes raised: `memory_overrun`, `sandbox_size_overrun`, `cpu_time_exhausted`, `command_count_overflow` |

## 8. Self-Check Fixtures

The runtime self-check fixture suite (`run_self_check`, exposed via `make resource-limit-check`) covers the twelve cases below.

1. **`allowed_pwd_succeeds`** — `execute_command_bounded("pwd", sandbox)` returns `status="ok"`, `exit_code=0`, all manifest resource fields populated, `resource_violations=[]`.
2. **`stdout_flood_truncates_deterministically`** — A python -c command emitting `"a" * 100000` bytes with `stdout_limit_bytes=65536` produces exactly 65 536 bytes of captured stdout, `stdout_truncated=true`, deterministic `stdout_hash`.
3. **`sleep_timeout_kills_process_group`** — `/bin/sleep 5` under `wall_clock_timeout_seconds=0.5` returns `status="timed_out"`, `process_tree_killed=true`, `duration_ms ∈ [400, 5000)`.
4. **`nested_child_must_not_survive_parent_death`** — `/bin/sh -c '/bin/sleep 60 & echo $! >&2 ; wait'` with elevated `process_limit` and shell-extended profile, then short timeout. After kill, the inner sleep PID (parsed from stderr) is verified dead via `os.kill(pid, 0)` raising `ProcessLookupError`.
5. **`fd_exhaustion_rejected`** — A python command opening 100 files in the sandbox with `fd_limit=32` returns nonzero exit; stderr contains an `OSError` / `EMFILE` marker.
6. **`memory_exhaustion_handled`** — A python command allocating 256 MiB with `memory_limit_bytes=64 MiB`. On Linux: child fails with `MemoryError`. On macOS: `RLIMIT_AS` setrlimit fails (recorded as `memory_limit_applied=false`); `peak_rss_bytes` exceeds the limit; `memory_overrun` violation is recorded.
7. **`fork_attempt_rejected`** — A python command calling `os.fork()` with `process_limit=100` (below user's process count) returns nonzero exit; stderr contains `BlockingIOError` / `Resource temporarily unavailable`.
8. **`excessive_command_count_rejected_pre_exec`** — `execute_commands_bounded([cmd] * 4, …, command_count_limit=3)` returns a refusal manifest with `final_status="rejected_pre_exec"`, code `command_count_overflow`, and zero subprocesses spawned.
9. **`sandbox_size_over_limit_detected`** — A python command writing 2 MiB to the sandbox under `sandbox_size_limit_bytes=1 MiB` causes `sandbox_size_bytes ≥ 2 MiB`, `resource_violations` containing `sandbox_size_overrun`.
10. **`repo_fingerprint_unchanged`** — running fixture 1 leaves the protocol-canon `repo_fingerprint(REPO_ROOT)` byte-identical pre/post.
11. **`manifest_resource_fields_populated`** — fixture 1's result dict carries all fields from §7.
12. **`deterministic_truncation_hashes_stable`** — running fixture 2 twice produces byte-identical `stdout_hash` values despite distinct timestamps.

## 9. Bounded-Runtime Law

> **Governance determines admissibility. Kernel isolation constrains scope. Resource limits constrain survivability.**

The runtime claims exactly one new property over `OS-ISOLATION-RUNTIME-v0.1.md`: an isolated, governed subprocess can no longer consume unbounded CPU, memory, file descriptors, child processes, output bandwidth, sandbox disk, or batch length. Even on macOS where `RLIMIT_AS` is unprivileged-unenforceable, the runtime detects and reports the overrun honestly, so an auditor reading the manifest can see whether each limit was kernel-enforced or post-hoc-detected.

## 10. Required Analysis

### 10.1 What is now resource-bounded

- CPU time, via `RLIMIT_CPU` (kernel-enforced on both macOS and Linux).
- File descriptor count, via `RLIMIT_NOFILE` (kernel-enforced on both).
- Child process count, via `RLIMIT_NPROC` (kernel-enforced on both — the user's existing process count exceeds the cap, so any `fork()` fails with `EAGAIN`).
- Process-tree termination on timeout, via `os.setsid()` + `os.killpg(SIGKILL)`.
- Captured stdout / stderr byte length, via deterministic truncation at the `*_limit_bytes` boundary plus sha256 of the truncated bytes.
- Sandbox disk usage, via `os.walk()` post-execution.
- Batch command count, via pre-execution length check.
- Memory address space (Linux only, kernel-enforced via `RLIMIT_AS`); macOS post-hoc detected via `getrusage(RUSAGE_CHILDREN).ru_maxrss`.

### 10.2 Which attacks now fail mechanically

- **CPU spin.** A loop in a permitted binary terminates after `cpu_limit_seconds` of CPU time (kernel-enforced).
- **Fork bomb.** First `fork()` fails with `EAGAIN`. Subsequent attempts fail. The bomb produces zero offspring.
- **Fd exhaustion.** First `open()` past the cap fails with `EMFILE`. The subprocess cannot starve the kernel fd table.
- **Stdout flood.** Captured output is truncated at exactly `stdout_limit_bytes`. The remainder is discarded; the manifest records `stdout_truncated=true` and a sha256 of the truncated bytes for replay-stability.
- **Sandbox disk fill.** A command writing N gigabytes of files inside its sandbox is detected post-execution; the run is recorded with a `sandbox_size_overrun` violation. The disk is filled, but the manifest tells the truth and a future hardening can refuse to keep the artifacts.
- **Long-running batch.** A list of more than `command_count_limit` commands is refused before any subprocess is spawned. Zero kernel resources consumed.
- **Orphan child.** `os.setsid()` makes every spawned subprocess a process-group leader; `os.killpg(SIGKILL)` on timeout takes down the entire descendant tree.

### 10.3 Difference between timeout-only vs true bounded execution

A timeout-only executor (v0.2) had a single dimension of bound: wall-clock. A wedge of attacks fit underneath it:

- A 9.99-second-long program could allocate 100 GiB of memory and exit cleanly within timeout.
- A 9.99-second-long program could fork 10 000 children that detach from the parent and survive timeout.
- A 9.99-second-long program could emit 5 GiB of stdout that the harness captured into a manifest.
- A 9.99-second-long program could open 100 000 file descriptors and starve the user's fd table.

Each of those is now refused by an independent rlimit:

- Memory (best-effort on macOS): `RLIMIT_AS` + `getrusage` post-check.
- Forks: `RLIMIT_NPROC` + `setsid` + `killpg`.
- Stdout: deterministic byte cap + truncated-bytes sha256.
- Fds: `RLIMIT_NOFILE`.

A "bounded" executor refuses *survivability* attacks even when *admissibility* and *kernel isolation* would have admitted the command. That is the point of this layer.

### 10.4 What still prevents *"fully autonomous governed agents"*

Even with admission + isolation + bounding, several conditions remain unmet for the phrase *"fully autonomous governed agents"* to be technically defensible:

1. **Memory enforcement on macOS is best-effort.** `RLIMIT_AS` is unprivileged-unenforceable on macOS Tahoe. A rogue command can allocate beyond the limit; the runtime detects post-hoc but does not prevent.
2. **CPU and fd limits are per-process, not per-batch.** A `command_count_limit=3` run can consume `3 × cpu_limit_seconds` of CPU and `3 × fd_limit` cumulative fds. Per-batch limits are not yet enforced.
3. **`ru_maxrss` is reported across all reaped children.** The runtime trusts that one bounded run is in flight at a time; concurrent bounded runs would conflate their RSS readings.
4. **Disk overrun is detected, not prevented.** The bytes were written before the runtime noticed.
5. **No quota on the manifest itself.** A clever subprocess that exits quickly could induce many manifest writes via repeated invocation.
6. **No CPU isolation across cores.** A bounded run can pin a core; nothing prevents it.
7. **Reviewer chaining is single-identity.** A defensible "fully governed" claim probably requires Class-C-style quorum.
8. **Network egress is denied at syscall time but not attested.** The manifest does not record "no network call attempted."
9. **Sandbox-exec is deprecated.** Any long-term defensible claim must move off the deprecated substrate.
10. **Side channels remain.** Process timing, scheduler observation, page-fault patterns — none addressed.

### 10.5 Remaining kernel/isolation gaps

- **macOS `RLIMIT_AS` is not enforced** for unprivileged setrlimit. v0.1 records `memory_limit_applied=false` honestly on macOS.
- **The blanket `(allow mach-lookup)`** in the underlying isolation profile is still unconstrained except for the `LaunchServices` family.
- **Read-side allowlist** is still broad (`file-read*`).
- **Resource-limits across exec boundaries** are inherited, but kernel has no atomic "set limits + exec" syscall guarantee against TOCTOU; a malicious binary could in principle race.
- **`setrlimit` itself can be reset upward** by a process that has the privilege, but our subprocess does not (it runs as the user, who can only lower hard limits). v0.1 is safe here.
- **Sandbox.kext / kernel sandbox bugs** would defeat the kernel-enforcement guarantees.

### 10.6 Whether the executor is now technically *"contained and bounded"*

The executor is now:

- **Admitted** by the proposer / reviewer / classifier chain (governance).
- **Isolated** by `sandbox-exec` profile (kernel scope).
- **Bounded** by `setrlimit` + process-group kill + truncation + post-walk (kernel survivability).

That is, on macOS Tahoe, the technically defensible claim is: *"contained at the kernel level, bounded at the kernel level except for memory which is bounded post-hoc."*

The phrase "bounded" is now defensible. The phrase "fully bounded" is not, on macOS, until either (a) the runtime moves to a substrate where memory rlimit is enforceable unprivileged, or (b) the runtime gains a way to refuse memory-exhausting runs pre-execution rather than detecting them post-hoc.

## 11. CLI

- `tools/resource_limit_runtime.py self-check` — run all twelve fixtures; refresh the runtime report at `reports/resource_limit_runtime/resource_limit_runtime_v0.1.{md,json}`. Exit 0 iff all twelve pass.
- `tools/resource_limit_runtime.py run-fixture` — run the canonical valid fixture (`pwd` under bounded isolation) and print the result for ad-hoc inspection.

The Makefile exposes two targets, neither in `make ci`:

- `make resource-limit-check` — invoke `self-check`.
- `make resource-limit-fixture` — invoke `run-fixture`.

## 12. Future Work

- **Pre-execution memory refusal.** Migrate to a substrate where `RLIMIT_AS` is enforced unprivileged (Linux containers, macOS containerization).
- **Per-batch (cumulative) caps.** Enforce CPU / fd / RSS at the batch level, not per-command.
- **Disk-write quota during execution.** Use `RLIMIT_FSIZE` to refuse the write at the syscall level, not detect post-execution.
- **Cgroups / containerization backend.** On Linux, route through `unshare` + `cgroup v2`. On macOS, evaluate `containerization` (Apple's WWDC 2024 framework).
- **Atomic admission + kernel + bounding policy DSL.** A single declarative file per work order that drives all three layers.

## 13. Final Law

**L-1. v0.1 adds hard bounded-resource enforcement to already-isolated, already-governed execution.**
**L-2. v0.1 does NOT create autonomy.**
**L-3. v0.1 does NOT weaken any deny-first policy.**
**L-4. v0.1 preserves every existing manifest field, every classifier verdict, every kernel-profile rule, every refusal code.**
**L-5. v0.1 produces a deterministic truncation hash for every captured stream.**
**L-6. v0.1 fails closed.** Memory limit unenforceable → still recorded; sandbox overrun → recorded; fork blocked → recorded; timeout → process group killed.
**L-7. v0.1 is not added to `make ci`.**
**L-8. Governance determines admissibility. Kernel isolation constrains scope. Resource limits constrain survivability.** This is the runtime's defining boundary.

---

**End of RESOURCE LIMIT RUNTIME v0.1.**
