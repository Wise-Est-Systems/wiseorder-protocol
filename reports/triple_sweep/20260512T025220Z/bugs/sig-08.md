# Disagreement signature 8

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-C1-control,contains-DEL,contains-U+2029`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-C1-control, contains-DEL, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"\">�\\": 529, "\u0007ࠀ >ÿÿ": 633}`

Canonical per implementation:
- **python** (len 43, sha f5abe13b38091f4b...):

  ```
  {"\">�\\":529,"\u0007ࠀ >ÿÿ":633}
  ```
- **go** (len 46, sha e5f2b4bb831dd4fb...):

  ```
  {"\">�\\":529,"\u0007ࠀ\u2029>ÿÿ":633}
  ```
- **rust** (len 43, sha f5abe13b38091f4b...):

  ```
  {"\">�\\":529,"\u0007ࠀ >ÿÿ":633}
  ```
