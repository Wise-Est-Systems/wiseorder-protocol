# Disagreement signature 66

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-DEL,contains-U+2029`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-DEL, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 1

## Examples

### Example 1

- generator: `nested`
- input: `{"߿\\�\\": [[0.1, 0.2, "\u0000<ࠀ\u0000  ￿"], 0.3, "ࠀ Ā>\"\""], "tag": 2}`

Canonical per implementation:
- **python** (len 79, sha 25099814c0504a84...):

  ```
  {"tag":2,"߿\\�\\":[[0.1,0.2,"\u0000<ࠀ\u0000  ￿"],0.3,"ࠀ Ā>\"\""]}
  ```
- **go** (len 82, sha 615cf56fc616bd1d...):

  ```
  {"tag":2,"߿\\�\\":[[0.1,0.2,"\u0000<ࠀ\u0000\u2029 ￿"],0.3,"ࠀ Ā>\"\""]}
  ```
- **rust** (len 79, sha 25099814c0504a84...):

  ```
  {"tag":2,"߿\\�\\":[[0.1,0.2,"\u0000<ࠀ\u0000  ￿"],0.3,"ࠀ Ā>\"\""]}
  ```
