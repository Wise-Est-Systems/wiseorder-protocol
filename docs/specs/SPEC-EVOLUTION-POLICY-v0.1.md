# SPEC EVOLUTION POLICY v0.1
**Controlled Evolution for Deterministic Cognition Protocols**

**Status:** Normative for the WiseOrder Protocol family beginning at v0.1.0.
**Scope:** `SPEC.md`, `STATUS-REGISTRY.md`, `CONFORMANCE.md`, `vectors/`, `interop/`, `canonicalization/`, and any artifact whose bytes are referenced by a published digest.
**Companions:** [`SPEC.md`](./SPEC.md), [`CONFORMANCE.md`](./CONFORMANCE.md), [`CROSS-LANGUAGE-CANONICALIZATION-v0.1.md`](./CROSS-LANGUAGE-CANONICALIZATION-v0.1.md), [`RELEASE-CHECKLIST-v0.1.md`](./RELEASE-CHECKLIST-v0.1.md), [`TOOLS.md`](./TOOLS.md).

**Core thesis:** Uncontrolled specification evolution destroys interoperability, replayability, and protocol legitimacy. A protocol that cannot bound its own change cannot be implemented twice.

---

## 1. Purpose

This document defines the rules under which WiseOrder Protocol and its dependent specifications (Intellagent runtime, canonicalization corpus, conformance vector suite, interoperability fixtures) are permitted to change.

It exists for one reason: to make every spec-level event mechanically detectable, classifiable, and reviewable, so that no implementer is ever surprised by a silent semantic mutation between two releases that share a name.

This policy is not a roadmap, not a feature plan, and not an opinion about direction. It is the change-control surface of the protocol.

---

## 2. Why Protocol Drift Is Dangerous

A deterministic cognition protocol stakes its legitimacy on three claims:

1. **Replayability.** The same inputs under the same version produce byte-identical audit memory.
2. **Interoperability.** Independent implementations of the same version produce byte-identical canonical artifacts and accept/reject the same vectors with the same status codes.
3. **Conformance comparability.** A `PASS` from implementation X under version V means the same thing as a `PASS` from implementation Y under version V.

Drift defeats all three. A vector whose meaning silently changes invalidates every prior `PASS`. A canonicalizer whose output changes for the same input invalidates every prior digest. An invariant whose semantics shift retroactively invalidates every prior refusal record.

Once any of these legitimacy claims is broken without being declared, the protocol stops being a protocol and becomes a moving codebase that happens to share a name with its predecessor.

---

## 3. Semantic Stability Philosophy

Three priorities, ordered:

1. **Semantic correctness** — the spec must describe the protocol it intends to describe.
2. **Replay continuity** — within a version line, replays must remain byte-identical.
3. **Backward compatibility** — older inputs should continue to be accepted under the same status codes when this can be done without violating (1) or (2).

**Backward compatibility is subordinate to semantic correctness.** When the two conflict, correctness wins and the change is classified as a CANON BREAK (§14, §26).

Stability does not mean stagnation. It means: every change is named, classified, and gated before it ships, and every implementer can tell from the version string alone what continuity guarantees they still hold.

---

## 4. What Counts As A Spec-Level Event

A change is a **spec-level event** if it does any of the following:

- changes the canonical bytes produced for any input the canonicalizer previously accepted;
- changes the semantics of any invariant in `SPEC.md` (A1–A3, CS1–CS3, B1–B3, C1–C4, D1–D5, CC1–CC4, AG1–AG3, §9 telemetry);
- changes the replay semantics of `intellagent_runtime/runtime.py` such that a previously byte-identical replay no longer holds;
- changes the refusal semantics of `intellagent_runtime/refusal.py` or `intellagent_runtime/kernel.py` such that a previously refused proposal would now be accepted, or a previously accepted one would now be refused, on identical inputs;
- changes the meaning, expected status, or class of any committed conformance vector under `vectors/`;
- changes any value listed in `STATUS-REGISTRY.md` (label, class membership, terminal/transient designation);
- changes any field name, field type, or field semantics in the schemas under `schemas/`;
- changes the format or fields of any record whose digest is published (`vectors_suite_sha256`, `manifests_suite_sha256`, `corpus_sha256`, `state_id`, `this_entry_sha256`, `manifest_sha256`).

