# Disagreement signature 94

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C1-control,contains-DEL,contains-SMP,contains-U+2028`

**Count:** 5

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C1-control, contains-DEL, contains-SMP, contains-U+2028

**Length pattern:** longest:go,shortest:python

**By generator:**
  - array_order: 2
  - nested: 2
  - unicode_string: 1

## Examples

### Example 1

- generator: `array_order`
- input: `[-60, -21, "/ࠀ>", 55, 18, "𐀀￿ \\ ", 97]`

Canonical per implementation:
- **python** (len 47, sha ec3cf4bc7dc76af6...):

  ```
  [-60,-21,"/ࠀ>",55,18,"𐀀￿ \\ ",97]
  ```
- **go** (len 53, sha 8e6c23e242f6ad0f...):

  ```
  [-60,-21,"/ࠀ>",55,18,"𐀀￿\u2028\\\u2028",97]
  ```
- **rust** (len 47, sha ec3cf4bc7dc76af6...):

  ```
  [-60,-21,"/ࠀ>",55,18,"𐀀￿ \\ ",97]
  ```

### Example 2

- generator: `nested`
- input: `[{"/ÿ ߿􏿿": [[[0.3333333333333333, -0.0, ">ࠀ\""], 1e-100, " 𐀀 \\"], 1000000000000000.0, "Ā\"Ā\"𐀀"], "tag": 8}, 2147483647, "􏿿>"]`

Canonical per implementation:
- **python** (len 140, sha dda341aa42ae9af9...):

  ```
  [{"/ÿ ߿􏿿":[[[0.3333333333333333,-0.0,">ࠀ\""],1e-100," 𐀀 \\"],1000000000000000.0,"Ā\"Ā\"𐀀"],"tag":8},2147483647,"􏿿>"]
  ```
- **go** (len 143, sha 275e14ca1ad4c1d8...):

  ```
  [{"/ÿ\u2028߿􏿿":[[[0.3333333333333333,-0.0,">ࠀ\""],1e-100," 𐀀 \\"],1000000000000000.0,"Ā\"Ā\"𐀀"],"tag":8},2147483647,"􏿿>"]
  ```
- **rust** (len 140, sha dda341aa42ae9af9...):

  ```
  [{"/ÿ ߿􏿿":[[[0.3333333333333333,-0.0,">ࠀ\""],1e-100," 𐀀 \\"],1000000000000000.0,"Ā\"Ā\"𐀀"],"tag":8},2147483647,"􏿿>"]
  ```

### Example 3

- generator: `unicode_string`
- input: `"  􏿿\"\\￿"`

Canonical per implementation:
- **python** (len 20, sha 34a6f0b3af1a5b5b...):

  ```
  "  􏿿\"\\￿"
  ```
- **go** (len 23, sha c118baabaeec03c2...):

  ```
  " \u2028􏿿\"\\￿"
  ```
- **rust** (len 20, sha 34a6f0b3af1a5b5b...):

  ```
  "  􏿿\"\\￿"
  ```
