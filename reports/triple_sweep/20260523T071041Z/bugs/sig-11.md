# Disagreement signature 11

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-SMP,contains-U+2028,contains-U+2029,contains-emoji`

**Count:** 3

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-SMP, contains-U+2028, contains-U+2029, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 2
  - array_order: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"߿\u0000   ": 667, "ࠀ/ >": 937, "\u001f</߿􏿿߿<😀": 887}`

Canonical per implementation:
- **python** (len 66, sha 925ee4deaff175da...):

  ```
  {"\u001f</߿􏿿߿<😀":887,"߿\u0000   ":667,"ࠀ/ >":937}
  ```
- **go** (len 75, sha c3d6328cc0401981...):

  ```
  {"\u001f</߿􏿿߿<😀":887,"߿\u0000 \u2029\u2028":667,"ࠀ/\u2029>":937}
  ```
- **rust** (len 66, sha 925ee4deaff175da...):

  ```
  {"\u001f</߿􏿿߿<😀":887,"߿\u0000   ":667,"ࠀ/ >":937}
  ```

### Example 2

- generator: `object_unicode_keys`
- input: `{" 😀�￿< 𐀀": -942, "&😀  >�\u0007ÿ": 824}`

Canonical per implementation:
- **python** (len 56, sha f1ecd8b4c4af4809...):

  ```
  {"&😀  >�\u0007ÿ":824," 😀�￿< 𐀀":-942}
  ```
- **go** (len 62, sha b91b99ecd8bb22a6...):

  ```
  {"&😀\u2029 >�\u0007ÿ":824,"\u2028😀�￿< 𐀀":-942}
  ```
- **rust** (len 56, sha f1ecd8b4c4af4809...):

  ```
  {"&😀  >�\u0007ÿ":824," 😀�￿< 𐀀":-942}
  ```

### Example 3

- generator: `array_order`
- input: `[0.0, "􏿿<\"", 91, " Āÿ􏿿ࠀ\u0000", "ÿ\u001fÿ\\😀", 5e-324, "  < Ā"]`

Canonical per implementation:
- **python** (len 80, sha c4ce6cd312bbfa55...):

  ```
  [0.0,"􏿿<\"",91," Āÿ􏿿ࠀ\u0000","ÿ\u001fÿ\\😀",5e-324,"  < Ā"]
  ```
- **go** (len 89, sha d96084e0a9f778cc...):

  ```
  [0.0,"􏿿<\"",91,"\u2029Āÿ􏿿ࠀ\u0000","ÿ\u001fÿ\\😀",5e-324,"\u2028 <\u2029Ā"]
  ```
- **rust** (len 80, sha c4ce6cd312bbfa55...):

  ```
  [0.0,"􏿿<\"",91," Āÿ􏿿ࠀ\u0000","ÿ\u001fÿ\\😀",5e-324,"  < Ā"]
  ```
