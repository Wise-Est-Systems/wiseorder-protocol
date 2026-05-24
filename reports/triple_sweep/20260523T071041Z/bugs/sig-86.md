# Disagreement signature 86

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-C1-control,contains-U+2028,contains-U+2029`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-C1-control, contains-U+2028, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - unicode_string: 1

## Examples

### Example 1

- generator: `unicode_string`
- input: `"Ā\u001f <  "`

Canonical per implementation:
- **python** (len 20, sha ca156d0d3b82d433...):

  ```
  "Ā\u001f <  "
  ```
- **go** (len 26, sha 95c828c0fbe1f087...):

  ```
  "Ā\u001f\u2028< \u2029"
  ```
- **rust** (len 20, sha ca156d0d3b82d433...):

  ```
  "Ā\u001f <  "
  ```
