# Disagreement signature 23

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-DEL,contains-SMP,contains-U+2028,contains-U+2029,contains-emoji`

**Count:** 14

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-DEL, contains-SMP, contains-U+2028, contains-U+2029, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 7
  - nested: 6
  - array_order: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"߿􏿿  / ": 376, "\\\"😀\\\u0007 ￿": 634}`

Canonical per implementation:
- **python** (len 54, sha 9f2794e04b134451...):

  ```
  {"\\\"😀\\\u0007 ￿":634,"߿􏿿  / ":376}
  ```
- **go** (len 63, sha 542a70105f872ad5...):

  ```
  {"\\\"😀\\\u0007\u2028￿":634,"߿􏿿\u2028\u2029/ ":376}
  ```
- **rust** (len 54, sha 9f2794e04b134451...):

  ```
  {"\\\"😀\\\u0007 ￿":634,"߿􏿿  / ":376}
  ```

### Example 2

- generator: `object_unicode_keys`
- input: `{"😀􏿿😀Ā": 566, "ÿ >>>𐀀": -205, "ࠀ/<>𐀀𐀀�": 173, "𐀀􏿿 ￿\u001f ": 416}`

Canonical per implementation:
- **python** (len 98, sha d63212759ffaca99...):

  ```
  {"ÿ >>>𐀀":-205,"ࠀ/<>𐀀𐀀�":173,"𐀀􏿿 ￿\u001f ":416,"😀􏿿😀Ā":566}
  ```
- **go** (len 107, sha 83c02554d0799e1d...):

  ```
  {"ÿ\u2028>>>𐀀":-205,"ࠀ/<>𐀀𐀀�":173,"𐀀􏿿\u2028￿\u001f\u2029":416,"😀􏿿😀Ā":566}
  ```
- **rust** (len 98, sha d63212759ffaca99...):

  ```
  {"ÿ >>>𐀀":-205,"ࠀ/<>𐀀𐀀�":173,"𐀀􏿿 ￿\u001f ":416,"😀􏿿😀Ā":566}
  ```

### Example 3

- generator: `object_unicode_keys`
- input: `{" &𐀀": 123, "ࠀ�𐀀ÿÿ😀": -67, "￿ ࠀ😀 \u0000/": 924}`

Canonical per implementation:
- **python** (len 72, sha 6e6d13535f5211f0...):

  ```
  {"ࠀ�𐀀ÿÿ😀":-67," &𐀀":123,"￿ ࠀ😀 \u0000/":924}
  ```
- **go** (len 81, sha bc3da8c67a64207f...):

  ```
  {"ࠀ�𐀀ÿÿ😀":-67,"\u2029&𐀀":123,"￿\u2029ࠀ😀\u2028\u0000/":924}
  ```
- **rust** (len 72, sha 6e6d13535f5211f0...):

  ```
  {"ࠀ�𐀀ÿÿ😀":-67," &𐀀":123,"￿ ࠀ😀 \u0000/":924}
  ```
