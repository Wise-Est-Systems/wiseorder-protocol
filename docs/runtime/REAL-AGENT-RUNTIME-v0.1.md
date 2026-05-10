# REAL AGENT RUNTIME v0.1
## Local Sandboxed Worker Execution For Governed Work Orders

**Status:** v0.1 — operational specification, normative for `tools/real_agent_runtime.py` and the `workforce/real_agents/` tree. Non-overlapping with WiseOrder, Intellagent, runtime, validator, workflow, authority, forbidden-surface, and waiver semantics. This document does not redefine those layers; it specifies the local OS-process boundary under which a role-labeled "agent" becomes a bounded executing process whose file access, commands, outputs, logs, and closure artifacts are constrained by enforceable runtime boundaries.
**Companion documents:** `WORKFORCE-EXECUTION-RUNTIME-v0.1.md` (lifecycle + records), `AGENT-GOVERNANCE-WORKFORCE-v0.1.md` (roles + authority), `WORKFORCE-HARDENING-v0.2.md` (validator hardening), `WORKFORCE-SANDBOX-STRESS-v0.1.md` (record-level pressure suite), `WAIVER-MECHANISM-v0.1.md` (sanctioned exception class), `FORBIDDEN-SURFACES-v0.1.md` (non-authority surface), `VALIDATION-LAW-v0.1.md`, `REPLAY-LAW-v0.1.md`, `TRUST-LAW-v0.1.md`.

> **Core thesis.** Agents become real only when role labels become bounded executing processes whose file access, commands, outputs, logs, and closure artifacts are constrained by enforceable runtime boundaries.

> **Explicitly stated.**
>
> - **This does not create autonomous AI agents yet.**
> - **This creates the first local process boundary for governed worker execution.**
> - **The runtime enforces that no agent execution exists without an approved work order, an assigned identity, a sandbox, an allowed command set, and a machine-checkable run manifest.**

---

## 1. Purpose

This document defines the first local sandboxed worker runtime for the WiseOrder / Intellagent stack. Until v0.1 of this runtime, "agents" in the workforce documentation were role labels in YAML — `canon_guardian`, `reviewer`, `release`, `builder` — with no associated executing process, no enforceable scope, and no OS-level boundary. Every prior closure cycle's record-level discipline was load-bearing on operator self-discipline; nothing prevented an unscoped read or write at the operating-system level.

The Real Agent Runtime carves out a single, narrow surface: a **dry-run-only** local process that admits an approved-and-assigned work order, creates a fresh sandboxed copy of the repository, applies a deny-by-default command and filesystem policy under a named agent identity, and produces a machine-checkable run manifest. It does not yet execute commands. It does not yet replace the validator. It does not yet make agents autonomous. It establishes the single property that has been missing: that "agent" is a process with a boundary, not a string in a YAML file.

The runtime is governance-anchored. It refuses to admit any work order whose status, assignment, or scope fields are inconsistent with the rules in `WORKFORCE-EXECUTION-RUNTIME-v0.1.md`. It refuses any command outside a fixed allowlist. It refuses any write outside a sandbox path or `reports/real_agent_runtime/`. It produces a manifest that records every attempted command, every blocked command, every file-policy outcome, and every gate verdict, with an exit status of zero if and only if all admission and policy checks pass.

The runtime is bounded. v0.1 supports dry-run only. Real execution, real model integration, real autonomous planning, real network access, real persistence, and real key-attested identity are explicit non-goals enumerated below.

---

## 2. Why Real Agents Require Runtime Boundaries

Operational legitimacy depends on the property that an agent's actions are bounded, recorded, and replayable per `WORKFORCE-EXECUTION-RUNTIME-v0.1.md` §1. Until this runtime, that property was enforced only by record (the action log) and by validator (`tools/check_workforce.py`). The OS-level enforcement layer — the layer that would prevent an agent from reading `SPEC.md` or writing `intellagent_runtime/kernel.py` even if the operator forgot to disallow it — did not exist.

This is not a defect of the prior runtime. It is the v0.1 enforcement gap that `WORKFORCE-EXECUTION-RUNTIME-v0.1.md` §27 names as future enforcement: "the runtime does not prevent an agent from reading or writing a forbidden file at the OS level. Enforcement is by record (action log) and by validator, both of which depend on the agent honestly reporting its activity."

