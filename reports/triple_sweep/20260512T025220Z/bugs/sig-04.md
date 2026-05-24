# Disagreement signature 4

**Signature:** `all-three-different | longest:go,shortest:python | markers:contains-U+2028,contains-bigint>2^53,contains-bigint>=2^64,contains-bigint>i64,contains-emoji`

**Count:** 1

**Partition:** all-three-different

**Outlier:** all-three-different

**Markers:** contains-U+2028, contains-bigint>2^53, contains-bigint>=2^64, contains-bigint>i64, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - mixed_object: 1

## Examples

### Example 1

- generator: `mixed_object`
- input: `{"k3": 18446744073709551616, "k0": null, "k1": [9223372036854775807], "k2": " 😀"}`

Canonical per implementation:
- **python** (len 79, sha a37298f4b4030e07...):

  ```
  {"k0":null,"k1":[9223372036854775807],"k2":" 😀","k3":18446744073709551616}
  ```
- **go** (len 82, sha 3527565e004d848f...):

  ```
  {"k0":null,"k1":[9223372036854775807],"k2":"\u2028😀","k3":18446744073709551616}
  ```
- **rust** (len 81, sha 812f0829d3fc919e...):

  ```
  {"k0":null,"k1":[9223372036854775807],"k2":" 😀","k3":1.8446744073709552e+19}
  ```
