# Disagreement signature 41

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-DEL,contains-SMP,contains-U+2029`

**Count:** 12

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-DEL, contains-SMP, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 8
  - nested: 4

## Examples

### Example 1

- generator: `nested`
- input: `[{"\u001f": {"﻿": [{"\"ÿ": 0.2, "tag": 9}, 1000000000000000.0, " >߿ࠀ"], "tag": 3}, "tag": 9}, -2147483648, "�􏿿￿\u0007߿<&\u0000"]`

Canonical per implementation:
- **python** (len 132, sha 42930f3b0fd212c3...):

  ```
  [{"\u001f":{"tag":3,"﻿":[{"\"ÿ":0.2,"tag":9},1000000000000000.0," >߿ࠀ"]},"tag":9},-2147483648,"�􏿿￿\u0007߿<&\u0000"]
  ```
- **go** (len 135, sha adcc579f4dde2551...):

  ```
  [{"\u001f":{"tag":3,"﻿":[{"\"ÿ":0.2,"tag":9},1000000000000000.0,"\u2029>߿ࠀ"]},"tag":9},-2147483648,"�􏿿￿\u0007߿<&\u0000"]
  ```
- **rust** (len 132, sha 42930f3b0fd212c3...):

  ```
  [{"\u001f":{"tag":3,"﻿":[{"\"ÿ":0.2,"tag":9},1000000000000000.0," >߿ࠀ"]},"tag":9},-2147483648,"�􏿿￿\u0007߿<&\u0000"]
  ```

### Example 2

- generator: `object_unicode_keys`
- input: `{"ࠀÿ<\u0000􏿿￿ \"": 505, "\"\u001f\u0007\\": -864, "𐀀\u001f ﻿": -754}`

Canonical per implementation:
- **python** (len 79, sha 7915e7e90ba8ccec...):

  ```
  {"\"\u001f\u0007\\":-864,"𐀀\u001f ﻿":-754,"ࠀÿ<\u0000􏿿￿ \"":505}
  ```
- **go** (len 82, sha b55da71baceda59a...):

  ```
  {"\"\u001f\u0007\\":-864,"𐀀\u001f\u2029﻿":-754,"ࠀÿ<\u0000􏿿￿ \"":505}
  ```
- **rust** (len 79, sha 7915e7e90ba8ccec...):

  ```
  {"\"\u001f\u0007\\":-864,"𐀀\u001f ﻿":-754,"ࠀÿ<\u0000􏿿￿ \"":505}
  ```

### Example 3

- generator: `nested`
- input: `[{"ࠀ<\u001f\"\u0000<𐀀": {"<\u0007Ā/﻿Ā": 1, "tag": 6}, "tag": 5}, 0, "﻿ / ࠀ߿"]`

Canonical per implementation:
- **python** (len 88, sha c3402fcdfbe037fc...):

  ```
  [{"tag":5,"ࠀ<\u001f\"\u0000<𐀀":{"<\u0007Ā/﻿Ā":1,"tag":6}},0,"﻿ / ࠀ߿"]
  ```
- **go** (len 94, sha c0675fcbfa2f830f...):

  ```
  [{"tag":5,"ࠀ<\u001f\"\u0000<𐀀":{"<\u0007Ā/﻿Ā":1,"tag":6}},0,"﻿\u2029/\u2029ࠀ߿"]
  ```
- **rust** (len 88, sha c3402fcdfbe037fc...):

  ```
  [{"tag":5,"ࠀ<\u001f\"\u0000<𐀀":{"<\u0007Ā/﻿Ā":1,"tag":6}},0,"﻿ / ࠀ߿"]
  ```
