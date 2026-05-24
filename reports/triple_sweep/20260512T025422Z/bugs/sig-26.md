# Disagreement signature 26

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-U+2028,contains-U+2029`

**Count:** 14

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-U+2028, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 4
  - unicode_string: 3
  - object_unicode_keys: 3
  - mixed_object: 2
  - array_order: 2

## Examples

### Example 1

- generator: `nested`
- input: `[[2.718281828459045, 0.0, "  \u0007߿Ā/\u0007"], 5e-324, "ࠀ￿"]`

Canonical per implementation:
- **python** (len 67, sha f668535ab080d8ff...):

  ```
  [[2.718281828459045,0.0,"  \u0007߿Ā/\u0007"],5e-324,"ࠀ￿"]
  ```
- **go** (len 73, sha fb9377bd5ef77655...):

  ```
  [[2.718281828459045,0.0,"\u2029\u2028\u0007߿Ā/\u0007"],5e-324,"ࠀ￿"]
  ```
- **rust** (len 67, sha f668535ab080d8ff...):

  ```
  [[2.718281828459045,0.0,"  \u0007߿Ā/\u0007"],5e-324,"ࠀ￿"]
  ```

### Example 2

- generator: `unicode_string`
- input: `"\u001f �ÿ/ "`

Canonical per implementation:
- **python** (len 20, sha c735f863a94f68c5...):

  ```
  "\u001f �ÿ/ "
  ```
- **go** (len 26, sha b0b62bfa180bc254...):

  ```
  "\u001f\u2028�ÿ/\u2029"
  ```
- **rust** (len 20, sha c735f863a94f68c5...):

  ```
  "\u001f �ÿ/ "
  ```

### Example 3

- generator: `nested`
- input: `{" ": {"� <": [5e-324, 0.3, "\u0000"], "tag": 8}, "tag": 6}`

Canonical per implementation:
- **python** (len 57, sha fd141bbd84b3d2c2...):

  ```
  {"tag":6," ":{"tag":8,"� <":[5e-324,0.3,"\u0000"]}}
  ```
- **go** (len 63, sha dab249206e0f8792...):

  ```
  {"tag":6,"\u2029":{"tag":8,"�\u2028<":[5e-324,0.3,"\u0000"]}}
  ```
- **rust** (len 57, sha fd141bbd84b3d2c2...):

  ```
  {"tag":6," ":{"tag":8,"� <":[5e-324,0.3,"\u0000"]}}
  ```
