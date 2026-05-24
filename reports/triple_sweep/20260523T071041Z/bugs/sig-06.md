# Disagreement signature 6

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-U+2029`

**Count:** 4

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - unicode_string: 2
  - array_order: 1
  - mixed_object: 1

## Examples

### Example 1

- generator: `unicode_string`
- input: `"& "`

Canonical per implementation:
- **python** (len 6, sha 2326f306ff966940...):

  ```
  "& "
  ```
- **go** (len 9, sha a98d7bef7cc5d610...):

  ```
  "&\u2029"
  ```
- **rust** (len 6, sha 2326f306ff966940...):

  ```
  "& "
  ```

### Example 2

- generator: `unicode_string`
- input: `" ߿"`

Canonical per implementation:
- **python** (len 7, sha 97ddd14ee060817a...):

  ```
  " ߿"
  ```
- **go** (len 10, sha 5076503c394efb11...):

  ```
  "\u2029߿"
  ```
- **rust** (len 7, sha 97ddd14ee060817a...):

  ```
  " ߿"
  ```

### Example 3

- generator: `array_order`
- input: `[64, -59, " ", 2.718281828459045]`

Canonical per implementation:
- **python** (len 32, sha 49d46eba26748dd0...):

  ```
  [64,-59," ",2.718281828459045]
  ```
- **go** (len 35, sha bb8c61c536ab3904...):

  ```
  [64,-59,"\u2029",2.718281828459045]
  ```
- **rust** (len 32, sha 49d46eba26748dd0...):

  ```
  [64,-59," ",2.718281828459045]
  ```
