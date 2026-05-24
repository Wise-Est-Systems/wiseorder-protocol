# Disagreement signature 88

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-C1-control,contains-DEL,contains-U+2028`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-C1-control, contains-DEL, contains-U+2028

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 1

## Examples

### Example 1

- generator: `nested`
- input: `{"</": {"�Ā\u001f": [[0, 2.2250738585072014e-308, "\""], 5e-324, "ÿ \u0000\\￿"], "tag": 9}, "tag": 4}`

Canonical per implementation:
- **python** (len 104, sha 805e0febd7201a58...):

  ```
  {"tag":4,"</":{"tag":9,"�Ā\u001f":[[0,2.2250738585072014e-308,"\""],5e-324,"ÿ \u0000\\￿"]}}
  ```
- **go** (len 107, sha 2af474ee5a118792...):

  ```
  {"tag":4,"</":{"tag":9,"�Ā\u001f":[[0,2.2250738585072014e-308,"\""],5e-324,"ÿ\u2028\u0000\\￿"]}}
  ```
- **rust** (len 104, sha 805e0febd7201a58...):

  ```
  {"tag":4,"</":{"tag":9,"�Ā\u001f":[[0,2.2250738585072014e-308,"\""],5e-324,"ÿ \u0000\\￿"]}}
  ```
