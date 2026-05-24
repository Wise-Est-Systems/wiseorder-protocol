# Disagreement signature 32

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-DEL,contains-U+2028,contains-bigint>2^53`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-DEL, contains-U+2028, contains-bigint>2^53

**Length pattern:** longest:go,shortest:python

**By generator:**
  - mixed_object: 1

## Examples

### Example 1

- generator: `mixed_object`
- input: `{"k1": {"nk0": 9223372036854775807}, "k0": " Ā߿", "k3": {"nk0": 1e+100}, "k2": null, "k5": 0.001, "k4": 2147483647}`

Canonical per implementation:
- **python** (len 107, sha 0d5a9b2fba0a43a2...):

  ```
  {"k0":" Ā߿","k1":{"nk0":9223372036854775807},"k2":null,"k3":{"nk0":1e+100},"k4":2147483647,"k5":0.001}
  ```
- **go** (len 110, sha 940258e1901263a0...):

  ```
  {"k0":"\u2028Ā߿","k1":{"nk0":9223372036854775807},"k2":null,"k3":{"nk0":1e+100},"k4":2147483647,"k5":0.001}
  ```
- **rust** (len 107, sha 0d5a9b2fba0a43a2...):

  ```
  {"k0":" Ā߿","k1":{"nk0":9223372036854775807},"k2":null,"k3":{"nk0":1e+100},"k4":2147483647,"k5":0.001}
  ```
