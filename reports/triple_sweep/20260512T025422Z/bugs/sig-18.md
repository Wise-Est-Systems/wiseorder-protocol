# Disagreement signature 18

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-U+2028`

**Count:** 16

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-U+2028

**Length pattern:** longest:go,shortest:python

**By generator:**
  - unicode_string: 6
  - array_order: 5
  - nested: 2
  - mixed_object: 2
  - object_unicode_keys: 1

## Examples

### Example 1

- generator: `nested`
- input: `{"  &": {" \u0000ÿ": [1.7976931348623157e+308, 0.3333333333333333, "�<\u001f ﻿"], "tag": 5}, "tag": 8}`

Canonical per implementation:
- **python** (len 101, sha 564449302b2ab8b6...):

  ```
  {"  &":{"tag":5," \u0000ÿ":[1.7976931348623157e+308,0.3333333333333333,"�<\u001f ﻿"]},"tag":8}
  ```
- **go** (len 104, sha 3e2547007bcb8c81...):

  ```
  {"  &":{"tag":5,"\u2028\u0000ÿ":[1.7976931348623157e+308,0.3333333333333333,"�<\u001f ﻿"]},"tag":8}
  ```
- **rust** (len 101, sha 564449302b2ab8b6...):

  ```
  {"  &":{"tag":5," \u0000ÿ":[1.7976931348623157e+308,0.3333333333333333,"�<\u001f ﻿"]},"tag":8}
  ```

### Example 2

- generator: `nested`
- input: `[{"\u001fÿ \\<  ": [[3.141592653589793, 2.2250738585072014e-308, "﻿/<"], 1e-100, "Ā߿/>"], "tag": 2}, 9007199254740992, "﻿"]`

Canonical per implementation:
- **python** (len 127, sha cacf749c0b84ee6a...):

  ```
  [{"\u001fÿ \\<  ":[[3.141592653589793,2.2250738585072014e-308,"﻿/<"],1e-100,"Ā߿/>"],"tag":2},9007199254740992,"﻿"]
  ```
- **go** (len 136, sha d991295bfd5eda6c...):

  ```
  [{"\u001fÿ\u2028\\<\u2028\u2028":[[3.141592653589793,2.2250738585072014e-308,"﻿/<"],1e-100,"Ā߿/>"],"tag":2},9007199254740992,"﻿"]
  ```
- **rust** (len 127, sha cacf749c0b84ee6a...):

  ```
  [{"\u001fÿ \\<  ":[[3.141592653589793,2.2250738585072014e-308,"﻿/<"],1e-100,"Ā߿/>"],"tag":2},9007199254740992,"﻿"]
  ```

### Example 3

- generator: `unicode_string`
- input: `" ﻿ \u0007ÿ߿&"`

Canonical per implementation:
- **python** (len 22, sha a2164e7636a5bc87...):

  ```
  " ﻿ \u0007ÿ߿&"
  ```
- **go** (len 28, sha 3c91ee92e0cc9647...):

  ```
  "\u2028﻿\u2028\u0007ÿ߿&"
  ```
- **rust** (len 22, sha a2164e7636a5bc87...):

  ```
  " ﻿ \u0007ÿ߿&"
  ```
