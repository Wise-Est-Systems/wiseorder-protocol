# Disagreement signature 43

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-DEL,contains-U+2028`

**Count:** 11

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-DEL, contains-U+2028

**Length pattern:** longest:go,shortest:python

**By generator:**
  - unicode_string: 5
  - array_order: 2
  - object_unicode_keys: 2
  - nested: 1
  - mixed_object: 1

## Examples

### Example 1

- generator: `array_order`
- input: `[-1, 2.2250738585072014e-308, "߿& ߿\u0007", "\u0007>ÿÿ\"\" ", 3.14159, 0.2, -23]`

Canonical per implementation:
- **python** (len 81, sha 70e93c914bc034a7...):

  ```
  [-1,2.2250738585072014e-308,"߿& ߿\u0007","\u0007>ÿÿ\"\" ",3.14159,0.2,-23]
  ```
- **go** (len 84, sha 1bf95cbd1376f7bd...):

  ```
  [-1,2.2250738585072014e-308,"߿& ߿\u0007","\u0007>ÿÿ\"\"\u2028",3.14159,0.2,-23]
  ```
- **rust** (len 81, sha 70e93c914bc034a7...):

  ```
  [-1,2.2250738585072014e-308,"߿& ߿\u0007","\u0007>ÿÿ\"\" ",3.14159,0.2,-23]
  ```

### Example 2

- generator: `unicode_string`
- input: `" \u0000<\u001fࠀ\u001f�"`

Canonical per implementation:
- **python** (len 31, sha 5166ff9e8ab06608...):

  ```
  " \u0000<\u001fࠀ\u001f�"
  ```
- **go** (len 34, sha da94e5799c01fe4a...):

  ```
  "\u2028\u0000<\u001fࠀ\u001f�"
  ```
- **rust** (len 31, sha 5166ff9e8ab06608...):

  ```
  " \u0000<\u001fࠀ\u001f�"
  ```

### Example 3

- generator: `unicode_string`
- input: `"\u0000<Ā "`

Canonical per implementation:
- **python** (len 15, sha faf7459af5b21ac4...):

  ```
  "\u0000<Ā "
  ```
- **go** (len 18, sha 3756af36607c365e...):

  ```
  "\u0000<Ā\u2028"
  ```
- **rust** (len 15, sha faf7459af5b21ac4...):

  ```
  "\u0000<Ā "
  ```
