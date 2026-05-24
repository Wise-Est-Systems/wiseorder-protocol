# Disagreement signature 7

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-C1-control,contains-SMP,contains-U+2029,contains-emoji`

**Count:** 3

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-C1-control, contains-SMP, contains-U+2029, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 3

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{" </߿\u0000/😀߿": -651, "\\�\u001f<𐀀߿😀𐀀": -971, "": 867, " 􏿿﻿": -396, "߿": 617, "\"\\<߿\u0000": 31}`

Canonical per implementation:
- **python** (len 118, sha a8abf87926f36475...):

  ```
  {" </߿\u0000/😀߿":-651,"\"\\<߿\u0000":31,"\\�\u001f<𐀀߿😀𐀀":-971,"":867,"߿":617," 􏿿﻿":-396}
  ```
- **go** (len 121, sha bd581ae81054e2fd...):

  ```
  {" </߿\u0000/😀߿":-651,"\"\\<߿\u0000":31,"\\�\u001f<𐀀߿😀𐀀":-971,"":867,"߿":617,"\u2029􏿿﻿":-396}
  ```
- **rust** (len 118, sha a8abf87926f36475...):

  ```
  {" </߿\u0000/😀߿":-651,"\"\\<߿\u0000":31,"\\�\u001f<𐀀߿😀𐀀":-971,"":867,"߿":617," 􏿿﻿":-396}
  ```

### Example 2

- generator: `object_unicode_keys`
- input: `{"\u0007😀ࠀÿ�": -505, "Ā􏿿\u001f\"": 652, "ÿ�\\􏿿<߿/": 258, "/": 770, ">﻿ ﻿\" ࠀ": 228}`

Canonical per implementation:
- **python** (len 103, sha 49fd645121e20e50...):

  ```
  {"\u0007😀ࠀÿ�":-505,"/":770,">﻿ ﻿\" ࠀ":228,"ÿ�\\􏿿<߿/":258,"Ā􏿿\u001f\"":652}
  ```
- **go** (len 106, sha d2ee7cf9a320c441...):

  ```
  {"\u0007😀ࠀÿ�":-505,"/":770,">﻿ ﻿\"\u2029ࠀ":228,"ÿ�\\􏿿<߿/":258,"Ā􏿿\u001f\"":652}
  ```
- **rust** (len 103, sha 49fd645121e20e50...):

  ```
  {"\u0007😀ࠀÿ�":-505,"/":770,">﻿ ﻿\" ࠀ":228,"ÿ�\\􏿿<߿/":258,"Ā􏿿\u001f\"":652}
  ```

### Example 3

- generator: `object_unicode_keys`
- input: `{">�􏿿﻿�Ā\\ ": 585, "𐀀�߿ࠀ\u001f": 717, "😀Ā": 897, "�� � &\u001f": -614, "\u001f>😀": 402, " \\": 757}`

Canonical per implementation:
- **python** (len 125, sha 4b4b282b4606dbc6...):

  ```
  {"\u001f>😀":402," \\":757,">�􏿿﻿�Ā\\ ":585,"�� � &\u001f":-614,"𐀀�߿ࠀ\u001f":717,"😀Ā":897}
  ```
- **go** (len 128, sha 32788c00860c507f...):

  ```
  {"\u001f>😀":402," \\":757,">�􏿿﻿�Ā\\ ":585,"�� �\u2029&\u001f":-614,"𐀀�߿ࠀ\u001f":717,"😀Ā":897}
  ```
- **rust** (len 125, sha 4b4b282b4606dbc6...):

  ```
  {"\u001f>😀":402," \\":757,">�􏿿﻿�Ā\\ ":585,"�� � &\u001f":-614,"𐀀�߿ࠀ\u001f":717,"😀Ā":897}
  ```
