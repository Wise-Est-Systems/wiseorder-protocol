# Disagreement signature 45

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-C1-control,contains-DEL,contains-SMP,contains-U+2029`

**Count:** 11

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-C1-control, contains-DEL, contains-SMP, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 5
  - nested: 4
  - array_order: 2

## Examples

### Example 1

- generator: `nested`
- input: `[{"�<&\"": {"&Ā<\u001f   𐀀": [2.2250738585072014e-308, 0.001, "￿\u0000"], "tag": 0}, "tag": 2}, 2147483647, "><ÿ߿\u001f/>"]`

Canonical per implementation:
- **python** (len 134, sha 548e57321a8bb039...):

  ```
  [{"tag":2,"�<&\"":{"&Ā<\u001f   𐀀":[2.2250738585072014e-308,0.001,"￿\u0000"],"tag":0}},2147483647,"><ÿ߿\u001f/>"]
  ```
- **go** (len 143, sha 61295753f3d1c8a3...):

  ```
  [{"tag":2,"�<&\"":{"&Ā<\u001f\u2029\u2029\u2029𐀀":[2.2250738585072014e-308,0.001,"￿\u0000"],"tag":0}},2147483647,"><ÿ߿\u001f/>"]
  ```
- **rust** (len 134, sha 548e57321a8bb039...):

  ```
  [{"tag":2,"�<&\"":{"&Ā<\u001f   𐀀":[2.2250738585072014e-308,0.001,"￿\u0000"],"tag":0}},2147483647,"><ÿ߿\u001f/>"]
  ```

### Example 2

- generator: `array_order`
- input: `[" �\u0007", "< ", -17, "/\u001f 𐀀Ā", 2147483647]`

Canonical per implementation:
- **python** (len 60, sha 5e5bebcfc6548f0d...):

  ```
  [" �\u0007","< ",-17,"/\u001f 𐀀Ā",2147483647]
  ```
- **go** (len 66, sha f900a72001f68a15...):

  ```
  [" �\u0007","<\u2029",-17,"/\u001f\u2029𐀀Ā",2147483647]
  ```
- **rust** (len 60, sha 5e5bebcfc6548f0d...):

  ```
  [" �\u0007","< ",-17,"/\u001f 𐀀Ā",2147483647]
  ```

### Example 3

- generator: `object_unicode_keys`
- input: `{"\u0007􏿿ࠀ�￿<\u001f": -495, "�/>\u0000 &\u0000": -587, ">&\"�/": 394, "\u0007߿<߿ ": -65}`

Canonical per implementation:
- **python** (len 104, sha 1e77e6ce08b9934d...):

  ```
  {"\u0007߿<߿ ":-65,"\u0007􏿿ࠀ�￿<\u001f":-495,">&\"�/":394,"�/>\u0000 &\u0000":-587}
  ```
- **go** (len 107, sha 4fe390241c571dc4...):

  ```
  {"\u0007߿<߿ ":-65,"\u0007􏿿ࠀ�￿<\u001f":-495,">&\"�/":394,"�/>\u0000\u2029&\u0000":-587}
  ```
- **rust** (len 104, sha 1e77e6ce08b9934d...):

  ```
  {"\u0007߿<߿ ":-65,"\u0007􏿿ࠀ�￿<\u001f":-495,">&\"�/":394,"�/>\u0000 &\u0000":-587}
  ```
