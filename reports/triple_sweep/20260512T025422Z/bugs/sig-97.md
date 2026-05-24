# Disagreement signature 97

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C1-control,contains-DEL,contains-SMP,contains-U+2028,contains-emoji`

**Count:** 5

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C1-control, contains-DEL, contains-SMP, contains-U+2028, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 2
  - nested: 2
  - array_order: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"&\\ ﻿ࠀ > ": -441, "𐀀\"": -544, " \\𐀀&": -79, ">�😀": -91, "<�": 181, "/": -7}`

Canonical per implementation:
- **python** (len 93, sha fb7cfaceea72ef47...):

  ```
  {"&\\ ﻿ࠀ > ":-441,"/":-7,"<�":181,">�😀":-91," \\𐀀&":-79,"𐀀\"":-544}
  ```
- **go** (len 102, sha 85639c770b511fad...):

  ```
  {"&\\\u2028﻿ࠀ >\u2028":-441,"/":-7,"<�":181,">�😀":-91,"\u2028\\𐀀&":-79,"𐀀\"":-544}
  ```
- **rust** (len 93, sha fb7cfaceea72ef47...):

  ```
  {"&\\ ﻿ࠀ > ":-441,"/":-7,"<�":181,">�😀":-91," \\𐀀&":-79,"𐀀\"":-544}
  ```

### Example 2

- generator: `object_unicode_keys`
- input: `{" Ā/﻿": -448, "ࠀ/": -385, "😀ÿ𐀀>�𐀀": -475}`

Canonical per implementation:
- **python** (len 62, sha 23a1549dc955c7a3...):

  ```
  {"ࠀ/":-385," Ā/﻿":-448,"😀ÿ𐀀>�𐀀":-475}
  ```
- **go** (len 65, sha c231fee10ea5dd4e...):

  ```
  {"ࠀ/":-385,"\u2028Ā/﻿":-448,"😀ÿ𐀀>�𐀀":-475}
  ```
- **rust** (len 62, sha 23a1549dc955c7a3...):

  ```
  {"ࠀ/":-385," Ā/﻿":-448,"😀ÿ𐀀>�𐀀":-475}
  ```

### Example 3

- generator: `nested`
- input: `[{"&": {"<>𐀀&": {"�\\߿>😀﻿": 0.3, "tag": 4}, "tag": 1}, "tag": 9}, 3.14159, "￿\"􏿿 "]`

Canonical per implementation:
- **python** (len 95, sha 57aa7d0227d256e0...):

  ```
  [{"&":{"<>𐀀&":{"tag":4,"�\\߿>😀﻿":0.3},"tag":1},"tag":9},3.14159,"￿\"􏿿 "]
  ```
- **go** (len 98, sha e19d5af36eca3719...):

  ```
  [{"&":{"<>𐀀&":{"tag":4,"�\\߿>😀﻿":0.3},"tag":1},"tag":9},3.14159,"￿\"􏿿\u2028"]
  ```
- **rust** (len 95, sha 57aa7d0227d256e0...):

  ```
  [{"&":{"<>𐀀&":{"tag":4,"�\\߿>😀﻿":0.3},"tag":1},"tag":9},3.14159,"￿\"􏿿 "]
  ```
