# Disagreement signature 43

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-DEL,contains-U+2028`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-DEL, contains-U+2028

**Length pattern:** longest:go,shortest:python

**By generator:**
  - unicode_string: 1

## Examples

### Example 1

- generator: `unicode_string`
- input: `"﻿ /"`

Canonical per implementation:
- **python** (len 10, sha 18972e10a0101cd9...):

  ```
  "﻿ /"
  ```
- **go** (len 13, sha 6ec03a30b33a6ec8...):

  ```
  "﻿\u2028/"
  ```
- **rust** (len 10, sha 18972e10a0101cd9...):

  ```
  "﻿ /"
  ```
