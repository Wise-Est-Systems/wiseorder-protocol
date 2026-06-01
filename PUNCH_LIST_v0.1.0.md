# PUNCH_LIST — v0.1.0 (target ship: 2026-06-15)

**Roadmap commitment:** "wiseorder-protocol v0.1.0 audit bundle published; conformance vector set frozen" — Sunday 2026-06-15.

**Status as of 2026-06-01:** ~80% complete. The full pre-release `RELEASE-STATUS-v0.1.md` (run 2026-05-06) reports green across all 7 hard gates. This punch list inventories what changed since that report and what must still happen in the 14 days before the ship date.

---

## Already green per RELEASE-STATUS-v0.1.md (2026-05-06)

| Gate / artifact | Latest captured state |
|---|---|
| `make no-pseudocode` | exit 0; 0 violations |
| `pytest tests/` | 135 / 135 passing in ~1.30s |
| `make conformance` | 23 / 23 vectors pass; 2 / 2 implementations pass |
| `make interop` | 3 / 3 fixtures pass |
| `make ci` | green |
| `make verify-drift` | no drift |
| `tools/demo_transformer_proposer.py` | overall PASS, exit 0 |
| `vectors_suite_sha256` | `sha256:37d3ec45ecca12d256b7df1c02ac0f0d1474f71b68510e9475fa449b8eb1331b` |
| `manifests_suite_sha256` | `sha256:74eaaa62271f23172232bda43ba3340543e66c46ba1e2f5e6da18d3447a6ba29` |
| `canonicalization corpus_sha256` | `sha256:c95685bff48c15abc313c462908b05ac309250bc660c2d802ae51af5a8038b09` |
| Determinism cross-run hash | byte-identical (`b71c7134…`) |

## Fresh re-run on current main (2026-06-01)

`make ci` re-executed against the head commit including the new `SECURITY.md`, `SPEC_TLDR.md`, `STRUCTURE.md`, `STACK_ROLE.md`, and `verify-stack` artifacts:

| Gate / artifact | Live result |
|---|---|
| `make ci` | exit 0 |
| Conformance vectors | **33 / 33** passed (up from 23 — vector set grew between May 6 and June 1) |
| Canonicalization golden corpus | 10 / 10 entries verified |
| Rust verifier | independent track green; agrees on all 3 frozen fingerprints |
| Go verifier | independent track green; agrees on all 3 frozen fingerprints |
| New CI lines now in the ci chain | governed-runtime core, v0.2.0 chain (III digest + .win chain primitives + tamper detection), minimal-verifier, replay-diff, binary-fixture, sandbox-escape |
| Drift | none |

**Implication:** the v0.1.0 audit bundle ships from a *strictly larger* green surface than the May 6 freeze report. The vector growth (23 → 33) is real coverage gain. Update RELEASE-STATUS-v0.1.md with these numbers before tagging.

---

## Changes since the 2026-05-06 status report

These were merged after the freeze report and need re-verification:

