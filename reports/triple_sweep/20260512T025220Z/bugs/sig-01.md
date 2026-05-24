# Disagreement signature 1

**Signature:** `agree:go+python|outlier:rust | longest:rust,shortest:python | markers:contains-bigint>2^53,contains-bigint>=2^64,contains-bigint>i64`

**Count:** 3

**Partition:** agree:go+python|outlier:rust

**Outlier:** rust

**Markers:** contains-bigint>2^53, contains-bigint>=2^64, contains-bigint>i64

**Length pattern:** longest:rust,shortest:python

**By generator:**
  - number_edge: 2
  - mixed_object: 1

## Examples

### Example 1

- generator: `number_edge`
- input: `18446744073709551616`

Canonical per implementation:
- **python** (len 20, sha 8b292fc2d32f1fd4...):

  ```
  18446744073709551616
  ```
- **go** (len 20, sha 8b292fc2d32f1fd4...):

  ```
  18446744073709551616
  ```
- **rust** (len 22, sha 7e7e9a94b89d2f5e...):

  ```
  1.8446744073709552e+19
  ```

### Example 2

- generator: `number_edge`
- input: `18446744073709551616`

Canonical per implementation:
- **python** (len 20, sha 8b292fc2d32f1fd4...):

  ```
  18446744073709551616
  ```
- **go** (len 20, sha 8b292fc2d32f1fd4...):

  ```
  18446744073709551616
  ```
- **rust** (len 22, sha 7e7e9a94b89d2f5e...):

  ```
  1.8446744073709552e+19
  ```

### Example 3

- generator: `mixed_object`
- input: `{"k0": [], "k2": {}, "k3": true, "k4": [5e-324, 0, 1e-100], "k1": 18446744073709551616}`

Canonical per implementation:
- **python** (len 76, sha dc3fc2d33ba0611c...):

  ```
  {"k0":[],"k1":18446744073709551616,"k2":{},"k3":true,"k4":[5e-324,0,1e-100]}
  ```
- **go** (len 76, sha dc3fc2d33ba0611c...):

  ```
  {"k0":[],"k1":18446744073709551616,"k2":{},"k3":true,"k4":[5e-324,0,1e-100]}
  ```
- **rust** (len 78, sha f8e8bc1944b0b3fe...):

  ```
  {"k0":[],"k1":1.8446744073709552e+19,"k2":{},"k3":true,"k4":[5e-324,0,1e-100]}
  ```
