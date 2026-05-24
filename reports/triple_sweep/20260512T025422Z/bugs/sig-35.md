# Disagreement signature 35

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-SMP,contains-U+2028,contains-U+2029`

**Count:** 13

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-SMP, contains-U+2028, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 6
  - nested: 4
  - array_order: 3

## Examples

### Example 1

- generator: `nested`
- input: `{"߿￿𐀀": [{"\u001f": [-2147483648, 0, " ࠀ﻿"], "tag": 6}, 0.30000000000000004, "�  ࠀ￿\u0000﻿ "], "tag": 6}`

Canonical per implementation:
- **python** (len 120, sha 838d3bfea9f50157...):

  ```
  {"tag":6,"߿￿𐀀":[{"\u001f":[-2147483648,0," ࠀ﻿"],"tag":6},0.30000000000000004,"�  ࠀ￿\u0000﻿ "]}
  ```
- **go** (len 132, sha d4d93eab3a673d90...):

  ```
  {"tag":6,"߿￿𐀀":[{"\u001f":[-2147483648,0,"\u2029ࠀ﻿"],"tag":6},0.30000000000000004,"�\u2028\u2028ࠀ￿\u0000﻿\u2028"]}
  ```
- **rust** (len 120, sha 838d3bfea9f50157...):

  ```
  {"tag":6,"߿￿𐀀":[{"\u001f":[-2147483648,0," ࠀ﻿"],"tag":6},0.30000000000000004,"�  ࠀ￿\u0000﻿ "]}
  ```

### Example 2

- generator: `object_unicode_keys`
- input: `{"\"𐀀﻿": -956, " & ÿ\u0000": 174, " 􏿿&ࠀ": 133}`

Canonical per implementation:
- **python** (len 58, sha b951d2dbef4ae0db...):

  ```
  {"\"𐀀﻿":-956," & ÿ\u0000":174," 􏿿&ࠀ":133}
  ```
- **go** (len 67, sha 9edc359f6e1780c8...):

  ```
  {"\"𐀀﻿":-956,"\u2028&\u2028ÿ\u0000":174,"\u2029􏿿&ࠀ":133}
  ```
- **rust** (len 58, sha b951d2dbef4ae0db...):

  ```
  {"\"𐀀﻿":-956," & ÿ\u0000":174," 􏿿&ࠀ":133}
  ```

### Example 3

- generator: `array_order`
- input: `[0.3, "􏿿﻿﻿<", "ÿ\u0000 ÿ \u0000/ÿ", 1e+17]`

Canonical per implementation:
- **python** (len 53, sha 01d73aef1efcaa48...):

  ```
  [0.3,"􏿿﻿﻿<","ÿ\u0000 ÿ \u0000/ÿ",1e+17]
  ```
- **go** (len 59, sha acc0dcb0404198f4...):

  ```
  [0.3,"􏿿﻿﻿<","ÿ\u0000\u2028ÿ\u2029\u0000/ÿ",1e+17]
  ```
- **rust** (len 53, sha 01d73aef1efcaa48...):

  ```
  [0.3,"􏿿﻿﻿<","ÿ\u0000 ÿ \u0000/ÿ",1e+17]
  ```
