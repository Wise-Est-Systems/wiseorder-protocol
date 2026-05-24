# Disagreement signature 3

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-SMP,contains-U+2029,contains-emoji`

**Count:** 4

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-SMP, contains-U+2029, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 2
  - mixed_object: 1
  - array_order: 1

## Examples

### Example 1

- generator: `mixed_object`
- input: `{"k4": 0.3, "k0": [], "k2": " 𐀀ࠀ𐀀😀�&😀", "k1": false, "k3": null}`

Canonical per implementation:
- **python** (len 73, sha b9d76670b64581e1...):

  ```
  {"k0":[],"k1":false,"k2":" 𐀀ࠀ𐀀😀�&😀","k3":null,"k4":0.3}
  ```
- **go** (len 76, sha d38fb92286017c80...):

  ```
  {"k0":[],"k1":false,"k2":"\u2029𐀀ࠀ𐀀😀�&😀","k3":null,"k4":0.3}
  ```
- **rust** (len 73, sha b9d76670b64581e1...):

  ```
  {"k0":[],"k1":false,"k2":" 𐀀ࠀ𐀀😀�&😀","k3":null,"k4":0.3}
  ```

### Example 2

- generator: `nested`
- input: `{"߿߿𐀀߿\\": {"𐀀𐀀&&😀/�": {"􏿿ÿ> ": 1e+100, "tag": 6}, "tag": 4}, "tag": 3}`

Canonical per implementation:
- **python** (len 85, sha a0d69ba69986bc54...):

  ```
  {"tag":3,"߿߿𐀀߿\\":{"tag":4,"𐀀𐀀&&😀/�":{"tag":6,"􏿿ÿ> ":1e+100}}}
  ```
- **go** (len 88, sha 56839a75f8502e5f...):

  ```
  {"tag":3,"߿߿𐀀߿\\":{"tag":4,"𐀀𐀀&&😀/�":{"tag":6,"􏿿ÿ>\u2029":1e+100}}}
  ```
- **rust** (len 85, sha a0d69ba69986bc54...):

  ```
  {"tag":3,"߿߿𐀀߿\\":{"tag":4,"𐀀𐀀&&😀/�":{"tag":6,"􏿿ÿ> ":1e+100}}}
  ```

### Example 3

- generator: `array_order`
- input: `[20, ">􏿿  ", "\\￿\"􏿿", ">ÿࠀ😀", 0, -5]`

Canonical per implementation:
- **python** (len 50, sha 3360bbba64e5c059...):

  ```
  [20,">􏿿  ","\\￿\"􏿿",">ÿࠀ😀",0,-5]
  ```
- **go** (len 56, sha 95340a9f44657138...):

  ```
  [20,">􏿿\u2029\u2029","\\￿\"􏿿",">ÿࠀ😀",0,-5]
  ```
- **rust** (len 50, sha 3360bbba64e5c059...):

  ```
  [20,">􏿿  ","\\￿\"􏿿",">ÿࠀ😀",0,-5]
  ```
