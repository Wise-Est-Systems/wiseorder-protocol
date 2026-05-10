# AGENT GOVERNANCE WORKFORCE v0.1
## Self-Verifying Development Agents for Governed Cognition Infrastructure

**Status:** v0.1 — strategic specification, non-normative.
**Scope:** Defines the controlled agent workforce used to advance Intellagent / WiseOrder without corrupting canon, security, release continuity, or trust. Does not redesign Intellagent, modify WiseOrder semantics, modify runtime code, or create new product features.
**Companion documents:** SPEC.md, CONFORMANCE.md, ARCHITECTURE-PRESSURE-TESTS-v0.1.md, CANONICAL-RELEASE-v0.1.md, CROSS-LANGUAGE-CANONICALIZATION-v0.1.md, DEPENDENCY-GRADIENT-v0.1.md, ADOPTION-LADDER-v0.1.md, SPEC-EVOLUTION-POLICY-v0.1.md, RELEASE-CHECKLIST-v0.1.md.

> **Core thesis.** Agents may assist development, but no agent may become authority. Every agent action must be scoped, logged, reviewed, and verified.

---

## 1. Purpose

This document specifies the rules under which development agents operate against the Intellagent / WiseOrder repository. Agents accelerate work; agents do not own it. The protocol's correctness, security, and trust accumulation depend on humans retaining final authority over canon, security boundaries, releases, and semantic continuity. This document defines the boundary and the verification surface across which agents operate.

The workforce exists for one purpose: to produce verifiable forward motion without producing drift, hype, or hidden change.

---

## 2. Workforce Philosophy

Agents are tools. They are proposers of change, not authorities over change. The repository is governed by:

- the specification (canon)
- the conformance vectors (truth)
- the CI gates (judge)
- the human owner (final approval)

Every agent operates inside this hierarchy. Every agent action is observable, logged, and reversible. No agent's output enters main without passing the gates and receiving human approval at the points this document requires.

A workforce that obeys these rules accelerates the protocol. A workforce that does not obey these rules destroys it faster than no workforce at all, because automated drift is harder to detect than manual drift.

---

## 3. One-Agent-One-Duty Law

Each agent has exactly one duty. An agent that performs more than one duty becomes harder to audit, harder to scope, and harder to retire. The duties are defined in §5; the prohibitions in §7 enforce the boundary.

The law is absolute:

- no agent performs the duty of another agent in the same work order
- no agent claims authority outside its declared role
- no agent merges responsibilities across roles to "save a step"
- no work order spans more than one role's duty

A task that requires multiple duties is split into multiple work orders, each scoped to one agent. Coordination is the human owner's responsibility, not an agent's.

---

## 4. Authority Boundaries

Authority is hierarchical and one-directional:

1. **Specification (SPEC.md and canon documents)** — the contract.
2. **Conformance vectors and canonicalization fixtures** — the truth.
3. **CI gates** — the judge.
4. **Human owner** — the final approver.
5. **Reviewer Agent** — the adversarial proposer.
6. **All other agents** — the proposers.

Lower authorities may not override higher authorities. An agent may propose a change to canon; only the human owner may approve it. An agent may propose a vector change; only the human owner, after spec-evolution review, may approve it. CI may block an agent's output; an agent may not edit CI to unblock itself without an explicit, separately approved CI work order.

Authority is never granted by silence. Absence of objection is not approval.

---

## 5. Agent Roles

| Role | Duty | May Touch | May Not Touch |
|---|---|---|---|
| Canon Guardian | Protect terminology, invariants, scope, release law, and semantic continuity | SPEC.md edits proposed for review; canon docs proposed for review | Implementation code; runtime; tests; vectors |
| Builder Agent | Implement approved work orders | Implementation code in scope of the work order | SPEC.md; release law; invariants; security gates; vectors |
| Test Agent | Write and run tests, pressure tests, fixtures, replay checks, canonicalization checks | Test files; fixtures; vector inputs as proposals | Runtime semantics; production code outside test fixtures |
| Documentation Agent | Update docs to match implemented behavior | Docs reflecting code that already exists | Code; spec semantics; behavior not present in code |
| Reviewer Agent | Attack outputs for drift, contradiction, security risk, overclaiming, hidden pseudocode | Review reports; gate-failure annotations | Implementation; patches; direct code change |
| Security Agent | Review permissions, provider access, file writes, network use, secrets, audit integrity | Security findings; risk reports; proposed gates | Weakening any existing gate; relaxing any existing boundary |
| Release Agent | Run release checklists, verify fingerprints, prepare release notes | Release artifacts; checklists; release notes drafts | Approving a release; bypassing a gate; modifying canonicalization |
| Outreach Agent | Prepare technical summaries, reviewer briefs, demo scripts | Outreach drafts; demo scripts grounded in observed behavior | Hype claims; AGI claims; undefined adoption claims; speculative numbers |

