# Disagreement signature 57

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-SMP,contains-U+2028`

**Count:** 9

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-SMP, contains-U+2028

**Length pattern:** longest:go,shortest:python

**By generator:**
  - unicode_string: 5
  - array_order: 2
  - object_unicode_keys: 2

## Examples

### Example 1

- generator: `unicode_string`
- input: `" 􏿿ÿÿ/﻿"`

Canonical per implementation:
- **python** (len 17, sha 40c72557824e734c...):

  ```
  " 􏿿ÿÿ/﻿"
  ```
- **go** (len 20, sha 0d7ebe6d320811dc...):

  ```
  "\u2028􏿿ÿÿ/﻿"
  ```
- **rust** (len 17, sha 40c72557824e734c...):

  ```
  " 􏿿ÿÿ/﻿"
  ```

### Example 2

- generator: `array_order`
- input: `["﻿Ā� 𐀀", -2.5, -32, 1000000000000000.0, 37]`

Canonical per implementation:
- **python** (len 50, sha 2b2ec9e02ceccfd6...):

  ```
  ["﻿Ā� 𐀀",-2.5,-32,1000000000000000.0,37]
  ```
- **go** (len 53, sha be5fb86a1daff880...):

  ```
  ["﻿Ā�\u2028𐀀",-2.5,-32,1000000000000000.0,37]
  ```
- **rust** (len 50, sha 2b2ec9e02ceccfd6...):

  ```
  ["﻿Ā� 𐀀",-2.5,-32,1000000000000000.0,37]
  ```

### Example 3

- generator: `object_unicode_keys`
- input: `{"𐀀ࠀ￿": 824, "/﻿ ": -937}`

Canonical per implementation:
- **python** (len 33, sha 0c20618de964fbc2...):

  ```
  {"/﻿ ":-937,"𐀀ࠀ￿":824}
  ```
- **go** (len 36, sha 4ce773a728aa24dc...):

  ```
  {"/﻿\u2028":-937,"𐀀ࠀ￿":824}
  ```
- **rust** (len 33, sha 0c20618de964fbc2...):

  ```
  {"/﻿ ":-937,"𐀀ࠀ￿":824}
  ```
