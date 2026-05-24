# Disagreement signature 70

**Signature:** `all-three-different | longest:go,shortest:python | markers:contains-U+2029,contains-bigint>2^53,contains-bigint>=2^64,contains-bigint>i64`

**Count:** 1

**Partition:** all-three-different

**Outlier:** all-three-different

**Markers:** contains-U+2029, contains-bigint>2^53, contains-bigint>=2^64, contains-bigint>i64

**Length pattern:** longest:go,shortest:python

**By generator:**
  - mixed_object: 1

## Examples

### Example 1

- generator: `mixed_object`
- input: `{"k1": [1e+100, 0.2, -1, 0.001], "k2": "\"ࠀ ÿÿ", "k0": {"nk0": 18446744073709551616, "nk1": 2.718281828459045, "nk2": 9007199254740992}}`

Canonical per implementation:
- **python** (len 129, sha 702f1345dcd708a6...):

  ```
  {"k0":{"nk0":18446744073709551616,"nk1":2.718281828459045,"nk2":9007199254740992},"k1":[1e+100,0.2,-1,0.001],"k2":"\"ࠀ ÿÿ"}
  ```
- **go** (len 132, sha 2240d33b8dac3651...):

  ```
  {"k0":{"nk0":18446744073709551616,"nk1":2.718281828459045,"nk2":9007199254740992},"k1":[1e+100,0.2,-1,0.001],"k2":"\"ࠀ\u2029ÿÿ"}
  ```
- **rust** (len 131, sha 7b826bada63d5feb...):

  ```
  {"k0":{"nk0":1.8446744073709552e+19,"nk1":2.718281828459045,"nk2":9007199254740992},"k1":[1e+100,0.2,-1,0.001],"k2":"\"ࠀ ÿÿ"}
  ```
