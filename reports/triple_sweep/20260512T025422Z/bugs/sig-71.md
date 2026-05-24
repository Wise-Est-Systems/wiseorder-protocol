# Disagreement signature 71

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-SMP,contains-U+2029,contains-emoji`

**Count:** 7

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-SMP, contains-U+2029, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 4
  - nested: 3

## Examples

### Example 1

- generator: `nested`
- input: `{"&\\/>&ࠀ": {"\"𐀀 >�Ā&": [[1e+16, 0.2, "ÿࠀĀ﻿😀&\"ࠀ"], 2.718281828459045, "\u0000\u001f\"& \\﻿😀"], "tag": 8}, "tag": 1}`

Canonical per implementation:
- **python** (len 133, sha 47dbfbd47658f829...):

  ```
  {"&\\/>&ࠀ":{"\"𐀀 >�Ā&":[[1e+16,0.2,"ÿࠀĀ﻿😀&\"ࠀ"],2.718281828459045,"\u0000\u001f\"& \\﻿😀"],"tag":8},"tag":1}
  ```
- **go** (len 136, sha d53525d3bf9024da...):

  ```
  {"&\\/>&ࠀ":{"\"𐀀\u2029>�Ā&":[[1e+16,0.2,"ÿࠀĀ﻿😀&\"ࠀ"],2.718281828459045,"\u0000\u001f\"& \\﻿😀"],"tag":8},"tag":1}
  ```
- **rust** (len 133, sha 47dbfbd47658f829...):

  ```
  {"&\\/>&ࠀ":{"\"𐀀 >�Ā&":[[1e+16,0.2,"ÿࠀĀ﻿😀&\"ࠀ"],2.718281828459045,"\u0000\u001f\"& \\﻿😀"],"tag":8},"tag":1}
  ```

### Example 2

- generator: `object_unicode_keys`
- input: `{"Ā😀😀": -803, "\u0007ÿ﻿\u001f􏿿/": 356, "/\u001fࠀ": -995, "﻿\u0007\u001f ": -643}`

Canonical per implementation:
- **python** (len 92, sha 034c4265fd33b12c...):

  ```
  {"\u0007ÿ﻿\u001f􏿿/":356,"/\u001fࠀ":-995,"Ā😀😀":-803,"﻿\u0007\u001f ":-643}
  ```
- **go** (len 95, sha 7c62cdda67d69223...):

  ```
  {"\u0007ÿ﻿\u001f􏿿/":356,"/\u001fࠀ":-995,"Ā😀😀":-803,"﻿\u0007\u001f\u2029":-643}
  ```
- **rust** (len 92, sha 034c4265fd33b12c...):

  ```
  {"\u0007ÿ﻿\u001f􏿿/":356,"/\u001fࠀ":-995,"Ā😀😀":-803,"﻿\u0007\u001f ":-643}
  ```

### Example 3

- generator: `object_unicode_keys`
- input: `{"Ā": 641, "\u0000\\􏿿😀\\\\": -157, "𐀀": -240, "  ": 920, "﻿ �\u0007\u001f\\\u001f": -985}`

Canonical per implementation:
- **python** (len 96, sha cea3f78e08aecfe8...):

  ```
  {"\u0000\\􏿿😀\\\\":-157,"  ":920,"Ā":641,"﻿ �\u0007\u001f\\\u001f":-985,"𐀀":-240}
  ```
- **go** (len 99, sha 300dc3e2bde3a3b8...):

  ```
  {"\u0000\\􏿿😀\\\\":-157," \u2029":920,"Ā":641,"﻿ �\u0007\u001f\\\u001f":-985,"𐀀":-240}
  ```
- **rust** (len 96, sha cea3f78e08aecfe8...):

  ```
  {"\u0000\\􏿿😀\\\\":-157,"  ":920,"Ā":641,"﻿ �\u0007\u001f\\\u001f":-985,"𐀀":-240}
  ```
