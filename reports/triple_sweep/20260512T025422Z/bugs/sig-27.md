# Disagreement signature 27

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-C1-control,contains-SMP,contains-U+2028,contains-emoji`

**Count:** 14

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-C1-control, contains-SMP, contains-U+2028, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 10
  - nested: 3
  - array_order: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"😀 >￿": -137, " \u0007😀߿&\\": 241, "�\u0007߿ ￿": 181, "￿\"﻿/>": -279, "\u0000": 694, "𐀀􏿿ÿ߿": 639}`

Canonical per implementation:
- **python** (len 119, sha b223b6f2cd776224...):

  ```
  {"\u0000":694," \u0007😀߿&\\":241,"�\u0007߿ ￿":181,"￿\"﻿/>":-279,"𐀀􏿿ÿ߿":639,"😀 >￿":-137}
  ```
- **go** (len 125, sha c4fc471d17638d1d...):

  ```
  {"\u0000":694,"\u2028\u0007😀߿&\\":241,"�\u0007߿ ￿":181,"￿\"﻿/>":-279,"𐀀􏿿ÿ߿":639,"😀\u2028>￿":-137}
  ```
- **rust** (len 119, sha b223b6f2cd776224...):

  ```
  {"\u0000":694," \u0007😀߿&\\":241,"�\u0007߿ ￿":181,"￿\"﻿/>":-279,"𐀀􏿿ÿ߿":639,"😀 >￿":-137}
  ```

### Example 2

- generator: `nested`
- input: `[{"  \\😀": {" ߿&\u001f𐀀ÿ�": {"﻿\u0000": [-2147483648, 1.7976931348623157e+308, "𐀀�\\"], "tag": 3}, "tag": 2}, "tag": 7}, -2.5, "\"😀Ā \u0007"]`

Canonical per implementation:
- **python** (len 155, sha 93e91aa0e7e780a2...):

  ```
  [{"  \\😀":{"tag":2," ߿&\u001f𐀀ÿ�":{"tag":3,"﻿\u0000":[-2147483648,1.7976931348623157e+308,"𐀀�\\"]}},"tag":7},-2.5,"\"😀Ā \u0007"]
  ```
- **go** (len 158, sha be2a04d00d252646...):

  ```
  [{"  \\😀":{"tag":2,"\u2028߿&\u001f𐀀ÿ�":{"tag":3,"﻿\u0000":[-2147483648,1.7976931348623157e+308,"𐀀�\\"]}},"tag":7},-2.5,"\"😀Ā \u0007"]
  ```
- **rust** (len 155, sha 93e91aa0e7e780a2...):

  ```
  [{"  \\😀":{"tag":2," ߿&\u001f𐀀ÿ�":{"tag":3,"﻿\u0000":[-2147483648,1.7976931348623157e+308,"𐀀�\\"]}},"tag":7},-2.5,"\"😀Ā \u0007"]
  ```

### Example 3

- generator: `object_unicode_keys`
- input: `{"/􏿿\u0007\u001f": 876, "﻿😀": -188, "😀􏿿<\">﻿": -238, " ": -241}`

Canonical per implementation:
- **python** (len 80, sha 8d1cb4035625d5dc...):

  ```
  {"/􏿿\u0007\u001f":876," ":-241,"﻿😀":-188,"😀􏿿<\">﻿":-238}
  ```
- **go** (len 83, sha c34877dd50f4a42e...):

  ```
  {"/􏿿\u0007\u001f":876,"\u2028":-241,"﻿😀":-188,"😀􏿿<\">﻿":-238}
  ```
- **rust** (len 80, sha 8d1cb4035625d5dc...):

  ```
  {"/􏿿\u0007\u001f":876," ":-241,"﻿😀":-188,"😀􏿿<\">﻿":-238}
  ```
