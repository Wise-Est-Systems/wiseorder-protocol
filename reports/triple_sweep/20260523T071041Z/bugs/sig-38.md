# Disagreement signature 38

**Signature:** `all-three-different | longest:go,shortest:python | markers:contains-C0-control,contains-C1-control,contains-U+2028,contains-bigint>2^53,contains-bigint>=2^64,contains-bigint>i64`

**Count:** 1

**Partition:** all-three-different

**Outlier:** all-three-different

**Markers:** contains-C0-control, contains-C1-control, contains-U+2028, contains-bigint>2^53, contains-bigint>=2^64, contains-bigint>i64

**Length pattern:** longest:go,shortest:python

**By generator:**
  - array_order: 1

## Examples

### Example 1

- generator: `array_order`
- input: `["߿\u001f<ÿ \u0000", 30, 9007199254740992, 18446744073709551616, "/\u0000"]`

Canonical per implementation:
- **python** (len 79, sha 8a29773c6be8f1ac...):

  ```
  ["߿\u001f<ÿ \u0000",30,9007199254740992,18446744073709551616,"/\u0000"]
  ```
- **go** (len 82, sha c37b64800073de23...):

  ```
  ["߿\u001f<ÿ\u2028\u0000",30,9007199254740992,18446744073709551616,"/\u0000"]
  ```
- **rust** (len 81, sha 0b0092549728193a...):

  ```
  ["߿\u001f<ÿ \u0000",30,9007199254740992,1.8446744073709552e+19,"/\u0000"]
  ```
