# Disagreement signature 7

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-DEL,contains-U+2028,contains-U+2029`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-DEL, contains-U+2028, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - unicode_string: 1

## Examples

### Example 1

- generator: `unicode_string`
- input: `"\u0007 > \"\u001f"`

Canonical per implementation:
- **python** (len 24, sha 22d8b0f023f98a64...):

  ```
  "\u0007 > \"\u001f"
  ```
- **go** (len 30, sha cbf1b68a650768f0...):

  ```
  "\u0007\u2029>\u2028\"\u001f"
  ```
- **rust** (len 24, sha 22d8b0f023f98a64...):

  ```
  "\u0007 > \"\u001f"
  ```
