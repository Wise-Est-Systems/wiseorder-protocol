# WISEORDER SYSTEMS ARCHITECTURE v1
## Canonical Technical Architecture for the Governed Execution Stack

**Status:** v1 — descriptive systems-architecture specification. Normative documents (`SPEC.md`, the `*-RUNTIME-v0.1.md` family, `REAL-AGENT-RUNTIME-v0.2.md`, `REPLAY-LAW-v0.1.md`, `WORKFORCE-EXECUTION-RUNTIME-v0.1.md`, `AGENT-GOVERNANCE-WORKFORCE-v0.1.md`, `FORBIDDEN-SURFACES-v0.1.md`, `VALIDATION-LAW-v0.1.md`, `TRUST-LAW-v0.1.md`) govern in case of conflict. This document explains how those surfaces compose into a single governed-execution system. It introduces no new policy and weakens none.

**Scope of this document:** the *governed-execution* layer — work orders, proposers, the reviewer gate, the executor, the pipeline, kernel isolation, and bounded-resource enforcement. The parallel `intellagent_runtime/` cognition state-machine (Class A/B/C/D claim transitions over the WiseOrder kernel) is referenced only at the boundary.

**Audience:** systems engineers, security reviewers, replay auditors. Reader is assumed to be comfortable with Linux/macOS process model, syscall confinement, and deterministic-hash-anchored append-only records.

**Audit posture:** every major claim in this document is tagged with one of the following enforcement labels. The labels are not editorial; they bind reviewers to a specific layer at which a claim can be falsified.

| Label | Meaning |
| --- | --- |
| **[IMPLEMENTED]** | Code path exists in this repository, exercised by a passing self-check fixture, with a committed report under `reports/`. |
| **[PARTIALLY IMPLEMENTED]** | Code path exists for some inputs / platforms but not all; the gap is named explicitly. |
| **[POLICY-ONLY]** | Enforced by Python in this repository; not enforced by the host kernel. A privileged operator or buggy classifier could defeat it. |
| **[KERNEL-ENFORCED]** | Enforced by the host kernel via `sandbox-exec` profile or `setrlimit` on `execve`. Defeated only by a kernel bug in the relevant subsystem. |
| **[FUTURE WORK]** | Documented in a runtime spec's "Future Work" section; not authorized by any current work order; not present in code. |
| **[EXPLICITLY UNSUPPORTED]** | Stated as out-of-scope in a runtime spec's "What Remains Not Real" or "Security Non-Guarantees" section. Deliberately not built. |

Conformance to this document is conformance to the labels. A reader who finds an unlabeled claim has found a defect in this document; a reader who finds a label that misrepresents the underlying runtime spec has found a defect against the runtime spec, which governs.

---

## Table of contents

1. Why the system exists
2. Core thesis
3. System overview
4. Complete runtime architecture
5. Manifest, artifact, and report types
6. Governance model
7. State machine
8. Security model
9. Isolation model
10. Determinism model
11. Implemented vs unimplemented matrix
12. Explicit non-claims
13. Data flow and execution flow
14. Threat model
15. Future enforcement ladder
16. Diagrams
17. Appendices
18. What is actually real today

---

## 1. Why the system exists

The system exists to convert a single technical impossibility into a recoverable engineering problem.

The impossibility: a generative system whose execution produces effects on a host machine cannot, after the fact, be independently distinguished from an unrelated process that produced the same effects. Stated bluntly: stdout is not provenance, exit status is not authority, and a file modified by a prompt is indistinguishable from a file modified by a typo. Without a governed-execution envelope, every action a generative agent takes is, at audit time, an unrecorded incident.

Five concrete failure modes drive the design.

**1.1 Trust collapse on uninspectable execution.** A generative system invoking `subprocess.run` produces side effects whose authorization, scope, and intent are not recoverable from the artifact set the system leaves behind. An auditor reading a modified file, a written log line, or a modified working tree has no mechanical means to determine whether the change was within scope, was approved, or even occurred under an identity the operator authorized. Trust under this regime is testimonial — the operator says it happened that way, the auditor accepts. Testimonial trust does not survive operator turnover, contested incidents, or hostile review.

**1.2 Non-replayable behavior.** A generative system's outputs depend on prompts, sampling temperature, model weights, harness state, time, and any number of nondeterministic inputs. A run that "worked yesterday" may produce a different output today, and a different output is, for governance purposes, a different operation. Replay of "same inputs → same outputs" is not a property of generative cognition; it is a property a system must add by recording every byte that determined an action and excluding everything else.

**1.3 Absence of bounded governance.** Most generative systems, deployed against real machines, operate under three implicit grants the operator never made explicit: arbitrary file write, arbitrary subprocess spawn, arbitrary network egress. These grants are convenient and devastating. A bounded-governance system inverts the default: the only thing the runtime may do is the small, declared, allowlisted thing for which a work order exists. Everything else is refused, and the refusal is recorded.

**1.4 Inability to reconstruct execution legitimacy from the record alone.** An operation is *legitimate* if (a) it had explicit authorization, (b) it satisfied its declared scope, (c) it satisfied its declared gates, (d) it was reviewed against an out-of-band identity, and (e) it produced a record from which (a)–(d) can be mechanically re-checked. Most generative-execution systems satisfy (a) loosely, ignore (b)–(d), and produce a record that depends on operator memory. `REPLAY-LAW-v0.1.md` Principle 3 names the requirement directly: "the operational chain reconstructs from the record alone." Without it, governance was theatre.

**1.5 No primitive for "the system refused."** A generative system that fails silently — by returning empty output, by skipping a step, by approximating around a constraint — produces a result indistinguishable from one that succeeded. The system needs a primitive for *refusal*: a typed, recorded, hash-anchored event that a reviewer can read and that the runtime cannot suppress. `REAL-AGENT-RUNTIME-v0.2.md` §13 calls this *fail closed*: every refusal produces `exit_status = 1` and a recorded `policy_violations` entry. Silent success is forbidden.

Each failure mode in this section has a corresponding mechanism downstream:

| Failure mode | Mechanism |
| --- | --- |
| Trust collapse | per-run manifest with full subprocess capture (`REAL-AGENT-RUNTIME-v0.2.md` §11) |
| Non-replayable behavior | deterministic hashing of every artifact (`PROPOSER-RUNTIME-v0.1.md` §6, `REVIEW-GATE-RUNTIME-v0.1.md` §6, `PIPELINE-RUNTIME-v0.1.md` §6) |
| Absent bounded governance | deny-first command policy + execute allowlist (`REAL-AGENT-RUNTIME-v0.2.md` §8) |
| Unreconstructible legitimacy | append-only artifact tree under `reports/` + work-order lifecycle (`WORKFORCE-EXECUTION-RUNTIME-v0.1.md` §4) |
| No refusal primitive | refusal-coded manifests with `exit_status = 1` at every layer |

---

## 2. Core thesis

The system is built on six commitments. They are not aspirational; they are testable against the runtime specs and the committed self-check reports.

**2.1 Governance before execution.** Admission must complete before any subprocess is spawned. The order — work order → proposer → reviewer → executor — is structural, not advisory. There is no code path in `tools/pipeline_runtime.py` from the proposer to the executor that does not first pass through `review.decision == "approved"` (`PIPELINE-RUNTIME-v0.1.md` L-4). **[IMPLEMENTED]**

**2.2 Replayability over intelligence.** A bounded executor that produces a replayable record is preferred over a more capable executor whose record cannot be reconstructed. `REPLAY-LAW-v0.1.md` Principle 8 makes this absolute: replay is binary; partial replay is not replay. The system stores enough to reconstruct the operational chain from the record alone, and refuses any operation it could not record this way. **[IMPLEMENTED]** at the per-run level (proposer, review, executor, pipeline manifests), **[POLICY-ONLY]** for cross-run chaining (no manifest hash chain exists; `REAL-AGENT-RUNTIME-v0.2.md` §14: "manifests are independent").

**2.3 Determinism over claims.** Every artifact carries a deterministic hash computed over an audit-stable subset of its own content. Two runs of the same input produce byte-identical hashes (modulo a small, recorded-but-not-hashed envelope: `timestamp`, run identifiers). A claim that a record is genuine is only as strong as the hash, and the hash is only as strong as the canonicalization rules that produced it. **[IMPLEMENTED]** for proposer (`deterministic_hash`), reviewer (`review_hash`), pipeline (`pipeline_hash`), kernel-isolation profile (`sandbox_profile_hash`), and resource-limit truncation (`stdout_hash` / `stderr_hash`). **[NOT IMPLEMENTED]**: cryptographic signing of any of those hashes.

**2.4 Bounded authority.** No identity has open-ended permission. Each of the four executor identities (`canon_guardian-01`, `reviewer-01`, `builder-01`, `release-01`) has a per-identity `allowed_statuses`, `default_denied_paths`, `allowed_commands`, and `forbidden_commands` set in `IDENTITIES`. The proposer cannot widen scope; the reviewer cannot grant execution authority; the executor cannot select work. **[IMPLEMENTED]**

**2.5 Refusal is greater than silent failure.** Every layer of the stack treats a failed precondition as a typed, recorded, hash-anchored refusal — not as a soft warning, not as a silent skip, not as a fallback. The proposer raises 14 refusal codes (§7 of its runtime); the reviewer raises 13; the executor raises 14; the pipeline aggregates all of them. The runtime never fails open — any unexpected condition surfaces as a Python exception with traceback rather than a swallowed error. **[IMPLEMENTED]**

**2.6 Admissibility before capability.** A proposer that emits a candidate command is making an admissibility claim, not a capability claim. A reviewer that approves is making an admissibility claim, not a capability claim. The executor's own admission re-runs at execution time (`PIPELINE-RUNTIME-v0.1.md` §9: "reviewer approval is necessary but not sufficient; executor admission still governs execution"). Each upstream gate narrows the set of admissible operations; capability — what the operation actually does — is bounded only at the executor and only by the kernel. **[IMPLEMENTED]**

These six commitments compose. Removing any one collapses the system into a different class of artifact: an unbounded executor (drop 2.1), a non-auditable executor (drop 2.2), a forgeable executor (drop 2.3), an unbounded-authority executor (drop 2.4), a silent-failure executor (drop 2.5), or a capability-claim executor (drop 2.6). The architecture's load-bearing property is that all six hold simultaneously.

---

## 3. System overview

### 3.1 Stack position

```
                  reasoning
                      ↓
              ┌───────────────┐
              │   WiseOrder   │   ← protocol kernel (SPEC.md)
              └───────────────┘
                      ↓
       ┌────────────────────────────┐
       │   Intellagent Runtime v0.1  │   ← cognition state machine (out of scope here)
       └────────────────────────────┘
                      ↓
       ┌────────────────────────────────────────────────────────────────┐
       │   Governed-Execution Stack                                     │
       │   (this document)                                              │
       │                                                                │
       │   proposer → review gate → pipeline → executor → isolation →   │
       │                                                  resource cap  │
       └────────────────────────────────────────────────────────────────┘
                      ↓
       ┌────────────────────────────┐
       │   Winstack    │   WISEATA  │   ← proof-substrate implementations
       └────────────────────────────┘
                      ↓
                  execution systems
```

The protocol kernel (`SPEC.md`) defines what counts as a legitimate epistemic artifact (Class A/B/C/D, status registry, canonicalization, action governance). The Intellagent Runtime is a state-machine over those artifacts (claim transitions, audit memory, refusal store) — it shares the kernel laws with the governed-execution stack but its concerns are different: it commits *cognition* transitions; this stack governs *side effects*. The governed-execution stack converts an admitted work order into a bounded, isolated, resource-capped subprocess invocation whose record is replayable from the artifact set alone.

### 3.2 Components

| Component | Spec | Code | Reports |
| --- | --- | --- | --- |
| Work-order lifecycle | `WORKFORCE-EXECUTION-RUNTIME-v0.1.md` | `workforce/work_orders/`, `tools/check_workforce.py` | `workforce/reports/` |
| Proposer | `PROPOSER-RUNTIME-v0.1.md` | `tools/proposer_runtime.py` | `reports/proposer_runtime/` |
| Review gate | `REVIEW-GATE-RUNTIME-v0.1.md` | `tools/review_gate_runtime.py` | `reports/review_gate_runtime/` |
| Executor (dry-run / execute) | `REAL-AGENT-RUNTIME-v0.1.md`, `REAL-AGENT-RUNTIME-v0.2.md` | `tools/real_agent_runtime.py` | `reports/real_agent_runtime/`, `workforce/real_agents/runs/` |
| Pipeline | `PIPELINE-RUNTIME-v0.1.md` | `tools/pipeline_runtime.py` | `reports/pipeline_runtime/` |
| OS isolation | `OS-ISOLATION-RUNTIME-v0.1.md` | `tools/os_isolation_runtime.py` | `reports/os_isolation_runtime/` |
| Resource limits | `RESOURCE-LIMIT-RUNTIME-v0.1.md` | `tools/resource_limit_runtime.py` | `reports/resource_limit_runtime/` |

Each component is independently invokable and independently testable. The pipeline composes the first four; isolation and resource-limits are an opt-in wrapping for the executor's subprocess invocation. None of the six is on the default `make ci` path; all are explicitly opt-in (see §4.13).

### 3.3 Three concentric containment rings

The runtime stack expresses three concentric containment rings around an executed subprocess. Each ring fails closed independently of the others.

```
            ┌───────────────────────────────────────────────┐
            │  Ring 3: Resource ceiling                     │
            │  - RLIMIT_CPU                  KERNEL-ENFORCED │
            │  - RLIMIT_NOFILE               KERNEL-ENFORCED │
            │  - RLIMIT_NPROC                KERNEL-ENFORCED │
            │  - RLIMIT_AS                   PARTIAL (Linux only) │
            │  - setsid + killpg(SIGKILL)    KERNEL-ENFORCED │
            │  - stdout/stderr byte cap      POLICY-ONLY     │
            │  - sandbox disk overrun        POST-HOC POLICY │
            │   ┌─────────────────────────────────────────┐ │
            │   │  Ring 2: Kernel isolation profile        │ │
            │   │  - process-exec allowlist  KERNEL-ENF.    │ │
            │   │  - file-write outside sb   KERNEL-ENF.    │ │
            │   │  - LaunchServices deny     KERNEL-ENF.    │ │
            │   │  - network deny            KERNEL-ENF.    │ │
            │   │   ┌─────────────────────────────────────┐ │ │
            │   │   │  Ring 1: Policy classifier          │ │ │
            │   │   │  - identity admission   POLICY-ONLY │ │ │
            │   │   │  - allowlist match      POLICY-ONLY │ │ │
            │   │   │  - forbidden patterns   POLICY-ONLY │ │ │
            │   │   │  - allowed_files glob   POLICY-ONLY │ │ │
            │   │   │   ┌────────────────────────────────┐│ │ │
            │   │   │   │  Subprocess (cwd=sandbox copy) ││ │ │
            │   │   │   └────────────────────────────────┘│ │ │
            │   │   └─────────────────────────────────────┘ │ │
            │   └─────────────────────────────────────────┘ │
            └───────────────────────────────────────────────┘
```

Ring 1 governs *whether* the subprocess is allowed to run. It runs first, in Python, before any subprocess is spawned. Ring 2 governs *what syscalls* the subprocess may execute, evaluated by the macOS kernel on every relevant `execve`/`open`/`mach_lookup`/socket call. Ring 3 bounds the magnitude of damage a permitted syscall can cause: CPU time, address space, file-descriptor table, descendant process count, captured-output size, sandbox disk consumption, and per-batch command count.

A misclassification at Ring 1 does not defeat the system: Ring 2 still denies the syscall (`OS-ISOLATION-RUNTIME-v0.1.md` §10.5: "even if the classifier is wrong, the kernel says no"). A permitted-but-unbounded syscall at Ring 2 does not exhaust the host: Ring 3 caps consumption. The rings are designed to fail independently.

### 3.4 Replay chain

Every artifact in the stack is a node in a directed acyclic replay graph anchored to the work order:

```
work_order.yaml
    │
    ├──► proposal-<run_id>.json     deterministic_hash
    │         │
    │         ▼
    │      review-<run_id>.json     review_hash
    │         │
    │         ▼ (decision=approved)
    │      executor manifest         (run-id-keyed JSON in workforce/real_agents/runs/)
    │         │
    │         ▼
    └──► pipeline-<run_id>.json     pipeline_hash
```

Each downstream artifact references its upstream by path and re-derives the upstream's hash on read. A mutation at any point breaks the next-stage hash check. The replay chain is the per-run audit anchor; cross-run chaining (a hash chain linking pipeline N to pipeline N+1) is **[NOT IMPLEMENTED]**.

### 3.5 Repo fingerprint invariance

