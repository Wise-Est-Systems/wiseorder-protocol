# Disagreement signature 73

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-DEL,contains-SMP,contains-U+2028,contains-emoji`

**Count:** 6

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-DEL, contains-SMP, contains-U+2028, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 3
  - array_order: 2
  - nested: 1

## Examples

### Example 1

- generator: `array_order`
- input: `["\u0007\u001f�>ÿ 😀", "𐀀&"]`

Canonical per implementation:
- **python** (len 38, sha ea24f7b7b75b7567...):

  ```
  ["\u0007\u001f�>ÿ 😀","𐀀&"]
  ```
- **go** (len 41, sha c2e0cbf0a7522a38...):

  ```
  ["\u0007\u001f�>ÿ\u2028😀","𐀀&"]
  ```
- **rust** (len 38, sha ea24f7b7b75b7567...):

  ```
  ["\u0007\u001f�>ÿ 😀","𐀀&"]
  ```

### Example 2

- generator: `nested`
- input: `[{">\u0007<": 3.14159, "tag": 3}, 0.30000000000000004, "￿𐀀￿😀\\ "]`

Canonical per implementation:
- **python** (len 73, sha dfd8d4dbfc0c744c...):

  ```
  [{"tag":3,">\u0007<":3.14159},0.30000000000000004,"￿𐀀￿😀\\ "]
  ```
- **go** (len 76, sha 0a51f0bf3b268dfd...):

  ```
  [{"tag":3,">\u0007<":3.14159},0.30000000000000004,"￿𐀀￿😀\\\u2028"]
  ```
- **rust** (len 73, sha dfd8d4dbfc0c744c...):

  ```
  [{"tag":3,">\u0007<":3.14159},0.30000000000000004,"￿𐀀￿😀\\ "]
  ```

### Example 3

- generator: `object_unicode_keys`
- input: `{"Ā ": 550, " ￿􏿿\\": 671, " /߿&": -194, "߿￿&": 872, "\u0007😀ࠀ\u001f𐀀": -284}`

Canonical per implementation:
- **python** (len 90, sha ff4bb7a9390e3872...):

  ```
  {"\u0007😀ࠀ\u001f𐀀":-284," /߿&":-194,"Ā ":550,"߿￿&":872," ￿􏿿\\":671}
  ```
- **go** (len 96, sha a3d91cf74e691935...):

  ```
  {"\u0007😀ࠀ\u001f𐀀":-284," /߿&":-194,"Ā\u2028":550,"߿￿&":872,"\u2028￿􏿿\\":671}
  ```
- **rust** (len 90, sha ff4bb7a9390e3872...):

  ```
  {"\u0007😀ࠀ\u001f𐀀":-284," /߿&":-194,"Ā ":550,"߿￿&":872," ￿􏿿\\":671}
  ```
