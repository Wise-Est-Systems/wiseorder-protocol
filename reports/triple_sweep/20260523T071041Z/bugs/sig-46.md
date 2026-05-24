# Disagreement signature 46

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-SMP,contains-U+2028,contains-bigint>2^53`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-SMP, contains-U+2028, contains-bigint>2^53

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 1

## Examples

### Example 1

- generator: `nested`
- input: `[{"􏿿\\": [{"﻿﻿\u0000𐀀": 9223372036854775807, "tag": 6}, -0.0, "􏿿 "], "tag": 1}, -1, "\"Ā"]`

Canonical per implementation:
- **python** (len 96, sha a2d62e86485bcf14...):

  ```
  [{"tag":1,"􏿿\\":[{"tag":6,"﻿﻿\u0000𐀀":9223372036854775807},-0.0,"􏿿 "]},-1,"\"Ā"]
  ```
- **go** (len 99, sha 88c4c530e5a61068...):

  ```
  [{"tag":1,"􏿿\\":[{"tag":6,"﻿﻿\u0000𐀀":9223372036854775807},-0.0,"􏿿\u2028"]},-1,"\"Ā"]
  ```
- **rust** (len 96, sha a2d62e86485bcf14...):

  ```
  [{"tag":1,"􏿿\\":[{"tag":6,"﻿﻿\u0000𐀀":9223372036854775807},-0.0,"􏿿 "]},-1,"\"Ā"]
  ```
