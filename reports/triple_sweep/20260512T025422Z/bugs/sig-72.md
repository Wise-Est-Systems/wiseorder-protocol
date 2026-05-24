# Disagreement signature 72

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-SMP,contains-U+2029`

**Count:** 7

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-SMP, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 4
  - object_unicode_keys: 2
  - array_order: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"<": -36, " \\": -774, "߿  ﻿ >>￿": -364, "\"﻿߿\u001f": -709, ">𐀀�": 577}`

Canonical per implementation:
- **python** (len 85, sha a6031fcef244372e...):

  ```
  {"\"﻿߿\u001f":-709,"<":-36,">𐀀�":577,"߿  ﻿ >>￿":-364," \\":-774}
  ```
- **go** (len 97, sha d1065f384d77ff2a...):

  ```
  {"\"﻿߿\u001f":-709,"<":-36,">𐀀�":577,"߿\u2029\u2029﻿\u2029>>￿":-364,"\u2029\\":-774}
  ```
- **rust** (len 85, sha a6031fcef244372e...):

  ```
  {"\"﻿߿\u001f":-709,"<":-36,">𐀀�":577,"߿  ﻿ >>￿":-364," \\":-774}
  ```

### Example 2

- generator: `array_order`
- input: `["﻿/ 􏿿>\u0007\u0007 ", -31, 24, 1.7976931348623157e+308]`

Canonical per implementation:
- **python** (len 60, sha 57504a2d205fb421...):

  ```
  ["﻿/ 􏿿>\u0007\u0007 ",-31,24,1.7976931348623157e+308]
  ```
- **go** (len 63, sha 2b17719ec99150de...):

  ```
  ["﻿/\u2029􏿿>\u0007\u0007 ",-31,24,1.7976931348623157e+308]
  ```
- **rust** (len 60, sha 57504a2d205fb421...):

  ```
  ["﻿/ 􏿿>\u0007\u0007 ",-31,24,1.7976931348623157e+308]
  ```

### Example 3

- generator: `nested`
- input: `[[9007199254740992, 0, " \u001f􏿿\"􏿿\u0000\"﻿"], -0.0, "􏿿 >>"]`

Canonical per implementation:
- **python** (len 72, sha 523f95e03bcec19c...):

  ```
  [[9007199254740992,0," \u001f􏿿\"􏿿\u0000\"﻿"],-0.0,"􏿿 >>"]
  ```
- **go** (len 78, sha 993faaaca205a21f...):

  ```
  [[9007199254740992,0,"\u2029\u001f􏿿\"􏿿\u0000\"﻿"],-0.0,"􏿿\u2029>>"]
  ```
- **rust** (len 72, sha 523f95e03bcec19c...):

  ```
  [[9007199254740992,0," \u001f􏿿\"􏿿\u0000\"﻿"],-0.0,"􏿿 >>"]
  ```