Every executor invocation computes `repo_fingerprint(REPO_ROOT)` before and after the run. The fingerprint is a sha256 over a fixed file set:

- `SPEC.md`
- `STATUS-REGISTRY.md`
- `ARTIFACTS.md`
- `CONFORMANCE.md`
- `Makefile`
- `tools/check_workforce.py`
- `tools/check_no_pseudocode.py`

(`REAL-AGENT-RUNTIME-v0.2.md` §7.) The runtime's invariant is byte-equality before and after every run. A drift records a `repo_fingerprint_drift` policy violation and forces `exit_status = 1`. This is the runtime's belt-and-suspenders check that the source repository's protocol-canon was not mutated by a subprocess that should have run only against its sandbox copy. **[IMPLEMENTED]**, **[POLICY-ONLY]** (the runtime computes it; the kernel does not enforce it).

### 3.6 Closure semantics

A work order *closes* when its lifecycle reaches the `closed` state under the rules in `WORKFORCE-EXECUTION-RUNTIME-v0.1.md` §4 + §20. Closure requires:

- a passing action log
- a passing self-verification block
- every required gate in `gates_passed`
- a reviewer agent finding
- a human-owner approval recorded in `status_history`

The runtime stack's contribution to closure is the executor manifest and the pipeline aggregate, both of which feed `gates_passed` evidence and provide the replay anchor. Closure itself is a governance event, not a runtime event — the runtime can produce a passing manifest and the work order may still not close (because a reviewer rejected the finding, or the human owner did not sign). **[IMPLEMENTED]** for runtime evidence; **[POLICY-ONLY]** for governance signature.

---

## 4. Complete runtime architecture

### 4.1 Identities

The stack defines five identity strings, each bound to a per-identity policy. Identities are not bound to any TPM, key, hardware enclave, or cryptographic credential — they are strings keyed into a Python dict (`REAL-AGENT-RUNTIME-v0.2.md` §14: "identities are strings"). **[POLICY-ONLY]**

| Identity | Role | Allowed statuses (admission) | Source |
| --- | --- | --- | --- |
| `canon_guardian-01` | proposer / executor | as defined in `IDENTITIES` | `REAL-AGENT-RUNTIME-v0.1.md` §6 |
| `reviewer-01` | proposer / executor | as defined in `IDENTITIES` | `REAL-AGENT-RUNTIME-v0.1.md` §6 |
| `builder-01` | proposer / executor | as defined in `IDENTITIES` | `REAL-AGENT-RUNTIME-v0.1.md` §6 |
| `release-01` | proposer / executor | as defined in `IDENTITIES` | `REAL-AGENT-RUNTIME-v0.1.md` §6 |
| `review-gate-01` | reviewer | n/a (no admission; consumes proposals) | `REVIEW-GATE-RUNTIME-v0.1.md` §6 |

The `review-gate-01` identity is operationally distinct from `reviewer-01`. `reviewer-01` is an executor identity that can run admitted commands; `review-gate-01` is the deterministic admission filter for proposer output. They are not interchangeable. **[IMPLEMENTED]**

A proposer instance and an executor instance MAY share an identity (e.g., a `canon_guardian-01` proposer and a `canon_guardian-01` executor), but the proposer's process and the executor's process are different invocations with no shared state. The architecture forbids any code path that lets a proposer call an executor without an out-of-band reviewer step (`PROPOSER-RUNTIME-v0.1.md` §9).

### 4.2 Scope: allowed_files, forbidden_files

Every work order declares two lists of paths (or globs):

- `allowed_files` — non-empty; the closed set the agent may read or write. An empty `allowed_files` is invalid.
- `forbidden_files` — non-empty; the open-ended deny list. Overrides `allowed_files` on overlap.

The runtime applies these via `classify_read` and `classify_write` (`REAL-AGENT-RUNTIME-v0.2.md` §9). Reads are default-allow within scope and deny on `forbidden_files` / `default_denied_paths`. Writes are default-deny: a path admitted only if it matches `allowed_files` AND does not match `forbidden_files` AND is inside the sandbox path or `reports/real_agent_runtime/`. **[POLICY-ONLY]**

**Standing forbidden paths** (always implicitly forbidden under `WORKFORCE-EXECUTION-RUNTIME-v0.1.md` §7): `SPEC.md`, `vectors/**`, `canonicalization/**`, `.github/workflows/**`, `Makefile`, and any file under `workforce/` other than the agent's own action log and assigned work order. A work order needing to touch any of these requires `human_approval_required: true` plus an attached approver record. **[POLICY-ONLY]**

### 4.3 Allowlists: deny-first then allowlist-second

Command policy is two-stage. Stage one is a deny-first match against `FORBIDDEN_COMMAND_PATTERNS`. Stage two is an allowlist match against either `ALLOWED_COMMANDS` (v0.1 dry-run) or `EXECUTE_ALLOWED_COMMANDS` (v0.2 execute mode). A command must clear stage one (no forbidden-pattern match) AND clear stage two (allowlist hit).

**FORBIDDEN_COMMAND_PATTERNS** (`REAL-AGENT-RUNTIME-v0.2.md` §8, identical to v0.1):

```
sudo, curl, wget, ssh, scp, git push, git reset --hard, git clean,
rm -rf, chmod, chown, open<space>, http://, https://
```

**EXECUTE_ALLOWED_COMMANDS** (`REAL-AGENT-RUNTIME-v0.2.md` §8):

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

Match semantics: exact equality OR starts-with the allowed entry followed by a space. `make no-pseudocode -j 1` matches `make no-pseudocode`; `find . -name '*.md'` matches `find`. The execute allowlist deliberately omits bare `python3` and `.venv/bin/python` — bare interpreter invocations could run arbitrary scripts. **[POLICY-ONLY]**

The proposer reuses the v0.2 allowlist verbatim (`PROPOSER-RUNTIME-v0.1.md` §3); the reviewer reuses both the deny set and the allowlist verbatim (`REVIEW-GATE-RUNTIME-v0.1.md` §3). No layer in the stack defines its own command policy; all four (proposer, reviewer, executor, pipeline) refer to the same constants.

### 4.4 Manifest generation (general)

Every layer emits one and only one manifest per invocation:

- proposer → `proposal-<run_id>.json` + `.md`
- reviewer → `review-<run_id>.json` + `.md`
- executor → run-id-keyed JSON under `workforce/real_agents/runs/`
- pipeline → `pipeline-<run_id>.json` + `.md`
- isolation → per-run JSON under `reports/os_isolation_runtime/runs/`
- resource-limit → per-run JSON under `reports/resource_limit_runtime/runs/`

All manifests are JSON, sorted by key, indented two spaces, UTF-8, trailing newline. None of them is signed. None of them is hash-chained to any other. A post-hoc edit by an operator with write access to `reports/` is detectable only by re-deriving the recorded hash — which is the audit reviewer's job. **[IMPLEMENTED]** for emission; **[NOT IMPLEMENTED]** for cryptographic anti-tamper.

### 4.5 Subprocess execution discipline

Every v0.2 execute-mode subprocess is invoked through a single function with the following parameters fixed at compile time (`REAL-AGENT-RUNTIME-v0.2.md` §6):

- `subprocess.run` from stdlib only; no third-party process manager
- `argv` list form; `shell=False` mandatory
- `cwd` = sandbox path
- `stdin = subprocess.DEVNULL`
- `stdout = subprocess.PIPE`, `stderr = subprocess.PIPE`
- `timeout = <bounded float>` (see §4.10)
- `check = False` (the runtime records the exit code; never raises)
- `env = _minimal_env()` — `PATH`, `LC_ALL=C`, `LANG=C`, optional `PYTHONPATH`; nothing else

Truncation: stdout and stderr are truncated at 64 KiB each (`EXECUTE_OUTPUT_BYTE_CAP`); truncation is recorded as `stdout_truncated` / `stderr_truncated`. The single `argv` rewriting the runtime performs is replacing a leading `.venv/bin/python` token with the absolute interpreter path. **[POLICY-ONLY]**

The bounded variant (`tools/resource_limit_runtime.py`) wraps the same `subprocess.run` in `subprocess.Popen` plus a `preexec_fn` that calls `os.setsid()` and `resource.setrlimit()` for each enforceable limit, then calls `Popen.communicate(timeout=…)`. On timeout it calls `os.killpg(pgid, SIGKILL)` to terminate every descendant. **[KERNEL-ENFORCED]** for the rlimits the platform supports (`RESOURCE-LIMIT-RUNTIME-v0.1.md` §10.1).

### 4.6 Sandbox lifecycle

A sandbox is a fresh per-run directory copy of the canonical repository, created via `shutil.copytree(REPO_ROOT, sandbox_path, ignore=…)`. The ignore filter excludes `.venv`, `venv`, `.git`, `__pycache__`, `.pytest_cache`, `.mypy_cache`, `node_modules`, plus the runtime's own `workforce/real_agents/sandboxes/`, `workforce/real_agents/runs/`, and `reports/real_agent_runtime/` subtrees. (`REAL-AGENT-RUNTIME-v0.2.md` §7.)

Sandboxes are isolated per run. No two runs share a sandbox. The sandbox is deleted on exit unless `--preserve-sandbox` was passed. The manifest (not the sandbox) is the durable record. **[POLICY-ONLY]** at the path level — the kernel enforces no relationship between the sandbox path and the subprocess; only the executor's `cwd=sandbox_path` and the kernel-isolation profile's `(allow file-write* (subpath sandbox_path))` rule keep the subprocess inside.

The sandbox is fingerprinted before and after execution. Each fingerprint is an aggregate sha256 over sorted `(relpath \x00 file_sha256 \x00)` tuples. The before/after diff yields `sandbox_files_changed` — the audit trail of what the subprocess actually wrote. **[IMPLEMENTED]**

### 4.7 Policy enforcement (Python layer)

`classify_execute_command(command_text)` runs deny-first against `FORBIDDEN_COMMAND_PATTERNS`, then allowlist-second against `EXECUTE_ALLOWED_COMMANDS`. Failure returns a structured rejection with a reason string. **[POLICY-ONLY]**

`classify_read(path)` and `classify_write(path)` apply work-order `forbidden_files`, identity `default_denied_paths`, and work-order `allowed_files` in the order specified by `REAL-AGENT-RUNTIME-v0.2.md` §9. **[POLICY-ONLY]**

These classifiers run *before* any subprocess is spawned. A blocked command results in `commands_blocked` populated, `argv` empty, and no `subprocess.run` invocation at all. The kernel-isolation layer (when enabled) is the second line; the classifier is the first.

### 4.8 Timeout enforcement

Three layers of timeout discipline (`REAL-AGENT-RUNTIME-v0.2.md` §12):

1. **Per-call timeout.** Default 60.0 s (`EXECUTE_TIMEOUT_DEFAULT_S`). Caller may override via `--timeout`.
2. **Hard cap.** 300.0 s (`EXECUTE_TIMEOUT_HARD_CAP_S`). The runtime clamps any caller-supplied timeout via `min(max(t, 0.001), 300.0)`. A caller cannot opt out.
3. **Floor.** 0.001 s. Prevents the `subprocess.run` zero-timeout error class.

On `subprocess.TimeoutExpired`:
- The subprocess is killed by `subprocess.run` (SIGTERM, then SIGKILL) — or, in the bounded variant, by `os.killpg(pgid, SIGKILL)` on the entire process group.
- Manifest entry: `status="timed_out"`, `timed_out=true`, `exit_code=null`, partial output captured up to the kill moment.
- Required-gate timeouts surface as `gate_failed` policy violations; non-gate timeouts surface as `command_timed_out` policy violations.

Timeouts are wall-clock only at the v0.2 layer. CPU time, memory, fd count, and process count are bounded only when the bounded-resource wrapper is invoked (§4.11). **[KERNEL-ENFORCED]** for the kill itself; **[POLICY-ONLY]** for the choice of timeout value.

### 4.9 Process-tree termination

The bounded-resource wrapper's `preexec_fn` calls `os.setsid()` to make the spawned subprocess the leader of a fresh session and process group. On `subprocess.TimeoutExpired` the wrapper calls `os.killpg(pgid, SIGKILL)` — terminating every descendant in the group, not just the immediate child. (`RESOURCE-LIMIT-RUNTIME-v0.1.md` §3 and fixture 4 `nested_child_must_not_survive_parent_death`.) **[KERNEL-ENFORCED]**

The unbounded v0.2 path (without the resource-limit wrapper) relies on `subprocess.run`'s default behavior — SIGTERM then SIGKILL of the immediate child only. A subprocess that has spawned descendants and detached them (orphan-style) under v0.2-only enforcement may survive timeout. The bounded wrapper closes that gap. **[PARTIALLY IMPLEMENTED]** — only when running through `tools/resource_limit_runtime.py`, not when running through `tools/real_agent_runtime.py` directly.

### 4.10 Kernel isolation

`OS-ISOLATION-RUNTIME-v0.1.md` defines the kernel-enforcement layer for macOS via `/usr/bin/sandbox-exec`. The runtime generates a deterministic profile keyed on `(target_binary, sandbox_path)`, writes it to `reports/os_isolation_runtime/profiles/<sha256>.sb`, and invokes `sandbox-exec -f <profile_path> <argv>` as the outer wrapper.

**Profile structure** (`OS-ISOLATION-RUNTIME-v0.1.md` §6, abbreviated):

- `(deny default)` — implicit deny of everything not explicitly allowed
- `(deny process-exec*)` — no `execve` of any binary
- `(allow process-exec (literal "<target>"))` — the explicit target binary only
- `(allow file-read*)` — broad reads (so dyld can resolve)
- `(deny file-write*)` then `(allow file-write* (subpath "<sandbox>"))` — writes only inside the sandbox
- `(allow file-write-data (literal "/dev/null"))`, `(allow file-write-data (literal "/dev/dtracehelper"))` — necessary kernel-side writes
- `(deny mach-lookup (global-name "com.apple.coreservices.launchservicesd"))` plus three other LaunchServices entries
- `(deny network*)` — no socket creation, bind, connect, listen
- `(allow sysctl-read)`, `(allow ipc-posix-shm)`, `(allow iokit-open)`, `(allow signal (target self))`, `(allow mach-lookup)` — operational allowances

Variant routing: when `target=/bin/sh` or `/bin/bash`, both literals are emitted because macOS internally rewrites `/bin/sh` to `/bin/bash` and the kernel checks the resolved variant. **[KERNEL-ENFORCED]**

The profile is content-hashed (sha256 of the bytes); the hash is recorded as `sandbox_profile_hash` in the manifest. Same `(target, sandbox)` produces identical profile bytes and identical hash (`OS-ISOLATION-RUNTIME-v0.1.md` fixture 9 `sandbox_profile_hash_stable`). **[IMPLEMENTED]**

Runtime policy vs kernel policy distinction (`OS-ISOLATION-RUNTIME-v0.1.md` §10.2):

- Kernel-enforced: process-exec allowlist, write boundary, LaunchServices denial, network denial, default deny.
- Policy-only (still): work-order admission (`assigned_to == agent_id`, status validity, `allowed_files`/`forbidden_files` glob), command allowlist string match, rationale presence, hash verification, reviewer decision, repo fingerprint invariance.

The asymmetry is deliberate. The kernel-isolation layer is a *second* line of defense after the policy classifier. It is not a replacement.

### 4.11 Resource-limit enforcement

`RESOURCE-LIMIT-RUNTIME-v0.1.md` defines the bounded-resource wrapper. It composes on top of OS isolation (which composes on top of the v0.2 executor). The wrapper applies the following bounds via `resource.setrlimit()` in a `preexec_fn`:

| Bound | Default | Mechanism | Status |
| --- | --- | --- | --- |
| CPU time | 10 s | `RLIMIT_CPU` | **[KERNEL-ENFORCED]** |
| File descriptors | 64 | `RLIMIT_NOFILE` | **[KERNEL-ENFORCED]** |
| Child processes | 100 | `RLIMIT_NPROC` | **[KERNEL-ENFORCED]** |
| Address space | 512 MiB | `RLIMIT_AS` | **[PARTIALLY IMPLEMENTED]** — kernel-enforced on Linux; on macOS Tahoe (26.x), unprivileged `RLIMIT_AS` is rejected and the runtime records `memory_limit_applied=false` plus a post-hoc `peak_rss_bytes` from `getrusage(RUSAGE_CHILDREN)`. A `memory_overrun` violation is raised if peak exceeds the requested limit. |
| Process-group kill on timeout | n/a | `os.setsid` + `os.killpg(SIGKILL)` | **[KERNEL-ENFORCED]** |
| stdout / stderr capture | 64 KiB each | byte-cap + sha256 of truncated bytes | **[POLICY-ONLY]** |
| Sandbox disk consumption | 50 MiB | post-execution `os.walk` | **[POLICY-ONLY]** (post-hoc detection only — the bytes were written before the runtime noticed) |
| Per-batch command count | 3 | pre-execution length check | **[POLICY-ONLY]** |

