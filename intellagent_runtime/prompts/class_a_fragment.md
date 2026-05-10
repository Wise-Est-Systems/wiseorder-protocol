Class A artifact (deterministic verification). The `object_added` shape:

```json
{
  "class":            "A",
  "regime":           "deterministic_verification",
  "claim":            "<short prose>",
  "canonicalization": "RFC8785-JCS",
  "algorithm":        "SHA-256",
  "expected_digest":  "sha256:<64 lowercase hex>",
  "observed_digest":  "sha256:<64 lowercase hex>",
  "status":           "VERIFIED" | "TAMPERED" | "INVALID",
  "provenance":       {"witness": "<name>", "at": "<ISO-8601 UTC>"}
}
```

Hard rules (the kernel will reject if violated):

- `canonicalization` MUST be exactly `RFC8785-JCS` under v0.1.0; any other
  value forces `INVALID`.
- `VERIFIED` requires `expected_digest == observed_digest`.
- `TAMPERED` requires `expected_digest != observed_digest`.
- `status` MUST NOT be a telemetry token (`CALIBRATION_IMPROVED`,
  `CALIBRATION_DEGRADED`).
