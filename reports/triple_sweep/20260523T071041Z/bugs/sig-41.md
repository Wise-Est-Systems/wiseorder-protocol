# Disagreement signature 41

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C1-control,contains-SMP,contains-U+2028,contains-bigint>2^53`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C1-control, contains-SMP, contains-U+2028, contains-bigint>2^53

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 1

## Examples

### Example 1

- generator: `nested`
- input: `[{"􏿿߿  ": [0.3333333333333333, 0.30000000000000004, "\"\"�􏿿 ÿ"], "tag": 3}, -9223372036854775808, "\"߿"]`

Canonical per implementation:
- **python** (len 114, sha 2130b41caae32ff0...):

  ```
  [{"tag":3,"􏿿߿  ":[0.3333333333333333,0.30000000000000004,"\"\"�􏿿 ÿ"]},-9223372036854775808,"\"߿"]
  ```
- **go** (len 120, sha 23c446caa49b005a...):

  ```
  [{"tag":3,"􏿿߿\u2028\u2028":[0.3333333333333333,0.30000000000000004,"\"\"�􏿿 ÿ"]},-9223372036854775808,"\"߿"]
  ```
- **rust** (len 114, sha 2130b41caae32ff0...):

  ```
  [{"tag":3,"􏿿߿  ":[0.3333333333333333,0.30000000000000004,"\"\"�􏿿 ÿ"]},-9223372036854775808,"\"߿"]
  ```
