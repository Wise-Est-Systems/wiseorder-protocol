# Disagreement signature 40

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-C1-control,contains-U+2028,contains-emoji`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-C1-control, contains-U+2028, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"<&": -753, "\u001f >": -802, "😀﻿ÿ\\Ā\\<😀": 108, "  ": -824, "\\�😀&߿﻿ࠀ": 772}`

Canonical per implementation:
- **python** (len 93, sha 52139bb762a24895...):

  ```
  {"\u001f >":-802,"  ":-824,"<&":-753,"\\�😀&߿﻿ࠀ":772,"😀﻿ÿ\\Ā\\<😀":108}
  ```
- **go** (len 96, sha 20c3fd3a24d0aafa...):

  ```
  {"\u001f\u2028>":-802,"  ":-824,"<&":-753,"\\�😀&߿﻿ࠀ":772,"😀﻿ÿ\\Ā\\<😀":108}
  ```
- **rust** (len 93, sha 52139bb762a24895...):

  ```
  {"\u001f >":-802,"  ":-824,"<&":-753,"\\�😀&߿﻿ࠀ":772,"😀﻿ÿ\\Ā\\<😀":108}
  ```
