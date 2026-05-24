# Disagreement signature 52

**Signature:** `agree:go+python|outlier:rust | longest:rust,shortest:python | markers:contains-C0-control,contains-C1-control,contains-bigint>2^53,contains-bigint>=2^64,contains-bigint>i64,contains-emoji`

**Count:** 1

**Partition:** agree:go+python|outlier:rust

**Outlier:** rust

**Markers:** contains-C0-control, contains-C1-control, contains-bigint>2^53, contains-bigint>=2^64, contains-bigint>i64, contains-emoji

**Length pattern:** longest:rust,shortest:python

**By generator:**
  - array_order: 1

## Examples

### Example 1

- generator: `array_order`
- input: `[3.14159, 42, 18446744073709551616, "\u0007Āÿÿ😀>", 19, -23]`

Canonical per implementation:
- **python** (len 62, sha 3bdce6ea23db9fe7...):

  ```
  [3.14159,42,18446744073709551616,"\u0007Āÿÿ😀>",19,-23]
  ```
- **go** (len 62, sha 3bdce6ea23db9fe7...):

  ```
  [3.14159,42,18446744073709551616,"\u0007Āÿÿ😀>",19,-23]
  ```
- **rust** (len 64, sha 98af9b3251b9b5a7...):

  ```
  [3.14159,42,1.8446744073709552e+19,"\u0007Āÿÿ😀>",19,-23]
  ```
