# Disagreement signature 82

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-SMP,contains-U+2029,contains-emoji`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-SMP, contains-U+2029, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - array_order: 1

## Examples

### Example 1

- generator: `array_order`
- input: `[" ", " <\u001f𐀀Ā<<", 2.2250738585072014e-308, 1e-100, 0, 1e+16, "﻿߿ࠀ￿😀😀", -14]`

Canonical per implementation:
- **python** (len 91, sha 502f8953cd0a3d95...):

  ```
  [" "," <\u001f𐀀Ā<<",2.2250738585072014e-308,1e-100,0,1e+16,"﻿߿ࠀ￿😀😀",-14]
  ```
- **go** (len 94, sha fc5433ec8d57e59a...):

  ```
  ["\u2029"," <\u001f𐀀Ā<<",2.2250738585072014e-308,1e-100,0,1e+16,"﻿߿ࠀ￿😀😀",-14]
  ```
- **rust** (len 91, sha 502f8953cd0a3d95...):

  ```
  [" "," <\u001f𐀀Ā<<",2.2250738585072014e-308,1e-100,0,1e+16,"﻿߿ࠀ￿😀😀",-14]
  ```
