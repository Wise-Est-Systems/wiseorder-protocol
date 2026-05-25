# REPO_HYGIENE_REPORT

Per-repo findings for every repository under `github.com/Wise-Est-Systems` as of 2026-05-25. Severity rating per item: 🔴 BLOCKER (visible-to-public defect) · 🟡 ISSUE (should fix before tagged release) · 🟢 OK · ⚪ N/A.

Classifications: **CANONICAL** · **ACTIVE EXPERIMENT** · **ARCHIVE CANDIDATE** · **PRIVATE CANDIDATE** · **DELETE CANDIDATE**.

---

## `wop` — CANONICAL · STABLE

| | |
|---|---|
| visibility | public |
| last push | 2026-05-04 |
| size | 185 KB |
| description | "WISEATA — deterministic structural processing of artifacts before they are trusted (proofs + expansions, local-first, no servers)" |
| license | Apache-2.0 ✅ |
| README | starts with `# WISEATA` (repo name `wop` ≠ project name `WISEATA` — intentional, documented in README) ✅ |
| CI | yes ✅ |
| stars | 1 |

**Findings:**
- 🟢 LICENSE present (Apache-2.0)
- 🟢 README clearly explains the project, has badges, points at the spec
- 🟢 Tagged release exists (manifest + `.wiseproof` for v0.1.0 and v0.1.1)
- 🟡 Repo name `wop` vs project name `WISEATA` is a naming friction. A drive-by reader sees `wop`, clicks, sees `WISEATA`. Not fatal, but a renaming to `wiseata` would close the gap permanently. (Renaming public repos breaks bookmarks; weigh accordingly.)
- 🟡 Description mentions "no servers" — true today but may not stay true as the system grows. Phrase as "local-first" only.

**Verdict:** CANONICAL · STABLE · keep as-is, consider repo rename to `wiseata` to match the project name.

---

## `wiseorder-protocol` — CANONICAL · ACTIVE

| | |
|---|---|
| visibility | private (pre-v0.1.0) |
| last push | 2026-05-25 |
| size | 2.8 MB |
| description | "WiseOrder governance protocol — kernel, chain, verifiers, conformance vectors" ✅ |
| license | ❌ missing (referenced in `pyproject.toml`) |
| README | infrastructure-grade 13-section ✅ |
| CI | 4 workflows ✅ |

**Findings:**
- 🔴 **Broken badge URL** — first badge pointed at `Wise-Est-Systems/systems` instead of `Wise-Est-Systems/wiseorder-protocol`. **Fixed in this audit pass.**
- 🔴 **No LICENSE file.** `pyproject.toml` references "see LICENSE" but the file doesn't exist. By default copyright law applies; this is not yet open source. Blocks the first public release.
- 🟡 **CHANGELOG entries are template-grade for v0.1.0-pre.** Granular per-fix attribution lives in commit messages. Acceptable for pre-release; should improve before v0.1.0 tag.
- 🟡 **Branch protection documented but not enforced** (`docs/BRANCH_PROTECTION.md` exists; GitHub UI side not configured).
- 🟢 480 tests pass · 9 xfailed · chain valid · all 4 CI workflows green on `main`.
- 🟢 Crash-safety proven by 3 SIGKILL tests + 7 synthetic crash-injection tests.

**Verdict:** CANONICAL · ACTIVE · address LICENSE before going public; everything else is normal pre-release work.

---

## `wiseorder` — CANONICAL · ACTIVE

| | |
|---|---|
| visibility | private (pre-v0.1.0) |
| last push | 2026-05-25 |
| size | 91 KB |
| description | "WiseOrder Runtime v0.1 — operational orchestration layer" ✅ |
| license | ❌ missing (referenced in `pyproject.toml`) |
| README | infrastructure-grade 13-section ✅ |
| CI | 3 workflows ✅ |