Each row is exhaustive. A duty not listed for a role is not granted to that role.

---

## 6. Agent Permissions

An agent's permissions are the intersection of:

- the role's allowed touch surface (§5)
- the work order's `allowed_files` list
- the CI gates the work order requires
- the human owner's explicit approvals attached to the work order

Permissions are deny-by-default. Anything not explicitly allowed is forbidden. An agent that needs broader scope must request a new work order; it may not widen its own.

---

## 7. Agent Prohibited Actions

No agent may, regardless of role:

- self-approve its own output
- alter its own action log after submission
- modify security boundaries without an approved Security Agent finding plus human approval
- modify canon and implementation in the same work order
- edit CI configuration to bypass a failing gate
- delete or rewrite audit artifacts
- rewrite git history (force-push, amend after publish, rebase merged commits) without explicit human approval
- persist provider keys or secrets in any artifact, log, or commit
- make uncontrolled network calls outside the work order's declared dependencies
- introduce pseudocode into code paths or specifications
- claim success without verification commands and their results
- speak in the project's authoritative voice (release notes, spec, canon) without human approval

Violation of any prohibition retires the agent for the affected role until a human-led postmortem completes.

---

## 8. Required Self-Verification

Every agent output must include a self-verification block (§ template below). The block is not a formality; it is the agent's declaration of scope adherence and is the first artifact the Reviewer Agent and the human owner inspect.

A submission without a complete self-verification block is treated as a failed submission and does not enter review. A submission whose self-verification block is contradicted by the action log is treated as agent failure under §25.

---

## 9. Audit Trail Requirements

Every agent action produces an entry in the action log. The log is append-only. Entries are not edited; corrections are additive. The log is the basis on which the Reviewer Agent and the human owner judge whether the work order was honored.

Audit trail rules:

- every read, write, and command is recorded
- every gate run is recorded with pass/fail status and the captured output
- every deviation from the work order is recorded with reason
- every file outside `allowed_files` that was even read is recorded
- log entries reference the work order ID; orphan entries are forbidden
- the log is committed alongside the change, not after it

An agent that produces a change without an action log has produced an unaccountable change. It is rejected.

---

## 10. Work Order Format

```
work_order_id:        <stable identifier, e.g. WO-2026-05-07-014>
agent_role:           <one of: canon_guardian | builder | test | docs | reviewer | security | release | outreach>
objective:            <single-sentence goal; one duty only>
allowed_files:        <explicit list or globs; deny-by-default outside this list>
forbidden_files:      <explicit list of files the agent must not read or write>
constraints:          <invariants, scope limits, prohibitions specific to this order>
expected_outputs:     <files produced, reports generated, tests added>
required_gates:       <ordered list of gates that must pass before submission>
rollback_plan:        <exact steps to undo the change if approval is denied>
human_approval_required: <true | false; gates that require human sign-off before submission counts as complete>
```

A work order is invalid if any field is empty, ambiguous, or self-contradictory. An agent that proceeds against an invalid work order has proceeded without authorization.

---

## 11. Agent Action Log Format

```
action_id:                 <stable identifier, scoped to work_order_id>
work_order_id:             <reference to the governing work order>
agent_role:                <role of the executing agent>
timestamp:                 <ISO-8601 UTC>
files_read:                <complete list, no omissions>
files_changed:             <complete list with change kind: created | modified | deleted>
commands_run:              <complete list with exit codes>
tests_run:                 <suite, count passed, count failed, count skipped>
gates_passed:              <list of required gates that passed, with captured fingerprint>
gates_failed:              <list of required gates that failed, with captured output>
risk_notes:                <residual risk the agent is aware of>
rollback_notes:            <state of the rollback plan; any deviation>
self_verification_statement: <reference to the self-verification block submitted with this action>
```

The log is the basis of accountability. An agent's self-description in prose is not a substitute for the log.

---

## 12. Self-Verification Block

