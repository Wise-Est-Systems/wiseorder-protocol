# Disagreement signature 10

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-C1-control,contains-DEL,contains-SMP,contains-U+2029,contains-emoji`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-C1-control, contains-DEL, contains-SMP, contains-U+2029, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 1

## Examples

### Example 1

- generator: `nested`
- input: `{" � ߿<": [{"\\\u0000￿\u001f😀": {"􏿿ÿ": [9007199254740991, 0.3333333333333333, "﻿"], "tag": 2}, "tag": 6}, 0.3, "Ā߿𐀀"], "tag": 3}`

Canonical per implementation:
- **python** (len 145, sha 0d5c1927c460ce0c...):

  ```
  {"tag":3," � ߿<":[{"\\\u0000￿\u001f😀":{"tag":2,"􏿿ÿ":[9007199254740991,0.3333333333333333,"﻿"]},"tag":6},0.3,"Ā߿𐀀"]}
  ```
- **go** (len 148, sha ba11f092658419a8...):

  ```
  {"tag":3,"\u2029� ߿<":[{"\\\u0000￿\u001f😀":{"tag":2,"􏿿ÿ":[9007199254740991,0.3333333333333333,"﻿"]},"tag":6},0.3,"Ā߿𐀀"]}
  ```
- **rust** (len 145, sha 0d5c1927c460ce0c...):

  ```
  {"tag":3," � ߿<":[{"\\\u0000￿\u001f😀":{"tag":2,"􏿿ÿ":[9007199254740991,0.3333333333333333,"﻿"]},"tag":6},0.3,"Ā߿𐀀"]}
  ```
