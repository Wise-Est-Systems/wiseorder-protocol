# Disagreement signature 93

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-DEL,contains-SMP,contains-U+2028,contains-emoji`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-DEL, contains-SMP, contains-U+2028, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - array_order: 1

## Examples

### Example 1

- generator: `array_order`
- input: `["ÿ𐀀😀﻿ ", "\u0007߿﻿ÿ/>", 0.001, 3.141592653589793, 0.2, "", "\u0000 "]`

Canonical per implementation:
- **python** (len 82, sha df2a04c70210fb7c...):

  ```
  ["ÿ𐀀😀﻿ ","\u0007߿﻿ÿ/>",0.001,3.141592653589793,0.2,"","\u0000 "]
  ```
- **go** (len 85, sha d1d2d3dfb446e2f8...):

  ```
  ["ÿ𐀀😀﻿\u2028","\u0007߿﻿ÿ/>",0.001,3.141592653589793,0.2,"","\u0000 "]
  ```
- **rust** (len 82, sha df2a04c70210fb7c...):

  ```
  ["ÿ𐀀😀﻿ ","\u0007߿﻿ÿ/>",0.001,3.141592653589793,0.2,"","\u0000 "]
  ```
