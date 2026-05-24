# Disagreement signature 51

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-C1-control,contains-DEL,contains-SMP,contains-U+2028,contains-emoji`

**Count:** 10

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-C1-control, contains-DEL, contains-SMP, contains-U+2028, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 5
  - nested: 5

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"\"\u0000￿": 111, "𐀀/": -459, "<😀>߿": -315, "ÿ\u001fĀ \\": 774, "<<Ā𐀀": 433}`

Canonical per implementation:
- **python** (len 94, sha c3734d444af1aa70...):

  ```
  {"\"\u0000￿":111,"<😀>߿":-315,"<<Ā𐀀":433,"ÿ\u001fĀ \\":774,"𐀀/":-459}
  ```
- **go** (len 97, sha 435cdafb43927100...):

  ```
  {"\"\u0000￿":111,"<😀>߿":-315,"<<Ā𐀀":433,"ÿ\u001fĀ\u2028\\":774,"𐀀/":-459}
  ```
- **rust** (len 94, sha c3734d444af1aa70...):

  ```
  {"\"\u0000￿":111,"<😀>߿":-315,"<<Ā𐀀":433,"ÿ\u001fĀ \\":774,"𐀀/":-459}
  ```

### Example 2

- generator: `nested`
- input: `{"ÿ< \u0007": [[[[1e+17, 0.30000000000000004, ">😀\u0007<"], 0.3333333333333333, " ￿😀ࠀ"], 10000000000.0, "�􏿿>"], 1e+16, "/ 􏿿�&\u0000"], "tag": 0}`

Canonical per implementation:
- **python** (len 167, sha 768f44837e1e2e8e...):

  ```
  {"tag":0,"ÿ< \u0007":[[[[1e+17,0.30000000000000004,">😀\u0007<"],0.3333333333333333," ￿😀ࠀ"],10000000000.0,"�􏿿>"],1e+16,"/ 􏿿�&\u0000"]}
  ```
- **go** (len 173, sha 80314ecf0c0f1690...):

  ```
  {"tag":0,"ÿ<\u2028\u0007":[[[[1e+17,0.30000000000000004,">😀\u0007<"],0.3333333333333333," ￿😀ࠀ"],10000000000.0,"�􏿿>"],1e+16,"/\u2028􏿿�&\u0000"]}
  ```
- **rust** (len 167, sha 768f44837e1e2e8e...):

  ```
  {"tag":0,"ÿ< \u0007":[[[[1e+17,0.30000000000000004,">😀\u0007<"],0.3333333333333333," ￿😀ࠀ"],10000000000.0,"�􏿿>"],1e+16,"/ 􏿿�&\u0000"]}
  ```

### Example 3

- generator: `nested`
- input: `[[[{"ÿ\u0007 / ࠀ": 1.7976931348623157e+308, "tag": 7}, 0.1, "￿􏿿"], 0.0, "�\u0000Ā>􏿿&\"\u0000"], -0.0, ">𐀀Ā\u0007￿<😀ࠀ"]`

Canonical per implementation:
- **python** (len 141, sha 7422694da40ffb22...):

  ```
  [[[{"tag":7,"ÿ\u0007 / ࠀ":1.7976931348623157e+308},0.1,"￿􏿿"],0.0,"�\u0000Ā>􏿿&\"\u0000"],-0.0,">𐀀Ā\u0007￿<😀ࠀ"]
  ```
- **go** (len 147, sha ed6f21d222207de6...):

  ```
  [[[{"tag":7,"ÿ\u0007\u2028/\u2028ࠀ":1.7976931348623157e+308},0.1,"￿􏿿"],0.0,"�\u0000Ā>􏿿&\"\u0000"],-0.0,">𐀀Ā\u0007￿<😀ࠀ"]
  ```
- **rust** (len 141, sha 7422694da40ffb22...):

  ```
  [[[{"tag":7,"ÿ\u0007 / ࠀ":1.7976931348623157e+308},0.1,"￿􏿿"],0.0,"�\u0000Ā>􏿿&\"\u0000"],-0.0,">𐀀Ā\u0007￿<😀ࠀ"]
  ```
