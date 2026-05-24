# WO-D5-SIZE-CAP — Preimage size cap for Class D commit stages

**Scope:** v0.2.0 only. v0.1.0 is frozen and inherits no behavioral change.
**Filed:** 2026-05-23
**Status:** DRAFT — spec patch + vector + test landed; verifier enforcement pending (separate WO).

## 1. Problem

Invariant **D5** (`SPEC.md §3 Class D`) requires Class D commit-chain stages to
include preimage `content`. An external reviewer flagged this as an unbounded
DoS surface: a producer (malicious or sloppy) can attach an arbitrarily large
preimage to a single stage — e.g. a 10 GB LLM context blob — and force every
conformant verifier to materialize, canonicalize, and hash it. The verifier has
no spec authority to reject on size, so it must either OOM or violate D5.

D5 as written gives the attacker the choice between two bad outcomes for the
verifier. That is a spec defect, not an implementation defect.

## 2. Proposed cap

| Bound | Value | Rationale |
|---|---|---|
| Per-stage preimage `content` | **1 MiB** (1,048,576 bytes) of canonical JSON serialization | ~1,000× the median size of existing v0.1.0 conduct-vector stages; large enough for paragraph-scale governance summaries, small enough to make whole-context-dump attacks impossible. |
| Per-artifact total (sum of all stage preimages) | **4 MiB** (4,194,304 bytes) | Matches the default request-body limit of most HTTP front-ends; prevents the same DoS via many medium stages. |

Measurement is over the **canonical JSON serialization** of the `content`
field (sorted keys, compact separators, UTF-8), so cap accounting is
deterministic and verifier-independent.

## 3. Affected invariant text

A new invariant **D6** is added under `SPEC_LOCK_v0.2.0.md §2.5` (see
`work_orders/D5-SIZE-CAP-spec-patch.md` for exact patch markdown). D5 itself
is unchanged — D6 narrows D5 with a bounded-resource constraint.

## 4. Rejection status

A v0.2.0 Class D artifact whose commit chain violates D6 MUST receive
`CONDUCT_INVALID`. No new top-level status token is introduced; the status
registry is unchanged. Verifiers MUST emit a stable reason code
`PREIMAGE_OVERSIZED` in their per-verdict reasons list so the violation is
machine-distinguishable from generic D5 / CC1 failures.

## 5. Follow-up

- Verifier enforcement (Python `tools/minimal_verifier.py`, Rust, Go) — separate WO.
- v0.1.0 is unaffected; existing 33-vector suite continues to pass `make ci`.
