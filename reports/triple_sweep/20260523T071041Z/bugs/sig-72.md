# Disagreement signature 72

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-C1-control,contains-DEL,contains-U+2028,contains-U+2029`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-C1-control, contains-DEL, contains-U+2028, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"￿ࠀ <<\u0007": 449, "<� / \"\"": 918, "\u0007\u001f": -968, " &ࠀ�>�\u001f": 94, "﻿ >&ࠀ�": -794}`

Canonical per implementation:
- **python** (len 118, sha a5251d0ba70993ff...):

  ```
  {"\u0007\u001f":-968,"<� / \"\"":918,"￿ࠀ <<\u0007":449," &ࠀ�>�\u001f":94,"﻿ >&ࠀ�":-794}
  ```
- **go** (len 130, sha 407c9d9fe81ddfa7...):

  ```
  {"\u0007\u001f":-968,"<� /\u2029\"\"":918,"￿ࠀ\u2028<<\u0007":449,"\u2029&ࠀ�>�\u001f":94,"﻿\u2029>&ࠀ�":-794}
  ```
- **rust** (len 118, sha a5251d0ba70993ff...):

  ```
  {"\u0007\u001f":-968,"<� / \"\"":918,"￿ࠀ <<\u0007":449," &ࠀ�>�\u001f":94,"﻿ >&ࠀ�":-794}
  ```
