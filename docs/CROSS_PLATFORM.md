# CROSS_PLATFORM

How `wiseorder-protocol` behaves across operating systems and how to verify equivalence.

## What we test in CI

| job | OS | Python | what runs |
|---|---|---|---|
| `tests / pytest ubuntu-latest py3.11` | Ubuntu (GitHub-hosted) | 3.11 | full pytest |
| `tests / pytest ubuntu-latest py3.12` | Ubuntu | 3.12 | full pytest |
| `tests / pytest macos-latest py3.11` | macOS (GitHub-hosted, ARM64) | 3.11 | full pytest |
| `tests / pytest macos-latest py3.12` | macOS | 3.12 | full pytest |
| `lint / ruff` | Ubuntu | 3.12 | ruff check + format |
| `verify-chain / chain integrity` | Ubuntu | 3.12 | `verify_chain` over `chain/` |
| `WiseOrder Conformance` | Ubuntu | 3.12 | full `make ci` (pseudocode + tests + conformance + interop + Rust + Go verifiers) |

**The four-job tests matrix is the primary cross-platform proof.** Every push to `main` triggers all four; merges to `main` require all four green per `docs/BRANCH_PROTECTION.md`.

## What CI does NOT yet exercise

- **Windows.** Not in the matrix. The SIGKILL test in `tests/test_sigkill_recovery.py` explicitly skips on Windows (`pytest.mark.skipif(sys.platform == "win32")`) because Windows uses TerminateProcess instead of POSIX SIGKILL and the test's helper subprocess primitives differ. Other tests should pass on Windows but are not verified.
- **Linux distributions other than `ubuntu-latest`.** Alpine, Debian, RHEL, etc. are not in the matrix. The dependencies (Python stdlib + standard PyPI packages + the Rust + Go verifier binaries) have no known distro-specific issues, but "no known issues" is not "verified."
- **ARM Linux.** GitHub Actions doesn't run ARM Ubuntu by default. The macOS-latest jobs run on ARM (M-series); Ubuntu jobs run on x86_64. Cross-architecture parity between macOS-ARM64 and Ubuntu-x86_64 IS exercised.

## Replay invariants (what should be identical across platforms)

Given the same git commit and the same `make ci` invocation, every supported platform should produce:

| artifact | identical across platforms? | reason |
|---|---|---|
| `pytest` exit code | ✅ yes | unit tests are deterministic |
| `make chain-verify` output (status + head + count) | ✅ yes | re-derivation from on-disk bytes |
| `vectors_suite_sha256` | ✅ yes | canonical JSON over committed vectors |
| `manifests_suite_sha256` | ✅ yes | canonical JSON over committed fixtures |
| `corpus_sha256` | ✅ yes | canonical JSON over committed corpus |
| Rust verifier's fingerprint output | ✅ yes | Rust's canonical-JSON path uses the same algorithm |
| Go verifier's fingerprint output | ✅ yes | Go's canonical-JSON path uses the same algorithm |
| Audit-memory entry hash for a given transition + state | ✅ yes (under fixed clock) | `canonical.set_clock(...)` injects deterministic timestamps for tests |
| Process-level wall-clock timestamps in entry's `sealed_at` | ❌ varies per run | unavoidable; mitigated by clock injection in tests |
| `os.path.sep` in any logged path | ⚠ may vary (Windows backslash vs POSIX slash) | not load-bearing — paths are inspected, not hashed |

## Local cross-platform verification

If you have access to both macOS and Linux:

```bash
# on machine A
git clone https://github.com/Wise-Est-Systems/wiseorder-protocol.git /tmp/check_a
cd /tmp/check_a
make ci > /tmp/result_a.log 2>&1
make chain-verify > /tmp/chain_a.log 2>&1

# on machine B
git clone https://github.com/Wise-Est-Systems/wiseorder-protocol.git /tmp/check_b
cd /tmp/check_b
make ci > /tmp/result_b.log 2>&1
make chain-verify > /tmp/chain_b.log 2>&1

# compare invariants (strip timestamps + process IDs first)
diff <(grep -E "^(test_|FAIL|PASS|count=|head=)" /tmp/result_a.log) \
     <(grep -E "^(test_|FAIL|PASS|count=|head=)" /tmp/result_b.log)

# chain verification result must be byte-identical (no wall-clock dependency)
diff /tmp/chain_a.log /tmp/chain_b.log
```

