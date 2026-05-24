# Disagreement signature 53

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-SMP,contains-U+2029,contains-bigint>2^53`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-SMP, contains-U+2029, contains-bigint>2^53

**Length pattern:** longest:go,shortest:python

**By generator:**
  - mixed_object: 1

## Examples

### Example 1

- generator: `mixed_object`
- input: `{"k3": [9007199254740991, 0, -9223372036854775808], "k2": "\u001f", "k4": ">﻿􏿿ÿ 􏿿", "k1": [2.2250738585072014e-308], "k0": "﻿"}`

Canonical per implementation:
- **python** (len 129, sha b143667fee45dbb2...):

  ```
  {"k0":"﻿","k1":[2.2250738585072014e-308],"k2":"\u001f","k3":[9007199254740991,0,-9223372036854775808],"k4":">﻿􏿿ÿ 􏿿"}
  ```
- **go** (len 132, sha d477d16b6c52828a...):

  ```
  {"k0":"﻿","k1":[2.2250738585072014e-308],"k2":"\u001f","k3":[9007199254740991,0,-9223372036854775808],"k4":">﻿􏿿ÿ\u2029􏿿"}
  ```
- **rust** (len 129, sha b143667fee45dbb2...):

  ```
  {"k0":"﻿","k1":[2.2250738585072014e-308],"k2":"\u001f","k3":[9007199254740991,0,-9223372036854775808],"k4":">﻿􏿿ÿ 􏿿"}
  ```
