# Disagreement signature 22

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-U+2029`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - unicode_string: 1

## Examples

### Example 1

- generator: `unicode_string`
- input: `"&&/� <\u0000Ā"`

Canonical per implementation:
- **python** (len 20, sha 3d62ca50ba392b97...):

  ```
  "&&/� <\u0000Ā"
  ```
- **go** (len 23, sha 158c3caaa76c2c39...):

  ```
  "&&/�\u2029<\u0000Ā"
  ```
- **rust** (len 20, sha 3d62ca50ba392b97...):

  ```
  "&&/� <\u0000Ā"
  ```
