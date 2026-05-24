# Disagreement signature 24

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-SMP,contains-U+2029,contains-bigint>2^53`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-SMP, contains-U+2029, contains-bigint>2^53

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 1

## Examples

### Example 1

- generator: `nested`
- input: `[{"𐀀￿/�\u001f\u0007>": [-9223372036854775808, 0.3, " 􏿿"], "tag": 4}, 1000000000000000.0, ">﻿"]`

Canonical per implementation:
- **python** (len 101, sha fa21487d51857c22...):

  ```
  [{"tag":4,"𐀀￿/�\u001f\u0007>":[-9223372036854775808,0.3," 􏿿"]},1000000000000000.0,">﻿"]
  ```
- **go** (len 104, sha 5f8e733f8225f196...):

  ```
  [{"tag":4,"𐀀￿/�\u001f\u0007>":[-9223372036854775808,0.3,"\u2029􏿿"]},1000000000000000.0,">﻿"]
  ```
- **rust** (len 101, sha fa21487d51857c22...):

  ```
  [{"tag":4,"𐀀￿/�\u001f\u0007>":[-9223372036854775808,0.3," 􏿿"]},1000000000000000.0,">﻿"]
  ```
