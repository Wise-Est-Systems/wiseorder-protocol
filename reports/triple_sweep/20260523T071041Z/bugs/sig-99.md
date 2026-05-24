# Disagreement signature 99

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-C1-control,contains-DEL,contains-SMP,contains-U+2028,contains-U+2029,contains-bigint>2^53`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-C1-control, contains-DEL, contains-SMP, contains-U+2028, contains-U+2029, contains-bigint>2^53

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 1

## Examples

### Example 1

- generator: `nested`
- input: `[[{"\u0000﻿ ": {"\"\u001f Ā\\\u0007": {"<￿\\": 10000000000.0, "tag": 0}, "tag": 8}, "tag": 8}, 2.718281828459045, "􏿿"], 9007199254740993, "ÿ  \u001f߿ࠀ\""]`

Canonical per implementation:
- **python** (len 164, sha 706190d70c424f0b...):

  ```
  [[{"\u0000﻿ ":{"\"\u001f Ā\\\u0007":{"tag":0,"<￿\\":10000000000.0},"tag":8},"tag":8},2.718281828459045,"􏿿"],9007199254740993,"ÿ  \u001f߿ࠀ\""]
  ```
- **go** (len 173, sha ad933ce3ce4e789d...):

  ```
  [[{"\u0000﻿\u2028":{"\"\u001f\u2029Ā\\\u0007":{"tag":0,"<￿\\":10000000000.0},"tag":8},"tag":8},2.718281828459045,"􏿿"],9007199254740993,"ÿ \u2028\u001f߿ࠀ\""]
  ```
- **rust** (len 164, sha 706190d70c424f0b...):

  ```
  [[{"\u0000﻿ ":{"\"\u001f Ā\\\u0007":{"tag":0,"<￿\\":10000000000.0},"tag":8},"tag":8},2.718281828459045,"􏿿"],9007199254740993,"ÿ  \u001f߿ࠀ\""]
  ```
