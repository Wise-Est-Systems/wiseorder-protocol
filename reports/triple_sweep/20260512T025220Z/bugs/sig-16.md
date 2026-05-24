# Disagreement signature 16

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-SMP,contains-U+2028,contains-bigint>2^53`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-SMP, contains-U+2028, contains-bigint>2^53

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 1

## Examples

### Example 1

- generator: `nested`
- input: `[{"Ā": {"􏿿&&\u001f": [[0.3, 9007199254740993, "߿ÿĀĀ<<Ā"], 1e+16, "\u0000\u0000<"], "tag": 9}, "tag": 6}, 1e+16, "\u001f  /􏿿/ÿ"]`

Canonical per implementation:
- **python** (len 132, sha 1f704d5feda099b8...):

  ```
  [{"tag":6,"Ā":{"tag":9,"􏿿&&\u001f":[[0.3,9007199254740993,"߿ÿĀĀ<<Ā"],1e+16,"\u0000\u0000<"]}},1e+16,"\u001f  /􏿿/ÿ"]
  ```
- **go** (len 138, sha 5d02cb90543aa1a2...):

  ```
  [{"tag":6,"Ā":{"tag":9,"􏿿&&\u001f":[[0.3,9007199254740993,"߿ÿĀĀ<<Ā"],1e+16,"\u0000\u0000<"]}},1e+16,"\u001f\u2028\u2028/􏿿/ÿ"]
  ```
- **rust** (len 132, sha 1f704d5feda099b8...):

  ```
  [{"tag":6,"Ā":{"tag":9,"􏿿&&\u001f":[[0.3,9007199254740993,"߿ÿĀĀ<<Ā"],1e+16,"\u0000\u0000<"]}},1e+16,"\u001f  /􏿿/ÿ"]
  ```
