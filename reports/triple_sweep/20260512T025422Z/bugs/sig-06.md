# Disagreement signature 6

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-SMP,contains-U+2029`

**Count:** 24

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-SMP, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - unicode_string: 10
  - object_unicode_keys: 5
  - array_order: 4
  - mixed_object: 4
  - nested: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"􏿿": -293, " \u0007￿\u0007": -71, "\u0000\u001f￿\u0007\u0000ࠀ": -500}`

Canonical per implementation:
- **python** (len 76, sha dad27c1fc74572b8...):

  ```
  {"\u0000\u001f￿\u0007\u0000ࠀ":-500," \u0007￿\u0007":-71,"􏿿":-293}
  ```
- **go** (len 79, sha fbd7b006bc4ab30d...):

  ```
  {"\u0000\u001f￿\u0007\u0000ࠀ":-500,"\u2029\u0007￿\u0007":-71,"􏿿":-293}
  ```
- **rust** (len 76, sha dad27c1fc74572b8...):

  ```
  {"\u0000\u001f￿\u0007\u0000ࠀ":-500," \u0007￿\u0007":-71,"􏿿":-293}
  ```

### Example 2

- generator: `object_unicode_keys`
- input: `{"<<􏿿&￿�􏿿\u001f": -546, " \u0007\u0007�￿􏿿\\􏿿": -940}`

Canonical per implementation:
- **python** (len 71, sha 26c78a7c90600eb4...):

  ```
  {"<<􏿿&￿�􏿿\u001f":-546," \u0007\u0007�￿􏿿\\􏿿":-940}
  ```
- **go** (len 74, sha a33eafe0afb5041f...):

  ```
  {"<<􏿿&￿�􏿿\u001f":-546,"\u2029\u0007\u0007�￿􏿿\\􏿿":-940}
  ```
- **rust** (len 71, sha 26c78a7c90600eb4...):

  ```
  {"<<􏿿&￿�􏿿\u001f":-546," \u0007\u0007�￿􏿿\\􏿿":-940}
  ```

### Example 3

- generator: `unicode_string`
- input: `"􏿿 \u0000𐀀ࠀ&𐀀>"`

Canonical per implementation:
- **python** (len 28, sha de3596aa9b8b12b1...):

  ```
  "􏿿 \u0000𐀀ࠀ&𐀀>"
  ```
- **go** (len 31, sha e392c65d7ed2c730...):

  ```
  "􏿿\u2029\u0000𐀀ࠀ&𐀀>"
  ```
- **rust** (len 28, sha de3596aa9b8b12b1...):

  ```
  "􏿿 \u0000𐀀ࠀ&𐀀>"
  ```
