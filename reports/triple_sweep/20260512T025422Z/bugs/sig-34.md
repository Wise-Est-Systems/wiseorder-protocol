# Disagreement signature 34

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-C1-control,contains-SMP,contains-U+2028,contains-U+2029,contains-emoji`

**Count:** 13

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-C1-control, contains-SMP, contains-U+2028, contains-U+2029, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 11
  - nested: 2

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"߿ ￿ÿ􏿿\u0007😀>": 636, "ࠀ\u0007 �😀": -807, "\u0007": -644, " \u001f\u0007\\ ࠀ": -934, "\\😀\u0007": -383}`

Canonical per implementation:
- **python** (len 123, sha 01ab08d067229e57...):

  ```
  {"\u0007":-644,"\\😀\u0007":-383,"߿ ￿ÿ􏿿\u0007😀>":636,"ࠀ\u0007 �😀":-807," \u001f\u0007\\ ࠀ":-934}
  ```
- **go** (len 129, sha 6fe508b8614bd8b7...):

  ```
  {"\u0007":-644,"\\😀\u0007":-383,"߿\u2028￿ÿ􏿿\u0007😀>":636,"ࠀ\u0007 �😀":-807,"\u2029\u001f\u0007\\ ࠀ":-934}
  ```
- **rust** (len 123, sha 01ab08d067229e57...):

  ```
  {"\u0007":-644,"\\😀\u0007":-383,"߿ ￿ÿ􏿿\u0007😀>":636,"ࠀ\u0007 �😀":-807," \u001f\u0007\\ ࠀ":-934}
  ```

### Example 2

- generator: `nested`
- input: `{"\u001fĀ\u001f𐀀ࠀ￿": [[[[-2147483648, 9007199254740992, " \\"], 2.2250738585072014e-308, "& 😀 "], 1e+17, "\u001f>߿&ÿĀÿ "], 1e-100, "&😀ÿ𐀀>"], "tag": 9}`

Canonical per implementation:
- **python** (len 167, sha 9ee358be65300738...):

  ```
  {"\u001fĀ\u001f𐀀ࠀ￿":[[[[-2147483648,9007199254740992," \\"],2.2250738585072014e-308,"& 😀 "],1e+17,"\u001f>߿&ÿĀÿ "],1e-100,"&😀ÿ𐀀>"],"tag":9}
  ```
- **go** (len 173, sha c64b845185a73b5f...):

  ```
  {"\u001fĀ\u001f𐀀ࠀ￿":[[[[-2147483648,9007199254740992," \\"],2.2250738585072014e-308,"&\u2028😀\u2029"],1e+17,"\u001f>߿&ÿĀÿ "],1e-100,"&😀ÿ𐀀>"],"tag":9}
  ```
- **rust** (len 167, sha 9ee358be65300738...):

  ```
  {"\u001fĀ\u001f𐀀ࠀ￿":[[[[-2147483648,9007199254740992," \\"],2.2250738585072014e-308,"& 😀 "],1e+17,"\u001f>߿&ÿĀÿ "],1e-100,"&😀ÿ𐀀>"],"tag":9}
  ```

### Example 3

- generator: `object_unicode_keys`
- input: `{"\u001f\u0007 Ā Ā😀𐀀": 846, "￿􏿿 &": -23, "/&𐀀\\  ": 908, "�\u0007ࠀÿ\" ": 163, ">&😀": 770}`

Canonical per implementation:
- **python** (len 116, sha e6988dd078208275...):

  ```
  {"\u001f\u0007 Ā Ā😀𐀀":846,"/&𐀀\\  ":908,">&😀":770,"�\u0007ࠀÿ\" ":163,"￿􏿿 &":-23}
  ```
- **go** (len 131, sha 815726b6a9a19cfe...):

  ```
  {"\u001f\u0007\u2029Ā\u2028Ā😀𐀀":846,"/&𐀀\\ \u2029":908,">&😀":770,"�\u0007ࠀÿ\"\u2028":163,"￿􏿿\u2028&":-23}
  ```
- **rust** (len 116, sha e6988dd078208275...):

  ```
  {"\u001f\u0007 Ā Ā😀𐀀":846,"/&𐀀\\  ":908,">&😀":770,"�\u0007ࠀÿ\" ":163,"￿􏿿 &":-23}
  ```
