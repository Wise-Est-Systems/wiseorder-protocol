# Disagreement signature 34

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C1-control,contains-SMP,contains-U+2028,contains-U+2029,contains-emoji`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C1-control, contains-SMP, contains-U+2028, contains-U+2029, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"Ā\\﻿  \\￿": 597, "&\"�ࠀ<": -595, "􏿿Ā": 900, "ÿ😀߿�": 815, " Ā߿𐀀/😀": 926}`

Canonical per implementation:
- **python** (len 102, sha 6ae824e472ae1f7c...):

  ```
  {"&\"�ࠀ<":-595,"ÿ😀߿�":815,"Ā\\﻿  \\￿":597," Ā߿𐀀/😀":926,"􏿿Ā":900}
  ```
- **go** (len 111, sha f49b9ed7a26e8330...):

  ```
  {"&\"�ࠀ<":-595,"ÿ😀߿�":815,"Ā\\﻿\u2028\u2029\\￿":597,"\u2029Ā߿𐀀/😀":926,"􏿿Ā":900}
  ```
- **rust** (len 102, sha 6ae824e472ae1f7c...):

  ```
  {"&\"�ࠀ<":-595,"ÿ😀߿�":815,"Ā\\﻿  \\￿":597," Ā߿𐀀/😀":926,"􏿿Ā":900}
  ```
