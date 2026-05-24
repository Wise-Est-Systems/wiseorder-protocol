# Disagreement signature 39

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-DEL,contains-SMP,contains-U+2028`

**Count:** 12

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-DEL, contains-SMP, contains-U+2028

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 5
  - array_order: 4
  - nested: 3

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"&": 215, " 𐀀ࠀ": 400, "  \u0000  􏿿": 523, "<\"": -43, "ࠀĀ߿߿\u0007": 506, "  > ": -127}`

Canonical per implementation:
- **python** (len 101, sha 3241ad290ac20fb1...):

  ```
  {" 𐀀ࠀ":400,"&":215,"<\"":-43,"ࠀĀ߿߿\u0007":506,"  \u0000  􏿿":523,"  > ":-127}
  ```
- **go** (len 116, sha bf9256a237793877...):

  ```
  {" 𐀀ࠀ":400,"&":215,"<\"":-43,"ࠀĀ߿߿\u0007":506,"\u2028 \u0000\u2028\u2028􏿿":523,"\u2028\u2028> ":-127}
  ```
- **rust** (len 101, sha 3241ad290ac20fb1...):

  ```
  {" 𐀀ࠀ":400,"&":215,"<\"":-43,"ࠀĀ߿߿\u0007":506,"  \u0000  􏿿":523,"  > ":-127}
  ```

### Example 2

- generator: `array_order`
- input: `[46, "\\  >\u0007", 0.2, -1, "\\&𐀀\u0000ࠀ\u0000￿/", 2.718281828459045, 27, "/𐀀 \u001f"]`

Canonical per implementation:
- **python** (len 94, sha 4d723c7afe21716f...):

  ```
  [46,"\\  >\u0007",0.2,-1,"\\&𐀀\u0000ࠀ\u0000￿/",2.718281828459045,27,"/𐀀 \u001f"]
  ```
- **go** (len 97, sha e2a9b629e27c2604...):

  ```
  [46,"\\  >\u0007",0.2,-1,"\\&𐀀\u0000ࠀ\u0000￿/",2.718281828459045,27,"/𐀀\u2028\u001f"]
  ```
- **rust** (len 94, sha 4d723c7afe21716f...):

  ```
  [46,"\\  >\u0007",0.2,-1,"\\&𐀀\u0000ࠀ\u0000￿/",2.718281828459045,27,"/𐀀 \u001f"]
  ```

### Example 3

- generator: `object_unicode_keys`
- input: `{" 𐀀\"": 360, "\u001f<": -6, "�": 604}`

Canonical per implementation:
- **python** (len 41, sha c4cd6206e36f6bc4...):

  ```
  {"\u001f<":-6," 𐀀\"":360,"�":604}
  ```
- **go** (len 44, sha 66f479287a5a2105...):

  ```
  {"\u001f<":-6,"\u2028𐀀\"":360,"�":604}
  ```
- **rust** (len 41, sha c4cd6206e36f6bc4...):

  ```
  {"\u001f<":-6," 𐀀\"":360,"�":604}
  ```
