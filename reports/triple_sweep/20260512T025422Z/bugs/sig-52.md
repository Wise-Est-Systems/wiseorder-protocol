# Disagreement signature 52

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-C1-control,contains-U+2029`

**Count:** 10

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-C1-control, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - unicode_string: 5
  - object_unicode_keys: 2
  - array_order: 1
  - mixed_object: 1
  - nested: 1

## Examples

### Example 1

- generator: `unicode_string`
- input: `"\u001f\u0000 "`

Canonical per implementation:
- **python** (len 21, sha 4720a9833ef5910f...):

  ```
  "\u001f\u0000 "
  ```
- **go** (len 24, sha 29f4356b026e23df...):

  ```
  "\u001f\u0000\u2029"
  ```
- **rust** (len 21, sha 4720a9833ef5910f...):

  ```
  "\u001f\u0000 "
  ```

### Example 2

- generator: `unicode_string`
- input: `"/&�< \u0007ÿ"`

Canonical per implementation:
- **python** (len 21, sha 3a221a7f9612d6d9...):

  ```
  "/&�< \u0007ÿ"
  ```
- **go** (len 24, sha 98e3898c6cb439ad...):

  ```
  "/&�<\u2029\u0007ÿ"
  ```
- **rust** (len 21, sha 3a221a7f9612d6d9...):

  ```
  "/&�< \u0007ÿ"
  ```

### Example 3

- generator: `unicode_string`
- input: `"\u0000\"�߿ ࠀࠀ"`

Canonical per implementation:
- **python** (len 26, sha 9647cba0166d1525...):

  ```
  "\u0000\"�߿ ࠀࠀ"
  ```
- **go** (len 29, sha b8ad6850f1e1446b...):

  ```
  "\u0000\"�߿\u2029ࠀࠀ"
  ```
- **rust** (len 26, sha 9647cba0166d1525...):

  ```
  "\u0000\"�߿ ࠀࠀ"
  ```
