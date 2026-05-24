# Disagreement signature 13

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-C1-control,contains-SMP,contains-U+2029`

**Count:** 17

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-C1-control, contains-SMP, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 6
  - array_order: 4
  - object_unicode_keys: 4
  - unicode_string: 3

## Examples

### Example 1

- generator: `nested`
- input: `{"Ā/\u0000�ÿ􏿿 Ā": {"􏿿�": [[{"&": 0.30000000000000004, "tag": 9}, 9007199254740991, ""], 5e-324, " ߿߿"], "tag": 9}, "tag": 4}`

Canonical per implementation:
- **python** (len 132, sha c3a84bac247955e7...):

  ```
  {"tag":4,"Ā/\u0000�ÿ􏿿 Ā":{"tag":9,"􏿿�":[[{"&":0.30000000000000004,"tag":9},9007199254740991,""],5e-324," ߿߿"]}}
  ```
- **go** (len 138, sha f8e19f0b1485af9b...):

  ```
  {"tag":4,"Ā/\u0000�ÿ􏿿\u2029Ā":{"tag":9,"􏿿�":[[{"&":0.30000000000000004,"tag":9},9007199254740991,""],5e-324,"\u2029߿߿"]}}
  ```
- **rust** (len 132, sha c3a84bac247955e7...):

  ```
  {"tag":4,"Ā/\u0000�ÿ􏿿 Ā":{"tag":9,"􏿿�":[[{"&":0.30000000000000004,"tag":9},9007199254740991,""],5e-324," ߿߿"]}}
  ```

### Example 2

- generator: `array_order`
- input: `["\\ Ā< 􏿿�", "\u0007< ", ">ࠀ\u0000"]`

Canonical per implementation:
- **python** (len 48, sha 725cb2e668203535...):

  ```
  ["\\ Ā< 􏿿�","\u0007< ",">ࠀ\u0000"]
  ```
- **go** (len 54, sha ee076c6b2a221c17...):

  ```
  ["\\\u2029Ā<\u2029􏿿�","\u0007< ",">ࠀ\u0000"]
  ```
- **rust** (len 48, sha 725cb2e668203535...):

  ```
  ["\\ Ā< 􏿿�","\u0007< ",">ࠀ\u0000"]
  ```

### Example 3

- generator: `unicode_string`
- input: `"￿ \u0007𐀀"`

Canonical per implementation:
- **python** (len 20, sha 445544dd7bb1ee40...):

  ```
  "￿ \u0007𐀀"
  ```
- **go** (len 23, sha 48dbb8c6661275e2...):

  ```
  "￿\u2029\u0007𐀀"
  ```
- **rust** (len 20, sha 445544dd7bb1ee40...):

  ```
  "￿ \u0007𐀀"
  ```
