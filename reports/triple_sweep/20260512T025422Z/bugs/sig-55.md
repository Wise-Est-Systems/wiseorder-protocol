# Disagreement signature 55

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-C1-control,contains-DEL,contains-SMP,contains-U+2029,contains-emoji`

**Count:** 9

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-C1-control, contains-DEL, contains-SMP, contains-U+2029, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 4
  - array_order: 3
  - nested: 2

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"\u0000 😀߿": -27, "􏿿>": -123, "\u0000ÿ": 510, "ÿ": -418}`

Canonical per implementation:
- **python** (len 64, sha 2c640a64f8178e73...):

  ```
  {"\u0000ÿ":510,"\u0000 😀߿":-27,"ÿ":-418,"􏿿>":-123}
  ```
- **go** (len 67, sha b901fcfcb22f7f3c...):

  ```
  {"\u0000ÿ":510,"\u0000\u2029😀߿":-27,"ÿ":-418,"􏿿>":-123}
  ```
- **rust** (len 64, sha 2c640a64f8178e73...):

  ```
  {"\u0000ÿ":510,"\u0000 😀߿":-27,"ÿ":-418,"􏿿>":-123}
  ```

### Example 2

- generator: `array_order`
- input: `[0.1, "\u001f𐀀\" \"😀", -27, "\u001f <\u0007߿", -40, "<\u0000", -94, 3.141592653589793]`

Canonical per implementation:
- **python** (len 93, sha f7e6e51e28cb3308...):

  ```
  [0.1,"\u001f𐀀\" \"😀",-27,"\u001f <\u0007߿",-40,"<\u0000",-94,3.141592653589793]
  ```
- **go** (len 99, sha 1c22cac62c23ac72...):

  ```
  [0.1,"\u001f𐀀\"\u2029\"😀",-27,"\u001f\u2029<\u0007߿",-40,"<\u0000",-94,3.141592653589793]
  ```
- **rust** (len 93, sha f7e6e51e28cb3308...):

  ```
  [0.1,"\u001f𐀀\" \"😀",-27,"\u001f <\u0007߿",-40,"<\u0000",-94,3.141592653589793]
  ```

### Example 3

- generator: `object_unicode_keys`
- input: `{"􏿿>𐀀/ÿ😀": -394, "߿߿  ": 561, "\u0007": -362, "𐀀>😀": 415, " ࠀ\u0007 ��": 517, "\u0007": 244}`

Canonical per implementation:
- **python** (len 121, sha 974906b09ab0442b...):

  ```
  {"\u0007":-362,"\u0007":244," ࠀ\u0007 ��":517,"߿߿  ":561,"𐀀>😀":415,"􏿿>𐀀/ÿ😀":-394}
  ```
- **go** (len 133, sha 5b71a62285997168...):

  ```
  {"\u0007":-362,"\u0007":244,"\u2029ࠀ\u0007\u2029��":517,"߿߿\u2029\u2029":561,"𐀀>😀":415,"􏿿>𐀀/ÿ😀":-394}
  ```
- **rust** (len 121, sha 974906b09ab0442b...):

  ```
  {"\u0007":-362,"\u0007":244," ࠀ\u0007 ��":517,"߿߿  ":561,"𐀀>😀":415,"􏿿>𐀀/ÿ😀":-394}
  ```
