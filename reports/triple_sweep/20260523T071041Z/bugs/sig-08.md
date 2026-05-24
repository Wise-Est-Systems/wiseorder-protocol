# Disagreement signature 8

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-C1-control,contains-SMP,contains-U+2028,contains-emoji`

**Count:** 3

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-C1-control, contains-SMP, contains-U+2028, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 3

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{" \"\u001f�ÿ﻿�": 249, " \u0007": -906, ">Ā": 412, "😀\u001f􏿿 ": 921, ">&\u0007\u001f ￿􏿿": -349, "ࠀĀ": -148}`

Canonical per implementation:
- **python** (len 128, sha 222aa38f21eea164...):

  ```
  {" \"\u001f�ÿ﻿�":249,">&\u0007\u001f ￿􏿿":-349,">Ā":412,"ࠀĀ":-148," \u0007":-906,"😀\u001f􏿿 ":921}
  ```
- **go** (len 134, sha b4adb2332267a5df...):

  ```
  {" \"\u001f�ÿ﻿�":249,">&\u0007\u001f\u2028￿􏿿":-349,">Ā":412,"ࠀĀ":-148,"\u2028\u0007":-906,"😀\u001f􏿿 ":921}
  ```
- **rust** (len 128, sha 222aa38f21eea164...):

  ```
  {" \"\u001f�ÿ﻿�":249,">&\u0007\u001f ￿􏿿":-349,">Ā":412,"ࠀĀ":-148," \u0007":-906,"😀\u001f􏿿 ":921}
  ```

### Example 2

- generator: `object_unicode_keys`
- input: `{" \\\u0000😀": -40, "\"�😀 >􏿿": -214, "ࠀ\"/𐀀": 922, "\u0007Ā\u0007\u0000": 896, "﻿": 812, "\"߿": -947}`

Canonical per implementation:
- **python** (len 114, sha df6b24fe54090557...):

  ```
  {"\u0007Ā\u0007\u0000":896,"\"߿":-947,"\"�😀 >􏿿":-214,"ࠀ\"/𐀀":922," \\\u0000😀":-40,"﻿":812}
  ```
- **go** (len 117, sha 33499f83cf181f14...):

  ```
  {"\u0007Ā\u0007\u0000":896,"\"߿":-947,"\"�😀 >􏿿":-214,"ࠀ\"/𐀀":922,"\u2028\\\u0000😀":-40,"﻿":812}
  ```
- **rust** (len 114, sha df6b24fe54090557...):

  ```
  {"\u0007Ā\u0007\u0000":896,"\"߿":-947,"\"�😀 >􏿿":-214,"ࠀ\"/𐀀":922," \\\u0000😀":-40,"﻿":812}
  ```

### Example 3

- generator: `object_unicode_keys`
- input: `{" ": -392, "𐀀􏿿𐀀􏿿😀�\"": -818, "\\﻿": -346, "Ā𐀀</<\\&😀": -938, "￿﻿\u0000": -45, "\u001fĀ￿Ā": -129}`

Canonical per implementation:
- **python** (len 124, sha 5f77fb49a6bd7601...):

  ```
  {"\u001fĀ￿Ā":-129,"\\﻿":-346,"Ā𐀀</<\\&😀":-938," ":-392,"￿﻿\u0000":-45,"𐀀􏿿𐀀􏿿😀�\"":-818}
  ```
- **go** (len 127, sha c2397b116244a045...):

  ```
  {"\u001fĀ￿Ā":-129,"\\﻿":-346,"Ā𐀀</<\\&😀":-938,"\u2028":-392,"￿﻿\u0000":-45,"𐀀􏿿𐀀􏿿😀�\"":-818}
  ```
- **rust** (len 124, sha 5f77fb49a6bd7601...):

  ```
  {"\u001fĀ￿Ā":-129,"\\﻿":-346,"Ā𐀀</<\\&😀":-938," ":-392,"￿﻿\u0000":-45,"𐀀􏿿𐀀􏿿😀�\"":-818}
  ```
