# Disagreement signature 26

**Signature:** `agree:go+python|outlier:rust | longest:rust,shortest:python | markers:contains-C0-control,contains-bigint>2^53,contains-bigint>=2^64,contains-bigint>i64`

**Count:** 1

**Partition:** agree:go+python|outlier:rust

**Outlier:** rust

**Markers:** contains-C0-control, contains-bigint>2^53, contains-bigint>=2^64, contains-bigint>i64

**Length pattern:** longest:rust,shortest:python

**By generator:**
  - nested: 1

## Examples

### Example 1

- generator: `nested`
- input: `[[{"\"ࠀࠀ\u0007": 9007199254740993, "tag": 0}, 18446744073709551616, "ࠀ\u0007\u0007"], 0.1, "/>\u001f"]`

Canonical per implementation:
- **python** (len 101, sha ea6a220f8e04ee79...):

  ```
  [[{"\"ࠀࠀ\u0007":9007199254740993,"tag":0},18446744073709551616,"ࠀ\u0007\u0007"],0.1,"/>\u001f"]
  ```
- **go** (len 101, sha ea6a220f8e04ee79...):

  ```
  [[{"\"ࠀࠀ\u0007":9007199254740993,"tag":0},18446744073709551616,"ࠀ\u0007\u0007"],0.1,"/>\u001f"]
  ```
- **rust** (len 103, sha 5222a76924556bcf...):

  ```
  [[{"\"ࠀࠀ\u0007":9007199254740993,"tag":0},1.8446744073709552e+19,"ࠀ\u0007\u0007"],0.1,"/>\u001f"]
  ```
