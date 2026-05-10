# DOC-COMPLETION-AUDIT v0.1

**Status:** Audit-only governance assessment, non-normative.
**Governing work order:** `WO-2026-05-07-004` (canon_guardian; constitutional-closure audit).
**Agent role:** `canon_guardian`
**Agent identity:** `canon_guardian-01`
**Date of run:** 2026-05-08.
**Companion documents:** `SPEC.md`, `MASTER-ROADMAP-v0.1.md`, `WORKFORCE-EXECUTION-RUNTIME-v0.1.md`, `AGENT-GOVERNANCE-WORKFORCE-v0.1.md`, `RELEASE-STATUS-v0.1.md`.

> This audit does not extend canon. It does not introduce primitives, governance layers, or cognition classes. It surveys the governance documents already on disk, identifies the bounded set that remains required for first constitutional closure, names the categories that must NOT be added, and defines the stop condition that ends the document-expansion phase.

---

## 1. Purpose

This audit answers four questions, deterministically, against the on-disk top-level document corpus:

1. **What governance surfaces does the existing corpus already cover, and at what depth?**
2. **Where does the corpus risk overlap, contradiction, or drift if expansion continues unchecked?**
3. **What bounded set of remaining documents is required for first constitutional closure, and no more?**
4. **At what point does further document expansion become the wrong work, and execution / hardening / replay / interop / sandbox / release become the right work?**

The deliverable is this audit and nothing else. No SPEC change, no validator change, no governance amendment, no canon mutation, and no new cognition class is authorized by this work order or proposed by this audit. The audit recommends a bounded queue of at most ten remaining documents; none of those is authorized by this audit, and each requires its own drafted, approved, and assigned work order per `AGENT-GOVERNANCE-WORKFORCE-v0.1.md` §3.

The audit's sole authority is *observation and classification*. Every claim is grounded in the current state of the top-level `*.md` corpus.

---

## 2. Current Document Inventory

The top-level governance corpus contains **35** Markdown documents, listed alphabetically:

| # | File | Versioned |
| -: | --- | :-: |
| 01 | `ADOPTION-LADDER-v0.1.md` | v0.1 |
| 02 | `AGENT-GOVERNANCE-WORKFORCE-v0.1.md` | v0.1 |
| 03 | `ARCHITECTURE-PRESSURE-TESTS-v0.1.md` | v0.1 |
| 04 | `ARTIFACTS.md` | unversioned (extract) |
| 05 | `AUTHORITY-LAW-v0.1.md` | v0.1 |
| 06 | `CANONICAL-RELEASE-v0.1.md` | v0.1 |
| 07 | `CONFORMANCE.md` | unversioned (extract) |
| 08 | `CORRECTION-LAW-v0.1.md` | v0.1 |
| 09 | `CROSS-LANGUAGE-CANONICALIZATION-v0.1.md` | v0.1 |
| 10 | `DEPENDENCY-GRADIENT-v0.1.md` | v0.1 |
| 11 | `FORBIDDEN-SURFACES-v0.1.md` | v0.1 |
| 12 | `IMPLEMENTATIONS.md` | unversioned (registry) |
| 13 | `INPUT-GRAMMAR-v0.1.md` | v0.1 |
| 14 | `INTELLAGENT-DEMOS.md` | unversioned (draft) |
| 15 | `INTELLAGENT-EVALUATION.md` | unversioned (draft) |
| 16 | `INTELLAGENT-PROPOSERS.md` | unversioned (draft) |
| 17 | `INTELLAGENT-RUNTIME.md` | unversioned (draft) |
| 18 | `INTELLAGENT.md` | unversioned (draft) |
| 19 | `MASTER-ROADMAP-v0.1.md` | v0.1 |
| 20 | `README.md` | unversioned |
| 21 | `RELEASE-CHECKLIST-v0.1.md` | v0.1 |
| 22 | `RELEASE-STATUS-v0.1.md` | v0.1 |
| 23 | `REPLAY-LAW-v0.1.md` | v0.1 |
| 24 | `SPEC-EVOLUTION-POLICY-v0.1.md` | v0.1 |
| 25 | `SPEC.md` | v0.1.0 (Draft Canon) |
| 26 | `STATUS-REGISTRY.md` | unversioned (extract) |
| 27 | `TOOLS.md` | unversioned |
| 28 | `TRANSFORMER-PROPOSER-v0.1.md` | v0.1 |
| 29 | `TRANSLATION-LAYER-v0.1.md` | v0.1 |
| 30 | `TRUST-LAW-v0.1.md` | v0.1 |
| 31 | `VALIDATION-LAW-v0.1.md` | v0.1 |
| 32 | `WORKFLOW-GRAMMAR-v0.1.md` | v0.1 |
| 33 | `WORKFORCE-EXECUTION-RUNTIME-v0.1.md` | v0.1 |
| 34 | `WORKFORCE-HARDENING-v0.2.md` | v0.2 |
| 35 | `WORKFORCE-SANDBOX-STRESS-v0.1.md` | v0.1 |

Counts (closure-relevant):

| Field | Count |
| --- | -: |
| Total top-level documents | 35 |
| Versioned `*-v0.1.md` documents | 21 |
| Versioned `*-v0.2.md` documents | 1 |
| Unversioned reference / extract / registry documents | 8 |
| Documents with `Status: Draft Canon` or `Locked` lock declaration | 2 (`SPEC.md`, `ARCHITECTURE-PRESSURE-TESTS-v0.1.md`) |
| Documents with explicit `non-normative` declaration | ≥6 |

