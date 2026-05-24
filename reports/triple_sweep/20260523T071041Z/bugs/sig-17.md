# Disagreement signature 17

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-SMP,contains-U+2029,contains-emoji`

**Count:** 2

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-SMP, contains-U+2029, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - array_order: 1
  - unicode_string: 1

## Examples

### Example 1

- generator: `array_order`
- input: `["\"� <", ">\u0000😀😀 􏿿\u001f"]`

Canonical per implementation:
- **python** (len 42, sha 516e9a4287c6f399...):

  ```
  ["\"� <",">\u0000😀😀 􏿿\u001f"]
  ```
- **go** (len 45, sha f7c6f58bd1901505...):

  ```
  ["\"� <",">\u0000😀😀\u2029􏿿\u001f"]
  ```
- **rust** (len 42, sha 516e9a4287c6f399...):

  ```
  ["\"� <",">\u0000😀😀 􏿿\u001f"]
  ```

### Example 2

- generator: `unicode_string`
- input: `"\u0000𐀀\\ >😀"`

Canonical per implementation:
- **python** (len 22, sha ac77690a843f7c9d...):

  ```
  "\u0000𐀀\\ >😀"
  ```
- **go** (len 25, sha 4b51c070c4d3a901...):

  ```
  "\u0000𐀀\\\u2029>😀"
  ```
- **rust** (len 22, sha ac77690a843f7c9d...):

  ```
  "\u0000𐀀\\ >😀"
  ```