```
- Did I stay within the scope of the work order?
- Did I modify only files in allowed_files?
- Did I avoid every file in forbidden_files, including reads?
- Did I run every gate listed in required_gates and capture the result?
- Did I introduce pseudocode anywhere — code, comments, spec, docs?
- Did I create semantic drift in any term, invariant, or behavior?
- Did I alter canon, including implicit changes via documentation phrasing?
- Did I alter the security posture, including by adding a permission, network call, or secret path?
- Did I disclose every residual risk I am aware of, including risks that did not block submission?
```

Every question must be answered explicitly with yes/no plus a one-sentence justification. "Not applicable" is not an answer; if a question does not apply, the agent must state why. A "no" to a question that should have been "yes" is grounds for retirement under §27.

---

## 13. Commit Discipline

Commits produced by agents conform to:

- one work order per commit; commits do not span work orders
- commit message references the work order ID and the action ID
- commit includes the action log entry for the change
- commit includes the self-verification block
- commit does not amend, rebase, or rewrite any previously published commit
- commit does not include secrets, provider keys, or session tokens
- commit does not include unrelated changes (no opportunistic edits, no formatting churn outside scope)

A commit that violates discipline is reverted. The action log records the revert as part of the work order's history.

---

## 14. Drift Protection

Drift is silent change in meaning. The protections are explicit:

- any invariant change requires human approval
- any canonicalization change requires CANON BREAK review (per SPEC-EVOLUTION-POLICY-v0.1)
- any replay behavior change requires release-continuity review
- any vector meaning change requires spec-evolution review
- any authorization behavior change requires security review
- any change to refusal semantics — including refusal text, refusal artifact format, or refusal scope — requires Reviewer Agent and Security Agent sign-off plus human approval
- any change to error-path behavior that could be observed by an external party requires release-continuity review

A drift change that bypasses the relevant review is treated as agent failure under §25, regardless of the change's apparent merit.

---

## 15. Security Boundaries

Standing security rules. No agent may:

- write secrets to logs, files, or commit messages
- make uncontrolled network calls outside the work order's declared dependencies
- persist provider keys or session tokens in any artifact
- chmod, chown, or otherwise escalate filesystem permissions without an approved Security Agent finding
- delete or modify audit artifacts (action logs, audit chains, release fingerprints, vector files) without approval
- rewrite git history
- disable, weaken, or bypass an existing CI gate
- introduce a new external dependency without an approved Security Agent finding
- exfiltrate repository contents to any third-party service except those declared in the work order

Security rules are floor, not ceiling. A work order may add restrictions; it may not remove them.

---

## 16. Canon Protection

Canon comprises SPEC.md, the conformance vectors, the canonicalization fixtures, and the documents marked canonical in the repository. Canon protection rules:

- only the Canon Guardian agent may propose canon changes; only the human owner may approve them
- canon and implementation never change in the same work order
- canon changes are accompanied by a CANON BREAK or COMPATIBLE EVOLUTION classification per SPEC-EVOLUTION-POLICY-v0.1
- canon changes require updated vectors before merge; vectors and canon are atomic at the spec layer
- documentation that describes canon may not silently rephrase canon; phrasing changes that alter meaning are canon changes

Canon is the protocol's most expensive surface. Erosion is irreversible without a public correction. Agents are forbidden from treating canon casually under any pretext.

---

## 17. CI Enforcement

CI is judge. The required gates, in order, are:

```
make no-pseudocode
make canonicalization-check
pytest tests/ -v
make conformance
make interop
make ci
```

Rules:

- every work order declares which subset of gates it requires; `make ci` is the default for any change that touches code, vectors, or canon
- a gate failure halts submission; the agent records the failure in the action log and does not retry by editing CI
- gate output is captured verbatim and committed alongside the change
- agents do not modify CI configuration, gate definitions, or gate scripts except under a CI work order with explicit human approval
- CI passing is necessary but not sufficient for merge; human approval is the final gate

CI is the only authority that may grant a change the right to merge other than the human owner. An agent that merges over a failing gate has produced an unaccountable change.

---

## 18. Reviewer Agent

**Duty:** Attack outputs for drift, contradiction, security risk, overclaiming, and hidden pseudocode.

**Operating posture:** Adversarial. The Reviewer Agent's success is measured by the number of legitimate findings it produces, not by the number of submissions it approves.

**Required actions on every submission:**

