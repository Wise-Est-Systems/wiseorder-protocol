# Disagreement signature 71

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-U+2028`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-U+2028

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 1

## Examples

### Example 1

- generator: `nested`
- input: `{"￿Āÿ\u0007\u0007 &": [{"�￿ࠀ/ ": 0, "tag": 7}, 0.001, "﻿"], "tag": 3}`

Canonical per implementation:
- **python** (len 75, sha 57c85bd710971e2a...):

  ```
  {"tag":3,"￿Āÿ\u0007\u0007 &":[{"tag":7,"�￿ࠀ/ ":0},0.001,"﻿"]}
  ```
- **go** (len 78, sha c1a0b656d817e79c...):

  ```
  {"tag":3,"￿Āÿ\u0007\u0007 &":[{"tag":7,"�￿ࠀ/\u2028":0},0.001,"﻿"]}
  ```
- **rust** (len 75, sha 57c85bd710971e2a...):

  ```
  {"tag":3,"￿Āÿ\u0007\u0007 &":[{"tag":7,"�￿ࠀ/ ":0},0.001,"﻿"]}
  ```
