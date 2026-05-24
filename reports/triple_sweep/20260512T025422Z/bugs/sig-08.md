# Disagreement signature 8

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-C1-control,contains-DEL,contains-SMP,contains-U+2028,contains-U+2029,contains-emoji`

**Count:** 18

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-C1-control, contains-DEL, contains-SMP, contains-U+2028, contains-U+2029, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 12
  - nested: 6

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"�𐀀": -703, "Ā<<￿ \"": 736, "ÿ ߿߿/﻿\\Ā": -300, "\u001f😀\u0007߿﻿􏿿": -931, "/&\"<\u0007\"": 776, "\u0007 >ࠀ\u0007": 497}`

Canonical per implementation:
- **python** (len 142, sha bf18aba65dd96f3b...):

  ```
  {"\u0007 >ࠀ\u0007":497,"\u001f😀\u0007߿﻿􏿿":-931,"/&\"<\u0007\"":776,"ÿ ߿߿/﻿\\Ā":-300,"Ā<<￿ \"":736,"�𐀀":-703}
  ```
- **go** (len 148, sha ff8c6e648abe2d69...):

  ```
  {"\u0007\u2029>ࠀ\u0007":497,"\u001f😀\u0007߿﻿􏿿":-931,"/&\"<\u0007\"":776,"ÿ\u2028߿߿/﻿\\Ā":-300,"Ā<<￿ \"":736,"�𐀀":-703}
  ```
- **rust** (len 142, sha bf18aba65dd96f3b...):

  ```
  {"\u0007 >ࠀ\u0007":497,"\u001f😀\u0007߿﻿􏿿":-931,"/&\"<\u0007\"":776,"ÿ ߿߿/﻿\\Ā":-300,"Ā<<￿ \"":736,"�𐀀":-703}
  ```

### Example 2

- generator: `object_unicode_keys`
- input: `{"\u001f😀/߿ �": 40, "&\" Ā�😀": -561, "😀Ā ߿ Ā􏿿": -992, "ࠀ﻿ ": -561, "/�&😀ÿ": -712}`

Canonical per implementation:
- **python** (len 120, sha e6acd95feb866232...):

  ```
  {"\u001f😀/߿ �":40,"&\" Ā�😀":-561,"/�&😀ÿ":-712,"ࠀ﻿ ":-561,"😀Ā ߿ Ā􏿿":-992}
  ```
- **go** (len 135, sha 717daf9a979e55a6...):

  ```
  {"\u001f😀/߿\u2028�":40,"&\"\u2028Ā�😀":-561,"/�&😀ÿ":-712,"ࠀ﻿\u2029":-561,"😀Ā\u2029߿\u2028Ā􏿿":-992}
  ```
- **rust** (len 120, sha e6acd95feb866232...):

  ```
  {"\u001f😀/߿ �":40,"&\" Ā�😀":-561,"/�&😀ÿ":-712,"ࠀ﻿ ":-561,"😀Ā ߿ Ā􏿿":-992}
  ```

### Example 3

- generator: `nested`
- input: `[[[{"￿": {" 😀﻿": 3.141592653589793, "tag": 1}, "tag": 5}, 5e-324, " 😀&\u001fࠀ"], 9007199254740991, "￿ >😀﻿Ā"], 5e-324, " ￿𐀀\u0000"]`

Canonical per implementation:
- **python** (len 154, sha d26d93909db9bdb4...):

  ```
  [[[{"tag":5,"￿":{"tag":1," 😀﻿":3.141592653589793}},5e-324," 😀&\u001fࠀ"],9007199254740991,"￿ >😀﻿Ā"],5e-324," ￿𐀀\u0000"]
  ```
- **go** (len 166, sha 6886b5ec87514b89...):

  ```
  [[[{"tag":5,"￿":{"tag":1,"\u2028😀﻿":3.141592653589793}},5e-324,"\u2028😀&\u001fࠀ"],9007199254740991,"￿\u2028>😀﻿Ā"],5e-324,"\u2029￿𐀀\u0000"]
  ```
- **rust** (len 154, sha d26d93909db9bdb4...):

  ```
  [[[{"tag":5,"￿":{"tag":1," 😀﻿":3.141592653589793}},5e-324," 😀&\u001fࠀ"],9007199254740991,"￿ >😀﻿Ā"],5e-324," ￿𐀀\u0000"]
  ```
