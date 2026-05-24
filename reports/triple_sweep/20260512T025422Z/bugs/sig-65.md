# Disagreement signature 65

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-U+2028,contains-emoji`

**Count:** 8

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-U+2028, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 3
  - array_order: 2
  - object_unicode_keys: 2
  - unicode_string: 1

## Examples

### Example 1

- generator: `nested`
- input: `{"\u0000\\> ": {"﻿ ￿ࠀ": [5e-324, -0.0, "\u0000ࠀ￿߿  😀 "], "tag": 0}, "tag": 0}`

Canonical per implementation:
- **python** (len 87, sha f0c2426fcc4f203f...):

  ```
  {"\u0000\\> ":{"tag":0,"﻿ ￿ࠀ":[5e-324,-0.0,"\u0000ࠀ￿߿  😀 "]},"tag":0}
  ```
- **go** (len 93, sha cd68f2c44937c87e...):

  ```
  {"\u0000\\> ":{"tag":0,"﻿\u2028￿ࠀ":[5e-324,-0.0,"\u0000ࠀ￿߿\u2028 😀 "]},"tag":0}
  ```
- **rust** (len 87, sha f0c2426fcc4f203f...):

  ```
  {"\u0000\\> ":{"tag":0,"﻿ ￿ࠀ":[5e-324,-0.0,"\u0000ࠀ￿߿  😀 "]},"tag":0}
  ```

### Example 2

- generator: `array_order`
- input: `["😀﻿\u001f>ࠀ߿  ", -4, -0.0, 100, 9007199254740991]`

Canonical per implementation:
- **python** (len 56, sha 005935a1359955ad...):

  ```
  ["😀﻿\u001f>ࠀ߿  ",-4,-0.0,100,9007199254740991]
  ```
- **go** (len 59, sha ff2b9471d0279af3...):

  ```
  ["😀﻿\u001f>ࠀ߿ \u2028",-4,-0.0,100,9007199254740991]
  ```
- **rust** (len 56, sha 005935a1359955ad...):

  ```
  ["😀﻿\u001f>ࠀ߿  ",-4,-0.0,100,9007199254740991]
  ```

### Example 3

- generator: `array_order`
- input: `[9007199254740992, -88, "\u0007﻿", 0.2, " ￿/😀Ā﻿", -0.0, "/"]`

Canonical per implementation:
- **python** (len 66, sha 172219b20853b4e6...):

  ```
  [9007199254740992,-88,"\u0007﻿",0.2," ￿/😀Ā﻿",-0.0,"/"]
  ```
- **go** (len 69, sha 42049771b1dfa8cf...):

  ```
  [9007199254740992,-88,"\u0007﻿",0.2,"\u2028￿/😀Ā﻿",-0.0,"/"]
  ```
- **rust** (len 66, sha 172219b20853b4e6...):

  ```
  [9007199254740992,-88,"\u0007﻿",0.2," ￿/😀Ā﻿",-0.0,"/"]
  ```