Real agents — agents that actually execute commands, read files, write artifacts — require a runtime boundary because:

1. An honest record of dishonest behavior is still dishonest behavior. The validator inspects what the agent reports; it does not inspect what the agent did.
2. A scoped agent that has the OS-level ability to read everything is scoped only by its own discipline. Discipline that holds in normal operation does not necessarily hold under bug, fatigue, optimization pressure, or model error.
3. Trust accumulation per `TRUST-LAW-v0.1.md` §3 is the property that bounded continuity holds across pressure. Pressure includes operator pressure, time pressure, and model pressure. A boundary that only exists in record collapses under pressure that isn't recording-bound.
4. Replay continuity per `REPLAY-LAW-v0.1.md` §1 requires that an operation be reconstructable from record alone. If the operating system enforces nothing, the record is the only evidence — and the record is itself produced by the agent. Self-evidence is not evidence.

The boundary this runtime establishes is the smallest thing that converts "agent" from label to process: a fresh sandbox per run, a deny-by-default command policy, a deny-by-default filesystem policy, and a manifest that an outside party can inspect.

---

## 3. Difference Between Role Labels And Executing Agents

A **role label** is a string in a YAML field (`agent_role: canon_guardian` or `assigned_to: canon_guardian-01`). It carries no execution authority. It is governance metadata; the validator inspects it for consistency, but it does not run anything.

An **executing agent** is a local OS process with:

- a named identity (e.g., `canon_guardian-01`) that maps to a permission profile,
- a per-run sandbox path constructed by copying the repository under `workforce/real_agents/sandboxes/`,
- a deny-by-default command policy enforced before any command is issued,
- a deny-by-default filesystem policy that refuses writes outside the sandbox or `reports/real_agent_runtime/`,
- a run manifest produced at start, updated during execution, and finalized at exit, recording every attempted command, every gate run, every file accessed, and every policy violation.

Until v0.1 of this runtime, the workforce had only role labels. The validator interpreted them, the action logs cited them, and the closure summaries referenced them — but no process ever bore them. v0.1 of this runtime introduces the first step toward executing agents: a dry-run executor that applies the full policy enforcement layer without yet running real commands. The dry-run is not the destination; it is the floor on which real execution can later be built.

---

## 4. v0.1 Scope

### In Scope

- Standard-library-only Python implementation at `tools/real_agent_runtime.py`.
- Local execution only (subprocess invocations limited to gate validation; no dry-run side effects).
- No network calls (no `urllib.request.urlopen`, no `socket.connect` to remote hosts, no `subprocess` calls to network-touching commands).
- Deny-by-default file access enforced against per-WO `forbidden_files` and per-identity default-denied paths.
- Admission of approved-and-assigned work orders; refusal of drafted, unassigned, closed, or wrong-identity work orders.
- Per-run sandbox creation under `workforce/real_agents/sandboxes/` via `shutil.copytree`.
- Per-run manifest under `workforce/real_agents/runs/<run_id>.json` with the 16 required fields.
- Self-check fixture suite covering 10 admission and policy cases.
- Reports at `reports/real_agent_runtime/real_agent_runtime_v0.1.{md,json}`.
- Two Makefile targets: `make real-agent-check` (run self-check + write reports), `make real-agent-dry-run WO=<path> AGENT=<id>` (admit + sandbox + dry-run a specific WO under a specific identity).
- Fail-closed behavior: any policy violation returns non-zero exit status and records a `policy_violations` entry in the manifest.

### Out Of Scope For v0.1

- Real command execution. v0.1 logs commands as would-execute; it does not invoke them. The single exception is the runtime's own gate self-checks (`make no-pseudocode`, `make workforce-check`) which the runtime references in its manifests but does not itself invoke.
- Autonomous planning. The runtime executes only the work order's declared `required_gates` plus the documented allowed-command set; it does not select, schedule, or invent steps.
- Model calls. The runtime does not call any LLM, classifier, or external service.
- Background daemon. The runtime is a one-shot CLI; no persistent process.
- Secret access. The runtime does not read environment variables, credential files, or secret stores.
- `git push`, network commands, destructive commands (`rm -rf` outside `/tmp`, `chmod`, `chown`, `open`, `curl`, `wget`, `ssh`, `scp`).
- Deletion of source repo files. The runtime never writes to or deletes anything outside its per-run sandbox or `reports/real_agent_runtime/`.
- Modification of the canonical source repository, except where the human owner copies an artifact from the sandbox into the canonical repo through a separate (non-runtime) operation.
- Adding the runtime to `make ci`. v0.1 stays out of `make ci` until cross-machine reproducibility (per `reports/NEXT-3-EARNED-MOVES-v0.1.md` EARN-2) is established. The runtime is opt-in via `make real-agent-check` and `make real-agent-dry-run`.

