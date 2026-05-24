# Disagreement signature 25

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C1-control,contains-U+2028`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C1-control, contains-U+2028

**Length pattern:** longest:go,shortest:python

**By generator:**
  - unicode_string: 1

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
