# CI Drift Hygiene Report — v0.2

**Work Order:** 021 — Untrack stale sandbox-profile files (closes WO019-RES-1)
**Timestamp (UTC):** 2026-05-11T19:00:00Z
**Overall Result:** **PASS**
**Authority:** This document is the evidence record that the 225 stale, non-deterministic sandbox-profile files have been removed from the git index, the .gitignore rule from WO 019 keeps them ignored on disk, and `make ci` + `make demo` + `make verify-drift` remain green.

---

## 1. Problem Closed

WO 019 left 225 already-tracked `reports/os_isolation_runtime/profiles/profile_*.sb` files in the repo. Their content embeds a per-process random mkdtemp path (`/T/osisol-fields-XXXXXXXX`, `/T/governed-run-XXXXXXXX`), so they are not deterministic evidence. The WO 019 `.gitignore` rule prevents *new* profiles from polluting `git status`, but does not untrack already-tracked files.

WO 021 closes WO019-RES-1 by removing the 225 stale entries from the index without deleting them from disk.

## 2. Action

```
git ls-files -z reports/os_isolation_runtime/profiles/ | xargs -0 git rm --cached
```

- 225 files staged as deletions in the index.
- Working tree unchanged: 285 .sb files remain on disk.
- All 285 are correctly ignored by `.gitignore:63` (added in WO 019).

The shell glob form `git rm --cached reports/os_isolation_runtime/profiles/*.sb` is **rejected** because the now-gitignored on-disk files would expand into the glob and fail the pathspec check. The `git ls-files | xargs` form operates strictly on the index, which is the correct boundary.

## 3. Verification

| Check | Result |
|---|---|
| `git ls-files reports/os_isolation_runtime/profiles/ \| wc -l` | 0 (was 225) |
| `find reports/os_isolation_runtime/profiles -type f -name '*.sb' \| wc -l` | 285 (on disk, unchanged) |
| `make ci PYTHON=.venv/bin/python` | PASS, exit 0, ~8.1s |
| `make demo PYTHON=.venv/bin/python` | OVERALL PASS; 3 fingerprints MATCH |
| `make verify-drift` | PASS — "OK: regenerated artifacts match committed state." |
| Frozen fingerprints | unchanged from WO 019 |

```
vectors_suite_sha256:   sha256:6168d2075931baa98bba763f9cd537142554aae7b26f19e3e93a60de2ee5bb0f
manifests_suite_sha256: sha256:74eaaa62271f23172232bda43ba3340543e66c46ba1e2f5e6da18d3447a6ba29
corpus_sha256:          sha256:c95685bff48c15abc313c462908b05ac309250bc660c2d802ae51af5a8038b09
```

## 4. Final Git Status (pre-commit)

```
225 D   reports/os_isolation_runtime/profiles/profile_*.sb
 2 ??   reports/repo_health/ci_drift_hygiene_v0.2.md (this file)
 2 ??   reports/repo_health/ci_drift_hygiene_v0.2.json
```

(WO 020 system-map files were committed separately before this work order.)

## 5. What Is Now Fixed

- WO019-RES-1 closed: zero stale profile files remain in the git index.
- The repo no longer carries 225 non-deterministic per-run artifacts as if they were canonical evidence.
- Combined with the WO 019 `.gitignore` rule, future CI runs cannot reintroduce profile drift.

## 6. What Remains Unresolved (carry-forward)

- **WO019-RES-2** — Default `PYTHON=python3` in Makefile resolves to system Python without project deps. Unchanged.
- **WO019-RES-3** — Rust verifier dead-code warnings. Unchanged.

## 7. Commands Run

```
git ls-files reports/os_isolation_runtime/profiles/ | wc -l         # 225 before, 0 after
git ls-files -z reports/os_isolation_runtime/profiles/ | xargs -0 git rm --cached
find reports/os_isolation_runtime/profiles -type f -name '*.sb' | wc -l  # 285 (unchanged)
make ci PYTHON=.venv/bin/python
make demo PYTHON=.venv/bin/python
make verify-drift
git status --short | awk '{print $1}' | sort | uniq -c
```
