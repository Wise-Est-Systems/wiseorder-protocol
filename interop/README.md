# Interoperability

> Operational layer that proves real implementation artifacts, real vectors, real tooling, and real reports interoperate under WiseOrder Protocol v0.1.0 — without conflating the four concerns.

---

## Conformance vs. interoperability

**Conformance** (under [`tools/`](../tools/) and [`vectors/`](../vectors/)) asks: does an implementation correctly implement WiseOrder for the classes it declares? Conformance writes [`reports/conformance-report.json`](../reports/conformance-report.json).

**Interoperability** (here) asks: do the artifacts an implementation produces fit cleanly into the wider WiseOrder ecosystem?

- Does the artifact's class match what the implementation declared in `IMPLEMENTATIONS.md`?
- Does the fixture align with at least one published vector?
- Does the aligned vector share the same class as the fixture?
- Is the fixture metadata stable, deterministic, and tamper-evident?
- Does the registry-level F-1 ban (WISEATA cannot declare Class A) hold at the **fixture** level too?

Conformance proves the rules. Interoperability proves the rules apply to actual artifacts.

A failing interop check says "this fixture does not fit cleanly into the registered ecosystem." It does **not** say "this implementation is non-conformant" — that is a separate claim made by the conformance run.

---

## Why WISEATA has no Class A fixture

Per F-1 (see [`../IMPLEMENTATIONS.md`](../IMPLEMENTATIONS.md)), WISEATA-v0.1.1 uses a line-oriented `key=value` canonicalization, not RFC 8785 JCS. WiseOrder v0.1.0 registers JCS only.

WISEATA therefore declares `classes_supported: ["B"]` only. Producing a Class A fixture from WISEATA would require either migrating WISEATA proofs to JCS or registering a second canonicalization scheme — both rejected for v0.1.0.

The interop layer enforces this **at two layers**:

1. **`generate_fixture_manifest.py`** refuses to write a manifest for any `*.fixture.json` whose `implementation == "WISEATA"` and `artifact_class == "A"`.
2. **`run_interop_checks.py`** rejects any manifest with that combination, even if it somehow lands on disk.

---

## Why vectors remain the law

Vectors govern *what conformance means.* Fixtures govern *whether real artifacts cleanly map onto vectors.* The interop layer cross-references fixtures against the published vector suite, but does **not** redefine vector semantics. If `class-b-valid-wiseexp` ever changes, every Class B fixture aligned with it inherits that change at audit time without any modification under `interop/`.

This separation is enforced by:

- `aligned_vectors` listing only `vector_id`s that exist under [`../vectors/`](../vectors/).
- The class of every aligned vector being verified to equal the fixture's `artifact_class`.

---

## Why manifests are deterministic

Manifests are tooling artifacts, not protocol artifacts. They must regenerate to byte-identical content on repeated runs so a CI diff can detect drift. Determinism is achieved by:

- Pinning `generated_at` in the fixture source — the wall clock is never read by the generator.
- Sorting JSON keys via `sort_keys=True` on every serialization.
- Computing `artifact_sha256` over a tooling-internal canonical JSON form of the embedded `artifact` field (sorted keys, compact separators, UTF-8).

This is **tooling-internal** canonicalization for fingerprinting only. **It is not a Class A canonicalization scheme.** Class A canonicalization remains RFC 8785 JCS only, per `SPEC.md` §4. The interop fingerprinting exists to catch tampering of fixture and manifest files, not to validate Class A artifacts (that is the job of the conformance suite).

A fixture's `generated_at` is a frozen point-in-time stamp from when the source was authored. It is **not** "the current time when the manifest was written," which is intentional: that property would make CI diffs noisy without providing audit value.

---

## Why interoperability ≠ semantic equivalence outside declared classes

A passing interop check proves the fixture's metadata is consistent with the registry and vector suite. It does **not** prove:

- That the implementation produces semantically-equivalent artifacts to other implementations across all inputs.
- That the implementation is conformant for classes it has not declared.
- That cross-implementation behaviors agree under adversarial inputs.

Those questions belong elsewhere — formal audit programs, independent attack-suite testing, separate vector classes (potentially in future protocol versions). The interop layer's purpose is narrower: catch the cheap, fast classes of misalignment (registry mismatch, vector typo, F-1 bypass attempt, manifest-byte drift) before they get baked into a `CONFORMANT` audit declaration.

---

## Layout

```
interop/
├── README.md                                     ← this file
├── fixtures/
│   ├── winstack/
│   │   ├── winstack-class-a-valid-001.fixture.json   ← authored source
│   │   ├── winstack-class-a-valid-001.manifest.json  ← generated, committed
│   │   ├── winstack-class-b-valid-001.fixture.json
│   │   └── winstack-class-b-valid-001.manifest.json
│   └── wiseata/
│       ├── wiseata-class-b-valid-001.fixture.json
│       └── wiseata-class-b-valid-001.manifest.json
├── reports/
│   ├── .gitkeep
│   ├── fixture-manifest-report.json              ← regenerated by `make interop`
│   ├── interop-report.json                        ← regenerated by `make interop`
│   └── interop-summary.txt                        ← regenerated by `make interop`
└── scripts/
    ├── generate_fixture_manifest.py
    └── run_interop_checks.py
```

`*.fixture.json` files are **authored and committed**. `*.manifest.json` files are **generated and committed** (so `audit_status: "CONFORMANT"` declarations elsewhere in the registry can reference them with stable hashes).

---

## Running it

```bash
make interop          # generate manifests + run checks; updates reports/
make ci               # tests + conformance + interop, in that order
```

Self-tests covering the interop tooling live at [`../tests/test_interop.py`](../tests/test_interop.py); they verify deterministic generation, the F-1 enforcement, vector-class alignment, the SHA-256 format gate, and serialization stability.

---

## Adding a new fixture

1. Author `interop/fixtures/<implementation_lower>/<fixture_id>.fixture.json`. The `fixture_id` MUST equal the filename stem.
2. The fixture's `implementation` MUST be a registered implementation in `IMPLEMENTATIONS.md` whose `classes_supported` includes the fixture's `artifact_class`.
3. The fixture's `aligned_vectors` MUST reference at least one published `vectors/*.json` whose class equals the fixture's `artifact_class`.
4. Run `make interop`. The manifest is written deterministically; commit it alongside the source.
5. `make ci` should pass before opening a PR.

---

## What this layer is *not*

- Not a runtime. The interop scripts do not execute Class A/B/C/D verification on the artifact contents; that is the conformance suite's job.
- Not a network service.
- Not a protocol negotiator. Fixtures pin `protocol: "wiseorder"` and `version: "0.1.0"` literally; mismatches fail.
- Not a canonicalization scheme registry.

If a feature would push the layer into any of the above, it belongs elsewhere.
