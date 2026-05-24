# Disagreement signature 46

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-U+2029`

**Count:** 11

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - unicode_string: 3
  - array_order: 3
  - object_unicode_keys: 3
  - mixed_object: 2

## Examples

### Example 1

- generator: `unicode_string`
- input: `"\u001fÿ﻿ >�\u001f\u0007"`

Canonical per implementation:
- **python** (len 32, sha 237ac738f6fda4c5...):

  ```
  "\u001fÿ﻿ >�\u001f\u0007"
  ```
- **go** (len 35, sha 41cb45ba2a24a2b9...):

  ```
  "\u001fÿ﻿\u2029>�\u001f\u0007"
  ```
- **rust** (len 32, sha 237ac738f6fda4c5...):

  ```
  "\u001fÿ﻿ >�\u001f\u0007"
  ```

### Example 2

- generator: `array_order`
- input: `[" ÿ&\u001f�﻿", 9007199254740991, -64]`

Canonical per implementation:
- **python** (len 43, sha 3e8c9ec99ca4f3cc...):

  ```
  [" ÿ&\u001f�﻿",9007199254740991,-64]
  ```
- **go** (len 46, sha 43117d70e14d2522...):

  ```
  ["\u2029ÿ&\u001f�﻿",9007199254740991,-64]
  ```
- **rust** (len 43, sha 3e8c9ec99ca4f3cc...):

  ```
  [" ÿ&\u001f�﻿",9007199254740991,-64]
  ```

### Example 3

- generator: `mixed_object`
- input: `{"k2": false, "k0": " /�<\u001f﻿", "k1": 5e-324}`

Canonical per implementation:
- **python** (len 49, sha b851652690612119...):

  ```
  {"k0":" /�<\u001f﻿","k1":5e-324,"k2":false}
  ```
- **go** (len 52, sha aa1047b79dc0ddde...):

  ```
  {"k0":"\u2029/�<\u001f﻿","k1":5e-324,"k2":false}
  ```
- **rust** (len 49, sha b851652690612119...):

  ```
  {"k0":" /�<\u001f﻿","k1":5e-324,"k2":false}
  ```
