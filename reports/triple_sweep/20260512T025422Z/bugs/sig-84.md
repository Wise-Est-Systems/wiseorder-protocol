# Disagreement signature 84

**Signature:** `agree:go+python|outlier:rust | longest:rust,shortest:python | markers:contains-C0-control,contains-SMP,contains-bigint>2^53,contains-bigint>=2^64,contains-bigint>i64`

**Count:** 6

**Partition:** agree:go+python|outlier:rust

**Outlier:** rust

**Markers:** contains-C0-control, contains-SMP, contains-bigint>2^53, contains-bigint>=2^64, contains-bigint>i64

**Length pattern:** longest:rust,shortest:python

**By generator:**
  - mixed_object: 3
  - array_order: 2
  - nested: 1

## Examples

### Example 1

- generator: `array_order`
- input: `[-47, 18446744073709551616, "\u0000􏿿ࠀ<<"]`

Canonical per implementation:
- **python** (len 44, sha 1b4aaa645c155c9b...):

  ```
  [-47,18446744073709551616,"\u0000􏿿ࠀ<<"]
  ```
- **go** (len 44, sha 1b4aaa645c155c9b...):

  ```
  [-47,18446744073709551616,"\u0000􏿿ࠀ<<"]
  ```
- **rust** (len 46, sha d5d98d0c865ac0b5...):

  ```
  [-47,1.8446744073709552e+19,"\u0000􏿿ࠀ<<"]
  ```

### Example 2

- generator: `mixed_object`
- input: `{"k2": {"nk0": 10000000000.0, "nk1": 18446744073709551616}, "k1": "\u0000𐀀\u0007<", "k0": []}`

Canonical per implementation:
- **python** (len 88, sha e3e083c750ca5442...):

  ```
  {"k0":[],"k1":"\u0000𐀀\u0007<","k2":{"nk0":10000000000.0,"nk1":18446744073709551616}}
  ```
- **go** (len 88, sha e3e083c750ca5442...):

  ```
  {"k0":[],"k1":"\u0000𐀀\u0007<","k2":{"nk0":10000000000.0,"nk1":18446744073709551616}}
  ```
- **rust** (len 90, sha 49880795bf61286a...):

  ```
  {"k0":[],"k1":"\u0000𐀀\u0007<","k2":{"nk0":10000000000.0,"nk1":1.8446744073709552e+19}}
  ```

### Example 3

- generator: `nested`
- input: `[[3.14159, 18446744073709551616, "<"], 0.3333333333333333, "\\ÿ𐀀\u0007&𐀀߿\\"]`

Canonical per implementation:
- **python** (len 81, sha 33af458f0a61943d...):

  ```
  [[3.14159,18446744073709551616,"<"],0.3333333333333333,"\\ÿ𐀀\u0007&𐀀߿\\"]
  ```
- **go** (len 81, sha 33af458f0a61943d...):

  ```
  [[3.14159,18446744073709551616,"<"],0.3333333333333333,"\\ÿ𐀀\u0007&𐀀߿\\"]
  ```
- **rust** (len 83, sha 94de63dc1424aaaf...):

  ```
  [[3.14159,1.8446744073709552e+19,"<"],0.3333333333333333,"\\ÿ𐀀\u0007&𐀀߿\\"]
  ```
