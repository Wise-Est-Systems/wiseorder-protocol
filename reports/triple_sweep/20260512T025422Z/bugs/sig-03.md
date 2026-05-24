# Disagreement signature 3

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-U+2028`

**Count:** 28

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-U+2028

**Length pattern:** longest:go,shortest:python

**By generator:**
  - unicode_string: 16
  - array_order: 4
  - object_unicode_keys: 3
  - mixed_object: 3
  - nested: 2

## Examples

### Example 1

- generator: `unicode_string`
- input: `"> "`

Canonical per implementation:
- **python** (len 6, sha 1e74f8b712486a10...):

  ```
  "> "
  ```
- **go** (len 9, sha dd2347c0394b8410...):

  ```
  ">\u2028"
  ```
- **rust** (len 6, sha 1e74f8b712486a10...):

  ```
  "> "
  ```

### Example 2

- generator: `array_order`
- input: `[-71, "ÿ߿� \\ ￿ÿ", 5e-324]`

Canonical per implementation:
- **python** (len 33, sha 38be286b22611fa5...):

  ```
  [-71,"ÿ߿� \\ ￿ÿ",5e-324]
  ```
- **go** (len 36, sha dd3d7f5a37c15ce9...):

  ```
  [-71,"ÿ߿� \\\u2028￿ÿ",5e-324]
  ```
- **rust** (len 33, sha 38be286b22611fa5...):

  ```
  [-71,"ÿ߿� \\ ￿ÿ",5e-324]
  ```

### Example 3

- generator: `array_order`
- input: `[28, "/ "]`

Canonical per implementation:
- **python** (len 11, sha 31942934dfc8517e...):

  ```
  [28,"/ "]
  ```
- **go** (len 14, sha d0f29a9718c014df...):

  ```
  [28,"/\u2028"]
  ```
- **rust** (len 11, sha 31942934dfc8517e...):

  ```
  [28,"/ "]
  ```
