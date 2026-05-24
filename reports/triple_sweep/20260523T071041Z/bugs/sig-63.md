# Disagreement signature 63

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-DEL,contains-SMP,contains-U+2028,contains-emoji`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-DEL, contains-SMP, contains-U+2028, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"\\\u0000\u0007\u001f\u0000￿": 618, "/\"😀𐀀߿Ā": 615, "\\߿<ÿ&\\<": -674, " ": 901}`

Canonical per implementation:
- **python** (len 89, sha 668e8fcbc97a4acd...):

  ```
  {"/\"😀𐀀߿Ā":615,"\\\u0000\u0007\u001f\u0000￿":618,"\\߿<ÿ&\\<":-674," ":901}
  ```
- **go** (len 92, sha 26899816994a2afc...):

  ```
  {"/\"😀𐀀߿Ā":615,"\\\u0000\u0007\u001f\u0000￿":618,"\\߿<ÿ&\\<":-674,"\u2028":901}
  ```
- **rust** (len 89, sha 668e8fcbc97a4acd...):

  ```
  {"/\"😀𐀀߿Ā":615,"\\\u0000\u0007\u001f\u0000￿":618,"\\߿<ÿ&\\<":-674," ":901}
  ```