---

## 5. Agent Identity Model

Four identities are declared in v0.1:

| Identity | Role | Allowed work-order statuses | Default-denied paths (in addition to per-WO forbidden_files) | Allowed commands | Forbidden command patterns |
| --- | --- | --- | --- | --- | --- |
| `canon_guardian-01` | `canon_guardian` | `approved`, `assigned` | `runtime/`, `intellagent_runtime/`, `vectors/`, `canonicalization/corpus/`, `tools/`, `Makefile`, `SPEC.md` | `pwd`, `ls`, `find`, `cat`, `python3`, `.venv/bin/python`, `make no-pseudocode`, `make workforce-check` | `sudo`, `curl`, `wget`, `ssh`, `scp`, `git push`, `git reset --hard`, `git clean`, `rm -rf`, `chmod`, `chown`, `open`, `http://`, `https://` |
| `reviewer-01` | `reviewer` | `approved`, `assigned` | `runtime/`, `intellagent_runtime/`, `vectors/`, `canonicalization/corpus/`, `tools/` | (same allowed-command set) | (same forbidden patterns) |
| `builder-01` | `builder` | `approved`, `assigned` | `vectors/`, `canonicalization/corpus/`, `SPEC.md` | (same allowed-command set) | (same forbidden patterns) |
| `release-01` | `release` | `approved`, `assigned` | `vectors/`, `canonicalization/corpus/`, `intellagent_runtime/` | (same allowed-command set) | (same forbidden patterns) |

Every identity declares all five required fields: `role`, `allowed_statuses`, `default_denied_paths`, `allowed_commands`, `forbidden_commands`. The identity table is the runtime's canonical permission profile; modifying it requires a hardening cycle work order under `WORKFORCE-HARDENING-v0.2.md` (or v0.3+) with the full lifecycle.

Identities are scoped, not authoritative. A `canon_guardian-01` invocation against a work order that is `assigned_to: release-01` is refused at admission with refusal code `assigned_to_mismatch`. A `release-01` invocation against a work order in status `drafted` is refused with `status_not_admissible`. Identity is the door key; the work order is the room. Without both, no admission.

---

## 6. Work Order Admission Rules

Admission is a single function with a single return value: `accepted: bool` plus a `refusal_code` (empty when accepted). The runtime applies the following rules in order; first-match denies admission:

1. **`unknown_agent_identity`** — the requested `agent_id` is not in the identity table.
2. **`missing_required_field`** — the work order is missing `work_order_id` or `status`.
3. **`status_not_admissible`** — the work order's `status` is not in the identity's `allowed_statuses` (i.e., not `approved` or `assigned`). This refuses `drafted`, `executed`, `self-verified`, `gate-checked`, `reviewed`, `human_approved`, `closed`, `rejected`, and any unknown state.
4. **`assigned_to_mismatch`** — the work order's `assigned_to` is empty or does not equal `agent_id`. This refuses unassigned work orders and wrong-identity invocations.
5. **`missing_allowed_files`** — the work order has no `allowed_files` list, or the list is empty.
6. **`missing_forbidden_files`** — the work order has no `forbidden_files` list, or the list is empty.

A work order that passes all six checks is admitted. Admission does not authorize execution; it authorizes sandbox creation and policy enforcement.

The runtime does not distinguish between `approved` and `assigned` for admission purposes; both are admissible when the assignment is consistent with the agent identity. Per `WORKFORCE-EXECUTION-RUNTIME-v0.1.md` lifecycle, `approved` precedes `assigned`; the runtime accepts both because in practice the `assigned_to` field may be filled at either point.

---

## 7. Sandbox Model

A sandbox is a fresh per-run copy of the repository at a path under `workforce/real_agents/sandboxes/`. Construction:

