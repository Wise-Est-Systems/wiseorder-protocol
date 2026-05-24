# Disagreement signature 81

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-C1-control,contains-DEL,contains-SMP,contains-U+2028,contains-U+2029,contains-bigint>2^53`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-C1-control, contains-DEL, contains-SMP, contains-U+2028, contains-U+2029, contains-bigint>2^53

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 1

## Examples

### Example 1

- generator: `nested`
- input: `[[[[1000000000000000.0, -9223372036854775808, ">ࠀ ߿"], 0.1, " ࠀ>� ÿ"], 3.141592653589793, "ÿ/"], 0.0, "&\u001f￿𐀀"]`

Canonical per implementation:
- **python** (len 129, sha 523eca3d2eceb00d...):

  ```
  [[[[1000000000000000.0,-9223372036854775808,">ࠀ ߿"],0.1," ࠀ>� ÿ"],3.141592653589793,"ÿ/"],0.0,"&\u001f￿𐀀"]
  ```
- **go** (len 138, sha ec3258719f4606f8...):

  ```
  [[[[1000000000000000.0,-9223372036854775808,">ࠀ\u2028߿"],0.1,"\u2029ࠀ>�\u2029ÿ"],3.141592653589793,"ÿ/"],0.0,"&\u001f￿𐀀"]
  ```
- **rust** (len 129, sha 523eca3d2eceb00d...):

  ```
  [[[[1000000000000000.0,-9223372036854775808,">ࠀ ߿"],0.1," ࠀ>� ÿ"],3.141592653589793,"ÿ/"],0.0,"&\u001f￿𐀀"]
  ```
