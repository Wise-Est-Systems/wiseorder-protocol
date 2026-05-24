# Disagreement signature 86

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-DEL,contains-U+2028,contains-U+2029`

**Count:** 5

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-DEL, contains-U+2028, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - array_order: 2
  - nested: 2
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

### Example 2

- generator: `array_order`
- input: `["\u0000 ", 1, 58, " \u0007/ÿ "]`

Canonical per implementation:
- **python** (len 37, sha 356ef2f1e5b93067...):

  ```
  ["\u0000 ",1,58," \u0007/ÿ "]
  ```
- **go** (len 46, sha a6a88e78b18e7ee2...):

  ```
  ["\u0000\u2029",1,58,"\u2028\u0007/ÿ\u2028"]
  ```
- **rust** (len 37, sha 356ef2f1e5b93067...):

  ```
  ["\u0000 ",1,58," \u0007/ÿ "]
  ```

### Example 3

- generator: `nested`
- input: `{"ÿ": {"\"&￿\\ࠀ": {"\\ÿ  <￿": [3.141592653589793, 10000000000.0, "\u0007 "], "tag": 5}, "tag": 7}, "tag": 3}`

Canonical per implementation:
- **python** (len 112, sha b4fc779a67362f3d...):

  ```
  {"tag":3,"ÿ":{"\"&￿\\ࠀ":{"\\ÿ  <￿":[3.141592653589793,10000000000.0,"\u0007 "],"tag":5},"tag":7}}
  ```
- **go** (len 121, sha acdd78401e22f66c...):

  ```
  {"tag":3,"ÿ":{"\"&￿\\ࠀ":{"\\ÿ\u2029\u2029<￿":[3.141592653589793,10000000000.0,"\u0007\u2028"],"tag":5},"tag":7}}
  ```
- **rust** (len 112, sha b4fc779a67362f3d...):

  ```
  {"tag":3,"ÿ":{"\"&￿\\ࠀ":{"\\ÿ  <￿":[3.141592653589793,10000000000.0,"\u0007 "],"tag":5},"tag":7}}
  ```