The wrapper records all defaults, the per-rlimit success/failure, the captured stream hashes, the post-walk sandbox size, and any violation codes (`memory_overrun`, `sandbox_size_overrun`, `cpu_time_exhausted`, `command_count_overflow`) in the per-run manifest. **[IMPLEMENTED]**

### 4.12 Repo invariance verification

`repo_fingerprint(REPO_ROOT)` is computed before the run and again at run-end (`REAL-AGENT-RUNTIME-v0.2.md` §7, §9). Equality is the v0.2 invariant for the canonical repository. Any drift records a `repo_fingerprint_drift` policy violation and forces `exit_status = 1`.

The fingerprint walk skips `.git`, `.venv`, `venv`, `__pycache__`, `.pytest_cache`, `.mypy_cache`, `node_modules`, the runtime's own sandbox / runs directories, and `reports/real_agent_runtime/` — so that running `make real-agent-check` inside the sandbox does not register as a violation. **[IMPLEMENTED]**, **[POLICY-ONLY]** (the runtime computes equality; the kernel does not enforce it).

Subprocesses run with `cwd=sandbox_path`. Combined with the kernel-isolation profile's write boundary, the source repository's protocol-canon files are unwritable from inside an isolated subprocess. Without isolation, only `cwd` keeps the subprocess in scope; an absolute-path write would not be prevented at the kernel level, but would be prevented at the policy level by `classify_write`. **[KERNEL-ENFORCED]** under isolation; **[POLICY-ONLY]** without it.

### 4.13 CI inclusion

`make ci` is the default local-CI target. It runs:

```
no-pseudocode → test → conformance → interop → canonicalization-check
```

(`Makefile`.) None of the executor / proposer / reviewer / pipeline / isolation / resource-limit targets are on `make ci`. They are explicitly opt-in:

- `make proposer-check`
- `make review-gate-check`
- `make pipeline-check`, `make pipeline-run-fixture`
- `make real-agent-check`, `make real-agent-dry-run`, `make real-agent-execute`, `make real-agent-execute-check`
- `make os-isolation-check`, `make os-isolation-fixture`
- `make resource-limit-check`, `make resource-limit-fixture`

Every runtime spec L-9 says the same thing: this layer is not added to `make ci`; future hardening cycles may evaluate inclusion. **[POLICY-ONLY]**

---

## 5. Manifest, artifact, and report types

This section enumerates every artifact the stack produces. For each: purpose, invariants, required fields (a précis; the runtime spec governs the full schema), replay role, trust boundary, what it proves, what it does not prove.

### 5.1 Proposal manifest

**Purpose.** Convert a work order's declared scope into a deterministically-ordered, capped-at-three candidate set. (`PROPOSER-RUNTIME-v0.1.md` §6.)

**Path.** `reports/proposer_runtime/proposal-<run_id>.json` + `.md`.

**Required fields (précis).** `proposal_id`, `work_order_id`, `agent_id`, `rationale`, `commands_proposed[]`, `commands_rejected[]`, `policy_rejections[]`, `allowed_command_matches[]`, `timestamp`, `deterministic_hash`, `runtime_version="v0.1"`, `exit_status`.

**Invariants.**
- At most three entries in `commands_proposed`.
- `commands_proposed` is lexicographically sorted.
- `deterministic_hash` is sha256 over the proposal serialization with `timestamp` and `deterministic_hash` removed.
- Every entry in `commands_proposed` matches a v0.2 allowlist entry; no entry matches a v0.1 forbidden pattern.
- `rationale` is non-empty.
- `agent_id` is in `IDENTITIES`.

**Replay role.** Anchor: re-derive the hash and verify. The proposal is the input to the reviewer.

**Trust boundary.** A proposal asserts admissibility-from-a-work-order. It does not assert correctness, intent, or capability. Two reviewers with different policies could reach different decisions on the same proposal.

**What it proves.** That at the moment of proposal, the work order's `required_gates` enumerated to a specific candidate set under the v0.2 classifiers.

**What it does NOT prove.** That the candidate set should be approved. That the work order itself was correctly authored. That the executor will admit the same set.

**Status.** **[IMPLEMENTED]** — 7 self-check fixtures pass (`reports/proposer_runtime/proposer_runtime_v0.1.json`).

### 5.2 Review artifact

**Purpose.** Convert a proposal into a deterministic admit-or-reject verdict. (`REVIEW-GATE-RUNTIME-v0.1.md` §6.)

**Path.** `reports/review_gate_runtime/review-<run_id>.json` + `.md`.

**Required fields (précis).** `review_id`, `proposal_id`, `work_order_id`, `reviewer_id`, `decision ∈ {"approved","rejected"}`, `approval_scope[]`, `rejected_commands[]`, `rejection_reasons[]`, `deterministic_hash_verified`, `timestamp`, `review_hash`, `runtime_version="v0.1"`, `exit_status`.

**Invariants.**
- `deterministic_hash_verified` is true iff the recomputed proposer hash equals the proposal's claimed `deterministic_hash` byte-for-byte.
- `decision="approved"` requires: hash verified, agent in `IDENTITIES`, rationale non-empty, `commands_proposed` non-empty and ≤3, every command clears deny-first AND hits the allowlist.
- `review_hash` is sha256 over the artifact serialization with `review_id`, `timestamp`, `review_hash` removed.
- The reviewer never spawns a subprocess. The module imports no `subprocess`, `socket`, `urllib`.

**Replay role.** Necessary admission gate between proposer and executor. Without an `approved` review artifact, the pipeline does not invoke the executor (`PIPELINE-RUNTIME-v0.1.md` self-check fixture 8).

**Trust boundary.** A review artifact's `approved` decision is *necessary, not sufficient*, for executor admission. The executor re-runs its own admission (`REAL-AGENT-RUNTIME-v0.1.md` §6) — it does not trust the reviewer's verdict. (`REVIEW-GATE-RUNTIME-v0.1.md` §9.)

**What it proves.** That the proposal cleared every v0.1 reviewer-admission constraint.

**What it does NOT prove.** That the executor will admit it. That the underlying work is correct.

**Status.** **[IMPLEMENTED]** — 8 self-check fixtures pass (`reports/review_gate_runtime/review_gate_runtime_v0.1.json`).

### 5.3 Executor manifest (v0.2 execute mode)

**Purpose.** Record one full subprocess invocation under bounded conditions — admission, command policy, fingerprint, and per-command result. (`REAL-AGENT-RUNTIME-v0.2.md` §11.)

**Path.** `workforce/real_agents/runs/<run_id>.json`.

**Required fields (v0.2 superset over v0.1).** All 16 v0.1 fields plus: `mode ∈ {"dry-run","execute"}`, `replay_mode`, `command_results[]`, `sandbox_fingerprint_before`, `sandbox_fingerprint_after`, `sandbox_files_changed[]`, `env_keys[]`. `command_results[i]` has 16 keys including `argv`, `cwd`, `timeout_s`, `status`, `exit_code`, `stdout`, `stdout_truncated`, `stderr`, `stderr_truncated`, `duration_ms`, `timed_out`, `error`, `timestamp_start`, `timestamp_end`.

**Invariants.**
- `repo_fingerprint_before == repo_fingerprint_after`, or `policy_violations` contains `repo_fingerprint_drift`.
- For every blocked command: `argv = []`, no subprocess spawned.
- For every executed command: `stdin=DEVNULL`, `cwd=sandbox`, env keys subset of `{PATH, LC_ALL, LANG, PYTHONPATH}`, `timeout_s ∈ (0.001, 300.0]`.
- `exit_status = 0` iff `policy_violations = []` AND all required-gate exits are 0.

**Replay role.** Per-run audit anchor. From the manifest alone an auditor can reconstruct: which work order, under which identity, which commands attempted, which blocked, which executed, with what exit code and duration, against what sandbox state, with what minimal env.

**Trust boundary.** The manifest is unsigned plain JSON. An operator with write access to `workforce/real_agents/runs/` can post-hoc edit it; detection requires re-derivation of the recorded hashes. (`REAL-AGENT-RUNTIME-v0.2.md` §14.)

**What it proves.** That a subprocess was invoked under the recorded parameters and produced the recorded output, *if* the manifest has not been tampered with.

**What it does NOT prove.** Cryptographic non-tampering. Identity binding to a hardware key. That the operator who invoked the runtime was the operator who claimed to.

**Status.** **[IMPLEMENTED]** — v0.2 self-check fixture suite covers 10 cases.

### 5.4 Pipeline aggregate manifest

**Purpose.** Single audit envelope spanning proposer, reviewer, and executor for one work order. (`PIPELINE-RUNTIME-v0.1.md` §6.)

**Path.** `reports/pipeline_runtime/pipeline-<pipeline_id>.json` + `.md`.

**Required fields (précis).** `pipeline_id`, `work_order_id`, `proposer_artifact`, `review_artifact`, `executor_manifest`, `proposer_hash`, `review_hash`, `executor_manifest_hash`, `final_status ∈ {executed, executed_with_violations, refused_at_review, refused_at_executor}`, `refusal_reason`, `commands_proposed[]`, `commands_approved[]`, `commands_executed[]`, `timestamps`, `repo_fingerprint_before`, `repo_fingerprint_after`, `policy_violations[]`, `pipeline_hash`, `runtime_version="v0.1"`, `exit_status`.

**Invariants.**
- `repo_fingerprint_before == repo_fingerprint_after`.
- If `review.decision != "approved"` then `executor_manifest = null` AND `commands_executed = []`.
- `pipeline_hash` is sha256 over the aggregate's audit-stable subset (excludes `pipeline_id`, `timestamps`, intermediate artifact paths, `executor_manifest_hash`, `pipeline_hash` itself).
- The pipeline module imports no `subprocess`, `socket`, `urllib` — the only subprocess in the chain is the executor's.

**Replay role.** End-to-end audit envelope. From the aggregate alone an auditor can reconstruct: which stage refused (or did not), at what hash, under what identity. The aggregate references the three intermediate artifacts by path.

**Trust boundary.** Same as the executor manifest — unsigned JSON. The pipeline's contribution is *transition recording*, not anti-tamper.

**What it proves.** That the three stages executed in order; that no stage was bypassed; that any refusal halted the pipeline at the correct stage.

**What it does NOT prove.** That the work order itself was authorized. That a hostile pipeline binary did not skip stages and write a fabricated aggregate.

**Status.** **[IMPLEMENTED]** — 8 self-check fixtures pass (`reports/pipeline_runtime/pipeline_runtime_v0.1.json`).

### 5.5 Isolation manifest (per-run, sandbox-exec)

**Purpose.** Record one kernel-isolated subprocess invocation under a content-hashed sandbox profile. (`OS-ISOLATION-RUNTIME-v0.1.md` §7.)

**Path.** `reports/os_isolation_runtime/runs/run-<id>.json`. Profiles: `reports/os_isolation_runtime/profiles/<sha256>.sb`.

