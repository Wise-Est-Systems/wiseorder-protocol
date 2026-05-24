# Disagreement signature 85

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-C1-control,contains-DEL,contains-U+2028,contains-emoji`

**Count:** 6

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-C1-control, contains-DEL, contains-U+2028, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 4
  - object_unicode_keys: 2

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"\u0000\u0007\"<>߿": -396, "<\u0000￿ \">": -465, "&>": 935, "> ///\u0007�": -28, "\u0000😀": 756, "ࠀ߿": 558}`

Canonical per implementation:
- **python** (len 115, sha bc873a518a19ce0c...):

  ```
  {"\u0000\u0007\"<>߿":-396,"\u0000😀":756,"&>":935,"<\u0000￿ \">":-465,"> ///\u0007�":-28,"ࠀ߿":558}
  ```
- **go** (len 118, sha 9a5896cfa31a650e...):

  ```
  {"\u0000\u0007\"<>߿":-396,"\u0000😀":756,"&>":935,"<\u0000￿\u2028\">":-465,"> ///\u0007�":-28,"ࠀ߿":558}
  ```
- **rust** (len 115, sha bc873a518a19ce0c...):

  ```
  {"\u0000\u0007\"<>߿":-396,"\u0000😀":756,"&>":935,"<\u0000￿ \">":-465,"> ///\u0007�":-28,"ࠀ߿":558}
  ```

### Example 2

- generator: `nested`
- input: `[[{"Ā>ÿ\u0000\u0000\\😀": 1e-100, "tag": 2}, -1, "\u0007\u0000&  \\"], 0, "ĀĀ😀"]`

Canonical per implementation:
- **python** (len 87, sha a70727444e9eda78...):

  ```
  [[{"tag":2,"Ā>ÿ\u0000\u0000\\😀":1e-100},-1,"\u0007\u0000&  \\"],0,"ĀĀ😀"]
  ```
- **go** (len 90, sha 24266a533b29346f...):

  ```
  [[{"tag":2,"Ā>ÿ\u0000\u0000\\😀":1e-100},-1,"\u0007\u0000& \u2028\\"],0,"ĀĀ😀"]
  ```
- **rust** (len 87, sha a70727444e9eda78...):

  ```
  [[{"tag":2,"Ā>ÿ\u0000\u0000\\😀":1e-100},-1,"\u0007\u0000&  \\"],0,"ĀĀ😀"]
  ```

### Example 3

- generator: `object_unicode_keys`
- input: `{"߿Ā😀\\ÿ߿": -729, "ࠀ\u0007": 699, "\u001f\u0007>": -466, "😀<\u0007": 545, "߿ࠀ>߿": 21, "￿ �\u0000<": 600}`

Canonical per implementation:
- **python** (len 121, sha 2d343459b11bd867...):

  ```
  {"\u001f\u0007>":-466,"߿Ā😀\\ÿ߿":-729,"߿ࠀ>߿":21,"ࠀ\u0007":699,"￿ �\u0000<":600,"😀<\u0007":545}
  ```
- **go** (len 124, sha bac7c560e82759b6...):

  ```
  {"\u001f\u0007>":-466,"߿Ā😀\\ÿ߿":-729,"߿ࠀ>߿":21,"ࠀ\u0007":699,"￿\u2028�\u0000<":600,"😀<\u0007":545}
  ```
- **rust** (len 121, sha 2d343459b11bd867...):

  ```
  {"\u001f\u0007>":-466,"߿Ā😀\\ÿ߿":-729,"߿ࠀ>߿":21,"ࠀ\u0007":699,"￿ �\u0000<":600,"😀<\u0007":545}
  ```
