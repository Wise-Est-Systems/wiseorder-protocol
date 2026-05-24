# Disagreement signature 96

**Signature:** `agree:go+python|outlier:rust | longest:rust,shortest:python | markers:contains-C0-control,contains-SMP,contains-bigint>2^53,contains-bigint>=2^64,contains-bigint>i64`

**Count:** 1

**Partition:** agree:go+python|outlier:rust

**Outlier:** rust

**Markers:** contains-C0-control, contains-SMP, contains-bigint>2^53, contains-bigint>=2^64, contains-bigint>i64

**Length pattern:** longest:rust,shortest:python

**By generator:**
  - mixed_object: 1

## Examples

### Example 1

- generator: `mixed_object`
- input: `{"k3": "\u001f𐀀", "k0": {"nk0": 5e-324, "nk1": 5e-324, "nk2": 18446744073709551616}, "k1": [1e-100, 1e-100, 0.2], "k2": [2.2250738585072014e-308]}`

Canonical per implementation:
- **python** (len 135, sha 669270687debb0cf...):

  ```
  {"k0":{"nk0":5e-324,"nk1":5e-324,"nk2":18446744073709551616},"k1":[1e-100,1e-100,0.2],"k2":[2.2250738585072014e-308],"k3":"\u001f𐀀"}
  ```
- **go** (len 135, sha 669270687debb0cf...):

  ```
  {"k0":{"nk0":5e-324,"nk1":5e-324,"nk2":18446744073709551616},"k1":[1e-100,1e-100,0.2],"k2":[2.2250738585072014e-308],"k3":"\u001f𐀀"}
  ```
- **rust** (len 137, sha 26c4abe007b10899...):

  ```
  {"k0":{"nk0":5e-324,"nk1":5e-324,"nk2":1.8446744073709552e+19},"k1":[1e-100,1e-100,0.2],"k2":[2.2250738585072014e-308],"k3":"\u001f𐀀"}
  ```