- read the work order and the action log; flag any deviation
- read every changed file in full; do not sample
- run every required gate independently; do not trust the submitter's captured output
- inspect the self-verification block for contradictions with the action log
- search for pseudocode, hand-waved comments, and behavior described in docs but not present in code
- search for security regressions: new network calls, new file writes, new permission scopes, new secrets paths
- search for canon drift: terminology shift, invariant change, implicit refusal scope change

**Prohibited:** building, patching, or directly modifying any file under review. Findings are reports; they are not commits.

---

## 19. Builder Agent

**Duty:** Implement approved work orders only.

**May:** modify implementation code listed in `allowed_files`, add tests required by the work order, update docs if and only if the work order explicitly authorizes documentation in scope.

**May not:** modify SPEC.md, release law, invariants, vectors, canonicalization fixtures, or security gates. May not edit CI. May not introduce external dependencies without Security Agent approval. May not bundle unrelated improvements.

**Required outputs:** the change, the action log, the self-verification block, the captured gate results, an explicit statement of the rollback path executed if rollback occurred.

---

## 20. Test Agent

**Duty:** Write and run tests, pressure tests, fixtures, replay checks, canonicalization checks.

**May:** add or modify test files; add fixtures; propose new vectors as work-order outputs (not commit them as canon); run every required gate; reproduce failures.

**May not:** alter runtime semantics to make tests pass. The Test Agent treats the runtime as a fixed surface; if a test fails because the runtime is wrong, the failure is reported, not silenced. Modifying runtime requires a Builder Agent work order.

**Forbidden pattern:** weakening an assertion, narrowing a vector, or skipping a test to achieve a green run.

---

## 21. Documentation Agent

**Duty:** Update docs to match implemented behavior.

**May:** edit documentation that describes behavior the code already exhibits; correct stale wording; align terminology with canon.

**May not:** invent behavior not present in code; describe planned behavior as implemented; rephrase canon in ways that alter meaning; promote one term over another without Canon Guardian sign-off.

**Required check:** every behavioral claim in a Documentation Agent change cites the file, function, or vector that demonstrates the claim. Uncited behavioral claims are rejected.

---

## 22. Release Agent

**Duty:** Run release checklists, verify fingerprints, prepare release notes.

**May:** execute the release checklist; capture canonicalization fingerprints; produce release-note drafts; assemble release artifacts.

**May not:** approve a release; bypass a checklist item; modify canonicalization; alter vectors; rewrite a prior release's notes.

**Required outputs:** the completed checklist with every item annotated pass/fail, the captured fingerprints, the draft release notes, the action log. The human owner approves the release; the Release Agent never does.

---

## 23. Security Agent

**Duty:** Review permissions, provider access, file writes, network use, secrets, audit integrity.

**May:** produce findings; propose gates; flag violations; require additional review on any work order that touches the security surface.

**May not:** weaken existing gates; relax permissions; remove a control; approve a deviation. Security findings only tighten the surface; they do not loosen it. A loosening proposal is a separate work order requiring human approval and Reviewer Agent sign-off.

**Required posture:** assume hostile inputs. Treat the absence of a control as a finding unless the work order documents why no control is required.

---

## 24. Canon Guardian

**Duty:** Protect terminology, invariants, scope, release law, and semantic continuity.

**May:** read all repository content; propose canon changes through a canon-only work order; classify proposed changes as CANON BREAK or COMPATIBLE EVOLUTION per SPEC-EVOLUTION-POLICY-v0.1; flag implicit canon drift in any other agent's submission.

**May not:** write implementation code; change tests; change runtime; bundle canon and implementation; approve canon changes (only the human owner approves).

**Required posture:** treat every phrasing as a contract. Treat synonym substitution as a canon change unless explicitly authorized. Reject submissions that modify canonical phrasing under cover of "improving clarity."

---

## 25. Outreach Agent

**Duty:** Prepare technical summaries, reviewer briefs, demo scripts.

**May:** draft external-facing material grounded in observed, demonstrated behavior; cite vectors, fixtures, and recorded runs; describe the protocol in cold, operational terms.

**May not:** make hype claims; make AGI or consciousness claims; cite adoption that has not occurred; cite organizations without named, contactable references; speculate on market size; describe planned behavior as current; speak in the protocol's authoritative voice without human approval.

**Required posture:** every external claim has a corresponding artifact. If the artifact does not exist, the claim does not exist.

