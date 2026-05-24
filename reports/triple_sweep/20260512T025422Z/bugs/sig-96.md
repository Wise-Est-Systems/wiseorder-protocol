# Disagreement signature 96

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-C1-control,contains-DEL,contains-U+2028,contains-U+2029,contains-emoji`

**Count:** 5

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-C1-control, contains-DEL, contains-U+2028, contains-U+2029, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 2
  - object_unicode_keys: 2
  - mixed_object: 1

## Examples

### Example 1

- generator: `nested`
- input: `[{"\u001f> ﻿&Ā￿": [[{"//😀﻿": 3.14159, "tag": 8}, 0, "<<﻿\\&  "], 9007199254740991, ""], "tag": 2}, 0.3333333333333333, "\u001f "]`

Canonical per implementation:
- **python** (len 142, sha c0bbc6a9e11644b3...):

  ```
  [{"\u001f> ﻿&Ā￿":[[{"//😀﻿":3.14159,"tag":8},0,"<<﻿\\&  "],9007199254740991,""],"tag":2},0.3333333333333333,"\u001f "]
  ```
- **go** (len 154, sha 4748ce977c690d21...):

  ```
  [{"\u001f>\u2028﻿&Ā￿":[[{"//😀﻿":3.14159,"tag":8},0,"<<﻿\\&\u2029\u2028"],9007199254740991,""],"tag":2},0.3333333333333333,"\u001f\u2029"]
  ```
- **rust** (len 142, sha c0bbc6a9e11644b3...):

  ```
  [{"\u001f> ﻿&Ā￿":[[{"//😀﻿":3.14159,"tag":8},0,"<<﻿\\&  "],9007199254740991,""],"tag":2},0.3333333333333333,"\u001f "]
  ```

### Example 2

- generator: `object_unicode_keys`
- input: `{"😀>/": -224, "߿ࠀ�  /﻿": -809, "\u0007\\\u0000﻿ÿ ": 47, "\"\\�<<Ā\"": -59, "�﻿�": 272}`

Canonical per implementation:
- **python** (len 112, sha 845ffd955d44807f...):

  ```
  {"\u0007\\\u0000﻿ÿ ":47,"\"\\�<<Ā\"":-59,"߿ࠀ�  /﻿":-809,"�﻿�":272,"😀>/":-224}
  ```
- **go** (len 121, sha d83492fccfa58d69...):

  ```
  {"\u0007\\\u0000﻿ÿ\u2029":47,"\"\\�<<Ā\"":-59,"߿ࠀ�\u2028\u2028/﻿":-809,"�﻿�":272,"😀>/":-224}
  ```
- **rust** (len 112, sha 845ffd955d44807f...):

  ```
  {"\u0007\\\u0000﻿ÿ ":47,"\"\\�<<Ā\"":-59,"߿ࠀ�  /﻿":-809,"�﻿�":272,"😀>/":-224}
  ```

### Example 3

- generator: `nested`
- input: `[{"Ā\u001f": {"﻿ 😀  ": [{"\u0007߿<Ā\u0007": 9007199254740991, "tag": 1}, 1e+16, "ࠀ"], "tag": 2}, "tag": 9}, 10000000000.0, " >\u001f\u0007 "]`

Canonical per implementation:
- **python** (len 148, sha 7a6836815500e5ca...):

  ```
  [{"tag":9,"Ā\u001f":{"tag":2,"﻿ 😀  ":[{"\u0007߿<Ā\u0007":9007199254740991,"tag":1},1e+16,"ࠀ"]}},10000000000.0," >\u001f\u0007 "]
  ```
- **go** (len 157, sha e9360e2277fa5460...):

  ```
  [{"tag":9,"Ā\u001f":{"tag":2,"﻿\u2029😀 \u2028":[{"\u0007߿<Ā\u0007":9007199254740991,"tag":1},1e+16,"ࠀ"]}},10000000000.0," >\u001f\u0007\u2028"]
  ```
- **rust** (len 148, sha 7a6836815500e5ca...):

  ```
  [{"tag":9,"Ā\u001f":{"tag":2,"﻿ 😀  ":[{"\u0007߿<Ā\u0007":9007199254740991,"tag":1},1e+16,"ࠀ"]}},10000000000.0," >\u001f\u0007 "]
  ```
