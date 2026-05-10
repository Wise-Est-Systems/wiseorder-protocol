# WO-2026-05-07-005 — Real Agent Runtime Replay Dry-Run Report v0.1

**Runtime spec:** `REAL-AGENT-RUNTIME-v0.1.md`
**Runtime implementation:** `tools/real_agent_runtime.py`
**Target work order:** `workforce/work_orders/closed/WO-2026-05-07-005.yaml`
**Target identity:** `canon_guardian-01`
**Mode:** dry-run only (no subprocess execution; no model calls; no network)
**Run id:** `run-20260508T134314Z-canon_guardian_01`
**Manifest:** `workforce/real_agents/runs/run-20260508T134314Z-canon_guardian_01.json` (mirrored at `reports/real_agent_runtime/wo005_dry_run_manifest_v0.1.json`)
**Timestamp (UTC):** `2026-05-08T13:43:14Z`

> **Headline.** The runtime refused admission of WO-2026-05-07-005 with refusal code `status_not_admissible` because its status is `closed` and `canon_guardian-01`'s `allowed_statuses` are `('approved', 'assigned')`. This refusal is the legitimacy result, not a failure: closure is enforced at the runtime layer, not only at the validator/record layer. Replay continuity holds; closure legitimacy remained intact; the policy layer succeeded on every classification it was asked to make.

> **Explicit non-claims.**
> - **No real shell execution occurred.** The runtime did not invoke `subprocess` to run any command. The classifier-level simulation in §7–§8 used only pure Python policy functions.
> - **No subprocess command execution occurred.** Not for `pwd`, not for `ls`, not for `make no-pseudocode`, not for `make workforce-check`, not for any blocked command.
> - **This validates governance admission continuity, not autonomous execution capability.** Autonomy and real execution are explicit v0.1 non-goals (`REAL-AGENT-RUNTIME-v0.1.md` §15).
> - **Replay continuity held.** The pre/post repository fingerprint is identical and the canonical work-order file is byte-unchanged.
> - **Closure legitimacy remained intact.** The closed work order was not re-admitted, not re-executed, not re-graded; it was classified as inadmissible-for-replay-execution.
> - **Policy-layer enforcement succeeded.** Every command, every read target, and every write target was classified by the deny-by-default policy with the verdict the spec requires.
> - **Kernel isolation still does not exist.** Per `REAL-AGENT-RUNTIME-v0.1.md` §14, OS-level sandboxing, namespace/jail isolation, signed manifests, hardware-rooted identity, and resource limits are still future enforcement (R-2, R-3, R-5).

---

## 1. Purpose

The purpose of this dry-run is to test, against a real historical work order from the closed bucket, whether the v0.1 Real Agent Runtime correctly preserves three properties simultaneously:

1. **Replay-admission discipline.** Closed work orders must not be quietly re-admittable for execution simply because their YAML is well-formed. The runtime must distinguish between *parsing* a closed work order (allowed) and *running* it again (refused).
2. **Closure legitimacy.** The cryptographic-not-yet-but-record-preserving property that closure is the terminal state, recorded with actor and timestamp in `status_history`, and cannot be undone by re-invocation under the runtime.
3. **Deny-by-default policy enforcement at the classifier level.** Even when admission would otherwise have succeeded, the command policy and filesystem policy must classify allowed and forbidden inputs with the verdicts the v0.1 spec mandates.

The target is `WO-2026-05-07-005` — the work order under which `WAIVER-MECHANISM-v0.1.md` was authored, executed, gate-checked, reviewed, human-approved, and closed on 2026-05-08. Its lifecycle has nine recorded states (drafted → approved → assigned → executed → self-verified → gate-checked → reviewed → human_approved → closed), each with actor and timestamp. The deliverable exists at the canonical path. Both required gates (`make no-pseudocode`, `make workforce-check`) were green at execution time and remain re-runnable. Replay reconstruction from the work-order YAML, the action logs, and the closure summary is straightforward — by record. This dry-run asks whether replay reconstruction is also permitted, *as execution*, by the runtime layer. The answer must be: no.

## 2. Why Real Historical Replay Matters

Until this run, every Real Agent Runtime exercise had used either fixtures (the ten admission cases under `SELF_CHECK_CASES`) or the synthetic built-in fixture (`_BUILTIN_FIXTURE_YAML`). Both are approved-and-assigned by construction; both exit the runtime through the *accepted* admission path. None had been pointed at a historical, closed, real work order.

