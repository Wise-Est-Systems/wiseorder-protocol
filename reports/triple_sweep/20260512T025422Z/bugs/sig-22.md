# Disagreement signature 22

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-DEL,contains-SMP,contains-U+2029`

**Count:** 15

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-DEL, contains-SMP, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 8
  - nested: 5
  - unicode_string: 2

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"\"<>￿�\u0007": 379, "\u001f": 72, "߿�￿߿�\\": 445, "&𐀀�": 294, ">\u0007𐀀": 924, "\u001f \"\u0007\u0000ࠀ <": -71}`

Canonical per implementation:
- **python** (len 127, sha 5d67bbc6f63ebe98...):

  ```
  {"\u001f":72,"\u001f \"\u0007\u0000ࠀ <":-71,"\"<>￿�\u0007":379,"&𐀀�":294,">\u0007𐀀":924,"߿�￿߿�\\":445}
  ```
- **go** (len 130, sha 8d8c721ee375062e...):

  ```
  {"\u001f":72,"\u001f \"\u0007\u0000ࠀ\u2029<":-71,"\"<>￿�\u0007":379,"&𐀀�":294,">\u0007𐀀":924,"߿�￿߿�\\":445}
  ```
- **rust** (len 127, sha 5d67bbc6f63ebe98...):

  ```
  {"\u001f":72,"\u001f \"\u0007\u0000ࠀ <":-71,"\"<>￿�\u0007":379,"&𐀀�":294,">\u0007𐀀":924,"߿�￿߿�\\":445}
  ```

### Example 2

- generator: `object_unicode_keys`
- input: `{" <\u001f>": 545, "\u001f<\u001f": 960, "\u0000": -783, "/\u0007\u0000􏿿": -174}`

Canonical per implementation:
- **python** (len 80, sha c2e4c99062501045...):

  ```
  {"\u0000":-783,"\u001f<\u001f":960,"/\u0007\u0000􏿿":-174," <\u001f>":545}
  ```
- **go** (len 83, sha 7596e7aa44a5df60...):

  ```
  {"\u0000":-783,"\u001f<\u001f":960,"/\u0007\u0000􏿿":-174,"\u2029<\u001f>":545}
  ```
- **rust** (len 80, sha c2e4c99062501045...):

  ```
  {"\u0000":-783,"\u001f<\u001f":960,"/\u0007\u0000􏿿":-174," <\u001f>":545}
  ```

### Example 3

- generator: `object_unicode_keys`
- input: `{"&\u0000ÿ\u0007 ": -821, "𐀀𐀀": -501, "<": -371, "߿�߿𐀀 Ā￿": 289}`

Canonical per implementation:
- **python** (len 80, sha 152107f2df82432f...):

  ```
  {"&\u0000ÿ\u0007 ":-821,"<":-371,"߿�߿𐀀 Ā￿":289,"𐀀𐀀":-501}
  ```
- **go** (len 86, sha fa104a062de90e2e...):

  ```
  {"&\u0000ÿ\u0007\u2029":-821,"<":-371,"߿�߿𐀀\u2029Ā￿":289,"𐀀𐀀":-501}
  ```
- **rust** (len 80, sha 152107f2df82432f...):

  ```
  {"&\u0000ÿ\u0007 ":-821,"<":-371,"߿�߿𐀀 Ā￿":289,"𐀀𐀀":-501}
  ```
