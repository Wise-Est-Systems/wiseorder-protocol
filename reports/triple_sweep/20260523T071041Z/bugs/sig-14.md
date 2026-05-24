# Disagreement signature 14

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-SMP,contains-U+2029`

**Count:** 3

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-SMP, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 2
  - object_unicode_keys: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"  \"&Ā ": 911, "�> ÿࠀ𐀀\u0007": 169}`

Canonical per implementation:
- **python** (len 45, sha 3822b70e6c22ea18...):

  ```
  {"  \"&Ā ":911,"�> ÿࠀ𐀀\u0007":169}
  ```
- **go** (len 48, sha 049a72686b501ffc...):

  ```
  {"  \"&Ā\u2029":911,"�> ÿࠀ𐀀\u0007":169}
  ```
- **rust** (len 45, sha 3822b70e6c22ea18...):

  ```
  {"  \"&Ā ":911,"�> ÿࠀ𐀀\u0007":169}
  ```

### Example 2

- generator: `nested`
- input: `[[2147483647, 9007199254740991, "/\u001f􏿿"], -0.0, "𐀀\"ÿ𐀀\u0000ࠀ ߿"]`

Canonical per implementation:
- **python** (len 79, sha 20f79ec30fae9748...):

  ```
  [[2147483647,9007199254740991,"/\u001f􏿿"],-0.0,"𐀀\"ÿ𐀀\u0000ࠀ ߿"]
  ```
- **go** (len 82, sha 71fd9b50e2952811...):

  ```
  [[2147483647,9007199254740991,"/\u001f􏿿"],-0.0,"𐀀\"ÿ𐀀\u0000ࠀ\u2029߿"]
  ```
- **rust** (len 79, sha 20f79ec30fae9748...):

  ```
  [[2147483647,9007199254740991,"/\u001f􏿿"],-0.0,"𐀀\"ÿ𐀀\u0000ࠀ ߿"]
  ```

### Example 3

- generator: `nested`
- input: `{"\\𐀀�\u001f /\u0007": [0.1, 0.001, "\u0000􏿿"], "tag": 7}`

Canonical per implementation:
- **python** (len 62, sha 7013e21fca092413...):

  ```
  {"\\𐀀�\u001f /\u0007":[0.1,0.001,"\u0000􏿿"],"tag":7}
  ```
- **go** (len 65, sha 7fef7da3d52935a7...):

  ```
  {"\\𐀀�\u001f\u2029/\u0007":[0.1,0.001,"\u0000􏿿"],"tag":7}
  ```
- **rust** (len 62, sha 7013e21fca092413...):

  ```
  {"\\𐀀�\u001f /\u0007":[0.1,0.001,"\u0000􏿿"],"tag":7}
  ```