---

## 3. Functional Classification

Each top-level document is assigned to exactly one operational role, per the work order's eight buckets.

| Bucket | Document(s) | Count |
| --- | --- | -: |
| **Constitutional kernel + laws** | `SPEC.md`, `AUTHORITY-LAW-v0.1.md`, `CORRECTION-LAW-v0.1.md`, `REPLAY-LAW-v0.1.md`, `TRUST-LAW-v0.1.md`, `VALIDATION-LAW-v0.1.md`, `FORBIDDEN-SURFACES-v0.1.md` | 7 |
| **Operational / runtime specs** | `INTELLAGENT.md`, `INTELLAGENT-RUNTIME.md`, `INTELLAGENT-PROPOSERS.md`, `TRANSFORMER-PROPOSER-v0.1.md`, `INTELLAGENT-EVALUATION.md`, `INTELLAGENT-DEMOS.md`, `INPUT-GRAMMAR-v0.1.md`, `WORKFLOW-GRAMMAR-v0.1.md` | 8 |
| **Validator / workforce specs** | `AGENT-GOVERNANCE-WORKFORCE-v0.1.md`, `WORKFORCE-EXECUTION-RUNTIME-v0.1.md`, `WORKFORCE-HARDENING-v0.2.md`, `WORKFORCE-SANDBOX-STRESS-v0.1.md` | 4 |
| **Release / milestone artifacts** | `CANONICAL-RELEASE-v0.1.md`, `RELEASE-CHECKLIST-v0.1.md`, `RELEASE-STATUS-v0.1.md`, `SPEC-EVOLUTION-POLICY-v0.1.md` | 4 |
| **Translation / communication docs** | `TRANSLATION-LAYER-v0.1.md` | 1 |
| **Pressure / security docs** | `ARCHITECTURE-PRESSURE-TESTS-v0.1.md`, `CROSS-LANGUAGE-CANONICALIZATION-v0.1.md` | 2 |
| **Roadmap / directional docs** | `MASTER-ROADMAP-v0.1.md`, `ADOPTION-LADDER-v0.1.md`, `DEPENDENCY-GRADIENT-v0.1.md` | 3 |
| **Supporting / reference docs** | `README.md`, `CONFORMANCE.md`, `STATUS-REGISTRY.md`, `ARTIFACTS.md`, `IMPLEMENTATIONS.md`, `TOOLS.md` | 6 |
| **Total** |  | **35** |

Closure-relevant counts derived from the table above:

| Closure-relevant count | Value |
| --- | -: |
| Total core constitutional laws (incl. kernel `SPEC.md`) | **7** |
| Total supporting specs (operational + validator + pressure) | **14** |
| Load-bearing documents (kernel + laws + operational/validator/pressure specs) | **21** |
| Supporting-only documents (translation + supporting/reference) | **7** |
| Release artifacts | **4** |
| Roadmap docs | **3** |

A "load-bearing" document is one whose deletion would break the legitimacy or replayability of an action recorded under workforce or release operations. A "supporting-only" document is one that summarizes or reframes load-bearing content and could be regenerated from the load-bearing set.

---

## 4. Existing Constitutional Laws

The constitutional layer consists of one kernel and six laws. Together they define what is permitted, what must be replayable, what may be corrected, what may be admitted, what authority may be exercised, and what surfaces may not be touched.

| Document | Law surface | Lock status |
| --- | --- | --- |
| `SPEC.md` | Constitutional kernel: classes, statuses, canonicalization, conformance, artifacts, refusal, audit chain. | Draft Canon, Locked unless implementation reality breaks it. |
| `AUTHORITY-LAW-v0.1.md` | Declared, bounded, recorded, replayable authority across humans, agents, reviewers, release operators. | Normative. |
| `CORRECTION-LAW-v0.1.md` | Correction legitimacy, divergence handling, hardening legitimacy. | Normative. |
| `REPLAY-LAW-v0.1.md` | Reconstructability, reproducibility, replayability of recorded operations. | Normative. |
| `TRUST-LAW-v0.1.md` | Trust accumulation, invalidation, evidence-based dependency formation. | Normative. |
| `VALIDATION-LAW-v0.1.md` | Validator legitimacy, gate legitimacy, admissibility, deterministic inspection. | Normative. |
| `FORBIDDEN-SURFACES-v0.1.md` | Non-authority boundary surface — what may not be touched without declared authority. | Normative non-authority surface. |

**Coverage observation.** The five `*-LAW-v0.1.md` documents form a self-consistent tuple. Each declares what it does *not* redefine, and each names the others as out-of-scope. Together with `FORBIDDEN-SURFACES-v0.1.md` they account for: who may act (Authority), how recorded action may be reconstructed (Replay), how divergences may be repaired (Correction), how trust accumulates from recorded behavior (Trust), how admissibility is enforced (Validation), and where authority may not be applied (Forbidden Surfaces). The kernel `SPEC.md` is the substrate over which they bind.

**Closure observation.** No additional `*-LAW-v0.1.md` document is structurally required for v0.1. The known follow-up work items from `WO-2026-05-07-001` and `WO-2026-05-07-003` (FU-1, FU-2, FU-3, FU-14, FU-15) are *amendments to existing specs* and *supporting governance instruments*, not new laws.

