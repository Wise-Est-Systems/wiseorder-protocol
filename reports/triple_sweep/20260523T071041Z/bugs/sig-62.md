# Disagreement signature 62

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-C1-control,contains-SMP,contains-U+2028,contains-bigint>2^53`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-C1-control, contains-SMP, contains-U+2028, contains-bigint>2^53

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 1

## Examples

### Example 1

- generator: `nested`
- input: `[{"�￿& ": {"\u0000": 0, "tag": 6}, "tag": 7}, 9007199254740993, "￿\u0000>ࠀ￿￿􏿿"]`

Canonical per implementation:
- **python** (len 90, sha a4d3a4a982775bd7...):

  ```
  [{"tag":7,"�￿& ":{"\u0000":0,"tag":6}},9007199254740993,"￿\u0000>ࠀ￿￿􏿿"]
  ```
- **go** (len 93, sha c98186d9d9aae514...):

  ```
  [{"tag":7,"�￿&\u2028":{"\u0000":0,"tag":6}},9007199254740993,"￿\u0000>ࠀ￿￿􏿿"]
  ```
- **rust** (len 90, sha a4d3a4a982775bd7...):

  ```
  [{"tag":7,"�￿& ":{"\u0000":0,"tag":6}},9007199254740993,"￿\u0000>ࠀ￿￿􏿿"]
  ```