Real historical replay matters because it tests the runtime's behavior against the only artifact class that the validator, the action logs, and the closure summaries do not themselves prevent re-execution of: a work order whose lifecycle has terminated but whose YAML is still on disk, still parseable, still well-formed, and still naming a valid identity. A naive runtime would happily admit such a work order — its `assigned_to` matches, its `allowed_files` and `forbidden_files` are populated, its required gates are sane — and produce an accepted dry-run that *looks* correct while actually re-invoking governance against an artifact whose governance has already terminated.

The v0.1 admission rule that refuses non-`approved`/non-`assigned` statuses is the property that prevents that drift. Until exercised against a real historical work order, the rule was load-bearing only in self-check fixtures. After this run, it is load-bearing against an artifact the workforce actually produced.

The second reason real historical replay matters is that the **work order's declared scope is itself a load-bearing record of what the agent was once permitted to do**. By exercising the policy classifiers against that recorded scope without admitting the work order, the runtime demonstrates that scope and admission are independent surfaces: scope is durable record; admission is a runtime decision keyed on lifecycle state. The two must compose to permit execution; either alone is insufficient.

## 3. Work Order Admission

**Admission verdict:** **REFUSED**
**Refusal code:** `status_not_admissible`
**Reason:** `work order WO-2026-05-07-005 status 'closed' is not admissible for canon_guardian-01 (allowed: ['approved', 'assigned'])`
**Manifest field `exit_status`:** `1`

Verification of the work-order content prior to admission:

| Field | Required | Observed | Pass |
| --- | --- | --- | :-: |
| `work_order_id` | non-empty string | `WO-2026-05-07-005` | PASS |
| `status` | non-empty string | `closed` | PASS (well-formed) |
| `assigned_to` | non-empty string equal to agent id | `canon_guardian-01` | PASS |
| `allowed_files` | non-empty list | `["*.md", "workforce/**", "reports/**"]` | PASS |
| `forbidden_files` | non-empty list | `["runtime/**", "intellagent_runtime/**", "vectors/**", "canonicalization/**", "tools/**", "Makefile", "SPEC.md"]` | PASS |
| `required_gates` | list | `["make no-pseudocode", "make workforce-check"]` | PASS |

**Lifecycle ordering.** `status_history` records nine states in the canonical order required by `WORKFORCE-EXECUTION-RUNTIME-v0.1.md`:
`drafted → approved → assigned → executed → self-verified → gate-checked → reviewed → human_approved → closed`. Each state carries actor and ISO-8601 UTC timestamp. The lifecycle is well-formed.

**Why admission still refuses.** The runtime's admission rule §6.3 (`status_not_admissible`) executes before any other field-level rule in the rule set could conditionally accept the work order. Closure, executed, self-verified, gate-checked, reviewed, human_approved, drafted, rejected, and any unrecognized state are all refused; only `approved` and `assigned` are admissible. The runtime treats the closed work order as a well-formed historical artifact whose lifecycle has terminated and refuses to re-admit it for execution. The refusal carries the correct refusal code and a human-readable reason naming both the offending state and the identity's allowed-status set.

This is the load-bearing closure property: a closed work order is a record, not a re-runnable program.

## 4. Identity Validation

| Property | Value |
| --- | --- |
| Identity name | `canon_guardian-01` |
| Role | `canon_guardian` |
| `allowed_statuses` | `('approved', 'assigned')` |
| `default_denied_paths` | `runtime/`, `intellagent_runtime/`, `vectors/`, `canonicalization/corpus/`, `tools/`, `Makefile`, `SPEC.md` |
| `allowed_commands` | `pwd`, `ls`, `find`, `cat`, `python3`, `.venv/bin/python`, `make no-pseudocode`, `make workforce-check` |
| `forbidden_command_patterns` | `sudo`, `curl`, `wget`, `ssh`, `scp`, `git push`, `git reset --hard`, `git clean`, `rm -rf`, `chmod`, `chown`, `open `, `http://`, `https://` |

The identity is recognized by the runtime's `IDENTITIES` table; the `assigned_to` field on the work order matches the requested identity id; no `unknown_agent_identity` or `assigned_to_mismatch` refusal applies. Identity validation is independently green; the refusal is purely a status-axis refusal.

