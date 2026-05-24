# Disagreement signature 55

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C1-control,contains-U+2028,contains-U+2029`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C1-control, contains-U+2028, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 1

## Examples

### Example 1

- generator: `nested`
- input: `{"﻿﻿": [2.2250738585072014e-308, 0, "ÿ  \"Āÿࠀ�"], "tag": 8}`

Canonical per implementation:
- **python** (len 73, sha 6552a0157f6cf78c...):

  ```
  {"tag":8,"﻿﻿":[2.2250738585072014e-308,0,"ÿ  \"Āÿࠀ�"]}
  ```
- **go** (len 79, sha f080e33d0bee59b9...):

  ```
  {"tag":8,"﻿﻿":[2.2250738585072014e-308,0,"ÿ\u2028\u2029\"Āÿࠀ�"]}
  ```
- **rust** (len 73, sha 6552a0157f6cf78c...):

  ```
  {"tag":8,"﻿﻿":[2.2250738585072014e-308,0,"ÿ  \"Āÿࠀ�"]}
  ```
