# Disagreement signature 4

**Signature:** `agree:go+python|outlier:rust | longest:rust,shortest:python | markers:contains-bigint>2^53,contains-bigint>=2^64,contains-bigint>i64`

**Count:** 4

**Partition:** agree:go+python|outlier:rust

**Outlier:** rust

**Markers:** contains-bigint>2^53, contains-bigint>=2^64, contains-bigint>i64

**Length pattern:** longest:rust,shortest:python

**By generator:**
  - mixed_object: 2
  - array_order: 2

## Examples

### Example 1

- generator: `mixed_object`
- input: `{"k1": 0, "k2": 9007199254740993, "k0": {"nk0": 1e+17, "nk1": 1000000000000000.0, "nk2": 0.30000000000000004}, "k3": 18446744073709551616}`

Canonical per implementation:
- **python** (len 126, sha 65c6b95c4c009c24...):

  ```
  {"k0":{"nk0":1e+17,"nk1":1000000000000000.0,"nk2":0.30000000000000004},"k1":0,"k2":9007199254740993,"k3":18446744073709551616}
  ```
- **go** (len 126, sha 65c6b95c4c009c24...):

  ```
  {"k0":{"nk0":1e+17,"nk1":1000000000000000.0,"nk2":0.30000000000000004},"k1":0,"k2":9007199254740993,"k3":18446744073709551616}
  ```
- **rust** (len 128, sha 4edd8c20ec45f1e8...):

  ```
  {"k0":{"nk0":1e+17,"nk1":1000000000000000.0,"nk2":0.30000000000000004},"k1":0,"k2":9007199254740993,"k3":1.8446744073709552e+19}
  ```

### Example 2

- generator: `array_order`
- input: `[-36, 18446744073709551616]`

Canonical per implementation:
- **python** (len 26, sha 132209658996372a...):

  ```
  [-36,18446744073709551616]
  ```
- **go** (len 26, sha 132209658996372a...):

  ```
  [-36,18446744073709551616]
  ```
- **rust** (len 28, sha 9c4ffe71ad1588ca...):

  ```
  [-36,1.8446744073709552e+19]
  ```

### Example 3

- generator: `mixed_object`
- input: `{"k0": [], "k4": null, "k3": [9007199254740993, -2.5, 18446744073709551616, -1], "k5": null, "k1": {"nk0": -2.5, "nk1": 0.001}, "k2": []}`

Canonical per implementation:
- **python** (len 120, sha 63cd898ca9f5d57d...):

  ```
  {"k0":[],"k1":{"nk0":-2.5,"nk1":0.001},"k2":[],"k3":[9007199254740993,-2.5,18446744073709551616,-1],"k4":null,"k5":null}
  ```
- **go** (len 120, sha 63cd898ca9f5d57d...):

  ```
  {"k0":[],"k1":{"nk0":-2.5,"nk1":0.001},"k2":[],"k3":[9007199254740993,-2.5,18446744073709551616,-1],"k4":null,"k5":null}
  ```
- **rust** (len 122, sha 430e4f85adbda856...):

  ```
  {"k0":[],"k1":{"nk0":-2.5,"nk1":0.001},"k2":[],"k3":[9007199254740993,-2.5,1.8446744073709552e+19,-1],"k4":null,"k5":null}
  ```
