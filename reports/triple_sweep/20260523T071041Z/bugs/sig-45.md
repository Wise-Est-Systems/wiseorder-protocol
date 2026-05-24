# Disagreement signature 45

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-U+2029,contains-emoji`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-U+2029, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - array_order: 1

## Examples

### Example 1

- generator: `array_order`
- input: `[" ￿", "﻿😀"]`

Canonical per implementation:
- **python** (len 20, sha 521322ccddb654ab...):

  ```
  [" ￿","﻿😀"]
  ```
- **go** (len 23, sha 475e0a903aad76f1...):

  ```
  ["\u2029￿","﻿😀"]
  ```
- **rust** (len 20, sha 521322ccddb654ab...):

  ```
  [" ￿","﻿😀"]
  ```