Anything that satisfies one or more of these criteria is a spec-level event and is governed by this policy in full.

---

## 5. Implementation Change vs Protocol Change

Not every change is a spec-level event. The following are **implementation changes** and do not, by themselves, require a protocol version bump:

- refactors inside `intellagent_runtime/` that preserve every external behavior listed in §4;
- performance optimizations that produce byte-identical outputs;
- additional CLI subcommands that do not alter the meaning of existing ones;
- new tests that exercise behavior already mandated by `SPEC.md`;
- new tooling under `tools/` that does not alter committed reports or digests;
- documentation edits that do not change normative meaning.

The defining test is mechanical: after the change, run `make ci`. If `vectors_suite_sha256`, `manifests_suite_sha256`, `corpus_sha256`, and the cross-run audit hash all remain identical to their pre-change values, the change is an implementation change. If any of them changes, the change is a spec-level event regardless of intent.

**Intent does not classify a change. Bytes do.**

---

## 6. Runtime Change Categories

Within the runtime (`intellagent_runtime/`), changes fall into four categories, each with distinct release implications:

| Category | Examples | Triggers |
| --- | --- | --- |
| **Internal refactor** | rename a private helper; restructure a module; tighten typing | none — implementation change |
| **Surface addition** | new CLI subcommand; new optional kernel parameter with safe default; new `Provider` implementation | MINOR (§13) |
| **Surface modification** | rename a CLI subcommand; remove a documented field; change a default | MAJOR (§13) |
| **Semantic modification** | change what `kernel.evaluate` returns for an existing input; change canonical-byte output; change refusal triggers | CANON BREAK (§13, §14) |

The category is determined by the most semantically heavy change in the diff. A single CANON BREAK in a thousand-line diff makes the entire diff a CANON BREAK.

---

## 7. Canonicalization Change Policy

Canonicalization is the load-bearing surface of the protocol. Every digest depends on it. Its policy is the strictest in this document.

**Permitted without version bump:**

- comments, docstrings, and tests inside `intellagent_runtime/canonical.py` that do not alter byte output;
- additions to the golden corpus under `canonicalization/` — provided the existing 10 entries continue to verify byte-for-byte and `corpus_sha256` is recomputed as part of the change;
- new validation tooling that reads canonical bytes without producing new ones.

**Requires MINOR with explicit notice:**

- new canonicalization helper functions that are additive and unused by the kernel until a later release;
- new schema fields that are documented as optional and ignored by the canonicalizer when absent.

**Requires MAJOR:**

- changing which characters require escaping;
- changing whitespace, separator, or key-ordering rules in a way that produces identical bytes for currently-canonicalized inputs but differs in coverage (e.g. accepting inputs previously rejected);
- replacing the implementation backing `canonical_json_bytes` with a different library where the new library has been verified, against the full golden corpus, to produce byte-identical output for every existing entry.

**Requires CANON BREAK:**

- any change that produces non-identical bytes for any existing canonicalization-corpus entry;
- migration from the v0.1 sort-keys-plus-compact form to strict RFC 8785 JCS, unless and until JCS has been verified to produce byte-identical output across the entire committed corpus (per the v0.1 known-limitation entry on canonicalization);
- adoption of any non-Python canonicalizer whose output differs, on any corpus entry, from the committed `corpus_sha256`.

The canonicalization corpus under `canonicalization/` is the **single source of truth** for canonicalization correctness across the protocol family. A change that alters its bytes is a CANON BREAK by definition. A new-language canonicalizer that fails to reproduce its bytes is non-conformant by definition.

---

## 8. Vector Evolution Policy

The conformance vector suite under `vectors/` defines what each kernel class accepts and refuses. It is normative.

**Vectors must be regenerated** (and `vectors_suite_sha256` updated) when, and only when:

- a new vector is added to cover behavior already mandated by `SPEC.md` but previously untested;
- an existing vector's metadata (description, references, comments) is edited without altering its classification, expected status, or input bytes;
- a typo correction in a vector input that the spec already required to be invalid leaves the expected status unchanged;
- the schema under which vectors are validated changes in a way that does not alter the accept/refuse decision for any existing vector.

**Vectors must NOT be edited in place** when:

