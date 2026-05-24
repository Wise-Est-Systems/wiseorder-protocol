# Disagreement signature 24

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-C1-control,contains-SMP,contains-U+2028`

**Count:** 2

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-C1-control, contains-SMP, contains-U+2028

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 2

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{" ﻿ \u0000 ": -493, "\"𐀀>/": -825, "￿&\u0007": 812, "\\�\u0007\u001f﻿": 827}`

Canonical per implementation:
- **python** (len 87, sha bcd5c99b7dcee729...):

  ```
  {"\"𐀀>/":-825,"\\�\u0007\u001f﻿":827," ﻿ \u0000 ":-493,"￿&\u0007":812}
  ```
- **go** (len 93, sha 959d128f719ab79b...):

  ```
  {"\"𐀀>/":-825,"\\�\u0007\u001f﻿":827,"\u2028﻿ \u0000\u2028":-493,"￿&\u0007":812}
  ```
- **rust** (len 87, sha bcd5c99b7dcee729...):

  ```
  {"\"𐀀>/":-825,"\\�\u0007\u001f﻿":827," ﻿ \u0000 ":-493,"￿&\u0007":812}
  ```

### Example 2

- generator: `object_unicode_keys`
- input: `{"\"\u0000 ﻿\"߿<\u0007": -901, "ࠀ ߿<": 780, "￿￿߿𐀀\\": 943}`

Canonical per implementation:
- **python** (len 73, sha 64549ce92f55669b...):

  ```
  {"\"\u0000 ﻿\"߿<\u0007":-901,"ࠀ ߿<":780,"￿￿߿𐀀\\":943}
  ```
- **go** (len 79, sha 78a8ade60de9b6a6...):

  ```
  {"\"\u0000\u2028﻿\"߿<\u0007":-901,"ࠀ\u2028߿<":780,"￿￿߿𐀀\\":943}
  ```
- **rust** (len 73, sha 64549ce92f55669b...):

  ```
  {"\"\u0000 ﻿\"߿<\u0007":-901,"ࠀ ߿<":780,"￿￿߿𐀀\\":943}
  ```