---

## 5. Existing Operational Specs

The operational layer consists of 8 documents covering architecture, runtime, proposer abstractions, demos, evaluation, input grammar, and workflow grammar.

| Document | Operational surface |
| --- | --- |
| `INTELLAGENT.md` | Architecture proposal: governed transitions over the WiseOrder kernel. |
| `INTELLAGENT-RUNTIME.md` | Runtime spec: state machine, audit memory, authorization gate, refusal record. |
| `INTELLAGENT-PROPOSERS.md` | Proposer interface contract: candidate-only, never authority. |
| `TRANSFORMER-PROPOSER-v0.1.md` | Transformer integration: provider-agnostic, deterministic-replay-capable, untrusted-by-default. |
| `INTELLAGENT-EVALUATION.md` | Benchmark framework: 10 scenarios × 9 axes × 8 metrics, no partial credit. |
| `INTELLAGENT-DEMOS.md` | Demonstration suite: 10 demos against `DeterministicMockProvider`, byte-deterministic. |
| `INPUT-GRAMMAR-v0.1.md` | Human-to-execution translation discipline at the input layer. |
| `WORKFLOW-GRAMMAR-v0.1.md` | Stage-to-stage operational continuity grammar. |

**Coverage observation.** The runtime axis (architecture → runtime → proposer → transformer integration → evaluation → demos) is fully populated. The grammar axis (input → workflow) is populated and named as non-overlapping with runtime, governance, and validator semantics by each document's own scope clause.

**Closure observation.** No additional operational-spec document is structurally required for v0.1 unless implementation reality breaks an assumption in one of the existing specs (in which case the change is governed by `SPEC-EVOLUTION-POLICY-v0.1.md`, not by adding a new doc).

---

## 6. Existing Roadmaps

| Document | Directional surface |
| --- | --- |
| `MASTER-ROADMAP-v0.1.md` | 20-year directional framework; immutable core principles; six strategic phases; explicit non-goals; non-prescriptive on calendar dates. |
| `ADOPTION-LADDER-v0.1.md` | Operational stages from isolated protocol to trusted infrastructure dependency; one-directional; cannot be skipped. |
| `DEPENDENCY-GRADIENT-v0.1.md` | Sequence of operational properties that move the system from "available" to "depended upon"; one-directional. |

**Coverage observation.** The roadmap axis is saturated. `MASTER-ROADMAP` covers long-term direction; `ADOPTION-LADDER` covers the operational sequence by which adoption progresses; `DEPENDENCY-GRADIENT` covers the property compounding that makes the system load-bearing for outside systems.

**Closure observation.** Adding a fourth roadmap is the highest-risk drift category in the entire corpus. See §13 (Redundant Surface Warnings) and §14 (Documents That Should NOT Be Created).

---

## 7. Existing Translation Docs

| Document | Translation surface |
| --- | --- |
| `TRANSLATION-LAYER-v0.1.md` | Plain-language explanation of the stack (Intellagent, WiseOrder, Winstack, WOP) for non-technical readers; explicit on what the stack does NOT claim. |

**Coverage observation.** The translation axis has one document and is sufficient at v0.1. The document is explicitly non-normative and explicitly bounded.

**Closure observation.** No additional translation document is structurally required at v0.1. A second translation document for a different audience (e.g., regulators, partners) is a candidate for v0.2+, governed by the same anti-drift discipline.

---

## 8. Existing Pressure Docs

| Document | Pressure surface |
| --- | --- |
| `ARCHITECTURE-PRESSURE-TESTS-v0.1.md` | Failure-oriented validation: the falsification surface for the cognition architecture; locked baseline. |
| `CROSS-LANGUAGE-CANONICALIZATION-v0.1.md` | Pressure surface for cross-language canonical-byte agreement; documents the gap between Python v0.1 and RFC 8785 JCS. |

**Coverage observation.** The pressure axis is partially populated. Architecture-level falsification is covered. Cross-language canonicalization is covered as a documented pressure surface, but the drift surfaces it enumerates remain unexercised by the v0.1 corpus per `reports/canonicalization_readiness_audit_v0.1.md`.

**Closure observation.** A second pressure document covering cross-runtime, cross-machine, and cross-Python-version determinism is a v0.2 candidate. It is not strictly required for first constitutional closure because the existing pressure docs already document the gap; closing the gap is *execution work*, not *document work*.

---

## 9. Existing Release Docs

| Document | Release surface |
| --- | --- |
| `CANONICAL-RELEASE-v0.1.md` | Public technical release statement for Intellagent v0.1; enumerates components, versions, prerequisite reading. |
| `RELEASE-CHECKLIST-v0.1.md` | Operational gate definitions; seven gates in execution order; a single failure blocks release. |
| `RELEASE-STATUS-v0.1.md` | Current pass/fail state across every gate at release date; pre-release status report. |
| `SPEC-EVOLUTION-POLICY-v0.1.md` | Change-control surface for SPEC and dependent specs; rules under which the protocol family may change. |

**Coverage observation.** Release axis is fully populated for v0.1. Static (canonical statement), procedural (checklist), instantaneous (status), and longitudinal (evolution policy) views are all present and cross-referenced.

**Closure observation.** No additional release document is structurally required for v0.1. A `RELEASE-PLAYBOOK` for closure operators may be useful operationally but is a v0.2 candidate at most.

