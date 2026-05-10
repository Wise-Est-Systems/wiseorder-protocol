# MILESTONE-FOUNDATION v0.1

**Milestone identifier:** `wiseorder-foundation-v0.1.0`
**Date:** 2026-05-07
**Governing work order:** `WO-2026-05-07-003` (release + continuity)
**Companion documents:** `MASTER-ROADMAP-v0.1.md`, `WORKFORCE-EXECUTION-RUNTIME-v0.1.md`, `WORKFORCE-SANDBOX-STRESS-v0.1.md`, `WORKFORCE-HARDENING-v0.2.md`, `TRANSLATION-LAYER-v0.1.md`.

> This milestone does not prove trustworthy AI. It proves the stack can begin governing and hardening itself operationally under constraint and pressure.

---

## 1. Infrastructure Formation

The foundation milestone bundles the artifacts that, taken together, form the first coherent infrastructure layer of the governed cognition stack.

- **`MASTER-ROADMAP-v0.1.md`** — 20-year directional framework for Intellagent and WiseOrder; immutable core principles; six strategic phases; explicit non-goals.
- **`TRANSLATION-LAYER-v0.1.md`** — human-readable explanation of the stack for non-technical audiences; preserves architectural truth without losing readability.
- **`WORKFORCE-EXECUTION-RUNTIME-v0.1.md`** — operational specification for the workforce lifecycle, work-order schema, action-log schema, self-verification block, gate execution, closure criteria, and minimum-viable enforcement.
- **`WORKFORCE-SANDBOX-STRESS-v0.1.md`** — specification for the 900-check, 3-sandbox stress harness; defines case categories A–J, augmentations, and reporting requirements.
- **`WORKFORCE-HARDENING-v0.2.md`** — migration of stress-suite augmentations into the native validator; documents the 25 new rule names and their backward compatibility surface.
- **`tools/check_workforce.py`** (extended) — native workforce records validator with v0.2 hardening augmentations integrated.
- **`tools/workforce_sandbox_stress.py`** (created) — deterministic, stdlib-only stress harness with 100 rule templates × 3 variants × 3 sandboxes.
- **`Makefile`** (extended) — added `workforce-check` and `workforce-stress` targets; `make ci` unchanged.
- **`workforce/`** tree — directory layout, templates, and the executed first real work-order cycle (`WO-2026-05-07-001` closed).
- **`reports/`** — canonicalization readiness audit, hardening report, sandbox stress aggregate and per-sandbox reports.

The pieces are deliberately narrow. None of them changes runtime semantics, canonicalization behavior, vectors, conformance, or interop. They form the governance and self-pressure-test surface around the existing protocol kernel.

---

## 2. Governance Formation

What changed at the governance layer:

- **Work-order lifecycle is operational.** A complete cycle from `drafted` through `closed` was executed against `WO-2026-05-07-001`, with every state transition recorded with actor, timestamp, and note. Two human-owner amendments to `forbidden_files` were recorded openly when scope deviations surfaced.
- **Roles, prohibitions, and authority hierarchy are codified.** `AGENT-GOVERNANCE-WORKFORCE-v0.1.md` (pre-existing) defines roles, permissions, prohibitions, and the authority hierarchy. The runtime spec operationalizes them.
- **Human approval is the closure gate.** No work order closes without a recorded `closed` entry in `status_history` with a non-empty actor; the validator enforces this.
- **Canon discipline is mechanically enforced.** Builder/test/docs roles cannot touch canon paths; canon changes require an explicit `CANON BREAK` marker; canon and implementation may not share `allowed_files`.
- **Reviewer signoff and closure summary presence are mechanically enforced** when declared in `expected_outputs`.

Governance is no longer narrative-only. The validator now refuses closure for the categories the docs already required.

---

## 3. Verification Formation

What changed at the verification layer:

- **Workforce records validator is hardened.** 25 new rule names cover lifecycle, security patterns, canon discipline, lifecycle artifacts, gate ordering, duplicate IDs, action-log orphans, undocumented deviations, and pseudocode markers in YAML.
- **The stress suite re-runs on every hardening cycle.** Coverage gap dropped from 243 → 0 between v0.1 and v0.2; future stress findings will resurface as a non-zero gap and become candidates for the next hardening cycle.
- **Cross-sandbox identity holds.** All 300 (rule, variant) pairs agree across three independently-cloned sandboxes running in parallel.
- **Existing canonicalization verification is unchanged.** `make canonicalization-check` passes against the v0.1 corpus; `corpus_sha256: sha256:c95685bff48c15abc313c462908b05ac309250bc660c2d802ae51af5a8038b09` is stable.
- **Existing conformance and interop verification is unchanged.** 23/23 vectors pass; 3/3 interop fixtures pass; F-1 enforcement remains active.

Verification is now narrower at the bytes layer (canonicalization, conformance, interop — all unchanged) and broader at the governance layer (workforce records — substantially hardened).

---

## 4. Workforce Formation

What changed at the workforce layer:

- **The first real workforce cycle ran end-to-end** (`WO-2026-05-07-001`): canonicalization readiness audit produced; reviewer self-verification completed; two `forbidden_files` deviations disclosed by the agent rather than surfaced by adversarial review; human-owner amendments recorded; closure granted with full audit trail.
- **Stress suite validates the workforce surface against itself.** 900 deterministic checks per run; identical fixtures produce identical verdicts in three sandboxes; mismatches are zero.
- **The lifecycle has been operationally tested.** All ten transitions in the documented lifecycle have been exercised by stress fixtures; the rejected lifecycle and the amendment lifecycle are also exercised.
- **Three operational lessons were recorded in the closure summary** (L-1 reviewer-identity collision; L-2 audit-grounding reads collide with strict `forbidden_files`; L-3 no formal waiver mechanism for `allowed_files`/`forbidden_files`). These are roadmap-only improvements, not blockers.

The workforce surface now has its own pressure-test harness, its own validator, and its own first-real-cycle audit trail.

---

## 5. Translation Layer Formation

What changed at the translation layer:

- **`TRANSLATION-LAYER-v0.1.md`** explains the stack (Intellagent, WiseOrder, Winstack, WOP) in plain terms for non-technical readers.
- **Architectural truth is preserved.** The translation does not soften the four principles, the role boundaries, or the explicit non-goals.
- **The stack's claims are bounded explicitly.** What the stack does NOT do is enumerated alongside what it does.
- **Stack relationship is captured in one line each:** WOP proves where something came from; Winstack proves whether it changed; WiseOrder governs what is allowed; Intellagent governs how AI systems operate under consequence.

The translation layer is the document the stack hands to anyone who has not read the engineering specs and is trying to understand what the stack is for. It is explanatory, not promotional.

---

## 6. Remaining Reality Gaps

Material gaps that exist after this milestone:

- **OS-level enforcement is absent.** The runtime is record-based. An agent can read or write a file the action log does not declare; the validator cannot detect what is not in the records.
- **Action logs and work orders are not signed.** Agent identity and human-owner approval are unverified strings.
- **Cross-language canonicalization is absent.** No Rust, TypeScript, Go, or any non-Python implementation produces byte-identical canonical bytes against the corpus. Every cross-language interoperability claim is unsupported.
- **Cross-machine determinism for canonicalization is unverified.** No second-runner CI step exists.
- **Cross-Python-version determinism is unverified.** No multi-interpreter CI step exists.
- **Distributed governance is absent.** All actions are recorded against one identity tree.
- **Adversarial runtime resistance is unverified.** The stress suite operates on records, not on a running adversary.
- **Cryptographic attestation is absent.** Audit chains are not hash-chained across action logs in a tamper-evident form.

Each gap is a candidate for a future hardening cycle. None is closed by this milestone, and the milestone does not claim otherwise.

---

## 7. Most Important Architectural Lesson