- the change would alter the expected status of an existing vector for the same input;
- the change would move an existing vector to a different class;
- the change would cause an implementation that previously passed the suite to now fail it (or vice versa).

Such changes are spec-level events. They require:

1. classification under §13 (typically MAJOR or CANON BREAK);
2. retirement of the existing vector to a versioned archive path before any replacement is added;
3. recomputation of `vectors_suite_sha256` with the change documented in the release notes;
4. drift detection (`make verify-drift`) green on the new bytes.

A vector's published `expected_status` is a contract with every implementer. Changing it without a version bump is forbidden.

---

## 9. Invariant Evolution Policy

The kernel invariants enumerated in `SPEC.md` (A1–A3, CS1–CS3, B1–B3, C1–C4, D1–D5, CC1–CC4, AG1–AG3, §9 telemetry) are the protocol's semantic core.

**Adding** an invariant is a MINOR change if and only if the new invariant rejects only inputs that no committed vector currently asserts to be accepted. If any existing accepted vector would be rejected by the new invariant, the change is a CANON BREAK.

**Tightening** an invariant (rejecting a strict subset of what it previously accepted) is permitted only if no committed vector currently exercises the now-rejected subset; otherwise the change is a CANON BREAK.

**Loosening** an invariant (accepting a strict superset of what it previously accepted) is a MAJOR change. It may not be applied retroactively to refusal records: the kernel must continue to refuse inputs that were refused under the previous version, unless the proposer re-issues them under the new version (§10).

**Removing** an invariant is always a CANON BREAK, regardless of test coverage.

**Renumbering** an invariant is forbidden. Once `B2` means a particular thing in any released version, no later version may reuse the symbol `B2` for a different meaning. Retired invariants are listed in `STATUS-REGISTRY.md` with a permanent note.

---

## 10. Replay Compatibility Policy

Replay is the binding contract that a fixed clock, fixed ID source, fixed seed, fixed provider, and fixed prompt produce byte-identical audit memory.

**Within a version line** (e.g. all v0.1.x): replay must be byte-identical. Any change that breaks this within a version line is a defect, not a release.

**Across MINOR boundaries** (e.g. v0.1.x → v0.2.0): replay of audit memory committed under the older line must continue to verify under the newer kernel without rewriting. The newer kernel must accept the older audit-chain bytes as-is and produce a `verify_chain` PASS. New audit entries written by the newer kernel may include additional fields that the older kernel would not produce; this is permitted.

**Across MAJOR boundaries** (e.g. v0.x → v1.0): replay of older audit memory is not guaranteed. The release notes must publish the explicit migration path or declare migration unsupported.

**Across CANON BREAK boundaries:** no replay continuity is guaranteed and none is implied.

A version that loses replay continuity within its own line is withdrawn, not patched. The published release is yanked from the registry and replaced under a new version number.

---

## 11. Cross-Version Compatibility

Cross-version interoperability claims must be precise:

- **Conformant under v0.1.0** means the implementation produces every committed `expected_status` for every vector in the v0.1.0 suite and reproduces `vectors_suite_sha256: sha256:37d3ec45ecca12d256b7df1c02ac0f0d1474f71b68510e9475fa449b8eb1331b`.
- **Interoperable under v0.1.0** means the implementation produces, for each fixture in the v0.1.0 interop suite, a manifest that reproduces `manifests_suite_sha256: sha256:74eaaa62271f23172232bda43ba3340543e66c46ba1e2f5e6da18d3447a6ba29`.
- **Canonicalization-conformant under v0.1.0** means the implementation reproduces `corpus_sha256: sha256:c95685bff48c15abc313c462908b05ac309250bc660c2d802ae51af5a8038b09` byte-for-byte across the 10-entry corpus.

An implementation may not claim conformance with a version it does not exactly reproduce. "Substantially compatible," "mostly conformant," and similar phrases are not protocol terms and have no normative meaning.

A multi-version implementation must declare the set of versions it claims, and pass each version's gates independently.

---

## 12. Conformance Stability Rules

The conformance report (`reports/conformance-report.json`) and interop report (`interop/reports/interop-report.json`) are byte-stable artifacts. They are committed to the repository.