---

## 10. Overlap Analysis

The corpus is largely non-overlapping by explicit scope declaration. Each `*-LAW-v0.1.md` and each grammar/forbidden-surfaces document begins with a "Scope" or "Status" clause naming the layers it does NOT redefine. The remaining overlap risks are:

- **O-1.** *Roadmap layer overlap:* `ADOPTION-LADDER-v0.1.md` (operational stages) and `DEPENDENCY-GRADIENT-v0.1.md` (operational properties) both describe one-directional progression toward infrastructure status. They are framed differently (stages vs. properties), but a careless reader could conflate them. Mitigation: each document declares its own surface and names the other as a companion. No corrective action required at v0.1.
- **O-2.** *Workforce layer overlap:* `AGENT-GOVERNANCE-WORKFORCE-v0.1.md` (roles + authority) and `WORKFORCE-EXECUTION-RUNTIME-v0.1.md` (lifecycle + records) operate on overlapping subjects but are explicit about the *who/what* vs. *how* split. `WORKFORCE-HARDENING-v0.2.md` extends the validator surface specified in the runtime doc; `WORKFORCE-SANDBOX-STRESS-v0.1.md` provides an opt-in pressure harness. The four documents form a coherent layered set with no semantic overlap.
- **O-3.** *Release / status / checklist overlap:* `RELEASE-CHECKLIST-v0.1.md` (gate definitions) and `RELEASE-STATUS-v0.1.md` (current state) intentionally overlap in subject because the second is the instantaneous evaluation of the first. `CANONICAL-RELEASE-v0.1.md` lists the components; `SPEC-EVOLUTION-POLICY-v0.1.md` governs their change. No drift; the four documents form the release-axis tuple.
- **O-4.** *SPEC.md and SPEC-extract overlap:* `STATUS-REGISTRY.md`, `ARTIFACTS.md`, and `CONFORMANCE.md` are explicit extracts from `SPEC.md` §9, §10, §11–§13 respectively, with prominent "in case of any discrepancy with `SPEC.md`, `SPEC.md` governs" disclaimers. The overlap is by design and is mechanically subordinate to the canon.

**Result.** Overlap risk is low. Each potential overlap is either disclaimed in scope clauses, ordered by an explicit "in case of conflict, X governs" rule, or layered along a *who/what/how/state* axis.

---

## 11. Contradiction Risk

A contradiction risk is a place where two documents could disagree on a normative claim such that both could not be true at once.

- **C-1.** *SPEC vs. extracts:* Resolved by the "in case of discrepancy, SPEC.md governs" disclaimer in every extract. No actual contradictions are currently present.
- **C-2.** *Cross-language canonicalization vs. SPEC §4:* `SPEC.md` §4 mandates RFC 8785 JCS for Class A. `CROSS-LANGUAGE-CANONICALIZATION-v0.1.md` documents that the v0.1 Python canonicalizer does not fully implement RFC 8785 JCS. This is *not* a contradiction in the documents — the second document is the explicit gap report — but it is a contradiction between SPEC and runtime. Resolution surface is `reports/canonicalization_readiness_audit_v0.1.md` and `SPEC-EVOLUTION-POLICY-v0.1.md`. The contradiction is *acknowledged* and is the v0.1 → v0.2 migration target. Adding new documents does not narrow it; *implementation work* does.
- **C-3.** *Runtime vs. proposer interface drift:* `INTELLAGENT-RUNTIME.md` specifies a `Proposer` interface; `INTELLAGENT-PROPOSERS.md` specifies how learned proposers integrate; `TRANSFORMER-PROPOSER-v0.1.md` specifies the transformer integration. The three documents are 1:1 with the implementation per `RELEASE-STATUS-v0.1.md` §1. No active contradiction; the future risk is that any one drifts independently of the others. Mitigation: `SPEC-EVOLUTION-POLICY-v0.1.md` is the change-control surface and binds them together.
- **C-4.** *Workforce lifecycle vs. validator enforcement:* `WORKFORCE-EXECUTION-RUNTIME-v0.1.md` specifies the lifecycle. `WORKFORCE-HARDENING-v0.2.md` migrates stress-suite findings into the native validator. The validator now enforces lifecycle order (rule `lifecycle_out_of_order`, surfaced and corrected during `WO-2026-05-07-003` closure). The runtime spec and the validator are consistent; no contradiction.

**Result.** Contradiction risk is low and bounded. Every present contradiction is *between document and runtime reality*, not *between two documents*. Such contradictions are the legitimate work of `SPEC-EVOLUTION-POLICY-v0.1.md`, not of new documents.

---

## 12. Missing Surfaces

A "missing surface" is a governance surface that the existing corpus does not address and whose absence is currently load-bearing on convention rather than declaration.

