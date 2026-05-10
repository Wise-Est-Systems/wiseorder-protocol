# INTELLAGENT + WISEORDER — Part 3: Layers

*Canonicalization, determinism, authorization, memory, refusal.*

**Conformant to:** [`INTELLAGENT-MASTER-SPEC-STANDARD-v1.0.md`](./INTELLAGENT-MASTER-SPEC-STANDARD-v1.0.md).
**Document type:** Normative specification — split form.
**Subject release:** v0.1.0.
**Date:** 2026-05-10.

**Parts:**
- Part 1 — Foundations: [`WISEORDER-WHITEPAPER-PART-1-FOUNDATIONS.md`](./WISEORDER-WHITEPAPER-PART-1-FOUNDATIONS.md) (§2.1 TITLE → §2.6 DEFINITIONS)
- Part 2 — Mechanics: [`WISEORDER-WHITEPAPER-PART-2-MECHANICS.md`](./WISEORDER-WHITEPAPER-PART-2-MECHANICS.md) (§2.7 PRIMITIVES → §2.11 DATA STRUCTURES)
- Part 3 — Layers: [`WISEORDER-WHITEPAPER-PART-3-LAYERS.md`](./WISEORDER-WHITEPAPER-PART-3-LAYERS.md) (§2.12 CANONICALIZATION → §2.16 REFUSAL)
- Part 4 — Conformance & Release: [`WISEORDER-WHITEPAPER-PART-4-CONFORMANCE.md`](./WISEORDER-WHITEPAPER-PART-4-CONFORMANCE.md) (§2.17 CONFORMANCE → §3 STATUS)

The four parts together constitute the complete normative specification. No part is independently sufficient; each cites terms defined in others (DEFINITIONS in Part 1; INVARIANTS in Part 2). Read in order on first pass; reference any part directly thereafter.

---

## 2.12 CANONICALIZATION

The stack's canonicalization layer is the single most pressure-sensitive surface: any byte-level disagreement between two implementations of the canonical scheme produces silent, undetectable divergence in every downstream `sha256` digest.

### 2.12.1 Canonical scheme registration

v0.1.0 registers exactly one canonicalization scheme: **RFC 8785 JCS** (semantically). The v0.1 Python encoder ships as a near-equivalent — `json.dumps(..., sort_keys=True, separators=(',', ':'), ensure_ascii=False)` — and is internal tooling, not the canonical reference. The 10-entry golden corpus (`canonicalization/golden/`) is the canonical implementation.

### 2.12.2 Canonical serialization rules

Per the registered scheme:

- Object keys MUST be sorted in code-point order.
- Strings MUST be UTF-8 encoded.
- Whitespace between tokens MUST be empty (`separators=(',', ':')`).
- Numbers MUST follow RFC 8785 §3.2.2.3 number serialization (no trailing zeros; exponent notation per spec).
- Unicode strings MUST NOT contain lone surrogates.
- Booleans serialize as `true` / `false`.
- `null` is the only valid null literal.

### 2.12.3 Hashing semantics

For every artifact whose content-addressing matters:

- Compute canonical bytes via the registered scheme.
- Compute SHA-256 over those bytes.
- Encode the digest as 64 lowercase hex characters; prefix with `sha256:` when persisted as a string identifier.

The `sha256:` prefix is policy, not algorithm; the prefix appears in identifier strings (e.g., `state_id`, `provenance.signature_sha256`). Internal computations work over raw 64-hex digests.

### 2.12.4 Replay stability guarantees

- `canonicalize(canonicalize(x)) == canonicalize(x)` for any artifact `x` (idempotent — CS2).
- For two implementations of the registered scheme, byte-identical canonical output is required for every artifact in the golden corpus.
- For two runs of the same implementation, byte-identical canonical output is required for every input.

### 2.12.5 Cross-platform expectations

- The corpus pins inputs and expected canonical bytes; an implementation is conformant if it produces those bytes byte-identically.
- v0.1 ships only the Python implementation; second-language implementations (Rust, TypeScript, Go) are future work and become trust-accumulation events when they pass the corpus.
- Drift between the v0.1 Python encoder and a future strict-RFC-8785-JCS Python implementation is itself a coordinated drift event (TR-6) requiring a documented migration.

### 2.12.6 Failure modes addressed by the corpus