**Required fields (over v0.2 executor manifest's `command_results` shape).** `isolation_mode ∈ {"sandbox-exec"}`, `sandbox_profile_hash`, `sandbox_profile_path`, `kernel_enforced`, `denied_syscalls`, plus the v0.2 fields.

**Invariants.**
- `kernel_enforced = true` iff sandbox-exec was actually invoked (false when the classifier blocked the command before sandbox-exec).
- `sandbox_profile_hash` is the sha256 of the on-disk profile bytes; identical inputs produce identical hash (fixture 9).
- Status `"blocked_by_classifier"` is added for commands rejected before sandbox-exec.

**Replay role.** Per-run kernel-enforcement audit. The profile path + hash is the kernel's input artifact; the result is the kernel's output. A future replay tool could re-run the recorded profile against the recorded argv and compare denial outcomes (**[FUTURE WORK]** — `OS-ISOLATION-RUNTIME-v0.1.md` §10.6 item 5).

**Trust boundary.** Trusts that the host kernel has not been tampered with. (`OS-ISOLATION-RUNTIME-v0.1.md` §10.6 item 10.) No TPM-rooted attestation. **[EXPLICITLY UNSUPPORTED]** for cross-host attestation.

**What it proves.** That on the recording host, at the recording time, the kernel evaluated the recorded profile against the recorded argv and produced the recorded outcome.

**What it does NOT prove.** That the kernel was unmodified. That sandbox-exec is bug-free. That side channels (timing, page-fault patterns) leaked no information.

**Status.** **[IMPLEMENTED]** — 9 self-check fixtures pass on `darwin` (`reports/os_isolation_runtime/os_isolation_runtime_v0.1.json`).

### 5.6 Resource-limit manifest

**Purpose.** Record a subprocess invocation under the bounded-resource wrapper, including which rlimits were applied, which were rejected (macOS `RLIMIT_AS`), and any violations detected post-hoc. (`RESOURCE-LIMIT-RUNTIME-v0.1.md` §7.)

**Path.** `reports/resource_limit_runtime/runs/run-<id>.json`.

**Required fields.** All isolation-manifest fields plus: configured limits (`cpu_limit_seconds`, `memory_limit_bytes`, `fd_limit`, `process_limit`, `stdout_limit_bytes`, `stderr_limit_bytes`, `sandbox_size_limit_bytes`, `command_count_limit`); enforcement results (`process_tree_killed`, `stdout_truncated`, `stderr_truncated`, `stdout_hash`, `stderr_hash`, `sandbox_size_bytes`, `peak_rss_bytes`, `rlimits_applied = {cpu, memory, fd, nproc}`, `resource_violations[]`).

**Invariants.**
- `rlimits_applied.cpu`, `.fd`, `.nproc` are `true` on supported platforms (Linux, macOS).
- `rlimits_applied.memory` is `false` on macOS Tahoe; `peak_rss_bytes` is recorded; `memory_overrun` is added to `resource_violations` if peak exceeds `memory_limit_bytes`.
- `process_tree_killed = true` iff `os.killpg(pgid, SIGKILL)` fired on timeout.
- Truncation hashes are deterministic across re-runs of the same input (fixture 12 `deterministic_truncation_hashes_stable`).

**Replay role.** Survivability audit. An auditor can verify that the run's resource consumption was bounded (or was bounded best-effort and detected post-hoc).

**Trust boundary.** Same as the isolation manifest — trusts the host kernel.

**What it proves.** That the subprocess terminated within the recorded bounds, or that a violation was recorded.

**What it does NOT prove.** That memory was prevented from being allocated on macOS — only that it was detected. That CPU/fd consumption across a multi-command batch was capped — current limits are per-process, not cumulative across the batch (`RESOURCE-LIMIT-RUNTIME-v0.1.md` §10.4 item 2).

**Status.** **[IMPLEMENTED]** — 12 self-check fixtures pass (`reports/resource_limit_runtime/resource_limit_runtime_v0.1.json`).

### 5.7 Self-check report (per runtime)

**Purpose.** Per-runtime aggregate result of all internal fixtures. Written by `<runtime>.py self-check`. (Each runtime spec §8.)

**Path.** `reports/<runtime>/<runtime>_v0.1.{md,json}`.

**Required fields.** `runtime`, `runtime_version`, `timestamp`, `fixtures[]` (each with `name`, `passed`, `detail`, plus runtime-specific anchors), `all_passed`.

**Invariants.** `all_passed = true` iff every fixture's `passed = true`. The harness writes each fixture's per-run manifest under `reports/<runtime>/runs/` (or equivalent), and references it from the report.

**Replay role.** Closure evidence for the runtime as a whole. A reviewer reads the self-check report and verifies that every fixture's listed `<run_manifest>` exists and re-derives its hash.

**Trust boundary.** Plain JSON; unsigned.

**What it proves.** That at the time of the self-check, every fixture passed.

**What it does NOT prove.** That the runtime is correct on inputs the fixtures don't cover.

**Status.** **[IMPLEMENTED]** for all six runtimes (proposer, reviewer, real-agent v0.1, real-agent v0.2, pipeline, OS isolation, resource-limit). All committed reports show `all_passed: true`.

### 5.8 Closure report (work-order level)

**Purpose.** Record that a single work order traversed `drafted → approved → assigned → executed → self-verified → gate-checked → reviewed → closed` with all required artifacts attached. (`WORKFORCE-EXECUTION-RUNTIME-v0.1.md` §4 + §20.)

**Path.** Work order in `workforce/work_orders/closed/` (after closure); action log in `workforce/action_logs/`; self-verification block at `workforce/action_logs/<action_id>.self_verification.md`; per-WO gate outputs under `workforce/reports/<action_id>/`.

**Required fields (précis).** Work-order yaml: `work_order_id`, `status`, `assigned_to`, `agent_role`, `allowed_files[]`, `forbidden_files[]`, `required_gates[]`, `status_history[]`, etc. Action log: as enumerated in `WORKFORCE-EXECUTION-RUNTIME-v0.1.md` §8 — 13 required fields, no omissions.

**Invariants.** Closure state is irreversible except by rollback (`status_history` is append-only). All gates in `required_gates` appear in `gates_passed`. Self-verification block is complete with `yes`/`no` per question. Reviewer finding is attached. Human-owner approval recorded with identity and timestamp in `status_history`.

**Replay role.** Governance-level closure anchor. The runtime stack feeds the action log's `gates_passed` evidence; the work order's lifecycle enforces the surrounding chain.

**Trust boundary.** Plain text on disk; unsigned. **[POLICY-ONLY]**

**What it proves.** That at closure time, every governance precondition was met.

**What it does NOT prove.** Cryptographic non-tampering. Hardware-rooted identity. That a hostile operator did not edit `status_history` after the fact.

**Status.** **[IMPLEMENTED]** as a policy surface; **[POLICY-ONLY]** at the cryptographic layer.

---

## 6. Governance model

The stack composes from a small set of named laws, each in its own normative document. This section summarizes the load-bearing law from each. None is invented in this document; all are quoted-or-paraphrased from the cited spec.

### 6.1 Admission law

> **Every action requires a work-order admission.** A subprocess invocation, a proposal generation, or a review verdict must complete an admission check against the work order's `work_order_id`, `status`, `assigned_to`, `allowed_files`, `forbidden_files`, and the acting identity's `IDENTITIES` entry. (`REAL-AGENT-RUNTIME-v0.1.md` §6.)

Refusal codes: `unknown_agent_identity`, `missing_required_field`, `status_not_admissible`, `assigned_to_mismatch`, `missing_allowed_files`, `missing_forbidden_files`. **[POLICY-ONLY]**

### 6.2 Review law

> **The reviewer gate has approval authority only over proposal admissibility. It has zero execution authority.** (`REVIEW-GATE-RUNTIME-v0.1.md` §9.)

The reviewer cannot grant capability. An `approved` verdict is necessary for executor invocation; it is not sufficient. The executor re-runs admission. **[IMPLEMENTED]**

### 6.3 Replay law

> **The operational chain reconstructs from the record alone.** (`REPLAY-LAW-v0.1.md` §5 Principle 3, the strongest of the immutable replay principles.)

Replay is binary. Partial replay is not replay. Replay does not depend on operator testimony or live system state. **[IMPLEMENTED]** at the per-run level; **[NOT IMPLEMENTED]** for cross-run hash chaining.

### 6.4 Closure law

> **A work order in any state other than `closed` or `rejected` is open. Open work orders block their own files for any other work order.** (`WORKFORCE-EXECUTION-RUNTIME-v0.1.md` §4.)

Closure is irreversible except by rollback. Rollback is a separately-logged action with its own `action_id`. **[POLICY-ONLY]**

### 6.5 Isolation law

> **The kernel enforces the sandbox; the runtime enforces the policy. Governance determines admissibility; kernel isolation constrains damage radius.** (`OS-ISOLATION-RUNTIME-v0.1.md` §9.)

Two-layer defense. Removing either layer changes the artifact class. **[IMPLEMENTED]** on macOS via `sandbox-exec`; **[FUTURE WORK]** for non-macOS substrates.

### 6.6 Bounded-runtime law

> **Governance determines admissibility. Kernel isolation constrains scope. Resource limits constrain survivability.** (`RESOURCE-LIMIT-RUNTIME-v0.1.md` §9.)

Three-layer defense composed. **[IMPLEMENTED]** on macOS (best-effort for memory); **[IMPLEMENTED]** kernel-enforced for CPU/fd/nproc.

### 6.7 Refusal semantics

Every refusal is typed (one of the codes in §17.6), recorded in a manifest, and forces `exit_status = 1`. The runtime never fails open. Any unexpected condition surfaces as a Python exception with traceback rather than a swallowed error. (`PROPOSER-RUNTIME-v0.1.md` §7, `REVIEW-GATE-RUNTIME-v0.1.md` §7, `REAL-AGENT-RUNTIME-v0.2.md` §13.) **[IMPLEMENTED]**

### 6.8 Lifecycle monotonicity

Work-order state transitions are recorded in `status_history`. The history is append-only — no edit, no replacement, no in-place mutation. A correction is a new entry referencing the prior. (`WORKFORCE-EXECUTION-RUNTIME-v0.1.md` §4 + §8.) **[POLICY-ONLY]** — disk-level append-only is enforced by convention; no `chattr +a` or filesystem-level immutability.

### 6.9 Deterministic approval

A reviewer running over the same proposal under the same reviewer identity produces a `review_hash` that is byte-identical (modulo recorded-but-not-hashed `review_id`, `timestamp`). (`REVIEW-GATE-RUNTIME-v0.1.md` fixture 8 `review_artifact_hash_stable`.) **[IMPLEMENTED]**

### 6.10 Audit reconstruction

A reviewer auditing a closed work order reconstructs the full chain by:

1. Reading `workforce/work_orders/closed/<id>.yaml` → identity, scope, gates.
2. Reading `workforce/action_logs/<action_id>.{md,yaml}` → files read, files changed, commands run, gate outcomes.
3. Reading `workforce/action_logs/<action_id>.self_verification.md` → scope-adherence claims.
4. Reading `reports/pipeline_runtime/pipeline-<id>.json` → end-to-end audit envelope.
5. Following the aggregate's `proposer_artifact`, `review_artifact`, `executor_manifest` paths and re-deriving each hash.
6. Verifying `repo_fingerprint_before == repo_fingerprint_after`.
7. Verifying every required-gate output under `workforce/reports/<action_id>/`.

The chain is mechanically reconstructible. **[IMPLEMENTED]** at the per-WO level.

---

## 7. State machine

The work-order lifecycle is a strict ordering with explicit transitions. (`WORKFORCE-EXECUTION-RUNTIME-v0.1.md` §4.) Each state has an entry condition, an exit condition, allowed transitions, forbidden transitions, replay implications, and closure implications.

```
            ┌──────────┐
            │ drafted  │
            └────┬─────┘
                 │ human owner approval
                 ▼
            ┌──────────┐
            │ approved │
            └────┬─────┘
                 │ human owner assignment to identity
                 ▼
            ┌──────────┐
            │ assigned │
            └────┬─────┘
                 │ executor invocation; subprocess runs
                 ▼
            ┌──────────┐
            │ executed │
            └────┬─────┘
                 │ agent self-verification block written
                 ▼
            ┌──────────────┐
            │ self_verified│
            └────┬─────────┘
                 │ all required gates pass
                 ▼
            ┌────────────┐
            │ gate_checked│
            └────┬────────┘
                 │ reviewer agent finding attached
                 ▼
            ┌──────────┐
            │ reviewed │
            └────┬─────┘
                 │ human owner final approval
                 ▼
            ┌────────────────┐
            │ human_approved │
            └────┬───────────┘
                 │ closure criteria all met
                 ▼
            ┌──────────┐
            │  closed  │ ◄── terminal
            └──────────┘

  Any state except drafted, closed, or rejected may transition to:
            ┌──────────┐
            │  refused │ ◄── terminal
            └──────────┘
```

### 7.1 `drafted`

**Entry.** Work order written to `workforce/work_orders/<id>.yaml`. `status: drafted`.

**Allowed transitions.** `drafted → approved` via human owner signature recorded in `status_history`. `drafted → refused` via owner refusal.

**Forbidden transitions.** `drafted → assigned` (cannot skip approval). `drafted → executed`. `drafted → closed`.

**Replay implications.** A drafted work order has no executable record yet. Replay reconstructs only the draft text and the eventual approval (if any).

**Closure implications.** `drafted` is not a closed state. Open until terminal.

**Status.** **[POLICY-ONLY]**

### 7.2 `approved`

**Entry.** Human owner approval recorded.

**Allowed transitions.** `approved → assigned` via owner-bound assignment to one identity.

**Forbidden transitions.** `approved → executed` (assignment is required). `approved → drafted` (irreversible).

**Replay implications.** The approval timestamp and approver identity are part of the replayable record.

**Status.** **[POLICY-ONLY]**

### 7.3 `assigned`

**Entry.** `assigned_to: <identity>` field set. Identity must match `IDENTITIES` and the work order's required role.

**Allowed transitions.** `assigned → executed` via successful executor invocation. `assigned → refused` via executor admission failure (e.g., `assigned_to_mismatch` if invoked under wrong identity).

**Forbidden transitions.** Self-assignment by an agent. Reassignment without an explicit transition entry. Concurrent assignment to multiple identities.

**Replay implications.** The executor re-checks `assigned_to == agent_id` on every invocation; mismatch refuses with `assigned_to_mismatch`.

**Status.** **[POLICY-ONLY]**

### 7.4 `executed`

**Entry.** Executor manifest written. `files_changed`, `commands_run`, gate outputs all recorded. `repo_fingerprint_before == repo_fingerprint_after` or `repo_fingerprint_drift` violation.

**Allowed transitions.** `executed → self_verified` via agent's self-verification block.

**Forbidden transitions.** `executed → reviewed` (self-verification is required first). `executed → closed`.

**Replay implications.** The executor manifest is the per-run replay anchor. A future replay re-derives every recorded hash and verifies the recorded outcomes.

**Status.** **[IMPLEMENTED]** at the runtime layer.

### 7.5 `self_verified`

**Entry.** Self-verification block written at `workforce/action_logs/<action_id>.self_verification.md`. Every question answered explicitly with `yes` or `no` plus a one-sentence justification. (`WORKFORCE-EXECUTION-RUNTIME-v0.1.md` §9, §23.)

**Allowed transitions.** `self_verified → gate_checked` via gate execution.

**Forbidden transitions.** `self_verified → closed` (gates required). Skipping any question or answering "not applicable" without justification is treated as a failed submission.

**Replay implications.** The self-verification block is the agent's scope-adherence claim. A reviewer cross-checks it against the action log's `files_changed` / `commands_run` / `gates_passed`.

**Status.** **[POLICY-ONLY]**

### 7.6 `gate_checked`

**Entry.** Every gate in `required_gates` has run; pass/fail captured in the action log's `gates_passed` / `gates_failed`. Captured gate outputs under `workforce/reports/<action_id>/`.

**Allowed transitions.** `gate_checked → reviewed` if all gates passed. `gate_checked → refused` if any required gate failed.

**Forbidden transitions.** Closure with `gates_failed` non-empty. Modifying `Makefile` or `.github/workflows/**` to silence a failure (`WORKFORCE-EXECUTION-RUNTIME-v0.1.md` §11 — itself a §25 failure).

**Replay implications.** Gate outputs are committed alongside the change. A replay re-runs each gate against the recorded artifacts; outcome must match.

**Status.** **[POLICY-ONLY]**

### 7.7 `reviewed`

**Entry.** Reviewer Agent finding produced and attached to the work order. The reviewer is a different identity than the executor (`AGENT-GOVERNANCE-WORKFORCE-v0.1.md`).

**Allowed transitions.** `reviewed → human_approved` via owner approval.

**Forbidden transitions.** `reviewed → closed` (human approval required).

**Replay implications.** The reviewer finding is part of the replayable record.

**Status.** **[POLICY-ONLY]**

### 7.8 `human_approved`

**Entry.** Human owner final approval recorded in `status_history` with approver identity and timestamp. (`WORKFORCE-EXECUTION-RUNTIME-v0.1.md` §12.)

**Allowed transitions.** `human_approved → closed` if all closure criteria (§7.9) are met.

**Forbidden transitions.** Verbal approval. Silent approval. Approval recorded retroactively.

**Replay implications.** The human approval is the unit of release. Without it, no work order closes.

**Status.** **[POLICY-ONLY]**

### 7.9 `closed`

**Entry.** All §20 closure criteria met: action log present, self-verification block present and complete, every required gate in `gates_passed`, reviewer finding present, human approval present, no policy violations.

**Allowed transitions.** None (terminal). Rollback is a *new* work order with its own `action_id` referencing the closed one.

**Forbidden transitions.** `closed → executed`. Re-execution under the same `work_order_id`. Edit of `status_history`.

**Replay implications.** A closed work order's replay produces an identical closed state by every reconstructable property. (`REPLAY-LAW-v0.1.md` §13.)

**Status.** **[POLICY-ONLY]** for irreversibility (no kernel-level immutability).

### 7.10 `refused`

**Entry.** Any pre-closure state may transition to refused on a typed refusal. The action log records the refusal code and the offending input. Rollback plan executes; postmortem under `workforce/reports/<work_order_id>/postmortem.md`.

**Allowed transitions.** None (terminal).

**Forbidden transitions.** Silent refusal. Refusal without a recorded code. Refusal that does not trigger the rollback plan.

**Replay implications.** A refused work order's record is preserved as-is — nothing is rewritten, nothing is deleted. The refusal is itself a first-class artifact.

**Status.** **[IMPLEMENTED]** at the runtime layer (every runtime emits typed refusals); **[POLICY-ONLY]** at the lifecycle layer.

### 7.11 Replay-mode admission of `closed`

`REAL-AGENT-RUNTIME-v0.2.md` §5 defines a single bounded admission exception: when `replay_mode=True` (CLI flag `--replay`) AND the only refusal would be `status_not_admissible` AND the WO's status is exactly `"closed"`, admission is re-evaluated as if status were `"approved"`. Every other refusal still applies. The manifest records `replay_mode: true`. The work order's lifecycle is *not* mutated — the replay is forensic re-run, not closure-undo. **[IMPLEMENTED]**

---

## 8. Security model

This section enumerates the attack surfaces the stack defends against, the layer at which each defense fires, and the residual risks each layer does not address. Every claim is grounded in an explicit "security non-guarantees" or "what attacks still remain possible" section of a runtime spec.

### 8.1 Attack surface enumeration

| Surface | Layer of first defense | Layer of last defense | Residual risk |
| --- | --- | --- | --- |
| Subprocess execution of unapproved command | classifier (Python) | sandbox-exec (kernel) | classifier bypass + kernel bug |
| Filesystem write outside sandbox | `classify_write` (Python) | `(allow file-write* (subpath sandbox))` (kernel) | absolute-path write under classifier-only |
| Network egress | classifier deny-list (Python) | `(deny network*)` (kernel) | classifier bypass + kernel bug |
| Application launch via `open -a` | classifier (Python) | `(deny mach-lookup launchservicesd)` (kernel) | non-LaunchServices launch path |
| Forbidden binary exec via shell | classifier (Python) | `(deny process-exec*)` + per-target allow (kernel) | exec of allowed binary |
| Resource exhaustion | none at v0.2 executor | `setrlimit` (kernel) | macOS `RLIMIT_AS` unprivileged |
| Manifest forgery | none | manual hash re-derivation | unsigned JSON |
| Hash mutation | hash field excluded from hash input | reviewer re-derivation | post-mutation undetected at write time |
| Identity spoofing | identity string match | none | `IDENTITIES` is a Python dict |
| Operator privilege abuse | none | none | **[EXPLICITLY UNSUPPORTED]** |

### 8.2 Policy-layer containment

**What it covers.** Admission (work-order match, identity match, scope match), command policy (deny-first then allowlist), filesystem policy (`classify_read` / `classify_write`), rationale validation, hash re-derivation, command-count cap.

**What defeats it.** A bug in the classifier that misclassifies a command as allowed. A smuggled allowlist entry. A hostile change to `EXECUTE_ALLOWED_COMMANDS`. A privileged operator with write access to `tools/*.py`.

**Status.** **[POLICY-ONLY]**

### 8.3 Kernel-layer containment

**What it covers (macOS, sandbox-exec):** process-exec allowlist (target binary only, `EPERM` on every other `execve`), file-write outside sandbox (`EPERM`), `mach-lookup` of LaunchServices family (denied), `network*` (all socket creation denied), default-deny on every operation not explicitly allowed.

**What defeats it.** A kernel bug in `sandbox.kext`. Apple deprecating `sandbox-exec` and removing the binary in a future macOS. (`OS-ISOLATION-RUNTIME-v0.1.md` §10.4 — `sandbox-exec` is already marked deprecated by Apple.) A kernel-level rootkit.

**Status.** **[KERNEL-ENFORCED]**

### 8.4 Subprocess risks

**Stdin abuse.** `stdin=subprocess.DEVNULL` — the subprocess cannot read from the operator's terminal. **[POLICY-ONLY]**

**Stdout/stderr exhaustion.** Capped at 64 KiB each (v0.2 default), with sha256 of truncated bytes recorded for replay-stable comparison. **[POLICY-ONLY]**

**Stdout exfiltration.** The subprocess can read any file the kernel-isolation profile permits (`(allow file-read*)` is broad) and emit the contents to stdout, which the harness captures. The kernel does not enforce a read-side allowlist. (`OS-ISOLATION-RUNTIME-v0.1.md` §10.4, §10.6 item 1 — narrowing reads is **[FUTURE WORK]**.) **[EXPLICITLY UNSUPPORTED]** at v0.1.

**Fork abuse.** `RLIMIT_NPROC` set below the user's existing process count. First `fork()` returns `EAGAIN`. (`RESOURCE-LIMIT-RUNTIME-v0.1.md` fixture 7 `fork_attempt_rejected`.) **[KERNEL-ENFORCED]**

**Orphan child survival.** Without the bounded wrapper, descendants detached from the parent may survive timeout. With `os.setsid()` + `os.killpg(SIGKILL)`, the entire process group dies. **[KERNEL-ENFORCED]** under bounded wrapper; **[PARTIAL]** without.

**In-sandbox harm.** Anything the target binary does *inside* its sandbox subpath is unrestricted by the kernel: garbage files, symlinks, oversized writes (capped only post-hoc by `sandbox_size_limit_bytes`). **[EXPLICITLY UNSUPPORTED]** for in-sandbox prevention.

### 8.5 Operator authority risks

The system is **[EXPLICITLY UNSUPPORTED]** against a privileged operator. (`REAL-AGENT-RUNTIME-v0.2.md` §14, `REAL-AGENT-RUNTIME-v0.1.md` §14.) An operator with:

- write access to `tools/*.py` can rewrite the classifiers.
- write access to `reports/` can post-hoc edit any manifest (detection: re-derive recorded hash).
- write access to `workforce/work_orders/` can synthesize a fake closure.
- root can defeat sandbox-exec.

The system's claim is *not* that an operator cannot subvert it. The claim is that an honest operator's actions are auditably reconstructable, and a hostile operator must mutate the artifact tree visibly.

### 8.6 Proposal tampering

A proposal's `deterministic_hash` is sha256 over the audit-stable subset (excludes `timestamp`, `deterministic_hash`). A reviewer re-derives the hash and rejects on mismatch (`REVIEW-GATE-RUNTIME-v0.1.md` fixture 2 `bad_hash_rejected`, refusal code `deterministic_hash_mismatch`). **[POLICY-ONLY]** but **[IMPLEMENTED]**.

A pipeline run (`PIPELINE-RUNTIME-v0.1.md` fixture 3 `mutated_proposal_hash_rejected`) demonstrates that mutating the proposer JSON's hash field after the proposer wrote it causes the reviewer to reject and the executor to never be invoked.

### 8.7 Replay attacks

The system does not yet have a primitive for replay-attack prevention across runs. Two pipeline runs of the same work order produce two independent aggregates with different `pipeline_id` and `timestamps` but byte-identical `pipeline_hash`. A hostile operator could re-submit a stale aggregate and claim it as fresh; detection requires a cross-run hash chain or signed timestamps. **[NOT IMPLEMENTED]** — `REAL-AGENT-RUNTIME-v0.2.md` §14: "anti-replay across runs: no chain links one manifest to the next."

### 8.8 Sandbox escape

In-sandbox: not prevented (see §8.4). Outside-sandbox via absolute path under classifier-only enforcement: not prevented at the kernel level without isolation; prevented at the syscall level with isolation (`(allow file-write* (subpath sandbox))`). **[KERNEL-ENFORCED]** under isolation; **[POLICY-ONLY]** without.

### 8.9 Filesystem abuse

Standing-forbidden paths (`SPEC.md`, `vectors/**`, `Makefile`, etc.) are blocked at `classify_write`. **[POLICY-ONLY]**. Under kernel isolation, source-repo writes require absolute paths AND are outside the sandbox subpath, so the kernel denies them. **[KERNEL-ENFORCED]** under isolation.

`forbidden_files` glob is enforced at the policy layer only — the kernel does not consult it. **[POLICY-ONLY]**

### 8.10 Reviewer corruption

A hostile reviewer (i.e., someone who edits `tools/review_gate_runtime.py` to always emit `decision=approved`) can defeat the review-gate layer. The executor's own admission (`REAL-AGENT-RUNTIME-v0.1.md` §6) is the next line. The pipeline records `review_artifact` and `review_hash` separately from the proposer artifact, so an auditor can re-derive both hashes independently and verify they cover the recorded inputs. **[POLICY-ONLY]**

A future protocol (`REVIEW-GATE-RUNTIME-v0.1.md` §12 future work) could require multiple `approved` review artifacts under distinct reviewer identities (Class C-style consensus). **[FUTURE WORK]**

### 8.11 Hash mutation

Every hash is sha256. A post-hoc mutation of an artifact's content (without updating the recorded hash) is detected on re-derivation. A coordinated mutation of both content and hash field requires the attacker to also re-derive the hash correctly — which they can, because the hash function is public. The defense against this class is *signed* hashes (cryptographic attestation), which is **[NOT IMPLEMENTED]** (`REAL-AGENT-RUNTIME-v0.2.md` §14).

### 8.12 Manifest forgery

Manifests are unsigned plain JSON. An operator with write access to `reports/` or `workforce/real_agents/runs/` can synthesize a fake manifest. Detection: cross-reference the work order's lifecycle, the reviewer artifact, the proposer artifact, and the pipeline aggregate — all four must agree, and each carries an independent hash over its own stable subset. **[POLICY-ONLY]**

### 8.13 What the system explicitly does not defend

- **Operator privilege.** **[EXPLICITLY UNSUPPORTED]**
- **Production-grade containment.** The macOS sandbox profile leaves `(allow mach-lookup)` broad; reads are not narrowly allowlisted. **[EXPLICITLY UNSUPPORTED]** at v0.1.
- **Distributed consensus.** Single-host. **[EXPLICITLY UNSUPPORTED]**.
- **Hardware-rooted identity.** Strings in a Python dict. **[EXPLICITLY UNSUPPORTED]**.
- **Side channels.** Timing, scheduler observation, page-fault patterns. **[EXPLICITLY UNSUPPORTED]**.
- **Cross-host attestation.** Trusts the local kernel. **[EXPLICITLY UNSUPPORTED]**.

---

## 9. Isolation model

### 9.1 macOS `sandbox-exec`

The runtime invokes `/usr/bin/sandbox-exec -f <profile_path> <argv>` as the outer wrapper for every isolated subprocess. (`OS-ISOLATION-RUNTIME-v0.1.md` §6.) `sandbox-exec` reads a TinyScheme-style profile and applies it to the child process via the kernel's sandbox.kext.

`sandbox-exec` is marked deprecated by Apple as of recent macOS releases. It still works on macOS 26.x. Long-term durability is not guaranteed; migration to Endpoint Security or to a Linux substrate via `unshare` is **[FUTURE WORK]** (§15).

### 9.2 `(deny process-exec*)`

The profile's first restrictive clause. Without it, the subprocess could `execve` any binary on `PATH`. With it, every `execve` returns `EPERM` from the kernel — except the explicit `(allow process-exec (literal "<target>"))` clause, which permits exec of *only* the resolved target binary path. (`OS-ISOLATION-RUNTIME-v0.1.md` §10.1.)

Variant routing: `/bin/sh` is rewritten to `/bin/bash` by macOS; both literals are emitted. `OS-ISOLATION-RUNTIME-v0.1.md` fixture 5 `nested_subprocess_spawn_denied` demonstrates that `/bin/sh -c '/bin/ls /usr'` fails because `/bin/ls` is not on the per-run allowlist. **[KERNEL-ENFORCED]**

### 9.3 `(deny network*)`

Denies socket creation, bind, listen, connect, sendto, recvfrom, sendmsg, recvmsg, and the rest of the BSD socket family at syscall time. No socket can be opened. The classifier's `https://` / `curl` / `wget` deny was a string check; this is a syscall check. **[KERNEL-ENFORCED]**

### 9.4 `(deny file-write*)` outside sandbox

The profile emits `(deny file-write*)` followed by `(allow file-write* (subpath "<sandbox_path>"))`. The order matters: the deny is first, the allow is the explicit exception. Result: writes inside the resolved sandbox subpath succeed; writes elsewhere return `EPERM`.

Two narrow exceptions: `(allow file-write-data (literal "/dev/null"))` and `(allow file-write-data (literal "/dev/dtracehelper"))` — both kernel-side writes that the libc / dyld machinery may issue. (`OS-ISOLATION-RUNTIME-v0.1.md` §6.)

`OS-ISOLATION-RUNTIME-v0.1.md` fixture 3 `write_outside_sandbox_denied_by_kernel_policy` demonstrates: `touch /private/tmp/<random>` returns nonzero exit and the file does not exist on disk afterward. **[KERNEL-ENFORCED]**

### 9.5 LaunchServices denial

The profile broadly allows `mach-lookup` (so dyld and libc can resolve required services) but explicitly denies four LaunchServices entries: `com.apple.coreservices.launchservicesd`, `com.apple.lsd.mapdb`, `com.apple.lsd.modifydb`, `com.apple.lsd.openurls`. As a result, `/usr/bin/open -a Calculator` cannot reach the app launcher and fails with "Unable to find application named 'Calculator'". (`OS-ISOLATION-RUNTIME-v0.1.md` fixture 4 `open_calculator_app_denied`.) **[KERNEL-ENFORCED]**

### 9.6 Syscall-layer enforcement

Every syscall a target binary issues is evaluated by sandbox.kext against the loaded profile. The kernel is the gatekeeper; the runtime is the policy author. The runtime cannot defeat the kernel; an attacker who edits the profile after sandbox-exec has loaded it cannot affect the running subprocess (the kernel reads the profile at exec time only).

### 9.7 Runtime policy vs kernel policy

The split is precise (`OS-ISOLATION-RUNTIME-v0.1.md` §10.2):

**Kernel-enforced:** process-exec allowlist, file-write boundary, LaunchServices denial, network denial, default-deny on unallowed operations.

**Policy-only (still):** work-order admission, identity match, command-string allowlist, rationale presence, hash verification, reviewer decision, repo fingerprint invariance, in-sandbox write semantics (the kernel allows any write inside the sandbox; `allowed_files` glob is consulted only by `classify_write`).

A reader assessing whether a given protection is policy-only or kernel-enforced must consult §10.2 of the OS-isolation spec; this document summarizes but does not replace it.

### 9.8 Remaining isolation gaps before "production-grade"

`OS-ISOLATION-RUNTIME-v0.1.md` §10.6 enumerates ten gaps that prevent the phrase "real isolated governed agents" from being technically defensible. The document is explicit about which are **[FUTURE WORK]**:

1. Read-side allowlist enforced at syscall time.
2. Fine-grained `mach-lookup` allowlist (currently broad).
3. Resource limits (partial — see §4.11).
4. Containment of in-sandbox writes per work-order glob.
5. Replay of the recorded profile.
6. Isolation surviving `sandbox-exec` deprecation.
7. Removal of the blanket `(allow mach-lookup)`.
8. Multi-reviewer admission.
9. Network-egress proof in manifest.
10. Cross-host attestation.

Items 1, 2, 3, 6 are the most load-bearing. Until they are addressed, the v0.1 isolation layer is "a meaningful step, not a destination" (`OS-ISOLATION-RUNTIME-v0.1.md` §10.6).

---

## 10. Determinism model

### 10.1 Deterministic hashing

Every artifact carries a sha256 hash over an audit-stable subset of its own content. The subset is a fixed set of fields enumerated in the runtime spec; specifically excluded are non-stable fields like `timestamp`, run identifiers, intermediate paths, and the hash field itself. Two runs of the same input produce byte-identical hashes.

| Hash | Spec | Stable subset | Excluded |
| --- | --- | --- | --- |
| `deterministic_hash` (proposal) | `PROPOSER-RUNTIME-v0.1.md` §6 | `agent_id`, `allowed_command_matches`, `commands_proposed`, `commands_rejected`, `policy_rejections`, `rationale`, `runtime_version`, `work_order_id` | `timestamp`, `deterministic_hash`, `proposal_id` |
| `review_hash` | `REVIEW-GATE-RUNTIME-v0.1.md` §6 | review verdict + scope + reasons + hash-verified flag + runtime_version + work-order-id + proposal-id + reviewer-id | `review_id`, `timestamp`, `review_hash`, `exit_status` |
| `executor_manifest_hash` | `PIPELINE-RUNTIME-v0.1.md` §6 | derived by pipeline as sha256 of the executor manifest's audit-stable subset | exec-side timestamps and run id |
| `pipeline_hash` | `PIPELINE-RUNTIME-v0.1.md` §6 | aggregate's audit-stable subset | `pipeline_id`, `timestamps`, intermediate paths, `executor_manifest_hash`, `pipeline_hash` |
| `sandbox_profile_hash` | `OS-ISOLATION-RUNTIME-v0.1.md` §6 | profile bytes | n/a (profile is the input) |
| `stdout_hash`, `stderr_hash` | `RESOURCE-LIMIT-RUNTIME-v0.1.md` §7 | sha256 of the (possibly truncated) captured bytes | n/a |

**[IMPLEMENTED]** Each hash has a stability fixture in its runtime's self-check suite.

### 10.2 Replay continuity

The proposer's `deterministic_hash` is the input to the reviewer. The reviewer recomputes it (`REVIEW-GATE-RUNTIME-v0.1.md` §3) and rejects on mismatch. The pipeline's aggregate references the proposer artifact, the review artifact, and the executor manifest by path; each artifact's own hash is independently re-derivable. Continuity across the chain is by re-derivation, not by signing.

A break anywhere in the chain (mutated proposal, mutated review, mutated executor manifest) is detected by the next consumer. **[IMPLEMENTED]**

### 10.3 Stable manifests

Every manifest is JSON, sorted by key, indented two spaces, UTF-8, trailing newline. Two emissions of the same manifest under the same input produce byte-identical bytes (modulo the recorded-but-not-hashed envelope: `timestamp`, run id, and stage-specific paths).

The byte-identical property is what makes the hash a hash of the *content*, not of the *bytes that happened to be written*. **[IMPLEMENTED]**

### 10.4 Canonical replay

A replay tool, given a work order and the four runtime modules at the version they were when the original run executed, can re-derive every recorded hash and check equality. (`REPLAY-LAW-v0.1.md` §11–§14.)

The current stack does not ship such a replay tool — it ships the artifact set and the runtimes under which a manual replay is possible. A turn-key replay binary is **[FUTURE WORK]** (`OS-ISOLATION-RUNTIME-v0.1.md` §10.6 item 5).

### 10.5 Deterministic proposal generation

The proposer's candidate set is computed by:

1. Read the work order's `required_gates`.
2. For each gate text, run `classify_execute_command` (deny-first, then allowlist).
3. Lexicographically sort the eligible set.
4. Truncate to three.
5. Hash the result.

No model call, no embedding lookup, no nondeterministic operation. (`PROPOSER-RUNTIME-v0.1.md` §3, §10 property 7.) **[IMPLEMENTED]**

### 10.6 Deterministic review hash

The reviewer's verdict is computed by:

1. Parse the proposal JSON.
2. Re-derive `deterministic_hash` from the proposal's stable subset.
3. Compare byte-for-byte to the proposal's claimed hash.
4. Re-classify each `commands_proposed` entry through deny-first then allowlist.
5. Apply the v0.1 reviewer-specific checks (rationale, command count, expected work-order id).
6. Emit decision + scope + reasons.
7. Hash the resulting artifact's stable subset.

No model call. (`REVIEW-GATE-RUNTIME-v0.1.md` §3, §10 property 7.) **[IMPLEMENTED]**

### 10.7 Fingerprint invariants

`repo_fingerprint(REPO_ROOT)` is sha256 over a fixed file set (§3.5). `tree_fingerprint(sandbox_path)` is sha256 over sorted `(relpath \x00 file_sha256 \x00)` tuples for every file under the sandbox.

Invariants:
- `repo_fingerprint_before == repo_fingerprint_after` (mandatory across every run).
- `sandbox_fingerprint_before` and `sandbox_fingerprint_after` differ only by what the subprocess actually wrote; the diff is recorded as `sandbox_files_changed`.

**[IMPLEMENTED]**

### 10.8 Byte-identical guarantees

The system claims byte-identical hashes for the same inputs. It does *not* claim byte-identical *bytes* on disk: timestamps, run identifiers, and absolute paths legitimately differ between runs. The hash excludes those. Byte-identical bytes are a property of the audit-stable subset only. (Each runtime spec L-7 makes this explicit.) **[IMPLEMENTED]**

---

## 11. Implemented vs unimplemented matrix

### 11.1 Implemented

- **Proposer runtime** — bounded candidate-command generation; 7 self-check fixtures pass; deterministic hash; opt-in via `make proposer-check`. **[IMPLEMENTED]**
- **Review gate runtime** — deterministic admission of proposer output; 8 self-check fixtures pass; hash re-derivation; opt-in via `make review-gate-check`. **[IMPLEMENTED]**
- **Executor runtime (v0.1 dry-run)** — admission, classification, sandbox copy, fingerprint, manifest emission, no subprocess. **[IMPLEMENTED]**
- **Executor runtime (v0.2 execute mode)** — `subprocess.run` invocation with `cwd=sandbox`, minimal env, bounded timeout, full stdout/stderr capture; 10 self-check fixtures; opt-in via `make real-agent-execute-check`. **[IMPLEMENTED]**
- **Pipeline runtime** — end-to-end orchestration of proposer → reviewer → executor; 8 self-check fixtures pass; aggregate hash; opt-in via `make pipeline-check`. **[IMPLEMENTED]**
- **Sandbox copy** — per-run `shutil.copytree` of the canonical repository under `workforce/real_agents/sandboxes/`. **[IMPLEMENTED]**
- **Sandbox tree fingerprint** — sha256 over sorted `(relpath, file_sha256)` tuples; before/after diff. **[IMPLEMENTED]**
- **Source-repo fingerprint invariance** — `repo_fingerprint(REPO_ROOT)` invariant before/after every run. **[IMPLEMENTED]** (policy-only enforcement).
- **Deterministic manifesting** — every layer's manifest carries a hash over its audit-stable subset; stability fixtures pass at every layer. **[IMPLEMENTED]**
- **Timeout enforcement** — wall-clock per-call, hard cap at 300 s, floor at 0.001 s. **[IMPLEMENTED]** (kernel-enforced kill).
- **OS isolation (macOS)** — `sandbox-exec` profile; deny-default; per-run binary allowlist; network deny; LaunchServices deny; 9 self-check fixtures pass. **[IMPLEMENTED]** **[KERNEL-ENFORCED]**.
- **Resource limits** — `RLIMIT_CPU`, `RLIMIT_NOFILE`, `RLIMIT_NPROC` kernel-enforced; `RLIMIT_AS` Linux-only; `os.setsid` + `os.killpg(SIGKILL)` process-tree termination; stdout/stderr byte cap with sha256; sandbox disk overrun detection; per-batch command count cap; 12 self-check fixtures pass. **[IMPLEMENTED]**.
- **Replay-mode forensic re-run** — `--replay` flag admits a `closed` work order under bounded conditions; manifest records `replay_mode: true`. **[IMPLEMENTED]**

### 11.2 Not implemented

- **Autonomous planning.** No LLM, no model call, no policy proposer in the runtime. The proposer derives candidates by string operations. **[EXPLICITLY UNSUPPORTED]**
- **Memory persistence across runs.** Each invocation is single-shot; no daemon, no cache, no database, no scratch directory. **[EXPLICITLY UNSUPPORTED]**
- **Daemonization.** No `os.fork` to detach, no `os.setsid` to detach (the bounded wrapper uses setsid only for kill semantics, not detachment), no `launchd` integration. **[EXPLICITLY UNSUPPORTED]**
- **Networked coordination.** No HTTP, no socket, no DNS lookup. The runtime cannot reach a remote host. **[EXPLICITLY UNSUPPORTED]**
- **Cryptographic attestation.** Manifests are unsigned plain JSON. No per-identity keys. No TPM. **[NOT IMPLEMENTED]** **[FUTURE WORK]**
- **Distributed replay verification.** Replay is single-host. No consensus, no quorum, no peer cross-check. **[NOT IMPLEMENTED]**
- **Multi-review quorum.** A single `approved` review artifact suffices. No Class C-style consensus over multiple reviewer identities. **[FUTURE WORK]** — `REVIEW-GATE-RUNTIME-v0.1.md` §12, `OS-ISOLATION-RUNTIME-v0.1.md` §10.6 item 8.
- **Firecracker / microVM isolation.** Not built. `OS-ISOLATION-RUNTIME-v0.1.md` §16 enumerates this as an aspirational "strongest possible" substrate. **[FUTURE WORK]**
- **Linux namespace isolation.** Not built. `unshare(CLONE_NEW*)`, seccomp, Landlock all candidate paths. **[FUTURE WORK]**
- **Hardware-rooted identity.** Identities are strings in `IDENTITIES`. No TPM, no hardware enclave, no Apple Silicon Secure Boot integration. **[EXPLICITLY UNSUPPORTED]**
- **Capability tokens.** No bearer token, no signed capability artifact, no cryptographically scoped grant. Identity is checked by string match. **[NOT IMPLEMENTED]**
- **Autonomous work selection.** The proposer takes a work-order path as a CLI argument. It does not enumerate `workforce/work_orders/open/`, does not pick "the next pending one." (`PROPOSER-RUNTIME-v0.1.md` §10 property 1.) **[EXPLICITLY UNSUPPORTED]**

### 11.3 Partial / asymmetric

- **`RLIMIT_AS` (memory).** **[KERNEL-ENFORCED]** on Linux; **[POLICY-ONLY]** post-hoc on macOS Tahoe (unprivileged setrlimit rejected).
- **Read-side syscall allowlist.** Profile allows broad reads. **[FUTURE WORK]** for narrow allowlist.
- **In-sandbox write enforcement of `allowed_files` glob.** Kernel allows any write inside sandbox; policy layer's `classify_write` is consulted only by code paths that go through it. **[POLICY-ONLY]**
- **Process-tree termination.** **[KERNEL-ENFORCED]** under bounded wrapper; **[POLICY-ONLY]** without.
- **`make ci` inclusion.** None of the runtime targets is on `make ci`. **[POLICY-ONLY]**

---

## 12. Explicit non-claims

The system does not claim any of the following. Each non-claim is explicit in at least one runtime spec; this section gathers them.

**12.1 This is NOT AGI.** The runtime does not contain a neural network. The proposer does not call a model. The reviewer does not call a model. The executor does not call a model. (`README.md`, `PROPOSER-RUNTIME-v0.1.md` §4, `REVIEW-GATE-RUNTIME-v0.1.md` §4.)

**12.2 This is NOT autonomous intelligence.** No layer selects its own work, plans across runs, or maintains state across runs. Each invocation is single-shot. (`PROPOSER-RUNTIME-v0.1.md` §10, `REAL-AGENT-RUNTIME-v0.2.md` §17 L-2, L-3.)

**12.3 This is NOT self-modifying AI.** The proposer cannot propose commands that edit itself or its outputs (`PROPOSER-RUNTIME-v0.1.md` §10 property 9, refusal code `recursive_self_modification`). The reviewer cannot. The pipeline cannot. The executor's command policy denies it.

**12.4 This is NOT unconstrained agency.** Every action requires a work-order admission. Every command must pass deny-first and allowlist. Every write must match `allowed_files`. (`REAL-AGENT-RUNTIME-v0.2.md` §5, §8, §9.)

**12.5 This is NOT secure against privileged operators.** An operator with write access to `tools/`, `reports/`, or `workforce/` can defeat any policy-layer protection. (`REAL-AGENT-RUNTIME-v0.2.md` §14.)

**12.6 This is NOT production-grade containment.** macOS sandbox profile leaves `(allow mach-lookup)` broad and reads broad. Memory limits are best-effort on macOS. `sandbox-exec` is deprecated. (`OS-ISOLATION-RUNTIME-v0.1.md` §10.4, §10.6.)

**12.7 This is NOT distributed consensus.** Single-host. No quorum. No multi-reviewer chain. No peer cross-validation. (`REVIEW-GATE-RUNTIME-v0.1.md` §12, `OS-ISOLATION-RUNTIME-v0.1.md` §10.6 item 8.)

---

## 13. Data flow and execution flow

End-to-end execution chain for one successful pipeline run.

### Step 1. Work order

A human owner writes `workforce/work_orders/<id>.yaml` with `status: drafted`. Required fields: `work_order_id`, `status`, `assigned_to`, `agent_role`, `objective`, `allowed_files[]`, `forbidden_files[]`, `required_gates[]`, `status_history[]`.

The owner approves the work order (`status: approved`), then assigns it to an identity (`status: assigned`). Both transitions are recorded in `status_history` with approver identity and timestamp. **[POLICY-ONLY]**

### Step 2. Proposal

`tools/proposer_runtime.py propose --work-order <path> --agent-id <id>` runs:

1. Reads the work order via the same flat-YAML reader the v0.2 executor uses.
2. Runs admission rules (`unknown_agent_identity`, `missing_required_field`, `status_not_admissible`, `assigned_to_mismatch`, `missing_allowed_files`, `missing_forbidden_files`).
3. For each entry in `required_gates`, calls `classify_execute_command` (deny-first, then allowlist).
4. Sorts admissible candidates lexicographically; truncates to three.
5. For each candidate, checks for path-outside-`allowed_files`, `recursive_self_modification`, `network_proposal`.
6. Builds the proposal record.
7. Computes `deterministic_hash` over the audit-stable subset.
8. Writes `reports/proposer_runtime/proposal-<run_id>.json` and `.md`.
9. Exits 0 if at least one command was proposed and no admission refusal occurred; 1 otherwise.

### Step 3. Review

`tools/review_gate_runtime.py review --proposal <path> [--expected-work-order-id <id>] [--reviewer-id <id>]` runs:

1. Reads the proposal JSON.
2. Validates required fields.
3. Re-derives the proposal's `deterministic_hash`; compares byte-for-byte to the claimed hash.
4. Validates the proposer identity against `IDENTITIES`.
5. Re-classifies every `commands_proposed` entry through deny-first then allowlist.
6. Checks command count ≤ 3.
7. Checks rationale non-empty.
8. If supplied, compares `--expected-work-order-id` to the proposal's `work_order_id`.
9. Builds the review artifact.
10. Computes `review_hash` over the audit-stable subset.
11. Writes `reports/review_gate_runtime/review-<run_id>.json` and `.md`.
12. Exits 0 on `decision="approved"`; 1 on `"rejected"`.

### Step 4. Execution admission

The executor (`tools/real_agent_runtime.py execute --work-order <path> --agent-id <id>`) re-runs admission. The reviewer's `approved` decision is *not* trusted as a substitute. Specifically:

1. Validates `agent_id ∈ IDENTITIES`.
2. Reads work-order yaml.
3. Validates required fields.
4. Validates `status ∈ identity.allowed_statuses` (or `replay_mode=True` AND status is exactly `closed`).
5. Validates `assigned_to == agent_id`.
6. Validates `allowed_files` and `forbidden_files` non-empty.

A failure at any step records the corresponding policy violation, no subprocess is spawned, and `exit_status = 1`.

### Step 5. Sandbox creation

On admission accept:

1. `sandbox_path = workforce/real_agents/sandboxes/real-agent-<run_id>-<temp>/`
2. `shutil.copytree(REPO_ROOT, sandbox_path, ignore=…)` with the v0.1 ignore filter.
3. `tree_fingerprint(sandbox_path) → sandbox_fingerprint_before`.
4. `repo_fingerprint(REPO_ROOT) → repo_fingerprint_before`.

The sandbox is the subprocess's `cwd`. **[IMPLEMENTED]**

### Step 6. Subprocess execution

For each command (from `required_gates` or `--command`):

1. `classify_execute_command(text)` runs deny-first, then allowlist.
2. If blocked: append to `commands_blocked`, no subprocess, status `"blocked"`.
3. If admitted: build the resolved argv (with `.venv/bin/python` rewriting if applicable).
4. (Optionally, under `tools/os_isolation_runtime.py`) generate sandbox profile, write to `reports/os_isolation_runtime/profiles/<sha256>.sb`, prepend `/usr/bin/sandbox-exec -f <profile>` to argv.
5. (Optionally, under `tools/resource_limit_runtime.py`) construct `preexec_fn` that calls `os.setsid()` then `setrlimit(CPU)`, `setrlimit(NOFILE)`, `setrlimit(NPROC)`, attempt `setrlimit(AS)`.
6. `subprocess.run(argv, cwd=sandbox, env=_minimal_env(), stdin=DEVNULL, stdout=PIPE, stderr=PIPE, timeout=<bounded>, shell=False, check=False)` (or `Popen.communicate(timeout=…)` under bounded wrapper).
7. On `subprocess.TimeoutExpired`: kill (process group under bounded wrapper); record `status="timed_out"`.
8. Capture stdout / stderr (truncated at 64 KiB; sha256 of truncated bytes under bounded wrapper).
9. Record duration_ms, exit_code, cwd, env_keys, timestamps, status.

### Step 7. Manifest recording

Per-command `command_results[i]` populated. Then:

1. `tree_fingerprint(sandbox_path) → sandbox_fingerprint_after`.
2. `sandbox_files_changed = diff(before, after)`.
3. `repo_fingerprint(REPO_ROOT) → repo_fingerprint_after`.
4. If `repo_fingerprint_before != repo_fingerprint_after`: append `repo_fingerprint_drift` to `policy_violations`.
5. Aggregate `gates_passed` / `gates_failed` from per-command results.
6. Compute `exit_status` (0 iff `policy_violations = []` AND all required gates passed).
7. Write `workforce/real_agents/runs/<run_id>.json`.
8. (Pipeline) Aggregate proposer + reviewer + executor manifests into `reports/pipeline_runtime/pipeline-<id>.json`. Compute `pipeline_hash`.
9. Delete sandbox unless `--preserve-sandbox`.

### Step 8. Closure

After the runtime stack returns, the work order's lifecycle continues through `executed → self_verified → gate_checked → reviewed → human_approved → closed`. Each transition is policy-layer; the runtime artifacts are evidence inputs to the governance flow.

### Step 9. Replay reconstruction

A future auditor reconstructs the run by:

1. Locate the closed work order at `workforce/work_orders/closed/<id>.yaml`.
2. Read `status_history` to identify approver identities and timestamps.
3. Locate the action log at `workforce/action_logs/<action_id>.{md,yaml}`.
4. Locate the self-verification block.
5. Locate the pipeline aggregate (referenced from the action log).
6. Locate the proposal, review, executor manifest (referenced from the aggregate).
7. Re-derive each hash and verify byte-equality.
8. Re-run each gate against the recorded artifacts; verify recorded outcome.
9. Verify `repo_fingerprint_before == repo_fingerprint_after` matches the recorded values.

If every check passes, the run is replay-validated. If any check fails, the run is a *replay-drift event* (`REPLAY-LAW-v0.1.md` §16). **[IMPLEMENTED]** at the per-run level for steps 5–9.

---

## 14. Threat model

### 14.1 What the system defends against

| Threat | Defense | Layer |
| --- | --- | --- |
| Unapproved command execution | classifier deny-first + sandbox-exec process-exec allowlist | policy + kernel |
| Network egress | classifier deny + sandbox-exec `(deny network*)` | policy + kernel |
| Filesystem write outside scope | `classify_write` + sandbox-exec write boundary | policy + kernel |
| App launch via `open -a` | classifier `open<space>` deny + LaunchServices `mach-lookup` deny | policy + kernel |
| Fork bomb | `RLIMIT_NPROC` | kernel |
| Stdout flood | 64 KiB cap + truncated-bytes sha256 | policy |
| Sandbox disk fill | `sandbox_size_limit_bytes` post-walk | policy (post-hoc) |
| Long-running batch | `command_count_limit` pre-execution | policy |
| Orphan child survival | `os.setsid` + `os.killpg(SIGKILL)` | kernel |
| CPU spin | `RLIMIT_CPU` | kernel |
| Fd table exhaustion | `RLIMIT_NOFILE` | kernel |
| Hash mutation (single artifact) | hash field excluded from hash input + reviewer re-derivation | policy |
| Mismatched work-order id | `wrong_work_order_id` reviewer rejection | policy |
| Recursive self-modification by proposer | `recursive_self_modification` proposer refusal | policy |
| Unknown identity | `unknown_agent_identity` admission refusal | policy |
| Status mismatch | `status_not_admissible` admission refusal | policy |
| Wrong identity for assignment | `assigned_to_mismatch` admission refusal | policy |
| Missing scope | `missing_allowed_files` / `missing_forbidden_files` | policy |
| Empty rationale | `empty_rationale` proposer refusal | policy |
| Forbidden command pattern | `forbidden_pattern` classifier refusal | policy |
| Command not in allowlist | `not_in_execute_allowlist` refusal | policy |

### 14.2 What it partially defends against

| Threat | Partial defense | Gap |
| --- | --- | --- |
| Memory exhaustion (macOS) | post-hoc `peak_rss_bytes` + `memory_overrun` violation | bytes were already allocated |
| Sandbox disk fill | post-walk `sandbox_size_overrun` | bytes were already written |
| In-sandbox write of arbitrary files | `classify_write` if invoked | kernel allows any write inside sandbox |
| Read-side scope | `classify_read` for code that consults it | kernel `(allow file-read*)` is broad |
| `mach-lookup` abuse | LaunchServices family denied | `(allow mach-lookup)` broad otherwise |
| Process-tree termination | bounded wrapper kills group | unbounded path kills only immediate child |

### 14.3 What it explicitly does not defend against

| Threat | Status | Citation |
| --- | --- | --- |
| Privileged operator subverting policy code | **[EXPLICITLY UNSUPPORTED]** | `REAL-AGENT-RUNTIME-v0.2.md` §14 |
| Manifest forgery (post-hoc edit by operator) | **[EXPLICITLY UNSUPPORTED]** at v0.2; **[FUTURE WORK]** signed manifests | `REAL-AGENT-RUNTIME-v0.2.md` §14 |
| Cross-run replay attack | **[NOT IMPLEMENTED]**; **[FUTURE WORK]** hash-chained manifests | `REAL-AGENT-RUNTIME-v0.2.md` §14 |
| Hardware-rooted identity spoofing | **[EXPLICITLY UNSUPPORTED]** | `REAL-AGENT-RUNTIME-v0.2.md` §14 |
| Side channels (timing, page faults) | **[EXPLICITLY UNSUPPORTED]** | `OS-ISOLATION-RUNTIME-v0.1.md` §10.4 |
| Kernel rootkit / sandbox.kext bug | **[EXPLICITLY UNSUPPORTED]** | `OS-ISOLATION-RUNTIME-v0.1.md` §10.4 |
| Sandbox-exec deprecation | **[FUTURE WORK]** Endpoint Security migration | `OS-ISOLATION-RUNTIME-v0.1.md` §10.4 |
| Multi-reviewer collusion | **[NOT IMPLEMENTED]**; **[FUTURE WORK]** Class-C-style quorum | `REVIEW-GATE-RUNTIME-v0.1.md` §12 |

---

## 15. Future enforcement ladder

The runtime specs collectively enumerate the ladder of stronger enforcement that future versions could climb. None of these is authorized by current work orders; each requires its own drafted-approved-assigned governance work order.

### 15.1 v0.3 candidates (incremental)

- **Process group + setrlimit on every executor invocation.** Currently only via the bounded-resource wrapper; v0.3 could roll it into the v0.2 default path.
- **macOS Endpoint Security migration.** Replace `sandbox-exec` with ES profiles; equivalent semantics but on a non-deprecated substrate.
- **Linux backend for OS isolation.** `unshare(CLONE_NEW*)` with seccomp-bpf and Landlock for filesystem narrowing; equivalent kernel-enforced syscall allowlist.
- **Read-side syscall allowlist.** Replace `(allow file-read*)` with a per-run subpath set narrower than the sandbox.
- **Fine-grained `mach-lookup` allowlist.** Invert the current "allow + four denies" to "deny + explicit allow list."
- **Per-WO `allowed_files` enforcement at syscall time.** Generate per-WO profiles whose write clauses match the work-order glob.

### 15.2 v0.4 candidates (substrate change)

- **Linux user namespaces.** `CLONE_NEWUSER | CLONE_NEWNS | CLONE_NEWNET | CLONE_NEWIPC | CLONE_NEWUTS | CLONE_NEWPID` for full process namespacing.
- **seccomp-bpf** filtering at syscall numbers + arguments.
- **Landlock** for filesystem narrowing.
- **Bind-mount sandbox into a minimal chroot / pivot_root.**
- **Container backend.** `podman` / `containerd` rootless containers.

### 15.3 v0.5+ candidates (strong substrates)

- **Firecracker microVM.** Snapshotted root filesystem; KVM-based isolation.
- **cloud-hypervisor** alternative microVM.
- **Apple containerization (WWDC 2024).** macOS-native lightweight VM.

### 15.4 Cross-cutting (any version)

- **Cryptographic signatures on manifests.** Per-identity Ed25519 keys; signature over the recorded hash.
- **Hash-chained manifests.** Each manifest commits to the prior manifest's hash, mirroring `Class A` lineage in `SPEC.md` §3.
- **Multi-review quorum.** Mirror Class C: require ≥N `approved` review artifacts under distinct reviewer identities before the executor admits.
- **Distributed replay verification.** Cross-host re-derivation; each host independently re-derives every hash and reaches a consensus on validity.
- **Capability-scoped identities.** Each invocation receives a signed, time-bounded capability token rather than a string identity match.
- **Attested execution.** TPM- or Apple-Silicon-Secure-Boot-rooted attestation chain; the kernel attests its own state.
- **Network-egress proof in manifest.** Record (and prove) "no network call attempted" — currently denied at syscall time but not affirmatively recorded.

All items in this section are **[FUTURE WORK]** unless otherwise noted.

---

## 16. Diagrams

### 16.1 Lifecycle diagram

See §7. (Reproduced for completeness.)

```
drafted → approved → assigned → executed → self_verified → gate_checked
                                                  │
                                                  ▼
                                              reviewed → human_approved → closed
                                                  │
                                                  ▼ (any state)
                                              refused
```

### 16.2 Runtime boundary map

```
┌──────────────────────────────────────────────────────────────┐
│ Operator shell                                               │
└────┬─────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│ tools/pipeline_runtime.py                                   │
│   imports: tools/proposer_runtime, review_gate_runtime,     │
│            real_agent_runtime                                │
│   does NOT import: subprocess, socket, urllib                │
└────┬─────────────────────────────────────────────────────────┘
     │ in-process call
     ▼
┌─────────────────────────────────────────────────────────────┐
│ tools/proposer_runtime.py                                    │
│   imports: stdlib + real_agent_runtime classifier constants  │
│   writes: reports/proposer_runtime/proposal-*.json           │
└────┬─────────────────────────────────────────────────────────┘
     │ on-disk handoff (JSON file)
     ▼
┌─────────────────────────────────────────────────────────────┐
│ tools/review_gate_runtime.py                                 │
│   imports: stdlib + real_agent_runtime constants             │
│   reads: proposal-*.json                                     │
│   writes: reports/review_gate_runtime/review-*.json          │
└────┬─────────────────────────────────────────────────────────┘
     │ on-disk handoff (JSON file)
     ▼
┌─────────────────────────────────────────────────────────────┐
│ tools/real_agent_runtime.py (execute mode)                   │
│   imports: subprocess, shutil, hashlib, ...                  │
│   reads: work_order, sandbox copy                            │
│   spawns: subprocess.run (THE ONE SUBPROCESS)                │
│   writes: workforce/real_agents/runs/run-*.json              │
└────┬─────────────────────────────────────────────────────────┘
     │ optional outer wrapper
     ▼
┌─────────────────────────────────────────────────────────────┐
│ tools/os_isolation_runtime.py     (sandbox-exec wrapper)     │
│ tools/resource_limit_runtime.py   (setrlimit + setsid)       │
└─────────────────────────────────────────────────────────────┘
```

### 16.3 Proposal / review / execute chain

```
work_order.yaml
     │
     │  proposer reads, classifies, sorts, caps
     ▼
proposal-<id>.json   [ deterministic_hash ]
     │
     │  reviewer reads, re-hashes, re-classifies
     ▼
review-<id>.json     [ review_hash, decision ∈ {approved, rejected} ]
     │
     │  if rejected → STOP; pipeline records refused_at_review
     │  if approved → continue
     ▼
executor admission (re-runs admission rules)
     │
     │  if refused → STOP; pipeline records refused_at_executor
     │  if admitted
     ▼
sandbox copy
     │
     ▼
subprocess.run (optionally wrapped by sandbox-exec, optionally bounded)
     │
     ▼
executor manifest under workforce/real_agents/runs/
     │
     ▼
pipeline aggregate under reports/pipeline_runtime/   [ pipeline_hash ]
```

### 16.4 Manifest dependency graph

```
work_order.yaml
   │
   │  ←── referenced by all four below
   │
   ├──► proposal-<id>.json
   │       │ (proposer_artifact path)
   │       │ (proposer_hash)
   │       ▼
   ├──► review-<id>.json
   │       │ (review_artifact path)
   │       │ (review_hash, deterministic_hash_verified)
   │       ▼
   ├──► executor manifest
   │       │ (executor_manifest path)
   │       │ (executor_manifest_hash)
   │       │ (sandbox_fingerprint_before, sandbox_fingerprint_after)
   │       │ (repo_fingerprint_before, repo_fingerprint_after)
   │       ▼
   └──► pipeline aggregate
           │ (pipeline_hash over all of the above)
           │ (final_status ∈ {executed, executed_with_violations,
           │                   refused_at_review, refused_at_executor})
           ▼
       (action log links into governance closure)
```

### 16.5 Kernel vs policy enforcement map

```
                         Operation
                            │
                            ▼
              ┌─────────────────────────────┐
              │   Ring 1: Policy classifier │   POLICY-ONLY (Python)
              │   classify_execute_command  │
              │   classify_read / write     │
              │   admission rules           │
              │   identity match            │
              │   hash re-derivation        │
              │   command count cap         │
              │   rationale validation      │
              └─────────────┬───────────────┘
                            │ admitted
                            ▼
              ┌─────────────────────────────┐
              │   Ring 2: sandbox-exec      │   KERNEL-ENFORCED (macOS)
              │   process-exec allowlist    │
              │   write boundary            │
              │   network deny              │
              │   LaunchServices deny       │
              │   default deny              │
              └─────────────┬───────────────┘
                            │ syscall permitted
                            ▼
              ┌─────────────────────────────┐
              │   Ring 3: setrlimit + setsid│   KERNEL-ENFORCED (rlimits)
              │   RLIMIT_CPU                │   POLICY-ONLY (post-hoc on macOS for AS)
              │   RLIMIT_NOFILE             │
              │   RLIMIT_NPROC              │
              │   RLIMIT_AS (Linux only)    │
              │   killpg(SIGKILL) on timeout│
              │   stdout/stderr cap         │
              │   sandbox disk overrun      │
              │   command count cap         │
              └─────────────┬───────────────┘
                            │
                            ▼
                       Subprocess executes
```

### 16.6 Replay reconstruction flow

```
Auditor                             Artifact tree
  │                                       │
  ├── read closed work-order yaml ────────┤
  │                                       │
  ├── read action log ────────────────────┤
  │                                       │
  ├── read self-verification block ───────┤
  │                                       │
  ├── read pipeline aggregate ────────────┤
  │     │                                 │
  │     ├── follow proposer_artifact ─────┤
  │     │     │                           │
  │     │     └── re-derive               │
  │     │         deterministic_hash ─────┤  byte-equal?
  │     │                                 │
  │     ├── follow review_artifact ───────┤
  │     │     │                           │
  │     │     └── re-derive review_hash ──┤  byte-equal?
  │     │                                 │
  │     ├── follow executor_manifest ─────┤
  │     │     │                           │
  │     │     ├── verify                  │
  │     │     │   repo_fingerprint_before │
  │     │     │   == repo_fingerprint_after│
  │     │     │                           │
  │     │     └── re-derive               │
  │     │         executor_manifest_hash ─┤  byte-equal?
  │     │                                 │
  │     └── re-derive pipeline_hash ──────┤  byte-equal?
  │                                       │
  └── verdict ◄───────────── replay-validated  if all checks pass
                            replay-drift event if any check fails
```

---

## 17. Appendices

### 17.1 Glossary

| Term | Meaning |
| --- | --- |
| **Admission** | The act of validating a work order's identity, status, scope, and assignment fields before any further operation proceeds. |
| **Allowlist match** | A command-text match of exact equality OR starts-with-allowed-entry-followed-by-space against `EXECUTE_ALLOWED_COMMANDS`. |
| **Audit-stable subset** | The fields of an artifact over which a deterministic hash is computed; excludes `timestamp`, run identifiers, and the hash field itself. |
| **Class A/B/C/D** | The four epistemic verification regimes in `SPEC.md` §3 — deterministic, instrumented-empirical, protocol-bound consensus, interpretive governance. |
| **Closure** | Terminal lifecycle state reached when all governance preconditions are met (action log, self-verification, gates, reviewer finding, human approval). |
| **Deny-first** | The first stage of command policy: a match against `FORBIDDEN_COMMAND_PATTERNS` blocks the command before the allowlist is consulted. |
| **Deterministic hash** | A sha256 over the audit-stable subset of an artifact; identical for identical inputs. |
| **Execute mode** | The v0.2 executor mode that actually invokes `subprocess.run`; distinct from the v0.1 dry-run mode that classifies but does not invoke. |
| **Fail closed** | Property that any unexpected condition produces `exit_status = 1` and a recorded refusal code; never fails open with silent success. |
| **Fingerprint** | Aggregate sha256 over a tree (sandbox or canonical-repo file set). |
| **Identity** | A stable string keyed into `IDENTITIES` that names the acting agent for admission purposes. Not bound to a hardware key. |
| **Kernel-enforced** | A constraint enforced by the host kernel (via sandbox-exec profile or setrlimit). Defeated only by a kernel bug. |
| **Manifest** | A per-run JSON record of every input, decision, and output for one invocation of one runtime layer. |
| **Pipeline aggregate** | The end-to-end JSON record spanning proposer + reviewer + executor for one work order. |
| **Policy-only** | A constraint enforced by Python code in this repository; not enforced by the host kernel. |
| **Process group** | Set of processes sharing a session id created by `os.setsid()`; `os.killpg(SIGKILL)` terminates the entire group. |
| **Proposal record** | The per-run JSON written by the proposer, containing candidate commands, deterministic hash, and policy rejections. |
| **Replay** | Reconstruction of an operation's full chain from the artifact set alone, without operator testimony. |
| **Resource limit** | A `setrlimit`-applied or post-hoc-detected bound on subprocess resource consumption. |
| **Review artifact** | The per-run JSON written by the reviewer gate, containing decision, approval scope, rejection reasons, and review hash. |
| **Sandbox** | Per-run directory copy of the canonical repository, created via `shutil.copytree`; the subprocess's `cwd`. |
| **Sandbox profile** | TinyScheme-style file consumed by `/usr/bin/sandbox-exec`; defines the kernel-enforced syscall allowlist. |
| **Self-check fixture** | A test case under a runtime's `run_self_check` function; produces a per-run manifest and a pass/fail entry in the runtime report. |
| **Source-repo fingerprint** | Aggregate sha256 over a fixed seven-file set (`SPEC.md`, `STATUS-REGISTRY.md`, `ARTIFACTS.md`, `CONFORMANCE.md`, `Makefile`, `tools/check_workforce.py`, `tools/check_no_pseudocode.py`). |
| **Sandbox tree fingerprint** | Aggregate sha256 over sorted `(relpath, file_sha256)` tuples for every file under the sandbox. |
| **Sandbox-exec** | macOS binary at `/usr/bin/sandbox-exec` that loads a profile and applies it to a child process. Marked deprecated by Apple. |
| **Work order** | YAML file under `workforce/work_orders/` declaring the unit of authorization for one agent action. |

### 17.2 Identity table

| Identity | Layer(s) | Role | Source |
| --- | --- | --- | --- |
| `canon_guardian-01` | proposer / executor | canon authority | `IDENTITIES` |
| `reviewer-01` | proposer / executor | reviewer agent | `IDENTITIES` |
| `builder-01` | proposer / executor | builder | `IDENTITIES` |
| `release-01` | proposer / executor | release authority | `IDENTITIES` |
| `review-gate-01` | review gate | deterministic admission filter | `REVIEW-GATE-RUNTIME-v0.1.md` §6 |

### 17.3 Runtime table

| Runtime | Spec | Code | Self-check fixtures | Make target |
| --- | --- | --- | --- | --- |
| Proposer | `PROPOSER-RUNTIME-v0.1.md` | `tools/proposer_runtime.py` | 7 | `make proposer-check` |
| Review gate | `REVIEW-GATE-RUNTIME-v0.1.md` | `tools/review_gate_runtime.py` | 8 | `make review-gate-check` |
| Real-agent (dry-run) | `REAL-AGENT-RUNTIME-v0.1.md` | `tools/real_agent_runtime.py` | (v0.1 fixtures) | `make real-agent-check`, `make real-agent-dry-run` |
| Real-agent (execute) | `REAL-AGENT-RUNTIME-v0.2.md` | `tools/real_agent_runtime.py` | 10 | `make real-agent-execute`, `make real-agent-execute-check` |
| Pipeline | `PIPELINE-RUNTIME-v0.1.md` | `tools/pipeline_runtime.py` | 8 | `make pipeline-check`, `make pipeline-run-fixture` |
| OS isolation | `OS-ISOLATION-RUNTIME-v0.1.md` | `tools/os_isolation_runtime.py` | 9 | `make os-isolation-check`, `make os-isolation-fixture` |
| Resource limits | `RESOURCE-LIMIT-RUNTIME-v0.1.md` | `tools/resource_limit_runtime.py` | 12 | `make resource-limit-check`, `make resource-limit-fixture` |

### 17.4 Manifest table

| Manifest | Path | Hash field | Spec |
| --- | --- | --- | --- |
| Proposal | `reports/proposer_runtime/proposal-*.json` | `deterministic_hash` | `PROPOSER-RUNTIME-v0.1.md` §6 |
| Review | `reports/review_gate_runtime/review-*.json` | `review_hash` | `REVIEW-GATE-RUNTIME-v0.1.md` §6 |
| Executor (v0.1 dry-run) | `workforce/real_agents/runs/run-*.json` | (16 v0.1 fields) | `REAL-AGENT-RUNTIME-v0.1.md` §11 |
| Executor (v0.2 execute) | `workforce/real_agents/runs/run-*.json` | (v0.1 + v0.2 fields) | `REAL-AGENT-RUNTIME-v0.2.md` §11 |
| Pipeline aggregate | `reports/pipeline_runtime/pipeline-*.json` | `pipeline_hash` | `PIPELINE-RUNTIME-v0.1.md` §6 |
| Isolation per-run | `reports/os_isolation_runtime/runs/run-*.json` | `sandbox_profile_hash` | `OS-ISOLATION-RUNTIME-v0.1.md` §7 |
| Resource-limit per-run | `reports/resource_limit_runtime/runs/run-*.json` | `stdout_hash`, `stderr_hash` (truncation), plus inherited | `RESOURCE-LIMIT-RUNTIME-v0.1.md` §7 |
| Runtime self-check report | `reports/<runtime>/<runtime>_v0.1.json` | (per-fixture hashes inline) | each runtime spec §8 |

### 17.5 Gate table

| Gate | Spec / source | Default in `make ci` | Opt-in target |
| --- | --- | --- | --- |
| `make no-pseudocode` | `tools/check_no_pseudocode.py` | yes | n/a |
| `make workforce-check` | `tools/check_workforce.py` | no | `make workforce-check` |
| `make canonicalization-check` | `canonicalization/tools/verify_golden.py` | yes | n/a |
| `make conformance` | `tools/run_conformance.py` | yes | `make conformance` |
| `make interop` | `interop/scripts/*` | yes | `make interop` |
| `pytest tests/` | `tests/` | yes (via `make test` in `make ci`) | `make test` |
| `make real-agent-check` | `tools/real_agent_runtime.py check` | no | `make real-agent-check` |
| `make real-agent-execute-check` | `tools/real_agent_runtime.py execute-check` | no | `make real-agent-execute-check` |
| `make proposer-check` | `tools/proposer_runtime.py self-check` | no | `make proposer-check` |
| `make review-gate-check` | `tools/review_gate_runtime.py self-check` | no | `make review-gate-check` |
| `make pipeline-check` | `tools/pipeline_runtime.py self-check` | no | `make pipeline-check` |
| `make os-isolation-check` | `tools/os_isolation_runtime.py self-check` | no | `make os-isolation-check` |
| `make resource-limit-check` | `tools/resource_limit_runtime.py self-check` | no | `make resource-limit-check` |

### 17.6 Refusal-code table

(Subset; full lists are in each runtime spec §7 or §13.)

| Code | Source | Trigger |
| --- | --- | --- |
| `unknown_agent_identity` | admission | identity not in `IDENTITIES` |
| `missing_required_field` | admission | WO missing `work_order_id` or `status` |
| `status_not_admissible` | admission | WO status not in identity's `allowed_statuses` |
| `assigned_to_mismatch` | admission | WO `assigned_to` not equal to acting identity |
| `missing_allowed_files` | admission | WO `allowed_files` empty/missing |
| `missing_forbidden_files` | admission | WO `forbidden_files` empty/missing |
| `forbidden_pattern` | classifier | command matches `FORBIDDEN_COMMAND_PATTERNS` |
| `not_in_execute_allowlist` | classifier | command does not match `EXECUTE_ALLOWED_COMMANDS` |
| `path_outside_allowed_files` | proposer | candidate's path token not in `allowed_files` |
| `recursive_self_modification` | proposer | candidate references proposer module / report tree / spec |
| `network_proposal` | proposer | candidate references HTTP / SSH / network commands |
| `empty_rationale` | proposer / reviewer | rationale field empty |
| `cap_exceeded` | proposer | candidate-eligible set > 3 (cap applied) |
| `empty_proposal` | proposer | every candidate rejected |
| `proposal_file_missing` | reviewer | `--proposal` path not found |
| `proposal_json_invalid` | reviewer | proposal not parseable |
| `deterministic_hash_mismatch` | reviewer | recomputed hash ≠ claimed hash |
| `wrong_work_order_id` | reviewer | `--expected-work-order-id` mismatch |
| `unknown_proposer` | reviewer | proposer's `agent_id` not in `IDENTITIES` |
| `forbidden_command` | reviewer | proposed command matches forbidden pattern |
| `too_many_commands` | reviewer | `commands_proposed` length > 3 |
| `no_commands_to_approve` | reviewer | proposer's `commands_proposed` empty |
| `unreadable_proposer_runtime_version` | reviewer | proposal `runtime_version != "v0.1"` |
| `command_blocked` | executor | command blocked by classifier |
| `gate_failed` | executor | required gate non-zero exit or timeout |
| `command_timed_out` | executor | non-gate command exceeded timeout |
| `command_error` | executor | non-gate command subprocess error |
| `repo_fingerprint_drift` | executor | source-repo fingerprint changed during run |
| `memory_overrun` | resource-limit | `peak_rss_bytes` > `memory_limit_bytes` |
| `sandbox_size_overrun` | resource-limit | sandbox size > `sandbox_size_limit_bytes` |
| `cpu_time_exhausted` | resource-limit | CPU time bound reached |
| `command_count_overflow` | resource-limit | batch commands > `command_count_limit` |

### 17.7 Filesystem policy table

| Path scope | Read | Write |
| --- | --- | --- |
| Inside `sandbox_path` | allowed | allowed if matches `allowed_files` AND not `forbidden_files` |
| `reports/real_agent_runtime/` | allowed | allowed (runtime-internal output) |
| `forbidden_files` | denied | denied |
| `default_denied_paths` (per identity) | denied | denied |
| Anywhere else outside sandbox | denied if not on read scope | denied |
| Standing-forbidden paths (`SPEC.md`, `vectors/**`, `Makefile`, etc.) | allowed at `classify_read` (advisory) | denied unless `human_approval_required: true` work order |

### 17.8 Syscall denial table (macOS sandbox-exec)

| Operation | Default | Allowed exception |
| --- | --- | --- |
| `execve` of any binary | denied | `(allow process-exec (literal "<target>"))` only |
| `execve` of `/bin/bash` when target is `/bin/sh` | allowed | variant routing |
| `open`, `openat` for read | broadly allowed | `(allow file-read*)` |
| `open`, `openat` for write outside sandbox | denied | `/dev/null`, `/dev/dtracehelper` literals only |
| `open`, `openat` for write inside sandbox | allowed | `(allow file-write* (subpath sandbox))` |
| `socket`, `bind`, `connect`, `listen`, `sendto`, `recvfrom`, `sendmsg`, `recvmsg` | denied | none |
| `mach_lookup` of `com.apple.coreservices.launchservicesd` | denied | none |
| `mach_lookup` of `com.apple.lsd.{mapdb,modifydb,openurls}` | denied | none |
| `mach_lookup` of other services | broadly allowed | n/a (this is a known coarseness) |
| `sysctl` read | allowed | n/a |
| POSIX shared memory | allowed | n/a |
| `iokit-open` | allowed | n/a |
| `signal` to self | allowed | n/a |
| Default (any operation not above) | denied | n/a |

### 17.9 Invariant table

| Invariant | Source |
| --- | --- |
| `repo_fingerprint_before == repo_fingerprint_after` | `REAL-AGENT-RUNTIME-v0.2.md` §7 |
| Proposer's `commands_proposed` length ≤ 3 | `PROPOSER-RUNTIME-v0.1.md` §6 |
| Proposer's `commands_proposed` lexicographically sorted | `PROPOSER-RUNTIME-v0.1.md` §3 |
| Two same-input proposer runs produce equal `deterministic_hash` | `PROPOSER-RUNTIME-v0.1.md` fixture 7 |
| Two same-input reviewer runs produce equal `review_hash` | `REVIEW-GATE-RUNTIME-v0.1.md` fixture 8 |
| Two same-input pipeline runs produce equal `pipeline_hash` | `PIPELINE-RUNTIME-v0.1.md` fixture 7 |
| Same-input sandbox profile produces equal hash | `OS-ISOLATION-RUNTIME-v0.1.md` fixture 9 |
| Reviewer rejection ⇒ executor not invoked | `PIPELINE-RUNTIME-v0.1.md` fixture 8 |
| `reviewer-01` cannot grant execution authority | `REVIEW-GATE-RUNTIME-v0.1.md` §9 |
| Source repo unchanged after pipeline run | `PIPELINE-RUNTIME-v0.1.md` fixture 6 |
| `subprocess.run` always called with `cwd=sandbox`, `shell=False`, `stdin=DEVNULL`, bounded `timeout` | `REAL-AGENT-RUNTIME-v0.2.md` §6 |
| Timeout cap: 0.001 ≤ timeout ≤ 300.0 seconds | `REAL-AGENT-RUNTIME-v0.2.md` §12 |
| Proposer module imports no `subprocess`, `socket`, `urllib` | `PROPOSER-RUNTIME-v0.1.md` §5 |
| Reviewer module imports no `subprocess`, `socket`, `urllib` | `REVIEW-GATE-RUNTIME-v0.1.md` §5 |
| Pipeline module imports no `subprocess`, `socket`, `urllib` | `PIPELINE-RUNTIME-v0.1.md` §5 |

---

## 18. What is actually real today

This section is the document's terminal commitment. Reviewers and adopters who read only this section should leave with a calibrated picture of the system's truth.

### 18.1 Conceptual

These are commitments and laws, not running code. They determine the shape of everything below.

- **WiseOrder Protocol kernel.** Class A/B/C/D verification regimes, JCS canonicalization, action governance separation (AG1–AG3). (`SPEC.md`.) The kernel governs the form of legitimate epistemic artifacts; it does not, by itself, run anything.
- **Six-commitment thesis.** Governance before execution; replayability over intelligence; determinism over claims; bounded authority; refusal > silent failure; admissibility before capability. (§2.) These are design commitments verifiable against the runtime specs and reports.
- **Two-runtime architecture.** Cognition (Intellagent) governs the flow of *claims*; execution (this stack) governs the flow of *side effects*. Both inherit the kernel laws. This document covers the second.
- **Replay-as-infrastructure.** A record either replays or it does not (`REPLAY-LAW-v0.1.md` §5 Principle 8). Replay is governed at the same level as execution.

### 18.2 Policy-enforced (Python; defeatable by privileged operator)

These are constraints that fire because Python code in this repository checks them. A hostile operator with write access to `tools/`, `reports/`, or `workforce/` can defeat any of them. They survive only honest operators.

- Work-order admission (`unknown_agent_identity`, `missing_required_field`, `status_not_admissible`, `assigned_to_mismatch`, `missing_allowed_files`, `missing_forbidden_files`).
- Identity table — `IDENTITIES` is a Python dict; `assigned_to == agent_id` is a string match.
- Forbidden-pattern command deny set (`sudo`, `curl`, `wget`, `ssh`, `scp`, `git push`, `rm -rf`, etc.).
- Execute allowlist (`pwd`, `ls`, `find`, `cat`, the four script-call entries, the three make entries).
- `classify_read` and `classify_write` over `allowed_files` / `forbidden_files` globs.
- Proposer cap of three, lexicographic sort, recursive-self-modification check, network-proposal check, empty-rationale refusal.
- Reviewer hash re-derivation, command-count check, expected-work-order-id check, unknown-proposer check.
- Pipeline orchestration (refusal flows; no path skipping the reviewer).
- Source-repo fingerprint invariance (computed in Python; compared in Python).
- Sandbox tree fingerprint and `sandbox_files_changed` diff.
- Manifest emission, deterministic hashing, replay-stable byte structure (sorted keys, indent 2, trailing newline).
- Refusal codes — every layer raises typed refusals; none silently succeeds.
- Lifecycle ordering and `status_history` append-only convention.

### 18.3 Subprocess-enforced (subprocess.run parameters)

These are constraints that fire because of how `subprocess.run` (or `Popen`) is called. They are stronger than policy-only because they bind even if the policy classifier was wrong about admission.

- `shell=False` — no shell expansion, no globbing, no environment substitution beyond what `argv` provides.
- `cwd=sandbox_path` — relative paths resolve into the sandbox copy.
- `stdin=subprocess.DEVNULL` — the subprocess cannot read from operator's terminal.
- `stdout=PIPE`, `stderr=PIPE` with 64 KiB byte cap and truncation flags.
- `timeout=<bounded float ∈ (0.001, 300.0]>` — wall-clock kill.
- `check=False` — runtime records exit code; never raises.
- Minimal env: `PATH`, `LC_ALL=C`, `LANG=C`, optional `PYTHONPATH`. Nothing else propagated. (`HOME`, `USER`, `SHELL`, `AWS_*`, `OPENAI_*`, `GITHUB_*`, all proxy variables — explicitly excluded.)

### 18.4 Kernel-enforced (sandbox-exec + setrlimit, on macOS only at v0.1)

These fire at syscall time. The Python runtime is bypassed; the host kernel is the gatekeeper. Defeated only by a kernel bug or by removing the kernel-isolation wrapper.

- `(deny default)` — every operation not explicitly allowed returns `EPERM`.
- `(deny process-exec*)` plus per-target `(allow process-exec (literal …))` — only the resolved target binary may exec; nested exec of any other binary fails.
- `(deny file-write*)` plus `(allow file-write* (subpath sandbox))` — writes outside the sandbox subpath fail.
- `(deny mach-lookup (global-name "com.apple.coreservices.launchservicesd"))` plus three siblings — `open -a <App>` cannot reach the LaunchServices launcher.
- `(deny network*)` — no socket creation.
- `RLIMIT_CPU` — child receives `SIGXCPU` then `SIGKILL` on CPU-time overrun.
- `RLIMIT_NOFILE` — `open()` past cap returns `EMFILE`.
- `RLIMIT_NPROC` — `fork()` past cap returns `EAGAIN`.
- `os.setsid()` + `os.killpg(SIGKILL)` — entire process group dies on timeout.

### 18.5 Aspirational (NOT real today)

These are explicitly named in the runtime specs as `Future Work`, `Not Real`, or `Security Non-Guarantees`. They are *not* present in code. A reader who sees them claimed elsewhere has been misled.

- Cryptographic signatures on manifests.
- Hash-chained manifests linking run N to run N+1.
- Distributed replay verification.
- Multi-reviewer quorum (Class C-style consensus).
- Linux namespace isolation, seccomp-bpf, Landlock.
- Firecracker / cloud-hypervisor / containerd microVM substrates.
- Apple Endpoint Security migration (away from deprecated `sandbox-exec`).
- Hardware-rooted identity (TPM or Apple Silicon Secure Boot integration).
- Capability tokens (signed, time-bounded).
- Attested execution.
- Read-side syscall allowlist.
- Fine-grained `mach-lookup` allowlist (current profile is broad).
- Per-WO `allowed_files` glob enforced at syscall time.
- Pre-execution memory enforcement on macOS (currently post-hoc via `peak_rss_bytes`).
- Disk-write quota during execution (`RLIMIT_FSIZE`); currently post-walk only.
- Per-batch cumulative rlimits (current limits are per-process).
- Network-egress proof in manifest (currently denied at syscall time but not affirmatively recorded).
- Cross-host attestation.
- Autonomous work selection.
- Persistent agent memory across runs.
- Daemonization or scheduled re-entry.
- Networked coordination, RPC, model calls, LLM integration.
- Inclusion of any v0.1/v0.2 runtime target in `make ci`.

### 18.6 The honest one-line summary

The system is a single-host, opt-in, deterministic, audit-anchored, classifier-gated, sandbox-exec-isolated, setrlimit-bounded, JSON-manifested governed-execution stack on macOS — that does not run autonomously, does not call models, does not reach the network, does not survive privileged operators, and does not yet have cryptographic anti-tamper, multi-reviewer quorum, cross-host attestation, or microVM containment.

Everything else is **[FUTURE WORK]**.

---

**End of WISEORDER SYSTEMS ARCHITECTURE v1.**
