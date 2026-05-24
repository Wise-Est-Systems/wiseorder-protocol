# Disagreement signature 5

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-SMP,contains-U+2028,contains-U+2029,contains-emoji`

**Count:** 4

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-SMP, contains-U+2028, contains-U+2029, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 2
  - nested: 1
  - array_order: 1

## Examples

### Example 1

- generator: `nested`
- input: `[[[{"😀￿ࠀ": {"ࠀ": 2.718281828459045, "tag": 9}, "tag": 5}, -1, "\u001f  \"&&"], 5e-324, "  \u0007😀>﻿􏿿􏿿"], -1, " "]`

Canonical per implementation:
- **python** (len 127, sha 1db5c7afe071999c...):

  ```
  [[[{"tag":5,"😀￿ࠀ":{"tag":9,"ࠀ":2.718281828459045}},-1,"\u001f  \"&&"],5e-324,"  \u0007😀>﻿􏿿􏿿"],-1," "]
  ```
- **go** (len 136, sha 58e463bb0e77c6bc...):

  ```
  [[[{"tag":5,"😀￿ࠀ":{"tag":9,"ࠀ":2.718281828459045}},-1,"\u001f\u2029\u2028\"&&"],5e-324,"  \u0007😀>﻿􏿿􏿿"],-1,"\u2029"]
  ```
- **rust** (len 127, sha 1db5c7afe071999c...):

  ```
  [[[{"tag":5,"😀￿ࠀ":{"tag":9,"ࠀ":2.718281828459045}},-1,"\u001f  \"&&"],5e-324,"  \u0007😀>﻿􏿿􏿿"],-1," "]
  ```

### Example 2

- generator: `object_unicode_keys`
- input: `{"\u0007\u0000&￿\u0007": 637, "ÿࠀ﻿\u0007𐀀﻿􏿿": 620, "ࠀ\u0007𐀀 \u001fÿࠀ": 894, "\u0007 ": 267, "􏿿߿&􏿿 ": -947, "\u0007﻿/ 😀": -458}`

Canonical per implementation:
- **python** (len 157, sha 7961045695d732eb...):

  ```
  {"\u0007\u0000&￿\u0007":637,"\u0007 ":267,"\u0007﻿/ 😀":-458,"ÿࠀ﻿\u0007𐀀﻿􏿿":620,"ࠀ\u0007𐀀 \u001fÿࠀ":894,"􏿿߿&􏿿 ":-947}
  ```
- **go** (len 166, sha 6f36a6dea7779d28...):

  ```
  {"\u0007\u0000&￿\u0007":637,"\u0007 ":267,"\u0007﻿/\u2028😀":-458,"ÿࠀ﻿\u0007𐀀﻿􏿿":620,"ࠀ\u0007𐀀\u2029\u001fÿࠀ":894,"􏿿߿&􏿿\u2029":-947}
  ```
- **rust** (len 157, sha 7961045695d732eb...):

  ```
  {"\u0007\u0000&￿\u0007":637,"\u0007 ":267,"\u0007﻿/ 😀":-458,"ÿࠀ﻿\u0007𐀀﻿􏿿":620,"ࠀ\u0007𐀀 \u001fÿࠀ":894,"􏿿߿&􏿿 ":-947}
  ```

### Example 3

- generator: `array_order`
- input: `["😀>\u0000", "\\\"&￿ >", 0.0, 10000000000.0, -87, " \u001fÿ\u0000﻿﻿&􏿿", "𐀀﻿\"&�"]`

Canonical per implementation:
- **python** (len 99, sha f5f208850f5fae5f...):

  ```
  ["😀>\u0000","\\\"&￿ >",0.0,10000000000.0,-87," \u001fÿ\u0000﻿﻿&􏿿","𐀀﻿\"&�"]
  ```
- **go** (len 105, sha 82118ecd72029003...):

  ```
  ["😀>\u0000","\\\"&￿\u2028>",0.0,10000000000.0,-87,"\u2029\u001fÿ\u0000﻿﻿&􏿿","𐀀﻿\"&�"]
  ```
- **rust** (len 99, sha f5f208850f5fae5f...):

  ```
  ["😀>\u0000","\\\"&￿ >",0.0,10000000000.0,-87," \u001fÿ\u0000﻿﻿&􏿿","𐀀﻿\"&�"]
  ```
