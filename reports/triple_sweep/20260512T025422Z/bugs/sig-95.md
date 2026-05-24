# Disagreement signature 95

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-DEL,contains-U+2029,contains-emoji`

**Count:** 5

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-DEL, contains-U+2029, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 2
  - nested: 1
  - unicode_string: 1
  - array_order: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"😀😀": -442, "\\ \u001fÿ ": 209, "<": -519, " ÿ": 614}`

Canonical per implementation:
- **python** (len 63, sha 08d689990cd9e23b...):

  ```
  {"\\ \u001fÿ ":209,"<":-519," ÿ":614,"😀😀":-442}
  ```
- **go** (len 72, sha edd05bec7de7fcfc...):

  ```
  {"\\\u2029\u001fÿ\u2029":209,"<":-519,"\u2029ÿ":614,"😀😀":-442}
  ```
- **rust** (len 63, sha 08d689990cd9e23b...):

  ```
  {"\\ \u001fÿ ":209,"<":-519," ÿ":614,"😀😀":-442}
  ```

### Example 2

- generator: `nested`
- input: `{"�>": [{"߿\u001f\u0000": {"😀&\u0007": {" \\< ": 5e-324, "tag": 7}, "tag": 4}, "tag": 3}, -2.5, " "], "tag": 9}`

Canonical per implementation:
- **python** (len 106, sha 2d606d930018ec01...):

  ```
  {"tag":9,"�>":[{"tag":3,"߿\u001f\u0000":{"tag":4,"😀&\u0007":{" \\< ":5e-324,"tag":7}}},-2.5," "]}
  ```
- **go** (len 109, sha 3ba29aa6d2262940...):

  ```
  {"tag":9,"�>":[{"tag":3,"߿\u001f\u0000":{"tag":4,"😀&\u0007":{" \\<\u2029":5e-324,"tag":7}}},-2.5," "]}
  ```
- **rust** (len 106, sha 2d606d930018ec01...):

  ```
  {"tag":9,"�>":[{"tag":3,"߿\u001f\u0000":{"tag":4,"😀&\u0007":{" \\< ":5e-324,"tag":7}}},-2.5," "]}
  ```

### Example 3

- generator: `object_unicode_keys`
- input: `{"߿\"  ": -360, "😀/\u0007\u0000": -573}`

Canonical per implementation:
- **python** (len 43, sha 465f27c513be90af...):

  ```
  {"😀/\u0007\u0000":-573,"߿\"  ":-360}
  ```
- **go** (len 46, sha 7335b32d0c11c6cf...):

  ```
  {"😀/\u0007\u0000":-573,"߿\"\u2029 ":-360}
  ```
- **rust** (len 43, sha 465f27c513be90af...):

  ```
  {"😀/\u0007\u0000":-573,"߿\"  ":-360}
  ```
