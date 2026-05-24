# Disagreement signature 98

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-C1-control,contains-DEL,contains-SMP,contains-U+2028,contains-bigint>2^53,contains-emoji`

**Count:** 5

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-C1-control, contains-DEL, contains-SMP, contains-U+2028, contains-bigint>2^53, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 4
  - array_order: 1

## Examples

### Example 1

- generator: `nested`
- input: `[[{" ": 0.30000000000000004, "tag": 7}, 1000000000000000.0, "😀ࠀ<𐀀Ā>"], 9223372036854775807, "\u0007Ā<😀"]`

Canonical per implementation:
- **python** (len 115, sha ad30f0395ffed215...):

  ```
  [[{"tag":7," ":0.30000000000000004},1000000000000000.0,"😀ࠀ<𐀀Ā>"],9223372036854775807,"\u0007Ā<😀"]
  ```
- **go** (len 118, sha 886bfadc01776e32...):

  ```
  [[{"tag":7,"\u2028":0.30000000000000004},1000000000000000.0,"😀ࠀ<𐀀Ā>"],9223372036854775807,"\u0007Ā<😀"]
  ```
- **rust** (len 115, sha ad30f0395ffed215...):

  ```
  [[{"tag":7," ":0.30000000000000004},1000000000000000.0,"😀ࠀ<𐀀Ā>"],9223372036854775807,"\u0007Ā<😀"]
  ```

### Example 2

- generator: `array_order`
- input: `[" \"\u001f􏿿😀Ā", "&ࠀ\\😀", 9007199254740993, 0.3333333333333333, "/", -1, 84, "\u001f< "]`

Canonical per implementation:
- **python** (len 100, sha 6fbf9802c8c1d0d9...):

  ```
  [" \"\u001f􏿿😀Ā","&ࠀ\\😀",9007199254740993,0.3333333333333333,"/",-1,84,"\u001f< "]
  ```
- **go** (len 106, sha 51dd6bba778634c7...):

  ```
  ["\u2028\"\u001f􏿿😀Ā","&ࠀ\\😀",9007199254740993,0.3333333333333333,"/",-1,84,"\u001f<\u2028"]
  ```
- **rust** (len 100, sha 6fbf9802c8c1d0d9...):

  ```
  [" \"\u001f􏿿😀Ā","&ࠀ\\😀",9007199254740993,0.3333333333333333,"/",-1,84,"\u001f< "]
  ```

### Example 3

- generator: `nested`
- input: `{" ߿߿>𐀀߿": {"\u0000": [[[1e+100, 9007199254740993, "􏿿😀߿\"􏿿"], -0.0, "\u001f<􏿿߿<"], 9223372036854775807, "￿>"], "tag": 6}, "tag": 5}`

Canonical per implementation:
- **python** (len 149, sha 661b7d575b685f87...):

  ```
  {"tag":5," ߿߿>𐀀߿":{"\u0000":[[[1e+100,9007199254740993,"􏿿😀߿\"􏿿"],-0.0,"\u001f<􏿿߿<"],9223372036854775807,"￿>"],"tag":6}}
  ```
- **go** (len 152, sha 300ab1a125d0559c...):

  ```
  {"tag":5,"\u2028߿߿>𐀀߿":{"\u0000":[[[1e+100,9007199254740993,"􏿿😀߿\"􏿿"],-0.0,"\u001f<􏿿߿<"],9223372036854775807,"￿>"],"tag":6}}
  ```
- **rust** (len 149, sha 661b7d575b685f87...):

  ```
  {"tag":5," ߿߿>𐀀߿":{"\u0000":[[[1e+100,9007199254740993,"􏿿😀߿\"􏿿"],-0.0,"\u001f<􏿿߿<"],9223372036854775807,"￿>"],"tag":6}}
  ```
