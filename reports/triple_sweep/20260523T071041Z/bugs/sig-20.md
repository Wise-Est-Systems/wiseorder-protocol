# Disagreement signature 20

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-U+2029`

**Count:** 2

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - unicode_string: 1
  - nested: 1

## Examples

### Example 1

- generator: `unicode_string`
- input: `"Ā\u001f\u001f\u001f\u0000 ﻿"`

Canonical per implementation:
- **python** (len 34, sha d99d0f751ca616bd...):

  ```
  "Ā\u001f\u001f\u001f\u0000 ﻿"
  ```
- **go** (len 37, sha 81313db53de352dd...):

  ```
  "Ā\u001f\u001f\u001f\u0000\u2029﻿"
  ```
- **rust** (len 34, sha d99d0f751ca616bd...):

  ```
  "Ā\u001f\u001f\u001f\u0000 ﻿"
  ```

### Example 2

- generator: `nested`
- input: `{"﻿ \u0007�\u0000": [1e+100, 0.001, "\\&  "], "tag": 8}`

Canonical per implementation:
- **python** (len 58, sha 72bafe75a9def9ae...):

  ```
  {"tag":8,"﻿ \u0007�\u0000":[1e+100,0.001,"\\&  "]}
  ```
- **go** (len 64, sha ccd909bd0869c9b8...):

  ```
  {"tag":8,"﻿ \u0007�\u0000":[1e+100,0.001,"\\&\u2029\u2029"]}
  ```
- **rust** (len 58, sha 72bafe75a9def9ae...):

  ```
  {"tag":8,"﻿ \u0007�\u0000":[1e+100,0.001,"\\&  "]}
  ```
