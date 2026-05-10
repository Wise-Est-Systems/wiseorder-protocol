# NEXT 3 EARNED MOVES v0.1
## Independent Forward-Motion Assessment Under Governance

**Status:** Audit / assessment-only governance assessment, non-normative.
**Governing work order:** `WO-2026-05-07-006` (canon_guardian; independent forward-motion assessment).
**Agent role:** `canon_guardian`
**Agent identity:** `canon_guardian-01`
**Date of run:** 2026-05-08.
**Companion documents:** `reports/DOC-COMPLETION-AUDIT-v0.1.md`, `reports/MILESTONE-FOUNDATION-v0.1.md`, `WORKFORCE-HARDENING-v0.2.md`, `WORKFORCE-SANDBOX-STRESS-v0.1.md`, `VALIDATION-LAW-v0.1.md`, `REPLAY-LAW-v0.1.md`, `TRUST-LAW-v0.1.md`, `WAIVER-MECHANISM-v0.1.md`.

> **Core thesis.** Operational trust is earned through replayable, pressure-tested execution under governance. Forward motion is measured by increased operational legitimacy, not by document volume or architecture expansion.

---

## 1. Purpose

This assessment names the next three highest-leverage execution moves the system can take to most increase earned operational trust per `TRUST-LAW-v0.1.md`, replay legitimacy per `REPLAY-LAW-v0.1.md`, validator strength per `VALIDATION-LAW-v0.1.md`, sandbox containment per `WORKFORCE-SANDBOX-STRESS-v0.1.md`, and release readiness per `RELEASE-CHECKLIST-v0.1.md` and `RELEASE-STATUS-v0.1.md`.

The assessment is independent. It is determined from on-disk state of the seven cited documents and the closed-work-order audit trail; it does not adopt the recommendations of any prior closure summary as conclusions. It uses the audit's classifications as inputs but reaches its own ranking.

The assessment is bounded. Three moves and no more. Each move is a single, named, executable work-order target. None invents a new product family. None redesigns runtime, validator, workflow, or authority semantics. None redefines canon. None expands the bounded ten-document remaining-doc queue identified by `reports/DOC-COMPLETION-AUDIT-v0.1.md` §15. Two of the three moves are *operational and tooling* changes — not document authoring; one is a hardening migration.

The assessment does not authorize execution. Each named move requires its own drafted, approved, and assigned governance work order per `AGENT-GOVERNANCE-WORKFORCE-v0.1.md` §3. This document's authority is observation and ranking only.

---

## 2. Current Operational State

The state is grounded in the on-disk record of the four closed work orders (`WO-2026-05-07-001`, `WO-2026-05-07-003`, `WO-2026-05-07-004`, `WO-2026-05-07-005`), the milestone artifact, the canonicalization-readiness audit, and the constitutional-closure audit.

| Surface | Status | Anchor |
| --- | --- | --- |
| WiseOrder Protocol v0.1.0 (`SPEC.md`) | Locked | `RELEASE-STATUS-v0.1.md` §1 |
| Conformance vectors | 23 / 23 passing | `RELEASE-STATUS-v0.1.md` §3 |
| Interop fixtures | 3 / 3 passing | `RELEASE-STATUS-v0.1.md` §4 |
| Tests | 135 / 135 passing | `RELEASE-STATUS-v0.1.md` §3 |
| Canonicalization corpus | `corpus_sha256: sha256:c95685bff48c15abc313c462908b05ac309250bc660c2d802ae51af5a8038b09` stable | `MILESTONE-FOUNDATION-v0.1.md` §3 |
| Workforce runtime | v0.1 lifecycle + v0.2 hardening (25 native rules) | `WORKFORCE-HARDENING-v0.2.md` §2 |
| Workforce stress suite | 900 deterministic checks; coverage_gap = 0; cross-sandbox identity holds | `WORKFORCE-SANDBOX-STRESS-v0.1.md` §1 |
| Closed work orders | 4 (WO-001, WO-003, WO-004, WO-005); zero rejected | `workforce/work_orders/closed/` |
| Open work orders | 1 (WO-006 in flight) | `workforce/work_orders/open/` |
| Constitutional-closure audit | Approaching; bounded queue 9 of 10 remaining (after WO-005 closed `WAIVER-MECHANISM-v0.1.md`) | `reports/DOC-COMPLETION-AUDIT-v0.1.md` §15 |
| Cross-machine determinism | **Unverified** | `WO-001` closure summary §7 |
| Cross-Python-version determinism | **Unverified** | same |
| Cross-language byte equivalence | **Unverified**; no non-Python implementation runs against the corpus | same |
| `make ci` interpreter pin | **Convention-only**; system `python3` without pytest fails; `.venv/bin/python` passes | `WO-003` closure summary §10 L-4 |
| Validator enforcement of waiver failure classes F-1..F-14 | **Specified in `WAIVER-MECHANISM-v0.1.md` §14; not yet implemented in `tools/check_workforce.py`** | `WO-005` closure summary §10 L-7 |

