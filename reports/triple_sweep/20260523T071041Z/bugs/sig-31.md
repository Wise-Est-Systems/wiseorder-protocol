# Disagreement signature 31

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C1-control,contains-U+2029`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C1-control, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 1

## Examples

### Example 1

- generator: `nested`
- input: `[[10000000000.0, 10000000000.0, "< "], 0.1, ""]`

Canonical per implementation:
- **python** (len 47, sha 2e2e2ef9390ac1e6...):

  ```
  [[10000000000.0,10000000000.0,"< "],0.1,""]
  ```
- **go** (len 50, sha bc1e6ee3a4dffba0...):

  ```
  [[10000000000.0,10000000000.0,"<\u2029"],0.1,""]
  ```
- **rust** (len 47, sha 2e2e2ef9390ac1e6...):

  ```
  [[10000000000.0,10000000000.0,"< "],0.1,""]
  ```
