# Disagreement signature 17

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-C1-control,contains-DEL,contains-SMP,contains-U+2028,contains-U+2029`

**Count:** 16

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-C1-control, contains-DEL, contains-SMP, contains-U+2028, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 11
  - array_order: 2
  - nested: 2
  - mixed_object: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"\u0000": -594, "/Ā￿� ": 491, "   \u0007  Ā": 564, "\u0007\u0007": 631, "߿\u0000﻿>﻿􏿿\u0000": 789, "\u0000𐀀\u001f": -375}`

Canonical per implementation:
- **python** (len 140, sha 387d4cf4f5dc5a65...):

  ```
  {"\u0000𐀀\u001f":-375,"\u0007\u0007":631,"/Ā￿� ":491,"\u0000":-594,"߿\u0000﻿>﻿􏿿\u0000":789,"   \u0007  Ā":564}
  ```
- **go** (len 152, sha 097ff89938d7166f...):

  ```
  {"\u0000𐀀\u001f":-375,"\u0007\u0007":631,"/Ā￿�\u2029":491,"\u0000":-594,"߿\u0000﻿>﻿􏿿\u0000":789,"\u2029 \u2028\u0007\u2028 Ā":564}
  ```
- **rust** (len 140, sha 387d4cf4f5dc5a65...):

  ```
  {"\u0000𐀀\u001f":-375,"\u0007\u0007":631,"/Ā￿� ":491,"\u0000":-594,"߿\u0000﻿>﻿􏿿\u0000":789,"   \u0007  Ā":564}
  ```

### Example 2

- generator: `array_order`
- input: `["߿﻿\u001f<􏿿 ﻿", "\u0000>\u0007\\𐀀\\", "/􏿿", "߿ 􏿿", 9, "ࠀ\\􏿿ÿ\"\u001f􏿿 ", "  �𐀀ࠀ>", -0.0]`

Canonical per implementation:
- **python** (len 127, sha b3dd583f8774555e...):

  ```
  ["߿﻿\u001f<􏿿 ﻿","\u0000>\u0007\\𐀀\\","/􏿿","߿ 􏿿",9,"ࠀ\\􏿿ÿ\"\u001f􏿿 ","  �𐀀ࠀ>",-0.0]
  ```
- **go** (len 139, sha f35e44736154a6de...):

  ```
  ["߿﻿\u001f<􏿿\u2029﻿","\u0000>\u0007\\𐀀\\","/􏿿","߿\u2029􏿿",9,"ࠀ\\􏿿ÿ\"\u001f􏿿 ","\u2028\u2029�𐀀ࠀ>",-0.0]
  ```
- **rust** (len 127, sha b3dd583f8774555e...):

  ```
  ["߿﻿\u001f<􏿿 ﻿","\u0000>\u0007\\𐀀\\","/􏿿","߿ 􏿿",9,"ࠀ\\􏿿ÿ\"\u001f􏿿 ","  �𐀀ࠀ>",-0.0]
  ```

### Example 3

- generator: `object_unicode_keys`
- input: `{">\u001f𐀀ĀĀ߿": 871, "﻿": -991, "< ﻿﻿": 261, " \u0000 􏿿": 990, " \\𐀀&ࠀ ": -835}`

Canonical per implementation:
- **python** (len 99, sha e3dd8a02b28ebdb8...):

  ```
  {" \u0000 􏿿":990,"< ﻿﻿":261,">\u001f𐀀ĀĀ߿":871," \\𐀀&ࠀ ":-835,"﻿":-991}
  ```
- **go** (len 105, sha e0b2907272e05a27...):

  ```
  {" \u0000 􏿿":990,"< ﻿﻿":261,">\u001f𐀀ĀĀ߿":871,"\u2028\\𐀀&ࠀ\u2029":-835,"﻿":-991}
  ```
- **rust** (len 99, sha e3dd8a02b28ebdb8...):

  ```
  {" \u0000 􏿿":990,"< ﻿﻿":261,">\u001f𐀀ĀĀ߿":871," \\𐀀&ࠀ ":-835,"﻿":-991}
  ```
