# Disagreement signature 39

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-DEL,contains-SMP,contains-U+2028,contains-U+2029,contains-emoji`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-DEL, contains-SMP, contains-U+2028, contains-U+2029, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - array_order: 1

## Examples

### Example 1

- generator: `array_order`
- input: `[-42, "﻿ 􏿿 /", -96, 14, "ࠀ ", "\"￿&😀<", -9]`

Canonical per implementation:
- **python** (len 56, sha 0b19c625b1f818ef...):

  ```
  [-42,"﻿ 􏿿 /",-96,14,"ࠀ ","\"￿&😀<",-9]
  ```
- **go** (len 65, sha b086bf1f00fc2848...):

  ```
  [-42,"﻿\u2029􏿿\u2028/",-96,14,"ࠀ\u2029","\"￿&😀<",-9]
  ```
- **rust** (len 56, sha 0b19c625b1f818ef...):

  ```
  [-42,"﻿ 􏿿 /",-96,14,"ࠀ ","\"￿&😀<",-9]
  ```
