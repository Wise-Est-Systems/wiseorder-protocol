# Disagreement signature 73

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-C1-control,contains-DEL,contains-SMP,contains-U+2028,contains-U+2029,contains-emoji`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-C1-control, contains-DEL, contains-SMP, contains-U+2028, contains-U+2029, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - array_order: 1

## Examples

### Example 1

- generator: `array_order`
- input: `[0.1, "&>􏿿", " 😀￿߿/", 2147483647, "\u0000Ā>", -63, "�\\", "￿￿\u001f𐀀  "]`

Canonical per implementation:
- **python** (len 96, sha cf1fabcfdaeef365...):

  ```
  [0.1,"&>􏿿"," 😀￿߿/",2147483647,"\u0000Ā>",-63,"�\\","￿￿\u001f𐀀  "]
  ```
- **go** (len 105, sha dcf38ec24347e0a3...):

  ```
  [0.1,"&>􏿿","\u2028😀￿߿/",2147483647,"\u0000Ā>",-63,"�\\","￿￿\u001f𐀀\u2028\u2029"]
  ```
- **rust** (len 96, sha cf1fabcfdaeef365...):

  ```
  [0.1,"&>􏿿"," 😀￿߿/",2147483647,"\u0000Ā>",-63,"�\\","￿￿\u001f𐀀  "]
  ```
