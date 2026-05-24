# Disagreement signature 5

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
- input: `{"\u0000𐀀﻿Ā\u0007<<": -869, "\"Ā\u001fĀ ￿": -233, " \" 􏿿": -309, "\u0000> ￿": 917, "\u0007\u001f": 890, "ࠀ\u0000\\\u001f𐀀/𐀀": -766}`

Canonical per implementation:
- **python** (len 152, sha 0b56132312a1d75c...):

  ```
  {"\u0000> ￿":917,"\u0000𐀀﻿Ā\u0007<<":-869,"\u0007\u001f":890,"\"Ā\u001fĀ ￿":-233,"ࠀ\u0000\\\u001f𐀀/𐀀":-766," \" 􏿿":-309}
  ```
- **go** (len 158, sha 90d48585ae1f5859...):

  ```
  {"\u0000> ￿":917,"\u0000𐀀﻿Ā\u0007<<":-869,"\u0007\u001f":890,"\"Ā\u001fĀ ￿":-233,"ࠀ\u0000\\\u001f𐀀/𐀀":-766,"\u2029\"\u2029􏿿":-309}
  ```
- **rust** (len 152, sha 0b56132312a1d75c...):

  ```
  {"\u0000> ￿":917,"\u0000𐀀﻿Ā\u0007<<":-869,"\u0007\u001f":890,"\"Ā\u001fĀ ￿":-233,"ࠀ\u0000\\\u001f𐀀/𐀀":-766," \" 􏿿":-309}
  ```
