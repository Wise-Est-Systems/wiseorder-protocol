# Disagreement signature 27

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-C1-control,contains-SMP,contains-U+2028,contains-U+2029,contains-emoji`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-C1-control, contains-SMP, contains-U+2028, contains-U+2029, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - array_order: 1

## Examples

### Example 1

- generator: `array_order`
- input: `[" \\ÿ ￿&Ā", "𐀀/ÿ\u0000", 3.141592653589793, "😀￿﻿", "﻿\u0000", 17, "ÿ􏿿\u001f\u0007>", 1e+17]`

Canonical per implementation:
- **python** (len 114, sha c170dc4538def478...):

  ```
  [" \\ÿ ￿&Ā","𐀀/ÿ\u0000",3.141592653589793,"😀￿﻿","﻿\u0000",17,"ÿ􏿿\u001f\u0007>",1e+17]
  ```
- **go** (len 120, sha f09f50f05be94002...):

  ```
  ["\u2029\\ÿ\u2028￿&Ā","𐀀/ÿ\u0000",3.141592653589793,"😀￿﻿","﻿\u0000",17,"ÿ􏿿\u001f\u0007>",1e+17]
  ```
- **rust** (len 114, sha c170dc4538def478...):

  ```
  [" \\ÿ ￿&Ā","𐀀/ÿ\u0000",3.141592653589793,"😀￿﻿","﻿\u0000",17,"ÿ􏿿\u001f\u0007>",1e+17]
  ```
