# Disagreement signature 90

**Signature:** `agree:go+python|outlier:rust | longest:rust,shortest:python | markers:contains-BOM,contains-C0-control,contains-SMP,contains-bigint>2^53,contains-bigint>=2^64,contains-bigint>i64`

**Count:** 1

**Partition:** agree:go+python|outlier:rust

**Outlier:** rust

**Markers:** contains-BOM, contains-C0-control, contains-SMP, contains-bigint>2^53, contains-bigint>=2^64, contains-bigint>i64

**Length pattern:** longest:rust,shortest:python

**By generator:**
  - nested: 1

## Examples

### Example 1

- generator: `nested`
- input: `[[{"߿﻿": 3.14159, "tag": 2}, 0.3, "/􏿿﻿\u001f𐀀\\ 𐀀"], 18446744073709551616, "﻿"]`

Canonical per implementation:
- **python** (len 88, sha d14a314b3eee528b...):

  ```
  [[{"tag":2,"߿﻿":3.14159},0.3,"/􏿿﻿\u001f𐀀\\ 𐀀"],18446744073709551616,"﻿"]
  ```
- **go** (len 88, sha d14a314b3eee528b...):

  ```
  [[{"tag":2,"߿﻿":3.14159},0.3,"/􏿿﻿\u001f𐀀\\ 𐀀"],18446744073709551616,"﻿"]
  ```
- **rust** (len 90, sha 3912b34f1597beb6...):

  ```
  [[{"tag":2,"߿﻿":3.14159},0.3,"/􏿿﻿\u001f𐀀\\ 𐀀"],1.8446744073709552e+19,"﻿"]
  ```
