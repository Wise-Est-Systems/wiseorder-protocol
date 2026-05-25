# RELEASE_CHECKLIST

What must be true before a `v0.x.y` tag lands. Each step is binary: pass or fail. No "looks good enough."

This document is the source of truth; `docs/RELEASE_PROCESS.md` is the narrative explanation.

## Pre-tag gate (every release)

- [ ] Clean working tree on `main`: `git status` returns "nothing to commit, working tree clean".
- [ ] `git diff origin/main` is empty: local matches remote exactly.
- [ ] Latest CI run on `main` is green for every workflow:
    - `tests` (matrix: ubuntu/macos × py3.11/py3.12)
    - `conformance` (heavy `make ci`: pseudocode + tests + conformance + interop + verifiers)
    - `verify-chain` (chain integrity standalone)
    - `lint` (informational; non-blocking until baseline clean)
- [ ] `make chain-verify` locally prints `CHAIN_VALID count=N head=<hash>`.
- [ ] `make test` locally prints `N passed` with no failures.
- [ ] Three-language verifier parity: `make rust-verifier-check` AND `make go-verifier-check` AND `make minimal-verifier-check` all pass.
- [ ] Conformance vector counts match `CONFORMANCE.md`.
- [ ] `CHANGELOG.md` has a fully-fleshed-out section for the new version. `[Unreleased]` is renamed to `[<version>] — <YYYY-MM-DD>`. Categories: Added / Changed / Fixed / Security / Removed / Deprecated.
- [ ] `pyproject.toml` `version` field matches the tag.
- [ ] `Cargo.toml` `version` field in `rust_verifier/` matches the tag (if Rust verifier ships with this release).
- [ ] `LICENSE` file exists at repo root (Apache-2.0 for protocol + runtime; MIT for winstack-network).
- [ ] No unstaged or untracked files outside `.gitignore`.

## Frozen-fingerprint gate (every release that touches the chain or vectors)

- [ ] `make conformance` produces a `reports/conformance-report.json` whose `vectors_suite_sha256` matches the value published in `README.md`'s frozen-fingerprint table.
- [ ] `make interop` produces a `manifests_suite_sha256` that matches.
- [ ] `make canonicalization-check` produces a `corpus_sha256` that matches.
- [ ] If any fingerprint changed: the change is intentional, documented in CHANGELOG, and reflected in `SPEC_LOCK_v<X>.md`.

## Crash-safety gate (every release that touches `apply_transition` or its dependencies)

- [ ] `pytest tests/test_apply_transition_crash_safety.py` → 7 passed.
- [ ] `pytest tests/test_sigkill_recovery.py` → 3 passed.
- [ ] Chain on disk pre- and post-tests verifies `CHAIN_VALID`.

## Tag step

```bash
# annotated tag with a real summary in the message body
git tag -a v0.1.0 -m "release v0.1.0: <one-line summary>" -m "

Full changelog: see CHANGELOG.md
"

# if signing keys are configured (see RELEASE_VERIFICATION.md):
git tag -s v0.1.0 -m "..."

git push --tags
```

Do NOT use lightweight tags (`git tag v0.1.0` with no `-a` or `-s`). They are unsigned, unanchored to a message body, and treated by GitHub as decoration only.

## Post-tag steps (within 1 hour of tagging)

- [ ] GitHub Releases entry created from the tag; release notes match the CHANGELOG entry.
- [ ] Release artifacts attached to the GitHub Release: source tarball auto-generated; if applicable, signed manifest + `.wiseproof`.
- [ ] T7 evidence snapshot recut: `/Volumes/T7/<YYYY-MM-DD>/` contains the package + verify.sh + the chain triples at the version's head.
- [ ] `bash /Volumes/T7/<YYYY-MM-DD>/verify.sh` returns the same head hash as the tag.
- [ ] If three-language verifier parity is part of the release: re-run all three from a fresh clone of the tagged commit. All three must report the same `vectors_suite_sha256`.

## Rollback procedure

If a defect is discovered after tagging:

1. **Do NOT** move the tag. Tags are immutable references. Moving a published tag breaks every external bookmark and is treated as a hostile act by mirrors.
2. **Do NOT** delete the tag from GitHub Releases. Mark the release as "draft" or add a deprecation note, but the tag itself stays.
3. **Do** ship a follow-up patch release (`v0.1.1`) with the fix. The CHANGELOG entry for the patch documents the defect and references the broken tag.
4. **For chain-level errors:** append a new chain triple whose `statement` documents the withdrawal of the prior position. The chain is an audit trail; corrections are by addition, not deletion.

## What this checklist does NOT cover

- Pre-release marketing copy (out of scope).
- External-validation status changes (governed separately by `docs/release/THIRD_PARTY_VERIFIER_BRIEF_v0.1.md`).
- Major version bumps (`v1.0.0` and beyond) — these need a stricter checklist that includes spec re-locking, conformance vector freezing, and an external review packet acceptance.

## Reproducibility verification (a reviewer's gate)

A reviewer attempting to reproduce the release:

```bash
git clone --branch v0.1.0 git@github.com:Wise-Est-Systems/wiseorder-protocol.git /tmp/check
cd /tmp/check
make ci
make chain-verify
```

Expected outputs are documented in CHANGELOG.md per release. Divergence is a non-conformance.
