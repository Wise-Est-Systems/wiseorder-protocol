# Disagreement signature 28

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-U+2028,contains-emoji`

**Count:** 13

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-U+2028, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - array_order: 6
  - nested: 3
  - object_unicode_keys: 2
  - unicode_string: 1
  - mixed_object: 1

## Examples

### Example 1

- generator: `array_order`
- input: `[10000000000.0, 0.3, 1e-100, ">< \u001f😀"]`

Canonical per implementation:
- **python** (len 44, sha c6f52ee1c9146783...):

  ```
  [10000000000.0,0.3,1e-100,">< \u001f😀"]
  ```
- **go** (len 47, sha 26046ee1ede29715...):

  ```
  [10000000000.0,0.3,1e-100,"><\u2028\u001f😀"]
  ```
- **rust** (len 44, sha c6f52ee1c9146783...):

  ```
  [10000000000.0,0.3,1e-100,">< \u001f😀"]
  ```

### Example 2

- generator: `array_order`
- input: `["< �>/😀", "\u001f"]`

Canonical per implementation:
- **python** (len 26, sha e319e0160606d177...):

  ```
  ["< �>/😀","\u001f"]
  ```
- **go** (len 29, sha bcd847863707dac2...):

  ```
  ["<\u2028�>/😀","\u001f"]
  ```
- **rust** (len 26, sha e319e0160606d177...):

  ```
  ["< �>/😀","\u001f"]
  ```

### Example 3

- generator: `nested`
- input: `[{"<߿\u0000ÿ/": [{"\u0007": [1e+100, 0.3333333333333333, "�"], "tag": 2}, 9007199254740991, "� /\"߿ÿ>ࠀ"], "tag": 6}, 1e+16, "😀"]`

Canonical per implementation:
- **python** (len 131, sha e0e90d13a3543e1a...):

  ```
  [{"<߿\u0000ÿ/":[{"\u0007":[1e+100,0.3333333333333333,"�"],"tag":2},9007199254740991,"� /\"߿ÿ>ࠀ"],"tag":6},1e+16,"😀"]
  ```
- **go** (len 134, sha fd6abb56034594f1...):

  ```
  [{"<߿\u0000ÿ/":[{"\u0007":[1e+100,0.3333333333333333,"�"],"tag":2},9007199254740991,"�\u2028/\"߿ÿ>ࠀ"],"tag":6},1e+16,"😀"]
  ```
- **rust** (len 131, sha e0e90d13a3543e1a...):

  ```
  [{"<߿\u0000ÿ/":[{"\u0007":[1e+100,0.3333333333333333,"�"],"tag":2},9007199254740991,"� /\"߿ÿ>ࠀ"],"tag":6},1e+16,"😀"]
  ```
