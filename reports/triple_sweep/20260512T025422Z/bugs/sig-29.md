# Disagreement signature 29

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-DEL,contains-SMP,contains-U+2028`

**Count:** 13

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-DEL, contains-SMP, contains-U+2028

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 7
  - nested: 4
  - array_order: 2

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"﻿߿\u0007 \u001f": -504, " ￿  <": -259, "<﻿ࠀࠀ􏿿/": 918, "&/": -330}`

Canonical per implementation:
- **python** (len 80, sha 0e93ef96f9430bc7...):

  ```
  {" ￿  <":-259,"&/":-330,"<﻿ࠀࠀ􏿿/":918,"﻿߿\u0007 \u001f":-504}
  ```
- **go** (len 86, sha 8ca72ad4cc126b9c...):

  ```
  {" ￿\u2028\u2028<":-259,"&/":-330,"<﻿ࠀࠀ􏿿/":918,"﻿߿\u0007 \u001f":-504}
  ```
- **rust** (len 80, sha 0e93ef96f9430bc7...):

  ```
  {" ￿  <":-259,"&/":-330,"<﻿ࠀࠀ􏿿/":918,"﻿߿\u0007 \u001f":-504}
  ```

### Example 2

- generator: `object_unicode_keys`
- input: `{"\\\u0000&�": 324, "ࠀ\u001f\u001f ": 374, "\"\u0007<": -738, "﻿�\u0000﻿􏿿": 982}`

Canonical per implementation:
- **python** (len 90, sha a90c7182c1fc2fde...):

  ```
  {"\"\u0007<":-738,"\\\u0000&�":324,"ࠀ\u001f\u001f ":374,"﻿�\u0000﻿􏿿":982}
  ```
- **go** (len 93, sha 432a4ff29f62eec2...):

  ```
  {"\"\u0007<":-738,"\\\u0000&�":324,"ࠀ\u001f\u001f\u2028":374,"﻿�\u0000﻿􏿿":982}
  ```
- **rust** (len 90, sha a90c7182c1fc2fde...):

  ```
  {"\"\u0007<":-738,"\\\u0000&�":324,"ࠀ\u001f\u001f ":374,"﻿�\u0000﻿􏿿":982}
  ```

### Example 3

- generator: `object_unicode_keys`
- input: `{"￿<􏿿𐀀߿<": 339, "\u0007﻿/": -938, "ࠀ𐀀 ߿\u0000>": 514}`

Canonical per implementation:
- **python** (len 68, sha dc253e2d0f6f2305...):

  ```
  {"\u0007﻿/":-938,"ࠀ𐀀 ߿\u0000>":514,"￿<􏿿𐀀߿<":339}
  ```
- **go** (len 71, sha 0df1423e000b8079...):

  ```
  {"\u0007﻿/":-938,"ࠀ𐀀\u2028߿\u0000>":514,"￿<􏿿𐀀߿<":339}
  ```
- **rust** (len 68, sha dc253e2d0f6f2305...):

  ```
  {"\u0007﻿/":-938,"ࠀ𐀀 ߿\u0000>":514,"￿<􏿿𐀀߿<":339}
  ```
