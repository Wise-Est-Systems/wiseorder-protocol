# Cross-Machine Replay Report — v0.1.0

**Status:** macOS slot captured. Linux and second-independent-machine slots are open.
**Adopted:** 2026-05-10
**Authority:** This report records the deterministic-replay verification across machines for WiseOrder Protocol v0.1.0. A protocol-wide replay claim is established only when all three slots match the canonical fingerprints byte-for-byte.

---

## 1. Replay Equality Requirement

For v0.1.0 to be considered cross-machine deterministic, every machine running `make conformance && make interop && make canonicalization-check` from a clean checkout MUST produce:

| Fingerprint | Required value |
|---|---|
| `vectors_suite_sha256` | `sha256:6168d2075931baa98bba763f9cd537142554aae7b26f19e3e93a60de2ee5bb0f` |
| `manifests_suite_sha256` | `sha256:74eaaa62271f23172232bda43ba3340543e66c46ba1e2f5e6da18d3447a6ba29` |
| `corpus_sha256` | `sha256:c95685bff48c15abc313c462908b05ac309250bc660c2d802ae51af5a8038b09` |

These three fingerprints are the v0.1.0 lock anchors. Any machine producing a different value under v0.1.0 has discovered a non-conformance — either in the local environment (e.g., line-ending normalization, locale, hash impl) or in the implementation under test.

---

## 2. Machine Slots

### 2.1 Slot A — macOS (CAPTURED)

| Field | Value |
|---|---|
| Status | **PASS** |
| Captured | 2026-05-10 |
| OS | Darwin 25.3.0 (`xnu-12377.91.3~2/RELEASE_ARM64_T8132`) |
| Architecture | arm64 |
| Python | 3.14.3 |
| `vectors_suite_sha256` | `sha256:6168d2075931baa98bba763f9cd537142554aae7b26f19e3e93a60de2ee5bb0f` |
| `manifests_suite_sha256` | `sha256:74eaaa62271f23172232bda43ba3340543e66c46ba1e2f5e6da18d3447a6ba29` |
| `corpus_sha256` | `sha256:c95685bff48c15abc313c462908b05ac309250bc660c2d802ae51af5a8038b09` |
| `conformance-report.json` SHA-256 | `7a94a458fa531582705018db612108813144133e762fd3995dc4405a1337e3a4` |
| `conformance-summary.txt` SHA-256 | `535642f782019d82fb14fa74f95a6915b60754391266d5c5be753e80ce1b357c` |
| `interop-report.json` SHA-256 | `657637271717cf3df29504474f0658a306802b72fa94894fb6ab95f4f6414f0e` |
| `fixture-manifest-report.json` SHA-256 | `ae2ea415f90ac5b011556149f3cc6b673a9a61720675360dffb1477101656d93` |

This slot is the canonical baseline. Other slots reproduce equality against these fingerprints.

### 2.2 Slot B — Linux (OPEN)

| Field | Value |
|---|---|
| Status | **OPEN** |
| Required OS | x86_64 or aarch64 Linux, distribution unspecified |
| Required Python | 3.11+ (Python that can satisfy `requirements.txt`) |
| Required result | All three fingerprints in §1 MUST match Slot A byte-for-byte |
| Filed by | (pending) |
| Date | (pending) |

This slot will close once any reviewer captures the same fingerprints from a Linux host. No code change is required to close this slot — only execution.

### 2.3 Slot C — Independent second machine (OPEN)

| Field | Value |
|---|---|
| Status | **OPEN** |
| Required ownership | Operated by a party other than the first-party project |
| Required result | All three fingerprints in §1 MUST match Slot A byte-for-byte |
| Filed by | (pending) |
| Date | (pending) |

This slot is the harder of the two open slots: it requires not only OS diversity but operator independence. It is intentionally separate from Slot B because Linux-on-the-author's-laptop does not satisfy the independence rule from `IMPLEMENTATION_TRACKER.md §1`.

---

## 3. Replay Procedure

A reviewer reproducing a slot SHOULD execute exactly:

```bash
git clone <this repo> wiseorder-protocol
cd wiseorder-protocol
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
make conformance
make interop
make canonicalization-check
```

After completion, the reviewer SHOULD compute and report:

```bash
python3 -c "import json; r=json.load(open('reports/conformance-report.json')); print(r['vectors_suite_sha256'])"
python3 -c "import json; r=json.load(open('interop/reports/interop-report.json')); print(r['manifests_suite_sha256'])"
shasum -a 256 reports/conformance-report.json reports/conformance-summary.txt interop/reports/interop-report.json interop/reports/fixture-manifest-report.json
```

The reviewer MUST then compare the captured values against Slot A in §2.1. A divergence is a non-conformance to be filed under `AUDIT_SCOPE_v0.1.md §10`.

---

## 4. Common Sources of Drift (and what each indicates)

| Drift symptom | Likely cause | Severity |
|---|---|---|
| `vectors_suite_sha256` differs by exactly one vector hash | Per-file canonicalization or line-ending normalization | high |
| `vectors_suite_sha256` differs across all vector hashes | JSON parser non-determinism or locale-dependent encoding | critical |
| `corpus_sha256` differs but `vectors_suite_sha256` matches | JCS implementation divergence between Python versions | critical |
| `manifests_suite_sha256` differs only | `interop/scripts/generate_fixture_manifest.py` non-determinism | high |
| `conformance-summary.txt` SHA differs but JSON matches | Whitespace / locale formatting in human-readable summary | low (SHA of summary is informational, not protocol) |
| All fingerprints differ | Wrong checkout, dirty working tree, or unsupported environment | informational |

A `low`-severity finding does not break the protocol claim but should still be filed.

---

## 5. What This Report Does and Does Not Establish

**Establishes (when Slots A, B, C all pass):**
- The first-party verifier is deterministic across operating systems.
- The first-party verifier is deterministic across operator boundaries.
- The vector suite, canonicalization corpus, and interop manifests are environment-portable under v0.1.0.

**Does not establish (regardless of slot status):**
- That an *independent implementation* reproduces the fingerprints. That is the subject of `IMPLEMENTATION_TRACKER.md`.
- That the verifier's verdicts are correct. That is the subject of `AUDIT_SCOPE_v0.1.md`.
- That the protocol is adopted, audited, or production-ready.

A complete v0.1.0 cross-machine claim requires this report's Slots A/B/C closed AND at least one independent implementation per `IMPLEMENTATION_TRACKER.md §2` reproducing these same fingerprints.

---

## 6. Slot Closure Log

This log records when each slot was filled. Editing this log requires the same v0.1.0 freeze rules as `SPEC_LOCK_v0.1.md` §4 (no semantic-breaking changes without version increment).

| Slot | Status | Date | Filed by | Notes |
|---|---|---|---|---|
| A (macOS) | CLOSED | 2026-05-10 | first-party | initial baseline, arm64, Python 3.14.3 |
| B (Linux) | OPEN | — | — | — |
| C (independent) | OPEN | — | — | — |