The pattern is clear: **the runtime, governance, and corpus are sound on a single machine under a single interpreter; everything claimed beyond that is unverified.** The shortest path to forward motion is to close the gaps between single-machine legitimacy and multi-machine, multi-interpreter, mechanically-enforced legitimacy.

---

## 3. What Counts As Earned Forward Motion

A move counts as earned forward motion if and only if it measurably strengthens at least one of the seven priority axes:

1. **Replayability.** The post-move state can be reconstructed from on-disk record alone (`REPLAY-LAW-v0.1.md`).
2. **Validator legitimacy.** The post-move state has more rules mechanically enforced; no rule weakened (`VALIDATION-LAW-v0.1.md`).
3. **Sandbox safety.** The post-move state has tighter containment, lower coverage gap, or higher cross-sandbox identity (`WORKFORCE-SANDBOX-STRESS-v0.1.md`).
4. **Audit continuity.** The post-move state preserves more of the audit trail and exposes more of it to mechanical verification.
5. **Operational reproducibility.** The post-move state reproduces the same canonical bytes / verdicts / artifacts from a fresh clone on a fresh machine (`MILESTONE-FOUNDATION-v0.1.md` §3).
6. **Release legitimacy.** The post-move state passes more release-readiness gates without environmental dependencies (`RELEASE-CHECKLIST-v0.1.md`).
7. **Earned dependency readiness.** The post-move state moves the system one rung up the dependency gradient (`DEPENDENCY-GRADIENT-v0.1.md`); an outside party can perform a verifiable check against an externally observable property.

A move that does NOT measurably strengthen at least one of the above seven axes is not forward motion. It may be useful, interesting, or correct, but it is not earned forward motion under the priorities of this assessment.

**Move qualification clause (must-define):** *A move does not count unless it measurably strengthens replayability, validator legitimacy, sandbox safety, audit continuity, operational reproducibility, release legitimacy, or earned dependency readiness.*

---

## 4. What Does NOT Count As Forward Motion

The following categories of work, if attempted as the next move, are NOT earned forward motion under this assessment:

- **Document count growth without enforcement.** Authoring a document that is normative but not mechanically enforced moves the validator legitimacy axis by zero. Documents that bound enforcement targets (like `WAIVER-MECHANISM-v0.1.md`) are exceptions when paired with a future hardening cycle.
- **Architecture expansion.** Adding a new cognition class, a new primitive, a new runtime layer, or a new product family is forbidden by the work order and is also not the highest-leverage move from the current state.
- **Speculative capability.** Demos that show capability without strengthening any of the seven priority axes do not move trust accumulation per `TRUST-LAW-v0.1.md` §3 (trust accumulates by replayable continuity under pressure, not by capability).
- **New abstractions.** Refactoring runtime or validator code into "cleaner" abstractions does not strengthen replayability, validator legitimacy, sandbox safety, audit continuity, operational reproducibility, release legitimacy, or earned dependency readiness. It is internal-quality work, not forward motion.
- **Roadmap inflation.** Authoring a fourth roadmap, extending an existing roadmap, or producing "vision" / "strategy" / "methodology" documents is forbidden by the constitutional-closure audit §13–§14 and is also not forward motion.
- **Hype-oriented outputs.** Marketing material, launch announcements, partnership posts, journalist-facing summaries, or any output whose purpose is reputation accumulation rather than evidence accumulation is forbidden by `TRUST-LAW-v0.1.md` §3 and is not forward motion.
- **Non-canonical reformulation of existing work.** Restating the constitutional layer in narrative form, summarizing the audit's conclusions in a slide deck, or producing a "philosophy" document about the existing system does not advance any of the seven priority axes.