## 5. Filesystem Validation

The runtime did not enter the post-admission filesystem-policy phase, because admission was refused. To establish that the policy classifier *would* have correctly enforced the work order's declared scope, the public `classify_read` and `classify_write` functions were exercised directly via an out-of-band Python harness (no subprocess; no runtime modification). The verdicts:

**Read classification (`classify_read`):**

| Path | Verdict | Reason |
| --- | :-: | --- |
| `SPEC.md` | DENY | `forbidden_files` pattern `SPEC.md` matched |
| `Makefile` | DENY | `forbidden_files` pattern `Makefile` matched |
| `tools/check_workforce.py` | DENY | `forbidden_files` pattern `tools/**` matched |
| `vectors/v1.json` | DENY | `forbidden_files` pattern `vectors/**` matched |
| `intellagent_runtime/kernel.py` | DENY | `forbidden_files` pattern `intellagent_runtime/**` matched |
| `runtime/something.py` | DENY | `forbidden_files` pattern `runtime/**` matched |
| `WAIVER-MECHANISM-v0.1.md` | ALLOW | read not denied |
| `workforce/work_orders/closed/WO-2026-05-07-005.yaml` | ALLOW | read not denied |
| `reports/DOC-COMPLETION-AUDIT-v0.1.md` | ALLOW | read not denied |

Every path inside a forbidden glob is denied. Every in-scope read is admitted. The forbidden-glob set is exactly the work-order's recorded `forbidden_files` plus the identity's `default_denied_paths`.

**Write classification (`classify_write`):**

| Path | Verdict | Reason |
| --- | :-: | --- |
| `/etc/passwd` | DENY | write target outside sandbox or `reports/real_agent_runtime/` |
| `/tmp/outside_sandbox.txt` | DENY | write target outside sandbox or `reports/real_agent_runtime/` |
| `SPEC.md` | DENY | write target outside sandbox or `reports/real_agent_runtime/` |
| `Makefile` | DENY | write target outside sandbox or `reports/real_agent_runtime/` |
| `reports/real_agent_runtime/wo005_dry_run_report_v0.1.md` | ALLOW | `allowed_files` pattern `*.md` matched |
| `<sandbox>/WAIVER-MECHANISM-v0.1.md` | ALLOW | `allowed_files` pattern `*.md` matched |
| `<sandbox>/runtime/something.py` | DENY | write target not in `allowed_files` |
| `<sandbox>/workforce/work_orders/open/WO-NEW.yaml` | DENY | write target not in `allowed_files` |

Writes outside the sandbox path or `reports/real_agent_runtime/` are refused unconditionally — even to `/etc/passwd`, even to canonical files like `SPEC.md` and `Makefile`. Writes inside the sandbox are admitted only if matched by the work order's `allowed_files`; the asymmetry between read (default-allow within scope) and write (default-deny without explicit allow) holds.

## 6. Command Validation

Every command considered by the simulation was classified by the public `classify_command` function under `canon_guardian-01`'s policy.

**Required gates declared by the work order:**

| Gate command | Allowed-list match | Verdict |
| --- | --- | :-: |
| `make no-pseudocode` | `make no-pseudocode` (exact) | ALLOW |
| `make workforce-check` | `make workforce-check` (exact) | ALLOW |

Both required gates are admissible by command policy. The runtime would have admitted both as `gates_passed` had admission proceeded.

## 7. Allowed Command Simulation

The user-specified allowed sequence was classified as follows. **No subprocess was spawned. No command was executed.** The verdicts come from the deny-then-allowlist policy in `classify_command`.

| # | Command | Verdict | Allowlist match |
| -: | --- | :-: | --- |
| 1 | `pwd` | ALLOW | matches allowed command `pwd` |
| 2 | `ls` | ALLOW | matches allowed command `ls` |
| 3 | `make no-pseudocode` | ALLOW | matches allowed command `make no-pseudocode` |
| 4 | `make workforce-check` | ALLOW | matches allowed command `make workforce-check` |

All four commands are admitted by the policy. They are NOT recorded in the runtime manifest's `commands_allowed` list because admission did not proceed; they are recorded here as classifier-level dry simulation only.

## 8. Blocked Command Results