- **M-1.** *Formal waiver mechanism for `allowed_files` / `forbidden_files`.* Surfaced as L-3 in the `WO-2026-05-07-001` closure summary. The runtime spec asserts immutability of work-order content other than `status` and `status_history` (§21), but real closures have required amendments to `forbidden_files`. The waiver is currently performed by recording an `amended` `status_history` entry; no document declares this as a sanctioned mechanism with required justification fields.
- **M-2.** *Reviewer identity discipline.* Surfaced as L-1 in the `WO-2026-05-07-001` closure summary. `WORKFORCE-EXECUTION-RUNTIME-v0.1.md` §19 forbids self-review, but only one reviewer identity exists in v0.1; the human owner has assumed the reviewer signoff role for two work orders. No document declares the human-owner-as-reviewer fallback as a sanctioned mechanism.
- **M-3.** *Audit-grounding read access into `forbidden_files`.* Surfaced as L-2 in the `WO-2026-05-07-001` closure summary. A reviewer-role audit may need to read a forbidden file to verify a claim. No document declares an `audit_read_grants` field, a `forbidden_writes` / `forbidden_reads` split, or an equivalent mechanism.
- **M-4.** *Closure-operator runbook.* Surfaced as L-5 in the `WO-2026-05-07-003` closure summary. Lifecycle ordering rules are mechanically enforced and the spec-canonical order is not the wall-clock order. Post-hoc closures need explicit operator discipline; no document specifies it.
- **M-5.** *Canonical-interpreter pinning policy.* Surfaced as L-4 / FU-14 in the `WO-2026-05-07-003` closure summary. `make ci` defaults `PYTHON` to environment-resolved `python3`. No document declares which interpreter the gates are validated against.
- **M-6.** *Threat model.* The corpus does not contain an explicit threat-model document. Adversarial cases are addressed by `ARCHITECTURE-PRESSURE-TESTS-v0.1.md` and `WORKFORCE-SANDBOX-STRESS-v0.1.md`, but neither is a unified threat model with named adversaries, capabilities, and out-of-scope risks.
- **M-7.** *Agent / actor identity and key material.* The corpus declares actor strings in `status_history` and action logs but does not declare a per-identity key, signing scheme, or attestation surface. `WORKFORCE-EXECUTION-RUNTIME-v0.1.md` §27 names this as future enforcement; no specification document declares the eventual mechanism.
- **M-8.** *Constitutional-closure declaration.* No document declares what constitutional closure *is*, when it is *achieved*, and what changes about the documentation discipline *after* it is achieved. This audit is the proximate cause of writing such a document; the document itself does not yet exist.

**Result.** Eight missing surfaces are identified. Five (M-1, M-2, M-3, M-4, M-5) are immediate amendments to existing specs or small new operator runbooks; three (M-6, M-7, M-8) are larger but bounded specifications. None requires a new constitutional law.

### What Is Missing For Closure?

The following surfaces are **load-bearing on convention rather than declaration** and must be declared before constitutional closure can be granted:

1. A formal waiver mechanism for `allowed_files` / `forbidden_files` (M-1).
2. Reviewer identity discipline including the human-owner-as-reviewer fallback (M-2).
3. Audit-grounding read access into `forbidden_files` (M-3).
4. Closure-operator runbook (M-4).
5. Canonical-interpreter pinning policy (M-5).
6. Threat model for v0.1 (M-6).
7. Agent / actor identity and key material specification (M-7).
8. A constitutional-closure declaration document (M-8).

The above eight items are the **bounded missing surface**. They are not new laws; they are governance instruments that bind the existing corpus to operational reality and lock the documentation phase. Resolving them does not extend the canon; it terminates the document-expansion phase by declaring that no further document is required for v0.1.

Two additional items remain *desirable but not load-bearing for closure*:

- A second-audience translation document (regulators, partners). Not required for v0.1; v0.2+ candidate.
- A migration policy specifically for v0.1 → v0.2 in the runtime layer (extension of `SPEC-EVOLUTION-POLICY-v0.1.md` to runtime artifacts). Not required if `SPEC-EVOLUTION-POLICY-v0.1.md` is read as covering runtime artifacts already; if not, a small clarifying amendment is sufficient and does not require a new document.

These two items do **not** appear in the bounded queue in §15.

---

## 13. Redundant Surface Warnings

Surfaces that the corpus already covers and that must NOT be reopened by new documents:

- **R-1.** *Roadmap.* Three roadmap documents already exist. Adding a fourth roadmap (5-year, 10-year, business roadmap, "vision" roadmap, "strategic plan" doc) is the highest-risk drift category and is forbidden by §14.
- **R-2.** *Constitutional law.* Six constitutional laws plus the kernel are sufficient for v0.1. Adding a seventh law (e.g., "Refusal Law", "Audit Law", "Provenance Law") risks redefining surfaces already covered by `VALIDATION-LAW`, `REPLAY-LAW`, and `TRUST-LAW`.
- **R-3.** *Workforce layer.* Four workforce documents (governance + execution runtime + hardening + sandbox stress) form a tight tuple. Adding a fifth workforce document (e.g., a "WORKFORCE-PHILOSOPHY", "WORKFORCE-METHODOLOGY", "WORKFORCE-OPERATIONS-V2") risks duplicating their content.
- **R-4.** *Release axis.* Four release documents are sufficient. Adding "RELEASE-PROCESS", "RELEASE-PHILOSOPHY", "RELEASE-NOTES-FORMAT" duplicates surface already in `RELEASE-CHECKLIST-v0.1.md` and `SPEC-EVOLUTION-POLICY-v0.1.md`.
- **R-5.** *Translation layer.* One translation document is sufficient at v0.1. Adding more than one introduces audience-confusion drift.
- **R-6.** *Pressure layer.* Two pressure documents are sufficient at v0.1. The right next move is *executing* the pressure tests they enumerate, not writing more pressure documents.

---

