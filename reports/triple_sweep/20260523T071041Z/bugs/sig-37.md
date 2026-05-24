# Disagreement signature 37

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-SMP,contains-U+2028,contains-U+2029`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-SMP, contains-U+2028, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"𐀀< ": 206, "\\": -948, "  ": 117, " ": 937}`

Canonical per implementation:
- **python** (len 49, sha 49f7adc6b8aa41d9...):

  ```
  {"\\":-948,"  ":117," ":937,"𐀀< ":206}
  ```
- **go** (len 61, sha 96b6777c51fd2d49...):

  ```
  {"\\":-948,"\u2028\u2028":117,"\u2029":937,"𐀀<\u2028":206}
  ```
- **rust** (len 49, sha 49f7adc6b8aa41d9...):

  ```
  {"\\":-948,"  ":117," ":937,"𐀀< ":206}
  ```