> **Governance maturity equals migrating adversarial findings into native enforcement.** The v0.1 stress suite produced 243 augmentation findings — rules documented in the governance specs but enforced only by the stress script. The v0.2 hardening migrated all 243 into the native validator. The cycle worked: pressure test → record gap → migrate enforcement → re-run pressure test → confirm zero gap. The same cycle will produce v0.3, v0.4, and so on. The architecture's job is to make this cycle cheap to run repeatedly. It is.

---

## 8. Most Important Operational Lesson

> **The validator is the authority on procedural conformance, not the closure summary.** During `WO-2026-05-07-001` closure, the closure summary initially claimed that one of the recorded scope deviations did not require a `forbidden_files` amendment. The validator contradicted that claim at closure time by emitting a `forbidden_file_read` violation. The validator does not distinguish between read motives; it checks list membership. Closure-summary narrative and validator state must be reconciled *before* closure is granted, not after; when they disagree, the validator wins. This is the substance of "governance is a check on agent narrative, not a record of it."

---

## 9. What Would Break Trust Now

A short list of the events that would invalidate the milestone's claims:

- **A canonicalization change without a CANON BREAK procedure.** The corpus_sha256 stability is the load-bearing claim of the canonicalization layer.
- **A workforce-check failure on the live tree** that has not been disclosed and re-validated. The validator's verdict on the live records is the operational truth claim.
- **A stress-suite mismatch** that has not been investigated. The stress suite is the regression harness for the validator; mismatches mean either the validator broke or a fixture became wrong, and either is serious.
- **A scope deviation that was concealed by the agent** and surfaced only by adversarial review. This is the failure mode the runtime is built to detect; an undetected instance would rupture the trust accumulation.
- **A canon-touching change committed without a Canon Guardian work order and human approval.** Canon erosion is irreversible without a public correction.
- **A change to `tools/check_workforce.py` that weakens an existing check.** Hardening must be additive; weakening is a CANON BREAK.

Each is a recoverable event with a recorded postmortem. None is closeable without one.

---

## 10. Next Hardening Frontier

The next set of work orders, in priority order, addresses the gaps in §6:

1. **Cross-language canonicalization.** Adopt strict RFC 8785 JCS Python via a CANON BREAK; bring up a Rust harness against the new corpus; wire into CI. (Audit recommendations EN-FUT-1 through EN-FUT-3 from `WO-2026-05-07-001`.)
2. **Cross-machine and cross-Python-version CI.** Closes audit gaps N1, N2, C2.
3. **Workforce signing.** Action logs and work orders gain optional signatures; identity strings become verifiable.
4. **OS-level read/write enforcement.** Filesystem-level scope enforcement for agent processes; closes the "hidden read / hidden write" gap.
5. **Audit-chain hashing across action logs.** Tamper-evident chain over the action-log directory.
6. **Network egress controls per work order.** Declared dependencies become a network policy, not just a record field.
7. **Formal waiver mechanism for `allowed_files` / `forbidden_files`** (operational lesson L-3 from `WO-2026-05-07-001`).
8. **Reviewer-identity separation** (operational lesson L-1).
9. **Read/write split in `forbidden_files`** (operational lesson L-2).

Each item is a separate work order with a single duty. None of them are authorized by this milestone; they are recommendations.

---

## What Is Actually Proven Today?

- **Deterministic validator behavior.** The same workforce records produce the same verdict from `tools/check_workforce.py` on every run.
- **Replay continuity** of canonicalization. The v0.1 corpus regenerates byte-identically from the corpus inputs under the v0.1 Python canonicalizer; `corpus_sha256` is stable across runs.
- **Workforce governance continuity.** A complete work-order lifecycle ran from `drafted` through `closed` with full audit trail, two human-owner amendments to `forbidden_files`, and reviewer signoff (assumed by human owner in v0.1).
- **Canon-discipline enforcement.** The validator now refuses closure for builder-role canon touches, missing `CANON BREAK` markers, invariant changes without human approval, authorization changes by non-security roles, and replay-path changes by non-security/release roles.
- **Cross-sandbox validator consistency.** 300 (rule, variant) pairs produce identical verdicts in three independently-cloned sandboxes running in parallel.
- **Measurable enforcement evolution.** Coverage gap reduced from 243 → 0 between v0.1 and v0.2 of the validator; the reduction is mechanical and reproducible by re-running `make workforce-stress`.
- **Existing protocol guarantees are preserved.** 23/23 vectors pass; 3/3 interop fixtures pass; canonicalization golden verifies; pseudocode scan is clean across 34 markdown files.
- **The stack survives its own pressure test.** 900 deterministic stress checks, zero mismatches, zero coverage gap, all gates green.