## 14. Documents That Should NOT Be Created

The following document categories are **forbidden** from being written under the document-expansion phase, before, during, or after constitutional closure, unless and until a runtime-pressured discovery proves a missing governance surface and a new work order is drafted, approved, and assigned to author the missing surface.

| Forbidden category | Why forbidden |
| --- | --- |
| **Marketing / positioning / vision documents** | Not code-grounded; produces drift at the input layer. |
| **Methodology / philosophy documents** | Restate the existing constitutional layer in narrative form; high overlap risk. |
| **Additional roadmap documents (4th roadmap and beyond)** | Roadmap surface is saturated; adding more produces audience-confusion drift. |
| **Per-implementation specifications** | Belong in the implementation's own repository or `IMPLEMENTATIONS.md` registry. |
| **"Best practices" or "guidelines" documents** | Soft-normative; conflict with hard-normative constitutional layer. |
| **Documents about the documentation process itself** | Recursive surface; the existing `SPEC-EVOLUTION-POLICY-v0.1.md` covers change control. |
| **Any new `*-LAW-v0.1.md` beyond the existing six** | Constitutional layer is closed for v0.1; v0.2 amendments are governed by `SPEC-EVOLUTION-POLICY-v0.1.md`. |
| **Marketing case studies, launch announcements, blog posts** | Not governance surface. Belong elsewhere. |
| **Copies / mirrors / "v2 drafts" of existing documents** | Drift vector. Amendments go inside the existing document under SPEC-EVOLUTION-POLICY rules. |
| **Aspirational architecture documents not bound to runtime** | Produces drift between document and reality. |

### What Should Not Be Added?

In one sentence: **anything that is not a small, named, governance-binding surface required to lock convention into declaration; in particular, no new roadmap, no new constitutional law, no new workforce-layer document beyond the current four, no new translation document for v0.1, no new pressure document for v0.1, no new release document for v0.1, no marketing or vision document at any time, and no document whose purpose is to summarize or restate documents that already exist.**

---

## 15. Final Required Document List

The bounded set of remaining documents required for first constitutional closure. **At most ten entries.** Each entry is a candidate work order; this audit authorizes none of them.

### Recommended Next 10 Documents Max

1. **`CONSTITUTIONAL-CLOSURE-v0.1.md`**
   - **Purpose:** Declare what first constitutional closure is, when it is achieved, what locks at closure, and what changes about the documentation discipline post-closure.
   - **Contradiction boundaries:** Does not redefine SPEC, laws, runtime, validator, governance, or any existing canon. Is itself a meta-document that asserts the doc-expansion phase has ended.
   - **Necessity justification:** Without this document, "constitutional closure" remains a phrase used by audits, not a state declared by canon. The system cannot know when document-expansion stops.
   - **Closure relevance:** Maximal. Closure is not closure until it is declared.
   - **Priority:** **P0** (must be the last document written; everything else feeds into its closure declaration).

2. **`WAIVER-MECHANISM-v0.1.md`**
   - **Purpose:** Sanctioned mechanism for amending `allowed_files` / `forbidden_files` at closure time, with required justification fields, recorded rationale, and a pre-closure / post-closure distinction.
   - **Contradiction boundaries:** Does not change `WORKFORCE-EXECUTION-RUNTIME-v0.1.md` §21 immutability of other fields; it carves out a single, named, recorded exception for the file-scope fields.
   - **Necessity justification:** Two of three closures so far have required ad-hoc forbidden_files amendments. Convention is load-bearing where declaration must be.
   - **Closure relevance:** High. M-1 / L-3 / FU-1.
   - **Priority:** **P1**.

3. **`REVIEWER-IDENTITY-v0.1.md`**
   - **Purpose:** Specify reviewer identity discipline including the human-owner-as-reviewer fallback when no second reviewer identity exists, and the eventual second-reviewer requirement.
   - **Contradiction boundaries:** Does not change `WORKFORCE-EXECUTION-RUNTIME-v0.1.md` §19 prohibition on self-review; it sanctions one and only one fallback identity.
   - **Necessity justification:** Three closures so far have used the human-owner-as-reviewer fallback without sanctioning document.
   - **Closure relevance:** High. M-2 / L-1 / FU-2.
   - **Priority:** **P1**.

4. **`AUDIT-READ-GRANTS-v0.1.md`**
   - **Purpose:** Sanctioned mechanism for non-mutating audit-grounding reads into `forbidden_files`, either via an `audit_read_grants` field on the work-order schema or a `forbidden_writes` / `forbidden_reads` split.
   - **Contradiction boundaries:** Does not weaken the validator's enforcement of `forbidden_files` against writes; it carves out a recorded read-only exception.
   - **Necessity justification:** Two of the three V deviations in `WO-2026-05-07-001` were exactly this case. Convention is load-bearing where declaration must be.
   - **Closure relevance:** High. M-3 / L-2 / FU-3.
   - **Priority:** **P1**.

5. **`CLOSURE-OPERATOR-RUNBOOK-v0.1.md`**
   - **Purpose:** Operator discipline for closure cycles: lifecycle-ordering invariants for post-hoc closures, gate-rerun discipline, action-log pair authoring, closure-summary structure.
   - **Contradiction boundaries:** Does not extend `WORKFORCE-EXECUTION-RUNTIME-v0.1.md`; it is the operator-facing companion to it.
   - **Necessity justification:** `WO-2026-05-07-003` surfaced an operator error (lifecycle reorder) that the validator caught. The runbook prevents recurrence.
   - **Closure relevance:** Medium. M-4 / L-5 / FU-15.
   - **Priority:** **P2**.

