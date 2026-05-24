# Disagreement signature 44

**Signature:** `all-three-different | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-DEL,contains-SMP,contains-U+2029,contains-bigint>2^53,contains-bigint>=2^64,contains-bigint>i64`

**Count:** 1

**Partition:** all-three-different

**Outlier:** all-three-different

**Markers:** contains-BOM, contains-C0-control, contains-DEL, contains-SMP, contains-U+2029, contains-bigint>2^53, contains-bigint>=2^64, contains-bigint>i64

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 1

## Examples

### Example 1

- generator: `nested`
- input: `[[{"\u001fĀ�&﻿": {"\u001f߿\u0007": {"𐀀\u0007 >�": 18446744073709551616, "tag": 0}, "tag": 0}, "tag": 1}, 1e+16, "􏿿\\�\u001f &"], 0.001, " ࠀ\\\u001f"]`

Canonical per implementation:
- **python** (len 158, sha 5489f24c4064f7d0...):

  ```
  [[{"\u001fĀ�&﻿":{"\u001f߿\u0007":{"tag":0,"𐀀\u0007 >�":18446744073709551616},"tag":0},"tag":1},1e+16,"􏿿\\�\u001f &"],0.001," ࠀ\\\u001f"]
  ```
- **go** (len 161, sha cdc884d892b9dd6b...):

  ```
  [[{"\u001fĀ�&﻿":{"\u001f߿\u0007":{"tag":0,"𐀀\u0007 >�":18446744073709551616},"tag":0},"tag":1},1e+16,"􏿿\\�\u001f\u2029&"],0.001," ࠀ\\\u001f"]
  ```
- **rust** (len 160, sha 4d937c05c414cdd2...):

  ```
  [[{"\u001fĀ�&﻿":{"\u001f߿\u0007":{"tag":0,"𐀀\u0007 >�":1.8446744073709552e+19},"tag":0},"tag":1},1e+16,"􏿿\\�\u001f &"],0.001," ࠀ\\\u001f"]
  ```
