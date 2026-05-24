# Disagreement signature 23

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-DEL,contains-SMP,contains-U+2028,contains-U+2029`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-DEL, contains-SMP, contains-U+2028, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"&ÿ￿ 𐀀\"": 446, "\\ ߿": -263, "<\u001f/𐀀\"": -256, "﻿ÿ\u001f�\u0000 ": 533, "ÿ﻿ࠀ߿<𐀀>\u0007": -337, "\\": 112}`

Canonical per implementation:
- **python** (len 128, sha 733a6d256367d5c7...):

  ```
  {"&ÿ￿ 𐀀\"":446,"\\":112,"\\ ߿":-263,"<\u001f/𐀀\"":-256,"ÿ﻿ࠀ߿<𐀀>\u0007":-337,"﻿ÿ\u001f�\u0000 ":533}
  ```
- **go** (len 134, sha 45787805942d6587...):

  ```
  {"&ÿ￿ 𐀀\"":446,"\\":112,"\\\u2028߿":-263,"<\u001f/𐀀\"":-256,"ÿ﻿ࠀ߿<𐀀>\u0007":-337,"﻿ÿ\u001f�\u0000\u2029":533}
  ```
- **rust** (len 128, sha 733a6d256367d5c7...):

  ```
  {"&ÿ￿ 𐀀\"":446,"\\":112,"\\ ߿":-263,"<\u001f/𐀀\"":-256,"ÿ﻿ࠀ߿<𐀀>\u0007":-337,"﻿ÿ\u001f�\u0000 ":533}
  ```
