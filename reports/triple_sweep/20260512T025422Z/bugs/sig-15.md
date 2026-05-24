# Disagreement signature 15

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-C1-control,contains-DEL,contains-SMP,contains-U+2028,contains-U+2029,contains-emoji`

**Count:** 17

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-C1-control, contains-DEL, contains-SMP, contains-U+2028, contains-U+2029, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 7
  - object_unicode_keys: 7
  - array_order: 3

## Examples

### Example 1

- generator: `nested`
- input: `{"𐀀 ÿ\" ": [[[3.141592653589793, 0.3333333333333333, "ÿ"], 3.14159, "😀  \u0007"], 2.718281828459045, "\u001f\u0000 / "], "tag": 1}`

Canonical per implementation:
- **python** (len 138, sha 84e71ff4fe945e83...):

  ```
  {"tag":1,"𐀀 ÿ\" ":[[[3.141592653589793,0.3333333333333333,"ÿ"],3.14159,"😀  \u0007"],2.718281828459045,"\u001f\u0000 / "]}
  ```
- **go** (len 147, sha a517532a3195ba69...):

  ```
  {"tag":1,"𐀀\u2029ÿ\"\u2029":[[[3.141592653589793,0.3333333333333333,"ÿ"],3.14159,"😀  \u0007"],2.718281828459045,"\u001f\u0000 /\u2028"]}
  ```
- **rust** (len 138, sha 84e71ff4fe945e83...):

  ```
  {"tag":1,"𐀀 ÿ\" ":[[[3.141592653589793,0.3333333333333333,"ÿ"],3.14159,"😀  \u0007"],2.718281828459045,"\u001f\u0000 / "]}
  ```

### Example 2

- generator: `object_unicode_keys`
- input: `{" ÿ �￿Ā\u0007/": -151, "  \u001f \\": 365, "߿😀>": 648, "\u0007ÿĀ\"<😀Ā𐀀": 250}`

Canonical per implementation:
- **python** (len 97, sha 0ec82282df9978f9...):

  ```
  {"\u0007ÿĀ\"<😀Ā𐀀":250," ÿ �￿Ā\u0007/":-151,"  \u001f \\":365,"߿😀>":648}
  ```
- **go** (len 103, sha f02115e5ba7e280e...):

  ```
  {"\u0007ÿĀ\"<😀Ā𐀀":250," ÿ\u2028�￿Ā\u0007/":-151," \u2029\u001f \\":365,"߿😀>":648}
  ```
- **rust** (len 97, sha 0ec82282df9978f9...):

  ```
  {"\u0007ÿĀ\"<😀Ā𐀀":250," ÿ �￿Ā\u0007/":-151,"  \u001f \\":365,"߿😀>":648}
  ```

### Example 3

- generator: `object_unicode_keys`
- input: `{"􏿿�Ā\u001f": -387, "😀": 268, " 😀ࠀ\\ ࠀ\u0000": -565, "Ā ࠀ&  \u0007": -894}`

Canonical per implementation:
- **python** (len 97, sha e8a95b6d0c5eeb27...):

  ```
  {" 😀ࠀ\\ ࠀ\u0000":-565,"Ā ࠀ&  \u0007":-894,"😀":268,"􏿿�Ā\u001f":-387}
  ```
- **go** (len 109, sha c227616e495cb829...):

  ```
  {"\u2029😀ࠀ\\ ࠀ\u0000":-565,"Ā\u2029ࠀ&\u2028\u2029\u0007":-894,"😀":268,"􏿿�Ā\u001f":-387}
  ```
- **rust** (len 97, sha e8a95b6d0c5eeb27...):

  ```
  {" 😀ࠀ\\ ࠀ\u0000":-565,"Ā ࠀ&  \u0007":-894,"😀":268,"􏿿�Ā\u001f":-387}
  ```
