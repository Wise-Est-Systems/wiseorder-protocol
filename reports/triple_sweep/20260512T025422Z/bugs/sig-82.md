# Disagreement signature 82

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-DEL,contains-SMP,contains-U+2028,contains-U+2029,contains-bigint>2^53`

**Count:** 6

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-DEL, contains-SMP, contains-U+2028, contains-U+2029, contains-bigint>2^53

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 5
  - array_order: 1

## Examples

### Example 1

- generator: `nested`
- input: `[[[{"\u0000ÿĀ﻿/\u001fࠀ\\": 0.3333333333333333, "tag": 1}, -9223372036854775808, "􏿿  <"], 5e-324, "<\\\"􏿿ࠀ"], 1e+17, "<ÿ\u0007􏿿 \u001f"]`

Canonical per implementation:
- **python** (len 149, sha 5623c7e6994cc943...):

  ```
  [[[{"\u0000ÿĀ﻿/\u001fࠀ\\":0.3333333333333333,"tag":1},-9223372036854775808,"􏿿  <"],5e-324,"<\\\"􏿿ࠀ"],1e+17,"<ÿ\u0007􏿿 \u001f"]
  ```
- **go** (len 155, sha ade0a9bdfab77626...):

  ```
  [[[{"\u0000ÿĀ﻿/\u001fࠀ\\":0.3333333333333333,"tag":1},-9223372036854775808,"􏿿 \u2029<"],5e-324,"<\\\"􏿿ࠀ"],1e+17,"<ÿ\u0007􏿿\u2028\u001f"]
  ```
- **rust** (len 149, sha 5623c7e6994cc943...):

  ```
  [[[{"\u0000ÿĀ﻿/\u001fࠀ\\":0.3333333333333333,"tag":1},-9223372036854775808,"􏿿  <"],5e-324,"<\\\"􏿿ࠀ"],1e+17,"<ÿ\u0007􏿿 \u001f"]
  ```

### Example 2

- generator: `nested`
- input: `{" >﻿ࠀ𐀀": {"􏿿\u0007/": [[{"\\﻿￿": 9007199254740993, "tag": 7}, 9007199254740991, "  &"], -2.5, "𐀀\u0000￿Ā￿\\\u0007"], "tag": 0}, "tag": 8}`

Canonical per implementation:
- **python** (len 152, sha 2e02eaaee27fdbdb...):

  ```
  {"tag":8," >﻿ࠀ𐀀":{"tag":0,"􏿿\u0007/":[[{"\\﻿￿":9007199254740993,"tag":7},9007199254740991,"  &"],-2.5,"𐀀\u0000￿Ā￿\\\u0007"]}}
  ```
- **go** (len 158, sha ffffdb114fbcd35e...):

  ```
  {"tag":8,"\u2029>﻿ࠀ𐀀":{"tag":0,"􏿿\u0007/":[[{"\\﻿￿":9007199254740993,"tag":7},9007199254740991,"\u2028 &"],-2.5,"𐀀\u0000￿Ā￿\\\u0007"]}}
  ```
- **rust** (len 152, sha 2e02eaaee27fdbdb...):

  ```
  {"tag":8," >﻿ࠀ𐀀":{"tag":0,"􏿿\u0007/":[[{"\\﻿￿":9007199254740993,"tag":7},9007199254740991,"  &"],-2.5,"𐀀\u0000￿Ā￿\\\u0007"]}}
  ```

### Example 3

- generator: `nested`
- input: `{"\\ĀĀ": {"￿ ": {"߿﻿ ÿ﻿ÿ􏿿": [{"߿\u0007𐀀</": 9223372036854775807, "tag": 4}, 9007199254740993, "\u0007﻿\u001f >\u001f"], "tag": 5}, "tag": 0}, "tag": 4}`

Canonical per implementation:
- **python** (len 164, sha 4fafa4826ee26547...):

  ```
  {"\\ĀĀ":{"tag":0,"￿ ":{"tag":5,"߿﻿ ÿ﻿ÿ􏿿":[{"tag":4,"߿\u0007𐀀</":9223372036854775807},9007199254740993,"\u0007﻿\u001f >\u001f"]}},"tag":4}
  ```
- **go** (len 173, sha ce725cb5967ccf35...):

  ```
  {"\\ĀĀ":{"tag":0,"￿\u2029":{"tag":5,"߿﻿\u2028ÿ﻿ÿ􏿿":[{"tag":4,"߿\u0007𐀀</":9223372036854775807},9007199254740993,"\u0007﻿\u001f\u2028>\u001f"]}},"tag":4}
  ```
- **rust** (len 164, sha 4fafa4826ee26547...):

  ```
  {"\\ĀĀ":{"tag":0,"￿ ":{"tag":5,"߿﻿ ÿ﻿ÿ􏿿":[{"tag":4,"߿\u0007𐀀</":9223372036854775807},9007199254740993,"\u0007﻿\u001f >\u001f"]}},"tag":4}
  ```