1. The runtime computes a `run_id` of the form `run-<timestamp>-<agent_id>`.
2. The runtime creates a temp directory under `workforce/real_agents/sandboxes/` via `tempfile.mkdtemp(prefix="real-agent-<run_id>-", dir=...)`.
3. The runtime copies the repository tree into the sandbox via `shutil.copytree(REPO_ROOT, sandbox_path, ignore=...)`. The ignore filter excludes `.venv/`, `venv/`, `.git/`, `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `node_modules/`.
4. The sandbox path is recorded in the run manifest's `sandbox_path` field.
5. After the dry-run completes, the sandbox is deleted via `shutil.rmtree` unless the operator passed `--preserve-sandbox`.

Sandboxes are isolated per run. No two runs share a sandbox. A run that mutates the sandbox does not mutate the canonical repository because the sandbox is a copy, not a reference.

The repository fingerprint is computed before and after the dry-run by hashing a fixed set of files (`SPEC.md`, the SPEC extracts, the Makefile, the validator scripts) and verifying that the post-run fingerprint equals the pre-run fingerprint. Any drift records a `repo_fingerprint_drift` policy violation. v0.1 dry-run never mutates the canonical repo, so the fingerprint check is informational; in a future real-execution release, the check is load-bearing.

---

## 8. Command Policy

Commands are classified by two-stage policy:

1. **Forbidden patterns first.** Any command whose text contains any of the forbidden patterns (`sudo`, `curl`, `wget`, `ssh`, `scp`, `git push`, `git reset --hard`, `git clean`, `rm -rf`, `chmod`, `chown`, `open `, `http://`, `https://`) is blocked, regardless of any other property. This is the deny-first layer.
2. **Allowlist match.** A command not blocked by step 1 is admitted only if it matches an entry in the allowed-command set: `pwd`, `ls`, `find`, `cat`, `python3`, `.venv/bin/python`, `make no-pseudocode`, `make workforce-check`. Match means exact equality or starts-with the allowed entry followed by a space.

A command that fails either stage is recorded in the manifest's `commands_blocked` list with the failing reason and contributes to `policy_violations`. The dry-run continues to evaluate remaining commands; it does not abort on first block. The exit status is non-zero if any command was blocked or any other policy violation occurred.

The forbidden patterns are not hypothetical. Each one corresponds to a class of operation that has caused harm in real-world systems: privilege escalation (`sudo`), data exfiltration (`curl`, `wget`, network URLs), credential theft (`ssh`, `scp`), source-tree corruption (`git push`, `git reset --hard`, `git clean`), filesystem destruction (`rm -rf`), permission tampering (`chmod`, `chown`), application launch outside scope (`open `).

---

## 9. Filesystem Policy

The runtime applies separate read and write policies.

**Read policy (`classify_read`):**

- A read of any path matched by the work order's `forbidden_files` glob is blocked with reason `forbidden_files pattern '<P>' matched`.
- A read of any path matched by the identity's `default_denied_paths` is blocked with reason `identity default-denied path '<P>' matched`.
- All other reads are admitted.

**Write policy (`classify_write`):**

- A write to any path outside the per-run sandbox path AND outside `reports/real_agent_runtime/` is blocked with reason `write target outside sandbox or reports/real_agent_runtime/`.
- A write to any path matched by the work order's `forbidden_files` is blocked with the same forbidden-pattern reason.
- A write to any path matched by the work order's `allowed_files` is admitted.
- All other writes (paths in neither allowed_files nor forbidden_files, but inside the sandbox/reports area) are blocked with reason `write target not in allowed_files`.

The write policy is intentionally narrower than the read policy. Reads default-allow within scope; writes default-deny without explicit allowed_files match. This asymmetry reflects the asymmetry of damage: a read can leak; a write can corrupt.

The runtime does not enforce file-content correctness, schema validity, or canonicalization. Those concerns belong to the validator, the canonicalization tool, and the conformance suite. The runtime enforces only path-policy admission.

---

## 10. Action Logging

Every dry-run produces a single per-run manifest at `workforce/real_agents/runs/<run_id>.json`. The manifest is the action log of the run; the validator's notion of action logs (under `workforce/action_logs/`) is the per-work-order record, distinct from the per-run manifest. The two are complementary:

