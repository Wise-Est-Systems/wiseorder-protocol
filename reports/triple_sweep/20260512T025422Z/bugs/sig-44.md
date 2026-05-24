# Disagreement signature 44

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-SMP,contains-U+2029,contains-emoji`

**Count:** 11

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-SMP, contains-U+2029, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 5
  - array_order: 3
  - object_unicode_keys: 3

## Examples

### Example 1

- generator: `array_order`
- input: `[-60, "߿Ā/Ā😀ÿ", 47, 5e-324, 1.7976931348623157e+308, 34, "ࠀ𐀀&ÿ\u001f߿𐀀", "ÿࠀ😀  \u001f>"]`

Canonical per implementation:
- **python** (len 106, sha d8dfc5d63b7e9bca...):

  ```
  [-60,"߿Ā/Ā😀ÿ",47,5e-324,1.7976931348623157e+308,34,"ࠀ𐀀&ÿ\u001f߿𐀀","ÿࠀ😀  \u001f>"]
  ```
- **go** (len 109, sha 4d213aeefa8962a9...):

  ```
  [-60,"߿Ā/Ā😀ÿ",47,5e-324,1.7976931348623157e+308,34,"ࠀ𐀀&ÿ\u001f߿𐀀","ÿࠀ😀\u2029 \u001f>"]
  ```
- **rust** (len 106, sha d8dfc5d63b7e9bca...):

  ```
  [-60,"߿Ā/Ā😀ÿ",47,5e-324,1.7976931348623157e+308,34,"ࠀ𐀀&ÿ\u001f߿𐀀","ÿࠀ😀  \u001f>"]
  ```

### Example 2

- generator: `object_unicode_keys`
- input: `{" Ā\\\u0000􏿿&": -275, "\u001f/ 😀\u0007 ࠀ ": -637, "߿ÿ>": 100}`

Canonical per implementation:
- **python** (len 72, sha be198289de9927eb...):

  ```
  {"\u001f/ 😀\u0007 ࠀ ":-637,"߿ÿ>":100," Ā\\\u0000􏿿&":-275}
  ```
- **go** (len 78, sha 3f6a142f64609698...):

  ```
  {"\u001f/ 😀\u0007\u2029ࠀ ":-637,"߿ÿ>":100,"\u2029Ā\\\u0000􏿿&":-275}
  ```
- **rust** (len 72, sha be198289de9927eb...):

  ```
  {"\u001f/ 😀\u0007 ࠀ ":-637,"߿ÿ>":100," Ā\\\u0000􏿿&":-275}
  ```

### Example 3

- generator: `nested`
- input: `{" ࠀࠀ􏿿􏿿": {" & ￿": {"\"𐀀\u0007": {"<": [9007199254740992, -1, "𐀀😀\u0007<\u0000߿􏿿 "], "tag": 7}, "tag": 4}, "tag": 6}, "tag": 2}`

Canonical per implementation:
- **python** (len 146, sha e8a67c36b72238e6...):

  ```
  {"tag":2," ࠀࠀ􏿿􏿿":{"tag":6," & ￿":{"\"𐀀\u0007":{"<":[9007199254740992,-1,"𐀀😀\u0007<\u0000߿􏿿 "],"tag":7},"tag":4}}}
  ```
- **go** (len 158, sha 9cfb78dd2f2fef63...):

  ```
  {"tag":2,"\u2029ࠀࠀ􏿿􏿿":{"tag":6,"\u2029&\u2029￿":{"\"𐀀\u0007":{"<":[9007199254740992,-1,"𐀀😀\u0007<\u0000߿􏿿\u2029"],"tag":7},"tag":4}}}
  ```
- **rust** (len 146, sha e8a67c36b72238e6...):

  ```
  {"tag":2," ࠀࠀ􏿿􏿿":{"tag":6," & ￿":{"\"𐀀\u0007":{"<":[9007199254740992,-1,"𐀀😀\u0007<\u0000߿􏿿 "],"tag":7},"tag":4}}}
  ```
