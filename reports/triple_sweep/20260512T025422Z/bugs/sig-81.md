# Disagreement signature 81

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-U+2028,contains-U+2029`

**Count:** 6

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-U+2028, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - unicode_string: 4
  - array_order: 2

## Examples

### Example 1

- generator: `unicode_string`
- input: `"> <&> "`

Canonical per implementation:
- **python** (len 12, sha 1a2a6aeefe5dca32...):

  ```
  "> <&> "
  ```
- **go** (len 18, sha e8b31460e879a062...):

  ```
  ">\u2028<&>\u2029"
  ```
- **rust** (len 12, sha 1a2a6aeefe5dca32...):

  ```
  "> <&> "
  ```

### Example 2

- generator: `unicode_string`
- input: `"  ࠀ < "`

Canonical per implementation:
- **python** (len 18, sha d8b76390a1166d53...):

  ```
  "  ࠀ < "
  ```
- **go** (len 30, sha 756b162164441ff6...):

  ```
  "\u2028\u2029ࠀ\u2029<\u2028"
  ```
- **rust** (len 18, sha d8b76390a1166d53...):

  ```
  "  ࠀ < "
  ```

### Example 3

- generator: `unicode_string`
- input: `"￿Ā  ߿"`

Canonical per implementation:
- **python** (len 15, sha 8e88e5567b0167a8...):

  ```
  "￿Ā  ߿"
  ```
- **go** (len 21, sha 62f5f8a4d61ca06b...):

  ```
  "￿Ā\u2029\u2028߿"
  ```
- **rust** (len 15, sha 8e88e5567b0167a8...):

  ```
  "￿Ā  ߿"
  ```
