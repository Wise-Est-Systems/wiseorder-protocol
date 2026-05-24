# Disagreement signature 54

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-DEL,contains-SMP,contains-U+2028,contains-U+2029,contains-bigint>2^53,contains-emoji`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-DEL, contains-SMP, contains-U+2028, contains-U+2029, contains-bigint>2^53, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 1

## Examples

### Example 1

- generator: `nested`
- input: `[{"\u001f   \"😀": [0.1, 3.141592653589793, "􏿿😀<￿<>/"], "tag": 2}, 9007199254740993, "﻿\u001f"]`

Canonical per implementation:
- **python** (len 107, sha 40a54dcdada1a419...):

  ```
  [{"\u001f   \"😀":[0.1,3.141592653589793,"􏿿😀<￿<>/"],"tag":2},9007199254740993,"﻿\u001f"]
  ```
- **go** (len 116, sha 6546497c85ddd1aa...):

  ```
  [{"\u001f\u2029\u2029\u2028\"😀":[0.1,3.141592653589793,"􏿿😀<￿<>/"],"tag":2},9007199254740993,"﻿\u001f"]
  ```
- **rust** (len 107, sha 40a54dcdada1a419...):

  ```
  [{"\u001f   \"😀":[0.1,3.141592653589793,"􏿿😀<￿<>/"],"tag":2},9007199254740993,"﻿\u001f"]
  ```
