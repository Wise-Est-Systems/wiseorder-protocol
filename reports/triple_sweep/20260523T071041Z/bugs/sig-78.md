# Disagreement signature 78

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-U+2029`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 1

## Examples

### Example 1

- generator: `nested`
- input: `[[2.2250738585072014e-308, -1, "Ā "], -2147483648, "￿  ﻿"]`

Canonical per implementation:
- **python** (len 63, sha c0d2e18716f5ec65...):

  ```
  [[2.2250738585072014e-308,-1,"Ā "],-2147483648,"￿  ﻿"]
  ```
- **go** (len 69, sha d6a93eb88fd8863e...):

  ```
  [[2.2250738585072014e-308,-1,"Ā\u2029"],-2147483648,"￿ \u2029﻿"]
  ```
- **rust** (len 63, sha c0d2e18716f5ec65...):

  ```
  [[2.2250738585072014e-308,-1,"Ā "],-2147483648,"￿  ﻿"]
  ```
