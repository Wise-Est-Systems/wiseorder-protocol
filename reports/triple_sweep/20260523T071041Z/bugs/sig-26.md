# Disagreement signature 26

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-C1-control,contains-U+2028`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-C1-control, contains-U+2028

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 1

## Examples

### Example 1

- generator: `nested`
- input: `[[{"\\� / ߿": [0.30000000000000004, 0.1, "ÿ\u001f\u0000ÿ "], "tag": 2}, -2.5, "<߿>߿"], 10000000000.0, "\"\u0000"]`

Canonical per implementation:
- **python** (len 117, sha 68b7efaf8cda4ab6...):

  ```
  [[{"\\� / ߿":[0.30000000000000004,0.1,"ÿ\u001f\u0000ÿ "],"tag":2},-2.5,"<߿>߿"],10000000000.0,"\"\u0000"]
  ```
- **go** (len 123, sha bbd0992a0320952f...):

  ```
  [[{"\\� /\u2028߿":[0.30000000000000004,0.1,"ÿ\u001f\u0000ÿ\u2028"],"tag":2},-2.5,"<߿>߿"],10000000000.0,"\"\u0000"]
  ```
- **rust** (len 117, sha 68b7efaf8cda4ab6...):

  ```
  [[{"\\� / ߿":[0.30000000000000004,0.1,"ÿ\u001f\u0000ÿ "],"tag":2},-2.5,"<߿>߿"],10000000000.0,"\"\u0000"]
  ```
