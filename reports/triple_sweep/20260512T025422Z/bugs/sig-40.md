# Disagreement signature 40

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-DEL,contains-SMP,contains-U+2028,contains-emoji`

**Count:** 12

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-DEL, contains-SMP, contains-U+2028, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 6
  - nested: 3
  - array_order: 3

## Examples

### Example 1

- generator: `nested`
- input: `{"\\𐀀😀 ": {"\"￿&": [{"&߿\u001f߿�>": 0.3, "tag": 9}, 0.1, ">>﻿𐀀\""], "tag": 0}, "tag": 3}`

Canonical per implementation:
- **python** (len 97, sha 44a968893b5b3f1c...):

  ```
  {"\\𐀀😀 ":{"tag":0,"\"￿&":[{"&߿\u001f߿�>":0.3,"tag":9},0.1,">>﻿𐀀\""]},"tag":3}
  ```
- **go** (len 100, sha 0b5f76b57c424dd9...):

  ```
  {"\\𐀀😀\u2028":{"tag":0,"\"￿&":[{"&߿\u001f߿�>":0.3,"tag":9},0.1,">>﻿𐀀\""]},"tag":3}
  ```
- **rust** (len 97, sha 44a968893b5b3f1c...):

  ```
  {"\\𐀀😀 ":{"tag":0,"\"￿&":[{"&߿\u001f߿�>":0.3,"tag":9},0.1,">>﻿𐀀\""]},"tag":3}
  ```

### Example 2

- generator: `object_unicode_keys`
- input: `{"ÿ􏿿�": -591, "�ÿ ": -896, "\\&﻿\u001f": -945, "Ā﻿": 576, "Ā\u0007😀": -831}`

Canonical per implementation:
- **python** (len 87, sha 38be89f62b84b3df...):

  ```
  {"\\&﻿\u001f":-945,"ÿ􏿿�":-591,"Ā\u0007😀":-831,"Ā﻿":576,"�ÿ ":-896}
  ```
- **go** (len 90, sha 8af3880a85a92cb2...):

  ```
  {"\\&﻿\u001f":-945,"ÿ􏿿�":-591,"Ā\u0007😀":-831,"Ā﻿":576,"�ÿ\u2028":-896}
  ```
- **rust** (len 87, sha 38be89f62b84b3df...):

  ```
  {"\\&﻿\u001f":-945,"ÿ􏿿�":-591,"Ā\u0007😀":-831,"Ā﻿":576,"�ÿ ":-896}
  ```

### Example 3

- generator: `object_unicode_keys`
- input: `{"\u001f😀/\u0007﻿😀😀": 445, "ÿ Ā😀": 169, "\u0007𐀀 \u0007": -401, "/": 540, " \u001f": -599, "￿\u0007 􏿿&": 378}`

Canonical per implementation:
- **python** (len 127, sha dc456f014e0bb773...):

  ```
  {"\u0007𐀀 \u0007":-401,"\u001f😀/\u0007﻿😀😀":445," \u001f":-599,"/":540,"ÿ Ā😀":169,"￿\u0007 􏿿&":378}
  ```
- **go** (len 133, sha daf3cd6e91d6dc2d...):

  ```
  {"\u0007𐀀 \u0007":-401,"\u001f😀/\u0007﻿😀😀":445," \u001f":-599,"/":540,"ÿ\u2028Ā😀":169,"￿\u0007\u2028􏿿&":378}
  ```
- **rust** (len 127, sha dc456f014e0bb773...):

  ```
  {"\u0007𐀀 \u0007":-401,"\u001f😀/\u0007﻿😀😀":445," \u001f":-599,"/":540,"ÿ Ā😀":169,"￿\u0007 􏿿&":378}
  ```
