# Disagreement signature 11

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-U+2028`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-U+2028

**Length pattern:** longest:go,shortest:python

**By generator:**
  - unicode_string: 1

## Examples

### Example 1

- generator: `unicode_string`
- input: `"﻿ "`

Canonical per implementation:
- **python** (len 8, sha 50b876fe4ff4d35d...):

  ```
  "﻿ "
  ```
- **go** (len 11, sha 6c2d86ae6e0e8a3d...):

  ```
  "﻿\u2028"
  ```
- **rust** (len 8, sha 50b876fe4ff4d35d...):

  ```
  "﻿ "
  ```
