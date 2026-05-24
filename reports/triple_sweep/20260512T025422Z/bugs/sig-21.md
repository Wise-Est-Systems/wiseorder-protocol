# Disagreement signature 21

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-C1-control,contains-DEL,contains-SMP,contains-U+2029,contains-emoji`

**Count:** 15

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-C1-control, contains-DEL, contains-SMP, contains-U+2029, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 9
  - nested: 5
  - array_order: 1

## Examples

### Example 1

- generator: `nested`
- input: `{" � ߿<": [{"\\\u0000￿\u001f😀": {"􏿿ÿ": [9007199254740991, 0.3333333333333333, "﻿"], "tag": 2}, "tag": 6}, 0.3, "Ā߿𐀀"], "tag": 3}`

Canonical per implementation:
- **python** (len 145, sha 0d5c1927c460ce0c...):

  ```
  {"tag":3," � ߿<":[{"\\\u0000￿\u001f😀":{"tag":2,"􏿿ÿ":[9007199254740991,0.3333333333333333,"﻿"]},"tag":6},0.3,"Ā߿𐀀"]}
  ```
- **go** (len 148, sha ba11f092658419a8...):

  ```
  {"tag":3,"\u2029� ߿<":[{"\\\u0000￿\u001f😀":{"tag":2,"􏿿ÿ":[9007199254740991,0.3333333333333333,"﻿"]},"tag":6},0.3,"Ā߿𐀀"]}
  ```
- **rust** (len 145, sha 0d5c1927c460ce0c...):

  ```
  {"tag":3," � ߿<":[{"\\\u0000￿\u001f😀":{"tag":2,"􏿿ÿ":[9007199254740991,0.3333333333333333,"﻿"]},"tag":6},0.3,"Ā߿𐀀"]}
  ```

### Example 2

- generator: `nested`
- input: `{"߿\\ Ā": {"/ࠀ😀\"﻿  ": [[0.3333333333333333, 0.30000000000000004, " \u001f􏿿"], 2147483647, "&﻿￿\\>�"], "tag": 6}, "tag": 4}`

Canonical per implementation:
- **python** (len 136, sha c67fe93937139c01...):

  ```
  {"tag":4,"߿\\ Ā":{"/ࠀ😀\"﻿  ":[[0.3333333333333333,0.30000000000000004," \u001f􏿿"],2147483647,"&﻿￿\\>�"],"tag":6}}
  ```
- **go** (len 139, sha ba468b7852900249...):

  ```
  {"tag":4,"߿\\ Ā":{"/ࠀ😀\"﻿ \u2029":[[0.3333333333333333,0.30000000000000004," \u001f􏿿"],2147483647,"&﻿￿\\>�"],"tag":6}}
  ```
- **rust** (len 136, sha c67fe93937139c01...):

  ```
  {"tag":4,"߿\\ Ā":{"/ࠀ😀\"﻿  ":[[0.3333333333333333,0.30000000000000004," \u001f􏿿"],2147483647,"&﻿￿\\>�"],"tag":6}}
  ```

### Example 3

- generator: `object_unicode_keys`
- input: `{"": -798, "𐀀 ": 391, "Ā>/𐀀😀/": -24, "𐀀﻿>": -258, "\u001f ": 30, "😀\u001fࠀ𐀀�𐀀": 653}`

Canonical per implementation:
- **python** (len 108, sha 9cb4e03ad4342c1c...):

  ```
  {"\u001f ":30,"":-798,"Ā>/𐀀😀/":-24,"𐀀 ":391,"𐀀﻿>":-258,"😀\u001fࠀ𐀀�𐀀":653}
  ```
- **go** (len 111, sha c7fb5134c7d54b57...):

  ```
  {"\u001f ":30,"":-798,"Ā>/𐀀😀/":-24,"𐀀\u2029":391,"𐀀﻿>":-258,"😀\u001fࠀ𐀀�𐀀":653}
  ```
- **rust** (len 108, sha 9cb4e03ad4342c1c...):

  ```
  {"\u001f ":30,"":-798,"Ā>/𐀀😀/":-24,"𐀀 ":391,"𐀀﻿>":-258,"😀\u001fࠀ𐀀�𐀀":653}
  ```
