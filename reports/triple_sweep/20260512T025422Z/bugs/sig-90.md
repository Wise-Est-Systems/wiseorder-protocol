# Disagreement signature 90

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-DEL,contains-SMP,contains-U+2029,contains-emoji`

**Count:** 5

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-DEL, contains-SMP, contains-U+2029, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 1
  - mixed_object: 1
  - object_unicode_keys: 1
  - array_order: 1
  - unicode_string: 1

## Examples

### Example 1

- generator: `nested`
- input: `[[1e+17, 0, "￿􏿿\\߿"], 0.3, "߿߿/�😀\\ "]`

Canonical per implementation:
- **python** (len 51, sha 6068a4b28142d3a6...):

  ```
  [[1e+17,0,"￿􏿿\\߿"],0.3,"߿߿/�😀\\ "]
  ```
- **go** (len 54, sha ea5ed30856912ea5...):

  ```
  [[1e+17,0,"￿􏿿\\߿"],0.3,"߿߿/�😀\\\u2029"]
  ```
- **rust** (len 51, sha 6068a4b28142d3a6...):

  ```
  [[1e+17,0,"￿􏿿\\߿"],0.3,"߿߿/�😀\\ "]
  ```

### Example 2

- generator: `mixed_object`
- input: `{"k1": [], "k3": " < ÿ߿\\😀", "k5": [-2147483648, 1e+17], "k2": "𐀀Ā￿", "k4": 0.2, "k0": []}`

Canonical per implementation:
- **python** (len 92, sha ee700c3b3064e2c7...):

  ```
  {"k0":[],"k1":[],"k2":"𐀀Ā￿","k3":" < ÿ߿\\😀","k4":0.2,"k5":[-2147483648,1e+17]}
  ```
- **go** (len 95, sha 24a8a75118c08200...):

  ```
  {"k0":[],"k1":[],"k2":"𐀀Ā￿","k3":"\u2029< ÿ߿\\😀","k4":0.2,"k5":[-2147483648,1e+17]}
  ```
- **rust** (len 92, sha ee700c3b3064e2c7...):

  ```
  {"k0":[],"k1":[],"k2":"𐀀Ā￿","k3":" < ÿ߿\\😀","k4":0.2,"k5":[-2147483648,1e+17]}
  ```

### Example 3

- generator: `object_unicode_keys`
- input: `{"􏿿�\\ 𐀀": 658, "�\\&😀 &": 256}`

Canonical per implementation:
- **python** (len 47, sha b12d180b45206300...):

  ```
  {"�\\&😀 &":256,"􏿿�\\ 𐀀":658}
  ```
- **go** (len 53, sha 47e0b0232e593c17...):

  ```
  {"�\\&😀\u2029&":256,"􏿿�\\\u2029𐀀":658}
  ```
- **rust** (len 47, sha b12d180b45206300...):

  ```
  {"�\\&😀 &":256,"􏿿�\\ 𐀀":658}
  ```
