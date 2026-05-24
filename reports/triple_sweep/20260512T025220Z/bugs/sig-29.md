# Disagreement signature 29

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-DEL,contains-U+2028`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-DEL, contains-U+2028

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 1

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
