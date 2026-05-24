# Disagreement signature 7

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-C1-control,contains-SMP,contains-U+2028,contains-U+2029,contains-emoji`

**Count:** 23

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-C1-control, contains-SMP, contains-U+2028, contains-U+2029, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 14
  - nested: 8
  - array_order: 1

## Examples

### Example 1

- generator: `array_order`
- input: `[" \\ÿ ￿&Ā", "𐀀/ÿ\u0000", 3.141592653589793, "😀￿﻿", "﻿\u0000", 17, "ÿ􏿿\u001f\u0007>", 1e+17]`

Canonical per implementation:
- **python** (len 114, sha c170dc4538def478...):

  ```
  [" \\ÿ ￿&Ā","𐀀/ÿ\u0000",3.141592653589793,"😀￿﻿","﻿\u0000",17,"ÿ􏿿\u001f\u0007>",1e+17]
  ```
- **go** (len 120, sha f09f50f05be94002...):

  ```
  ["\u2029\\ÿ\u2028￿&Ā","𐀀/ÿ\u0000",3.141592653589793,"😀￿﻿","﻿\u0000",17,"ÿ􏿿\u001f\u0007>",1e+17]
  ```
- **rust** (len 114, sha c170dc4538def478...):

  ```
  [" \\ÿ ￿&Ā","𐀀/ÿ\u0000",3.141592653589793,"😀￿﻿","﻿\u0000",17,"ÿ􏿿\u001f\u0007>",1e+17]
  ```

### Example 2

- generator: `object_unicode_keys`
- input: `{"😀ÿ\" >￿﻿": 723, "\u001f  􏿿 ": -908, "𐀀/< ߿Ā\u001f": -161, "�\\  &\u0007😀": 989, "ࠀ&\u0000߿": 578}`

Canonical per implementation:
- **python** (len 122, sha 181e7579c643b3b6...):

  ```
  {"\u001f  􏿿 ":-908,"ࠀ&\u0000߿":578,"�\\  &\u0007😀":989,"𐀀/< ߿Ā\u001f":-161,"😀ÿ\" >￿﻿":723}
  ```
- **go** (len 131, sha 58c40add30d2eac7...):

  ```
  {"\u001f  􏿿\u2029":-908,"ࠀ&\u0000߿":578,"�\\\u2028 &\u0007😀":989,"𐀀/< ߿Ā\u001f":-161,"😀ÿ\"\u2028>￿﻿":723}
  ```
- **rust** (len 122, sha 181e7579c643b3b6...):

  ```
  {"\u001f  􏿿 ":-908,"ࠀ&\u0000߿":578,"�\\  &\u0007😀":989,"𐀀/< ߿Ā\u001f":-161,"😀ÿ\" >￿﻿":723}
  ```

### Example 3

- generator: `object_unicode_keys`
- input: `{"𐀀\u001f😀&😀Ā\u001f": -732, "\u0000 😀߿﻿ \u001f": -590, "<< ߿ /": 612}`

Canonical per implementation:
- **python** (len 89, sha 2c06f2f83f20a1dd...):

  ```
  {"\u0000 😀߿﻿ \u001f":-590,"<< ߿ /":612,"𐀀\u001f😀&😀Ā\u001f":-732}
  ```
- **go** (len 98, sha 39b3a0dd36d81f7f...):

  ```
  {"\u0000 😀߿﻿\u2028\u001f":-590,"<<\u2029߿\u2029/":612,"𐀀\u001f😀&😀Ā\u001f":-732}
  ```
- **rust** (len 89, sha 2c06f2f83f20a1dd...):

  ```
  {"\u0000 😀߿﻿ \u001f":-590,"<< ߿ /":612,"𐀀\u001f😀&😀Ā\u001f":-732}
  ```
