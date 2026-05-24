# Disagreement signature 12

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-C1-control,contains-U+2028`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-C1-control, contains-U+2028

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{" �￿ \u0007": 294, "߿": -221}`

Canonical per implementation:
- **python** (len 36, sha 8265bc7ec1c87686...):

  ```
  {"߿":-221," �￿ \u0007":294}
  ```
- **go** (len 39, sha 7bffc4c093b7f352...):

  ```
  {"߿":-221,"\u2028�￿ \u0007":294}
  ```
- **rust** (len 36, sha 8265bc7ec1c87686...):

  ```
  {"߿":-221," �￿ \u0007":294}
  ```
