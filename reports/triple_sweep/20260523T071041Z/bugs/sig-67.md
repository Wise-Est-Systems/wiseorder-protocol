# Disagreement signature 67

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-SMP,contains-U+2028,contains-emoji`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-SMP, contains-U+2028, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"😀￿𐀀\u0007": -242, " \\>﻿😀 ": 774, "￿/\u001f": 109, " \\߿\u0007􏿿ÿ�߿": 726}`

Canonical per implementation:
- **python** (len 93, sha c4434e39e5ad0db3...):

  ```
  {" \\>﻿😀 ":774," \\߿\u0007􏿿ÿ�߿":726,"￿/\u001f":109,"😀￿𐀀\u0007":-242}
  ```
- **go** (len 96, sha 9d5e631d458325ae...):

  ```
  {" \\>﻿😀 ":774,"\u2028\\߿\u0007􏿿ÿ�߿":726,"￿/\u001f":109,"😀￿𐀀\u0007":-242}
  ```
- **rust** (len 93, sha c4434e39e5ad0db3...):

  ```
  {" \\>﻿😀 ":774," \\߿\u0007􏿿ÿ�߿":726,"￿/\u001f":109,"😀￿𐀀\u0007":-242}
  ```
