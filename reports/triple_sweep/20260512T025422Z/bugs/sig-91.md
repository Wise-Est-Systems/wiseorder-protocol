# Disagreement signature 91

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-C1-control,contains-U+2028,contains-U+2029,contains-emoji`

**Count:** 5

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-C1-control, contains-U+2028, contains-U+2029, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 2
  - nested: 2
  - array_order: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"﻿�": -129, "\u001f\"😀￿& ": -926, "  </￿\u0007￿": 693, " \u0000ÿ ": 423}`

Canonical per implementation:
- **python** (len 90, sha fa1150f98d3c0c35...):

  ```
  {"\u001f\"😀￿& ":-926," \u0000ÿ ":423,"  </￿\u0007￿":693,"﻿�":-129}
  ```
- **go** (len 102, sha c48344189b35d678...):

  ```
  {"\u001f\"😀￿&\u2029":-926,"\u2028\u0000ÿ ":423,"\u2028\u2028</￿\u0007￿":693,"﻿�":-129}
  ```
- **rust** (len 90, sha fa1150f98d3c0c35...):

  ```
  {"\u001f\"😀￿& ":-926," \u0000ÿ ":423,"  </￿\u0007￿":693,"﻿�":-129}
  ```

### Example 2

- generator: `array_order`
- input: `[-98, "\"�\u0007 ", -55, "😀\"😀ÿ\u0007 ", "￿﻿\u0000\"😀\"/ ", 1]`

Canonical per implementation:
- **python** (len 79, sha 9912221a8fd4d5e8...):

  ```
  [-98,"\"�\u0007 ",-55,"😀\"😀ÿ\u0007 ","￿﻿\u0000\"😀\"/ ",1]
  ```
- **go** (len 85, sha 445e9db03d189892...):

  ```
  [-98,"\"�\u0007\u2029",-55,"😀\"😀ÿ\u0007 ","￿﻿\u0000\"😀\"/\u2028",1]
  ```
- **rust** (len 79, sha 9912221a8fd4d5e8...):

  ```
  [-98,"\"�\u0007 ",-55,"😀\"😀ÿ\u0007 ","￿﻿\u0000\"😀\"/ ",1]
  ```

### Example 3

- generator: `nested`
- input: `[[{"ÿ\u0007﻿ \"😀߿": [{"﻿": -2147483648, "tag": 7}, 2.718281828459045, "\\"], "tag": 0}, -2147483648, "ÿ>😀"], -1, "&/﻿߿/ÿ ￿"]`

Canonical per implementation:
- **python** (len 137, sha 8d92f587b5b91e1a...):

  ```
  [[{"tag":0,"ÿ\u0007﻿ \"😀߿":[{"tag":7,"﻿":-2147483648},2.718281828459045,"\\"]},-2147483648,"ÿ>😀"],-1,"&/﻿߿/ÿ ￿"]
  ```
- **go** (len 143, sha e3bb95ebb809ea62...):

  ```
  [[{"tag":0,"ÿ\u0007﻿\u2028\"😀߿":[{"tag":7,"﻿":-2147483648},2.718281828459045,"\\"]},-2147483648,"ÿ>😀"],-1,"&/﻿߿/ÿ\u2029￿"]
  ```
- **rust** (len 137, sha 8d92f587b5b91e1a...):

  ```
  [[{"tag":0,"ÿ\u0007﻿ \"😀߿":[{"tag":7,"﻿":-2147483648},2.718281828459045,"\\"]},-2147483648,"ÿ>😀"],-1,"&/﻿߿/ÿ ￿"]
  ```
