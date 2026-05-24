# Disagreement signature 69

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-U+2028,contains-bigint>2^53`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-U+2028, contains-bigint>2^53

**Length pattern:** longest:go,shortest:python

**By generator:**
  - array_order: 1

## Examples

### Example 1

- generator: `array_order`
- input: `[9007199254740993, -66, 70, "\u0007<<>&߿\\", "\u001fÿ �", -45]`

Canonical per implementation:
- **python** (len 63, sha b3749ec4c0940555...):

  ```
  [9007199254740993,-66,70,"\u0007<<>&߿\\","\u001fÿ �",-45]
  ```
- **go** (len 66, sha 81da037a9eb22f99...):

  ```
  [9007199254740993,-66,70,"\u0007<<>&߿\\","\u001fÿ\u2028�",-45]
  ```
- **rust** (len 63, sha b3749ec4c0940555...):

  ```
  [9007199254740993,-66,70,"\u0007<<>&߿\\","\u001fÿ �",-45]
  ```