**Findings:**
- 🔴 **No LICENSE file.** Same as protocol. Blocks public release.
- 🟢 21 tests pass · 8 service-deferred (auto-skip cleanly when no Postgres+Redis).
- 🟢 CHANGELOG.md in Keep a Changelog 1.1.0 format.
- 🟢 7 ops docs in `docs/` (SYSTEM_MAP, FAILURE_MODEL, RUNTIME_INVARIANTS, RECOVERY_MODEL, OPERATOR_GUIDE, BRANCH_PROTECTION, RELEASE_PROCESS, REVIEWER_GUIDE, INTEGRATION).
- 🟢 CI matrix all green: ubuntu/macos × py3.11/py3.12.

**Verdict:** CANONICAL · ACTIVE · same blocker as protocol (LICENSE).

---

## `winstack-network` — CANONICAL · ACTIVE · HAS BROKEN README

| | |
|---|---|
| visibility | PUBLIC |
| last push | 2026-05-25 |
| size | 2.3 MB |
| description | "Deterministic artifact verification for sovereign local-first systems." ✅ |
| license | MIT ✅ |
| README | **starts with `# Wise`, has 4 badge URLs pointing at non-existent `Wise-Est-Systems/wise`** 🔴 |

**Findings:**
- 🔴 **README header is wrong**: says `# Wise` but the repo is `winstack-network`. A first-time visitor sees a header that doesn't match the URL bar, immediately questions the project's coherence.
- 🔴 **All four CI badges point at the wrong repo path** (`/wise/actions/workflows/...` instead of `/winstack-network/actions/workflows/...`). Every badge image shows "404" or a broken state.
- 🟢 Rust workspace with CHANGELOG, CONTRIBUTING, ROADMAP, SECURITY, clippy.toml, crates/, fuzz/, mutants.out/, gallery/, desktop/, deny.toml — this is a mature codebase.
- 🟢 MIT LICENSE present.
- 🟢 1 star — has minor external interest.
- 🟡 No tagged release despite the codebase being substantial. A `v0.1.0` tag and CHANGELOG cut would communicate maturity.

**Recommended fix (manual):** Update `README.md`: change `# Wise` to `# Winstack` and replace 4 badge URLs `Wise-Est-Systems/wise` → `Wise-Est-Systems/winstack-network`. About 10 keystrokes. Tested locally before pushing.

**Verdict:** CANONICAL · ACTIVE · the broken README is the single most damaging public-facing artifact in the entire org. Fix this before doing anything else.

---

## `win` — ARCHIVE CANDIDATE

| | |
|---|---|
| visibility | PUBLIC |
| last push | 2026-03-04 (3 months stale) |
| size | 10 KB |
| description | "W.I.N (Wise Independent Network) — portable cryptographic proof for file integrity. WIN packets make artifacts self-verifying." |
| license | MIT ✅ |
| README | `# W.I.N` — works as a stand-alone description |

**Findings:**
- 🟢 LICENSE present, README clear, code structure clean (src/, tests/, spec/, examples/).
- 🔴 **Functionally superseded by `winstack-network`.** Same conceptual primitive ("self-verifying file"). A new visitor sees `win` AND `winstack-network` AND `winstack` and cannot tell which one to use.
- 🟡 Stale 3 months — no commits, no issues, no PR activity.

**Verdict:** ARCHIVE CANDIDATE. Add a `> ARCHIVED — see [winstack-network](https://github.com/Wise-Est-Systems/winstack-network)` line at the top of the README, then click the GitHub "Archive this repository" button. Code stays readable; nobody is misled into thinking it's current.

---

## `winstack` — ARCHIVE CANDIDATE

| | |
|---|---|
| visibility | PUBLIC |
| last push | 2026-03-04 (3 months stale) |
| size | 7 KB |
| description | (none) ❌ |
| license | MIT ✅ |
| README | `# WIN Packet (Winstack) — v0.3.0` |

**Findings:**
- 🔴 **Empty description on GitHub.** A drive-by visitor cannot tell what this is without clicking.
- 🔴 **Name collision with the canonical `winstack-network`.** Worse: this repo IS the more-natural URL match for "winstack" — a visitor searching "wise est systems winstack" lands HERE, sees stale code, and bounces.
- 🟢 README is technically correct.

