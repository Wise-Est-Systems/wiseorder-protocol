# Disagreement signature 76

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-DEL,contains-SMP,contains-U+2028`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-DEL, contains-SMP, contains-U+2028

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{" \u0007<ÿ<": 18, "߿\u001fĀ\u0007<": 178, "&\\﻿/": 13, "􏿿": 806, "﻿Ā\" ": -356}`

Canonical per implementation:
- **python** (len 87, sha 33316c7a112c9a88...):

  ```
  {"&\\﻿/":13,"߿\u001fĀ\u0007<":178," \u0007<ÿ<":18,"﻿Ā\" ":-356,"􏿿":806}
  ```
- **go** (len 93, sha dd06f52deea87a56...):

  ```
  {"&\\﻿/":13,"߿\u001fĀ\u0007<":178,"\u2028\u0007<ÿ<":18,"﻿Ā\"\u2028":-356,"􏿿":806}
  ```
- **rust** (len 87, sha 33316c7a112c9a88...):

  ```
  {"&\\﻿/":13,"߿\u001fĀ\u0007<":178," \u0007<ÿ<":18,"﻿Ā\" ":-356,"􏿿":806}
  ```
