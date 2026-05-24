# Disagreement signature 1

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-C1-control,contains-DEL,contains-SMP,contains-U+2028,contains-U+2029,contains-emoji`

**Count:** 6

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-C1-control, contains-DEL, contains-SMP, contains-U+2028, contains-U+2029, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 5
  - nested: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"\u0007\"﻿😀 ": -89, "ÿ&😀<𐀀": -991, "&ࠀ\"�& \u0007\u001f": -810, " ￿￿𐀀\u0007﻿": 483, "\\  􏿿﻿": -44, " ﻿>": 80}`

Canonical per implementation:
- **python** (len 143, sha c4a1a62003369ce3...):

  ```
  {"\u0007\"﻿😀 ":-89," ￿￿𐀀\u0007﻿":483,"&ࠀ\"�& \u0007\u001f":-810,"\\  􏿿﻿":-44,"ÿ&😀<𐀀":-991," ﻿>":80}
  ```
- **go** (len 155, sha e3bf8b6cff646621...):

  ```
  {"\u0007\"﻿😀 ":-89," ￿￿𐀀\u0007﻿":483,"&ࠀ\"�&\u2029\u0007\u001f":-810,"\\\u2029\u2029􏿿﻿":-44,"ÿ&😀<𐀀":-991,"\u2028﻿>":80}
  ```
- **rust** (len 143, sha c4a1a62003369ce3...):

  ```
  {"\u0007\"﻿😀 ":-89," ￿￿𐀀\u0007﻿":483,"&ࠀ\"�& \u0007\u001f":-810,"\\  􏿿﻿":-44,"ÿ&😀<𐀀":-991," ﻿>":80}
  ```

### Example 2

- generator: `object_unicode_keys`
- input: `{"𐀀<>ÿ\u0000": -276, "�": -787, "<ÿ <￿😀\u001f": -163, "\"𐀀𐀀😀\"􏿿﻿ ": 557, "�> 𐀀\u0007": 209, "& ": -13}`

Canonical per implementation:
- **python** (len 134, sha 52898723464ae3ea...):

  ```
  {"\"𐀀𐀀😀\"􏿿﻿ ":557,"& ":-13,"<ÿ <￿😀\u001f":-163,"�":-787,"�> 𐀀\u0007":209,"𐀀<>ÿ\u0000":-276}
  ```
- **go** (len 143, sha efae19112db221d6...):

  ```
  {"\"𐀀𐀀😀\"􏿿﻿ ":557,"&\u2028":-13,"<ÿ\u2028<￿😀\u001f":-163,"�":-787,"�>\u2029𐀀\u0007":209,"𐀀<>ÿ\u0000":-276}
  ```
- **rust** (len 134, sha 52898723464ae3ea...):

  ```
  {"\"𐀀𐀀😀\"􏿿﻿ ":557,"& ":-13,"<ÿ <￿😀\u001f":-163,"�":-787,"�> 𐀀\u0007":209,"𐀀<>ÿ\u0000":-276}
  ```

### Example 3

- generator: `nested`
- input: `[[[{"ࠀĀ": {"\u0007": 0.001, "tag": 7}, "tag": 9}, 0, "<"], -1, " <𐀀￿\"\u001f�"], 1e+100, "\"😀 ﻿ "]`

Canonical per implementation:
- **python** (len 109, sha 90e38b5d05d75aca...):

  ```
  [[[{"tag":9,"ࠀĀ":{"\u0007":0.001,"tag":7}},0,"<"],-1," <𐀀￿\"\u001f�"],1e+100,"\"😀 ﻿ "]
  ```
- **go** (len 115, sha 26907f01978b44f6...):

  ```
  [[[{"tag":9,"ࠀĀ":{"\u0007":0.001,"tag":7}},0,"<"],-1,"\u2029<𐀀￿\"\u001f�"],1e+100,"\"😀 ﻿\u2028"]
  ```
- **rust** (len 109, sha 90e38b5d05d75aca...):

  ```
  [[[{"tag":9,"ࠀĀ":{"\u0007":0.001,"tag":7}},0,"<"],-1," <𐀀￿\"\u001f�"],1e+100,"\"😀 ﻿ "]
  ```
