# Disagreement signature 28

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-DEL,contains-SMP,contains-U+2028`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-DEL, contains-SMP, contains-U+2028

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 1

## Examples

### Example 1

- generator: `nested`
- input: `{"﻿Ā￿": {"﻿  >𐀀􏿿": 0.1, "tag": 9}, "tag": 4}`

Canonical per implementation:
- **python** (len 54, sha 8e5ccafbbb70d81f...):

  ```
  {"tag":4,"﻿Ā￿":{"tag":9,"﻿  >𐀀􏿿":0.1}}
  ```
- **go** (len 57, sha 34647c1c147aa4c0...):

  ```
  {"tag":4,"﻿Ā￿":{"tag":9,"﻿ \u2028>𐀀􏿿":0.1}}
  ```
- **rust** (len 54, sha 8e5ccafbbb70d81f...):

  ```
  {"tag":4,"﻿Ā￿":{"tag":9,"﻿  >𐀀􏿿":0.1}}
  ```