- The per-WO action log records the work-order lifecycle: drafting, approval, assignment, execution, closure. It is governed by `WORKFORCE-EXECUTION-RUNTIME-v0.1.md` §8.
- The per-run manifest records the runtime's policy verdicts: which commands were attempted, which were allowed, which were blocked, which files were planned read/changed, which gates ran, which policy violations occurred. It is governed by this document §11.

The two records cite each other: a closed work order's action log records `make real-agent-dry-run` invocations and references the resulting `<run_id>.json` manifests; the manifest records the work_order_id it admitted. This is the v0.1 cross-reference; future hardening cycles may add cryptographic attestation linking the two.

---

## 11. Run Manifest

Every per-run manifest MUST contain the following 16 fields:

1. `run_id` — string of the form `run-<timestamp>-<agent_id>`.
2. `work_order_id` — the admitted work order's id, or empty if admission failed.
3. `agent_id` — the identity under which the run was attempted.
4. `sandbox_path` — absolute path to the sandbox copy, or empty if admission failed.
5. `repo_fingerprint_before` — `sha256:<hex>` of the canonical repo's fixed file set at run start.
6. `repo_fingerprint_after` — `sha256:<hex>` at run end. MUST equal `repo_fingerprint_before` for a clean dry-run.
7. `commands_attempted` — list of every command the runtime considered.
8. `commands_allowed` — subset of `commands_attempted` that passed command policy.
9. `commands_blocked` — subset that failed command policy, each with `command` and `reason`.
10. `files_read` — list of file paths the runtime classified as read targets (v0.1 dry-run logs would-read paths; v0.2+ may log actual reads).
11. `files_changed` — list of file paths the runtime classified as write targets.
12. `gates_run` — list of gate names attempted.
13. `gates_passed` — subset of `gates_run` that the command policy admitted.
14. `gates_failed` — subset that the command policy blocked.
15. `policy_violations` — list of policy-violation records, each with `code` and `reason` (and optional `command` or `path`).
16. `exit_status` — integer; 0 if admission accepted and no policy violations; 1 otherwise.

In addition, the manifest records: `timestamp_start`, `timestamp_end`, `runtime_version`, and `dry_run` (boolean, always `true` in v0.1).

The manifest is JSON. It is human-readable, machine-parseable, and replayable. The validator does not yet enforce manifest schema; that enforcement is a candidate hardening cycle work order.

---

## 12. Dry-Run Execution

A dry-run is a non-mutating evaluation of admission, sandbox creation, command policy, filesystem policy, and gate-set classification under a named agent identity for a named work order. Dry-run does not invoke commands.

Procedure:

1. Read the work-order YAML from disk.
2. Apply admission rules (§6). On refusal, write a manifest with `policy_violations` populated and `exit_status: 1`; return.
3. On admission acceptance, compute `repo_fingerprint_before`.
4. Create a sandbox copy of the repo (§7).
5. For each gate in `required_gates`, classify the gate command (§8); record outcome in manifest.
6. For each pattern in `forbidden_files`, sanity-check that `classify_read` blocks it; record any policy inconsistency.
7. Compute `repo_fingerprint_after`; verify it equals `repo_fingerprint_before`.
8. Set `exit_status` based on accumulated policy violations.
9. Write the manifest to `workforce/real_agents/runs/<run_id>.json`.
10. Delete the sandbox unless `--preserve-sandbox` was passed.

Dry-run is repeatable and deterministic. The same work order under the same agent identity produces identical admission verdicts, identical command classifications, and identical policy outcomes (modulo timestamps and run_id).

The CLI: `python3 tools/real_agent_runtime.py dry-run --work-order <PATH> --agent-id <ID> [--preserve-sandbox]`. The Makefile target: `make real-agent-dry-run WO=<PATH> AGENT=<ID>`.

---

## 13. Failure Modes

The runtime fails closed in the following cases:

