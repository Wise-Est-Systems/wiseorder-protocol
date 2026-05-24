# Disagreement signature 99

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-DEL,contains-SMP,contains-U+2028,contains-emoji`

**Count:** 4

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-DEL, contains-SMP, contains-U+2028, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 2
  - nested: 1
  - unicode_string: 1

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

### Example 2

- generator: `nested`
- input: `[{"􏿿😀ÿ߿\"": {" <�ࠀ￿ ": 0, "tag": 0}, "tag": 4}, 3.14159, "Ā&\"ÿ\\"]`

Canonical per implementation:
- **python** (len 81, sha 4f65de60ca436a8e...):

  ```
  [{"tag":4,"􏿿😀ÿ߿\"":{"tag":0," <�ࠀ￿ ":0}},3.14159,"Ā&\"ÿ\\"]
  ```
- **go** (len 87, sha b1ce0432ef00daf9...):

  ```
  [{"tag":4,"􏿿😀ÿ߿\"":{"tag":0,"\u2028<�ࠀ￿\u2028":0}},3.14159,"Ā&\"ÿ\\"]
  ```
- **rust** (len 81, sha 4f65de60ca436a8e...):

  ```
  [{"tag":4,"􏿿😀ÿ߿\"":{"tag":0," <�ࠀ￿ ":0}},3.14159,"Ā&\"ÿ\\"]
  ```

### Example 3

- generator: `object_unicode_keys`
- input: `{"�￿": -51, "😀": -109, "􏿿😀> ": -290, "ÿ\\": 914, " ￿": 867}`

Canonical per implementation:
- **python** (len 69, sha 30d7869c792f207d...):

  ```
  {"ÿ\\":914," ￿":867,"�￿":-51,"😀":-109,"􏿿😀> ":-290}
  ```
- **go** (len 72, sha ad1a08052c5dd2d9...):

  ```
  {"ÿ\\":914,"\u2028￿":867,"�￿":-51,"😀":-109,"􏿿😀> ":-290}
  ```
- **rust** (len 69, sha 30d7869c792f207d...):

  ```
  {"ÿ\\":914," ￿":867,"�￿":-51,"😀":-109,"􏿿😀> ":-290}
  ```
