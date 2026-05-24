# Disagreement signature 16

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-C1-control,contains-SMP,contains-U+2028,contains-U+2029,contains-emoji`

**Count:** 2

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-C1-control, contains-SMP, contains-U+2028, contains-U+2029, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 2

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"￿\"": 93, " < ": 286, "𐀀<😀 ": 390, "߿\u0000": -886, " ": 257}`

Canonical per implementation:
- **python** (len 69, sha 5638527941645771...):

  ```
  {" < ":286,"߿\u0000":-886," ":257,"￿\"":93,"𐀀<😀 ":390}
  ```
- **go** (len 75, sha 8cca6dd4028b1c93...):

  ```
  {" <\u2028":286,"߿\u0000":-886,"\u2029":257,"￿\"":93,"𐀀<😀 ":390}
  ```
- **rust** (len 69, sha 5638527941645771...):

  ```
  {" < ":286,"߿\u0000":-886," ":257,"￿\"":93,"𐀀<😀 ":390}
  ```

### Example 2

- generator: `object_unicode_keys`
- input: `{"ࠀ&": -343, "&😀 Ā\"": 261, " /\"�𐀀<": -471, "𐀀\\\u0007 \"&": 998, "\u0000>": -685}`

Canonical per implementation:
- **python** (len 96, sha 03701d85a0e531ef...):

  ```
  {"\u0000>":-685,"&😀 Ā\"":261,"ࠀ&":-343," /\"�𐀀<":-471,"𐀀\\\u0007 \"&":998}
  ```
- **go** (len 105, sha 4f443b1ad55b62e1...):

  ```
  {"\u0000>":-685,"&😀\u2028Ā\"":261,"ࠀ&":-343,"\u2028/\"�𐀀<":-471,"𐀀\\\u0007\u2029\"&":998}
  ```
- **rust** (len 96, sha 03701d85a0e531ef...):

  ```
  {"\u0000>":-685,"&😀 Ā\"":261,"ࠀ&":-343," /\"�𐀀<":-471,"𐀀\\\u0007 \"&":998}
  ```