**Drift detection is mandatory.** `make verify-drift` regenerates both reports and exits non-zero if the regenerated bytes differ from the committed bytes. CI must run `make verify-drift` on every change to anything under `vectors/`, `interop/`, `intellagent_runtime/`, `tools/`, or `schemas/`.

The published `vectors_suite_sha256` and `manifests_suite_sha256` are the authoritative fingerprints of the suite at a given commit. They are not advisory.

A conformance-report or interop-report change that is not accompanied by a corresponding suite-fingerprint change in the release notes is a defect.

---

## 13. Release Classification

Every release belongs to exactly one of four classes. The class is determined by the diff, not the author.

| Class | Version transition example | Permitted changes |
| --- | --- | --- |
| **PATCH** | v0.1.0 → v0.1.1 | implementation changes (§5); documentation edits with no normative impact; tooling changes that do not alter committed digests; no change to `SPEC.md` semantics; no change to vector or canonicalization bytes |
| **MINOR** | v0.1.0 → v0.2.0 | additive surfaces (new optional fields, new vectors covering already-mandated behavior, new optional invariants that reject only currently-uncovered inputs); replay continuity preserved per §10; no change to existing vector statuses; no change to canonical bytes for any existing input |
| **MAJOR** | v0.x → v1.0 | breaking surface or invariant changes that preserve interoperability continuity within the same canonicalization regime; vector regeneration permitted with archival of prior vectors; replay across the boundary not guaranteed but explicitly addressed |
| **CANON BREAK** | declared explicitly in the release notes | any change that alters canonical bytes for an existing input, alters an invariant retroactively, removes an invariant, or otherwise voids the interoperability claim of the prior version |

A release may not be classified below the highest-severity change in its diff. A diff containing one CANON BREAK and many PATCH-level edits is a CANON BREAK release.

---

## 14. Breaking Change Definition

A change is **breaking** if any of the following hold:

- after the change, an implementation that was conformant before the change is no longer conformant under the same version line;
- after the change, replay of audit memory committed under the prior version no longer verifies under the new version;
- after the change, a committed vector's `expected_status` is different;
- after the change, the canonicalizer produces non-identical bytes for any input previously accepted;
- after the change, a published digest (`vectors_suite_sha256`, `manifests_suite_sha256`, `corpus_sha256`) is different and the difference is not the sole, intended outcome of the change.

A breaking change forces at minimum MAJOR classification, and forces CANON BREAK if it touches canonicalization, invariant semantics, or refusal semantics.

**CANON BREAK = interoperability continuity no longer guaranteed.** Implementations conformant with the previous version cannot be assumed conformant with the new version. Replay across the boundary is not guaranteed. Vectors, fixtures, and the canonicalization corpus may all require regeneration. The release notes must explicitly state which prior digests are voided.

---

## 15. Non-Breaking Change Definition

A change is **non-breaking** if and only if all of the following hold:

- every existing vector retains its `expected_status` and class;
- every existing canonicalization-corpus entry retains its bytes;
- every existing audit-memory replay continues to produce identical bytes;
- every existing implementation that was conformant before the change remains conformant after it without modification;
- no published digest changes except as the deliberate, documented result of an additive edit (e.g. adding a new vector that necessarily updates `vectors_suite_sha256`).

A change that satisfies these conditions is a PATCH if the spec text is unchanged, and a MINOR if the spec text adds normative surface that no prior version mandated.

---

## 16. Experimental Surface Rules

Experimental surfaces (anything under `intellagent_runtime/` or `tools/` that the spec does not yet describe as normative) are governed by a relaxed but explicit rule:

- experimental surfaces must be clearly marked as such in their module docstring and in `IMPLEMENTATIONS.md`;
- experimental surfaces may change in any release class without invoking §14;
- experimental surfaces may not be referenced from `SPEC.md`, `STATUS-REGISTRY.md`, `CONFORMANCE.md`, or any committed vector or fixture;
- promotion of an experimental surface to normative status is, at minimum, a MINOR release and requires the surface to be added to `SPEC.md`, the schemas, and the conformance suite simultaneously.

An experimental surface that is referenced from a normative artifact is, by that act, no longer experimental — and any subsequent breaking change to it is governed by §14.

---

## 17. Deprecation Policy

Deprecation is a versioned process, not a notice.

To deprecate a normative surface:

