# Disagreement signature 83

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-C1-control,contains-U+2029`

**Count:** 6

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-C1-control, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 3
  - array_order: 2
  - nested: 1

## Examples

### Example 1

- generator: `nested`
- input: `{" ﻿\u0000\\": {"&&  \u001f\"ÿ": 3.141592653589793, "tag": 5}, "tag": 6}`

Canonical per implementation:
- **python** (len 75, sha 80607f8b94abf6c0...):

  ```
  {"tag":6," ﻿\u0000\\":{"&&  \u001f\"ÿ":3.141592653589793,"tag":5}}
  ```
- **go** (len 81, sha c727cdfdccc6bf73...):

  ```
  {"tag":6,"\u2029﻿\u0000\\":{"&& \u2029\u001f\"ÿ":3.141592653589793,"tag":5}}
  ```
- **rust** (len 75, sha 80607f8b94abf6c0...):

  ```
  {"tag":6," ﻿\u0000\\":{"&&  \u001f\"ÿ":3.141592653589793,"tag":5}}
  ```

### Example 2

- generator: `array_order`
- input: `[-68, 0.001, 62, "> � \">>", "߿\u001f￿﻿߿", 0.3333333333333333]`

Canonical per implementation:
- **python** (len 69, sha f4b5866e3f09374a...):

  ```
  [-68,0.001,62,"> � \">>","߿\u001f￿﻿߿",0.3333333333333333]
  ```
- **go** (len 72, sha 5950b21ccab1391a...):

  ```
  [-68,0.001,62,"> �\u2029\">>","߿\u001f￿﻿߿",0.3333333333333333]
  ```
- **rust** (len 69, sha f4b5866e3f09374a...):

  ```
  [-68,0.001,62,"> � \">>","߿\u001f￿﻿߿",0.3333333333333333]
  ```

### Example 3

- generator: `object_unicode_keys`
- input: `{"￿": -933, "": 115, "\u001f": -159, " >": -539, "﻿<": -331}`

Canonical per implementation:
- **python** (len 59, sha 093aa6450efa9504...):

  ```
  {"\u001f":-159,"":115," >":-539,"﻿<":-331,"￿":-933}
  ```
- **go** (len 62, sha 86efc82cff78985b...):

  ```
  {"\u001f":-159,"":115,"\u2029>":-539,"﻿<":-331,"￿":-933}
  ```
- **rust** (len 59, sha 093aa6450efa9504...):

  ```
  {"\u001f":-159,"":115," >":-539,"﻿<":-331,"￿":-933}
  ```
