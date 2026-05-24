# Disagreement signature 10

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-SMP,contains-U+2028`

**Count:** 18

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-SMP, contains-U+2028

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 8
  - object_unicode_keys: 6
  - mixed_object: 3
  - array_order: 1

## Examples

### Example 1

- generator: `nested`
- input: `[[{"\u0000>𐀀&\"": 1000000000000000.0, "tag": 5}, 2147483647, "􏿿ÿ𐀀 �&"], 1000000000000000.0, "�߿﻿"]`

Canonical per implementation:
- **python** (len 110, sha 13098623d353116d...):

  ```
  [[{"\u0000>𐀀&\"":1000000000000000.0,"tag":5},2147483647,"􏿿ÿ𐀀 �&"],1000000000000000.0,"�߿﻿"]
  ```
- **go** (len 113, sha 1e7029cc5d08a96d...):

  ```
  [[{"\u0000>𐀀&\"":1000000000000000.0,"tag":5},2147483647,"􏿿ÿ𐀀\u2028�&"],1000000000000000.0,"�߿﻿"]
  ```
- **rust** (len 110, sha 13098623d353116d...):

  ```
  [[{"\u0000>𐀀&\"":1000000000000000.0,"tag":5},2147483647,"􏿿ÿ𐀀 �&"],1000000000000000.0,"�߿﻿"]
  ```

### Example 2

- generator: `object_unicode_keys`
- input: `{"\u0000߿>": -463, "&>": 378, "߿ ࠀ﻿􏿿>\u0007": 728, "﻿": -501}`

Canonical per implementation:
- **python** (len 67, sha 453ae71877051b4e...):

  ```
  {"\u0000߿>":-463,"&>":378,"߿ ࠀ﻿􏿿>\u0007":728,"﻿":-501}
  ```
- **go** (len 70, sha ba49afccb2245a5c...):

  ```
  {"\u0000߿>":-463,"&>":378,"߿\u2028ࠀ﻿􏿿>\u0007":728,"﻿":-501}
  ```
- **rust** (len 67, sha 453ae71877051b4e...):

  ```
  {"\u0000߿>":-463,"&>":378,"߿ ࠀ﻿􏿿>\u0007":728,"﻿":-501}
  ```

### Example 3

- generator: `object_unicode_keys`
- input: `{"\u001f<ࠀ􏿿 ﻿ࠀ": 370, " \"\u001f ": -253}`

Canonical per implementation:
- **python** (len 49, sha abaa2943f5ed73a4...):

  ```
  {"\u001f<ࠀ􏿿 ﻿ࠀ":370," \"\u001f ":-253}
  ```
- **go** (len 52, sha 1078d4a7e32b8929...):

  ```
  {"\u001f<ࠀ􏿿 ﻿ࠀ":370,"\u2028\"\u001f ":-253}
  ```
- **rust** (len 49, sha abaa2943f5ed73a4...):

  ```
  {"\u001f<ࠀ􏿿 ﻿ࠀ":370," \"\u001f ":-253}
  ```
