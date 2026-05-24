# Disagreement signature 92

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-C1-control,contains-DEL,contains-U+2028,contains-U+2029,contains-emoji`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-C1-control, contains-DEL, contains-U+2028, contains-U+2029, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 1

## Examples

### Example 1

- generator: `nested`
- input: `{"\u0000﻿<": [{" ߿￿ÿ": [{" &\\￿": 1e+17, "tag": 2}, 0.3, "\u0000߿/ "], "tag": 2}, 0.3, " ߿﻿\\😀\u0007\""], "tag": 7}`

Canonical per implementation:
- **python** (len 128, sha bfd54d8278b5890f...):

  ```
  {"\u0000﻿<":[{"tag":2," ߿￿ÿ":[{"tag":2," &\\￿":1e+17},0.3,"\u0000߿/ "]},0.3," ߿﻿\\😀\u0007\""],"tag":7}
  ```
- **go** (len 140, sha cdb9fcf19260992d...):

  ```
  {"\u0000﻿<":[{"tag":2,"\u2029߿￿ÿ":[{"tag":2,"\u2028&\\￿":1e+17},0.3,"\u0000߿/\u2029"]},0.3,"\u2028߿﻿\\😀\u0007\""],"tag":7}
  ```
- **rust** (len 128, sha bfd54d8278b5890f...):

  ```
  {"\u0000﻿<":[{"tag":2," ߿￿ÿ":[{"tag":2," &\\￿":1e+17},0.3,"\u0000߿/ "]},0.3," ߿﻿\\😀\u0007\""],"tag":7}
  ```
