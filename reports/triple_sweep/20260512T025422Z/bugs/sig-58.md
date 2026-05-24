# Disagreement signature 58

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-U+2028`

**Count:** 8

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-U+2028

**Length pattern:** longest:go,shortest:python

**By generator:**
  - unicode_string: 5
  - mixed_object: 2
  - array_order: 1

## Examples

### Example 1

- generator: `unicode_string`
- input: `"﻿ "`

Canonical per implementation:
- **python** (len 8, sha 50b876fe4ff4d35d...):

  ```
  "﻿ "
  ```
- **go** (len 11, sha 6c2d86ae6e0e8a3d...):

  ```
  "﻿\u2028"
  ```
- **rust** (len 8, sha 50b876fe4ff4d35d...):

  ```
  "﻿ "
  ```

### Example 2

- generator: `mixed_object`
- input: `{"k0": [1.7976931348623157e+308], "k1": [0, 1e+17, 1e-100], "k2": " ", "k3": " ﻿", "k4": []}`

Canonical per implementation:
- **python** (len 87, sha 13a575322638f4f3...):

  ```
  {"k0":[1.7976931348623157e+308],"k1":[0,1e+17,1e-100],"k2":" ","k3":" ﻿","k4":[]}
  ```
- **go** (len 93, sha 1072ab56c55caccf...):

  ```
  {"k0":[1.7976931348623157e+308],"k1":[0,1e+17,1e-100],"k2":"\u2028","k3":"\u2028﻿","k4":[]}
  ```
- **rust** (len 87, sha 13a575322638f4f3...):

  ```
  {"k0":[1.7976931348623157e+308],"k1":[0,1e+17,1e-100],"k2":" ","k3":" ﻿","k4":[]}
  ```

### Example 3

- generator: `unicode_string`
- input: `"Ā￿ ﻿\""`

Canonical per implementation:
- **python** (len 15, sha f35dc666313fa347...):

  ```
  "Ā￿ ﻿\""
  ```
- **go** (len 18, sha 4a62d30c378905e9...):

  ```
  "Ā￿\u2028﻿\""
  ```
- **rust** (len 15, sha f35dc666313fa347...):

  ```
  "Ā￿ ﻿\""
  ```