The absence of these categories from the recommended moves below is intentional. Each was considered and explicitly rejected against the qualification clause in §3.

---

## 5. Next 3 Earned Moves

Three moves, ordered by sequencing dependency (M-1 → M-2; M-3 independent and parallel-eligible).

### Move 1 — Pin `make ci` to the canonical interpreter

| Field | Value |
| --- | --- |
| **move_id** | `EARN-1` |
| **objective** | Pin `PYTHON` in the Makefile to `.venv/bin/python` when `.venv/pyvenv.cfg` is present, eliminating environment-dependent CI failures and converting the `.venv/bin/python` convention into a declared interpreter contract. Ship the change as a small `CANONICAL-INTERPRETER-v0.1.md` companion (the audit's P2 entry) plus the Makefile amendment. |
| **why this was chosen** | The smallest possible bounded change with the largest legitimacy gain. Currently `make ci` exits 0 only under `PYTHON=.venv/bin/python` and exits 2 under system `python3` (Homebrew `python@3.14`, no pytest). Every release-status claim, every gate-run claim, and every "CI passing" assertion is environment-conditional in a way that is not declared on disk. A fresh machine cannot reproduce the release-status report's gate-green claim without the operator implicitly knowing the interpreter pin. This is a replay break. M-1 closes it with ~10 lines of Makefile change and one short companion document. |
| **operational trust gained** | Replay legitimacy (every gate run becomes reproducible from on-disk record alone). Release legitimacy (release-status claims become environment-declarative). Cross-machine reproducibility (a fresh machine can reproduce gate behavior given only the repo state). |
| **risk reduced** | Environment-dependent CI failure on fresh machines; release-status drift between machines; replay break across machines; downstream embarrassment if an outside reviewer's first `make ci` run fails on their default `python3`. |
| **required work order** | A release-discipline work order; `agent_role: release`; `allowed_files` MUST include `Makefile` (currently in `forbidden_files` of WO-006 and most prior canon_guardian orders) and the new top-level `CANONICAL-INTERPRETER-v0.1.md`; `forbidden_files` exclude SPEC, vectors, canonicalization, and the Intellagent runtime. The work order does not modify validator semantics, runtime semantics, or canon. |
| **expected artifact** | (a) Amended `Makefile` with `PYTHON ?= $(shell test -f .venv/pyvenv.cfg && echo .venv/bin/python || echo python3)` (or equivalent declarative pin); (b) new `CANONICAL-INTERPRETER-v0.1.md` (the audit's P2 entry) declaring the interpreter contract, the version constraints, and the activation discipline; (c) updated `RELEASE-STATUS-v0.1.md` note that the canonical interpreter is `.venv/bin/python`. |
| **required gates** | `make no-pseudocode`, `make workforce-check`, `make workforce-stress`, `make ci`. |
| **public-release relevance** | **Maximal.** No public release claim is replayable until this is done. An outside engineer's first `make ci` run is the single highest-leverage credibility test the protocol faces; today, that test fails environmentally. After this move, it passes mechanically. |
| **strengthens** | Replayability (yes); validator legitimacy (no — but does not weaken it); sandbox containment (no); trust continuity (yes). Primary axis: replayability + release legitimacy + cross-machine reproducibility. |

### Move 2 — Cross-machine + cross-Python-version CI replay harness

| Field | Value |
| --- | --- |
| **move_id** | `EARN-2` |
| **objective** | Stand up a second-machine and second-Python-version CI run that reproduces `corpus_sha256: sha256:c95685bff48c15abc313c462908b05ac309250bc660c2d802ae51af5a8038b09` byte-for-byte against the same v0.1 canonicalization corpus, plus the conformance and interop suites' existing PASS results, with the cross-replay verdict published as a versioned artifact at `interop/reports/cross-replay-v0.1.json`. The harness MAY be a GitHub Actions matrix (Linux + macOS × Python 3.12 + 3.13) or an equivalent declared-interpreter multi-runner setup. |
| **why this was chosen** | The longest-running unverified surface in the entire corpus. Every prior closure summary, the canonicalization-readiness audit, the constitutional-closure audit (M-1, §7 of WO-001 closure), and the `WORKFORCE-SANDBOX-STRESS-v0.1.md` scope clause name "cross-machine determinism is unverified" as load-bearing on every external-dependence claim. The system's claim of byte-deterministic canonicalization is currently a *single-machine* assertion. With this move, it becomes a multi-machine empirical record that an outside party can inspect (`interop/reports/cross-replay-v0.1.json`). M-1 is the prerequisite (without interpreter pinning, the multi-machine harness is itself environment-dependent). M-2 is the payoff. |
| **operational trust gained** | Replay legitimacy (canonical bytes proven reproducible across machines + interpreters); cross-machine reproducibility (mechanically demonstrated); earned dependency readiness (`DEPENDENCY-GRADIENT-v0.1.md` rung from "available" toward "depended upon" advances measurably); release legitimacy (release-status report cites cross-replay artifact instead of a single-machine claim). |
| **risk reduced** | Silent platform drift; hidden floating-point or string-handling differences across Python versions; cross-Python-version output instability in the canonicalizer's number-format path; outside-party doubt at the first reproduction attempt; `MILESTONE-FOUNDATION-v0.1.md` §3 G1 "byte-identical audit memory" claim collapsing under cross-machine inspection. |
| **required work order** | A pressure-tests / cross-replay work order; `agent_role: pressure_tester` (or `release` if no pressure_tester role exists in v0.1; this would be a sub-question for the work order's draft phase); `allowed_files` MUST include `canonicalization/**`, `interop/**`, the GitHub Actions config path, and the new `cross-replay-v0.1.json`; `forbidden_files` exclude SPEC, vectors (read-only), the Intellagent runtime. The work order does not modify canonicalization semantics or canon. |
| **expected artifact** | (a) `interop/reports/cross-replay-v0.1.json` — a deterministic, fixture-format report with per-runner, per-Python-version verdicts on `canonicalization-check`, `make ci`, `make conformance`, `make interop`; (b) GitHub Actions workflow file (or equivalent CI config) declaring the matrix; (c) updated `RELEASE-STATUS-v0.1.md` citing the cross-replay artifact; (d) optionally a `CROSS-REPLAY-v0.1.md` companion document if the report needs prose grounding (this would be **outside** the bounded ten-doc queue and requires an explicit "runtime-pressured discovery citation" per the audit's §17 stop condition — the citation is M-2 itself). |
| **required gates** | `make no-pseudocode`, `make workforce-check`, `make canonicalization-check`, `make ci`, `make workforce-stress`. The cross-replay harness's own internal gate (`make cross-replay` or equivalent) is added if and when M-2 is executed. |
| **public-release relevance** | **Maximal.** Cross-machine reproduction is the property external consumers will verify first. Until this exists, every claim of byte-deterministic canonicalization is testimonial. After this exists, it is empirical. |
| **strengthens** | Replayability (yes — primary); validator legitimacy (yes — adds a new gate); sandbox containment (yes — multi-runner is multi-sandbox by definition); trust continuity (yes — cross-machine identity is the load-bearing replay invariant per `REPLAY-LAW-v0.1.md` §4). Primary axes: replayability + cross-machine reproducibility + earned dependency readiness. |

### Move 3 — Migrate waiver failure classes F-1..F-14 into native validator rules

| Field | Value |
| --- | --- |
| **move_id** | `EARN-3` |
| **objective** | Implement, in `tools/check_workforce.py`, the 14 waiver failure classes specified in `WAIVER-MECHANISM-v0.1.md` §14 as native validator rules with named identifiers (`waiver_missing_actor`, `waiver_missing_timestamp`, `waiver_missing_rationale`, `waiver_original_deviation_removed`, `waiver_canon_path_waived`, `waiver_out_of_scope_field`, `waiver_pre_verdict_suppressed`, `waiver_post_verdict_missing`, `waiver_out_of_window`, `waiver_forward_binding`, `waiver_authority_expansion`, `waiver_canon_mutation`, `waiver_validator_weakening`, `waiver_gate_skip`), so that any work order whose waiver claim violates F-1 through F-14 is mechanically refused at closure time. Update `WORKFORCE-HARDENING-v0.2.md` (or author a small `WORKFORCE-HARDENING-v0.3.md` if v0.3 is the appropriate hardening cycle) to record the new rules. |
| **why this was chosen** | Converts `WAIVER-MECHANISM-v0.1.md` from normative-only to mechanically enforced. The waiver mechanism is the only sanctioned exception class to `WORKFORCE-EXECUTION-RUNTIME-v0.1.md` §21 immutability; without validator enforcement, it is convention dressed as declaration. Per `VALIDATION-LAW-v0.1.md` §3, validation is the only surface on which operational truth is mechanically visible. The waiver mechanism currently has the right specification but no mechanical visibility. M-3 closes that gap. |
| **operational trust gained** | Validator legitimacy (14 new mechanically enforced rules); audit continuity (every waiver record now subject to mechanical inspection by `make workforce-check`); operational reproducibility (waiver acceptance becomes reproducible from on-disk record + validator code, rather than from operator discipline). |
| **risk reduced** | Invalid waiver claims silently accepted at closure; operator-discipline drift across closures; convention masquerading as enforcement; the waiver mechanism degenerating into a formal-but-unenforced clause that is invoked without scrutiny. |
| **required work order** | A workforce hardening work order under `WORKFORCE-HARDENING-v0.2.md` (or v0.3 if that's the appropriate cycle). `agent_role: builder` or `canon_guardian`; `allowed_files` MUST include `tools/check_workforce.py` and the appropriate `WORKFORCE-HARDENING-v0.X.md`; tests directory inclusion is needed for the new test cases. The work order does not modify SPEC, vectors, canonicalization, runtime, or governance semantics; it adds validator rules. |
| **expected artifact** | (a) Amended `tools/check_workforce.py` with 14 new rule identifiers, each producing a `Violation` with the named rule on detection; (b) new test cases under `tests/` covering positive and negative cases for each F-N rule; (c) updated `WORKFORCE-HARDENING-v0.2.md` (or new `WORKFORCE-HARDENING-v0.3.md`) declaring the migration and citing `WAIVER-MECHANISM-v0.1.md` §14 as the normative source; (d) updated workforce stress fixtures (under `WORKFORCE-SANDBOX-STRESS-v0.1.md`'s harness) covering the new rules. |
| **required gates** | `make no-pseudocode`, `make workforce-check`, `make workforce-stress`, `make ci`. |
| **public-release relevance** | **Medium.** Internal enforcement strength is invisible to external consumers, but every future closure's legitimacy depends on it. An outside reviewer auditing a closed work order with an `amended` status_history entry will see — after this move — that the validator mechanically accepted the waiver, not just that the operator and human owner asserted it. |
| **strengthens** | Replayability (yes); validator legitimacy (yes — primary axis); sandbox containment (yes — waiver enforcement runs inside the workforce-stress sandboxes too); audit continuity (yes — every waiver becomes mechanically checkable post-closure); trust continuity (yes — the basis on which waivers are accepted becomes inspectable evidence). Primary axes: validator legitimacy + audit continuity + replayability. |

---

## 6. Why These 3 Matter Most

Each move addresses one of the three remaining structurally load-bearing gaps between v0.1 governance specification and v0.1 operational legitimacy:

- **EARN-1** addresses the **interpreter-environment gap**: the gap between "the canonical interpreter is `.venv/bin/python`" (operationally true, currently undeclared) and "the canonical interpreter is mechanically pinned in the Makefile" (replayably declared). Without EARN-1, every other gate-related move depends on an unstated assumption.
- **EARN-2** addresses the **single-machine gap**: the gap between "byte-deterministic canonicalization on the dev machine" (true) and "byte-deterministic canonicalization across two machines and two Python versions" (currently unverified). Without EARN-2, the protocol's longest-running open risk remains open and the dependency-gradient claim is single-machine.
- **EARN-3** addresses the **enforcement gap for waivers**: the gap between "waivers are specified as recorded exceptions" (`WAIVER-MECHANISM-v0.1.md` exists) and "waivers are mechanically refused if they fail F-1..F-14" (currently operator-discipline only). Without EARN-3, the waiver mechanism is normative without validator-attestation.

**Why these three together.** EARN-1 unlocks EARN-2 (cross-machine harness needs declarative interpreter pinning to be reproducible). EARN-3 is independent and parallel-eligible (it touches `tools/check_workforce.py` and tests, none of which intersect with the Makefile or the cross-machine harness). The three together close the most operationally load-bearing gaps the protocol currently carries — the gaps that an external party would surface within their first hour of inspection. None of the three expands architecture, redefines canon, or invents new product surface.

**Why not other candidates.** The constitutional-closure audit's bounded queue contains seven additional candidate documents (REVIEWER-IDENTITY, AUDIT-READ-GRANTS, CLOSURE-OPERATOR-RUNBOOK, THREAT-MODEL, AGENT-IDENTITY, STRESS-FIXTURE-CORPUS, v0.2-MIGRATION-NOTE, plus the P0 declaration). Each is governance-instrument work that strengthens declaration but not mechanical enforcement until paired with a hardening cycle. By the qualification clause in §3, document-only work that does not strengthen mechanical enforcement is not earned forward motion under the priorities of this assessment. EARN-3 is the exception because it migrates an existing document's normative content into native validator enforcement — i.e., it converts a document from declaration to mechanical truth.

---

## 7. Risks Reduced

The three earned moves jointly reduce the following risks:

| Risk | Reduced by | Reduction shape |
| --- | --- | --- |
| Environment-dependent CI failures | EARN-1 | Eliminated for `.venv/bin/python` users; declared in Makefile. |
| Replay break across machines | EARN-1 + EARN-2 | EARN-1 declarative; EARN-2 empirical. |
| Cross-Python-version output instability | EARN-2 | Detected mechanically by matrix run. |
| Cross-machine canonicalization drift | EARN-2 | Detected mechanically by `interop/reports/cross-replay-v0.1.json`. |
| Operator-discipline drift on waivers | EARN-3 | 14 mechanical rules refuse closure on invalid waivers. |
| Convention masquerading as enforcement (waiver class) | EARN-3 | Convention becomes mechanical rule. |
| External-reviewer first-touch failure | EARN-1 + EARN-2 | An outside engineer's first `make ci` and first cross-machine `make ci` both pass deterministically. |
| Release-status drift between machines | EARN-1 + EARN-2 | Release-status cites cross-replay artifact, not single-machine claim. |
| Trust accumulation through assertion rather than evidence | EARN-2 + EARN-3 | Both moves replace assertion (cross-machine determinism, waiver discipline) with mechanical evidence per `TRUST-LAW-v0.1.md` §3. |

The three moves do NOT reduce: cross-language drift (a separate, larger move under `CROSS-LANGUAGE-CANONICALIZATION-v0.1.md`); agent-identity / signed-action-log gap (the audit's P3 entry `AGENT-IDENTITY-v0.1.md`); threat-model formalization (the audit's P2 entry `THREAT-MODEL-v0.1.md`). Each of those is a candidate for a subsequent assessment cycle once the three EARN moves are closed.

---

## 8. What Remains Unproven

After all three moves are executed and closed, the following surfaces remain unproven:

- **Cross-language byte equivalence.** No non-Python implementation of the canonicalizer exists. The ten future enforcement items `EN-FUT-1` through `EN-FUT-10` from the canonicalization-readiness audit remain open. EARN-2's matrix is multi-Python, not multi-language.
- **RFC 8785 JCS conformance.** The v0.1 Python canonicalizer is documented as not fully RFC 8785 JCS compliant (`CROSS-LANGUAGE-CANONICALIZATION-v0.1.md`). EARN-1, EARN-2, EARN-3 do not narrow this gap. It is a v0.2 / v0.3 migration target.
- **Agent / actor cryptographic identity.** No key material exists for any agent identity in v0.1. Action logs and work-order approvals carry actor strings, not signatures. EARN moves do not address this; the audit's P3 entry `AGENT-IDENTITY-v0.1.md` does.
- **OS-level sandboxing.** No agent runs in an OS-level sandbox. EARN-3 strengthens validator enforcement of waivers but does not introduce kernel-level isolation. Sandbox safety is improved by EARN-3 only insofar as the workforce-stress harness exercises the new rules.
- **Audit-chain hashing across action logs.** Action logs are append-only by convention but not by hash chain. EARN moves do not address this; a future hardening cycle paired with `AGENT-IDENTITY-v0.1.md` would.
- **Threat model.** No unified threat model exists. EARN moves close enforcement gaps; they do not enumerate the adversary surface. The audit's P2 entry `THREAT-MODEL-v0.1.md` addresses this.
- **Constitutional closure declaration.** The audit's P0 entry `CONSTITUTIONAL-CLOSURE-v0.1.md` is the document that declares closure achieved; it is independent of the EARN moves and cannot be written until the bounded queue's P1 and P2 batches are also closed.

The above unproven surfaces are bounded and named. Each is a candidate for a subsequent earned-moves assessment.

---

## 9. What Must Wait

The following work is operationally important but is **not** the next move under this assessment's priorities. Each item must wait until the three EARN moves are closed (or until a clear runtime-pressured discovery surfaces an earlier need).

- **Cross-language interop harness (Rust, TypeScript, Go).** Higher payoff than EARN-2 but much larger scope; depends on EARN-1 + EARN-2 first to establish the multi-machine baseline against which a non-Python implementation would be compared.
- **`AGENT-IDENTITY-v0.1.md` and key-material specification.** P3 in the audit. Larger than EARN-3 and depends on the waiver-enforcement migration completing first so that the signing surface has a mechanical anchor.
- **`THREAT-MODEL-v0.1.md`.** P2 in the audit. Important for adversarial-readiness framing but adds no mechanical enforcement; document-only work that improves declaration without improving mechanical truth.
- **`REVIEWER-IDENTITY-v0.1.md` and `AUDIT-READ-GRANTS-v0.1.md`.** P1 in the audit. Both are convention-to-declaration locks. Their mechanical strength comes when paired with hardening cycles that enforce the declared mechanisms — i.e., they are precursors to future EARN-3-style migrations rather than standalone forward motion.
- **`CONSTITUTIONAL-CLOSURE-v0.1.md`.** P0. Cannot be written until the rest of the queue is closed.
- **Adoption-ladder advancement claims.** The dependency gradient does not advance until the cross-machine and cross-language proofs exist; making such claims earlier per `ADOPTION-LADDER-v0.1.md` §2 ("adoption stalls at the lowest unverified rung") is anti-forward motion.
- **Public release v0.1.0 announcement.** Per `RELEASE-STATUS-v0.1.md`'s recommendation ("Ready for first external engineering scrutiny"), v0.1 is review-ready; a public release announcement is permitted but is a release operation, not earned forward motion. Earned forward motion is the work that makes the announcement deserve more inspection, not the announcement itself.

These items waiting is not a deferral. It is the explicit recognition that operational dependency readiness compounds: each EARN move makes the next wave of moves more legitimate, and starting the next wave before EARN-1 / EARN-2 / EARN-3 close would mean accumulating reputation rather than earned trust per `TRUST-LAW-v0.1.md` §3.

---

## 10. Final Assessment

| Required output | Value |
| --- | --- |
| **Artifact path** | `reports/NEXT-3-EARNED-MOVES-v0.1.md` |
| **Three earned moves** | `EARN-1` (pin `make ci` interpreter); `EARN-2` (cross-machine + cross-Python-version replay harness); `EARN-3` (migrate waiver failure classes F-1..F-14 to native validator). |
| **Sequencing** | EARN-1 → EARN-2 (sequential dependency); EARN-3 in parallel. |
| **Move count bound** | Exactly 3 (≤ 3 by the work order's required action #2; = 3 to maximize forward motion within the bound). |
| **Architecture expansion** | Zero. None of the three moves adds a primitive, a layer, or a product family. |
| **Canon contradictions introduced** | Zero. None of the three moves modifies SPEC, vectors, canonicalization corpus, conformance, or interop semantics. |
| **Doc-queue expansion** | Zero. EARN-1's small `CANONICAL-INTERPRETER-v0.1.md` companion is the audit's P2 entry, already in the bounded queue. EARN-2 and EARN-3 are tooling / hardening work and do not author new top-level documents (an optional `CROSS-REPLAY-v0.1.md` is named in EARN-2 with explicit runtime-pressured discovery citation per the audit's §17 stop condition, and is small if needed). |
| **Constitutional-closure assessment delta** | EARN-1 closes one P2 entry (`CANONICAL-INTERPRETER-v0.1.md`). EARN-3 produces validator enforcement of `WAIVER-MECHANISM-v0.1.md` §14, advancing M-1 / FU-1 from declaration to mechanical truth. EARN-2 closes the longest-running unverified surface (cross-machine determinism), but does not close any audit queue entry directly. Bounded queue progresses by 1 (P2 → 2 of 3 remaining). |
| **Earned operational trust delta** | Substantial. Replayability moves from single-machine to multi-machine. Validator legitimacy moves from 25 hardened rules to 39 hardened rules. Release legitimacy moves from environment-conditional to environment-declarative. Earned dependency readiness moves one rung up the gradient. |

**Assessment summary.** The next three earned moves are operational and tooling moves, not document-authoring moves. The protocol's document corpus is approaching constitutional closure (the audit confirms this); the protocol's mechanical enforcement and cross-machine evidence base lag behind. The three EARN moves close the most load-bearing gaps between specification and operational legitimacy, in the smallest scope that still measurably strengthens the seven priority axes. Each is a single bounded work order with named gates, named expected artifacts, and a named risk-reduction shape. None of the three is authorized by this assessment; each requires its own drafted, approved, and assigned governance work order per `AGENT-GOVERNANCE-WORKFORCE-v0.1.md` §3. The audit's bounded queue is unchanged. The protocol's path forward is named.

**Stop condition reaffirmed.** Per `reports/DOC-COMPLETION-AUDIT-v0.1.md` §17 and this assessment's §4: forward motion is measured by mechanical legitimacy, not by document volume. After the three EARN moves close, the next assessment cycle should re-evaluate whether the next three moves are still tooling-and-hardening or have shifted to declaration-locks; in either case, the qualification clause in §3 governs.

---

**End of NEXT 3 EARNED MOVES v0.1.**