1. In release N (MINOR or higher): add a `DEPRECATED` annotation to the surface in `SPEC.md`, `STATUS-REGISTRY.md`, or the relevant schema; document the replacement; add a migration note to the release notes.
2. The deprecated surface continues to function exactly as before for the entire span of the current MAJOR line.
3. Removal occurs no earlier than the next MAJOR release (release N+1 if N is MAJOR; otherwise the next MAJOR after N).
4. Removal of a deprecated surface is a MAJOR change at minimum, and a CANON BREAK if removal alters canonical bytes, replay, or vector statuses.

Surprise removal is forbidden. A surface that has not gone through step 1 and step 2 may not be removed in step 3.

---

## 18. Migration Requirements

Every MAJOR and CANON BREAK release must publish a migration document under `migrations/<from>-to-<to>.md` containing:

- the precise list of voided digests with their old and new values;
- the precise list of vectors that have moved, retired, or changed expected status;
- the precise list of invariants added, tightened, loosened, or removed;
- replay-continuity status across the boundary (one of: continuous, supported via re-issue, unsupported);
- a reproduction recipe (specific `make` targets, in order) that an implementer can run against the new release to verify they have correctly migrated.

A MAJOR or CANON BREAK release without a migration document is not a release. CI must block tag creation under those classes when the corresponding `migrations/` file is absent.

---

## 19. Semantic Drift Detection

The protocol detects semantic drift through three mechanical surfaces:

- **Suite fingerprints** — `vectors_suite_sha256`, `manifests_suite_sha256`, `corpus_sha256`. Any change in any of these without a corresponding release entry is drift.
- **Cross-run replay hash** — the audit-memory hash produced by running the canonical replay against a fixed clock, fixed seed, and fixed provider. Any change without a corresponding release entry is drift.
- **Drift gate** — `make verify-drift` regenerates the conformance and interop reports and fails if their bytes diverge from the committed bytes.

Drift detected by any of these three is treated as a release-blocking incident. The change that produced it must be classified, documented, and either reverted or escalated to its correct release class before any further work proceeds.

---

## 20. Documentation Drift Detection

Documentation drift — text in `SPEC.md`, `STATUS-REGISTRY.md`, or any companion document that no longer matches the runtime — is detected by:

- the no-pseudocode gate (`make no-pseudocode`), which forbids `TODO`, `NotImplemented`, bare `pass`, bare `...`, and `return ...` in Python code blocks across documentation;
- direct correspondence checks: every primitive named in `SPEC.md` must appear in `intellagent_runtime/`; every kernel class must have a verifier in `kernel.py`; every committed vector must reference its invariant by ID;
- cross-reference review during the §24 spec-review gate: every normative reference in a release's diff is checked against the file it points to.

Documentation that asserts a behavior the runtime does not implement, or describes a behavior the runtime no longer exhibits, is drift. It is treated as a defect at the severity of the underlying semantic mismatch.

---

## 21. Golden Artifact Stability

The following artifacts are **golden**: their bytes are pinned, and any change to them is a spec-level event subject to the rules in this document.

- the conformance vector suite under `vectors/` and its fingerprint `vectors_suite_sha256`;
- the interop fixture suite under `interop/fixtures/` and its fingerprint `manifests_suite_sha256`;
- the canonicalization golden corpus under `canonicalization/` and its fingerprint `corpus_sha256`;
- the conformance report `reports/conformance-report.json`;
- the interop report `interop/reports/interop-report.json`;
- the cross-run audit-memory hash recorded in `RELEASE-STATUS-v<version>.md`.

Each golden artifact has a single authoritative regeneration target (`make conformance`, `make interop`, `make canonicalization-check`). A regeneration that does not produce identical bytes is, by itself, evidence of a spec-level event.

---

## 22. Versioning Rules

Versions follow the form `MAJOR.MINOR.PATCH` with the optional suffixes `-rc.N` (release candidate) and `-canon.N` (CANON BREAK candidate, used during pre-release review of declared CANON BREAK changes).

- PATCH increments are PATCH releases (§13).
- MINOR increments reset PATCH to 0 and are MINOR releases (§13).
- MAJOR increments reset MINOR and PATCH to 0 and are MAJOR releases (§13).
- CANON BREAK is **always** at minimum a MAJOR increment, and is annotated in the release notes with the literal phrase `CANON BREAK`.
- A version number may not be reused. A withdrawn release is recorded as withdrawn; the version is not republished against different bytes.

