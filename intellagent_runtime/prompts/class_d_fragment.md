Class D conduct artifact (interpretive governance). The `object_added` shape:

```json
{
  "class":  "D",
  "regime": "interpretive_governance",
  "claim":  "<short prose>",
  "values_frame": {
    "optimizing_for":     ["<value>"],
    "not_optimizing_for": ["<value>"]
  },
  "alternatives":      [{"id": "alt-1", "summary": "<text>"}],
  "challenge_surface": [{"id": "ch-1", "argument": "<text>"}],
  "commit_chain": [
    {
      "stage":      1,
      "name":       "values_frame_commit",
      "hash":       "sha256:<64 lowercase hex>",
      "content":    {"<preimage>": "<value>"},
      "depends_on": null,
      "created_at": "<ISO-8601 UTC>"
    }
  ],
  "status": "CONDUCT_VALID" | "CONDUCT_INVALID"
}
```

Hard rules (the kernel will reject if violated):

- D2: `alternatives` MUST be non-empty.
- D3: `challenge_surface` MUST be non-empty.
- D4: `status` MUST NEVER be `VERIFIED` for Class D.
- D5 / CC1: every `commit_chain` stage MUST include preimage `content`
  (never `null`).
- CC2: `stage[i].depends_on` MUST equal the prior stage's `hash`; stage 1
  MUST have `depends_on: null`.
