# Disagreement signature 12

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-C1-control,contains-SMP,contains-U+2028,contains-U+2029`

**Count:** 3

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-C1-control, contains-SMP, contains-U+2028, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 2
  - nested: 1

## Examples

### Example 1

- generator: `nested`
- input: `{"𐀀\u0007&\\>": [{"ࠀ 𐀀": 0.0, "tag": 8}, -2.5, "ĀĀ /"], "tag": 6}`

Canonical per implementation:
- **python** (len 75, sha 86392e817d40886a...):

  ```
  {"tag":6,"𐀀\u0007&\\>":[{"tag":8,"ࠀ 𐀀":0.0},-2.5,"ĀĀ /"]}
  ```
- **go** (len 81, sha 54b943ad512fda85...):

  ```
  {"tag":6,"𐀀\u0007&\\>":[{"tag":8,"ࠀ\u2028𐀀":0.0},-2.5,"ĀĀ\u2029/"]}
  ```
- **rust** (len 75, sha 86392e817d40886a...):

  ```
  {"tag":6,"𐀀\u0007&\\>":[{"tag":8,"ࠀ 𐀀":0.0},-2.5,"ĀĀ /"]}
  ```

### Example 2

- generator: `object_unicode_keys`
- input: `{"<\u0007 ߿/&": -413, " Ā\u0000\\\u001f𐀀Ā": 929, " �\"\"\\� ": 642}`

Canonical per implementation:
- **python** (len 84, sha eca7e01c1b95850d...):

  ```
  {"<\u0007 ߿/&":-413," �\"\"\\� ":642," Ā\u0000\\\u001f𐀀Ā":929}
  ```
- **go** (len 96, sha 8e86871e54f513de...):

  ```
  {"<\u0007\u2029߿/&":-413,"\u2028�\"\"\\�\u2028":642,"\u2029Ā\u0000\\\u001f𐀀Ā":929}
  ```
- **rust** (len 84, sha eca7e01c1b95850d...):

  ```
  {"<\u0007 ߿/&":-413," �\"\"\\� ":642," Ā\u0000\\\u001f𐀀Ā":929}
  ```

### Example 3

- generator: `object_unicode_keys`
- input: `{" 􏿿\\\\": -287, "𐀀𐀀�𐀀􏿿\\􏿿 ": -956, "𐀀\u0000": 882, "ÿ &": 796, "<ÿࠀ 􏿿􏿿": -421, "߿ <𐀀": 636}`

Canonical per implementation:
- **python** (len 126, sha 7599b00e1ade80f0...):

  ```
  {" 􏿿\\\\":-287,"<ÿࠀ 􏿿􏿿":-421,"ÿ &":796,"߿ <𐀀":636,"𐀀\u0000":882,"𐀀𐀀�𐀀􏿿\\􏿿 ":-956}
  ```
- **go** (len 135, sha 4c76a5f4ee172df4...):

  ```
  {" 􏿿\\\\":-287,"<ÿࠀ\u2028􏿿􏿿":-421,"ÿ\u2029&":796,"߿ <𐀀":636,"𐀀\u0000":882,"𐀀𐀀�𐀀􏿿\\􏿿\u2028":-956}
  ```
- **rust** (len 126, sha 7599b00e1ade80f0...):

  ```
  {" 􏿿\\\\":-287,"<ÿࠀ 􏿿􏿿":-421,"ÿ &":796,"߿ <𐀀":636,"𐀀\u0000":882,"𐀀𐀀�𐀀􏿿\\􏿿 ":-956}
  ```
