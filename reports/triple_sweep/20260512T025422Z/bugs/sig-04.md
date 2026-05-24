# Disagreement signature 4

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-U+2028`

**Count:** 26

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-U+2028

**Length pattern:** longest:go,shortest:python

**By generator:**
  - unicode_string: 9
  - nested: 6
  - object_unicode_keys: 4
  - mixed_object: 4
  - array_order: 3

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"ࠀ": -819, "  \\\u0000<": -730}`

Canonical per implementation:
- **python** (len 33, sha daad7917473f5a63...):

  ```
  {"ࠀ":-819,"  \\\u0000<":-730}
  ```
- **go** (len 36, sha abc7ffeb1c77eb78...):

  ```
  {"ࠀ":-819,"\u2028 \\\u0000<":-730}
  ```
- **rust** (len 33, sha daad7917473f5a63...):

  ```
  {"ࠀ":-819,"  \\\u0000<":-730}
  ```

### Example 2

- generator: `nested`
- input: `{"   \u0000�": [[0.3, 1.7976931348623157e+308, "߿"], -1, "\u0007"], "tag": 1}`

Canonical per implementation:
- **python** (len 77, sha c444381b7a22fc7e...):

  ```
  {"tag":1,"   \u0000�":[[0.3,1.7976931348623157e+308,"߿"],-1,"\u0007"]}
  ```
- **go** (len 83, sha 8a157f40406b7392...):

  ```
  {"tag":1,"\u2028\u2028 \u0000�":[[0.3,1.7976931348623157e+308,"߿"],-1,"\u0007"]}
  ```
- **rust** (len 77, sha c444381b7a22fc7e...):

  ```
  {"tag":1,"   \u0000�":[[0.3,1.7976931348623157e+308,"߿"],-1,"\u0007"]}
  ```

### Example 3

- generator: `nested`
- input: `{" ": {"Ā><\u0007": 2.2250738585072014e-308, "tag": 2}, "tag": 0}`

Canonical per implementation:
- **python** (len 62, sha e5a48e41aab9e27b...):

  ```
  {"tag":0," ":{"tag":2,"Ā><\u0007":2.2250738585072014e-308}}
  ```
- **go** (len 65, sha f03831ce7e7a3711...):

  ```
  {"tag":0,"\u2028":{"tag":2,"Ā><\u0007":2.2250738585072014e-308}}
  ```
- **rust** (len 62, sha e5a48e41aab9e27b...):

  ```
  {"tag":0," ":{"tag":2,"Ā><\u0007":2.2250738585072014e-308}}
  ```
