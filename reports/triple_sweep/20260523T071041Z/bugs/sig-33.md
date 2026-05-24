# Disagreement signature 33

**Signature:** `all-three-different | longest:go,shortest:python | markers:contains-C0-control,contains-U+2028,contains-bigint>2^53,contains-bigint>=2^64,contains-bigint>i64`

**Count:** 1

**Partition:** all-three-different

**Outlier:** all-three-different

**Markers:** contains-C0-control, contains-U+2028, contains-bigint>2^53, contains-bigint>=2^64, contains-bigint>i64

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 1

## Examples

### Example 1

- generator: `nested`
- input: `{"&": [0.2, 18446744073709551616, "￿\u0000��& "], "tag": 0}`

Canonical per implementation:
- **python** (len 62, sha cdbb827d996179db...):

  ```
  {"&":[0.2,18446744073709551616,"￿\u0000��& "],"tag":0}
  ```
- **go** (len 65, sha 013b92a77a8e0078...):

  ```
  {"&":[0.2,18446744073709551616,"￿\u0000��&\u2028"],"tag":0}
  ```
- **rust** (len 64, sha da9a79a122b891db...):

  ```
  {"&":[0.2,1.8446744073709552e+19,"￿\u0000��& "],"tag":0}
  ```
