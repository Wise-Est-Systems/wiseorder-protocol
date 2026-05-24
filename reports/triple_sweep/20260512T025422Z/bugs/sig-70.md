# Disagreement signature 70

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-C1-control,contains-U+2028`

**Count:** 7

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-C1-control, contains-U+2028

**Length pattern:** longest:go,shortest:python

**By generator:**
  - array_order: 3
  - nested: 2
  - mixed_object: 1
  - object_unicode_keys: 1

## Examples

### Example 1

- generator: `nested`
- input: `[{"ࠀ﻿\"\u0000": 10000000000.0, "tag": 5}, 1e+17, " / \\Ā\u0007"]`

Canonical per implementation:
- **python** (len 70, sha bb7a1bf0eea3f2c5...):

  ```
  [{"tag":5,"ࠀ﻿\"\u0000":10000000000.0},1e+17," / \\Ā\u0007"]
  ```
- **go** (len 76, sha b7cc9f70c9bd0435...):

  ```
  [{"tag":5,"ࠀ﻿\"\u0000":10000000000.0},1e+17,"\u2028/\u2028\\Ā\u0007"]
  ```
- **rust** (len 70, sha bb7a1bf0eea3f2c5...):

  ```
  [{"tag":5,"ࠀ﻿\"\u0000":10000000000.0},1e+17," / \\Ā\u0007"]
  ```

### Example 2

- generator: `nested`
- input: `[[{"￿Ā\u0007﻿": [1e+16, 0.3333333333333333, "<Ā"], "tag": 3}, -1, ">\u0007\u0007ÿ\u0000 "], 1e-100, "\u0000 ￿&"]`

Canonical per implementation:
- **python** (len 120, sha afc91a421c78c8f9...):

  ```
  [[{"tag":3,"￿Ā\u0007﻿":[1e+16,0.3333333333333333,"<Ā"]},-1,">\u0007\u0007ÿ\u0000 "],1e-100,"\u0000 ￿&"]
  ```
- **go** (len 123, sha fb0e4e3c65fa8b69...):

  ```
  [[{"tag":3,"￿Ā\u0007﻿":[1e+16,0.3333333333333333,"<Ā"]},-1,">\u0007\u0007ÿ\u0000\u2028"],1e-100,"\u0000 ￿&"]
  ```
- **rust** (len 120, sha afc91a421c78c8f9...):

  ```
  [[{"tag":3,"￿Ā\u0007﻿":[1e+16,0.3333333333333333,"<Ā"]},-1,">\u0007\u0007ÿ\u0000 "],1e-100,"\u0000 ￿&"]
  ```

### Example 3

- generator: `array_order`
- input: `[0, 0.3, -68, "﻿ \u0007  <ÿ", 1e+100, 9007199254740991]`

Canonical per implementation:
- **python** (len 57, sha 3b1eeacf4f187c0b...):

  ```
  [0,0.3,-68,"﻿ \u0007  <ÿ",1e+100,9007199254740991]
  ```
- **go** (len 60, sha 7629da0f26ded839...):

  ```
  [0,0.3,-68,"﻿\u2028\u0007  <ÿ",1e+100,9007199254740991]
  ```
- **rust** (len 57, sha 3b1eeacf4f187c0b...):

  ```
  [0,0.3,-68,"﻿ \u0007  <ÿ",1e+100,9007199254740991]
  ```
