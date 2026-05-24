# Disagreement signature 23

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-SMP,contains-U+2028`

**Count:** 2

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-SMP, contains-U+2028

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 1
  - object_unicode_keys: 1

## Examples

### Example 1

- generator: `nested`
- input: `[{"𐀀\"�\" 𐀀\u001fÿ": 9007199254740991, "tag": 2}, 2.2250738585072014e-308, " ￿𐀀\u0007�\\ "]`

Canonical per implementation:
- **python** (len 104, sha 5dce1748291bcd2a...):

  ```
  [{"tag":2,"𐀀\"�\" 𐀀\u001fÿ":9007199254740991},2.2250738585072014e-308," ￿𐀀\u0007�\\ "]
  ```
- **go** (len 107, sha ac4b0db3db21a065...):

  ```
  [{"tag":2,"𐀀\"�\"\u2028𐀀\u001fÿ":9007199254740991},2.2250738585072014e-308," ￿𐀀\u0007�\\ "]
  ```
- **rust** (len 104, sha 5dce1748291bcd2a...):

  ```
  [{"tag":2,"𐀀\"�\" 𐀀\u001fÿ":9007199254740991},2.2250738585072014e-308," ￿𐀀\u0007�\\ "]
  ```

### Example 2

- generator: `object_unicode_keys`
- input: `{"\u001f&\" 𐀀>>": -525, "/\\􏿿Ā ￿ ߿": -67}`

Canonical per implementation:
- **python** (len 50, sha 24c55451bea40db2...):

  ```
  {"\u001f&\" 𐀀>>":-525,"/\\􏿿Ā ￿ ߿":-67}
  ```
- **go** (len 53, sha ad8b5a93115418fe...):

  ```
  {"\u001f&\"\u2028𐀀>>":-525,"/\\􏿿Ā ￿ ߿":-67}
  ```
- **rust** (len 50, sha 24c55451bea40db2...):

  ```
  {"\u001f&\" 𐀀>>":-525,"/\\􏿿Ā ￿ ߿":-67}
  ```
