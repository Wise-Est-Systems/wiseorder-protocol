# Disagreement signature 74

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C1-control,contains-U+2028`

**Count:** 6

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C1-control, contains-U+2028

**Length pattern:** longest:go,shortest:python

**By generator:**
  - unicode_string: 5
  - mixed_object: 1

## Examples

### Example 1

- generator: `unicode_string`
- input: `"\"\"\"￿ "`

Canonical per implementation:
- **python** (len 16, sha c2fb12a02ebdb6ed...):

  ```
  "\"\"\"￿ "
  ```
- **go** (len 19, sha 6e67b5ef62c9ea39...):

  ```
  "\"\"\"￿\u2028"
  ```
- **rust** (len 16, sha c2fb12a02ebdb6ed...):

  ```
  "\"\"\"￿ "
  ```

### Example 2

- generator: `unicode_string`
- input: `"Ā /\"￿"`

Canonical per implementation:
- **python** (len 15, sha ff4e8092cba616e4...):

  ```
  "Ā /\"￿"
  ```
- **go** (len 18, sha b1bf65f2862dac46...):

  ```
  "Ā\u2028/\"￿"
  ```
- **rust** (len 15, sha ff4e8092cba616e4...):

  ```
  "Ā /\"￿"
  ```

### Example 3

- generator: `unicode_string`
- input: `" ￿�"`

Canonical per implementation:
- **python** (len 13, sha 66c4444b0d01ab37...):

  ```
  " ￿�"
  ```
- **go** (len 16, sha b3dc5cbca0bb7d29...):

  ```
  "\u2028￿�"
  ```
- **rust** (len 13, sha 66c4444b0d01ab37...):

  ```
  " ￿�"
  ```
