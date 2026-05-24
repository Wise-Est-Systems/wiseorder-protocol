# Disagreement signature 62

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-C1-control,contains-DEL,contains-SMP,contains-U+2028,contains-U+2029`

**Count:** 8

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-C1-control, contains-DEL, contains-SMP, contains-U+2028, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 4
  - nested: 3
  - array_order: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"<􏿿": -256, "Ā�\u0007": 836, "𐀀ÿ\\": 606, "\u0000": 177, " ": 314, "􏿿Ā<\u0007\u001f ": 756}`

Canonical per implementation:
- **python** (len 102, sha fc0af881e678c0c1...):

  ```
  {"\u0000":177,"<􏿿":-256,"Ā�\u0007":836," ":314,"𐀀ÿ\\":606,"􏿿Ā<\u0007\u001f ":756}
  ```
- **go** (len 108, sha f8d8f2b773cce0de...):

  ```
  {"\u0000":177,"<􏿿":-256,"Ā�\u0007":836,"\u2029":314,"𐀀ÿ\\":606,"􏿿Ā<\u0007\u001f\u2028":756}
  ```
- **rust** (len 102, sha fc0af881e678c0c1...):

  ```
  {"\u0000":177,"<􏿿":-256,"Ā�\u0007":836," ":314,"𐀀ÿ\\":606,"􏿿Ā<\u0007\u001f ":756}
  ```

### Example 2

- generator: `object_unicode_keys`
- input: `{" > ": -275, "/Āࠀࠀ ߿\u001f": -452, "\\𐀀\\\u0000\u001f\u0007\u0000": 150}`

Canonical per implementation:
- **python** (len 87, sha 13bc868ff63ba39d...):

  ```
  {"/Āࠀࠀ ߿\u001f":-452,"\\𐀀\\\u0000\u001f\u0007\u0000":150," > ":-275}
  ```
- **go** (len 96, sha 741e3bf32ad8dbf0...):

  ```
  {"/Āࠀࠀ\u2028߿\u001f":-452,"\\𐀀\\\u0000\u001f\u0007\u0000":150,"\u2029>\u2029":-275}
  ```
- **rust** (len 87, sha 13bc868ff63ba39d...):

  ```
  {"/Āࠀࠀ ߿\u001f":-452,"\\𐀀\\\u0000\u001f\u0007\u0000":150," > ":-275}
  ```

### Example 3

- generator: `nested`
- input: `[[{"𐀀<\\&<�": [{"<\u001f􏿿߿ 𐀀\u001f": 5e-324, "tag": 2}, 1.7976931348623157e+308, "􏿿�\u0007𐀀Ā\\ "], "tag": 9}, 0.3, "\"� ߿"], 10000000000.0, "￿/Ā"]`

Canonical per implementation:
- **python** (len 172, sha 7023ad6568c46c8c...):

  ```
  [[{"tag":9,"𐀀<\\&<�":[{"<\u001f􏿿߿ 𐀀\u001f":5e-324,"tag":2},1.7976931348623157e+308,"􏿿�\u0007𐀀Ā\\ "]},0.3,"\"� ߿"],10000000000.0,"￿/Ā"]
  ```
- **go** (len 181, sha 4e5678a209ae7838...):

  ```
  [[{"tag":9,"𐀀<\\&<�":[{"<\u001f􏿿߿\u2029𐀀\u001f":5e-324,"tag":2},1.7976931348623157e+308,"􏿿�\u0007𐀀Ā\\\u2028"]},0.3,"\"�\u2028߿"],10000000000.0,"￿/Ā"]
  ```
- **rust** (len 172, sha 7023ad6568c46c8c...):

  ```
  [[{"tag":9,"𐀀<\\&<�":[{"<\u001f􏿿߿ 𐀀\u001f":5e-324,"tag":2},1.7976931348623157e+308,"􏿿�\u0007𐀀Ā\\ "]},0.3,"\"� ߿"],10000000000.0,"￿/Ā"]
  ```
