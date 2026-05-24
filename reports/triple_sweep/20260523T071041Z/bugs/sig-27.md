# Disagreement signature 27

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
- input: `" �ࠀ﻿�\""`

Canonical per implementation:
- **python** (len 19, sha e95c3f6d1b9fef4e...):

  ```
  " �ࠀ﻿�\""
  ```
- **go** (len 22, sha a39e4784979104fd...):

  ```
  "\u2028�ࠀ﻿�\""
  ```
- **rust** (len 19, sha e95c3f6d1b9fef4e...):

  ```
  " �ࠀ﻿�\""
  ```
