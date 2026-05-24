# Disagreement signature 79

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-U+2029,contains-emoji`

**Count:** 6

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-U+2029, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - unicode_string: 4
  - nested: 1
  - object_unicode_keys: 1

## Examples

### Example 1

- generator: `unicode_string`
- input: `"😀< 😀�\\"`

Canonical per implementation:
- **python** (len 19, sha acee90192cf97dba...):

  ```
  "😀< 😀�\\"
  ```
- **go** (len 22, sha 31bec6ba435fa8f7...):

  ```
  "😀<\u2029😀�\\"
  ```
- **rust** (len 19, sha acee90192cf97dba...):

  ```
  "😀< 😀�\\"
  ```

### Example 2

- generator: `unicode_string`
- input: `"😀 >"`

Canonical per implementation:
- **python** (len 10, sha 1210953c0f1dee08...):

  ```
  "😀 >"
  ```
- **go** (len 13, sha 483b0bf5cd78f569...):

  ```
  "😀\u2029>"
  ```
- **rust** (len 10, sha 1210953c0f1dee08...):

  ```
  "😀 >"
  ```

### Example 3

- generator: `nested`
- input: `{"Ā\\ ￿😀": {"<": {"�": 0.1, "tag": 6}, "tag": 6}, "tag": 9}`

Canonical per implementation:
- **python** (len 60, sha ccaf44ec6927c967...):

  ```
  {"tag":9,"Ā\\ ￿😀":{"<":{"tag":6,"�":0.1},"tag":6}}
  ```
- **go** (len 63, sha 8191e2e52d5bf552...):

  ```
  {"tag":9,"Ā\\\u2029￿😀":{"<":{"tag":6,"�":0.1},"tag":6}}
  ```
- **rust** (len 60, sha ccaf44ec6927c967...):

  ```
  {"tag":9,"Ā\\ ￿😀":{"<":{"tag":6,"�":0.1},"tag":6}}
  ```