| Commit | Change | Risk |
|---|---|---|
| `6c1dd3a` | `STACK_ROLE.md` + `STRUCTURE.md` + `tools/verify_stack.py` + `verify-stack` CI workflow | LOW — new top-level files; should not affect drift on `reports/` or `vectors/` |
| `3c756ce` | `SECURITY.md` | LOW — new top-level file |
| `b87fda2` | `SPEC_TLDR.md` (non-normative reader's guide) | LOW — new file; does **not** modify SPEC.md |
| `bb1afa5` | `RELEASE_CHECKLIST` + `RELEASE_VERIFICATION` + `CROSS_PLATFORM` + `ADOPTION_REALITY` + `AUDIT_BUNDLE_v0.1` + `CONTRIBUTING` + issue templates | LOW — pre-existing release docs |

**Drift-check concern:** `make verify-drift` enforces `git diff --exit-code -- reports/ interop/`. None of the changes above touch `reports/` or `interop/`. Expected: still no drift.

---

## Required actions before 2026-06-15

| # | Action | Owner | Status |
|---|---|---|---|
| 1 | Re-run all 7 gates on current main (`make ci` + `make verify-drift` + `tools/demo_transformer_proposer.py`) | claude | IN PROGRESS (background run kicked off 2026-06-01) |
| 2 | Confirm `vectors_suite_sha256` and `manifests_suite_sha256` are unchanged from the May 6 values | claude | pending #1 |
| 3 | Update `RELEASE-STATUS-v0.1.md` with the fresh 2026-06-15 numbers (date of run, commit SHA, fingerprints) | claude | pending #1 |
| 4 | Add a `CHANGELOG.md` `[0.1.0]` section consolidating the `[Unreleased]` documentation work since the pre-release | claude | TODO |
| 5 | Compose the GitHub Release notes per `RELEASE-CHECKLIST-v0.1.md` §7.8 — links to RELEASE-STATUS, CHECKLIST, the five public demos, known-limitations | claude | TODO |
| 6 | **[HENRY]** Sign off per `RELEASE-CHECKLIST-v0.1.md` §10 — read the live numbers, attest the release has been reviewed, authorize the tag | HENRY | BLOCKED on actions #1–5 |
| 7 | `git tag v0.1.0 && git push --tags` on the signed-off commit | claude | BLOCKED on action #6 |
| 8 | Publish GitHub Release pointing at the tag + the release notes | claude | BLOCKED on action #7 |
| 9 | Update the org-page roadmap row from `open` to `hit (<commit-sha>)` | claude | BLOCKED on action #8 |
| 10 | Post-release: archive a snapshot of the canonical artifacts (manifest + reports + verifiers) into `audit_bundle_v0.1/` per `INDEX.md` schema, regenerate `artifact_manifest.sha256sum` | claude | BLOCKED on action #7 |

---

## Open questions for Henry

1. **Test count delta.** The latest status report claims 135 / 135 tests; the checklist §1 still says "113 passed as of v0.1 freeze." The 135 number is current; the 113 number is stale. Either we update the checklist to say 135, or we revert to the 113 baseline. Recommend update — the 22 extra tests are real coverage gains.
2. **`[Unreleased]` rollup.** The current `CHANGELOG.md` `[Unreleased]` section contains Documentation + Stewardship work that landed between the 2026-05-06 freeze and now (`REVIEWER_GUIDE`, `INTEGRATION`, README rewrite, status badges). Does that all roll into the `[0.1.0]` notes, or stay in `[Unreleased]` for v0.1.1?
3. **External-validation pre-coordination.** The roadmap commits to "first external conformance run by a non-Wise.Est party" on 2026-10-01. v0.1.0 ships before that — so the release notes for v0.1.0 should explicitly state "no external review yet; planned 2026-10-01." Confirm that framing.

---

## Risk items

| Risk | Mitigation |
|---|---|
| Test count drift between checklist and reality (113 vs 135) | Update checklist §1 to current numbers as part of this punch list. |
| New `STACK_ROLE.md` / `STRUCTURE.md` / `SECURITY.md` / `SPEC_TLDR.md` could affect `make verify-drift` if it accidentally widens its scope | The drift check explicitly scopes to `reports/` and `interop/`; new top-level files should not trigger it. Verify after re-run. |
| The "frozen vector set" commitment means no vector changes after 2026-06-15. Once tagged, vectors are immutable for v0.1.x. | Confirmed in `RELEASE-CHECKLIST-v0.1.md` §10. |
| Henry's day job may compress the sign-off window | Sign-off is operator-only (per checklist §10) and cannot be delegated. Build in a buffer day; aim for sign-off by 2026-06-13 to leave room for a tag-day slip. |

---

## 14-day plan

| Date | What ships |
|---|---|
| **2026-06-01** | Punch list (this file) committed + pushed. Fresh `make ci` run kicked off; results to be embedded in updated `RELEASE-STATUS-v0.1.md`. |
| **2026-06-03–05** | Actions 1–5 complete. Updated `RELEASE-STATUS-v0.1.md` committed. Release notes drafted. |
| **2026-06-08** | Dry run: tag a `v0.1.0-rc1` on a staging branch, generate the release packet, verify everything is byte-identical to expectation. Roll back the rc tag if anything fails. |
| **2026-06-13** | Henry sign-off (RELEASE-CHECKLIST §10). |
| **2026-06-14** | Final clean state. Working tree clean. CI green on the head commit. |
| **2026-06-15** | `git tag v0.1.0 && git push --tags`. GitHub Release published. Org-page roadmap row marked hit with commit SHA. First dated commitment closes. |

---

## What "hit" looks like on the org page

When this date closes, the row on `Wise-Est-Systems/.github/profile/README.md` changes from:

> `| 2026-06-15 | wiseorder-protocol v0.1.0 audit bundle published; conformance vector set frozen | open |`

to:

> `| 2026-06-15 | wiseorder-protocol v0.1.0 audit bundle published; conformance vector set frozen | hit (<commit-sha>) |`

That edit, atomically with publishing the tag, is what closes the first roadmap commitment. The past becomes a credential.
