# Disagreement signature 78

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-DEL,contains-U+2028,contains-emoji`

**Count:** 6

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-DEL, contains-U+2028, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 6

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"\u001f\" \u0000\u0007": 34, "￿<߿ÿ": -321, "😀\u001f /﻿<": -954, "Ā><ÿ": 207, "\u0000": -570}`

Canonical per implementation:
- **python** (len 99, sha fe36fc676aee4c66...):

  ```
  {"\u0000":-570,"\u001f\" \u0000\u0007":34,"Ā><ÿ":207,"￿<߿ÿ":-321,"😀\u001f /﻿<":-954}
  ```
- **go** (len 102, sha 52e8a473bbdf23fe...):

  ```
  {"\u0000":-570,"\u001f\"\u2028\u0000\u0007":34,"Ā><ÿ":207,"￿<߿ÿ":-321,"😀\u001f /﻿<":-954}
  ```
- **rust** (len 99, sha fe36fc676aee4c66...):

  ```
  {"\u0000":-570,"\u001f\" \u0000\u0007":34,"Ā><ÿ":207,"￿<߿ÿ":-321,"😀\u001f /﻿<":-954}
  ```

### Example 2

- generator: `object_unicode_keys`
- input: `{"😀😀ÿ\u001f\\�\"": -686, "<ÿ": 114, "\u001f😀ࠀ﻿>": 223, "& ߿ ": -352}`

Canonical per implementation:
- **python** (len 84, sha a294f26eec8eb742...):

  ```
  {"\u001f😀ࠀ﻿>":223,"& ߿ ":-352,"<ÿ":114,"😀😀ÿ\u001f\\�\"":-686}
  ```
- **go** (len 90, sha b4caa5eb184a1dce...):

  ```
  {"\u001f😀ࠀ﻿>":223,"&\u2028߿\u2028":-352,"<ÿ":114,"😀😀ÿ\u001f\\�\"":-686}
  ```
- **rust** (len 84, sha a294f26eec8eb742...):

  ```
  {"\u001f😀ࠀ﻿>":223,"& ߿ ":-352,"<ÿ":114,"😀😀ÿ\u001f\\�\"":-686}
  ```

### Example 3

- generator: `object_unicode_keys`
- input: `{"<\\>": 531, "/": -78, "￿😀": 41, "﻿ ߿ÿ \u0000&": -369}`

Canonical per implementation:
- **python** (len 60, sha 6deb114773b3b50a...):

  ```
  {"<\\>":531,"/":-78,"﻿ ߿ÿ \u0000&":-369,"￿😀":41}
  ```
- **go** (len 63, sha a12cba701d1ec602...):

  ```
  {"<\\>":531,"/":-78,"﻿\u2028߿ÿ \u0000&":-369,"￿😀":41}
  ```
- **rust** (len 60, sha 6deb114773b3b50a...):

  ```
  {"<\\>":531,"/":-78,"﻿ ߿ÿ \u0000&":-369,"￿😀":41}
  ```
