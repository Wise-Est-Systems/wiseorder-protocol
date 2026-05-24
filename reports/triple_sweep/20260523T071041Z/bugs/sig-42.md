# Disagreement signature 42

**Signature:** `agree:go+python|outlier:rust | longest:rust,shortest:python | markers:contains-SMP,contains-bigint>2^53,contains-bigint>=2^64,contains-bigint>i64,contains-emoji`

**Count:** 1

**Partition:** agree:go+python|outlier:rust

**Outlier:** rust

**Markers:** contains-SMP, contains-bigint>2^53, contains-bigint>=2^64, contains-bigint>i64, contains-emoji

**Length pattern:** longest:rust,shortest:python

**By generator:**
  - array_order: 1

## Examples

### Example 1

- generator: `array_order`
- input: `[18446744073709551616, 99, "😀>&𐀀"]`

Canonical per implementation:
- **python** (len 38, sha 1be6cc134e4eadb0...):

  ```
  [18446744073709551616,99,"😀>&𐀀"]
  ```
- **go** (len 38, sha 1be6cc134e4eadb0...):

  ```
  [18446744073709551616,99,"😀>&𐀀"]
  ```
- **rust** (len 40, sha b53c43fddb9e6b3d...):

  ```
  [1.8446744073709552e+19,99,"😀>&𐀀"]
  ```
