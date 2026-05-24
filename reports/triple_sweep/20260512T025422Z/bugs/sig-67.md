# Disagreement signature 67

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-SMP,contains-U+2028,contains-emoji`

**Count:** 7

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-SMP, contains-U+2028, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - unicode_string: 3
  - array_order: 2
  - nested: 1
  - mixed_object: 1

## Examples

### Example 1

- generator: `nested`
- input: `[{"􏿿": 2.718281828459045, "tag": 9}, 3.14159, "< 😀ࠀ\\"]`

Canonical per implementation:
- **python** (len 60, sha 54b2be842607e3cb...):

  ```
  [{"tag":9,"􏿿":2.718281828459045},3.14159,"< 😀ࠀ\\"]
  ```
- **go** (len 63, sha c541478e873cc0ad...):

  ```
  [{"tag":9,"􏿿":2.718281828459045},3.14159,"<\u2028😀ࠀ\\"]
  ```
- **rust** (len 60, sha 54b2be842607e3cb...):

  ```
  [{"tag":9,"􏿿":2.718281828459045},3.14159,"< 😀ࠀ\\"]
  ```

### Example 2

- generator: `unicode_string`
- input: `"😀􏿿 "`

Canonical per implementation:
- **python** (len 13, sha a3bfa00e5dfc465a...):

  ```
  "😀􏿿 "
  ```
- **go** (len 16, sha 928598dea1c10dcb...):

  ```
  "😀􏿿\u2028"
  ```
- **rust** (len 13, sha a3bfa00e5dfc465a...):

  ```
  "😀􏿿 "
  ```

### Example 3

- generator: `mixed_object`
- input: `{"k2": [], "k1": 0.0, "k0": " \\𐀀\" 😀𐀀"}`

Canonical per implementation:
- **python** (len 46, sha e3d1041a3e86604f...):

  ```
  {"k0":" \\𐀀\" 😀𐀀","k1":0.0,"k2":[]}
  ```
- **go** (len 49, sha f12f447f3566ebce...):

  ```
  {"k0":"\u2028\\𐀀\" 😀𐀀","k1":0.0,"k2":[]}
  ```
- **rust** (len 46, sha e3d1041a3e86604f...):

  ```
  {"k0":" \\𐀀\" 😀𐀀","k1":0.0,"k2":[]}
  ```
