# Disagreement signature 47

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-C1-control,contains-SMP,contains-U+2028,contains-U+2029`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-C1-control, contains-SMP, contains-U+2028, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"\u0007\\\\ Ā<\u0007": 893, " ": 261, "߿Ā": 916, "𐀀  \u0007﻿Ā": -968, "&\u0007": -251, "<￿�􏿿߿ ": -531}`

Canonical per implementation:
- **python** (len 115, sha c15af303ba49034e...):

  ```
  {"\u0007\\\\ Ā<\u0007":893,"&\u0007":-251,"<￿�􏿿߿ ":-531,"߿Ā":916," ":261,"𐀀  \u0007﻿Ā":-968}
  ```
- **go** (len 121, sha 4f11e5101a337397...):

  ```
  {"\u0007\\\\ Ā<\u0007":893,"&\u0007":-251,"<￿�􏿿߿\u2029":-531,"߿Ā":916,"\u2028":261,"𐀀  \u0007﻿Ā":-968}
  ```
- **rust** (len 115, sha c15af303ba49034e...):

  ```
  {"\u0007\\\\ Ā<\u0007":893,"&\u0007":-251,"<￿�􏿿߿ ":-531,"߿Ā":916," ":261,"𐀀  \u0007﻿Ā":-968}
  ```
