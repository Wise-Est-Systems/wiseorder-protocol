# Disagreement signature 88

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-DEL,contains-U+2029`

**Count:** 5

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-DEL, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 3
  - unicode_string: 1
  - object_unicode_keys: 1

## Examples

### Example 1

- generator: `nested`
- input: `[{"￿": {"": {" ￿ \"": {"ÿ\"\\\u0000\u001f&\u0007": 0.0, "tag": 5}, "tag": 6}, "tag": 0}, "tag": 1}, 9007199254740992, "\u001f /"]`

Canonical per implementation:
- **python** (len 127, sha b7b2519ea785f4c9...):

  ```
  [{"tag":1,"￿":{"tag":0,"":{"tag":6," ￿ \"":{"tag":5,"ÿ\"\\\u0000\u001f&\u0007":0.0}}}},9007199254740992,"\u001f /"]
  ```
- **go** (len 136, sha 2205c380325b1d36...):

  ```
  [{"tag":1,"￿":{"tag":0,"":{"tag":6,"\u2029￿\u2029\"":{"tag":5,"ÿ\"\\\u0000\u001f&\u0007":0.0}}}},9007199254740992,"\u001f\u2029/"]
  ```
- **rust** (len 127, sha b7b2519ea785f4c9...):

  ```
  [{"tag":1,"￿":{"tag":0,"":{"tag":6," ￿ \"":{"tag":5,"ÿ\"\\\u0000\u001f&\u0007":0.0}}}},9007199254740992,"\u001f /"]
  ```

### Example 2

- generator: `nested`
- input: `[[0.3333333333333333, 2147483647, "￿￿\u0000 ÿ <"], 5e-324, ""]`

Canonical per implementation:
- **python** (len 66, sha 6958326d0db3da37...):

  ```
  [[0.3333333333333333,2147483647,"￿￿\u0000 ÿ <"],5e-324,""]
  ```
- **go** (len 69, sha 80ef8947c09a1e8a...):

  ```
  [[0.3333333333333333,2147483647,"￿￿\u0000\u2029ÿ <"],5e-324,""]
  ```
- **rust** (len 66, sha 6958326d0db3da37...):

  ```
  [[0.3333333333333333,2147483647,"￿￿\u0000 ÿ <"],5e-324,""]
  ```

### Example 3

- generator: `unicode_string`
- input: `"\u0007&ÿ "`

Canonical per implementation:
- **python** (len 15, sha 86f370f435c5e688...):

  ```
  "\u0007&ÿ "
  ```
- **go** (len 18, sha 4d7563e72ac6cbcd...):

  ```
  "\u0007&ÿ\u2029"
  ```
- **rust** (len 15, sha 86f370f435c5e688...):

  ```
  "\u0007&ÿ "
  ```
