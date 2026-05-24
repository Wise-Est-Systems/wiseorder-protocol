# Disagreement signature 54

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-C1-control,contains-SMP,contains-U+2029`

**Count:** 9

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-C1-control, contains-SMP, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 4
  - array_order: 3
  - nested: 2

## Examples

### Example 1

- generator: `nested`
- input: `[[{"﻿𐀀 \u0000": {"￿": 1.7976931348623157e+308, "tag": 0}, "tag": 5}, 1e+16, ""], -1, "ࠀࠀ￿ࠀ\u001f"]`

Canonical per implementation:
- **python** (len 109, sha 29698f2ad7060fbf...):

  ```
  [[{"tag":5,"﻿𐀀 \u0000":{"tag":0,"￿":1.7976931348623157e+308}},1e+16,""],-1,"ࠀࠀ￿ࠀ\u001f"]
  ```
- **go** (len 112, sha 85de3374fb9ef8ca...):

  ```
  [[{"tag":5,"﻿𐀀\u2029\u0000":{"tag":0,"￿":1.7976931348623157e+308}},1e+16,""],-1,"ࠀࠀ￿ࠀ\u001f"]
  ```
- **rust** (len 109, sha 29698f2ad7060fbf...):

  ```
  [[{"tag":5,"﻿𐀀 \u0000":{"tag":0,"￿":1.7976931348623157e+308}},1e+16,""],-1,"ࠀࠀ￿ࠀ\u001f"]
  ```

### Example 2

- generator: `array_order`
- input: `["<&\u0007\"\\𐀀\"<", "𐀀 ", 9007199254740991, 58, "/﻿\\𐀀 𐀀", -17]`

Canonical per implementation:
- **python** (len 77, sha c7d323c0fe9c2bfd...):

  ```
  ["<&\u0007\"\\𐀀\"<","𐀀 ",9007199254740991,58,"/﻿\\𐀀 𐀀",-17]
  ```
- **go** (len 80, sha f6d027e1c58fc106...):

  ```
  ["<&\u0007\"\\𐀀\"<","𐀀 ",9007199254740991,58,"/﻿\\𐀀\u2029𐀀",-17]
  ```
- **rust** (len 77, sha c7d323c0fe9c2bfd...):

  ```
  ["<&\u0007\"\\𐀀\"<","𐀀 ",9007199254740991,58,"/﻿\\𐀀 𐀀",-17]
  ```

### Example 3

- generator: `object_unicode_keys`
- input: `{"\u0000": -899, "￿𐀀 ﻿ ﻿￿>": 6, " \u0000>ࠀ߿\u0000Ā ": -530, "\u0007\u0007�\u0000": -598, "ÿ": -890}`

Canonical per implementation:
- **python** (len 116, sha 51bfb27706e11ff8...):

  ```
  {"\u0000":-899,"\u0007\u0007�\u0000":-598,"ÿ":-890," \u0000>ࠀ߿\u0000Ā ":-530,"￿𐀀 ﻿ ﻿￿>":6}
  ```
- **go** (len 125, sha b713af5171e97434...):

  ```
  {"\u0000":-899,"\u0007\u0007�\u0000":-598,"ÿ":-890,"\u2029\u0000>ࠀ߿\u0000Ā\u2029":-530,"￿𐀀 ﻿\u2029﻿￿>":6}
  ```
- **rust** (len 116, sha 51bfb27706e11ff8...):

  ```
  {"\u0000":-899,"\u0007\u0007�\u0000":-598,"ÿ":-890," \u0000>ࠀ߿\u0000Ā ":-530,"￿𐀀 ﻿ ﻿￿>":6}
  ```