The 10 corpus entries collectively exercise every documented JCS drift surface (per `CROSS-LANGUAGE-CANONICALIZATION-v0.1.md` §5):

1. Number serialization (trailing zeros, exponent notation).
2. String escape sequences (`\u`, `\\`, control characters).
3. Unicode normalization (NFC vs NFD; RFC 8785 leaves this to upstream).
4. Surrogate handling (lone surrogates must fail).
5. Object key sort order (code-point, not lexical).
6. Whitespace handling (canonical JCS has no whitespace).
7. Edge-case numbers (0, -0, very small, very large).
8. Empty objects and arrays.
9. Deep nesting.
10. Mixed-type arrays.

The corpus is the v0.1.0 canonical implementation. Reviewers verify by running `make canonicalization-check`.

### 2.12.7 Suite fingerprint

`corpus_sha256: sha256:c95685bff48c15abc313c462908b05ac309250bc660c2d802ae51af5a8038b09`.

Computed over the sorted concatenation of every corpus entry's per-file SHA-256, newline-delimited.

---

## 2.13 DETERMINISM MODEL

The stack distinguishes deterministic from nondeterministic surfaces explicitly. No surface is silently nondeterministic.

### 2.13.1 Deterministic surfaces

The following surfaces are byte-deterministic across runs:

- **Canonical serialization.** Idempotent, scheme-locked.
- **Kernel verification.** Pure function of `(transition, prior_state)`.
- **Audit chain hashing.** Pure function of canonical body bytes + predecessor pointer.
- **Refusal record hashing.** Pure function of canonical body bytes.
- **State ID computation.** Pure function of `objects`.
- **Manifest generation.** Pure function of fixture inputs.
- **Conformance runner outputs.** Pure function of vectors + kernel.
- **Interop runner outputs.** Pure function of fixtures + manifests + implementations.
- **Suite fingerprints.** Pure function of suite contents.

### 2.13.2 Nondeterministic surfaces

The following surfaces are non-byte-deterministic and explicitly out of contract:

- **Real-provider sampling** (OpenAI, Anthropic). Fixed seeds reduce but do not eliminate cross-machine drift. Mitigation: capture full provider metadata (`provider_id`, `model_id`, `seed`, `temperature`, `tokens_in`, `tokens_out`, `finish_reason`, `provider_metadata`) in `proposal_cost`.
- **Wall-clock timestamps.** When `set_clock` is unpinned, `utcnow_iso8601()` returns the actual current time. Replay scenarios pin the clock; production scenarios do not.
- **Local OpenAI-compatible providers** running on different hardware. Same caveat as real providers.

### 2.13.3 Replay guarantees

Under the pinned-input contract (clock + ID source + seed + provider + prompt + query), the runtime guarantees:

- Byte-identical audit memory bytes.
- Byte-identical refusal records.
- Byte-identical state files.
- Byte-identical proposal candidates (when the provider is `DeterministicMockProvider`).

The `DeterministicMockProvider` is the in-contract Provider for replay scenarios.

### 2.13.4 Replay limitations

- Cross-machine real-provider determinism is not guaranteed even under fixed seeds.
- Cross-version replay is not guaranteed (v0.1 → v0.2 trust does not auto-promote, TP8).
- Cross-implementation replay is class-scoped and vector-bounded.

### 2.13.5 Live verification

Cross-run hash from `RELEASE-STATUS-v0.1.md` §6:

```
/tmp/demoA audit_sha: b71c7134ef2c33ea5fcc9a3eb723efe6294ba18759ed91d1f64bdfe826107ba5
/tmp/demoB audit_sha: b71c7134ef2c33ea5fcc9a3eb723efe6294ba18759ed91d1f64bdfe826107ba5
MATCH
```

Two clean tmp directories run the same demo; the audit memory bytes match SHA-256.

---

## 2.14 AUTHORIZATION MODEL

Authorization is declared, bounded, revocable, auditable, and never auto-promoted to trust. The stack treats verification (by the kernel) and authorization (by the gate) as distinct categories.

### 2.14.1 Authorization boundaries

