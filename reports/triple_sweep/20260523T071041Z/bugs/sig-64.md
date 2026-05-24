# Disagreement signature 64

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-C1-control,contains-SMP,contains-U+2029,contains-emoji`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-C1-control, contains-SMP, contains-U+2029, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 1

## Examples

### Example 1

- generator: `nested`
- input: `{"\u0000\\ ࠀ": [[[{"ÿ>\u0007<ÿ􏿿": 0, "tag": 0}, 2.718281828459045, "ࠀ&"], 0.3, "\"￿\"😀\u0000\"\\ÿ"], 0.30000000000000004, "􏿿😀Ā"], "tag": 8}`

Canonical per implementation:
- **python** (len 153, sha 7833876e1445d50d...):

  ```
  {"tag":8,"\u0000\\ ࠀ":[[[{"tag":0,"ÿ>\u0007<ÿ􏿿":0},2.718281828459045,"ࠀ&"],0.3,"\"￿\"😀\u0000\"\\ÿ"],0.30000000000000004,"􏿿😀Ā"]}
  ```
- **go** (len 156, sha 19c5632dd5b13d83...):

  ```
  {"tag":8,"\u0000\\\u2029ࠀ":[[[{"tag":0,"ÿ>\u0007<ÿ􏿿":0},2.718281828459045,"ࠀ&"],0.3,"\"￿\"😀\u0000\"\\ÿ"],0.30000000000000004,"􏿿😀Ā"]}
  ```
- **rust** (len 153, sha 7833876e1445d50d...):

  ```
  {"tag":8,"\u0000\\ ࠀ":[[[{"tag":0,"ÿ>\u0007<ÿ􏿿":0},2.718281828459045,"ࠀ&"],0.3,"\"￿\"😀\u0000\"\\ÿ"],0.30000000000000004,"􏿿😀Ā"]}
  ```
