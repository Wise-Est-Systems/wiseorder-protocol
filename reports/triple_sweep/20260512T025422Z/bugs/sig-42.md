# Disagreement signature 42

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-SMP,contains-U+2028,contains-emoji`

**Count:** 11

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-SMP, contains-U+2028, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 6
  - nested: 4
  - array_order: 1

## Examples

### Example 1

- generator: `nested`
- input: `[[[{"\u001f\\﻿ÿ ÿ ": 2147483647, "tag": 3}, 3.141592653589793, "😀>﻿ \u0000߿"], -2147483648, "𐀀"], 0, ">ÿ  "]`

Canonical per implementation:
- **python** (len 119, sha 67621c931051f573...):

  ```
  [[[{"\u001f\\﻿ÿ ÿ ":2147483647,"tag":3},3.141592653589793,"😀>﻿ \u0000߿"],-2147483648,"𐀀"],0,">ÿ  "]
  ```
- **go** (len 128, sha 15ea2786715603d9...):

  ```
  [[[{"\u001f\\﻿ÿ ÿ ":2147483647,"tag":3},3.141592653589793,"😀>﻿\u2028\u0000߿"],-2147483648,"𐀀"],0,">ÿ\u2028\u2028"]
  ```
- **rust** (len 119, sha 67621c931051f573...):

  ```
  [[[{"\u001f\\﻿ÿ ÿ ":2147483647,"tag":3},3.141592653589793,"😀>﻿ \u0000߿"],-2147483648,"𐀀"],0,">ÿ  "]
  ```

### Example 2

- generator: `object_unicode_keys`
- input: `{"\u001f߿𐀀�\"": -904, "<&<": 386, " >\u001f𐀀�": 731, "􏿿>😀\u0007﻿": 820, "\\􏿿ࠀ\u0000 \\\u0007": 718}`

Canonical per implementation:
- **python** (len 116, sha e194be65f26ca6ee...):

  ```
  {"\u001f߿𐀀�\"":-904," >\u001f𐀀�":731,"<&<":386,"\\􏿿ࠀ\u0000 \\\u0007":718,"􏿿>😀\u0007﻿":820}
  ```
- **go** (len 119, sha fab7c8518c91d54e...):

  ```
  {"\u001f߿𐀀�\"":-904," >\u001f𐀀�":731,"<&<":386,"\\􏿿ࠀ\u0000\u2028\\\u0007":718,"􏿿>😀\u0007﻿":820}
  ```
- **rust** (len 116, sha e194be65f26ca6ee...):

  ```
  {"\u001f߿𐀀�\"":-904," >\u001f𐀀�":731,"<&<":386,"\\􏿿ࠀ\u0000 \\\u0007":718,"􏿿>😀\u0007﻿":820}
  ```

### Example 3

- generator: `object_unicode_keys`
- input: `{"𐀀ࠀ\u001f": 165, "\u0007 �﻿": -74, "/߿>": 969, "\u0007ࠀ😀\u001f\u0007😀": -648, "﻿ÿ/😀 Ā": 198, " �\"\u0000": -306}`

Canonical per implementation:
- **python** (len 131, sha 4c4792f8e35bbad6...):

  ```
  {"\u0007 �﻿":-74,"\u0007ࠀ😀\u001f\u0007😀":-648,"/߿>":969," �\"\u0000":-306,"﻿ÿ/😀 Ā":198,"𐀀ࠀ\u001f":165}
  ```
- **go** (len 134, sha 0fc67f9c42ca8648...):

  ```
  {"\u0007 �﻿":-74,"\u0007ࠀ😀\u001f\u0007😀":-648,"/߿>":969,"\u2028�\"\u0000":-306,"﻿ÿ/😀 Ā":198,"𐀀ࠀ\u001f":165}
  ```
- **rust** (len 131, sha 4c4792f8e35bbad6...):

  ```
  {"\u0007 �﻿":-74,"\u0007ࠀ😀\u001f\u0007😀":-648,"/߿>":969," �\"\u0000":-306,"﻿ÿ/😀 Ā":198,"𐀀ࠀ\u001f":165}
  ```
