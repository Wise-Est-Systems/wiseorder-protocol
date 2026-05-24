# Disagreement signature 24

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-SMP,contains-U+2028,contains-U+2029,contains-emoji`

**Count:** 14

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-SMP, contains-U+2028, contains-U+2029, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 10
  - nested: 3
  - array_order: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"&ÿ 𐀀﻿": 167, " \u0007": 924, "ÿ😀ࠀࠀ/": 325, "﻿􏿿😀\u001f": 365}`

Canonical per implementation:
- **python** (len 81, sha 2d9f64ee50e4146f...):

  ```
  {"&ÿ 𐀀﻿":167,"ÿ😀ࠀࠀ/":325," \u0007":924,"﻿􏿿😀\u001f":365}
  ```
- **go** (len 87, sha 77cdcccb430e226d...):

  ```
  {"&ÿ\u2028𐀀﻿":167,"ÿ😀ࠀࠀ/":325,"\u2029\u0007":924,"﻿􏿿😀\u001f":365}
  ```
- **rust** (len 81, sha 2d9f64ee50e4146f...):

  ```
  {"&ÿ 𐀀﻿":167,"ÿ😀ࠀࠀ/":325," \u0007":924,"﻿􏿿😀\u001f":365}
  ```

### Example 2

- generator: `object_unicode_keys`
- input: `{"Ā�ÿ􏿿𐀀": -387, "\u0000�﻿\\Ā": 176, "\\/😀/߿􏿿ÿ\u0000": 194, "ࠀ": -772, "  &\u0007\u0007\u0007😀": -920}`

Canonical per implementation:
- **python** (len 124, sha af91793a975cb734...):

  ```
  {"\u0000�﻿\\Ā":176,"\\/😀/߿􏿿ÿ\u0000":194,"Ā�ÿ􏿿𐀀":-387,"ࠀ":-772,"  &\u0007\u0007\u0007😀":-920}
  ```
- **go** (len 130, sha 89e92a91afdfd35d...):

  ```
  {"\u0000�﻿\\Ā":176,"\\/😀/߿􏿿ÿ\u0000":194,"Ā�ÿ􏿿𐀀":-387,"ࠀ":-772,"\u2028\u2029&\u0007\u0007\u0007😀":-920}
  ```
- **rust** (len 124, sha af91793a975cb734...):

  ```
  {"\u0000�﻿\\Ā":176,"\\/😀/߿􏿿ÿ\u0000":194,"Ā�ÿ􏿿𐀀":-387,"ࠀ":-772,"  &\u0007\u0007\u0007😀":-920}
  ```

### Example 3

- generator: `object_unicode_keys`
- input: `{"😀\"\u0000 ࠀ\u001f\u001f": -366, "￿<\u001f ": 724, "﻿& 􏿿": 916, "߿<": 558}`

Canonical per implementation:
- **python** (len 85, sha a74aa0b1434d2311...):

  ```
  {"߿<":558,"﻿& 􏿿":916,"￿<\u001f ":724,"😀\"\u0000 ࠀ\u001f\u001f":-366}
  ```
- **go** (len 91, sha 4d8ffc5c0f1d080a...):

  ```
  {"߿<":558,"﻿&\u2029􏿿":916,"￿<\u001f\u2028":724,"😀\"\u0000 ࠀ\u001f\u001f":-366}
  ```
- **rust** (len 85, sha a74aa0b1434d2311...):

  ```
  {"߿<":558,"﻿& 􏿿":916,"￿<\u001f ":724,"😀\"\u0000 ࠀ\u001f\u001f":-366}
  ```
