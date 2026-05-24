# Disagreement signature 25

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-C1-control,contains-DEL,contains-SMP,contains-U+2029`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-C1-control, contains-DEL, contains-SMP, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"\u001f ﻿\u0000": 771, "􏿿 ": -277, "ࠀ𐀀 \u0000߿􏿿": 988, "&\u0000/߿\u001f": -589, "\u0000﻿&��￿ ": 25, "&\\߿": -687}`

Canonical per implementation:
- **python** (len 138, sha a25254344d9d3f88...):

  ```
  {"\u0000﻿&��￿ ":25,"\u001f ﻿\u0000":771,"&\u0000/߿\u001f":-589,"&\\߿":-687,"ࠀ𐀀 \u0000߿􏿿":988,"􏿿 ":-277}
  ```
- **go** (len 150, sha 21efbbf7beb0377a...):

  ```
  {"\u0000﻿&��￿\u2029":25,"\u001f\u2029﻿\u0000":771,"&\u0000/߿\u001f":-589,"&\\߿":-687,"ࠀ𐀀\u2029\u0000߿􏿿":988,"􏿿\u2029":-277}
  ```
- **rust** (len 138, sha a25254344d9d3f88...):

  ```
  {"\u0000﻿&��￿ ":25,"\u001f ﻿\u0000":771,"&\u0000/߿\u001f":-589,"&\\߿":-687,"ࠀ𐀀 \u0000߿􏿿":988,"􏿿 ":-277}
  ```