- **Verification ≠ authorization.** A kernel verdict of `passed=True` does NOT authorize an action. The gate independently evaluates `gate.evaluate(transition).authorized`.
- **Action ≠ cognition.** A pure cognitive transition (`action == null`) does not require authorization. Only action-bearing transitions require gate evaluation.
- **Source ≠ scope.** An authorization names its source (a policy or work order) and inherits that source's declared scope. Authority cannot exceed the declared scope.
- **Authorization ≠ trust.** A registered authorization grants the right to attempt; it does not grant the operational trust of the result. Trust accumulates only through TR-event-free continuity.

### 2.14.2 Authority surfaces

v0.1 surfaces:

- **Per-implementation classes_supported.** The set of classes the implementation declares it can produce or verify.
- **Per-identity allowlist.** `allowed_commands`, `forbidden_commands`, `allowed_files`, `default_denied_paths` per agent identity.
- **Per-action source_id.** Every action carries `authorization.source_id` resolving to a registered policy.
- **Per-work-order scope.** Work orders carry `allowed_commands`, `allowed_files`, `expiry`.

### 2.14.3 Privilege requirements

Each operation declares its privilege:

- **Read state.** Default privilege; no authorization required.
- **Append audit memory.** Kernel-internal; no operator privilege exposed.
- **Apply transition.** Requires kernel verification; for action-bearing, also gate authorization.
- **Modify canon.** Forbidden under any current authority (Forbidden Surfaces §2.7).
- **Spawn subprocess.** Requires work-order admission; identity-scoped.
- **Tag release.** Requires release-identity admission.

### 2.14.4 Execution refusal conditions

- **AG1.** Self-quoted authorization → gate refuses; `reason_codes=("AG1",)`.
- **AG3.** Missing `source_id` on action-bearing transition → gate refuses; `reason_codes=("AG3",)`.
- **Source not registered.** `authorization.source_id` does not resolve to any registered policy → gate refuses; `reason_codes=("AG3",)` (treated as missing).
- **Policy denies action.** Policy evaluation returns `denied` → gate refuses; `reason_codes` carries the policy code.
- **Work-order expired.** Work order's `expiry < now` → admission refuses; `reason_codes=("WO_EXPIRED",)`.
- **Identity mismatch.** Acting identity does not match work-order identity → admission refuses; `reason_codes=("WO_IDENTITY_MISMATCH",)`.
- **Cross-role action.** One-agent-one-duty violation (e.g., proposer attempting executor action) → admission refuses; `reason_codes=("WO_CROSS_ROLE",)`.

Verification does NOT imply authorization. The two are separately enforced.

---

## 2.15 MEMORY MODEL

The audit memory is the operational record of every transition the runtime accepts or refuses. It is append-only, content-addressed, commit-chained, and inspectable.

### 2.15.1 Mutation semantics

- Append-only. No in-place modification of any audit entry.
- Each append computes `this_entry_sha256` over the canonical body with the self-field omitted.
- Each append updates `head.json` atomically via `os.replace`.
- A failed append (e.g., disk full mid-write) is detected at next initialization via chain integrity check.

### 2.15.2 Persistence semantics

- Each entry persists as a single JSON file under `intellagent_audit/entries/<this_entry_sha256>.json`.
- The head pointer persists in `intellagent_audit/head.json`.
- Refusal records persist under `intellagent_audit/refusals/<refusal_sha256>.json`.
- Atomic writes throughout: temp-file + `os.replace`.
- File format: canonical JSON (sort_keys + compact + UTF-8).

### 2.15.3 Append semantics

`AuditMemory.append(entry: AuditEntry) -> None`:

1. Verify `entry.prev_entry_sha256 == current_head_sha256` (or both null for genesis).
2. Recompute `this_entry_sha256` from the entry's canonical body with self-field omitted; verify it matches `entry.this_entry_sha256`.
3. Write the entry file.
4. Write the new head pointer.

Any step failure raises a typed exception; the chain is left in a consistent state (the entry file may exist without the head update; next initialization detects this as an orphaned entry).

### 2.15.4 Replay semantics

- Full chain reconstructable from disk by walking from head backward via `prev_entry_sha256`.
- Each step recomputes `this_entry_sha256` and compares to recorded value.
- Walk terminates at genesis (`prev_entry_sha256 == null`).
- A successful walk proves byte-stability of the chain.

### 2.15.5 Tamper semantics