**Verdict:** ARCHIVE CANDIDATE with the same prefix-banner treatment. The name-collision issue is the bigger problem; consider whether the canonical repo should be renamed to claim the `winstack` slot (with a redirect from `winstack-network`).

---

## `win-proof-feed` — DELETE CANDIDATE

| | |
|---|---|
| visibility | PUBLIC |
| last push | 2026-02-28 (3 months stale) |
| size | **10.7 MB** 🔴 |
| description | (none) ❌ |
| license | ❌ missing |
| README | ❌ missing |
| top-level | only `apps/` directory containing `api/` and `web/` |

**Findings:**
- 🔴 **No README, no description, no LICENSE** — every public-facing trust signal is missing.
- 🔴 **10.7 MB on disk** with only `apps/api/` and `apps/web/` at top level — very likely contains committed binaries, node_modules, or build artifacts.
- 🔴 Public-but-opaque: a visitor sees the size, sees nothing inside they can read, assumes either abandoned vapor or accidentally-public private work.

**Verdict:** DELETE CANDIDATE — but follow the rules. Step 1: make private (immediate, reversible). Step 2: assess what's inside (likely a Vercel deployment or proof-of-concept apps). Step 3: extract anything worth keeping into a clearly-named canonical repo; archive or delete the rest.

---

## `winstack-integrity` — ARCHIVE CANDIDATE

| | |
|---|---|
| visibility | PUBLIC |
| last push | 2026-02-26 (3 months stale) |
| size | 14 KB |
| description | "Local-first dual verification CLI for deterministic file integrity (VERIFIED/TAMPERED) and governed execution (ALLOW/FLAG/HALT)" ✅ |
| license | MIT ✅ |
| README | `# Winstack Integrity + Truthlock` — describes two products at once |

**Findings:**
- 🟢 LICENSE present, README clear, CHANGELOG + CONTRIBUTING + .gitignore all present.
- 🔴 **Describes two products in one repo** (Winstack Integrity AND Truthlock) — making the boundary with `winstack-truthlock` unclear.
- 🟡 The "governed execution" framing here is conceptually adjacent to `wiseorder-protocol`'s authorization gate — should either fold into the protocol or remain a deliberate separate experiment.

**Verdict:** ARCHIVE CANDIDATE with a banner pointing at `winstack-network` (for the integrity half) and `winstack-truthlock` (for the truthlock half).

---

## `winstack-truthlock` — ACTIVE EXPERIMENT (DECIDE)

| | |
|---|---|
| visibility | PUBLIC |
| last push | 2026-02-22 (3 months stale) |
| size | 9 KB |
| description | "is a CLI that enforces structured, accountable AI output..." |
| license | MIT ✅ |
| README | `# winstack-truthlock` |
| stars | **2** — the only repo with > 1 star besides `wop` and `winstack-network` |

**Findings:**
- 🟢 LICENSE present, README explains the four commands, code is at `src/` with tests.
- 🟡 Description starts with "is a CLI..." — no project name, awkward.
- 🟡 The "TRUTHLOCK / ELOTBC / UNITAG" conceptual framework is distinct from the WiseOrder protocol — it's an AI-output linter, not a governance kernel.

**Verdict:** ACTIVE EXPERIMENT — but stale. **DECIDE**: either revive (add ROADMAP, fix the description, push commits), fold into `wiseorder-protocol` as a separate `tools/truthlock/` directory, or archive with a banner. The 2 stars suggest there's external interest worth not throwing away.

---

## `wisernance` — DELETE CANDIDATE (after rescue)

| | |
|---|---|
| visibility | PUBLIC |
| last push | 2026-02-15 (3 months stale) |
| size | **6.6 MB** 🔴 |
| description | "Wise.Est Systems — Infrastructure focused on verifiable correctness and governance discipline." |
| license | ❌ missing |
| README | `# Wisernance — minimal AI governance standard focused exclusively on pre-execution evaluation` |
| top-level | `.venv/`, `wisernance.egg-info/`, `wisernance_log.jsonl`, `run.sh` |

