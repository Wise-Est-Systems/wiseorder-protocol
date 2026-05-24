# Disagreement signature 20

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-C1-control,contains-DEL,contains-SMP,contains-U+2029`

**Count:** 15

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-C1-control, contains-DEL, contains-SMP, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 7
  - object_unicode_keys: 5
  - array_order: 3

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

### Example 2

- generator: `nested`
- input: `{"\\\u001f􏿿􏿿\"Ā􏿿": [{"\\Ā￿": {" ࠀ": {" \\\u001f߿": 1, "tag": 0}, "tag": 6}, "tag": 7}, -0.0, "/﻿/ÿ�\""], "tag": 0}`

Canonical per implementation:
- **python** (len 130, sha 6380b881655b4cda...):

  ```
  {"\\\u001f􏿿􏿿\"Ā􏿿":[{"tag":7,"\\Ā￿":{"tag":6," ࠀ":{"tag":0," \\\u001f߿":1}}},-0.0,"/﻿/ÿ�\""],"tag":0}
  ```
- **go** (len 133, sha 530a76f2833323e0...):

  ```
  {"\\\u001f􏿿􏿿\"Ā􏿿":[{"tag":7,"\\Ā￿":{"tag":6,"\u2029ࠀ":{"tag":0," \\\u001f߿":1}}},-0.0,"/﻿/ÿ�\""],"tag":0}
  ```
- **rust** (len 130, sha 6380b881655b4cda...):

  ```
  {"\\\u001f􏿿􏿿\"Ā􏿿":[{"tag":7,"\\Ā￿":{"tag":6," ࠀ":{"tag":0," \\\u001f߿":1}}},-0.0,"/﻿/ÿ�\""],"tag":0}
  ```

### Example 3

- generator: `nested`
- input: `[[{"ÿ�<": {"􏿿\u0000 <ÿ>߿": 0.3333333333333333, "tag": 8}, "tag": 3}, -1, "߿\u0000ࠀ﻿"], 2147483647, "�<�Ā\u001f�\u0000"]`

Canonical per implementation:
- **python** (len 135, sha 3eb104d713d10413...):

  ```
  [[{"tag":3,"ÿ�<":{"tag":8,"􏿿\u0000 <ÿ>߿":0.3333333333333333}},-1,"߿\u0000ࠀ﻿"],2147483647,"�<�Ā\u001f�\u0000"]
  ```
- **go** (len 138, sha dcdba8e8fb0bde8b...):

  ```
  [[{"tag":3,"ÿ�<":{"tag":8,"􏿿\u0000\u2029<ÿ>߿":0.3333333333333333}},-1,"߿\u0000ࠀ﻿"],2147483647,"�<�Ā\u001f�\u0000"]
  ```
- **rust** (len 135, sha 3eb104d713d10413...):

  ```
  [[{"tag":3,"ÿ�<":{"tag":8,"􏿿\u0000 <ÿ>߿":0.3333333333333333}},-1,"߿\u0000ࠀ﻿"],2147483647,"�<�Ā\u001f�\u0000"]
  ```
