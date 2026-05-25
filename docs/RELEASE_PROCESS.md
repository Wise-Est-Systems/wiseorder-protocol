# RELEASE_PROCESS

A WiseOrder protocol release is a tag on `main` plus a sealed evidence
carrier (T7 drop). The tag is the thing third parties pull; the T7 drop
is the offline verifier. Both must agree.

## Versioning

`vMAJOR.MINOR.PATCH` follows semantic versioning with one protocol-specific rule:

- **MAJOR** bumps when chain genesis is re-sealed (i.e., a new chain root)
  or when conformance vectors change in a non-backwards-compatible way
  (`v0.2.0 → v1.0.0` would qualify; `v0.2.0 → v0.3.0` would not).
- **MINOR** bumps when new conformance vectors are added or when CLI
  surface area expands. Existing seals remain valid.
- **PATCH** bumps for bugfixes that do not change any byte in `chain/`,
  `vectors/`, or `schemas/`.

## Pre-release checklist (run in this exact order)

1. **Clean working tree**
   ```
   git status                    # must be clean
   git diff --stat               # must be empty
   ```
2. **All tests pass**
   ```
   make ci                       # full conformance + tests
   ```
3. **Chain still verifies**
   ```
   make chain-verify
   ```
   The printed head must match the head you intend to release. If it
   doesn't, investigate before tagging — the tag will become an external
   reference point.
4. **CI is green on `main`** (check the GitHub Actions tab — every workflow
   that ran on the latest commit must be green; status badges are not
   enough)
5. **Migration check** (runtime repo only — N/A here for protocol)
6. **External verifiers re-run cleanly**
   ```
   cd rust_verifier && cargo test
   cd ../go_verifier && go test ./...
   ```
   All three language verifiers must agree on the head hash.

## Tagging

Once the checklist is green:

```
git tag -s v0.2.1 -m "release v0.2.1: <one-line summary>"
git push --tags
```

The `-s` flag signs the tag with your GPG/SSH key (preferred; not yet
strictly required — see `BRANCH_PROTECTION.md`).

A signed tag is the canonical reference. Do NOT re-tag the same commit
with a different version, and do NOT move a tag once pushed.

## Evidence snapshot (T7 archival)

After the tag lands:

1. Mount T7 drive.
2. Create a new dated folder: `/Volumes/T7/<YYYY-MM-DD>/`.
3. Copy:
   - `intellagent_runtime/` (excluding `__pycache__/`)
   - `verify.sh`
   - all `.win` files from `chain/`
   - `SPEC_LOCK_v<current>.md`
4. Run `bash /Volumes/T7/<YYYY-MM-DD>/verify.sh` and confirm `CHAIN_VALID`
   with the same head hash that the tag references.
5. Leave any prior snapshots untouched. T7 history is append-only.

## Post-release verification

1. Pull the tag from a clean clone:
   ```
   git clone --branch v0.2.1 git@github.com:Wise-Est-Systems/wiseorder-protocol.git /tmp/check
   cd /tmp/check && make chain-verify
   ```
2. Confirm the same head hash that you tagged.
3. Run `bash /Volumes/T7/<YYYY-MM-DD>/verify.sh` from a different machine
   (or the same machine with the T7 drive only) and confirm it agrees.

If any step disagrees, the release is broken. Do not tag again; revoke
the release (delete the tag from GitHub Releases, leave the git tag in
place as a permanent reference to the broken state), then ship `v0.2.2`
with the fix.

## What CANNOT change after a release

- The git tag's commit SHA (signed; immutable).
- The `chain/genesis.win` file (the only one; never re-seal genesis after
  a public release).
- Any `.win` file already on a public T7 drop (those drops are evidence;
  changing them invalidates external verification claims).
- `SPEC_LOCK_v<X>.md` for any version `<X>` that has been released.

## Rollback strategy

There is no chain rollback. Once a triple is sealed, it stays. A "rollback"
takes the form of appending a new triple whose `statement` documents the
withdrawal of the prior change, with a fresh `consequence_proof` and a
`previous_action` pointer to the now-superseded triple. The withdrawn
triple remains on the chain.

This is by design: the chain is an audit trail, not a working branch.

## Release notes template

```
# v0.2.1 — <one-line summary>

## Chain state
- head: <full hash>
- count: <N>
- this release seals: <if applicable, the WO-... statements that landed>

## Code changes
- <bulleted list, one per significant commit>

## External verifier parity
- Python: PASS
- Rust:   PASS
- Go:     PASS

## Evidence
- T7 snapshot: /Volumes/T7/<YYYY-MM-DD>/
- GitHub tag:  v0.2.1
```
