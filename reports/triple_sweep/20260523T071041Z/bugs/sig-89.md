# Disagreement signature 89

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C1-control,contains-DEL,contains-SMP,contains-U+2028,contains-emoji`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C1-control, contains-DEL, contains-SMP, contains-U+2028, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"ÿ𐀀𐀀": 535, "// 􏿿ÿ�ࠀ": 489, " Ā\\ ÿ😀": 525, "\"\"􏿿\\": -552, "\\": -863, "ࠀ/<߿Ā": 745}`

Canonical per implementation:
- **python** (len 108, sha cf151ade6148064f...):

  ```
  {"\"\"􏿿\\":-552,"// 􏿿ÿ�ࠀ":489,"\\":-863,"ÿ𐀀𐀀":535,"ࠀ/<߿Ā":745," Ā\\ ÿ😀":525}
  ```
- **go** (len 111, sha 8c194fc59d3f6361...):

  ```
  {"\"\"􏿿\\":-552,"// 􏿿ÿ�ࠀ":489,"\\":-863,"ÿ𐀀𐀀":535,"ࠀ/<߿Ā":745,"\u2028Ā\\ ÿ😀":525}
  ```
- **rust** (len 108, sha cf151ade6148064f...):

  ```
  {"\"\"􏿿\\":-552,"// 􏿿ÿ�ࠀ":489,"\\":-863,"ÿ𐀀𐀀":535,"ࠀ/<߿Ā":745," Ā\\ ÿ😀":525}
  ```
