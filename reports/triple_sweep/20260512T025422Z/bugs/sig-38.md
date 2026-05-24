# Disagreement signature 38

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-DEL,contains-SMP,contains-U+2028,contains-U+2029`

**Count:** 12

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-DEL, contains-SMP, contains-U+2028, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 5
  - array_order: 4
  - object_unicode_keys: 2
  - unicode_string: 1

## Examples

### Example 1

- generator: `nested`
- input: `{"\u001f\u0007􏿿\\ \\ \u0007": {">": [{"ࠀĀĀ>\u0000<�": [0.001, 0.3, "� / "], "tag": 5}, 9007199254740992, "￿߿�"], "tag": 3}, "tag": 8}`

Canonical per implementation:
- **python** (len 146, sha f18aae27ee7289a4...):

  ```
  {"\u001f\u0007􏿿\\ \\ \u0007":{">":[{"tag":5,"ࠀĀĀ>\u0000<�":[0.001,0.3,"� / "]},9007199254740992,"￿߿�"],"tag":3},"tag":8}
  ```
- **go** (len 158, sha e1a1a582f857efde...):

  ```
  {"\u001f\u0007􏿿\\\u2028\\\u2029\u0007":{">":[{"tag":5,"ࠀĀĀ>\u0000<�":[0.001,0.3,"�\u2029/\u2028"]},9007199254740992,"￿߿�"],"tag":3},"tag":8}
  ```
- **rust** (len 146, sha f18aae27ee7289a4...):

  ```
  {"\u001f\u0007􏿿\\ \\ \u0007":{">":[{"tag":5,"ࠀĀĀ>\u0000<�":[0.001,0.3,"� / "]},9007199254740992,"￿߿�"],"tag":3},"tag":8}
  ```

### Example 2

- generator: `unicode_string`
- input: `"ࠀ\u0000 \\\" 𐀀"`

Canonical per implementation:
- **python** (len 26, sha e8d21fe3498d238d...):

  ```
  "ࠀ\u0000 \\\" 𐀀"
  ```
- **go** (len 32, sha 0f63af50d430d504...):

  ```
  "ࠀ\u0000\u2029\\\"\u2028𐀀"
  ```
- **rust** (len 26, sha e8d21fe3498d238d...):

  ```
  "ࠀ\u0000 \\\" 𐀀"
  ```

### Example 3

- generator: `array_order`
- input: `[">￿>￿", " Ā􏿿\u001fÿ>ࠀ ", 28]`

Canonical per implementation:
- **python** (len 43, sha 3a76cf122c9a907a...):

  ```
  [">￿>￿"," Ā􏿿\u001fÿ>ࠀ ",28]
  ```
- **go** (len 49, sha 33d179ee7a7553fa...):

  ```
  [">￿>￿","\u2028Ā􏿿\u001fÿ>ࠀ\u2029",28]
  ```
- **rust** (len 43, sha 3a76cf122c9a907a...):

  ```
  [">￿>￿"," Ā􏿿\u001fÿ>ࠀ ",28]
  ```
