# Disagreement signature 30

**Signature:** `agree:go+python|outlier:rust | longest:rust,shortest:python | markers:contains-BOM,contains-C1-control,contains-SMP,contains-bigint>2^53,contains-bigint>=2^64,contains-bigint>i64`

**Count:** 1

**Partition:** agree:go+python|outlier:rust

**Outlier:** rust

**Markers:** contains-BOM, contains-C1-control, contains-SMP, contains-bigint>2^53, contains-bigint>=2^64, contains-bigint>i64

**Length pattern:** longest:rust,shortest:python

**By generator:**
  - nested: 1

## Examples

### Example 1

- generator: `nested`
- input: `[{"�𐀀": {"//﻿ࠀ": 18446744073709551616, "tag": 9}, "tag": 0}, 10000000000.0, "ࠀ"]`

Canonical per implementation:
- **python** (len 87, sha a0f54e639715370f...):

  ```
  [{"tag":0,"�𐀀":{"//﻿ࠀ":18446744073709551616,"tag":9}},10000000000.0,"ࠀ"]
  ```
- **go** (len 87, sha a0f54e639715370f...):

  ```
  [{"tag":0,"�𐀀":{"//﻿ࠀ":18446744073709551616,"tag":9}},10000000000.0,"ࠀ"]
  ```
- **rust** (len 89, sha 5e986af87a5da6cd...):

  ```
  [{"tag":0,"�𐀀":{"//﻿ࠀ":1.8446744073709552e+19,"tag":9}},10000000000.0,"ࠀ"]
  ```
