# Disagreement signature 11

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-C1-control,contains-SMP,contains-U+2029,contains-emoji`

**Count:** 18

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-C1-control, contains-SMP, contains-U+2029, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 9
  - nested: 8
  - array_order: 1

## Examples

### Example 1

- generator: `nested`
- input: `{"� ￿": [[{"𐀀￿": [0.3, 3.14159, "﻿ &&\u0007&𐀀"], "tag": 0}, -2.5, "\\𐀀"], 0.3, "😀ࠀ/&"], "tag": 2}`

Canonical per implementation:
- **python** (len 113, sha 3f30288878a7aed2...):

  ```
  {"tag":2,"� ￿":[[{"tag":0,"𐀀￿":[0.3,3.14159,"﻿ &&\u0007&𐀀"]},-2.5,"\\𐀀"],0.3,"😀ࠀ/&"]}
  ```
- **go** (len 116, sha 39ce4201f6a32a18...):

  ```
  {"tag":2,"� ￿":[[{"tag":0,"𐀀￿":[0.3,3.14159,"﻿\u2029&&\u0007&𐀀"]},-2.5,"\\𐀀"],0.3,"😀ࠀ/&"]}
  ```
- **rust** (len 113, sha 3f30288878a7aed2...):

  ```
  {"tag":2,"� ￿":[[{"tag":0,"𐀀￿":[0.3,3.14159,"﻿ &&\u0007&𐀀"]},-2.5,"\\𐀀"],0.3,"😀ࠀ/&"]}
  ```

### Example 2

- generator: `object_unicode_keys`
- input: `{"߿/\u0000ࠀ�": 489, "&\u0007�\u0007😀ÿ": -463, "﻿ ": 540, "ࠀ/ \\􏿿ࠀ�/": 66, "\"􏿿": 240, "😀�>\u001f": -329}`

Canonical per implementation:
- **python** (len 127, sha 31999b4b4b8d1bc3...):

  ```
  {"\"􏿿":240,"&\u0007�\u0007😀ÿ":-463,"߿/\u0000ࠀ�":489,"ࠀ/ \\􏿿ࠀ�/":66,"﻿ ":540,"😀�>\u001f":-329}
  ```
- **go** (len 130, sha 8d8c4ccec60ce471...):

  ```
  {"\"􏿿":240,"&\u0007�\u0007😀ÿ":-463,"߿/\u0000ࠀ�":489,"ࠀ/\u2029\\􏿿ࠀ�/":66,"﻿ ":540,"😀�>\u001f":-329}
  ```
- **rust** (len 127, sha 31999b4b4b8d1bc3...):

  ```
  {"\"􏿿":240,"&\u0007�\u0007😀ÿ":-463,"߿/\u0000ࠀ�":489,"ࠀ/ \\􏿿ࠀ�/":66,"﻿ ":540,"😀�>\u001f":-329}
  ```

### Example 3

- generator: `object_unicode_keys`
- input: `{"߿": 92, " 😀\\": -740, "﻿﻿\\": -575, "�𐀀Ā": -178, ">􏿿": -505, "😀\u0000Ā \\ ": -979}`

Canonical per implementation:
- **python** (len 100, sha 2c4e34a4185bfe43...):

  ```
  {" 😀\\":-740,">􏿿":-505,"߿":92,"﻿﻿\\":-575,"�𐀀Ā":-178,"😀\u0000Ā \\ ":-979}
  ```
- **go** (len 103, sha 30b9a26fd58a32f9...):

  ```
  {" 😀\\":-740,">􏿿":-505,"߿":92,"﻿﻿\\":-575,"�𐀀Ā":-178,"😀\u0000Ā \\\u2029":-979}
  ```
- **rust** (len 100, sha 2c4e34a4185bfe43...):

  ```
  {" 😀\\":-740,">􏿿":-505,"߿":92,"﻿﻿\\":-575,"�𐀀Ā":-178,"😀\u0000Ā \\ ":-979}
  ```
