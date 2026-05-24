# Disagreement signature 74

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-SMP,contains-U+2028`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-SMP, contains-U+2028

**Length pattern:** longest:go,shortest:python

**By generator:**
  - array_order: 1

## Examples

### Example 1

- generator: `array_order`
- input: `[3.14159, -2.5, "ࠀ􏿿/Ā ࠀࠀ ", "\\/ࠀ", 25]`

Canonical per implementation:
- **python** (len 49, sha f7f54e67dc468db3...):

  ```
  [3.14159,-2.5,"ࠀ􏿿/Ā ࠀࠀ ","\\/ࠀ",25]
  ```
- **go** (len 52, sha 8e516df90cc5ce60...):

  ```
  [3.14159,-2.5,"ࠀ􏿿/Ā ࠀࠀ\u2028","\\/ࠀ",25]
  ```
- **rust** (len 49, sha f7f54e67dc468db3...):

  ```
  [3.14159,-2.5,"ࠀ􏿿/Ā ࠀࠀ ","\\/ࠀ",25]
  ```
