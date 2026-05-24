# Disagreement signature 65

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-SMP,contains-U+2028,contains-U+2029`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-SMP, contains-U+2028, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - array_order: 1

## Examples

### Example 1

- generator: `array_order`
- input: `["߿><􏿿\u001f", "Ā > & ࠀ&", " \u001f>", "ࠀ﻿\\   􏿿", 59, "   <", "ࠀ\u0007\u0000߿ࠀ\\& ", "\u0007\" \\\u0000ࠀ ࠀ"]`

Canonical per implementation:
- **python** (len 137, sha 9cb2433c06a4cde4...):

  ```
  ["߿><􏿿\u001f","Ā > & ࠀ&"," \u001f>","ࠀ﻿\\   􏿿",59,"   <","ࠀ\u0007\u0000߿ࠀ\\& ","\u0007\" \\\u0000ࠀ ࠀ"]
  ```
- **go** (len 155, sha 2528aac71b761281...):

  ```
  ["߿><􏿿\u001f","Ā > & ࠀ&","\u2028\u001f>","ࠀ﻿\\ \u2029 􏿿",59,"\u2028 \u2028<","ࠀ\u0007\u0000߿ࠀ\\&\u2029","\u0007\"\u2029\\\u0000ࠀ ࠀ"]
  ```
- **rust** (len 137, sha 9cb2433c06a4cde4...):

  ```
  ["߿><􏿿\u001f","Ā > & ࠀ&"," \u001f>","ࠀ﻿\\   􏿿",59,"   <","ࠀ\u0007\u0000߿ࠀ\\& ","\u0007\" \\\u0000ࠀ ࠀ"]
  ```
