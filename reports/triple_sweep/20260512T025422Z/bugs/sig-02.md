# Disagreement signature 2

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-U+2029`

**Count:** 31

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - unicode_string: 12
  - object_unicode_keys: 8
  - array_order: 6
  - mixed_object: 3
  - nested: 2

## Examples

### Example 1

- generator: `unicode_string`
- input: `"&&/� <\u0000Ā"`

Canonical per implementation:
- **python** (len 20, sha 3d62ca50ba392b97...):

  ```
  "&&/� <\u0000Ā"
  ```
- **go** (len 23, sha 158c3caaa76c2c39...):

  ```
  "&&/�\u2029<\u0000Ā"
  ```
- **rust** (len 20, sha 3d62ca50ba392b97...):

  ```
  "&&/� <\u0000Ā"
  ```

### Example 2

- generator: `unicode_string`
- input: `" \u0000/"`

Canonical per implementation:
- **python** (len 12, sha dc994ed5cbeb362a...):

  ```
  " \u0000/"
  ```
- **go** (len 15, sha 950e87619017195e...):

  ```
  "\u2029\u0000/"
  ```
- **rust** (len 12, sha dc994ed5cbeb362a...):

  ```
  " \u0000/"
  ```

### Example 3

- generator: `array_order`
- input: `[-87, -52, -2.5, 2.718281828459045, "& \u0000￿", 0.0]`

Canonical per implementation:
- **python** (len 52, sha 10d8de8422f0639b...):

  ```
  [-87,-52,-2.5,2.718281828459045,"& \u0000￿",0.0]
  ```
- **go** (len 55, sha 49ba4b7180c7bfa1...):

  ```
  [-87,-52,-2.5,2.718281828459045,"&\u2029\u0000￿",0.0]
  ```
- **rust** (len 52, sha 10d8de8422f0639b...):

  ```
  [-87,-52,-2.5,2.718281828459045,"& \u0000￿",0.0]
  ```
