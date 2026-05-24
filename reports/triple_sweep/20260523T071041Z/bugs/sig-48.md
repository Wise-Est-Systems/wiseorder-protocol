# Disagreement signature 48

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-C1-control,contains-DEL,contains-SMP,contains-U+2029,contains-emoji`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-C1-control, contains-DEL, contains-SMP, contains-U+2029, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - array_order: 1

## Examples

### Example 1

- generator: `array_order`
- input: `["😀", " Ā� ", 0.1, 59, 0.3333333333333333, "𐀀﻿", -94, " 𐀀>/😀\u0007"]`

Canonical per implementation:
- **python** (len 85, sha 5446c35bf5bbcfbb...):

  ```
  ["😀"," Ā� ",0.1,59,0.3333333333333333,"𐀀﻿",-94," 𐀀>/😀\u0007"]
  ```
- **go** (len 91, sha bc44fa0824d36198...):

  ```
  ["😀","\u2029Ā� ",0.1,59,0.3333333333333333,"𐀀﻿",-94,"\u2029𐀀>/😀\u0007"]
  ```
- **rust** (len 85, sha 5446c35bf5bbcfbb...):

  ```
  ["😀"," Ā� ",0.1,59,0.3333333333333333,"𐀀﻿",-94," 𐀀>/😀\u0007"]
  ```
