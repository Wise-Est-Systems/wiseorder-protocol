Class C artifact (protocol-bound consensus). The `object_added` shape:

```json
{
  "class":  "C",
  "regime": "protocol_bound_consensus",
  "claim":  "<short prose>",
  "protocol": {
    "name":               "<protocol name>",
    "version":            "<version>",
    "required_quorum":    2,
    "eligible_attesters": ["<attester id>"]
  },
  "evidence": [
    {"attester_id": "<id>", "attestation": "approve|reject", "eligible": true}
  ],
  "action_policy": {
    "action_allowed":      false,
    "action_compelled":    false,
    "reason":              "<text>",
    "authorization_source": null
  },
  "status": "CONSENSUS_PENDING" | "CONSENSUS_VALID" | "CONSENSUS_FAILED" | "INVALID"
}
```

Hard rules (the kernel will reject if violated):

- Any attester not in `eligible_attesters` forces `status: INVALID` (C2).
- `action_policy.action_allowed: true` REQUIRES a non-null
  `authorization_source` (AG1, AG3). Consensus is not authorization.
- `status` MUST NOT be a telemetry token.
