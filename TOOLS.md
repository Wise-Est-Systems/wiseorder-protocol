# Tooling

> Operational guide for the WiseOrder Protocol v0.1.0 conformance and interop tooling. The protocol semantics live in [`SPEC.md`](./SPEC.md); this file documents *how to use the validators* and *what their guarantees are*, not *what they enforce* (that is `CONFORMANCE.md`, the JSON schemas, and the published vectors).

---

## What it does

The tooling layer turns the spec into mechanical pass/fail across three surfaces:

| Surface | What it audits | Where laws live |
| --- | --- | --- |
| Conformance vectors | Every `vectors/*.json` | `schemas/vector.schema.json` + cross-rules in `tools/validate_vectors.py` |
| Implementation declarations | Every JSON block in `IMPLEMENTATIONS.md` | `schemas/implementation.schema.json` + cross-rules in `tools/validate_implementations.py` |
| Interop fixtures + manifests | Every `interop/fixtures/*/*.fixture.json` and its generated `*.manifest.json` | `schemas/fixture.schema.json`, `schemas/manifest.schema.json` + cross-rules in `interop/scripts/run_interop_checks.py` |

Conformance composes into `tools/run_conformance.py`, interop composes into `interop/scripts/run_interop_checks.py`, and both write committed evidence artifacts under `reports/` and `interop/reports/`.

---

## Install

Python 3.12 or newer. From the repo root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Pinned dependencies:

- `jsonschema==4.26.0` — schema engine
- `pytest>=8,<9` — self-tests

---

## Targets

```bash
make validate-vectors            # validate every vectors/*.json
make validate-implementations    # audit every JSON block in IMPLEMENTATIONS.md
make conformance                 # full conformance run; writes reports/
make interop                     # generate manifests + run interop checks; writes interop/reports/
make test                        # tooling self-tests
make ci                          # test → conformance → interop
make verify-drift                # regenerate everything; fail if anything diffs from the committed tree
```

All targets exit `0` on PASS and `1` on any failure.

---

## Suite fingerprints

Both report layers carry a **suite fingerprint** alongside their per-item digests:

| Field | Lives in | Definition |
| --- | --- | --- |
| `vectors_suite_sha256` | `reports/conformance-report.json` | SHA-256 of the sorted-by-`vector_id` concatenation of every vector's per-file SHA-256, newline-delimited. |
| `manifests_suite_sha256` | `interop/reports/interop-report.json` | SHA-256 of the sorted-by-`fixture_id` concatenation of every manifest's per-file SHA-256, newline-delimited. |

These detect **silent suite drift** between runs. A vector edit that does not change the human-readable summary still changes one or more `sha256` fields, which changes the suite fingerprint.

### Artifact fingerprints vs. suite fingerprints

| | Scope | Where |
| --- | --- | --- |
| **Artifact fingerprint** | Identity of one artifact (one vector / one manifest / one fixture artifact). | Per-item field: `vector_results[].sha256`, `interop_results[].manifest_sha256`, `manifest.artifact_sha256`. |
| **Suite fingerprint** | Identity of the whole audited collection. | Top-level field: `vectors_suite_sha256`, `manifests_suite_sha256`. |

A suite fingerprint is a stable cryptographic name for "the law set the auditor was looking at." If two `audit_status: "CONFORMANT"` declarations cite reports with different suite fingerprints, they were audited against different law sets.

These are **tooling-internal** fingerprints, used for byte-stability detection and audit traceability. They are NOT Class A canonicalization schemes — that remains RFC 8785 JCS only, per `SPEC.md` §4.

---

## Deterministic regeneration

Every output the tooling produces is a pure function of committed inputs:

- `generated_at` in fixtures is committed in the source; the wall clock is never read.
- JSON serialization is `sort_keys=True, indent=2`, with a trailing newline; `dumps` is called the same way everywhere.
- Hashes are over byte-stable canonical forms.
- File discovery is `sorted(...)`, never iteration order.

Running `make conformance && make interop` twice on a clean checkout produces byte-identical reports and manifests. CI relies on this property.

---

## Drift enforcement

After `make interop`, CI runs:

```bash
git diff --exit-code -- reports/ interop/
```

A non-zero exit means one of:

- A developer hand-edited a manifest or report and committed the edit. Regeneration overwrote it; the diff surfaced the edit.
- The tooling's output format changed. Regeneration is correct under the new code, but the committed state still reflects the old code.
- A fixture, vector, or implementation declaration changed without the report being regenerated and committed.

Resolution is the same in all three cases: run `make conformance && make interop` locally and commit the result.

`make verify-drift` performs the same regenerate-then-diff dance locally.

---

## Why generated reports are committed

`reports/conformance-report.json`, `reports/conformance-summary.txt`, `interop/reports/interop-report.json`, `interop/reports/interop-summary.txt`, and every `interop/fixtures/*/*.manifest.json` are committed. Three reasons:

1. **Audit evidence.** `audit_status: "CONFORMANT"` declarations cite these files via `evidence.conformance_report` and `evidence.interop_report`. The references must resolve in a fresh checkout.
2. **Drift detection.** Without a committed baseline, `git diff --exit-code` has nothing to compare against.
3. **Suite-fingerprint traceability.** The committed `vectors_suite_sha256` and `manifests_suite_sha256` are the authoritative names for "what the protocol's law set looked like at this commit." Future audits cite them.

Other generated artifacts (`__pycache__/`, `.pytest_cache/`, virtualenvs) are listed in `.gitignore` and are never committed.

---

## Report linkage semantics

