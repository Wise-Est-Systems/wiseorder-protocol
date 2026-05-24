# Disagreement signature 19

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-SMP,contains-U+2028,contains-U+2029,contains-emoji`

**Count:** 16

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-SMP, contains-U+2028, contains-U+2029, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 8
  - nested: 7
  - mixed_object: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{" &": -767, "ÿ/ /": 534, "𐀀\u0000😀>\"ĀĀ ": -535}`

Canonical per implementation:
- **python** (len 57, sha e8e16bdf5c56e9a6...):

  ```
  {"ÿ/ /":534," &":-767,"𐀀\u0000😀>\"ĀĀ ":-535}
  ```
- **go** (len 63, sha 8be715e9dc67c466...):

  ```
  {"ÿ/ /":534,"\u2029&":-767,"𐀀\u0000😀>\"ĀĀ\u2028":-535}
  ```
- **rust** (len 57, sha e8e16bdf5c56e9a6...):

  ```
  {"ÿ/ /":534," &":-767,"𐀀\u0000😀>\"ĀĀ ":-535}
  ```

### Example 2

- generator: `nested`
- input: `[{" \u001f\\ ": {" ": [{">\" 😀 ": 0.2, "tag": 7}, 0, "\"ࠀ\"􏿿ÿ𐀀"], "tag": 5}, "tag": 0}, 0.3333333333333333, " >&>"]`

Canonical per implementation:
- **python** (len 122, sha aa95e430b6b00fff...):

  ```
  [{"tag":0," \u001f\\ ":{" ":[{">\" 😀 ":0.2,"tag":7},0,"\"ࠀ\"􏿿ÿ𐀀"],"tag":5}},0.3333333333333333," >&>"]
  ```
- **go** (len 134, sha cff05e7b67131e4e...):

  ```
  [{"tag":0,"\u2029\u001f\\\u2028":{" ":[{">\" 😀\u2028":0.2,"tag":7},0,"\"ࠀ\"􏿿ÿ𐀀"],"tag":5}},0.3333333333333333,"\u2028>&>"]
  ```
- **rust** (len 122, sha aa95e430b6b00fff...):

  ```
  [{"tag":0," \u001f\\ ":{" ":[{">\" 😀 ":0.2,"tag":7},0,"\"ࠀ\"􏿿ÿ𐀀"],"tag":5}},0.3333333333333333," >&>"]
  ```

### Example 3

- generator: `nested`
- input: `{"\u0000& ￿": {"￿\\😀𐀀\\\u0007􏿿": {"  \u0000𐀀": 9007199254740991, "tag": 2}, "tag": 3}, "tag": 3}`

Canonical per implementation:
- **python** (len 107, sha 57567446f4ca2b65...):

  ```
  {"\u0000& ￿":{"tag":3,"￿\\😀𐀀\\\u0007􏿿":{"tag":2,"  \u0000𐀀":9007199254740991}},"tag":3}
  ```
- **go** (len 113, sha 41a637659a421591...):

  ```
  {"\u0000&\u2028￿":{"tag":3,"￿\\😀𐀀\\\u0007􏿿":{"tag":2,"\u2029 \u0000𐀀":9007199254740991}},"tag":3}
  ```
- **rust** (len 107, sha 57567446f4ca2b65...):

  ```
  {"\u0000& ￿":{"tag":3,"￿\\😀𐀀\\\u0007􏿿":{"tag":2,"  \u0000𐀀":9007199254740991}},"tag":3}
  ```
