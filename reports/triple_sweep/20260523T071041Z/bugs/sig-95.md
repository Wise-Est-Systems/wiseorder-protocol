# Disagreement signature 95

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-C1-control,contains-SMP,contains-U+2028,contains-U+2029,contains-bigint>2^53,contains-emoji`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-C1-control, contains-SMP, contains-U+2028, contains-U+2029, contains-bigint>2^53, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 1

## Examples

### Example 1

- generator: `nested`
- input: `[[[{"ࠀ 𐀀߿": -2147483648, "tag": 9}, 5e-324, "😀Ā\u001f < Ā "], 1e+17, "﻿\u0007"], -9223372036854775808, "😀\u001f\u0007􏿿߿"]`

Canonical per implementation:
- **python** (len 144, sha b3582ac7b0a4b1c7...):

  ```
  [[[{"tag":9,"ࠀ 𐀀߿":-2147483648},5e-324,"😀Ā\u001f < Ā "],1e+17,"﻿\u0007"],-9223372036854775808,"😀\u001f\u0007􏿿߿"]
  ```
- **go** (len 153, sha ad5f334b28c6ab03...):

  ```
  [[[{"tag":9,"ࠀ\u2028𐀀߿":-2147483648},5e-324,"😀Ā\u001f\u2028<\u2029Ā "],1e+17,"﻿\u0007"],-9223372036854775808,"😀\u001f\u0007􏿿߿"]
  ```
- **rust** (len 144, sha b3582ac7b0a4b1c7...):

  ```
  [[[{"tag":9,"ࠀ 𐀀߿":-2147483648},5e-324,"😀Ā\u001f < Ā "],1e+17,"﻿\u0007"],-9223372036854775808,"😀\u001f\u0007􏿿߿"]
  ```
