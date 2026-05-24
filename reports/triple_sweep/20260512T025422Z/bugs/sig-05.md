# Disagreement signature 5

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-SMP,contains-U+2028`

**Count:** 24

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-SMP, contains-U+2028

**Length pattern:** longest:go,shortest:python

**By generator:**
  - unicode_string: 8
  - object_unicode_keys: 7
  - nested: 5
  - array_order: 3
  - mixed_object: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"􏿿  ࠀ\u0007": -944, "\u001f>\u001fࠀ\"": 233, "ÿ/\u0007": -470}`

Canonical per implementation:
- **python** (len 68, sha a4ea25b46721f228...):

  ```
  {"\u001f>\u001fࠀ\"":233,"ÿ/\u0007":-470,"􏿿  ࠀ\u0007":-944}
  ```
- **go** (len 71, sha 71a1497283e0c91e...):

  ```
  {"\u001f>\u001fࠀ\"":233,"ÿ/\u0007":-470,"􏿿 \u2028ࠀ\u0007":-944}
  ```
- **rust** (len 68, sha a4ea25b46721f228...):

  ```
  {"\u001f>\u001fࠀ\"":233,"ÿ/\u0007":-470,"􏿿  ࠀ\u0007":-944}
  ```

### Example 2

- generator: `unicode_string`
- input: `"/\u0007𐀀￿<> ÿ"`

Canonical per implementation:
- **python** (len 23, sha 5d0014ed79404daf...):

  ```
  "/\u0007𐀀￿<> ÿ"
  ```
- **go** (len 26, sha d644fecc60a8e882...):

  ```
  "/\u0007𐀀￿<>\u2028ÿ"
  ```
- **rust** (len 23, sha 5d0014ed79404daf...):

  ```
  "/\u0007𐀀￿<> ÿ"
  ```

### Example 3

- generator: `unicode_string`
- input: `"𐀀􏿿𐀀>\u0007 ࠀ"`

Canonical per implementation:
- **python** (len 27, sha f2eadc4e05ad69a8...):

  ```
  "𐀀􏿿𐀀>\u0007 ࠀ"
  ```
- **go** (len 30, sha 69d9a4e1e40a541c...):

  ```
  "𐀀􏿿𐀀>\u0007\u2028ࠀ"
  ```
- **rust** (len 27, sha f2eadc4e05ad69a8...):

  ```
  "𐀀􏿿𐀀>\u0007 ࠀ"
  ```
