# CI Drift Hygiene Report — v0.1

**Work Order:** 019 — CI Drift Hygiene Fix
**Timestamp (UTC):** 2026-05-11T00:00:00Z
**Overall Result:** **PASS**
**Authority:** This document is the evidence record that `make ci` no longer leaves the working tree dirty with generated sandbox-profile artifacts, that canonical evidence remains tracked, and that `make verify-drift` passes against committed state.

---

## 1. Drift Source Identified

Generated sandbox profiles materialized by the os_isolation_runtime layer accumulated under:

```
reports/os_isolation_runtime/profiles/profile_*.sb
```

Each `.sb` file is a macOS `sandbox-exec` profile. The filename is a content hash, but the content embeds a per-process random temp path issued by `mkdtemp(3)`, for example:

```
(allow file-write* (subpath "/private/var/folders/.../T/osisol-fields-kw0k_xk3"))
(allow file-write* (subpath "/private/var/folders/.../T/governed-run-72me9wql"))
```

Plain English: the random temp directory name changes on every process invocation, so the file content (and therefore the content-hash filename) differs every run. These files are **not** deterministic evidence; they are per-run runtime artifacts.

Observed accumulation across this work order's runs:

| Phase | Files on disk |
|---|---|
| Before WO 019 | 249 |
| After `make ci` (post-fix) | 261 |
| Delta (one CI + one demo run) | +12 |

## 2. Gitignore Change

Added to `.gitignore` (after the `reports/archive/` block, at lines 57–64):

```gitignore
# Generated sandbox profiles (WORK ORDER 019). The os_isolation_runtime
# materializes a sandbox-exec profile per invocation; the file name is a
# content hash, but the content embeds a per-process random temp path
# (e.g. /T/osisol-fields-XXXXXXXX, /T/governed-run-XXXXXXXX), so every
# CI run produces new files. They are not deterministic evidence and
# must not pollute drift checks.
reports/os_isolation_runtime/profiles/
```

## 3. Canonical Evidence Unaffected

`git check-ignore -v` confirms the following paths are **not** ignored by the new rule:

- `reports/conformance-report.json`
- `reports/conformance-summary.txt`
- `reports/canonical/README.md`
- `reports/repo_health/ci_drift_hygiene_v0.1.md` (this file)
- `interop/reports/interop-report.json`
- `canonicalization/golden/golden-digests.json`

Sample ignored profile match:

```
.gitignore:63:reports/os_isolation_runtime/profiles/	reports/os_isolation_runtime/profiles/profile_031e0943c9b82548.sb
```

## 4. Gate Results

| Gate | Result | Wall time | Evidence |
|---|---|---|---|
| `make ci PYTHON=.venv/bin/python` | PASS | ~8.7s | exit 0; all 18 stages green |
| `make demo PYTHON=.venv/bin/python` | PASS | ~0.4s | OVERALL PASS; 3 frozen fingerprints MATCH |
| `make verify-drift` | PASS | n/a (subseconds) | "OK: regenerated artifacts match committed state." |

Frozen fingerprints reproduced this run:

```
vectors_suite_sha256:   sha256:6168d2075931baa98bba763f9cd537142554aae7b26f19e3e93a60de2ee5bb0f
manifests_suite_sha256: sha256:74eaaa62271f23172232bda43ba3340543e66c46ba1e2f5e6da18d3447a6ba29
corpus_sha256:          sha256:c95685bff48c15abc313c462908b05ac309250bc660c2d802ae51af5a8038b09
```

## 5. Final Working Tree State

After running CI + demo + verify-drift with the gitignore fix in place, `git status --short` is:

```
 M .gitignore
```

No untracked profile artifacts. The fix holds under repeated CI invocation.

## 6. Known Remaining Hygiene Issues

These are **out of scope for WO 019** but flagged here for the next work order.

1. **225 already-tracked stale profile files.** `git ls-files reports/os_isolation_runtime/profiles/` returns 225 entries. These were committed before this work order and contain the same non-deterministic per-process temp paths described in §1. `.gitignore` does not untrack already-tracked files. A future work order should `git rm --cached reports/os_isolation_runtime/profiles/*.sb` to bring the repo into a consistent state.

2. **Default `PYTHON=python3` resolves to system Python without project deps.** On this machine, `python3` is homebrew 3.14.3 with no `pytest`/`jsonschema` installed. The project's `.venv/` has the pinned deps. A fresh-clone contributor running `make ci` fails at the `test` stage. Fix options: (a) Makefile auto-detects `.venv/bin/python` when present; (b) README pins the invocation.

3. **Rust verifier dead-code warnings.** `cargo` emits 3 warnings during every CI run (`canonical_sha256_hex`, `sha256_prefixed`, `Vector.{file, protocol_version}`). Non-blocking.

## 7. Commands Run

```
git status --short
find reports/os_isolation_runtime/profiles -type f | sort
git ls-files reports/os_isolation_runtime/profiles/ | wc -l
git check-ignore -v reports/os_isolation_runtime/profiles/*.sb
git check-ignore -v <canonical-evidence-paths>
make ci PYTHON=.venv/bin/python
make demo PYTHON=.venv/bin/python
make verify-drift
```

## 8. What Is Now Fixed

- CI no longer leaves untracked profile artifacts in the working tree.
- `make verify-drift` exits clean.
- Future CI runs cannot pollute drift checks via this path.

## 9. What Remains Unresolved

- 225 historical tracked profile files (see §6.1).
- System-python-vs-venv contributor friction (see §6.2).
- Rust verifier dead-code warnings (see §6.3).
