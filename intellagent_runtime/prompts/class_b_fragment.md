Class B artifact (instrumented empirical verification). The `object_added` shape:

```json
{
  "class":           "B",
  "regime":          "instrumented_empirical_verification",
  "claim":           "<short prose>",
  "sources":         [{"id": "<source id>", "kind": "<log|tsa|...>", "uri": "<uri>"}],
  "timestamps":      [{"source_id": "<id>", "value": "<ISO-8601 UTC>"}],
  "observations":    [{"source_id": "<id>", "result": "<text>", "supports_claim": true}],
  "structural_diff": { "byte": {"size_match": true, "digest_match": true} },
  "status":          "SUPPORTED" | "CONFLICTED" | "INSUFFICIENT_EVIDENCE" | "INVALID"
}
```

Hard rules (the kernel will reject if violated):

- `CONFLICTED` requires both a `supports_claim: true` and a
  `supports_claim: false` observation preserved in `observations`.
- All declared `sources` SHOULD appear in `observations` and `timestamps`
  (auditable ordering).
- `status` MUST NOT be a telemetry token.
