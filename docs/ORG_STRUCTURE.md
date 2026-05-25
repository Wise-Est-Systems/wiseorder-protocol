# ORG_STRUCTURE

The canonical structure of `github.com/Wise-Est-Systems` as of 2026-05-25. This document is the source of truth for which repos are first-class, which are archival, and how the public surface should be organized.

## The core stack

Five repositories, each with one clear responsibility. Everything else either supports these or is archive.

| layer | repo | visibility | status | one-line purpose |
|---|---|---|---|---|
| **1. Primitives** | [`wop`](https://github.com/Wise-Est-Systems/wop) | PUBLIC | CANONICAL · stable | WISEATA / WiseDigest-3 reference: the hash primitive and structural processing math the protocol depends on |
| **2. Protocol** | [`wiseorder-protocol`](https://github.com/Wise-Est-Systems/wiseorder-protocol) | private (pre-v0.1.0) | CANONICAL · active | Governance kernel + chain + conformance vectors + three-language verifiers + the `intellagent` CLI |
| **3. Runtime** | [`wiseorder`](https://github.com/Wise-Est-Systems/wiseorder) | private (pre-v0.1.0) | CANONICAL · active | Event-driven operational orchestration; one workflow (commit → summarize → draft → approve) |
| **4. Witness** | [`winstack-network`](https://github.com/Wise-Est-Systems/winstack-network) | PUBLIC | CANONICAL · active (with hygiene issues; see REPO_HYGIENE_REPORT.md) | Rust implementation of the `.win` tag system: files that prove themselves |
| **5. Demos** | (`demo-forge`, currently local-only) | not yet pushed | CANONICAL-INTENT · v0.1 | Reproducible operational demos generated from real subprocess captures |

These are the five repos a third party should ever need to know about. They map cleanly to four conceptual layers:

```
                  reasoning
                      ↓
              ┌───────────────────┐
              │   wop  (math)     │   ← WiseDigest-3, structural primitives
              └───────────────────┘
                      ↓
              ┌───────────────────┐
              │ wiseorder-protocol│   ← governance kernel, chain, conformance
              └───────────────────┘
                      ↓
              ┌───────────────────┐
              │     wiseorder     │   ← operational runtime (FastAPI + Postgres + Redis)
              └───────────────────┘
                      ↓
              ┌───────────────────┐
              │  winstack-network │   ← sibling product: file integrity / `.win` tags
              └───────────────────┘

   demo-forge (orthogonal) → captures real activity from any of the above
```

## Repository relationships

**`wop` → `wiseorder-protocol`**
The protocol's `intellagent_runtime/iii.py` is a **byte-identical mirror** of `wop/src/wise/digest_v3.py`. If WOP ships a new version of WiseDigest-3, the protocol updates in lockstep — never the other way. The protocol does NOT modify the WOP source.

**`wiseorder-protocol` → `wiseorder`**
The protocol is the kernel; the runtime is the operations layer above it. The runtime currently does NOT depend on the protocol at the import level — the two repos are independently runnable. They share architectural discipline and the same "fail closed" philosophy but not code.

**`winstack-network` ⟂ `wiseorder-protocol`**
Architectural siblings, not co-dependent. Both implement "drop the drive, prove the artifact" verification but with different artifact shapes (`.win` for Winstack, `.win` triples for the chain in WiseOrder — same extension, different schemas, source of mild confusion). They could converge later; today they don't.

**`demo-forge` → all of the above**
The pipeline captures real subprocess output from the canonical repos and packages it into demo artifacts (asciinema cast + MP4 + GIF + transcript + subtitles + X-thread). It is orthogonal — it produces demos *of* the other repos, it does not modify them.

## Trust boundaries

| boundary | who owns it |
|---|---|
| The chain on disk (`wiseorder-protocol/chain/*.win`) | The kernel. Tamper detection is at next read. |
| The WiseDigest-3 implementation | `wop`. Single source of truth; mirrored read-only into the protocol. |
| The `.win` tag format (Winstack) | `winstack-network`. Different schema from the WiseOrder chain's `.win` triples. |
| Operational state (Postgres rows, Redis lists) | `wiseorder` (the runtime). Idempotency keyed on `(repo, sha)`. |
| Public communication | The org account + `demo-forge` outputs. Nothing in any other repo speaks publicly. |

## Maturity matrix

| | wop | wiseorder-protocol | wiseorder | winstack-network | demo-forge |
|---|---|---|---|---|---|
| CI green | ✅ | ✅ | ✅ | ⚠ broken badge URLs to a non-existent `wise` repo | ❌ no CI yet |
| LICENSE | ✅ Apache-2.0 | ❌ missing (referenced in `pyproject.toml`) | ❌ missing (referenced in `pyproject.toml`) | ✅ MIT | ❌ missing |
| CHANGELOG | ⚠ release notes manifest only | ✅ Keep a Changelog 1.1.0 | ✅ Keep a Changelog 1.1.0 | ✅ present | ❌ none |
| Tagged release | `v0.1.0` / `v0.1.1` | none yet | none yet | none yet | none |
| External verifier | ✅ Python reference | ✅ Python / Rust / Go tracks (all first-party) | n/a | n/a | n/a |
| Documentation discipline | ✅ | ✅ (heavy: docs/release/, docs/specs/, etc.) | ✅ 13-section README + 7 ops docs | ✅ ROADMAP, SECURITY, CONTRIBUTING | ✅ 13-section README |
| Branch protection (UI) | unverified | aspirational (BRANCH_PROTECTION.md) | aspirational (BRANCH_PROTECTION.md) | unverified | none |
| Signed tags | none | aspirational | aspirational | none | none |

## Intended audiences per repo

| repo | who should read it first |
|---|---|
| `wop` | Cryptographic researchers evaluating WiseDigest-3. Open-source maintainers looking for a tested deterministic processing primitive. |
| `wiseorder-protocol` | Protocol engineers, regulatory-tech engineers, governance researchers, third-party verifier implementers. |
| `wiseorder` | Reliability engineers, platform engineers, infrastructure engineers operating LLM-driven pipelines. |
| `winstack-network` | Open-source maintainers, distribution maintainers, anyone needing portable file-integrity proofs. |
| `demo-forge` | Anyone evaluating any of the above and wanting a fast inspectable demo. |

## Release posture

| repo | release approach |
|---|---|
| `wop` | tagged releases at `v0.1.0`, `v0.1.1`; manifest + `.wiseproof` signatures committed |
| `wiseorder-protocol` | no public release yet. First tag (`v0.1.0`) gated on: (1) LICENSE chosen, (2) branch protection enforced, (3) external review packet accepted |
| `wiseorder` | no public release yet. First tag gated on same conditions + CHANGELOG entries |
| `winstack-network` | working on `main`; no tags yet despite mature code; release flow not yet documented |
| `demo-forge` | per-demo releases under `outputs/RELEASE_NNN_*/` with SHA-256 manifests; not yet pushed to remote |

## Non-canonical repos (under audit)

These repos exist under the org but are not part of the canonical stack. Each is classified in [`REPO_HYGIENE_REPORT.md`](REPO_HYGIENE_REPORT.md) with a concrete recommendation.

- `win` — pre-Winstack experiment; superseded by `winstack-network`
- `winstack` — second pre-Winstack experiment; superseded by `winstack-network`
- `winstack-integrity` — older integration of Winstack + Truthlock concepts; conceptually folded into `winstack-network`
- `winstack-truthlock` — separate "claim labeling / fabrication-pressure" governance experiment; may stand alone OR fold into `wiseorder-protocol` later
- `wisernance` — early AI-governance MVP; has hygiene problems (committed `.venv`)
- `wisest-systems` — 3 files (HTML + 2 PNGs); appears to be a static landing page, misleadingly named like a code repo
- `win-proof-feed` — 10.7 MB, no README, just `apps/api/` and `apps/web/`; status unclear

## What this document is NOT

- It is **not** authority to delete any repo. Per the audit rules: *DO NOT delete repos automatically.* Recommendations only; the human decides.
- It is **not** a marketing pitch. The "Intended audiences" column names actual engineering roles, not customer personas.
- It is **not** locked. As repos mature or get archived, this map updates. Today it reflects the state on 2026-05-25.

## How to update this document

1. A repo is added: append a row to the maturity matrix and place it in the layer that fits, or in "non-canonical" if it doesn't.
2. A repo is archived: move it from "core stack" to "non-canonical" with a one-line reason and a link to the GitHub archive.
3. A canonical repo is renamed: this document changes BEFORE the rename happens; any rename without updating this doc is a bug.
4. Maturity changes (e.g. tagged release lands): update the matrix row.
