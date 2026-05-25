# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

This file documents the governance protocol layer at
`~/Desktop/wiseorder-protocol` / `github.com/Wise-Est-Systems/wiseorder-protocol`.
The operational runtime layer (`wiseorder`) has its own changelog.

## [Unreleased]

### Documentation
- Infrastructure-grade `README.md` with current test counts (480, up from
  the historically-documented 113), CI badges, and the 13-section structure.
- `docs/REVIEWER_GUIDE.md` — consolidated 30-minute external-reviewer path
  pointing at the longer-form review packets in `docs/release/`.
- `docs/INTEGRATION.md` — protocol integration surface for external
  implementations.
- `CHANGELOG.md` (this file) replaces `git log --oneline` as the canonical
  release narrative.

### Stewardship
- CI status badges in the README (tests, conformance, verify-chain, lint).

## [0.1.0-pre] — 2026-05-25

This pre-release establishes the protocol as a CI-tested, crash-recoverable,
externally reviewable kernel. No tagged release yet (`v0.1.0` will follow
once branch protection is wired and a license is chosen).

### Added (Stewardship + CI)
- **GitHub Actions workflows**:
  - `tests.yml` — pytest matrix ubuntu/macos × py3.11/py3.12.
  - `lint.yml` — ruff check + ruff format (continue-on-error during baseline cleanup).
  - `verify-chain.yml` — standalone chain integrity; emits head hash to job summary.
  - (pre-existing) `conformance.yml` — full `make ci` (480 tests + conformance + interop + 3-language verifier parity).
- **Makefile targets**: `lint`, `lint-format`, `chain-verify`.
- **Crash-safety integration tests** (`tests/test_apply_transition_crash_safety.py`):
  7 synthetic crash-injection tests covering every window in the staging→save→finalize commit flow.
- **SIGKILL crash-recovery tests** (`tests/test_sigkill_recovery.py`): 3 real-process tests that
  spawn a subprocess, pause it at a known checkpoint, `os.kill(pid, SIGKILL)` it,
  and assert the parent's reconciliation brings the on-disk state to a consistent point.
- **Operator docs**: `docs/BRANCH_PROTECTION.md`, `docs/RELEASE_PROCESS.md`.

### Fixed (Integrity)
- **Crash-safe `apply_transition`** (memory.py, runtime.py, cli.py): two-phase
  commit pattern with staging file + atomic state save + rename. Replaces the
  v0.1 audit-then-state-save flow that could leave audit entries orphaned if
  the process died between the two writes. The fix introduces:
    - `AuditMemory.stage_entry(...)` — writes the entry to `<idx>.entry.json.staging`.
    - `AuditMemory.finalize_staged(entry)` — renames staging → final.
    - `AuditMemory.reconcile_pending(state.audit_head_sha256)` — startup recovery.
    - `AuditMemory.verify_state_consistency(state_audit_head)` — divergence detection.
    - `StateAuditDivergence` exception — raised on unrecoverable drift.
  CLI's `cmd_transition` runs `reconcile_pending` before `verify_chain` and
  before accepting work.
- **Strict transition schema validation** (`transitions.py`): `from_dict` rejects
  malformed `regime`, missing/empty `transition_id`, path-traversal characters,
  wrong types in `objects_removed` / `action` / `authorization`. Raises
  `TransitionSchemaError`.
- **Policy JSON schema validation** (`authorization.py`): `_load_policy` raises
  `PolicySchemaError` on known-kind bodies with malformed fields. Previously a
  typo in an allowlist entry silently denied all transitions.
- **`Policy` is now an `abc.ABC`** with `@abstractmethod evaluate`. Base class
  cannot be instantiated.
- **Typed exceptions in `TransformerProposer`** (`proposer_transformer.py`):
  replaces bare `except Exception` with `TimeoutError` / `ConnectionError` /
  `OSError` / `ValueError`. Records `_last_provider_error` for inspection.
  Provider failures no longer mask OOM or auth errors as "no candidates."

### Documented (Invariants)
- **TS-1 (timestamp precision)**: `chain.py` uses microsecond precision; the
  audit memory + conformance vectors use second precision. The divergence is
  intentional — chain filenames require sub-second uniqueness; audit/vectors
  require operator readability. Three sealed `.win` files encode microseconds;
  changing the format would change `consequence_proof` and break verifier
  parity. Documented in both module docstrings.

### Sealed
- **Chain triple 3 of 3**: `chain/2026-05-23T071437_482327Z-5964497c.win`.
  Seals WO-D5-SIZE-CAP + WO-CLASS-B-STATE-MACHINE + WO-IDENTITY-MODEL.
  Chain head is `5964497c48c877946e2c92d15e3116f5991c1d8a4c99dc7eadb477cec558dd81`.
- **v0.2.0 conformance vectors**: 6 new vectors under `vectors/v0.2.0/` covering
  Class B state-machine transitions, Class C signed attestation, and Class D
  preimage size cap (PREIMAGE_OVERSIZED).
- **Work orders**: WO-D5-SIZE-CAP, WO-CLASS-B-STATE-MACHINE, WO-IDENTITY-MODEL
  (intent docs that drove the v0.2.0 spec changes).

### Added (Tooling)
- **Triple sweep cryptanalysis tooling** (`tools/triple_sweep.py`, etc.) +
  6,072 evidence files under `reports/triple_sweep/` from the
  `20260512T025220Z`, `20260512T025422Z`, and `20260523T071041Z` sweep runs.

### Changed
- `requires-python` declared as `>=3.11` (was `>=3.12`). CI matrix tests both;
  code uses `from __future__ import annotations` everywhere.
- `init_db()` (in the runtime layer, not the protocol) replaced `create_all`
  with Alembic — but this is a runtime-layer change tracked in the runtime
  changelog.

### Pushed
- `github.com/Wise-Est-Systems/wiseorder-protocol` — private repo, every commit
  on `main` mirrored, every push triggers conformance + tests + lint + verify-chain.

### Verified
- All 480 tests pass + 9 xfailed. No regressions across the 3-language
  verifier parity (Python / Rust / Go).
- Chain status: **CHAIN_VALID** count=3 head=`5964497c...`.
- CI matrix all-green on the latest commit (ubuntu/macos × py3.11/py3.12 for
  tests; ubuntu/py3.12 for lint + verify-chain + conformance).

## [Earlier history — git log]

This changelog begins at the 2026-05-25 stewardship cut. Earlier work
(initial v0.1.0 spec, Rust + Go verifier tracks, governed-run pipeline,
III adoption, v0.2.0 spec lock) is documented in the git history; the
top-level work orders sealed into the chain (WO-018 etc.) reference those
changes by name.

See `docs/release/` for the per-version external-review packets, audit
scope documents, and third-party verifier briefs that predate this file.
