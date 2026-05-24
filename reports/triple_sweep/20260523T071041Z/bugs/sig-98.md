# Disagreement signature 98

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-C1-control,contains-DEL,contains-SMP,contains-U+2029`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-C1-control, contains-DEL, contains-SMP, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"\u0000\u0000￿": 473, "\"Ā􏿿": 587, "\u0007߿\"￿߿": -61, "\u001f\u0007\"\u0007 ÿ/": 231}`

Canonical per implementation:
- **python** (len 98, sha 072adc331f267b30...):

  ```
  {"\u0000\u0000￿":473,"\u0007߿\"￿߿":-61,"\u001f\u0007\"\u0007 ÿ/":231,"\"Ā􏿿":587}
  ```
- **go** (len 101, sha 518aeb873da9c067...):

  ```
  {"\u0000\u0000￿":473,"\u0007߿\"￿߿":-61,"\u001f\u0007\"\u0007\u2029ÿ/":231,"\"Ā􏿿":587}
  ```
- **rust** (len 98, sha 072adc331f267b30...):

  ```
  {"\u0000\u0000￿":473,"\u0007߿\"￿߿":-61,"\u001f\u0007\"\u0007 ÿ/":231,"\"Ā􏿿":587}
  ```
