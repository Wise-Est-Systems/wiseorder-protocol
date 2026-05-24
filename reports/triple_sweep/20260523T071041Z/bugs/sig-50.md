# Disagreement signature 50

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-SMP,contains-U+2028`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-SMP, contains-U+2028

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"􏿿￿": 207, "&<<߿": 10, " < >": 864, "﻿\">>": 105}`

Canonical per implementation:
- **python** (len 53, sha c011c3e883d74df0...):

  ```
  {" < >":864,"&<<߿":10,"﻿\">>":105,"􏿿￿":207}
  ```
- **go** (len 56, sha 53c8b1b1a9b6b0d5...):

  ```
  {" <\u2028>":864,"&<<߿":10,"﻿\">>":105,"􏿿￿":207}
  ```
- **rust** (len 53, sha c011c3e883d74df0...):

  ```
  {" < >":864,"&<<߿":10,"﻿\">>":105,"􏿿￿":207}
  ```
