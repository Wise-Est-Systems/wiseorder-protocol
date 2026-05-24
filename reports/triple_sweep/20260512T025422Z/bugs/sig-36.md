# Disagreement signature 36

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-C1-control,contains-SMP,contains-U+2029,contains-emoji`

**Count:** 12

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-C1-control, contains-SMP, contains-U+2029, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 5
  - nested: 4
  - array_order: 2
  - mixed_object: 1

## Examples

### Example 1

- generator: `array_order`
- input: `["ࠀ߿ ", "😀<� ", "\u0000", "𐀀Ā𐀀 "]`

Canonical per implementation:
- **python** (len 51, sha 198097148194a742...):

  ```
  ["ࠀ߿ ","😀<� ","\u0000","𐀀Ā𐀀 "]
  ```
- **go** (len 57, sha 43f3b8568e39e9a8...):

  ```
  ["ࠀ߿\u2029","😀<� ","\u0000","𐀀Ā𐀀\u2029"]
  ```
- **rust** (len 51, sha 198097148194a742...):

  ```
  ["ࠀ߿ ","😀<� ","\u0000","𐀀Ā𐀀 "]
  ```

### Example 2

- generator: `object_unicode_keys`
- input: `{"ÿÿ𐀀�􏿿": 742, "\"\"😀Ā ߿\u0007": -341, "😀\"😀\u0000": 273}`

Canonical per implementation:
- **python** (len 77, sha fd1ea7d9eea6d867...):

  ```
  {"\"\"😀Ā ߿\u0007":-341,"ÿÿ𐀀�􏿿":742,"😀\"😀\u0000":273}
  ```
- **go** (len 80, sha 1c0b0d548e491bf8...):

  ```
  {"\"\"😀Ā\u2029߿\u0007":-341,"ÿÿ𐀀�􏿿":742,"😀\"😀\u0000":273}
  ```
- **rust** (len 77, sha fd1ea7d9eea6d867...):

  ```
  {"\"\"😀Ā ߿\u0007":-341,"ÿÿ𐀀�􏿿":742,"😀\"😀\u0000":273}
  ```

### Example 3

- generator: `object_unicode_keys`
- input: `{"\u001fÿ": 357, "􏿿߿\"": -510, " \u001f\u001f": 314, "&😀 ": -138, " ￿Ā&": 384, "😀𐀀߿￿  ": -522}`

Canonical per implementation:
- **python** (len 115, sha c90af06c010b6a10...):

  ```
  {"\u001fÿ":357,"&😀 ":-138,"􏿿߿\"":-510," \u001f\u001f":314," ￿Ā&":384,"😀𐀀߿￿  ":-522}
  ```
- **go** (len 124, sha 53dafa3e45b6e8da...):

  ```
  {"\u001fÿ":357,"&😀\u2029":-138,"􏿿߿\"":-510,"\u2029\u001f\u001f":314,"\u2029￿Ā&":384,"😀𐀀߿￿  ":-522}
  ```
- **rust** (len 115, sha c90af06c010b6a10...):

  ```
  {"\u001fÿ":357,"&😀 ":-138,"􏿿߿\"":-510," \u001f\u001f":314," ￿Ā&":384,"😀𐀀߿￿  ":-522}
  ```
