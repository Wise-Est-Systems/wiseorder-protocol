# Disagreement signature 97

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-C1-control,contains-SMP,contains-U+2028,contains-U+2029,contains-bigint>2^53,contains-emoji`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-C1-control, contains-SMP, contains-U+2028, contains-U+2029, contains-bigint>2^53, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 1

## Examples

### Example 1

- generator: `nested`
- input: `[[[{" ĀĀ􏿿\u001f/ ": {"\u0000": 9007199254740993, "tag": 3}, "tag": 1}, 0.3, "Ā\\/\u001f😀\u0007"], 5e-324, "\u001f "], 0.3, "𐀀😀"]`

Canonical per implementation:
- **python** (len 139, sha f8f9473bed3dd88c...):

  ```
  [[[{"tag":1," ĀĀ􏿿\u001f/ ":{"\u0000":9007199254740993,"tag":3}},0.3,"Ā\\/\u001f😀\u0007"],5e-324,"\u001f "],0.3,"𐀀😀"]
  ```
- **go** (len 148, sha 06978b4040f0e97e...):

  ```
  [[[{"tag":1,"\u2028ĀĀ􏿿\u001f/\u2029":{"\u0000":9007199254740993,"tag":3}},0.3,"Ā\\/\u001f😀\u0007"],5e-324,"\u001f\u2029"],0.3,"𐀀😀"]
  ```
- **rust** (len 139, sha f8f9473bed3dd88c...):

  ```
  [[[{"tag":1," ĀĀ􏿿\u001f/ ":{"\u0000":9007199254740993,"tag":3}},0.3,"Ā\\/\u001f😀\u0007"],5e-324,"\u001f "],0.3,"𐀀😀"]
  ```
