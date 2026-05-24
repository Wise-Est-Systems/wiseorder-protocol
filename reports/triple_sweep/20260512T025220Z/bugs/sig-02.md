# Disagreement signature 2

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-SMP,contains-U+2028`

**Count:** 2

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-SMP, contains-U+2028

**Length pattern:** longest:go,shortest:python

**By generator:**
  - unicode_string: 1
  - object_unicode_keys: 1

## Examples

### Example 1

- generator: `unicode_string`
- input: `" \\􏿿 \"ÿ�"`

Canonical per implementation:
- **python** (len 19, sha ceb2a877668a15d9...):

  ```
  " \\􏿿 \"ÿ�"
  ```
- **go** (len 22, sha 772e606df9c3af4f...):

  ```
  "\u2028\\􏿿 \"ÿ�"
  ```
- **rust** (len 19, sha ceb2a877668a15d9...):

  ```
  " \\􏿿 \"ÿ�"
  ```

### Example 2

- generator: `object_unicode_keys`
- input: `{"&\" ": -254, "𐀀 ": 115}`

Canonical per implementation:
- **python** (len 27, sha ea2b25e3993f8ea6...):

  ```
  {"&\" ":-254,"𐀀 ":115}
  ```
- **go** (len 30, sha 47008fe41f6197e9...):

  ```
  {"&\"\u2028":-254,"𐀀 ":115}
  ```
- **rust** (len 27, sha ea2b25e3993f8ea6...):

  ```
  {"&\" ":-254,"𐀀 ":115}
  ```
