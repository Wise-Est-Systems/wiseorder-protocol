# Disagreement signature 6

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-DEL,contains-U+2028,contains-U+2029`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-DEL, contains-U+2028, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 1

## Examples

### Example 1

- generator: `nested`
- input: `{"": [{"ࠀ ": {"ࠀĀ﻿\" \" ": 1e+16, "tag": 2}, "tag": 7}, 9007199254740991, "﻿ "], "tag": 9}`

Canonical per implementation:
- **python** (len 93, sha 859267c0dc906cd9...):

  ```
  {"tag":9,"":[{"tag":7,"ࠀ ":{"tag":2,"ࠀĀ﻿\" \" ":1e+16}},9007199254740991,"﻿ "]}
  ```
- **go** (len 99, sha 4b4516d44fa6bf39...):

  ```
  {"tag":9,"":[{"tag":7,"ࠀ\u2028":{"tag":2,"ࠀĀ﻿\"\u2029\" ":1e+16}},9007199254740991,"﻿ "]}
  ```
- **rust** (len 93, sha 859267c0dc906cd9...):

  ```
  {"tag":9,"":[{"tag":7,"ࠀ ":{"tag":2,"ࠀĀ﻿\" \" ":1e+16}},9007199254740991,"﻿ "]}
  ```
