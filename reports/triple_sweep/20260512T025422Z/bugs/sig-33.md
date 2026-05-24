# Disagreement signature 33

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-U+2029,contains-emoji`

**Count:** 13

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-U+2029, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - unicode_string: 4
  - array_order: 3
  - object_unicode_keys: 3
  - nested: 2
  - mixed_object: 1

## Examples

### Example 1

- generator: `unicode_string`
- input: `"😀\u001f>\u001f ￿Ā "`

Canonical per implementation:
- **python** (len 28, sha a7b40cde34065123...):

  ```
  "😀\u001f>\u001f ￿Ā "
  ```
- **go** (len 31, sha 275417598f9cb49c...):

  ```
  "😀\u001f>\u001f\u2029￿Ā "
  ```
- **rust** (len 28, sha a7b40cde34065123...):

  ```
  "😀\u001f>\u001f ￿Ā "
  ```

### Example 2

- generator: `nested`
- input: `[{"😀 <>/ÿ": {"\u0007Ā": -0.0, "tag": 9}, "tag": 1}, 1, "<Ā&\\ "]`

Canonical per implementation:
- **python** (len 64, sha a8cb2147023ea46b...):

  ```
  [{"tag":1,"😀 <>/ÿ":{"\u0007Ā":-0.0,"tag":9}},1,"<Ā&\\ "]
  ```
- **go** (len 67, sha 07f6439fda8f05c0...):

  ```
  [{"tag":1,"😀 <>/ÿ":{"\u0007Ā":-0.0,"tag":9}},1,"<Ā&\\\u2029"]
  ```
- **rust** (len 64, sha a8cb2147023ea46b...):

  ```
  [{"tag":1,"😀 <>/ÿ":{"\u0007Ā":-0.0,"tag":9}},1,"<Ā&\\ "]
  ```

### Example 3

- generator: `mixed_object`
- input: `{"k0": 1e+17, "k1": "😀\u0000ࠀࠀࠀ \u001f"}`

Canonical per implementation:
- **python** (len 48, sha 79e56bf0abab5663...):

  ```
  {"k0":1e+17,"k1":"😀\u0000ࠀࠀࠀ \u001f"}
  ```
- **go** (len 51, sha f3ef38948d7777da...):

  ```
  {"k0":1e+17,"k1":"😀\u0000ࠀࠀࠀ\u2029\u001f"}
  ```
- **rust** (len 48, sha 79e56bf0abab5663...):

  ```
  {"k0":1e+17,"k1":"😀\u0000ࠀࠀࠀ \u001f"}
  ```