6. **`CANONICAL-INTERPRETER-v0.1.md`**
   - **Purpose:** Declare which Python interpreter the gates are validated against (`.venv/bin/python` per `.venv/pyvenv.cfg`), and the policy for pinning `make ci` to it.
   - **Contradiction boundaries:** Does not change SPEC, runtime, or validator semantics; it declares the operating interpreter as canon-adjacent infrastructure.
   - **Necessity justification:** `WO-2026-05-07-003` revealed that `make ci` exits 0 only under `PYTHON=.venv/bin/python` and exits 2 under system `python3`. Interpreter pinning is currently convention.
   - **Closure relevance:** Medium. M-5 / L-4 / FU-14.
   - **Priority:** **P2**.

7. **`THREAT-MODEL-v0.1.md`**
   - **Purpose:** Unified threat model: named adversaries, capabilities, in-scope and out-of-scope risks, the relationship between threat surfaces and existing pressure tests, and the residual risks accepted at v0.1.
   - **Contradiction boundaries:** Does not redefine `ARCHITECTURE-PRESSURE-TESTS-v0.1.md` or `WORKFORCE-SANDBOX-STRESS-v0.1.md`; it is the threat-surface scaffold those pressure documents pressure-test.
   - **Necessity justification:** Adversarial reasoning in the corpus is currently distributed across multiple pressure documents. A unified threat model bounds the adversary surface.
   - **Closure relevance:** Medium. M-6.
   - **Priority:** **P2**.

8. **`AGENT-IDENTITY-v0.1.md`**
   - **Purpose:** Specify the agent / actor identity surface for v0.2: per-identity key material, signing scheme, action-log attestation, work-order approval signing.
   - **Contradiction boundaries:** Does not retroactively require keys for v0.1 records; it specifies the v0.2 enforcement target so that v0.1 records can be migrated forward without rewriting.
   - **Necessity justification:** `WORKFORCE-EXECUTION-RUNTIME-v0.1.md` §27 names this as future enforcement; the eventual mechanism is currently undeclared.
   - **Closure relevance:** Medium. M-7.
   - **Priority:** **P3** (specifies a v0.2 surface; may be deferred behind a clear v0.2 work order).

9. **`STRESS-FIXTURE-CORPUS-v0.1.md`**
   - **Purpose:** Declare the workforce-stress fixture corpus (the 100 rule templates × 3 variants) as a versioned governance artifact, separate from the script that generates it, with its own corpus_sha256-style stability anchor.
   - **Contradiction boundaries:** Does not change `WORKFORCE-SANDBOX-STRESS-v0.1.md`; it carves out the fixtures as a first-class artifact distinct from the harness.
   - **Necessity justification:** The stress harness is currently script-resident; the fixtures are not separately addressable. As stress augmentations migrate to native validation under the hardening cycle, the fixtures need their own version anchor.
   - **Closure relevance:** Low–Medium. Optional but bounded.
   - **Priority:** **P3** (may be deferred to v0.2 hardening cycle).

10. **`v0.2-MIGRATION-NOTE-v0.1.md`** (single short note, not a full migration spec)
    - **Purpose:** A small, bounded note declaring that runtime-layer artifacts (canonicalization corpus, conformance vectors, interop fixtures, stress fixture corpus) are governed by `SPEC-EVOLUTION-POLICY-v0.1.md` for the v0.1 → v0.2 transition, with explicit list of which artifacts will be re-anchored at v0.2 release.
    - **Contradiction boundaries:** Does not extend `SPEC-EVOLUTION-POLICY-v0.1.md`; it is a list of artifacts the policy applies to during the v0.2 cut.
    - **Necessity justification:** Currently the artifact-set governed by SPEC-EVOLUTION-POLICY is implicit in cross-references. A short list document removes the ambiguity.
    - **Closure relevance:** Low. Optional but bounded.
    - **Priority:** **P3**.

**Bound check.** 10 entries. ≤ 10. Each entry has document name + purpose + contradiction boundaries + necessity justification + closure relevance + priority. All six required sub-fields present per entry.

**Authority check.** This audit authorizes none of these. Each entry is a candidate work order requiring its own drafted, approved, and assigned governance work order per `AGENT-GOVERNANCE-WORKFORCE-v0.1.md` §3.

---

## 16. Priority Order

The recommended order in which the bounded queue should be drafted, approved, assigned, and closed:

1. **P1 batch (closure blockers — convention-to-declaration locks):**
   - `WAIVER-MECHANISM-v0.1.md`
   - `REVIEWER-IDENTITY-v0.1.md`
   - `AUDIT-READ-GRANTS-v0.1.md`
2. **P2 batch (operator and infrastructure discipline):**
   - `CLOSURE-OPERATOR-RUNBOOK-v0.1.md`
   - `CANONICAL-INTERPRETER-v0.1.md`
   - `THREAT-MODEL-v0.1.md`
3. **P3 batch (deferrable v0.2 surface preparation):**
   - `AGENT-IDENTITY-v0.1.md` (deferrable to v0.2 work order)
   - `STRESS-FIXTURE-CORPUS-v0.1.md` (deferrable to v0.2 hardening cycle)
   - `v0.2-MIGRATION-NOTE-v0.1.md` (deferrable to v0.2 cut)
