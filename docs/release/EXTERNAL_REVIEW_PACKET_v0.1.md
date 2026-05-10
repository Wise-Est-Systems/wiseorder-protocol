# External Review Packet — WiseOrder Protocol v0.1.0

**Status:** Open for review.
**Adopted:** 2026-05-10
**Audience:** Independent reviewers, hostile security testers, prospective third-party implementers.
**Authority:** This packet is the entry point for someone outside Wise.Est Systems to inspect or implement against v0.1.0. It is concise and command-oriented. Where this document and the codebase disagree, **the codebase governs** — run the commands.

> **Do not trust claims in this document. Run the commands.**

---

## 1. What WiseOrder v0.1.0 Is

A protocol layer for classifying claims, assigning verification regimes, and producing auditable epistemic artifacts. It separates **reasoning, verification, authorization, and execution** at the protocol level.

- **`SPEC.md`** — kernel specification (4-class taxonomy A/B/C/D, invariants, status registry).
- **`SPEC_LOCK_v0.1.md`** — frozen reference semantics; defines version-increment rule.
- **`vectors/*.json`** — 33 conformance vectors (23 baseline + 10 adversarial). Vectors determine conformance; prose explains it.
- **`schemas/*.json`** — JSON schemas for vectors, manifests, fixtures, implementation declarations.
- **`canonicalization/corpus/*.json`** — 10 corpus entries used for byte-level canonicalization parity.

## 2. What It Is Not

- Not a model. The protocol contains no neural network.
- Not a network service. The reference runtime is single-host, no outbound HTTP.
- Not a claim of AGI, consciousness, autonomy, alignment, or universal trust.
- Not a moral system. WiseOrder governs the *form* a claim must take; substantive correctness lives elsewhere.
- Not a finished standard. v0.1.0 is locked but not externally validated.

## 3. What Is Implemented

| Surface | Status | Code |
|---|---|---|
| Class A / B / C / D verdict kernel | implemented | `intellagent_runtime/kernel.py` |
| RFC 8785 JCS canonicalization | implemented | `intellagent_runtime/canonical.py` |
| Commit-chain invariants (CC1–CC4) | implemented | `intellagent_runtime/kernel.py` |
| Refusal sealing | implemented | `intellagent_runtime/refusal.py` |
| Authorization gate (AG1–AG3) | implemented | `intellagent_runtime/authorization.py` |
| Pipeline runtime (proposer → review → executor) | implemented | `tools/pipeline_runtime.py` |
| OS isolation (macOS sandbox-exec) | partial (macOS only) | `tools/os_isolation_runtime.py` |
| 9-stage `make ci` gate | implemented | `Makefile` |
| First-party independent Rust verifier track | implemented | `rust_verifier/` |

Surface map authority: **`docs/audits/AUDIT_SCOPE_v0.1.md`**.

## 4. What Is First-Party Only

The following surfaces are authored, owned, and operated by Wise.Est Systems. Independence is logical (different language, different module surface) but not organizational:

- The reference Python verifier (`intellagent_runtime/`, `tools/`).
- The minimal independent Python verifier (`tools/minimal_verifier.py`).
- The Rust verifier track (`rust_verifier/`).
- The two declared implementations in `IMPLEMENTATIONS.md` (`Winstack`, `WISEATA`).
- All declarative conformance evidence under `reports/`.

> **The Rust verifier is classified `FIRST_PARTY_INDEPENDENT_IMPLEMENTATION_TRACK`. It is NOT third-party validation.**

## 5. What Is Not Yet Externally Validated

- No verifier authored by a non-first-party party reproduces the frozen fingerprints.
- No external audit has been performed; both declared implementations report `audit_status: NOT_AUDITED`.
- No production deployment, no adversarial third-party load, no operational scars.

> **Current external-validation status: NOT_COMPLETE.**

## 6. How To Reproduce CI

```bash
git clone <this repo>
cd wiseorder-protocol
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Required: Rust toolchain (cargo + rustc, 1.94+ tested) for the Rust track.
# Install via https://rustup.rs/ if not present.

make ci
```

`make ci` runs 10 stages. Expected: every stage `PASS`, final summary line printed, exit 0.

## 7. How To Reproduce Demo

```bash
make demo
```

Runs 6 stages and verifies the three frozen fingerprints MATCH byte-for-byte. Expected: `OVERALL: PASS`, exit 0.

## 8. How To Verify Vectors

```bash
make conformance        # Python reference verifier (33 vectors)
make minimal-verifier-check  # Python independent re-derivation (33 vectors)
cargo run --manifest-path rust_verifier/Cargo.toml -- verify-vectors  # Rust track
```

