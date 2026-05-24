# Disagreement signature 20

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-DEL,contains-SMP,contains-U+2028,contains-emoji`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-DEL, contains-SMP, contains-U+2028, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"Ā￿<": -370, "> 􏿿": 797, "Ā": -147, "&ࠀ￿": 206, "Ā &ÿ😀": -153, "￿􏿿 > 􏿿": 879}`

Canonical per implementation:
- **python** (len 94, sha a3366a9994fb1b70...):

  ```
  {"&ࠀ￿":206,"> 􏿿":797,"Ā":-147,"Ā &ÿ😀":-153,"Ā￿<":-370,"￿􏿿 > 􏿿":879}
  ```
- **go** (len 97, sha c39901ad88332017...):

  ```
  {"&ࠀ￿":206,"> 􏿿":797,"Ā":-147,"Ā\u2028&ÿ😀":-153,"Ā￿<":-370,"￿􏿿 > 􏿿":879}
  ```
- **rust** (len 94, sha a3366a9994fb1b70...):

  ```
  {"&ࠀ￿":206,"> 􏿿":797,"Ā":-147,"Ā &ÿ😀":-153,"Ā￿<":-370,"￿􏿿 > 􏿿":879}
  ```