4. **P0 (last; declares the closure that the prior items make possible):**
   - `CONSTITUTIONAL-CLOSURE-v0.1.md`

P1 is sequenced first because each P1 item replaces a load-bearing convention with a load-bearing declaration. P2 is sequenced second because it codifies operator discipline and infrastructure assumptions. P3 is sequenced third because each item is deferrable without blocking closure of the prior phases. P0 is sequenced last because it cannot be written until the prior phases (or their explicit deferral) are recorded.

---

## 17. Closure Criteria

First constitutional closure is achieved when **all** of the following are true on disk:

1. The seven constitutional documents (`SPEC.md` + the six laws) and `FORBIDDEN-SURFACES-v0.1.md` are committed and locked under `SPEC-EVOLUTION-POLICY-v0.1.md`.
2. The eight operational/runtime specs are committed.
3. The four workforce/validator specs are committed and the validator enforces lifecycle, scope, gates, action-log presence, self-verification presence, and human-approval closure.
4. The four release documents are committed and `make ci` exits 0 under the canonical interpreter.
5. The three roadmap documents are committed and saturate the directional axis.
6. The translation, pressure, and supporting/reference documents are committed and saturate their respective axes.
7. The P1 batch (3 documents: waiver mechanism, reviewer identity, audit-read grants) is drafted, approved, assigned, executed, and closed via the workforce runtime.
8. The P2 batch (3 documents: closure-operator runbook, canonical-interpreter policy, threat model) is drafted, approved, assigned, executed, and closed.
9. The P3 batch is either closed or explicitly deferred to v0.2 with a recorded deferral entry.
10. `CONSTITUTIONAL-CLOSURE-v0.1.md` is drafted, approved, assigned, executed, and closed; its content declares that closure is achieved, names the locked corpus, and states that document-expansion has terminated for v0.1.

When all ten conditions hold, **first constitutional closure is achieved**. The corpus is then locked for v0.1; further document expansion is forbidden until either (a) a runtime-pressured discovery surfaces a missing governance surface, in which case a single new work order is drafted to author the missing surface, or (b) the v0.2 → v0.3 transition is governed under `SPEC-EVOLUTION-POLICY-v0.1.md` with explicit per-document deltas.

### Stop Condition (verbatim)

> **The document-writing phase MUST terminate once the remaining governance surfaces are bounded and replayable. After closure, operational execution, hardening, replay validation, interoperability validation, sandbox enforcement, and release continuity become dominant priorities.**

The stop condition is mechanical, not aspirational. After `CONSTITUTIONAL-CLOSURE-v0.1.md` is closed:

- No new top-level governance document may be authored without a runtime-pressured discovery citation in the proposing work order.
- The work shifts to: closing the canonicalization-readiness audit's ten future enforcement items (`EN-FUT-1` through `EN-FUT-10`); cross-machine and cross-Python-version CI; cross-language harnesses; expanding the conformance vector suite; expanding the interop fixture set; running the stress suite on every hardening cycle; and producing v0.1.1 / v0.2.0 releases under `SPEC-EVOLUTION-POLICY-v0.1.md`.
- The operational dominant priorities are, in order: **execution → hardening → replay validation → interop validation → sandbox enforcement → release continuity**.

---

## 18. Final Assessment

| Required output | Value |
| --- | --- |
| **Artifact path** | `reports/DOC-COMPLETION-AUDIT-v0.1.md` |
| **Top-level document count** | 35 |
| **Final remaining-doc queue** | 10 candidates (3 P1 + 3 P2 + 3 P3 + 1 P0); see §15 |
| **Forbidden future-doc categories** | 10 forbidden categories enumerated in §14 |
| **Constitutional-closure assessment** | **Approaching.** The kernel + laws + operational + validator + release axes are saturated. The remaining bounded surface (≤10 documents) is convention-to-declaration locks plus operator discipline plus a closure declaration. No new constitutional law is required. No new roadmap is permitted. The corpus is one P1 batch + one P2 batch + one closure declaration away from first constitutional closure. |
| **Explicit stop condition** | Verbatim in §17: *"The document-writing phase MUST terminate once the remaining governance surfaces are bounded and replayable. After closure, operational execution, hardening, replay validation, interoperability validation, sandbox enforcement, and release continuity become dominant priorities."* |

**Assessment summary.** The 35-document top-level corpus is non-overlapping by explicit scope declaration, has low contradiction risk (and the active contradictions are between document and runtime reality, governed by `SPEC-EVOLUTION-POLICY-v0.1.md`, not between two documents), saturates the constitutional / operational / validator / release / roadmap / translation / pressure / supporting axes, and has eight identified missing surfaces — five of which are convention-to-declaration locks, three of which are larger but bounded specifications. The audit recommends a bounded queue of at most ten remaining documents and forbids ten categories of future documents. The constitutional-closure assessment is **approaching**: closure is one P1 batch + one P2 batch + one P0 declaration away, with the P3 batch optionally deferrable. No further document expansion is required beyond the bounded queue.

**This audit authorizes nothing.** Each candidate document in the bounded queue requires its own drafted, approved, and assigned governance work order. The audit's authority is observation and classification only.

---

**End of DOC-COMPLETION-AUDIT v0.1.**
