# Disagreement signature 68

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-C1-control,contains-DEL,contains-U+2028,contains-U+2029`

**Count:** 7

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-C1-control, contains-DEL, contains-U+2028, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 6
  - nested: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"﻿": -673, "� < ": -169, "<߿>": -574, "\"﻿ࠀ\u001f\">": 446, " &&\u0000<<\u0007": -781, "߿\u001f\u001f�\u0007Ā߿": 203}`

Canonical per implementation:
- **python** (len 130, sha bc9c65ef7936038d...):

  ```
  {"\"﻿ࠀ\u001f\">":446,"<߿>":-574," &&\u0000<<\u0007":-781,"߿\u001f\u001f�\u0007Ā߿":203,"﻿":-673,"� < ":-169}
  ```
- **go** (len 136, sha b85b14cbc4d4db3a...):

  ```
  {"\"﻿ࠀ\u001f\">":446,"<߿>":-574,"\u2028&&\u0000<<\u0007":-781,"߿\u001f\u001f�\u0007Ā߿":203,"﻿":-673,"� <\u2029":-169}
  ```
- **rust** (len 130, sha bc9c65ef7936038d...):

  ```
  {"\"﻿ࠀ\u001f\">":446,"<߿>":-574," &&\u0000<<\u0007":-781,"߿\u001f\u001f�\u0007Ā߿":203,"﻿":-673,"� < ":-169}
  ```

### Example 2

- generator: `nested`
- input: `[[{" �\u0000Ā": [9007199254740992, 0, "\""], "tag": 1}, 5e-324, "﻿ࠀ <\u001f <"], 0.3, " "]`

Canonical per implementation:
- **python** (len 97, sha e3f8d3f1bf821ae5...):

  ```
  [[{"tag":1," �\u0000Ā":[9007199254740992,0,"\""]},5e-324,"﻿ࠀ <\u001f <"],0.3," "]
  ```
- **go** (len 103, sha 260ff31f690aba7f...):

  ```
  [[{"tag":1,"\u2028�\u0000Ā":[9007199254740992,0,"\""]},5e-324,"﻿ࠀ <\u001f\u2029<"],0.3," "]
  ```
- **rust** (len 97, sha e3f8d3f1bf821ae5...):

  ```
  [[{"tag":1," �\u0000Ā":[9007199254740992,0,"\""]},5e-324,"﻿ࠀ <\u001f <"],0.3," "]
  ```

### Example 3

- generator: `object_unicode_keys`
- input: `{"\u0000\u001f/\" ": 295, " \u0007﻿": 530, "<\u0000\"ÿ\\￿\u001f�": -667, "ࠀ�/": 35, " ﻿  ": -653}`

Canonical per implementation:
- **python** (len 112, sha a5d2ef3453b7557e...):

  ```
  {"\u0000\u001f/\" ":295,"<\u0000\"ÿ\\￿\u001f�":-667," ﻿  ":-653,"ࠀ�/":35," \u0007﻿":530}
  ```
- **go** (len 124, sha f12425cca8b80c9d...):

  ```
  {"\u0000\u001f/\"\u2029":295,"<\u0000\"ÿ\\￿\u001f�":-667,"\u2029﻿\u2028 ":-653,"ࠀ�/":35,"\u2028\u0007﻿":530}
  ```
- **rust** (len 112, sha a5d2ef3453b7557e...):

  ```
  {"\u0000\u001f/\" ":295,"<\u0000\"ÿ\\￿\u001f�":-667," ﻿  ":-653,"ࠀ�/":35," \u0007﻿":530}
  ```