| Failure mode | Source | Manifest record | Exit status |
| --- | --- | --- | --- |
| Unknown agent identity | CLI / API | `policy_violations: [{code: unknown_agent_identity}]` | 1 |
| Missing required WO field | Admission | `policy_violations: [{code: missing_required_field}]` | 1 |
| WO status not admissible | Admission | `policy_violations: [{code: status_not_admissible}]` | 1 |
| `assigned_to` mismatch / empty | Admission | `policy_violations: [{code: assigned_to_mismatch}]` | 1 |
| Missing `allowed_files` | Admission | `policy_violations: [{code: missing_allowed_files}]` | 1 |
| Missing `forbidden_files` | Admission | `policy_violations: [{code: missing_forbidden_files}]` | 1 |
| Forbidden command pattern matched | Command policy | `commands_blocked: [{...}]` + `policy_violations: [{code: command_blocked}]` | 1 |
| Command not in allowlist | Command policy | same shape | 1 |
| Forbidden file read | Filesystem policy | `policy_violations: [{code: forbidden_file_read}]` (logged in dry-run when fixture exercises it) | 1 |
| Write outside sandbox / reports | Filesystem policy | `policy_violations: [{code: write_outside_sandbox}]` | 1 |
| Repo fingerprint drift | Sandbox / dry-run | `policy_violations: [{code: repo_fingerprint_drift}]` | 1 |
| Self-check fixture mismatch | `check` / `self-check` | console output enumerates failed cases | 1 |
| Configuration violation (missing dir/spec/Makefile target/identity) | `check` | console output enumerates violations | 1 |

The runtime never fails open. Any unexpected condition that the runtime cannot classify produces an explicit Python exception that surfaces to the operator with traceback; the CLI does not swallow exceptions silently.

---

## 14. Security Non-Guarantees

The runtime does NOT yet provide:

- **OS-level sandboxing.** The sandbox is a directory copy, not a kernel container, jail, or namespace. An agent process with sufficient OS privilege could still escape the sandbox path.
- **Process isolation.** The runtime runs in the operator's user account; any privilege the operator has, the runtime inherits.
- **Network isolation.** The runtime does not invoke network commands, but it does not prevent another process on the same host from doing so.
- **Cryptographic attestation.** The manifest is plain JSON; it is not signed. An attacker with write access to `workforce/real_agents/runs/` can edit a manifest after the fact.
- **Tamper detection on action logs.** The per-WO action log is not hash-chained to the per-run manifest. A manifest-action-log mismatch is detectable only by manual review.
- **Hardware-rooted identity.** Agent identities are strings in a Python dict; they are not bound to any hardware key, TPM, or secure enclave.
- **Anti-replay protection.** The runtime does not detect the same work order being dry-run twice with conflicting outcomes; both manifests are written and both are valid records.
- **Resource limits.** The runtime does not bound memory, CPU, file-descriptor count, or wall-clock time.
- **Audit-chain integrity across runs.** Each manifest is independent; no chain links one manifest to the next.

Each non-guarantee is a known v0.1 enforcement gap. Several are addressed by the audit's P3 entry `AGENT-IDENTITY-v0.1.md` (cryptographic identity), by future hardening cycles (OS-level sandboxing, resource limits), or by future runtime versions of this document. v0.1 establishes the boundary; later versions strengthen it.

---

## 15. What This Does Not Yet Prove

This runtime does NOT prove:

- That an autonomous agent can plan, propose, and execute a work order from end to end. v0.1 is dry-run-only; the agent does not act, only declares.
- That a real-execution agent can be safely run on the canonical repo. v0.1 sandboxes copies; v0.2+ may attempt real execution under tighter OS-level controls.
- That a model-driven proposer can be wired into the runtime without smuggling authority. The proposer architecture from `INTELLAGENT-PROPOSERS.md` is the constraint surface; integration into this runtime is a future work item.
- That the workforce validator and the real-agent runtime agree on every edge case. Cross-validation between `tools/check_workforce.py` and `tools/real_agent_runtime.py` is a candidate hardening cycle.
- That the runtime survives adversarial pressure. The 900-check workforce stress suite (`WORKFORCE-SANDBOX-STRESS-v0.1.md`) does not yet target this runtime; a successor stress harness for the real-agent surface is a future candidate.
- That cross-machine reproducibility holds for runtime manifests. Per `reports/NEXT-3-EARNED-MOVES-v0.1.md` EARN-2, cross-machine reproducibility for the entire stack is a separate work item.
- That the runtime's manifest is byte-deterministic across runs. Timestamps and run_ids vary; the policy outcomes are deterministic but the manifest as a whole is not byte-stable.

The runtime's contribution is bounded: it converts "agent" from string to bounded process for one specific case (dry-run admission + policy enforcement). Every other property remains future work.

---

## 16. Future Enforcement

The following are candidate work items that build on this runtime:

