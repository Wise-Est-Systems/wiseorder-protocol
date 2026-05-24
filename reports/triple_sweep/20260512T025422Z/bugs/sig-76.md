# Disagreement signature 76

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-DEL,contains-U+2028`

**Count:** 6

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-DEL, contains-U+2028

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 4
  - mixed_object: 1
  - unicode_string: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"\u001fĀ\"\u001f\\￿": -991, "&﻿": 625, "\\>": -235, "ÿ\u0000߿\u0007߿": 967, "ÿ ÿ": -711}`

Canonical per implementation:
- **python** (len 98, sha 677b9fd9e4984217...):

  ```
  {"\u001fĀ\"\u001f\\￿":-991,"&﻿":625,"\\>":-235,"ÿ ÿ":-711,"ÿ\u0000߿\u0007߿":967}
  ```
- **go** (len 101, sha 4614bd49f30ebdc4...):

  ```
  {"\u001fĀ\"\u001f\\￿":-991,"&﻿":625,"\\>":-235,"ÿ\u2028ÿ":-711,"ÿ\u0000߿\u0007߿":967}
  ```
- **rust** (len 98, sha 677b9fd9e4984217...):

  ```
  {"\u001fĀ\"\u001f\\￿":-991,"&﻿":625,"\\>":-235,"ÿ ÿ":-711,"ÿ\u0000߿\u0007߿":967}
  ```

### Example 2

- generator: `object_unicode_keys`
- input: `{"ĀĀ﻿": 411, "<": 962, "<\u001f ߿/": 968, "߿": -936}`

Canonical per implementation:
- **python** (len 55, sha 80742a45c277b09e...):

  ```
  {"<":962,"<\u001f ߿/":968,"ĀĀ﻿":411,"߿":-936}
  ```
- **go** (len 58, sha 5eb49d0227d5afef...):

  ```
  {"<":962,"<\u001f\u2028߿/":968,"ĀĀ﻿":411,"߿":-936}
  ```
- **rust** (len 55, sha 80742a45c277b09e...):

  ```
  {"<":962,"<\u001f ߿/":968,"ĀĀ﻿":411,"߿":-936}
  ```

### Example 3

- generator: `mixed_object`
- input: `{"k0": "\\﻿>Ā", "k1": "߿﻿\u0000 >\"", "k2": 3.141592653589793}`

Canonical per implementation:
- **python** (len 66, sha 4640510740b76f9e...):

  ```
  {"k0":"\\﻿>Ā","k1":"߿﻿\u0000 >\"","k2":3.141592653589793}
  ```
- **go** (len 69, sha 05064e50b04b8b20...):

  ```
  {"k0":"\\﻿>Ā","k1":"߿﻿\u0000\u2028>\"","k2":3.141592653589793}
  ```
- **rust** (len 66, sha 4640510740b76f9e...):

  ```
  {"k0":"\\﻿>Ā","k1":"߿﻿\u0000 >\"","k2":3.141592653589793}
  ```