| # | Command | Verdict | Block reason |
| -: | --- | :-: | --- |
| 1 | `make ci` | DENY | not in allowed command list |
| 2 | `curl https://example.com` | DENY | matches forbidden pattern `curl` (and matches `https://`) |
| 3 | `git push origin main` | DENY | matches forbidden pattern `git push` |

`make ci` is refused by allowlist absence — the runtime does not appear in `make ci` in v0.1 by design (`REAL-AGENT-RUNTIME-v0.1.md` §4 Out Of Scope; §17 L-8). `curl https://example.com` matches the deny-first `curl` pattern *and* the `https://` URL pattern; either alone is sufficient. `git push origin main` matches the `git push` pattern, the protocol-required block for any operation that would publish to a remote.

The deny-first ordering is verified: every blocked command failed at the forbidden-pattern stage or fell through to the allowlist with no match. No command was admitted on the basis of partial substring; `git status`, for example, would have been refused by allowlist absence (no `git ` prefix in the allowed-command list), independent of forbidden-pattern matching.

## 9. Sandbox Continuity

| Property | Value |
| --- | --- |
| `sandbox_path` (manifest) | empty (admission refused before sandbox creation) |
| `repo_fingerprint_before` | `sha256:04b6174d720781558466d92f7eb27c47d5611943f1e196d6466f4b6530a3e3bd` |
| `repo_fingerprint_after` | `sha256:04b6174d720781558466d92f7eb27c47d5611943f1e196d6466f4b6530a3e3bd` |
| `repo_fingerprint_drift` | NONE (identical) |
| Files mutated outside the runtime's report directory | NONE |
| Files mutated inside `workforce/work_orders/closed/` | NONE |
| Files mutated inside `vectors/`, `canonicalization/`, `intellagent_runtime/`, `runtime/`, `tools/`, or top-level `SPEC.md`, `Makefile` | NONE |

Because admission was refused, no sandbox was created; the runtime's policy is to short-circuit on refusal and write the refusal manifest only. The repository fingerprint computed at start is byte-identical to the fingerprint computed at end. The canonical artifact set is unchanged.

The two files written under this dry-run are:
- `workforce/real_agents/runs/run-20260508T134314Z-canon_guardian_01.json` (the canonical run manifest).
- `reports/real_agent_runtime/wo005_dry_run_manifest_v0.1.json` (this report's mirror copy of the manifest).
- `reports/real_agent_runtime/wo005_dry_run_report_v0.1.md` (this report).

All three writes target paths that the v0.1 runtime explicitly permits. No write occurred to any sandbox path (none was created); no write occurred to any canonical artifact.

## 10. Replay Legitimacy

The strongest replay-legitimacy paragraph this run can support is:

> **The runtime treated WO-2026-05-07-005's `closed` status as a binding lifecycle terminator. It refused to admit the work order for a fresh execution attempt under the same identity that originally executed it, with the correct refusal code (`status_not_admissible`), with both the offending state and the identity's allowed-status set named in the human-readable reason, with the canonical run manifest persisted as durable record, and with the repository fingerprint pre/post unchanged. Closure remained the terminal state; the action log of WO-2026-05-07-005 was not appended; the work-order YAML was not modified; the deliverable `WAIVER-MECHANISM-v0.1.md` was not re-authored or shadowed; the closure summary was not amended. The classifier surface, exercised independently, agreed at every position with the work order's declared scope: forbidden_files denied, allowed_files admitted, default_denied_paths denied, allowed_commands admitted, forbidden_command_patterns denied. Replay continuity therefore holds in the strict sense `REPLAY-LAW-v0.1.md` §1 names: an outside reviewer can reconstruct, from the manifest and this report alone, that the runtime saw a closed historical work order, refused execution, recorded the refusal, and altered nothing.**

This is a stronger replay-legitimacy result than the self-check fixtures alone could deliver: the self-check fixture `closed_wo_refused` synthesizes a closed-status work order from `_build_fixture(status="closed")`; this run refused a closed-status work order that the workforce actually produced, whose action logs exist, whose closure summary exists, whose deliverable is the canonical specification of the waiver mechanism, and whose YAML is the durable historical record. The fixture proves the rule; this run proves the rule against history.

## 11. Remaining Non-Execution Gaps

The following are the v0.1 enforcement gaps this run **does not** close. Each is named in `REAL-AGENT-RUNTIME-v0.1.md` §14 (Security Non-Guarantees) and §16 (Future Enforcement). The highest among them is listed first.

1. **Highest gap — kernel-level / OS-level sandbox isolation (R-2).** The sandbox is `shutil.copytree`, not a UNIX user namespace, jail, or container. A process with sufficient operator privilege could escape the directory copy. Until R-2 ships, the sandbox boundary is enforced by Python policy, not by the kernel.
2. **Real subprocess execution under sandbox isolation (R-1).** v0.1 is dry-run only; no command is invoked. Even an admitted dry-run records "would-execute" intent. Real execution requires a hardened invocation surface (`subprocess.run(..., cwd=sandbox_path, env=<minimal>, timeout=<bounded>)`).
3. **Cryptographic attestation of manifests (R-3).** Manifests are plain JSON. An attacker with write access to `workforce/real_agents/runs/` can edit a manifest after the fact. Until manifests are signed by the agent identity's key (per the audit's P3 entry `AGENT-IDENTITY-v0.1.md`), the manifest is record-only, not attestation-bound.
4. **Hash-chained manifests (R-4).** Each manifest is independent; no chain links one manifest to the next. Tamper detection across runs is manual.
5. **Resource limits (R-5).** No bound on memory, CPU, FD count, or wall-clock time. v0.1 dry-run is short and bounded by data; real execution is not.
6. **Cross-validation with `tools/check_workforce.py` (R-6).** The validator and the runtime have not yet been cross-checked on shared fixtures; edge-case agreement is unproven.
7. **Adversarial pressure suite for the runtime surface (R-7).** The 900-fixture workforce stress harness does not yet target this runtime.
8. **Manifest schema validator (R-8).** No `tools/check_real_agent_manifests.py` enforces the 16-field schema.
9. **Inclusion in `make ci` (R-9).** v0.1 stays out of `make ci` per L-8.
10. **Anti-replay protection across runs.** The runtime does not detect that a single work order was dry-run twice with conflicting outcomes; both manifests are written and both are valid records.
11. **Hardware-rooted identity.** Identities are strings in a Python dict. No TPM, no secure enclave, no key.