The version of the WiseOrder Protocol is the version named in `SPEC.md`. The version of the Intellagent runtime is the version named in `pyproject.toml`. These two version numbers may diverge — but a runtime release must declare exactly which protocol version it implements, and CI must enforce that the declared protocol version's vector and canonicalization fingerprints reproduce.

---

## 23. CI Requirements For Spec Changes

Every change that touches any path in the following set must run the full CI gate before merge:

`SPEC.md`, `STATUS-REGISTRY.md`, `CONFORMANCE.md`, `IMPLEMENTATIONS.md`, `vectors/`, `interop/`, `canonicalization/`, `schemas/`, `intellagent_runtime/`, `tools/`, `reports/`, `Makefile`.

The full CI gate is:

- `make no-pseudocode` — clean
- `make test` — 100% pass, no skips, no xfails, no flakes
- `make conformance` — all vectors and implementations PASS, fingerprint matches release notes
- `make interop` — all fixtures PASS, fingerprint matches release notes
- `make canonicalization-check` — corpus verified, fingerprint matches release notes
- `make verify-drift` — committed reports and regenerated reports byte-identical
- a determinism cross-run: two clean runs of the canonical replay produce byte-identical audit-memory hashes

A change that fails any single gate may not be merged. A change that requires a fingerprint update must update the corresponding release notes in the same commit.

---

## 24. Required Review Gates

Spec-level events require explicit review beyond CI:

- **PATCH releases:** one reviewer; CI green; no spec-level event in the diff (verified by §19).
- **MINOR releases:** two reviewers; CI green; the change is classified in the release notes; release notes enumerate every added vector, schema field, and invariant with its `SPEC.md` reference.
- **MAJOR releases:** two reviewers plus an architecture-level review; CI green; migration document present (§18); release notes enumerate every voided digest and every vector retirement.
- **CANON BREAK releases:** the same as MAJOR, plus an explicit, written interoperability-impact statement enumerating every existing implementation and the work each must do to remain conformant; CANON BREAK is named in the release notes with the literal phrase.

A release whose review record does not match its class is invalid and must be re-tagged after the missing review is recorded.

---

## 25. Release Freeze Conditions

The protocol enters a **release freeze** when any of the following are true:

- an unresolved canonicalization divergence between two implementations of the same version (a non-Python implementation produces a different `corpus_sha256` than the committed one);
- an unresolved replay divergence within a version line;
- an unresolved vector dispute (an implementation refuses a vector the suite says is `SUPPORTED`, or accepts one the suite says is `INVALID`, and neither side has been demonstrated wrong);
- an unresolved invariant ambiguity in `SPEC.md` flagged by an implementer in writing.

Under release freeze:

- no MINOR, MAJOR, or CANON BREAK release may be tagged;
- PATCH releases are permitted only to the extent that they do not interact with the disputed surface;
- the freeze is recorded in the repository (a `FREEZE.md` at the root, or the equivalent registry entry) with the reason and the conditions for lift.

The freeze lifts when the divergence is resolved by a release that classifies it explicitly and updates the affected fingerprints.

---

## 26. What Invalidates Protocol Continuity

Protocol continuity — the property that two releases under the same version family describe the same protocol — is invalidated by:

- a canonicalization-byte change for any existing input;
- a retroactive change to invariant semantics;
- a removal of any invariant;
- a renumbering of any invariant or status code;
- a vector reinterpretation without version bump;
- a refusal-semantics change that flips the accept/refuse decision on a previously evaluated input;
- the publication of a new version under an existing version number.

Each of these is, by itself, sufficient to require a CANON BREAK release. None of them may occur silently.

---

## 27. Known Evolution Risks

These are the named, foreseeable failure modes this policy exists to bound. They are listed because they have been considered, not because they are predicted.

