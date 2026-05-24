# Disagreement signature 48

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-C1-control,contains-U+2028`

**Count:** 10

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-C1-control, contains-U+2028

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 4
  - object_unicode_keys: 2
  - array_order: 2
  - mixed_object: 2

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{" �￿ \u0007": 294, "߿": -221}`

Canonical per implementation:
- **python** (len 36, sha 8265bc7ec1c87686...):

  ```
  {"߿":-221," �￿ \u0007":294}
  ```
- **go** (len 39, sha 7bffc4c093b7f352...):

  ```
  {"߿":-221,"\u2028�￿ \u0007":294}
  ```
- **rust** (len 36, sha 8265bc7ec1c87686...):

  ```
  {"߿":-221," �￿ \u0007":294}
  ```

### Example 2

- generator: `array_order`
- input: `[" &", "ࠀࠀ\u0000", 0.3333333333333333, 0.2, 84]`

Canonical per implementation:
- **python** (len 51, sha 09f60852e00157e7...):

  ```
  [" &","ࠀࠀ\u0000",0.3333333333333333,0.2,84]
  ```
- **go** (len 54, sha 20f45c106dc082ca...):

  ```
  ["\u2028&","ࠀࠀ\u0000",0.3333333333333333,0.2,84]
  ```
- **rust** (len 51, sha 09f60852e00157e7...):

  ```
  [" &","ࠀࠀ\u0000",0.3333333333333333,0.2,84]
  ```

### Example 3

- generator: `nested`
- input: `[[{"&>￿": {"\u0000�": 1e-100, "tag": 4}, "tag": 1}, 5e-324, "\u001f"], 3.14159, " \u0007\\"]`

Canonical per implementation:
- **python** (len 90, sha a8f0430ac341911f...):

  ```
  [[{"&>￿":{"\u0000�":1e-100,"tag":4},"tag":1},5e-324,"\u001f"],3.14159," \u0007\\"]
  ```
- **go** (len 93, sha 5911150b68fed09d...):

  ```
  [[{"&>￿":{"\u0000�":1e-100,"tag":4},"tag":1},5e-324,"\u001f"],3.14159,"\u2028\u0007\\"]
  ```
- **rust** (len 90, sha a8f0430ac341911f...):

  ```
  [[{"&>￿":{"\u0000�":1e-100,"tag":4},"tag":1},5e-324,"\u001f"],3.14159," \u0007\\"]
  ```
