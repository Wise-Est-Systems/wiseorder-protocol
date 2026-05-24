# Disagreement signature 19

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-C1-control,contains-DEL,contains-SMP,contains-U+2029,contains-emoji`

**Count:** 2

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-C1-control, contains-DEL, contains-SMP, contains-U+2029, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 1
  - array_order: 1

## Examples

### Example 1

- generator: `nested`
- input: `{"\u0007/ࠀ/ ": [2147483647, 2.2250738585072014e-308, "􏿿😀￿�😀 "], "tag": 2}`

Canonical per implementation:
- **python** (len 88, sha 70d60065ed6fa8e4...):

  ```
  {"\u0007/ࠀ/ ":[2147483647,2.2250738585072014e-308,"􏿿😀￿�😀 "],"tag":2}
  ```
- **go** (len 91, sha 0388cbbaea93ce9d...):

  ```
  {"\u0007/ࠀ/\u2029":[2147483647,2.2250738585072014e-308,"􏿿😀￿�😀 "],"tag":2}
  ```
- **rust** (len 88, sha 70d60065ed6fa8e4...):

  ```
  {"\u0007/ࠀ/ ":[2147483647,2.2250738585072014e-308,"􏿿😀￿�😀 "],"tag":2}
  ```

### Example 2

- generator: `array_order`
- input: `["😀􏿿�>\u0007𐀀", "Ā 😀", 7]`

Canonical per implementation:
- **python** (len 47, sha 24e6d836b9a1dc50...):

  ```
  ["😀􏿿�>\u0007𐀀","Ā 😀",7]
  ```
- **go** (len 50, sha fbf5ef501fa1092a...):

  ```
  ["😀􏿿�>\u0007𐀀","Ā\u2029😀",7]
  ```
- **rust** (len 47, sha 24e6d836b9a1dc50...):

  ```
  ["😀􏿿�>\u0007𐀀","Ā 😀",7]
  ```