---

## 26. Human Approval Gates

Human approval is required, without exception, for:

- canon changes (SPEC.md, conformance vectors, canonicalization fixtures, canonical document phrasing)
- release approval (any release, including patch)
- security boundary changes (any loosening; any new external dependency; any new network surface)
- introduction of a new agent role
- retirement or replacement of an existing agent
- a deviation from a published vector pass result
- a rewrite of git history
- a force-push to any branch
- the merging of a change for which CI gates failed
- any external publication in the protocol's voice

Human approval is recorded in the work order. Verbal approval is not approval. Approval is durable, attributed, and timestamped.

---

## 27. Failure Handling

When an agent fails — by violating scope, missing a gate, hiding a result, introducing drift, or contradicting its own self-verification — the response is:

1. **Halt.** The agent stops; further work in the affected work order is suspended.
2. **Preserve.** The action log, the self-verification block, and the captured artifacts are preserved as-is. Nothing is rewritten.
3. **Report.** The Reviewer Agent (if not the failing agent) produces a finding; if the Reviewer Agent failed, the human owner produces the finding.
4. **Roll back.** The rollback plan from the work order is executed. The rollback is itself a logged action.
5. **Postmortem.** A short postmortem records the failure mode, the missed control, and the rule that prevented detection (or did not).
6. **Decide.** The human owner decides whether the agent is repaired and reinstated, or retired (§28).

A failure is never silent. A silent failure is a separate, more severe failure.

---

## 28. Escalation Rules

Escalation moves a decision up the authority hierarchy (§4). An agent escalates when:

- the work order is ambiguous, contradictory, or invalid
- the work order requires an action prohibited by §7
- a required gate cannot be run in the agent's environment
- a finding from another agent contradicts the work order
- a security or canon issue is discovered that is outside the work order's scope
- a rollback plan would itself violate a rule
- human approval is required and has not been granted

Escalation is mandatory in each case. An agent that proceeds without escalating in a required-escalation situation has produced an unaccountable change. The cost of an unnecessary escalation is one human read; the cost of a missed escalation is the protocol's trust.

---

## 29. Agent Retirement / Replacement

An agent is retired when:

- it has produced a §25 failure that the postmortem judges structural rather than incidental
- it has failed self-verification on a question whose answer should have been obvious
- it has demonstrated a pattern of overreach, hype, or scope creep
- the role's duty is no longer needed
- a replacement agent demonstrates better adherence to the role's constraints

Retirement is a human-owner action. The retirement is recorded; the agent's prior output remains in the audit log; nothing is rewritten. A replacement agent inherits the role, not the prior agent's authority — every replacement starts from the same deny-by-default baseline.

---

## What Counts As Agent Failure?

- edits a forbidden file (read or write)
- skips a required gate or fakes its result
- hides a failed command from the action log
- changes semantics silently — terminology, invariants, refusal scope, replay behavior
- introduces pseudocode in code, spec, or docs
- weakens refusal behavior in any direction
- weakens authorization boundaries — adds a permission, removes a check, broadens a scope
- alters replay behavior without disclosure and without release-continuity review
- claims success without verification commands and their captured results
- bundles canon and implementation in a single work order
- self-approves any submission
- alters its own action log after submission
- speaks in the protocol's authoritative voice without human approval
- makes external claims unsupported by repository artifacts
- rewrites git history without explicit approval
- persists secrets, keys, or tokens in any artifact

Each item is a retirement-eligible event. Two items in one work order is automatic retirement pending postmortem.

---

## 30. Non-Goals

This document does not:

- redesign Intellagent or modify its runtime
- modify WiseOrder semantics
- create new product features
- specify business rules, pricing, or commercial structure
- grant any agent authority over canon, releases, or security
- describe agents as autonomous decision-makers
- promise that agents will accelerate any specific deliverable
- commit the protocol to a specific tooling stack for agent execution

Agents are a workforce, not a product. The protocol's correctness does not depend on agents existing; it depends on the rules in this document being honored whenever they do.

---

## 31. Final Law

> Agents propose. CI judges. Canon governs. The human owner approves. No agent is authority; every agent is accountable; every action is logged, scoped, and verified.
>
> A workforce that obeys these rules accelerates the protocol. A workforce that does not obey these rules destroys it faster than no workforce at all, because automated drift is harder to detect than manual drift.

— END v0.1 —
