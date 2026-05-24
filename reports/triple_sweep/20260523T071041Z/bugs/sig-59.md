# Disagreement signature 59

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-C1-control,contains-DEL,contains-U+2028,contains-bigint>2^53`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-C1-control, contains-DEL, contains-U+2028, contains-bigint>2^53

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 1

## Examples

### Example 1

- generator: `nested`
- input: `[[[-2.5, 0, "��ࠀ"], 2.2250738585072014e-308, "<\u0007"], 9223372036854775807, "<< ￿߿߿"]`

Canonical per implementation:
- **python** (len 96, sha 6600a0cbda9b196d...):

  ```
  [[[-2.5,0,"��ࠀ"],2.2250738585072014e-308,"<\u0007"],9223372036854775807,"<< ￿߿߿"]
  ```
- **go** (len 99, sha f9d0758dfae24d60...):

  ```
  [[[-2.5,0,"��ࠀ"],2.2250738585072014e-308,"<\u0007"],9223372036854775807,"<<\u2028￿߿߿"]
  ```
- **rust** (len 96, sha 6600a0cbda9b196d...):

  ```
  [[[-2.5,0,"��ࠀ"],2.2250738585072014e-308,"<\u0007"],9223372036854775807,"<< ￿߿߿"]
  ```