The chain verification result should be **byte-identical** between machines: `verify_chain` is a pure function over committed bytes, with no clock or randomness in the verification path.

The pytest output will differ in test timings and process IDs but the pass/fail vector and the test names should match exactly.

## Known platform-specific gotchas

| gotcha | platform | mitigation |
|---|---|---|
| `os.rename` is atomic only on the same file system | all POSIX | `write_atomic` always uses a tempfile in the SAME directory as the target. If you put `intellagent_state/` and the tempfile dir on different filesystems via symlink, atomicity breaks. Don't do that. |
| Filename casing | macOS HFS+ / APFS (case-insensitive by default) | the chain uses lowercase hex hashes; no collision risk unless you also have a custom-cased file. |
| `signal.SIGKILL` semantics | Windows | not POSIX; SIGKILL is uncatchable on POSIX, TerminateProcess is the equivalent on Windows. SIGKILL tests skip on Windows. |
| asciinema `--command` headless mode metadata | macOS, Linux | cast files record `headless` metadata when run via `--command`. Recording is correct; reviewers should know what the metadata means. |
| `time.time()` precision | varies by OS | irrelevant for chain hashes (we use ISO-8601 strings with microsecond precision per chain.py); only affects log timestamps. |
| Locale collation in `sorted(glob(...))` | varies by `LC_COLLATE` | `intellagent_runtime/chain.py` and `memory.py` sort by `Path.name` which uses byte-order, not locale collation. No surprise. |

## The unavoidable nondeterminism

Documented honestly so reviewers don't expect more reproducibility than exists:

1. **Wall-clock timestamps in chain triples and audit entries.** Each transition's `proposed_at` is `utcnow_iso8601()` (microsecond-precision UTC). Two different sealings of "the same" transition produce different bytes. **Mitigation:** tests inject a deterministic clock via `canonical.set_clock(fn)`. Production sealings are unique-by-time by design.

2. **LLM provider output in `wiseorder` runtime demos.** The `engineering_summary` and `social_post` outputs depend on the LLM's stochastic decoding. Two runs with the same commit produce different copy. **Mitigation:** the *shape* of the workflow (counts of tasks, statuses, the workflow_completed log event) is invariant; the *content* is not.

3. **Process IDs, hostnames, and OS-level temp paths.** Logs contain these; they vary per run. **Mitigation:** none needed — these aren't compared in any verification path.

4. **Asciinema cast file timestamps in the header.** `timestamp` field records the recording start time. **Mitigation:** narrator output matches by content (regex), not by timestamp, so transcripts and SRT files regenerate deterministically.

5. **Floating-point in vector data.** None of the protocol's load-bearing math uses floats. **Mitigation:** none needed.

## What this document does NOT promise

- It does NOT promise the code works on Windows. We don't test it there.
- It does NOT promise the code works on every Linux distribution. We test `ubuntu-latest` (which tracks Ubuntu 24.04 LTS at time of writing).
- It does NOT promise WiseDigest-3 produces the same output across 32-bit and 64-bit architectures. The algorithm uses 64-bit integer math; sub-64-bit platforms are out of scope.
- It does NOT promise the same Python version on different OSes produces identical bytecode. We test against the public CPython releases via `actions/setup-python`; alternate Python implementations (PyPy, Jython, etc.) are untested.

What it does promise: **the four-job CI matrix is the single source of truth for "does this work cross-platform" until a tagged release explicitly extends that scope.** Anything outside that matrix is the user's responsibility to verify.
