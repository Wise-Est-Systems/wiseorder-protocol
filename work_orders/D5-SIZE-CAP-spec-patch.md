# Proposed patch — `SPEC_LOCK_v0.2.0.md`

The following section is the proposed addition. It is NOT applied yet — the
human author of v0.2.0 must approve and land it.

Insertion point: a new subsection **§2.5** under **§2 Frozen Surfaces (changes
from v0.1.0)**, immediately after §2.4 Genesis and before §3 v0.1.0
Coexistence.

---

```markdown
### 2.5 Class D commit-stage preimage size cap

v0.1.0 invariant D5 (`SPEC.md §3 Class D`) requires Class D commit-chain
stages to carry preimage `content`. v0.2.0 narrows D5 with an explicit
resource bound to remove the denial-of-service surface created by an
unbounded preimage requirement.

**Invariant D6 (v0.2.0):**

A conformant v0.2.0 verifier MUST reject as `CONDUCT_INVALID` any Class D
artifact whose `commit_chain` violates either of the following bounds:

1. **Per-stage cap.** The canonical JSON serialization (sorted keys, compact
   separators `(',', ':')`, UTF-8) of any single stage's `content` field MUST
   NOT exceed **1,048,576 bytes (1 MiB)**.

2. **Per-artifact cap.** The sum of canonical JSON serialization sizes across
   every stage's `content` field in a single artifact's `commit_chain` MUST
   NOT exceed **4,194,304 bytes (4 MiB)**.

Both bounds are measured in bytes of the canonical serialization, not in
source-text bytes or Unicode code points. The serialization rules are the
same as those used for III hashing in §2.2.

Verifiers MUST include the stable reason code `PREIMAGE_OVERSIZED` in their
per-verdict reasons output when emitting `CONDUCT_INVALID` for a D6
violation, to distinguish the size-cap rejection from generic D5 / CC1
preimage-missing rejections.

D6 does NOT introduce a new top-level status token. The Class D status
registry remains `{CONDUCT_VALID, CONDUCT_INVALID}` (`STATUS-REGISTRY.md`).

**Threat model entry T-D6-1 (DoS via unbounded preimage):**

Without D6, a producer can attach a preimage of arbitrary size (e.g. an
entire LLM context window) to a single stage, forcing every conformant
verifier to materialize, canonicalize, and hash it. The verifier has no
spec authority to reject on size, so it must either exhaust memory or
violate D5. D6 removes this surface by giving the verifier explicit
authority to reject oversized preimages while still honoring the preimage
requirement.
```

---

End of proposed patch.
