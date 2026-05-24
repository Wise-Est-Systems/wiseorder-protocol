# Disagreement signature 94

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-U+2028,contains-U+2029`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-U+2028, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - unicode_string: 1

## Examples

### Example 1

- generator: `unicode_string`
- input: `" ߿ ￿ \u0000"`

Canonical per implementation:
- **python** (len 22, sha e4e64eb407ba5f6b...):

  ```
  " ߿ ￿ \u0000"
  ```
- **go** (len 31, sha b5c98942de892026...):

  ```
  "\u2029߿\u2029￿\u2028\u0000"
  ```
- **rust** (len 22, sha e4e64eb407ba5f6b...):

  ```
  " ߿ ￿ \u0000"
  ```
