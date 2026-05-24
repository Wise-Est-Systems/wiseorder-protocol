# Disagreement signature 50

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-DEL,contains-SMP,contains-U+2029,contains-emoji`

**Count:** 10

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-DEL, contains-SMP, contains-U+2029, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 6
  - nested: 2
  - array_order: 1
  - mixed_object: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"ࠀ\u0000ࠀĀ �": -9, "﻿ ÿ߿􏿿ࠀ\u0007ÿ": 730, "\\/": 87, " �😀𐀀￿￿": 715, "Ā": -293, "﻿/\\< ": -818}`

Canonical per implementation:
- **python** (len 122, sha 34192127d71508c9...):

  ```
  {" �😀𐀀￿￿":715,"\\/":87,"Ā":-293,"ࠀ\u0000ࠀĀ �":-9,"﻿/\\< ":-818,"﻿ ÿ߿􏿿ࠀ\u0007ÿ":730}
  ```
- **go** (len 131, sha e6926bdb49d1a420...):

  ```
  {" �😀𐀀￿￿":715,"\\/":87,"Ā":-293,"ࠀ\u0000ࠀĀ\u2029�":-9,"﻿/\\<\u2029":-818,"﻿\u2029ÿ߿􏿿ࠀ\u0007ÿ":730}
  ```
- **rust** (len 122, sha 34192127d71508c9...):

  ```
  {" �😀𐀀￿￿":715,"\\/":87,"Ā":-293,"ࠀ\u0000ࠀĀ �":-9,"﻿/\\< ":-818,"﻿ ÿ߿􏿿ࠀ\u0007ÿ":730}
  ```

### Example 2

- generator: `nested`
- input: `[[{"<😀": [0.2, 0.0, "\\\u0000﻿>�"], "tag": 1}, 2.2250738585072014e-308, "߿ 𐀀\u0000\""], 5e-324, " ߿ÿÿ\"ÿ￿\u001f"]`

Canonical per implementation:
- **python** (len 124, sha 7ee36fd263bbd8cc...):

  ```
  [[{"<😀":[0.2,0.0,"\\\u0000﻿>�"],"tag":1},2.2250738585072014e-308,"߿ 𐀀\u0000\""],5e-324," ߿ÿÿ\"ÿ￿\u001f"]
  ```
- **go** (len 127, sha 0f2e847ebf1cb812...):

  ```
  [[{"<😀":[0.2,0.0,"\\\u0000﻿>�"],"tag":1},2.2250738585072014e-308,"߿ 𐀀\u0000\""],5e-324,"\u2029߿ÿÿ\"ÿ￿\u001f"]
  ```
- **rust** (len 124, sha 7ee36fd263bbd8cc...):

  ```
  [[{"<😀":[0.2,0.0,"\\\u0000﻿>�"],"tag":1},2.2250738585072014e-308,"߿ 𐀀\u0000\""],5e-324," ߿ÿÿ\"ÿ￿\u001f"]
  ```

### Example 3

- generator: `object_unicode_keys`
- input: `{"􏿿𐀀Ā>􏿿": -829, "ÿ/<😀 \\": -71, "﻿/": -392, "ࠀ\u0000Ā": -103, "\u001f𐀀": 264}`

Canonical per implementation:
- **python** (len 93, sha af772ff17ad6f643...):

  ```
  {"\u001f𐀀":264,"ÿ/<😀 \\":-71,"ࠀ\u0000Ā":-103,"﻿/":-392,"􏿿𐀀Ā>􏿿":-829}
  ```
- **go** (len 96, sha ee8c0e91dc7bf93b...):

  ```
  {"\u001f𐀀":264,"ÿ/<😀\u2029\\":-71,"ࠀ\u0000Ā":-103,"﻿/":-392,"􏿿𐀀Ā>􏿿":-829}
  ```
- **rust** (len 93, sha af772ff17ad6f643...):

  ```
  {"\u001f𐀀":264,"ÿ/<😀 \\":-71,"ࠀ\u0000Ā":-103,"﻿/":-392,"􏿿𐀀Ā>􏿿":-829}
  ```
