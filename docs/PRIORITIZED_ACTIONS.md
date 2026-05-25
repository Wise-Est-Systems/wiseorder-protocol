# PRIORITIZED_ACTIONS

Sorted by what most damages public credibility today (top of file) down to medium-term cleanup. Each action names a single repo, a concrete change, and a rough time estimate.

**Rules followed in this plan:** no repo is automatically deleted, no history is rewritten, no canonical repo is renamed casually. Every "delete" or "archive" recommendation is paired with a rescue/extraction path.

---

## Immediate (this week — < 1 hour total)

### 1. Fix `winstack-network` README header + badge URLs
- **Severity:** 🔴 BLOCKER
- **What:** Change `# Wise` → `# Winstack` in line 1 of `README.md`. Replace 4 occurrences of `Wise-Est-Systems/wise/actions` with `Wise-Est-Systems/winstack-network/actions`.
- **Why:** Every visitor to the public Winstack repo sees a header that doesn't match the URL and 4 broken badge images. Single highest-impact fix.
- **How:** `sed -i '' 's|Wise-Est-Systems/wise/actions|Wise-Est-Systems/winstack-network/actions|g' README.md` (after a backup), or one-pass manual edit. Commit + push.
- **Time:** 5 min.

### 2. Add `LICENSE` to `wiseorder-protocol` and `wiseorder`
- **Severity:** 🔴 BLOCKER for first public tag
- **What:** Choose a license (recommendation: **Apache-2.0** to match `wop`; alternative MIT to match Winstack). Add `LICENSE` file at repo root.
- **Why:** Both repos' `pyproject.toml` reference `"see LICENSE"` but the file doesn't exist. By default copyright applies; engineers will not adopt code they can't legally redistribute.
- **How:** `curl -o LICENSE https://raw.githubusercontent.com/apache/apache-licenses/main/LICENSE-2.0.txt` (or equivalent), edit copyright line, commit.
- **Time:** 5 min per repo.

### 3. Make `wisest-systems` private OR add a README that says what it is
- **Severity:** 🔴 BLOCKER (public-but-empty)
- **What:** Either flip visibility to private via `gh repo edit Wise-Est-Systems/wisest-systems --visibility private --accept-visibility-change-consequences`, OR add a 5-line `README.md` that explains "this is a static landing page for wise-est.systems."
- **Why:** A 3.3 MB public repo with no README sends an unambiguous signal of vapor. Either decision is fine; the current state is the only bad option.
- **Time:** 2 min.

### 4. Make `win-proof-feed` private
- **Severity:** 🔴 BLOCKER (10.7 MB, no README, opaque)
- **What:** `gh repo edit Wise-Est-Systems/win-proof-feed --visibility private`. Reversible.
- **Why:** Public-but-opaque-and-huge is the worst combination. Until someone can confirm what's inside and write a README, it should not be public.
- **Time:** 1 min.

### 5. Add `LICENSE` and clean up `wisernance` OR archive it
- **Severity:** 🔴 BLOCKER
- **What:** Two paths:
  - **Rescue:** Add LICENSE. `git rm -r .venv wisernance.egg-info wisernance_log.jsonl`. Add proper `.gitignore`. Commit.
  - **Archive:** Add a banner to README pointing at `wiseorder-protocol`. Click "Archive this repository" in GitHub Settings.
- **Why:** Committed `.venv/` is the kind of thing infrastructure engineers screenshot. Either fix it or stop showing it.
- **Time:** 15 min for rescue, 2 min for archive.

---

## Medium-term (next 2 weeks)

### 6. Archive the superseded `win` / `winstack` / `winstack-integrity` repos
- **Severity:** 🟡
- **What:** For each: add a `> ARCHIVED — see [winstack-network](https://github.com/Wise-Est-Systems/winstack-network)` line at the top of `README.md`. Commit. Then click "Archive this repository" in GitHub Settings.
- **Why:** Three stale-and-superseded "winstack"-family repos confuse first-time visitors. A clearly-banner-archived repo is fine; an unmarked stale repo is not.
- **Note:** Archive is reversible. Do NOT delete.
- **Time:** 5 min per repo.

