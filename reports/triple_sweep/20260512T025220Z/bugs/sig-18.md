# Disagreement signature 18

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-SMP,contains-U+2028,contains-emoji`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-SMP, contains-U+2028, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 1

## Examples

### Example 1

- generator: `nested`
- input: `[{"􏿿": 2.718281828459045, "tag": 9}, 3.14159, "< 😀ࠀ\\"]`

Canonical per implementation:
- **python** (len 60, sha 54b2be842607e3cb...):

  ```
  [{"tag":9,"􏿿":2.718281828459045},3.14159,"< 😀ࠀ\\"]
  ```
- **go** (len 63, sha c541478e873cc0ad...):

  ```
  [{"tag":9,"􏿿":2.718281828459045},3.14159,"<\u2028😀ࠀ\\"]
  ```
- **rust** (len 60, sha 54b2be842607e3cb...):

  ```
  [{"tag":9,"􏿿":2.718281828459045},3.14159,"< 😀ࠀ\\"]
  ```