- **Replay instability across releases.** A runtime change that produces non-identical audit bytes for the same inputs across a version-line boundary that was supposed to be replay-continuous (§10).
- **Unresolved canonicalization divergence.** A non-Python canonicalizer produces output that does not reproduce `corpus_sha256` and the divergence is not classified before another release.
- **Invariant ambiguity.** Two reviewers reading `SPEC.md` produce different decisions about whether a given input satisfies an invariant.
- **Cross-language mismatch.** Two implementations of the same version disagree on the accept/refuse decision for a committed vector.
- **Authorization semantic leakage.** A change in `intellagent_runtime/authorization.py` causes the kernel to accept an action under a policy that previously refused it (or vice versa) without a corresponding spec-level event being declared.
- **Contradiction preservation instability.** A change that allows a `CONFLICTED` state to silently transition to `SUPPORTED` (or the reverse) on identical evidence — a direct violation of the B2 contract.

Each of these is detectable by the gates in §19 and §23, and each forces a CANON BREAK if it ships.

---

### What Would Force Intellagent v1.0?

A v1.0 release of the Intellagent runtime is forced — not chosen — when at least one of the following is true and cannot be resolved without a MAJOR-or-greater bump:

- replay continuity across the v0.x line is broken and cannot be restored without altering canonical bytes;
- canonicalization divergence between Python and at least one non-Python implementation cannot be resolved without changing the committed `corpus_sha256`;
- an invariant in `SPEC.md` is found to be ambiguous and the disambiguation changes the accept/refuse decision on at least one committed vector;
- the kernel's authorization gate is found to admit an action class that `SPEC.md` was understood to forbid, and closing the gate refuses inputs that committed vectors currently accept;
- the contradiction-preservation contract is found to be violable in practice and the fix changes the status flow for any committed vector;
- a non-additive structural change to the audit chain is required (e.g. a new mandatory field whose absence in older entries prevents `verify_chain` from succeeding under the new kernel).

A v1.0 release is the protocol declaring that the v0.x interoperability boundary is closed. It is a CANON BREAK by definition. It carries the migration document, the interop-impact statement, and the explicit voiding of the v0.x suite fingerprints.

It is not a marketing event. It is the moment after which v0.x conformance no longer implies v1.x conformance.

---

### What Is Not Allowed?

The following are forbidden under all classes, including PATCH:

- **Silent semantic mutation.** Any change that alters the accept/refuse decision for a previously evaluated input without a corresponding release-class declaration.
- **Undocumented replay drift.** Any change that breaks within-version replay continuity, regardless of whether the new bytes are themselves stable.
- **Hidden canonicalization changes.** Any change to `intellagent_runtime/canonical.py` (or its dependencies) that alters output bytes for any corpus entry without explicit CANON BREAK declaration.
- **Vector reinterpretation without version bump.** Any change to a vector's `expected_status`, class, or referenced invariant without classification and review at the appropriate level (§8, §13).
- **Implementation-specific truth behavior.** Any normative claim that depends on the implementation, the host, the operating system, the Python version, or any other environmental factor not specified in `SPEC.md` and the schemas.
- **Retroactive invariant change.** Any rewriting of an invariant that, applied to the prior version's vectors, would change their expected status.
- **Reuse of a published version number against different bytes.** A version, once tagged, is bound to its bytes for the lifetime of the protocol.

A change that does any of these is not merged. If it is merged in error, the release containing it is yanked and the corrected release is published under a new version number.

---

## 28. Non-Goals

This policy does not:

- prescribe a development cadence;
- define what features the protocol should adopt;
- legislate language choice for non-Python implementations beyond conformance to the canonicalization corpus;
- replace `SPEC.md` as the source of normative protocol semantics;
- replace `RELEASE-CHECKLIST-v0.1.md` as the operational gate definition for an individual release;
- govern any artifact outside the WiseOrder Protocol family (Winstack, WISEATA, and any future implementation are governed by their own release processes, with this policy applying only to their conformance claims against the protocol).

---

## 29. Final Law

A system that evolves faster than its replay guarantees is unstable.

Backward compatibility is subordinate to semantic correctness.

Every spec-level event is named, classified, and gated, or it is not a release.

Bytes do not lie. The bytes are the protocol.

---

*Normative for WiseOrder Protocol v0.1.0 and forward. Amendments to this policy are themselves spec-level events: changes to the rules in §13, §14, §15, §17, §18, §22, §23, §24, §25, or §26 are at minimum MAJOR releases of this document, and any amendment that loosens a rule retroactively is a CANON BREAK of the policy itself.*
