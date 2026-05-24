# Disagreement signature 36

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-SMP,contains-U+2028,contains-bigint>2^53,contains-emoji`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-SMP, contains-U+2028, contains-bigint>2^53, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 1

## Examples

### Example 1

- generator: `nested`
- input: `{">\u0007😀</𐀀\u0000\"": [{"<Ā&": {"﻿ÿÿ߿ ": 9223372036854775807, "tag": 7}, "tag": 0}, 2.718281828459045, "߿�Ā\"> ÿ"], "tag": 9}`

Canonical per implementation:
- **python** (len 137, sha 802cefe741f29079...):

  ```
  {">\u0007😀</𐀀\u0000\"":[{"<Ā&":{"tag":7,"﻿ÿÿ߿ ":9223372036854775807},"tag":0},2.718281828459045,"߿�Ā\"> ÿ"],"tag":9}
  ```
- **go** (len 143, sha abaa0aef49894566...):

  ```
  {">\u0007😀</𐀀\u0000\"":[{"<Ā&":{"tag":7,"﻿ÿÿ߿\u2028":9223372036854775807},"tag":0},2.718281828459045,"߿�Ā\">\u2028ÿ"],"tag":9}
  ```
- **rust** (len 137, sha 802cefe741f29079...):

  ```
  {">\u0007😀</𐀀\u0000\"":[{"<Ā&":{"tag":7,"﻿ÿÿ߿ ":9223372036854775807},"tag":0},2.718281828459045,"߿�Ā\"> ÿ"],"tag":9}
  ```
