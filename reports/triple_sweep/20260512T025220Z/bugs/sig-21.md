# Disagreement signature 21

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-SMP,contains-U+2028,contains-emoji`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-SMP, contains-U+2028, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 1

## Examples

### Example 1

- generator: `nested`
- input: `[[[{"\u001f\\﻿ÿ ÿ ": 2147483647, "tag": 3}, 3.141592653589793, "😀>﻿ \u0000߿"], -2147483648, "𐀀"], 0, ">ÿ  "]`

Canonical per implementation:
- **python** (len 119, sha 67621c931051f573...):

  ```
  [[[{"\u001f\\﻿ÿ ÿ ":2147483647,"tag":3},3.141592653589793,"😀>﻿ \u0000߿"],-2147483648,"𐀀"],0,">ÿ  "]
  ```
- **go** (len 128, sha 15ea2786715603d9...):

  ```
  [[[{"\u001f\\﻿ÿ ÿ ":2147483647,"tag":3},3.141592653589793,"😀>﻿\u2028\u0000߿"],-2147483648,"𐀀"],0,">ÿ\u2028\u2028"]
  ```
- **rust** (len 119, sha 67621c931051f573...):

  ```
  [[[{"\u001f\\﻿ÿ ÿ ":2147483647,"tag":3},3.141592653589793,"😀>﻿ \u0000߿"],-2147483648,"𐀀"],0,">ÿ  "]
  ```
