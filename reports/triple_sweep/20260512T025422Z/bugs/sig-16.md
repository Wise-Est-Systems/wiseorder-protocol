# Disagreement signature 16

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-C1-control,contains-DEL,contains-SMP,contains-U+2028`

**Count:** 16

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-C1-control, contains-DEL, contains-SMP, contains-U+2028

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 6
  - object_unicode_keys: 6
  - array_order: 4

## Examples

### Example 1

- generator: `array_order`
- input: `[-71, "</􏿿߿&\u001f", 59, "\"﻿\u0007\\", "�\"", " ﻿ ￿􏿿 ", 2147483647]`

Canonical per implementation:
- **python** (len 84, sha a308b44155a843e9...):

  ```
  [-71,"</􏿿߿&\u001f",59,"\"﻿\u0007\\","�\""," ﻿ ￿􏿿 ",2147483647]
  ```
- **go** (len 90, sha da9df11b14bb8687...):

  ```
  [-71,"</􏿿߿&\u001f",59,"\"﻿\u0007\\","�\""," ﻿\u2028￿􏿿\u2028",2147483647]
  ```
- **rust** (len 84, sha a308b44155a843e9...):

  ```
  [-71,"</􏿿߿&\u001f",59,"\"﻿\u0007\\","�\""," ﻿ ￿􏿿 ",2147483647]
  ```

### Example 2

- generator: `nested`
- input: `{"/\u001f": {"􏿿￿\u0007&": {"": [9007199254740992, 0.0, " /﻿ \\&�"], "tag": 6}, "tag": 9}, "tag": 9}`

Canonical per implementation:
- **python** (len 103, sha 70b4b6d0b255ed82...):

  ```
  {"/\u001f":{"tag":9,"􏿿￿\u0007&":{"tag":6,"":[9007199254740992,0.0," /﻿ \\&�"]}},"tag":9}
  ```
- **go** (len 106, sha 93967a6906dc3980...):

  ```
  {"/\u001f":{"tag":9,"􏿿￿\u0007&":{"tag":6,"":[9007199254740992,0.0,"\u2028/﻿ \\&�"]}},"tag":9}
  ```
- **rust** (len 103, sha 70b4b6d0b255ed82...):

  ```
  {"/\u001f":{"tag":9,"􏿿￿\u0007&":{"tag":6,"":[9007199254740992,0.0," /﻿ \\&�"]}},"tag":9}
  ```

### Example 3

- generator: `array_order`
- input: `[-0.0, "\u001f ", -27, "￿", "􏿿", "􏿿\u001f\\\\﻿\\\u0007", 0.3333333333333333, 1e-100]`

Canonical per implementation:
- **python** (len 94, sha 6193081ff58010cb...):

  ```
  [-0.0,"\u001f ",-27,"￿","􏿿","􏿿\u001f\\\\﻿\\\u0007",0.3333333333333333,1e-100]
  ```
- **go** (len 97, sha 649e80696146541d...):

  ```
  [-0.0,"\u001f\u2028",-27,"￿","􏿿","􏿿\u001f\\\\﻿\\\u0007",0.3333333333333333,1e-100]
  ```
- **rust** (len 94, sha 6193081ff58010cb...):

  ```
  [-0.0,"\u001f ",-27,"￿","􏿿","􏿿\u001f\\\\﻿\\\u0007",0.3333333333333333,1e-100]
  ```
