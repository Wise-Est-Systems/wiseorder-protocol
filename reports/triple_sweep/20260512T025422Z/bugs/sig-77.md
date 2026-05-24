# Disagreement signature 77

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-C1-control,contains-DEL,contains-U+2028`

**Count:** 6

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-C1-control, contains-DEL, contains-U+2028

**Length pattern:** longest:go,shortest:python

**By generator:**
  - array_order: 3
  - unicode_string: 1
  - mixed_object: 1
  - object_unicode_keys: 1

## Examples

### Example 1

- generator: `unicode_string`
- input: `" ߿\u001f"`

Canonical per implementation:
- **python** (len 16, sha 3999272a9229f870...):

  ```
  " ߿\u001f"
  ```
- **go** (len 19, sha a51ef72d6483eb7b...):

  ```
  "\u2028߿\u001f"
  ```
- **rust** (len 16, sha 3999272a9229f870...):

  ```
  " ߿\u001f"
  ```

### Example 2

- generator: `array_order`
- input: `[-39, 28, -19, -62, "Ā ÿ\u0007\u001f", -56, 56]`

Canonical per implementation:
- **python** (len 48, sha bcbc1a84d55603d3...):

  ```
  [-39,28,-19,-62,"Ā ÿ\u0007\u001f",-56,56]
  ```
- **go** (len 51, sha 3460620f43975e09...):

  ```
  [-39,28,-19,-62,"Ā\u2028ÿ\u0007\u001f",-56,56]
  ```
- **rust** (len 48, sha bcbc1a84d55603d3...):

  ```
  [-39,28,-19,-62,"Ā ÿ\u0007\u001f",-56,56]
  ```

### Example 3

- generator: `array_order`
- input: `["  &\u0000", "Āࠀࠀ", "߿", "Ā \u0000 ￿", "\\\"\u0000&߿\\", 0.3333333333333333, -57, -36]`

Canonical per implementation:
- **python** (len 102, sha 738e7a3d5601e2d8...):

  ```
  ["  &\u0000","Āࠀࠀ","߿","Ā \u0000 ￿","\\\"\u0000&߿\\",0.3333333333333333,-57,-36]
  ```
- **go** (len 111, sha 92aa625da53fae4d...):

  ```
  [" \u2028&\u0000","Āࠀࠀ","߿","Ā\u2028\u0000\u2028￿","\\\"\u0000&߿\\",0.3333333333333333,-57,-36]
  ```
- **rust** (len 102, sha 738e7a3d5601e2d8...):

  ```
  ["  &\u0000","Āࠀࠀ","߿","Ā \u0000 ￿","\\\"\u0000&߿\\",0.3333333333333333,-57,-36]
  ```