### 7. Decide on `winstack-truthlock`
- **Severity:** 🟡 (has 2 stars — external interest)
- **What:** Choose one of:
  - (a) Revive: add `ROADMAP.md`, push commits, fix description (currently starts with "is a CLI...").
  - (b) Fold into `wiseorder-protocol` as `tools/truthlock/`, archive the standalone repo with a banner.
  - (c) Archive with banner pointing at the conceptual replacement (the protocol's authorization gate fills part of this).
- **Why:** Two external stars represent existing trust; throwing it away costs that trust. Keeping it stale also costs trust. Move one direction.
- **Time:** 30 min (deciding), 1–4 h (executing).

### 8. Pin canonical repos on the org page
- **Severity:** 🟡
- **What:** Pin (in this order): `wop`, `wiseorder-protocol`, `wiseorder`, `winstack-network`. GitHub allows 6 pinned repos.
- **Why:** Pinned repos are the first thing a drive-by visitor sees. The current pin order (if any) is unverified; making it deliberate signals which 4 repos are canonical.
- **How:** Org page → Customize your pins.
- **Time:** 2 min.

### 9. Add org bio + profile README
- **Severity:** 🟡
- **What:** Create a repo named `.github` under the org. Inside, add `profile/README.md` with org-level positioning (2–3 paragraphs, no hype). This renders as the org's bio above the pinned repos.
- **Suggested body:**
  > ## Wise.Est Systems
  >
  > Verifiable correctness and governance discipline for systems that change real things.
  >
  > Our public stack is four repos in three layers:
  > - [`wop`](../wop) — WISEATA / WiseDigest-3 primitives.
  > - [`wiseorder-protocol`](../wiseorder-protocol) — governance kernel + chain + conformance vectors (private during pre-v0.1.0).
  > - [`wiseorder`](../wiseorder) — operational runtime (private during pre-v0.1.0).
  > - [`winstack-network`](../winstack-network) — `.win` tags: files that prove themselves.
  >
  > Everything else under this org is either archive or pre-canonical experiment.
- **Time:** 10 min.

### 10. Push `demo-forge` to the org
- **Severity:** 🟡
- **What:** Create `gh repo create Wise-Est-Systems/demo-forge --private` (start private), push `~/Desktop/demo-forge`, then promote to public after one more demo lands.
- **Why:** The current local-only state means external reviewers cannot replay the SIGKILL demo. The repo itself is small, well-structured, and explains what it does.
- **Time:** 10 min.

---

## Pre-public-release (before v0.1.0 tags)

### 11. Enforce branch protection in the GitHub UI
- **Severity:** 🟡
- **What:** For `wiseorder-protocol` and `wiseorder`, configure branch protection per `docs/BRANCH_PROTECTION.md`: require status checks (tests, conformance/verify-chain for the protocol; tests, migration-check for the runtime), require linear history, block force pushes.
- **Why:** The policy document exists; the UI does not enforce it. Until that gap closes, the document is aspirational.
- **Time:** 10 min per repo.

### 12. Cut `v0.1.0` tags
- **Severity:** 🟡
- **What:** For each canonical repo: green CI on `main` → `git tag -s v0.1.0 -m "release v0.1.0: ..."` → `git push --tags` → write a `CHANGELOG.md` entry. T7 evidence snapshot for the protocol per `docs/RELEASE_PROCESS.md`.
- **Why:** Tagged releases are the unit of trust for external adopters. Working off `main` is a stronger signal of "I am the author" than "I am a user."
- **Time:** 30 min per repo (assuming CHANGELOG is already up to date).

### 13. Tighten lint baselines
- **Severity:** 🟢 (low priority but worth doing)
- **What:** In `lint.yml`, change `continue-on-error: true` → `false` on `ruff check` and `ruff format --check`. Will require one cleanup pass to bring the baseline to clean.
- **Why:** Lint that doesn't block merges isn't lint, it's reporting.
- **Time:** 1–2 h.

### 14. Sign release tags
- **Severity:** 🟢
- **What:** Configure GPG or SSH signing key. Use `git tag -s` (already documented in `docs/RELEASE_PROCESS.md`).
- **Why:** A signed tag is provenance for every external adopter who pulls the repo. The cost is one-time setup; the benefit is permanent.
- **Time:** 30 min one-time.

---

## What this plan does NOT propose

- **No public deletions.** Every `DELETE CANDIDATE` flag is paired with a "make private first" or "extract then archive" step.
- **No history rewrites.** The committed `.venv` in `wisernance` is a hygiene problem, but rewriting history risks worse outcomes; the cleaner path is "rescue the source, archive the repo, start clean."
- **No renaming of canonical repos.** `wop` → `wiseata` is mentioned as a *consideration*, not a recommendation; renaming a public repo breaks every bookmark and link in the wild.
- **No new products.** Every action is about clarity of existing repos, not creation of new ones.

## What "done" looks like

After step 1–5 (immediate / < 1 hour total):
- No broken badge URLs in any public repo's README.
- Every public, non-archived repo has a LICENSE.
- No public-but-empty repos.
- No committed `.venv` directories in any public repo.

After step 6–10 (medium-term / next 2 weeks):
- Org bio explains the stack in two paragraphs.
- Pinned repos match the canonical stack.
- Archived repos have banners pointing at their replacements.
- `demo-forge` is on the org (public or private).

After step 11–14 (pre-public-release):
- Branch protection enforced on `main` for both pre-v0.1.0 canonical repos.
- `v0.1.0` tags exist with signed-tag provenance.
- CI gates merges instead of just reporting.

The pre-public-release block is what a skeptical infrastructure engineer expects to see before considering production adoption. None of it is hard. All of it is on the operator side, not the code side.
