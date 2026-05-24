# Disagreement signature 63

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-SMP,contains-U+2028,contains-emoji`

**Count:** 8

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-SMP, contains-U+2028, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 5
  - nested: 2
  - unicode_string: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{" \u0007𐀀//􏿿\"": -651, "\u0000Ā😀�": 853, "𐀀\"<𐀀": 723, "ࠀ߿": 345}`

Canonical per implementation:
- **python** (len 82, sha c21b97724fa03312...):

  ```
  {"\u0000Ā😀�":853,"ࠀ߿":345," \u0007𐀀//􏿿\"":-651,"𐀀\"<𐀀":723}
  ```
- **go** (len 85, sha ac973c241f1b2ac4...):

  ```
  {"\u0000Ā😀�":853,"ࠀ߿":345,"\u2028\u0007𐀀//􏿿\"":-651,"𐀀\"<𐀀":723}
  ```
- **rust** (len 82, sha c21b97724fa03312...):

  ```
  {"\u0000Ā😀�":853,"ࠀ߿":345," \u0007𐀀//􏿿\"":-651,"𐀀\"<𐀀":723}
  ```

### Example 2

- generator: `object_unicode_keys`
- input: `{"ࠀ􏿿􏿿 &\"\u001fÿ": -362, "ࠀࠀ\\": -163, "😀 Ā\u0000\\ ": -494, "�􏿿߿\u0000": 521}`

Canonical per implementation:
- **python** (len 96, sha 9a4e0592126a51a8...):

  ```
  {"ࠀࠀ\\":-163,"ࠀ􏿿􏿿 &\"\u001fÿ":-362,"�􏿿߿\u0000":521,"😀 Ā\u0000\\ ":-494}
  ```
- **go** (len 99, sha dffc4abbc1d1ce45...):

  ```
  {"ࠀࠀ\\":-163,"ࠀ􏿿􏿿 &\"\u001fÿ":-362,"�􏿿߿\u0000":521,"😀 Ā\u0000\\\u2028":-494}
  ```
- **rust** (len 96, sha 9a4e0592126a51a8...):

  ```
  {"ࠀࠀ\\":-163,"ࠀ􏿿􏿿 &\"\u001fÿ":-362,"�􏿿߿\u0000":521,"😀 Ā\u0000\\ ":-494}
  ```

### Example 3

- generator: `nested`
- input: `[{"<": {"�\\/& ": {"􏿿\"\u001f😀": 0.0, "tag": 0}, "tag": 9}, "tag": 5}, -1, "�"]`

Canonical per implementation:
- **python** (len 80, sha f6c4b445cc30f210...):

  ```
  [{"<":{"tag":9,"�\\/& ":{"tag":0,"􏿿\"\u001f😀":0.0}},"tag":5},-1,"�"]
  ```
- **go** (len 83, sha 50db1275a1ef85e9...):

  ```
  [{"<":{"tag":9,"�\\/&\u2028":{"tag":0,"􏿿\"\u001f😀":0.0}},"tag":5},-1,"�"]
  ```
- **rust** (len 80, sha f6c4b445cc30f210...):

  ```
  [{"<":{"tag":9,"�\\/& ":{"tag":0,"􏿿\"\u001f😀":0.0}},"tag":5},-1,"�"]
  ```
