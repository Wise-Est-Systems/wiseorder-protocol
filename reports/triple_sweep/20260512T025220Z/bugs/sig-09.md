# Disagreement signature 9

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-U+2028,contains-emoji`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-U+2028, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - array_order: 1

## Examples

### Example 1

- generator: `array_order`
- input: `[10000000000.0, 0.3, 1e-100, ">< \u001f😀"]`

Canonical per implementation:
- **python** (len 44, sha c6f52ee1c9146783...):

  ```
  [10000000000.0,0.3,1e-100,">< \u001f😀"]
  ```
- **go** (len 47, sha 26046ee1ede29715...):

  ```
  [10000000000.0,0.3,1e-100,"><\u2028\u001f😀"]
  ```
- **rust** (len 44, sha c6f52ee1c9146783...):

  ```
  [10000000000.0,0.3,1e-100,">< \u001f😀"]
  ```
