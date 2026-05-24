# Disagreement signature 60

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-DEL,contains-SMP,contains-U+2028,contains-U+2029,contains-emoji`

**Count:** 8

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-DEL, contains-SMP, contains-U+2028, contains-U+2029, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 4
  - nested: 3
  - mixed_object: 1

## Examples

### Example 1

- generator: `nested`
- input: `[{"𐀀�߿/\u0000ࠀ": [1e+16, 1000000000000000.0, "﻿￿\\😀￿𐀀&\u0000"], "tag": 0}, 10000000000.0, "\"  >\\😀\u0000"]`

Canonical per implementation:
- **python** (len 129, sha 4de32cf127ffcef0...):

  ```
  [{"tag":0,"𐀀�߿/\u0000ࠀ":[1e+16,1000000000000000.0,"﻿￿\\😀￿𐀀&\u0000"]},10000000000.0,"\"  >\\😀\u0000"]
  ```
- **go** (len 135, sha 57564fc9c07f9602...):

  ```
  [{"tag":0,"𐀀�߿/\u0000ࠀ":[1e+16,1000000000000000.0,"﻿￿\\😀￿𐀀&\u0000"]},10000000000.0,"\"\u2028\u2029>\\😀\u0000"]
  ```
- **rust** (len 129, sha 4de32cf127ffcef0...):

  ```
  [{"tag":0,"𐀀�߿/\u0000ࠀ":[1e+16,1000000000000000.0,"﻿￿\\😀￿𐀀&\u0000"]},10000000000.0,"\"  >\\😀\u0000"]
  ```

### Example 2

- generator: `mixed_object`
- input: `{"k1": {}, "k3": false, "k0": "😀\u0000﻿߿\"", "k5": " 𐀀￿\"�<", "k2": "ࠀ&￿  ࠀ", "k4": [1e-100, 5e-324, 0.001]}`

Canonical per implementation:
- **python** (len 121, sha 83610c6b61b4c924...):

  ```
  {"k0":"😀\u0000﻿߿\"","k1":{},"k2":"ࠀ&￿  ࠀ","k3":false,"k4":[1e-100,5e-324,0.001],"k5":" 𐀀￿\"�<"}
  ```
- **go** (len 130, sha 08b9696e102a827e...):

  ```
  {"k0":"😀\u0000﻿߿\"","k1":{},"k2":"ࠀ&￿\u2028\u2028ࠀ","k3":false,"k4":[1e-100,5e-324,0.001],"k5":"\u2029𐀀￿\"�<"}
  ```
- **rust** (len 121, sha 83610c6b61b4c924...):

  ```
  {"k0":"😀\u0000﻿߿\"","k1":{},"k2":"ࠀ&￿  ࠀ","k3":false,"k4":[1e-100,5e-324,0.001],"k5":" 𐀀￿\"�<"}
  ```

### Example 3

- generator: `object_unicode_keys`
- input: `{"&﻿\u0000Ā𐀀/😀>": 282, "\"": -720, " ": 682, "\u0000<�": 257, "￿\\ \\￿&": 678, "  ": 11}`

Canonical per implementation:
- **python** (len 101, sha 6e3cfe232368e61e...):

  ```
  {"\"":-720,"&﻿\u0000Ā𐀀/😀>":282,"\u0000<�":257," ":682,"  ":11,"￿\\ \\￿&":678}
  ```
- **go** (len 110, sha f7de1960dd0a0d8c...):

  ```
  {"\"":-720,"&﻿\u0000Ā𐀀/😀>":282,"\u0000<�":257,"\u2028":682,"\u2029 ":11,"￿\\\u2028\\￿&":678}
  ```
- **rust** (len 101, sha 6e3cfe232368e61e...):

  ```
  {"\"":-720,"&﻿\u0000Ā𐀀/😀>":282,"\u0000<�":257," ":682,"  ":11,"￿\\ \\￿&":678}
  ```