Each of the three must report `33 passed, 0 failed`. Cross-track agreement is part of v0.1.0's claim.

## 9. How To Verify Canonicalization

```bash
make canonicalization-check                                              # Python; 10 entries
cargo run --manifest-path rust_verifier/Cargo.toml -- verify-corpus      # Rust; 10 entries
```

Both must report 10 / 10 passing with `corpus_sha256` = `sha256:c95685bff48c15abc313c462908b05ac309250bc660c2d802ae51af5a8038b09`.

## 10. How To Verify Rust Cross-Language Track

```bash
cargo test --manifest-path rust_verifier/Cargo.toml
cargo run  --manifest-path rust_verifier/Cargo.toml -- fingerprints
make rust-verifier-check
```

Expected:
- `cargo test`: 26 / 26 passing.
- `fingerprints`: all three MATCH, `OVERALL: MATCH`, exit 0.
- `make rust-verifier-check` is wired into `make ci`; running it directly is a sanity check.

## 11. Frozen Fingerprints (v0.1.0 Lock)

```
vectors_suite_sha256:    sha256:6168d2075931baa98bba763f9cd537142554aae7b26f19e3e93a60de2ee5bb0f
manifests_suite_sha256:  sha256:74eaaa62271f23172232bda43ba3340543e66c46ba1e2f5e6da18d3447a6ba29
corpus_sha256:           sha256:c95685bff48c15abc313c462908b05ac309250bc660c2d802ae51af5a8038b09
```

Any reproduction of v0.1.0 must produce these exact values. A divergence is a non-conformance and must be reported per `docs/audits/AUDIT_SCOPE_v0.1.md §10`.

## 12. Known Limitations

1. No third-party verifier. Both declared implementations are first-party.
2. No external audit. Both implementations report `NOT_AUDITED`.
3. No production deployment. No external load.
4. Cross-machine replay verified only on macOS (`docs/release/CROSS_MACHINE_REPLAY_REPORT.md` Slot A). Slots B (Linux) and C (independent) are open.
5. OS isolation is macOS-only in v0.1.0.
6. Signing is out-of-band; v0.1.0 does not specify a signature mechanism.
7. ~30% of the spec corpus is backed by executing implementation; the rest is canon written ahead of code.
8. Vector suite is breadth-oriented (33 vectors), not exhaustive.

This list is published deliberately. A reviewer who restates one of these has not found a new finding.

## 13. Third-Party Verifier Requirements

See **`docs/release/THIRD_PARTY_VERIFIER_BRIEF_v0.1.md`** for full requirements. Summary:

- Author, own, and operate the verifier under a party *other than* Wise.Est Systems.
- Derive logic from `SPEC.md`, `SPEC_LOCK_v0.1.md`, `schemas/`, and the published vector + canonicalization corpora.
- MUST NOT import or translate the Python `intellagent_runtime` or copy the first-party verifier logic line-by-line.
- MUST reproduce all three frozen fingerprints byte-for-byte.
- MUST submit a reproducible build and a conformance report.

See also **`docs/release/IMPLEMENTATION_TRACKER.md`** for the implementer registry and submission flow.

## 14. What Counts As Successful External Validation

A reviewer or implementer has successfully validated v0.1.0 externally if **all** of the following hold:

1. The verifier is authored, owned, and operated by a party that is not Wise.Est Systems.
2. The verifier is built from the published sources of truth (spec, schemas, vectors, corpus) without importing or transliterating first-party Python code.
3. Running the verifier on a clean checkout produces:
   - `vectors_suite_sha256 = sha256:6168d2…1bb0f`
   - `manifests_suite_sha256 = sha256:74eaaa…ba29`
   - `corpus_sha256 = sha256:c95685…3b09`
   - 33 / 33 vector verdicts matching the published `expected_status` values
   - 10 / 10 canonicalization corpus entries matching the published digests
4. The verifier's source repository is public and its commit hash is recorded with the submission.
5. The submission is reproducible by a third party from the published commit.

## 15. What Does Not Count

- An implementation that imports or wraps `intellagent_runtime`.
- A line-by-line port of `tools/minimal_verifier.py` or `rust_verifier/` source.
- A claim of validation without published, reproducible evidence.
- A passing run that modifies vectors, schemas, the canonicalization corpus, or the frozen fingerprints.
- A first-party implementation, including by a contractor or anonymous author who is in fact employed or directed by Wise.Est Systems.

> **Run the commands. Verify the fingerprints. Read the spec. Don't take this document's word for any of it.**