For an implementation to declare `audit_status: "CONFORMANT"`, its `evidence` block MUST include **both** reports:

```json
{
  "implementation": "Winstack",
  "protocol": "wiseorder",
  "version": "0.1.0",
  "classes_supported": ["A", "B"],
  "audit_status": "CONFORMANT",
  "evidence": {
    "conformance_report": "reports/conformance-report.json",
    "interop_report":     "interop/reports/interop-report.json",
    "report_sha256":      "sha256:<combined hex>"
  }
}
```

Validation rules (enforced by `tools/validate_implementations.py`):

- Both reports MUST exist.
- Both reports MUST have `overall_status: "PASS"`.
- Both reports MUST declare `protocol == "wiseorder"` and the same `version` as the implementation.
- The conformance report MUST contain at least one passing vector for every class in `classes_supported`, and MUST NOT contain any failing vector in those classes.
- `report_sha256` is optional. When present, it MUST equal `sha256(canonical({"conformance": "sha256:<conformance>", "interop": "sha256:<interop>"}))` — a single fingerprint over the two report digests, sorted-key compact JSON.

`NOT_AUDITED` requires no evidence. `FAILED` requires non-empty `notes`.

---

## Fail-closed behavior

- An empty vector suite returns `overall_status: "FAIL"`.
- An empty fixture set returns `overall_status: "FAIL"`.
- An unparseable JSON file is recorded as a failure, not silently skipped.
- An `audit_status: "CONFORMANT"` declaration without `evidence.conformance_report` and `evidence.interop_report` fails before any I/O.
- A referenced report that does not exist, fails to parse, has the wrong protocol/version, or has `overall_status != "PASS"` invalidates the declaration.
- An optional `evidence.report_sha256`, when present, must match the computed value.
- A manifest that does not match `schemas/manifest.schema.json` is rejected.
- A fixture that does not match `schemas/fixture.schema.json` is rejected; no manifest is written.
- A vector whose `vector_id` does not match its filename stem is rejected.
- A WISEATA fixture claiming Class A is rejected at both layers (generation refuses to write a manifest; checking refuses any manifest with that combination).

Tooling never runs networking, never writes outside `reports/` and `interop/reports/`, never installs anything at runtime, and never coerces values silently.

---

## Adding a new vector

1. Stable `vector_id` matching filename stem: `vectors/<vector_id>.json`.
2. `protocol_version: "0.1.0"`. `class` ∈ {A,B,C,D}. `expected_status` is in that class's status registry.
3. `make validate-vectors` until green.
4. `make conformance` to refresh the conformance report (the suite fingerprint changes).
5. `make ci` should pass before opening a PR.

## Adding a new implementation

1. Add a JSON code block in `IMPLEMENTATIONS.md` matching `schemas/implementation.schema.json`.
2. Start with `audit_status: "NOT_AUDITED"`.
3. To upgrade to `CONFORMANT`: add an `evidence` block referencing both reports. The conformance report must cover every class in `classes_supported`. Optionally pin `evidence.report_sha256` for tighter audit traceability.
4. `make verify-drift` should pass before opening a PR.

## Adding a new interop fixture

1. Author `interop/fixtures/<implementation_lower>/<fixture_id>.fixture.json`. The `fixture_id` MUST equal the filename stem.
2. The fixture's `implementation` MUST be a registered implementation in `IMPLEMENTATIONS.md` whose `classes_supported` includes the fixture's `artifact_class`.
3. The fixture's `aligned_vectors` MUST reference at least one published `vectors/*.json` whose class equals the fixture's `artifact_class`.
4. `make interop`. The manifest is written deterministically; commit it.
5. `make verify-drift` should pass.

---

## Documentation Code Standard

All code examples in this repository MUST be implementation-realistic.
**Pseudocode is not permitted in Python code blocks.** Specifically:

- Bare `...` ellipsis statements are banned in any Python code block, except
  in blocks whose first non-blank line is the literal comment
  `# interface example`. That marker is reserved for `Protocol` and other
  abstract-interface declarations whose method bodies must be `...`.
- Bare `pass` statements are banned in all Python code blocks.
- `return ...` is banned in all Python code blocks.
- `TODO` is banned in all Python code blocks.
- `NotImplemented` and `NotImplementedError` are banned in all Python code blocks.
- Argument elisions like `def foo(self, ..., x: int = 0)` are banned.
  Use `*args` / `**kwargs` if you genuinely need to elide unspecified arguments.
- Comments like `# ... continued` or `# ... existing init` are pseudocode; do not use them.

Conceptual algorithms that do not map cleanly to executable code MUST be
written as numbered prose steps, not as fake Python with placeholder bodies.
JSON / shape examples that use `...` to denote array continuation
(e.g., `["<id>", ...]`) are documentation of structure, not Python code, and
remain permitted in JSON blocks.

The standard is enforced by [`tools/check_no_pseudocode.py`](./tools/check_no_pseudocode.py),
runnable via `make no-pseudocode` and checked on every CI run.
`SPEC.md` is excluded by default because its code blocks are normative
illustrations of protocol semantics rather than runnable code.

---

## What this layer is *not*

- Not a runtime. The tools do not implement Class A/B/C/D verification themselves; they verify the laws under which other implementations would do so.
- Not a network service.
- Not a signing system. SHA-256 is used for content fingerprinting only.
- Not a packaging story. There is no `setup.py`, no published package, no entry-point scripts. Run via `make` or `python3 path/to/script.py`.

If a feature would push the layer into any of the above, it belongs elsewhere.
