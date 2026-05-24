# Disagreement signature 56

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-C1-control,contains-SMP,contains-U+2028,contains-U+2029`

**Count:** 9

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-C1-control, contains-SMP, contains-U+2028, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 5
  - array_order: 2
  - nested: 2

## Examples

### Example 1

- generator: `array_order`
- input: `["􏿿 \u001f ߿> ", "﻿ \u001f \u001f", -1]`

Canonical per implementation:
- **python** (len 55, sha fff8fcea4a87cd67...):

  ```
  ["􏿿 \u001f ߿> ","﻿ \u001f \u001f",-1]
  ```
- **go** (len 67, sha 6c9e7e1449045272...):

  ```
  ["􏿿\u2029\u001f ߿>\u2029","﻿\u2028\u001f\u2028\u001f",-1]
  ```
- **rust** (len 55, sha fff8fcea4a87cd67...):

  ```
  ["􏿿 \u001f ߿> ","﻿ \u001f \u001f",-1]
  ```

### Example 2

- generator: `object_unicode_keys`
- input: `{" \u0007𐀀ࠀ": 498, "<": 870, "ࠀ\u0007\u001f\\�": 838, "﻿ÿ<\"﻿\u0007<": 80, " ": 778}`

Canonical per implementation:
- **python** (len 95, sha 0a8676eae72f0976...):

  ```
  {"<":870,"ࠀ\u0007\u001f\\�":838," \u0007𐀀ࠀ":498," ":778,"﻿ÿ<\"﻿\u0007<":80}
  ```
- **go** (len 101, sha ce76cb6019da4ffe...):

  ```
  {"<":870,"ࠀ\u0007\u001f\\�":838,"\u2028\u0007𐀀ࠀ":498,"\u2029":778,"﻿ÿ<\"﻿\u0007<":80}
  ```
- **rust** (len 95, sha 0a8676eae72f0976...):

  ```
  {"<":870,"ࠀ\u0007\u001f\\�":838," \u0007𐀀ࠀ":498," ":778,"﻿ÿ<\"﻿\u0007<":80}
  ```

### Example 3

- generator: `object_unicode_keys`
- input: `{"﻿\u001f\"𐀀ࠀ": -220, "￿\\ �𐀀": -873, " ": -840, "<": -803, "\u001f߿\u0007 ": -41}`

Canonical per implementation:
- **python** (len 94, sha 4870dea3c71525a3...):

  ```
  {"\u001f߿\u0007 ":-41," ":-840,"<":-803,"﻿\u001f\"𐀀ࠀ":-220,"￿\\ �𐀀":-873}
  ```
- **go** (len 100, sha 410c58d4fef7586a...):

  ```
  {"\u001f߿\u0007\u2028":-41," ":-840,"<":-803,"﻿\u001f\"𐀀ࠀ":-220,"￿\\\u2029�𐀀":-873}
  ```
- **rust** (len 94, sha 4870dea3c71525a3...):

  ```
  {"\u001f߿\u0007 ":-41," ":-840,"<":-803,"﻿\u001f\"𐀀ࠀ":-220,"￿\\ �𐀀":-873}
  ```
