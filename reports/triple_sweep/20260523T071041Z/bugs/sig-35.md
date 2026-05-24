# Disagreement signature 35

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-C1-control,contains-DEL,contains-U+2029`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-C1-control, contains-DEL, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 1

## Examples

### Example 1

- generator: `nested`
- input: `{"\u001f߿\u0000 ߿￿": {"\u0007  <Ā": 0.1, "tag": 0}, "tag": 6}`

Canonical per implementation:
- **python** (len 68, sha 4e7d4fa82d4c07aa...):

  ```
  {"\u001f߿\u0000 ߿￿":{"tag":0,"\u0007  <Ā":0.1},"tag":6}
  ```
- **go** (len 74, sha 21a92628be1292ee...):

  ```
  {"\u001f߿\u0000 ߿￿":{"tag":0,"\u0007\u2029\u2029<Ā":0.1},"tag":6}
  ```
- **rust** (len 68, sha 4e7d4fa82d4c07aa...):

  ```
  {"\u001f߿\u0000 ߿￿":{"tag":0,"\u0007  <Ā":0.1},"tag":6}
  ```
