# Review Quickstart — WiseOrder Protocol v0.1.0

Practical commands for a reviewer to confirm the repo from a cold clone. No prose. If you want context, see `EXTERNAL_REVIEW_PACKET_v0.1.md`.

## 1. Install dependencies

```bash
# Python ≥ 3.11
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Rust toolchain ≥ 1.94 (cargo + rustc).
# Install via https://rustup.rs if not present.
rustc --version    # confirm; tested with 1.94.1
```

## 2. Run the full CI gate

```bash
make ci
```

**Expected:** every stage `PASS`, final summary line printed, exit 0. Stages: `no-pseudocode → test → conformance → interop → canonicalization-check → minimal-verifier-check → replay-diff-check → binary-fixture-check → sandbox-escape-check → rust-verifier-check`.

## 3. Run the demo

```bash
make demo
```

**Expected output (tail):**

```
vectors_suite_sha256    expected: sha256:6168d2075931baa98bba763f9cd537142554aae7b26f19e3e93a60de2ee5bb0f
                        observed: sha256:6168d2075931baa98bba763f9cd537142554aae7b26f19e3e93a60de2ee5bb0f
                        MATCH
manifests_suite_sha256  expected: sha256:74eaaa62271f23172232bda43ba3340543e66c46ba1e2f5e6da18d3447a6ba29
                        observed: sha256:74eaaa62271f23172232bda43ba3340543e66c46ba1e2f5e6da18d3447a6ba29
                        MATCH
corpus_sha256           expected: sha256:c95685bff48c15abc313c462908b05ac309250bc660c2d802ae51af5a8038b09
                        observed: sha256:c95685bff48c15abc313c462908b05ac309250bc660c2d802ae51af5a8038b09
                        MATCH

OVERALL: PASS
```

If any line says `DIVERGENT`, the repo or your environment is wrong.

## 4. Rust verifier commands

```bash
cargo test --manifest-path rust_verifier/Cargo.toml
# expect: 26 passed; 0 failed

cargo run --manifest-path rust_verifier/Cargo.toml -- verify-vectors
# expect: Summary: 33 vectors, 33 passed, 0 failed

cargo run --manifest-path rust_verifier/Cargo.toml -- verify-corpus
# expect: Summary: 10 corpus entries, 10 passed, 0 failed

cargo run --manifest-path rust_verifier/Cargo.toml -- fingerprints
# expect: OVERALL: MATCH

make rust-verifier-check          # same as the three commands above, condensed
make rust-verifier-fingerprints   # fingerprint subset only
```

## 5. Direct conformance probes

```bash
make conformance               # Python reference verifier; reports/conformance-report.json
make interop                   # interop fixtures
make canonicalization-check    # 10 corpus entries
make minimal-verifier-check    # Python independent re-derivation
make pipeline-check            # governed pipeline self-check (8 fixtures)
make sandbox-escape-check      # sandbox refusal logic (29 attempts)
```

## 6. Pytest

```bash
python -m pytest
# expect: 271 passed
```

## 7. Frozen fingerprint values (v0.1.0)

```
vectors_suite_sha256:    sha256:6168d2075931baa98bba763f9cd537142554aae7b26f19e3e93a60de2ee5bb0f
manifests_suite_sha256:  sha256:74eaaa62271f23172232bda43ba3340543e66c46ba1e2f5e6da18d3447a6ba29
corpus_sha256:           sha256:c95685bff48c15abc313c462908b05ac309250bc660c2d802ae51af5a8038b09
```

Compute and compare:

```bash
python3 -c "import json; r=json.load(open('reports/conformance-report.json')); print(r['vectors_suite_sha256'])"
python3 -c "import json; r=json.load(open('interop/reports/interop-report.json')); print(r['manifests_suite_sha256'])"
make canonicalization-check       # the OK line prints corpus_sha256
```

## 8. Environmental assumptions

- **OS:** Linux or macOS. Windows untested.
- **Python:** 3.11+ recommended; 3.14 tested.
- **Rust:** 1.94+ (rustup-stable). The Rust verifier uses `serde`, `serde_json` (default features off + `std`), and `sha2`.
- **Locale:** UTF-8 (`LANG=C.UTF-8` or `en_US.UTF-8`). The canonicalization corpus contains non-ASCII characters; an ASCII-only locale will produce divergent canonical bytes.
- **Disk:** ~150 MB after `cargo build` (most of it is `rust_verifier/target/`, which is `.gitignore`d).
- **Network:** none. The CI gate does no outbound network calls.
- **Time:** about 1–3 seconds for a warm `make ci`; first `cargo build` adds ~30–60 seconds.

## 9. If something diverges

Do not change vectors, schemas, the canonicalization corpus, or the frozen fingerprints. File a finding per `docs/audits/AUDIT_SCOPE_v0.1.md §10`.

## 10. What to read next

| Goal | File |
|---|---|
| Understand the protocol | `SPEC.md`, `SPEC_LOCK_v0.1.md` |
| Submit a third-party verifier | `docs/release/THIRD_PARTY_VERIFIER_BRIEF_v0.1.md` |
| Audit scope and known gaps | `docs/audits/AUDIT_SCOPE_v0.1.md` |
| Implementation registry | `IMPLEMENTATIONS.md`, `docs/release/IMPLEMENTATION_TRACKER.md` |
