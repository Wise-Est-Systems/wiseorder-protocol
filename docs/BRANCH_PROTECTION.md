# BRANCH_PROTECTION

Operational policy for `main` on `wiseorder-protocol`. This document is the
source of truth; GitHub's branch-protection UI is to be configured to
match. **The doc precedes the enforcement** — if the UI is ever weaker
than what this file says, that is a bug to fix in the UI, not in the doc.

## Required (high-stakes — protocol semantics, chain artifacts, spec)

| rule | rationale |
|---|---|
| Required status checks before merge: `tests / pytest ubuntu-latest py3.12`, `verify-chain / chain integrity`, `WiseOrder Conformance / conformance` | Three independent gates: tests, chain integrity, conformance. Anything else is implicit. |
| Block force pushes to `main` | Force-push to `main` could rewrite history and silently invalidate `.win` filename references and external evidence carriers (T7 drops). |
| Require linear history | Merge commits hide intent in protocol changes. Use squash or rebase. |
| Require at least 1 review on PRs that touch: `SPEC.md`, `SPEC_LOCK_v0.*.md`, `vectors/**`, `schemas/**`, `canonicalization/**`, `intellagent_runtime/chain.py`, `intellagent_runtime/iii.py`, `chain/**.win` | These are the load-bearing surfaces. Self-merge is not appropriate here. |
| Dismiss stale reviews on new commits | If a reviewer approved one snapshot and the author pushed more, the approval no longer applies. |
| Require signed commits (recommended; not yet required) | Future: provenance of every chain seal back to a real identity. |

## Recommended (soft enforcement — policy, not gate)

| rule | rationale |
|---|---|
| Require signed tags for releases (`v*`) | Same provenance argument; cheaper than per-commit signing. |
| Use squash-merge by default for feature work; rebase-and-merge for hotfixes | Keeps `main` linear without losing intent. |
| Never `git push --force-with-lease origin main` | Even with lease, this is the wrong tool for `main`. Resolve conflicts in a feature branch. |
| Never commit `.win` files outside `chain/` | Stray `.win` files cause `verify_chain` to read garbage. The directory layout is part of the schema. |

## Forbidden

| rule | rationale |
|---|---|
| **NEVER** delete a `.win` file from `chain/` | Each triple is part of the linked history. Removing one breaks the linkage from the next one back to the genesis. |
| **NEVER** edit a `.win` file in place | The `consequence_proof` field is computed over the canonical body; any edit invalidates the seal and is detectable by `verify_chain`. To correct content, append a new triple referencing prior ones. |
| **NEVER** rebase `main` history that includes chain seals | Rewriting history that includes a `.win` seal would silently change the SHA referenced by external evidence carriers. The seal is a public-facing artifact even when the repo is private. |
| **NEVER** disable required status checks for an emergency merge | If CI is broken, the merge is broken. Fix CI first. |

## How to enable on GitHub (one-time setup)

```
Settings → Branches → Branch protection rules → Add rule
  Branch name pattern: main
  ☑ Require a pull request before merging
    ☑ Require approvals: 1
    ☑ Dismiss stale pull request approvals when new commits are pushed
  ☑ Require status checks to pass before merging
    ☑ Require branches to be up to date before merging
    Add: tests / pytest ubuntu-latest py3.12
    Add: verify-chain / chain integrity
    Add: WiseOrder Conformance / conformance
  ☑ Require linear history
  ☐ Allow force pushes  (must remain unchecked)
  ☐ Allow deletions     (must remain unchecked)
  ☑ Restrict who can push to matching branches: (you only)
```

## Operational invariants that this policy supports

- **The chain on disk in `main` always verifies as `CHAIN_VALID`.**
- **The chain head referenced by external evidence (T7 drops, third-party verifiers) is never silently rewritten.**
- **Every change to protocol semantics is observable in git history and reviewed.**
- **CI failure is a stop signal, not a suggestion.**
