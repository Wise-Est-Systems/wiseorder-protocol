# Disagreement signature 61

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-C1-control,contains-U+2028,contains-emoji`

**Count:** 8

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-C1-control, contains-U+2028, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 4
  - array_order: 2
  - mixed_object: 2

## Examples

### Example 1

- generator: `array_order`
- input: `[-95, 0.30000000000000004, "߿ \u0000ࠀ😀߿", -62, "\u0000<", 0.3333333333333333, "߿/"]`

Canonical per implementation:
- **python** (len 93, sha 8e48a602a759fc1f...):

  ```
  [-95,0.30000000000000004,"߿ \u0000ࠀ😀߿",-62,"\u0000<",0.3333333333333333,"߿/"]
  ```
- **go** (len 96, sha f2e33b4f5c690889...):

  ```
  [-95,0.30000000000000004,"߿\u2028\u0000ࠀ😀߿",-62,"\u0000<",0.3333333333333333,"߿/"]
  ```
- **rust** (len 93, sha 8e48a602a759fc1f...):

  ```
  [-95,0.30000000000000004,"߿ \u0000ࠀ😀߿",-62,"\u0000<",0.3333333333333333,"߿/"]
  ```

### Example 2

- generator: `nested`
- input: `[{"\u0000￿>  ÿ": [10000000000.0, 0.30000000000000004, "ࠀ\""], "tag": 3}, 2.2250738585072014e-308, "<\\ࠀ\u001fࠀ😀"]`

Canonical per implementation:
- **python** (len 126, sha fb6ab3869cce6e63...):

  ```
  [{"\u0000￿>  ÿ":[10000000000.0,0.30000000000000004,"ࠀ\""],"tag":3},2.2250738585072014e-308,"<\\ࠀ\u001fࠀ😀"]
  ```
- **go** (len 129, sha daa9c2023a67bbcf...):

  ```
  [{"\u0000￿>\u2028 ÿ":[10000000000.0,0.30000000000000004,"ࠀ\""],"tag":3},2.2250738585072014e-308,"<\\ࠀ\u001fࠀ😀"]
  ```
- **rust** (len 126, sha fb6ab3869cce6e63...):

  ```
  [{"\u0000￿>  ÿ":[10000000000.0,0.30000000000000004,"ࠀ\""],"tag":3},2.2250738585072014e-308,"<\\ࠀ\u001fࠀ😀"]
  ```

### Example 3

- generator: `mixed_object`
- input: `{"k0": "\u0007� ", "k1": "😀\u0007\\\u0000￿ \u0000&"}`

Canonical per implementation:
- **python** (len 60, sha a4c11f1fb91fc2e9...):

  ```
  {"k0":"\u0007� ","k1":"😀\u0007\\\u0000￿ \u0000&"}
  ```
- **go** (len 63, sha e568ad14c15f835a...):

  ```
  {"k0":"\u0007� ","k1":"😀\u0007\\\u0000￿\u2028\u0000&"}
  ```
- **rust** (len 60, sha a4c11f1fb91fc2e9...):

  ```
  {"k0":"\u0007� ","k1":"😀\u0007\\\u0000￿ \u0000&"}
  ```
