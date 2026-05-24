# Disagreement signature 84

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-C1-control,contains-U+2028,contains-U+2029`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-C1-control, contains-U+2028, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 1

## Examples

### Example 1

- generator: `nested`
- input: `[{"&  ߿￿": [[0.2, 0.2, " Ā\\﻿ÿ\u0000"], -2.5, "�\""], "tag": 0}, 0.0, "\"\u001f�&"]`

Canonical per implementation:
- **python** (len 93, sha 17fed040ec8f2bba...):

  ```
  [{"&  ߿￿":[[0.2,0.2," Ā\\﻿ÿ\u0000"],-2.5,"�\""],"tag":0},0.0,"\"\u001f�&"]
  ```
- **go** (len 99, sha 617d6ad4c5462d7a...):

  ```
  [{"& \u2029߿￿":[[0.2,0.2,"\u2028Ā\\﻿ÿ\u0000"],-2.5,"�\""],"tag":0},0.0,"\"\u001f�&"]
  ```
- **rust** (len 93, sha 17fed040ec8f2bba...):

  ```
  [{"&  ߿￿":[[0.2,0.2," Ā\\﻿ÿ\u0000"],-2.5,"�\""],"tag":0},0.0,"\"\u001f�&"]
  ```
