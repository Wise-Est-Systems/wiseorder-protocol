# Disagreement signature 32

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-C1-control,contains-SMP,contains-U+2028,contains-U+2029`

**Count:** 13

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-C1-control, contains-SMP, contains-U+2028, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 5
  - array_order: 4
  - nested: 3
  - mixed_object: 1

## Examples

### Example 1

- generator: `array_order`
- input: `[-44, "Ā", 91, 85, "ࠀࠀ<\u0007\\ÿ\u0007", 14, "> 􏿿 ", "\u001fÿࠀ> ߿  "]`

Canonical per implementation:
- **python** (len 87, sha a9d2366c18fa3102...):

  ```
  [-44,"Ā",91,85,"ࠀࠀ<\u0007\\ÿ\u0007",14,"> 􏿿 ","\u001fÿࠀ> ߿  "]
  ```
- **go** (len 102, sha 46898e883973d5be...):

  ```
  [-44,"Ā",91,85,"ࠀࠀ<\u0007\\ÿ\u0007",14,">\u2029􏿿\u2029","\u001fÿࠀ>\u2028߿\u2028\u2028"]
  ```
- **rust** (len 87, sha a9d2366c18fa3102...):

  ```
  [-44,"Ā",91,85,"ࠀࠀ<\u0007\\ÿ\u0007",14,"> 􏿿 ","\u001fÿࠀ> ߿  "]
  ```

### Example 2

- generator: `object_unicode_keys`
- input: `{"￿�& /\u0000<": 699, " ߿\u001fࠀĀ\\𐀀": -914, "& ": 584, "<\u0000Ā\u0007߿": 74, "  ": 185}`

Canonical per implementation:
- **python** (len 101, sha f9397c6a1f740d38...):

  ```
  {" ߿\u001fࠀĀ\\𐀀":-914,"& ":584,"<\u0000Ā\u0007߿":74,"  ":185,"￿�& /\u0000<":699}
  ```
- **go** (len 110, sha 0b9bb89d960fa8e4...):

  ```
  {" ߿\u001fࠀĀ\\𐀀":-914,"&\u2028":584,"<\u0000Ā\u0007߿":74,"\u2029 ":185,"￿�&\u2029/\u0000<":699}
  ```
- **rust** (len 101, sha f9397c6a1f740d38...):

  ```
  {" ߿\u001fࠀĀ\\𐀀":-914,"& ":584,"<\u0000Ā\u0007߿":74,"  ":185,"￿�& /\u0000<":699}
  ```

### Example 3

- generator: `array_order`
- input: `[" ", -61, 2.718281828459045, " \"ࠀ\u0007𐀀􏿿/\"", 0.30000000000000004]`

Canonical per implementation:
- **python** (len 81, sha 06d571be8fd6b8ce...):

  ```
  [" ",-61,2.718281828459045," \"ࠀ\u0007𐀀􏿿/\"",0.30000000000000004]
  ```
- **go** (len 87, sha a88a7c047b8073be...):

  ```
  ["\u2028",-61,2.718281828459045,"\u2029\"ࠀ\u0007𐀀􏿿/\"",0.30000000000000004]
  ```
- **rust** (len 81, sha 06d571be8fd6b8ce...):

  ```
  [" ",-61,2.718281828459045," \"ࠀ\u0007𐀀􏿿/\"",0.30000000000000004]
  ```
