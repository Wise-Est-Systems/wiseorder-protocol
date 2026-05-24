# Disagreement signature 51

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-C1-control,contains-DEL,contains-SMP,contains-U+2028,contains-emoji`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-C1-control, contains-DEL, contains-SMP, contains-U+2028, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 1

## Examples

### Example 1

- generator: `nested`
- input: `{"/&": [{"￿": {"😀ࠀ﻿\u001f😀 ": [1.7976931348623157e+308, 3.14159, "😀"], "tag": 6}, "tag": 8}, 1.7976931348623157e+308, "\u0007/\u0007􏿿😀Ā߿"], "tag": 0}`

Canonical per implementation:
- **python** (len 164, sha 0e463bbbae536f61...):

  ```
  {"/&":[{"tag":8,"￿":{"tag":6,"😀ࠀ﻿\u001f😀 ":[1.7976931348623157e+308,3.14159,"😀"]}},1.7976931348623157e+308,"\u0007/\u0007􏿿😀Ā߿"],"tag":0}
  ```
- **go** (len 167, sha b5fcc58e66b6aeff...):

  ```
  {"/&":[{"tag":8,"￿":{"tag":6,"😀ࠀ﻿\u001f😀\u2028":[1.7976931348623157e+308,3.14159,"😀"]}},1.7976931348623157e+308,"\u0007/\u0007􏿿😀Ā߿"],"tag":0}
  ```
- **rust** (len 164, sha 0e463bbbae536f61...):

  ```
  {"/&":[{"tag":8,"￿":{"tag":6,"😀ࠀ﻿\u001f😀 ":[1.7976931348623157e+308,3.14159,"😀"]}},1.7976931348623157e+308,"\u0007/\u0007􏿿😀Ā߿"],"tag":0}
  ```
