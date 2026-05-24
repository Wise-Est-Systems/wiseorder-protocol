# Disagreement signature 69

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-C1-control,contains-DEL,contains-SMP,contains-U+2028,contains-U+2029,contains-bigint>2^53,contains-emoji`

**Count:** 7

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-C1-control, contains-DEL, contains-SMP, contains-U+2028, contains-U+2029, contains-bigint>2^53, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 7

## Examples

### Example 1

- generator: `nested`
- input: `{" 𐀀߿": [[{">😀 \"": -9223372036854775808, "tag": 6}, 1, "\u0007/�߿&﻿"], 1.7976931348623157e+308, "😀﻿𐀀< "], "tag": 1}`

Canonical per implementation:
- **python** (len 133, sha b78cc30f64656bcc...):

  ```
  {"tag":1," 𐀀߿":[[{">😀 \"":-9223372036854775808,"tag":6},1,"\u0007/�߿&﻿"],1.7976931348623157e+308,"😀﻿𐀀< "]}
  ```
- **go** (len 139, sha 0bd01a1974a65ded...):

  ```
  {"tag":1,"\u2028𐀀߿":[[{">😀\u2029\"":-9223372036854775808,"tag":6},1,"\u0007/�߿&﻿"],1.7976931348623157e+308,"😀﻿𐀀< "]}
  ```
- **rust** (len 133, sha b78cc30f64656bcc...):

  ```
  {"tag":1," 𐀀߿":[[{">😀 \"":-9223372036854775808,"tag":6},1,"\u0007/�߿&﻿"],1.7976931348623157e+308,"😀﻿𐀀< "]}
  ```

### Example 2

- generator: `nested`
- input: `[{"<  <﻿\\": [[9007199254740993, 2.718281828459045, "  <\u0000>𐀀>"], 0.001, "\\ࠀ 😀﻿&"], "tag": 6}, 0.3333333333333333, ""]`

Canonical per implementation:
- **python** (len 136, sha b21a5ac4d790f15b...):

  ```
  [{"<  <﻿\\":[[9007199254740993,2.718281828459045,"  <\u0000>𐀀>"],0.001,"\\ࠀ 😀﻿&"],"tag":6},0.3333333333333333,""]
  ```
- **go** (len 148, sha d6c80ae0c1b9a1c0...):

  ```
  [{"<\u2029\u2029<﻿\\":[[9007199254740993,2.718281828459045," \u2028<\u0000>𐀀>"],0.001,"\\ࠀ\u2028😀﻿&"],"tag":6},0.3333333333333333,""]
  ```
- **rust** (len 136, sha b21a5ac4d790f15b...):

  ```
  [{"<  <﻿\\":[[9007199254740993,2.718281828459045,"  <\u0000>𐀀>"],0.001,"\\ࠀ 😀﻿&"],"tag":6},0.3333333333333333,""]
  ```

### Example 3

- generator: `nested`
- input: `{"𐀀ÿ&": [[{" \"�𐀀😀": [9007199254740991, 0.001, "𐀀\u0000\\ ࠀ& "], "tag": 9}, 1e+16, "\u0007Ā\u001f"], 9007199254740993, ">￿﻿�"], "tag": 7}`

Canonical per implementation:
- **python** (len 156, sha c831e1ccdf9461bf...):

  ```
  {"tag":7,"𐀀ÿ&":[[{"tag":9," \"�𐀀😀":[9007199254740991,0.001,"𐀀\u0000\\ ࠀ& "]},1e+16,"\u0007Ā\u001f"],9007199254740993,">￿﻿�"]}
  ```
- **go** (len 162, sha 0940df04aedb31b2...):

  ```
  {"tag":7,"𐀀ÿ&":[[{"tag":9,"\u2028\"�𐀀😀":[9007199254740991,0.001,"𐀀\u0000\\\u2029ࠀ& "]},1e+16,"\u0007Ā\u001f"],9007199254740993,">￿﻿�"]}
  ```
- **rust** (len 156, sha c831e1ccdf9461bf...):

  ```
  {"tag":7,"𐀀ÿ&":[[{"tag":9," \"�𐀀😀":[9007199254740991,0.001,"𐀀\u0000\\ ࠀ& "]},1e+16,"\u0007Ā\u001f"],9007199254740993,">￿﻿�"]}
  ```
