# Disagreement signature 17

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-C1-control,contains-SMP,contains-U+2028`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-C1-control, contains-SMP, contains-U+2028

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"/\\\u0000\u001f": 836, "\u0000\u001f￿ �": -3, "﻿�ÿ ": 938, "􏿿Ā﻿>": -200, "\\": 235}`

Canonical per implementation:
- **python** (len 103, sha 5dc64d4e5471e329...):

  ```
  {"\u0000\u001f￿ �":-3,"/\\\u0000\u001f":836,"\\":235,"﻿�ÿ ":938,"􏿿Ā﻿>":-200}
  ```
- **go** (len 109, sha 50ce403892842fd2...):

  ```
  {"\u0000\u001f￿\u2028�":-3,"/\\\u0000\u001f":836,"\\":235,"﻿�ÿ\u2028":938,"􏿿Ā﻿>":-200}
  ```
- **rust** (len 103, sha 5dc64d4e5471e329...):

  ```
  {"\u0000\u001f￿ �":-3,"/\\\u0000\u001f":836,"\\":235,"﻿�ÿ ":938,"􏿿Ā﻿>":-200}
  ```
