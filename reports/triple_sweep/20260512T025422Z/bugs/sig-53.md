# Disagreement signature 53

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-C1-control,contains-SMP,contains-U+2028`

**Count:** 10

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-C1-control, contains-SMP, contains-U+2028

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 5
  - array_order: 3
  - object_unicode_keys: 2

## Examples

### Example 1

- generator: `nested`
- input: `{"߿>𐀀\"": {"\u0000\u001fĀ": {"<": {" \\ࠀ/": 2147483647, "tag": 9}, "tag": 0}, "tag": 4}, "tag": 5}`

Canonical per implementation:
- **python** (len 97, sha 175c0102aea796c4...):

  ```
  {"tag":5,"߿>𐀀\"":{"\u0000\u001fĀ":{"<":{"tag":9," \\ࠀ/":2147483647},"tag":0},"tag":4}}
  ```
- **go** (len 100, sha a2113effa6a81120...):

  ```
  {"tag":5,"߿>𐀀\"":{"\u0000\u001fĀ":{"<":{"tag":9,"\u2028\\ࠀ/":2147483647},"tag":0},"tag":4}}
  ```
- **rust** (len 97, sha 175c0102aea796c4...):

  ```
  {"tag":5,"߿>𐀀\"":{"\u0000\u001fĀ":{"<":{"tag":9," \\ࠀ/":2147483647},"tag":0},"tag":4}}
  ```

### Example 2

- generator: `array_order`
- input: `[75, "􏿿<>􏿿\u0000", "􏿿<𐀀\u0007Ā&\u001f\u001f", "\"￿<\"&", "￿􏿿\\􏿿 𐀀 "]`

Canonical per implementation:
- **python** (len 96, sha e4a75fe4b7560461...):

  ```
  [75,"􏿿<>􏿿\u0000","􏿿<𐀀\u0007Ā&\u001f\u001f","\"￿<\"&","￿􏿿\\􏿿 𐀀 "]
  ```
- **go** (len 99, sha a75dcaf56c7dcf4d...):

  ```
  [75,"􏿿<>􏿿\u0000","􏿿<𐀀\u0007Ā&\u001f\u001f","\"￿<\"&","￿􏿿\\􏿿 𐀀\u2028"]
  ```
- **rust** (len 96, sha e4a75fe4b7560461...):

  ```
  [75,"􏿿<>􏿿\u0000","􏿿<𐀀\u0007Ā&\u001f\u001f","\"￿<\"&","￿􏿿\\􏿿 𐀀 "]
  ```

### Example 3

- generator: `nested`
- input: `{"߿ÿ𐀀\"&􏿿 ": {" �\u001f ": 5e-324, "tag": 3}, "tag": 3}`

Canonical per implementation:
- **python** (len 67, sha 5faa3fbc485e3ca8...):

  ```
  {"tag":3,"߿ÿ𐀀\"&􏿿 ":{"tag":3," �\u001f ":5e-324}}
  ```
- **go** (len 73, sha 416f91cd7c82d7a3...):

  ```
  {"tag":3,"߿ÿ𐀀\"&􏿿 ":{"tag":3,"\u2028�\u001f\u2028":5e-324}}
  ```
- **rust** (len 67, sha 5faa3fbc485e3ca8...):

  ```
  {"tag":3,"߿ÿ𐀀\"&􏿿 ":{"tag":3," �\u001f ":5e-324}}
  ```
