# Disagreement signature 49

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-C1-control,contains-SMP,contains-U+2028`

**Count:** 10

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-C1-control, contains-SMP, contains-U+2028

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 6
  - array_order: 2
  - nested: 2

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

### Example 2

- generator: `object_unicode_keys`
- input: `{"\\ࠀ>﻿﻿": 966, "𐀀&": 452, "\u001fࠀ𐀀\"\u0007": 15, "  \u001f&\"\u0000�\"": -361, "ÿ\u0007\"Ā": 308}`

Canonical per implementation:
- **python** (len 112, sha 71e7ea7efb47bb3c...):

  ```
  {"\u001fࠀ𐀀\"\u0007":15,"\\ࠀ>﻿﻿":966,"ÿ\u0007\"Ā":308,"  \u001f&\"\u0000�\"":-361,"𐀀&":452}
  ```
- **go** (len 115, sha 6815f8b07d1f2d0c...):

  ```
  {"\u001fࠀ𐀀\"\u0007":15,"\\ࠀ>﻿﻿":966,"ÿ\u0007\"Ā":308,"\u2028 \u001f&\"\u0000�\"":-361,"𐀀&":452}
  ```
- **rust** (len 112, sha 71e7ea7efb47bb3c...):

  ```
  {"\u001fࠀ𐀀\"\u0007":15,"\\ࠀ>﻿﻿":966,"ÿ\u0007\"Ā":308,"  \u001f&\"\u0000�\"":-361,"𐀀&":452}
  ```

### Example 3

- generator: `object_unicode_keys`
- input: `{" 􏿿>  ￿": -238, "/\u0000\"𐀀/ÿ﻿": 453, "\u0000𐀀": 349, "\u0007\u001fĀ\"ÿ": 650}`

Canonical per implementation:
- **python** (len 94, sha 32fd8b5253199767...):

  ```
  {"\u0000𐀀":349,"\u0007\u001fĀ\"ÿ":650,"/\u0000\"𐀀/ÿ﻿":453," 􏿿>  ￿":-238}
  ```
- **go** (len 100, sha 64561c00c3d0e809...):

  ```
  {"\u0000𐀀":349,"\u0007\u001fĀ\"ÿ":650,"/\u0000\"𐀀/ÿ﻿":453,"\u2028􏿿> \u2028￿":-238}
  ```
- **rust** (len 94, sha 32fd8b5253199767...):

  ```
  {"\u0000𐀀":349,"\u0007\u001fĀ\"ÿ":650,"/\u0000\"𐀀/ÿ﻿":453," 􏿿>  ￿":-238}
  ```
