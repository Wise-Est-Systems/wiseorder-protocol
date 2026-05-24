# Disagreement signature 49

**Signature:** `all-three-different | longest:go,shortest:python | markers:contains-C0-control,contains-DEL,contains-SMP,contains-U+2029,contains-bigint>2^53,contains-bigint>=2^64,contains-bigint>i64`

**Count:** 1

**Partition:** all-three-different

**Outlier:** all-three-different

**Markers:** contains-C0-control, contains-DEL, contains-SMP, contains-U+2029, contains-bigint>2^53, contains-bigint>=2^64, contains-bigint>i64

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 1

## Examples

### Example 1

- generator: `nested`
- input: `{" \u001f\u0000": {"�𐀀￿": [{"􏿿\u0007\u001f Ā": -1, "tag": 4}, 18446744073709551616, "\"߿>߿"], "tag": 0}, "tag": 7}`

Canonical per implementation:
- **python** (len 120, sha e5894c36ff3ff692...):

  ```
  {"tag":7," \u001f\u0000":{"tag":0,"�𐀀￿":[{"tag":4,"􏿿\u0007\u001f Ā":-1},18446744073709551616,"\"߿>߿"]}}
  ```
- **go** (len 123, sha aac281d9a448dc75...):

  ```
  {"tag":7,"\u2029\u001f\u0000":{"tag":0,"�𐀀￿":[{"tag":4,"􏿿\u0007\u001f Ā":-1},18446744073709551616,"\"߿>߿"]}}
  ```
- **rust** (len 122, sha 11b7de5c890d9ddd...):

  ```
  {"tag":7," \u001f\u0000":{"tag":0,"�𐀀￿":[{"tag":4,"􏿿\u0007\u001f Ā":-1},1.8446744073709552e+19,"\"߿>߿"]}}
  ```
