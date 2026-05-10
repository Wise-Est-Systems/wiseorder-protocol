# Status Labeling Rule — Permanent Release Discipline

**Status:** Permanent rule. Applies to every release of WiseOrder Protocol from v0.1.0 onward.
**Adopted:** 2026-05-10
**Authority:** This rule is binding on the project. A release that violates it is non-conformant with project release policy and MUST be retracted or relabeled.

---

## 1. The Rule

Every public release of this project MUST preserve the following five labels and MUST NOT blur them:

1. **implemented** — code exists, executes, has tests passing under `make ci`.
2. **partially implemented** — code exists, fails to cover the full documented surface; gaps are explicitly enumerated.
3. **policy-only** — specification text exists; no executing code in this repository enforces the surface.
4. **future work** — declared deferred in spec or roadmap; not in scope for the current release.
5. **unsupported** — explicitly out of scope; no implementation intended.

Any public artifact (README, website, paper, presentation, post, talk) that describes a surface MUST attach one of these labels OR cite a document that does (e.g., `AUDIT_SCOPE_v0.1.md`).

---

## 2. What "Blurring" Means

Blurring is any of the following:

- Describing a policy-only surface as if it were implemented.
- Describing a partially implemented surface as if it were fully implemented.
- Omitting the label so that a reader cannot tell the difference.
- Using marketing-style "powered by" or "enabled by" language for surfaces that are policy-only.
- Mixing implemented and policy-only surfaces in a single bulleted list without separator.
- Citing a future-work surface as a current capability.

Each of these is a release-discipline violation regardless of intent.

---

## 3. Where the Rule Applies

The rule applies to:

- The top-level `README.md`.
- The protocol website (`site/`).
- Whitepapers and explanatory documents under this repository.
- Conformance reports and interop reports.
- Any external communication that names a project surface.
- Any presentation, talk, or post by project maintainers when speaking on behalf of the project.

The rule does not apply to:

- Private working notes.
- Draft documents marked `DRAFT`.
- Internal planning documents not published to `main`.

---

## 4. Default Labels

If a label is ambiguous, the more conservative label applies:

| If unsure between… | Use… |
|---|---|
| implemented vs partial | partial |
| partial vs policy-only | policy-only |
| policy-only vs future | policy-only |
| future vs unsupported | future |

The conservative direction is always toward less-claimed.

---

## 5. The Single Authoritative Surface Map

`AUDIT_SCOPE_v0.1.md` is the authoritative surface map for v0.1.0. Future versions MUST publish a corresponding `AUDIT_SCOPE_v<X.Y>.md` before the version is tagged.

When a public artifact and `AUDIT_SCOPE` disagree about a surface's label, `AUDIT_SCOPE` governs and the public artifact is incorrect.

---

## 6. Periodic Audit

Every release MUST include a check that:

1. No `implemented` claim references a surface absent from `AUDIT_SCOPE §2`.
2. No `partial` claim references a surface absent from `AUDIT_SCOPE §3`.
3. No `policy-only` claim references a surface absent from `AUDIT_SCOPE §4`.
4. The README, the website, and any whitepaper align with `AUDIT_SCOPE`.

A release that fails this check MUST NOT be tagged.

---

## 7. Why This Rule Exists

The fastest way to lose engineering credibility on a governance protocol is to overstate. A spec that promises what it cannot deliver is a spec that cannot be trusted with what it can deliver.

This rule is upstream of every other release decision. Specifications can be revised. Implementations can be extended. A reputation for honest labeling, once lost, takes a decade to rebuild.

---

## 8. Enforcement

A reviewer or auditor encountering a labeling violation SHOULD file it as a finding under `AUDIT_SCOPE_v0.1.md §10`. The project SHOULD treat such findings as severity-medium minimum, regardless of whether the underlying surface is correctly implemented.

---

## 9. Successor Versions

When a version is incremented, this rule does not change. The labels remain the same. Only the surface map (`AUDIT_SCOPE_v<X.Y>.md`) is rewritten to reflect the new release.

This rule itself MAY be amended only by adding stricter labels, never by removing or relaxing them.
