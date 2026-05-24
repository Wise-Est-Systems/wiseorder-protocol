# Disagreement signature 83

**Signature:** `all-three-different | longest:go,shortest:python | markers:contains-C0-control,contains-C1-control,contains-U+2029,contains-bigint>2^53,contains-bigint>=2^64,contains-bigint>i64`

**Count:** 1

**Partition:** all-three-different

**Outlier:** all-three-different

**Markers:** contains-C0-control, contains-C1-control, contains-U+2029, contains-bigint>2^53, contains-bigint>=2^64, contains-bigint>i64

**Length pattern:** longest:go,shortest:python

**By generator:**
  - mixed_object: 1

## Examples

### Example 1

- generator: `mixed_object`
- input: `{"k1": "߿\u001f� &", "k4": [1000000000000000.0], "k2": [3.14159, 0.3333333333333333, 1], "k3": 3.141592653589793, "k0": {"nk0": 18446744073709551616}}`

Canonical per implementation:
- **python** (len 147, sha 78408d5bc3d21208...):

  ```
  {"k0":{"nk0":18446744073709551616},"k1":"߿\u001f� &","k2":[3.14159,0.3333333333333333,1],"k3":3.141592653589793,"k4":[1000000000000000.0]}
  ```
- **go** (len 150, sha 4011b41c6125a5dd...):

  ```
  {"k0":{"nk0":18446744073709551616},"k1":"߿\u001f�\u2029&","k2":[3.14159,0.3333333333333333,1],"k3":3.141592653589793,"k4":[1000000000000000.0]}
  ```
- **rust** (len 149, sha 96b4a8ef4b97faa6...):

  ```
  {"k0":{"nk0":1.8446744073709552e+19},"k1":"߿\u001f� &","k2":[3.14159,0.3333333333333333,1],"k3":3.141592653589793,"k4":[1000000000000000.0]}
  ```