---

## What Is NOT Proven Yet?

- **OS-level enforcement.** Filesystem read/write blocking, network egress controls, process-level containment — all absent.
- **Trusted execution.** No sandboxing, namespace isolation, seccomp, or container boundary between the agent and the repository.
- **Filesystem isolation.** A malicious or buggy agent could perform unrecorded operations; only the absence of those operations in the action log would be inspected.
- **Hidden-command prevention.** Pattern matching catches dangerous commands *recorded* in `commands_run`. It does not catch a `sudo` an agent ran but did not record.
- **Cross-language replay equivalence.** No non-Python implementation has produced byte-identical canonicalization or verification output against the corpus.
- **Cross-machine canonicalization determinism.** No second-machine CI step exists; the same input on two machines is unverified.
- **Cross-Python-version canonicalization determinism.** The corpus is pinned to one interpreter version; behavior under another version is unverified.
- **Distributed governance.** All actions occur within one identity tree; multi-organization governance is unimplemented.
- **Adversarial runtime resistance.** The stress suite is record-based; a real adversary running inside the runtime is not modeled.
- **Cryptographic attestation.** Action logs and work orders are unsigned; integrity depends on the agent reporting honestly and on filesystem trust.
- **External adoption.** No external party currently consumes any artifact produced by this stack in production.

The milestone's claims are bounded by this list. Anything outside these bounds is not claimed.

---

## Why This Milestone Matters

The milestone matters not because the stack is now trustworthy, but because the stack is now *capable of becoming more trustworthy in a recordable, mechanical, repeatable way*. The four properties (constraint, verification, auditability, correction) are now exercisable against the workforce surface itself. The cycle that took the v0.1 stress findings to the v0.2 native enforcement is the same cycle that will take v0.2 findings to v0.3, and v0.3 to v0.4.

That cycle, more than any individual artifact in this milestone, is what the foundation milestone establishes.

---

## Commit Artifacts

### Exact commit message

```text
foundation: governed cognition stack — workforce runtime, sandbox stress, hardening v0.2, roadmaps, translation layer

Adds the foundation milestone bundle for the governed cognition stack. This is
a release + continuity operation; no runtime, canonicalization, vector, or
release-gate behavior is modified. Every artifact below was authored under a
prior work order or direct human-owner authoring action; this commit bundles
them into a coherent foundation milestone.

Documentation:
- WORKFORCE-EXECUTION-RUNTIME-v0.1.md     — operational lifecycle, schemas, gates, closure
- WORKFORCE-SANDBOX-STRESS-v0.1.md        — 900-check, 3-sandbox stress harness specification
- WORKFORCE-HARDENING-v0.2.md             — migration of 243 augmentation findings into the native validator
- MASTER-ROADMAP-v0.1.md                  — 20-year directional framework
- TRANSLATION-LAYER-v0.1.md               — human-readable explanation of the stack

Tooling:
- tools/check_workforce.py                — workforce records validator (v0.2 hardened)
- tools/workforce_sandbox_stress.py       — 900-check stress suite (stdlib only)
- Makefile                                — workforce-check + workforce-stress targets (make ci unchanged)

Workforce records:
- workforce/{templates,work_orders,action_logs,reports}/
- workforce/work_orders/closed/WO-2026-05-07-001.yaml      — first real work-order cycle (canonicalization audit)
- workforce/action_logs/WO-2026-05-07-001-{reviewer,closure}.yaml
- workforce/reports/WO-2026-05-07-001-closure-summary.md
- workforce/work_orders/open/WO-2026-05-07-003.yaml         — this release work order

Reports:
- reports/canonicalization_readiness_audit_v0.1.md
- reports/workforce_hardening_v0_2.md
- reports/workforce_sandbox_stress/{aggregate,sandbox-001,sandbox-002,sandbox-003}.{json,md}
- reports/MILESTONE-FOUNDATION-v0.1.md     — this milestone report

Gates (all green at commit time):
- make no-pseudocode      OK (34 markdown files clean)
- make workforce-check    OK (2 work orders, 2 action logs, 1 closed)
- make workforce-stress   OK (900 checks, coverage_gap=0, 11.2s parallel)
- make ci                 OK (no-pseudocode + tests + conformance + interop + canonicalization-check)

Coverage gap reduced from 243 (v0.1) to 0 (v0.2). Cross-sandbox identity holds
for all 300 (rule, variant) pairs across three independently-cloned sandboxes.
The corpus_sha256 (sha256:c95685bff48c15abc313c462908b05ac309250bc660c2d802ae51af5a8038b09)
is unchanged and continues to verify against the existing canonicalization
golden corpus.

This milestone does not prove trustworthy AI. It proves the stack can begin
governing and hardening itself operationally under constraint and pressure.

Governing work order: WO-2026-05-07-003 (release + continuity).
Milestone identifier: wiseorder-foundation-v0.1.0.
```

