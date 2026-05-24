# Disagreement signature 37

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-DEL,contains-SMP,contains-U+2028,contains-U+2029`

**Count:** 12

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-DEL, contains-SMP, contains-U+2028, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 7
  - nested: 3
  - array_order: 1
  - mixed_object: 1

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

### Example 2

- generator: `nested`
- input: `{"﻿": [[{" ": [0, 1e+17, "&/𐀀Ā"], "tag": 2}, 3.141592653589793, "\u0000 􏿿"], 10000000000.0, "﻿߿􏿿< \u0000"], "tag": 1}`

Canonical per implementation:
- **python** (len 125, sha 48ad36a463776fdc...):

  ```
  {"tag":1,"﻿":[[{"tag":2," ":[0,1e+17,"&/𐀀Ā"]},3.141592653589793,"\u0000 􏿿"],10000000000.0,"﻿߿􏿿< \u0000"]}
  ```
- **go** (len 131, sha c9bc751fa8884b58...):

  ```
  {"tag":1,"﻿":[[{"tag":2,"\u2029":[0,1e+17,"&/𐀀Ā"]},3.141592653589793,"\u0000\u2028􏿿"],10000000000.0,"﻿߿􏿿< \u0000"]}
  ```
- **rust** (len 125, sha 48ad36a463776fdc...):

  ```
  {"tag":1,"﻿":[[{"tag":2," ":[0,1e+17,"&/𐀀Ā"]},3.141592653589793,"\u0000 􏿿"],10000000000.0,"﻿߿􏿿< \u0000"]}
  ```

### Example 3

- generator: `object_unicode_keys`
- input: `{"\" ￿": -445, "Ā": 811, " Ā<\u0007\u001f": 123, "𐀀�ࠀ> ": -697, "\u0007﻿/": -920, "Ā&𐀀﻿\u0000": 367}`

Canonical per implementation:
- **python** (len 115, sha b330887f4b12d80f...):

  ```
  {"\u0007﻿/":-920,"\" ￿":-445,"Ā":811,"Ā&𐀀﻿\u0000":367," Ā<\u0007\u001f":123,"𐀀�ࠀ> ":-697}
  ```
- **go** (len 124, sha bc3f1bf610319b72...):

  ```
  {"\u0007﻿/":-920,"\"\u2029￿":-445,"Ā":811,"Ā&𐀀﻿\u0000":367,"\u2028Ā<\u0007\u001f":123,"𐀀�ࠀ>\u2028":-697}
  ```
- **rust** (len 115, sha b330887f4b12d80f...):

  ```
  {"\u0007﻿/":-920,"\" ￿":-445,"Ā":811,"Ā&𐀀﻿\u0000":367," Ā<\u0007\u001f":123,"𐀀�ࠀ> ":-697}
  ```