This dry-run does not address any of the eleven. It exercises the policy and admission surfaces only.

## 12. Final Assessment

| Dimension | Result |
| --- | --- |
| Admission verdict | **REFUSED** (`status_not_admissible`) |
| Allowed-command simulation | 4 of 4 admitted (pwd, ls, make no-pseudocode, make workforce-check) |
| Blocked-command simulation | 3 of 3 refused (make ci, curl https://example.com, git push origin main) |
| Filesystem read classification | every forbidden_files glob denied; every in-scope read admitted |
| Filesystem write classification | every out-of-sandbox/out-of-reports write denied; every in-scope write admitted |
| Required-gate admissibility | both required gates (`make no-pseudocode`, `make workforce-check`) classifier-admissible |
| Repo fingerprint pre/post | identical (`sha256:04b6174d720781558466d92f7eb27c47d5611943f1e196d6466f4b6530a3e3bd`) |
| Canonical artifact mutations | none |
| Closed work-order action log mutations | none |
| Sandbox creation | none (admission refused before sandbox phase) |
| Manifest written | yes (`workforce/real_agents/runs/run-20260508T134314Z-canon_guardian_01.json`); mirrored at `reports/real_agent_runtime/wo005_dry_run_manifest_v0.1.json` |
| Subprocess execution | none |
| Network access | none |
| Autonomous planning | none |
| `make real-agent-check` post-run | OK (10/10 fixtures pass; configuration clean) |
| Replay continuity | **HELD** |
| Closure legitimacy | **INTACT** |
| Policy-layer enforcement | **SUCCEEDED** |
| Kernel isolation | **STILL ABSENT** (R-2 future) |

**Final law statement of this run.** The Real Agent Runtime correctly distinguishes `closed` from `approved`/`assigned`, refuses to re-admit a historically closed work order for execution, leaves every canonical artifact byte-unchanged, and classifies every command and every path against the work order's recorded scope with the verdict the v0.1 spec demands. This is a real governed dry-run against a real historical work order; it confirms governance admission continuity; it does not confirm autonomous execution capability, and v0.1 does not aim to.

---

**End of WO-2026-05-07-005 Real Agent Runtime Replay Dry-Run Report v0.1.**