### Exact release tag recommendation

```text
wiseorder-foundation-v0.1.0
```

Annotated tag message body:

```text
Foundation milestone — workforce runtime, sandbox stress, hardening v0.2,
roadmaps, translation layer. Release + continuity only; no runtime,
canonicalization, vector, or release-gate behavior modified. Coverage gap
reduced from 243 to 0 between validator v0.1 and v0.2. Governing work order:
WO-2026-05-07-003. corpus_sha256 unchanged.
```

### Exact release-summary paragraph

> The foundation milestone of the governed cognition stack bundles the workforce execution runtime, the 900-check sandbox stress harness, the v0.2 native validator hardening, the 20-year master roadmap, and the human-readable translation layer into a single coherent infrastructure formation. No runtime, canonicalization, vector, or release-gate behavior is modified by this milestone. The coverage gap measured by the stress suite — the count of rules documented in governance specs but enforced only by external augmentation — was reduced from 243 to 0 between validator v0.1 and v0.2. All four required gates (`make no-pseudocode`, `make workforce-check`, `make workforce-stress`, `make ci`) pass green. The milestone does not claim trustworthy AI; it claims the stack can now govern and harden itself operationally under constraint and pressure, with every iteration measurable and reproducible.

### Exact git status expectations before commit

This repository is not currently git-initialized (`git status` returns `fatal: not a git repository`). The expected sequence prior to commit is therefore:

```text
$ cd ~/Desktop/wiseorder-protocol
$ git init
$ git add -A
$ git status
# Expected output (relative to a clean init): every file under the repo
# tree is shown under "Untracked files" — there is no prior tracked baseline
# at this milestone. The user is expected to inspect the file list once
# before staging.

# After `git add -A`, expected status:
# All files (including .venv/ and reports/) are staged. The user should
# verify .venv/ is excluded via .gitignore before committing — .venv is a
# local Python virtual environment and must not be committed. If .gitignore
# is absent, add it before staging:
#
#   .venv/
#   __pycache__/
#   *.pyc
#   .pytest_cache/
#
# Then re-run `git add -A` and `git status` to confirm .venv/ is gone.

$ git commit -m "<the commit message above>"
$ git tag -a wiseorder-foundation-v0.1.0 -m "<the tag message above>"
```

If the repository is later initialized with a different baseline (for example, an existing `.git/` is restored from elsewhere), the diff at this milestone will reflect only the milestone artifacts plus the workforce records produced by `WO-2026-05-07-001` and this work order. No file outside `allowed_files` should appear in the diff; if one does, it is a scope violation under this work order and the commit must be aborted.

— END MILESTONE-FOUNDATION v0.1 —