**Findings:**
- 🔴 **`.venv/` committed to the repo** — virtualenv bin/ and lib/ are in git. This is a hard hygiene failure.
- 🔴 **`wisernance.egg-info/` and `wisernance_log.jsonl`** also committed — both regenerable artifacts.
- 🔴 **No LICENSE.**
- 🔴 **6.6 MB of size** is almost entirely the committed venv. Cleaning would reduce to ~50 KB.
- 🟡 Description is org-level positioning, not project-level — describes "Wise.Est Systems" instead of "Wisernance".
- 🟡 Name overlaps semantically with `wiseorder` and `wiseorder-protocol` — all three are AI-governance projects. Pick one canonical "governance" repo.

**Verdict:** DELETE CANDIDATE (after rescue). The PRE_EXECUTION_MVP.md and `wisernance/` source code may be worth salvaging if Wisernance is a real ongoing concern; the .venv and binary junk are not. Recommended rescue path: extract `PRE_EXECUTION_MVP.md`, `examples/`, `wisernance/`, `tests/` into a fresh clean repo with proper `.gitignore`; archive this one. Or: archive entirely if Wisernance has been superseded by `wiseorder-protocol`.

---

## `wisest-systems` — PRIVATE CANDIDATE OR REPURPOSE

| | |
|---|---|
| visibility | PUBLIC |
| last push | 2026-04-27 |
| size | 3.3 MB |
| description | (none) ❌ |
| license | ❌ missing |
| README | ❌ missing |
| top-level | `index.html`, `seal-bg.png`, `seal.png` — three files |

**Findings:**
- 🔴 **Three files: an HTML page and two PNGs.** This is a static landing page disguised as a code repo. 3.3 MB suggests the PNGs are large or there's history bloat.
- 🔴 **Misleading name.** A visitor sees `wisest-systems` next to `wiseorder` and `wisernance` and `winstack` and assumes it's another code project. It isn't.
- 🔴 **Public-but-empty** is the worst possible signal — the visitor reads "no README means no project."

**Verdict:** PRIVATE CANDIDATE OR REPURPOSE. If this is meant to be a landing page, deploy it via GitHub Pages from a dedicated `.github`-style repo or a clearly-named `homepage` repo; this repo's name suggests something it isn't. If it's vestigial, make it private. Do not leave it public-and-empty.

---

## Summary table

| repo | classification | severity of issues |
|---|---|---|
| `wop` | CANONICAL · STABLE | 🟡 minor (naming friction) |
| `wiseorder-protocol` | CANONICAL · ACTIVE | 🔴 LICENSE missing |
| `wiseorder` | CANONICAL · ACTIVE | 🔴 LICENSE missing |
| `winstack-network` | CANONICAL · ACTIVE | 🔴 README header + 4 badge URLs broken |
| `win` | ARCHIVE CANDIDATE | superseded |
| `winstack` | ARCHIVE CANDIDATE | superseded · name collision |
| `winstack-integrity` | ARCHIVE CANDIDATE | merged conceptually elsewhere |
| `winstack-truthlock` | ACTIVE EXPERIMENT — DECIDE | stale but starred |
| `wisernance` | DELETE CANDIDATE (after rescue) | 🔴 committed venv |
| `wisest-systems` | PRIVATE CANDIDATE | 🔴 no README, misleading name |
| `win-proof-feed` | DELETE CANDIDATE | 🔴 no README, 10.7 MB, opaque |

**Counts:**
- 🔴 BLOCKER issues across the org: **9**
- 🟡 issues: **6**
- repos in good standing: **2** (`wop`, `winstack-network` post-README-fix)

**The biggest hits to public credibility, ranked:**
1. `winstack-network` README header `# Wise` + 4 broken badge URLs — this is the canonical Rust repo and the public face of Winstack; the README looks like it was renamed away from but never updated. Single highest-impact fix.
2. `wisest-systems` empty README + 3.3 MB — every visitor draws the wrong conclusion.
3. `win-proof-feed` no README + 10.7 MB — same.
4. `wisernance` committed venv — the kind of thing infrastructure engineers screenshot.
5. Three repos missing LICENSE — blocks anyone who wants to actually use the code.