- Modifying any entry's body invalidates that entry's `this_entry_sha256`. Detected at the next `verify_chain()`.
- Modifying any entry's `prev_entry_sha256` breaks the predecessor link. Detected.
- Truncating the chain (removing the last N entries) breaks the head pointer or leaves an orphaned head. Detected.
- Inserting a forged entry requires recomputing all subsequent `this_entry_sha256` values, which requires forging every successor. Cost-prohibitive but not cryptographically impossible — defense-in-depth via reviewer reproduction.

### 2.15.6 Audit semantics

- `verify_chain()` returns `None` on success or raises `ChainCorrupt(entry_id, reason)` on first failure.
- `ChainCorrupt` is fail-closed; the runtime will not append new entries to a corrupt chain.
- An operator who detects `ChainCorrupt` must follow the correction-law procedure (`CORRECTION-LAW-v0.1.md` §4): public disclosure, root-cause analysis, patch + regression test, new tag, time-bounded probation.

### 2.15.7 Inspectability

The memory is inspectable in three ways:

- **CLI.** `intellagent audit verify` runs `verify_chain()` and reports OK or `ChainCorrupt`.
- **CLI.** `intellagent audit show <entry_id>` prints the entry body.
- **Direct.** Reading the JSON files directly. The files are canonical; no tooling is required to interpret them.

---

## 2.16 REFUSAL SEMANTICS

Refusal is a sealed first-class artifact, not a generic error. Every refusal carries the bytes that produced it and is inspectable independently.

### 2.16.1 Refusal conditions

A refusal is sealed when:

1. **Kernel rejection.** `kernel.verify(transition, prior_state).passed == False`.
2. **Gate rejection.** Action-bearing transition; `gate.evaluate(transition).authorized == False`.
3. **Empty proposer.** A proposer returns zero candidates for the query.
4. **All candidates rejected.** Every candidate from the proposer set fails kernel or gate.
5. **Search budget exhausted.** Cross-proposer search exceeds budget without acceptance.

### 2.16.2 Refusal artifacts

The `RefusalRecord` (per §2.11.7) carries:

- `transition_id` — the rejected transition (or query) identifier.
- `class_` — Class A/B/C/D as applicable.
- `kernel_verdict` — the kernel's `KernelVerdict` if the rejection was kernel-side.
- `gate_decision` — the gate's `AuthorizationDecision` if the rejection was gate-side.
- `candidates_rejected` — the list of all rejected candidates with their per-candidate reasons.
- `challenge_surface_sha256` — SHA-256 over the canonical bytes of the challenge surface (the query, or the rejected transition's canonical body).
- `timestamp` — refusal sealing time.
- `reason_codes` — invariant IDs that fired (A1, B2, AG3, etc.).
- `refusal_sha256` — content-addressed identifier.

### 2.16.3 Refusal replay behavior

- A refusal is fully replayable from its sealed bytes.
- A reviewer reads `intellagent_audit/refusals/<refusal_sha256>.json` and reconstructs:
  - What was queried.
  - What candidates were proposed.
  - What invariant fired.
  - What state was current at refusal time.
- Reproducing the refusal under the same Provider + same prompt + same seed produces a byte-identical record (under the determinism contract).

### 2.16.4 Refusal audit semantics

- Each refusal participates in the audit chain via a refusal-marker `AuditEntry`.
- The marker entry has `kernel_verdict` set to the refusing kernel's verdict (or null if gate-rejection); `gate_decision` set to the refusing gate's decision (or null if kernel-rejection); `state_id_after` equal to `state_id_before` (refusal does not advance state).
- The chain remains intact through refusals; `verify_chain()` walks through refusal markers identically to acceptance entries.

### 2.16.5 Refusal validity

- A refusal is valid if it carries a non-empty `challenge_surface_sha256` and at least one `reason_codes` entry.
- A refusal record with empty `challenge_surface_sha256` is itself a TR-7 unsupported-claim-surface event (the runtime claimed to refuse but recorded no challenge).
- A refusal that records `reason_codes` not corresponding to any defined invariant is a TR-4 validation drift event.

### 2.16.6 Refusal as legitimate outcome

Refusal is operational normality. The runtime is designed such that:

- Every malformed transition produces a refusal, not a crash.
- Every unauthorized action produces a refusal, not silent denial.
- Every empty-proposer search produces a refusal, not a null result.
- Every chain corruption produces fail-closed refusal of further appends.

The thesis (§2.5) is satisfied when the system refuses what it cannot verify.

---

