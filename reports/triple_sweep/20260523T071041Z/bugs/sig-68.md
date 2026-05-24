# Disagreement signature 68

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-C1-control,contains-U+2029`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-C1-control, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - unicode_string: 1

## Examples

### Example 1

- generator: `unicode_string`
- input: `"Ā߿/ \u001f"`

Canonical per implementation:
- **python** (len 18, sha 08afcb7cc678b3ee...):

  ```
  "Ā߿/ \u001f"
  ```
- **go** (len 21, sha 12ea6ed640607f28...):

  ```
  "Ā߿/\u2029\u001f"
  ```
- **rust** (len 18, sha 08afcb7cc678b3ee...):

  ```
  "Ā߿/ \u001f"
  ```
