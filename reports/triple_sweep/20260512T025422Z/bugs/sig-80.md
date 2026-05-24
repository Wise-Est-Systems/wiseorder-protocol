# Disagreement signature 80

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-C1-control,contains-SMP,contains-U+2028,contains-emoji`

**Count:** 6

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-C1-control, contains-SMP, contains-U+2028, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 6

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{" ": -609, "\u0000\u0007": 825, "􏿿&\u0000ÿ": 894, "𐀀😀􏿿>": -520}`

Canonical per implementation:
- **python** (len 74, sha fe9fcfff757d45ee...):

  ```
  {"\u0000\u0007":825,"􏿿&\u0000ÿ":894," ":-609,"𐀀😀􏿿>":-520}
  ```
- **go** (len 77, sha 0ab9c57e73b66be3...):

  ```
  {"\u0000\u0007":825,"􏿿&\u0000ÿ":894,"\u2028":-609,"𐀀😀􏿿>":-520}
  ```
- **rust** (len 74, sha fe9fcfff757d45ee...):

  ```
  {"\u0000\u0007":825,"􏿿&\u0000ÿ":894," ":-609,"𐀀😀􏿿>":-520}
  ```

### Example 2

- generator: `object_unicode_keys`
- input: `{"\u0007\u0000\u0000": 357, "𐀀Ā𐀀 \u0007ÿ𐀀": -164, "   😀￿\u0000": -726}`

Canonical per implementation:
- **python** (len 89, sha 2a912df2528ac64c...):

  ```
  {"\u0007\u0000\u0000":357,"   😀￿\u0000":-726,"𐀀Ā𐀀 \u0007ÿ𐀀":-164}
  ```
- **go** (len 98, sha 053d023b073d283c...):

  ```
  {"\u0007\u0000\u0000":357,"\u2028\u2028\u2028😀￿\u0000":-726,"𐀀Ā𐀀 \u0007ÿ𐀀":-164}
  ```
- **rust** (len 89, sha 2a912df2528ac64c...):

  ```
  {"\u0007\u0000\u0000":357,"   😀￿\u0000":-726,"𐀀Ā𐀀 \u0007ÿ𐀀":-164}
  ```

### Example 3

- generator: `object_unicode_keys`
- input: `{"𐀀\\😀> ࠀ": -728, "\u001f\\\u0007\u0000": -755, "&😀\"": -509}`

Canonical per implementation:
- **python** (len 71, sha 9a0dae13b7e82ed3...):

  ```
  {"\u001f\\\u0007\u0000":-755,"&😀\"":-509,"𐀀\\😀> ࠀ":-728}
  ```
- **go** (len 74, sha f950799c13efe0e9...):

  ```
  {"\u001f\\\u0007\u0000":-755,"&😀\"":-509,"𐀀\\😀>\u2028ࠀ":-728}
  ```
- **rust** (len 71, sha 9a0dae13b7e82ed3...):

  ```
  {"\u001f\\\u0007\u0000":-755,"&😀\"":-509,"𐀀\\😀> ࠀ":-728}
  ```
