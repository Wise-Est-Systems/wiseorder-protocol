# Disagreement signature 47

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-C1-control,contains-DEL,contains-U+2028,contains-emoji`

**Count:** 11

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-C1-control, contains-DEL, contains-U+2028, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 5
  - array_order: 3
  - nested: 2
  - mixed_object: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"😀": -377, "/\"￿﻿</": 394, " &\u0007 \u0007": -78, "﻿&": -711}`

Canonical per implementation:
- **python** (len 72, sha 02910747b1ee3da4...):

  ```
  {"/\"￿﻿</":394," &\u0007 \u0007":-78,"﻿&":-711,"😀":-377}
  ```
- **go** (len 78, sha fded476234f9e5c5...):

  ```
  {"/\"￿﻿</":394,"\u2028&\u0007\u2028\u0007":-78,"﻿&":-711,"😀":-377}
  ```
- **rust** (len 72, sha 02910747b1ee3da4...):

  ```
  {"/\"￿﻿</":394," &\u0007 \u0007":-78,"﻿&":-711,"😀":-377}
  ```

### Example 2

- generator: `object_unicode_keys`
- input: `{"߿߿￿ࠀĀ": -274, "> /<": 944, "/😀": 580, "\u001f\u0007 ߿": -762, "ࠀ﻿﻿￿>﻿": -374}`

Canonical per implementation:
- **python** (len 100, sha d32c04e9bb3786b2...):

  ```
  {"\u001f\u0007 ߿":-762,"/😀":580,"> /<":944,"߿߿￿ࠀĀ":-274,"ࠀ﻿﻿￿>﻿":-374}
  ```
- **go** (len 106, sha 034c83ddac6942c9...):

  ```
  {"\u001f\u0007\u2028߿":-762,"/😀":580,">\u2028/<":944,"߿߿￿ࠀĀ":-274,"ࠀ﻿﻿￿>﻿":-374}
  ```
- **rust** (len 100, sha d32c04e9bb3786b2...):

  ```
  {"\u001f\u0007 ߿":-762,"/😀":580,"> /<":944,"߿߿￿ࠀĀ":-274,"ࠀ﻿﻿￿>﻿":-374}
  ```

### Example 3

- generator: `array_order`
- input: `["﻿  ", -27, "😀<\u0000&ÿࠀ", 64, -8, " ", 0.30000000000000004]`

Canonical per implementation:
- **python** (len 72, sha 82242ad58ad25a36...):

  ```
  ["﻿  ",-27,"😀<\u0000&ÿࠀ",64,-8," ",0.30000000000000004]
  ```
- **go** (len 75, sha aea45fc6caf1629c...):

  ```
  ["﻿  ",-27,"😀<\u0000&ÿࠀ",64,-8,"\u2028",0.30000000000000004]
  ```
- **rust** (len 72, sha 82242ad58ad25a36...):

  ```
  ["﻿  ",-27,"😀<\u0000&ÿࠀ",64,-8," ",0.30000000000000004]
  ```