- **R-1.** Real command execution under sandbox isolation. Migrate from dry-run-only to actual subprocess invocation inside the sandbox path with `subprocess.run(..., cwd=sandbox_path, env=<minimal>, timeout=<bounded>)`.
- **R-2.** OS-level isolation. Bind the sandbox to a UNIX user namespace, container, or jail; prevent process escape.
- **R-3.** Cryptographic attestation. Sign manifests with the agent identity's key (per `AGENT-IDENTITY-v0.1.md`, the audit's P3 entry).
- **R-4.** Hash-chained manifests. Link each manifest to its predecessor by sha256, producing a tamper-evident audit chain across runs.
- **R-5.** Resource limits. Bound memory, CPU, file-descriptor count, and wall-clock time per `subprocess.run(..., resource_limits=...)`.
- **R-6.** Cross-validation with `tools/check_workforce.py`. Run both validators on the same WO + action-log fixture and assert agreement.
- **R-7.** Adversarial pressure suite. Extend `WORKFORCE-SANDBOX-STRESS-v0.1.md`'s harness to exercise this runtime's admission and policy rules against 900 fixtures.
- **R-8.** Manifest schema validator. Add a `tools/check_real_agent_manifests.py` that enforces the 16-field schema on every manifest under `workforce/real_agents/runs/`.
- **R-9.** Inclusion in `make ci`. Once R-1 through R-8 are credible, add `make real-agent-check` to `make ci`.
- **R-10.** Per-identity capability matrix. Extend the identity table to per-identity allowed-write-glob and per-identity allowed-gate sets, refining beyond the current uniform allowed-command list.

None of R-1 through R-10 is authorized by this document. Each requires its own drafted, approved, and assigned governance work order under `AGENT-GOVERNANCE-WORKFORCE-v0.1.md` §3 and `WORKFORCE-HARDENING-v0.2.md` (or v0.3+).

---

## 17. Final Law

The runtime is bounded by the following ten law statements. They are this document's terminal commitments; everything above is implementation.

**L-1. Agents become real only when role labels become bounded executing processes.** A string in a YAML field is not an agent. A process with a sandbox, a policy, a manifest, and a refusal mode is.

**L-2. No agent execution exists without an approved work order, an assigned identity, a sandbox, an allowed command set, and a machine-checkable run manifest.** Any one of these missing breaks the runtime contract; the runtime refuses admission.

**L-3. The runtime denies by default.** Commands not in the allowlist are denied. Writes outside the sandbox or `reports/real_agent_runtime/` are denied. Reads of `forbidden_files` patterns are denied. Identity defaults are denied unless the work order opens them.

**L-4. The runtime fails closed.** Any policy violation produces a non-zero exit status and a recorded `policy_violations` entry. Silence on a violation is forbidden.

**L-5. The runtime does not redesign WiseOrder, Intellagent, runtime, validator, workflow, or authority semantics.** It adds a new local OS-process layer that enforces those semantics; it does not modify them.

**L-6. The runtime is dry-run only in v0.1.** Real command execution, real model integration, real autonomous planning, real network access, real persistence, and real key-attested identity are all out of scope for v0.1.

**L-7. The runtime does not create autonomous AI agents.** It establishes the first local process boundary for governed worker execution. Autonomy is not a v0.1 property.

**L-8. The runtime is not added to `make ci` in v0.1.** It is opt-in via `make real-agent-check` and `make real-agent-dry-run`. Inclusion in `make ci` requires meeting the EARN-1 / EARN-2 cross-machine reproducibility floor first.

**L-9. The runtime's manifest is the per-run audit-trail anchor.** Every command attempted, every block, every policy verdict, every gate verdict, and every fingerprint is recorded. Replay continuity per `REPLAY-LAW-v0.1.md` requires that an outside reviewer can reconstruct the run from the manifest alone.

**L-10. The runtime is governance-anchored, not capability-anchored.** Its purpose is not to do more; its purpose is to bound what can be done. A runtime that broadens what an agent may do is anti-runtime under this law; only narrowing under explicit governance is forward motion.

These ten law statements are the runtime's normative commitments. They name the boundary between role label and executing process, refuse the failure modes the protocol exists to refuse, and establish the smallest local-process surface on which future hardening cycles can be built.

---

**End of REAL AGENT RUNTIME v0.1.**
