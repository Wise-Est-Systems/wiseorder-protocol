# Disagreement signature 85

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-C1-control,contains-SMP,contains-U+2029`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-C1-control, contains-SMP, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{">�": 547, "/􏿿߿ ": -769, "\u0000ࠀ𐀀": 216, ">>􏿿": -906, "ÿ\\߿\\\\>": 51}`

Canonical per implementation:
- **python** (len 85, sha 4b46b4a9755efc0a...):

  ```
  {"\u0000ࠀ𐀀":216,"/􏿿߿ ":-769,">>􏿿":-906,">�":547,"ÿ\\߿\\\\>":51}
  ```
- **go** (len 88, sha f377e4f17f6f87eb...):

  ```
  {"\u0000ࠀ𐀀":216,"/􏿿߿\u2029":-769,">>􏿿":-906,">�":547,"ÿ\\߿\\\\>":51}
  ```
- **rust** (len 85, sha 4b46b4a9755efc0a...):

  ```
  {"\u0000ࠀ𐀀":216,"/􏿿߿ ":-769,">>􏿿":-906,">�":547,"ÿ\\߿\\\\>":51}
  ```
