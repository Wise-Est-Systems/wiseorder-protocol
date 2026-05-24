# Disagreement signature 2

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-DEL,contains-SMP,contains-U+2028,contains-U+2029,contains-emoji`

**Count:** 5

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-DEL, contains-SMP, contains-U+2028, contains-U+2029, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 3
  - object_unicode_keys: 2

## Examples

### Example 1

- generator: `nested`
- input: `{"\u0007😀 ": {"􏿿\"\\\\ࠀ": [{" Ā﻿ \u0000": -0.0, "tag": 3}, 9007199254740992, "😀"], "tag": 6}, "tag": 6}`

Canonical per implementation:
- **python** (len 111, sha 17b378f1c1f3c05e...):

  ```
  {"\u0007😀 ":{"tag":6,"􏿿\"\\\\ࠀ":[{" Ā﻿ \u0000":-0.0,"tag":3},9007199254740992,"😀"]},"tag":6}
  ```
- **go** (len 117, sha d5a6b9817b39e74c...):

  ```
  {"\u0007😀\u2028":{"tag":6,"􏿿\"\\\\ࠀ":[{" Ā﻿\u2029\u0000":-0.0,"tag":3},9007199254740992,"😀"]},"tag":6}
  ```
- **rust** (len 111, sha 17b378f1c1f3c05e...):

  ```
  {"\u0007😀 ":{"tag":6,"􏿿\"\\\\ࠀ":[{" Ā﻿ \u0000":-0.0,"tag":3},9007199254740992,"😀"]},"tag":6}
  ```

### Example 2

- generator: `nested`
- input: `[[[[[3.141592653589793, 1e+17, "�Ā😀 &"], 1, "\u0000&ÿ  ࠀ"], 1000000000000000.0, "&߿􏿿�>\u0007 "], 3.141592653589793, "\u001f﻿<ÿ\u0007"], 0.0, "﻿😀𐀀&&\u001f"]`

Canonical per implementation:
- **python** (len 180, sha 3f12a7cb764508bb...):

  ```
  [[[[[3.141592653589793,1e+17,"�Ā😀 &"],1,"\u0000&ÿ  ࠀ"],1000000000000000.0,"&߿􏿿�>\u0007 "],3.141592653589793,"\u001f﻿<ÿ\u0007"],0.0,"﻿😀𐀀&&\u001f"]
  ```
- **go** (len 192, sha 36fa85ebb4adbae0...):

  ```
  [[[[[3.141592653589793,1e+17,"�Ā😀\u2029&"],1,"\u0000&ÿ\u2029\u2028ࠀ"],1000000000000000.0,"&߿􏿿�>\u0007\u2028"],3.141592653589793,"\u001f﻿<ÿ\u0007"],0.0,"﻿😀𐀀&&\u001f"]
  ```
- **rust** (len 180, sha 3f12a7cb764508bb...):

  ```
  [[[[[3.141592653589793,1e+17,"�Ā😀 &"],1,"\u0000&ÿ  ࠀ"],1000000000000000.0,"&߿􏿿�>\u0007 "],3.141592653589793,"\u001f﻿<ÿ\u0007"],0.0,"﻿😀𐀀&&\u001f"]
  ```

### Example 3

- generator: `object_unicode_keys`
- input: `{"\\ 𐀀ÿ&/\\": 250, "\u0000 \u001f😀 ࠀ": -23, "￿￿�߿�": -266, "ࠀ￿Ā\"": -17, "\u001f\u0000﻿\u001f ": 591, "ࠀ ߿😀\u0007\"": 341}`

Canonical per implementation:
- **python** (len 147, sha f036f78bfeee7dc0...):

  ```
  {"\u0000 \u001f😀 ࠀ":-23,"\u001f\u0000﻿\u001f ":591,"\\ 𐀀ÿ&/\\":250,"ࠀ ߿😀\u0007\"":341,"ࠀ￿Ā\"":-17,"￿￿�߿�":-266}
  ```
- **go** (len 153, sha 2b3067995a9d7831...):

  ```
  {"\u0000\u2028\u001f😀 ࠀ":-23,"\u001f\u0000﻿\u001f\u2029":591,"\\ 𐀀ÿ&/\\":250,"ࠀ ߿😀\u0007\"":341,"ࠀ￿Ā\"":-17,"￿￿�߿�":-266}
  ```
- **rust** (len 147, sha f036f78bfeee7dc0...):

  ```
  {"\u0000 \u001f😀 ࠀ":-23,"\u001f\u0000﻿\u001f ":591,"\\ 𐀀ÿ&/\\":250,"ࠀ ߿😀\u0007\"":341,"ࠀ￿Ā\"":-17,"￿￿�߿�":-266}
  ```
