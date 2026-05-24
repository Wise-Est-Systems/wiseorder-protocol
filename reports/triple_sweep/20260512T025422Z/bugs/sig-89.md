# Disagreement signature 89

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-DEL,contains-U+2029,contains-emoji`

**Count:** 5

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-DEL, contains-U+2029, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - unicode_string: 2
  - nested: 2
  - object_unicode_keys: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"&߿\u001f ߿ ߿": -604, "😀": 709, " \u0007>\u0007": 72, "߿﻿/�": 358}`

Canonical per implementation:
- **python** (len 76, sha f26849c41a616c86...):

  ```
  {"&߿\u001f ߿ ߿":-604,"߿﻿/�":358," \u0007>\u0007":72,"😀":709}
  ```
- **go** (len 82, sha 1a8369fb50a9c3ba...):

  ```
  {"&߿\u001f ߿\u2029߿":-604,"߿﻿/�":358,"\u2029\u0007>\u0007":72,"😀":709}
  ```
- **rust** (len 76, sha f26849c41a616c86...):

  ```
  {"&߿\u001f ߿ ߿":-604,"߿﻿/�":358," \u0007>\u0007":72,"😀":709}
  ```

### Example 2

- generator: `unicode_string`
- input: `"/😀 Ā\u0007\"﻿"`

Canonical per implementation:
- **python** (len 24, sha 3de37b0a9016a299...):

  ```
  "/😀 Ā\u0007\"﻿"
  ```
- **go** (len 27, sha 59dd375fab42a253...):

  ```
  "/😀\u2029Ā\u0007\"﻿"
  ```
- **rust** (len 24, sha 3de37b0a9016a299...):

  ```
  "/😀 Ā\u0007\"﻿"
  ```

### Example 3

- generator: `unicode_string`
- input: `"ࠀ﻿ 😀\u0000 "`

Canonical per implementation:
- **python** (len 23, sha d78e632ba1e6ef33...):

  ```
  "ࠀ﻿ 😀\u0000 "
  ```
- **go** (len 26, sha 571f2aa0660dd681...):

  ```
  "ࠀ﻿ 😀\u0000\u2029"
  ```
- **rust** (len 23, sha d78e632ba1e6ef33...):

  ```
  "ࠀ﻿ 😀\u0000 "
  ```
