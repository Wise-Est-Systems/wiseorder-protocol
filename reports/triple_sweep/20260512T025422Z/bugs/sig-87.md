# Disagreement signature 87

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C1-control,contains-DEL,contains-U+2028`

**Count:** 5

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C1-control, contains-DEL, contains-U+2028

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 2
  - unicode_string: 2
  - mixed_object: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"": 335, "￿ >": 158}`

Canonical per implementation:
- **python** (len 25, sha 31b96e99c8f21181...):

  ```
  {"":335,"￿ >":158}
  ```
- **go** (len 28, sha b67a831a99d68a6e...):

  ```
  {"":335,"￿\u2028>":158}
  ```
- **rust** (len 25, sha 31b96e99c8f21181...):

  ```
  {"":335,"￿ >":158}
  ```

### Example 2

- generator: `unicode_string`
- input: `" ÿ/Ā￿"`

Canonical per implementation:
- **python** (len 16, sha 0d0dc07704361479...):

  ```
  " ÿ/Ā￿"
  ```
- **go** (len 19, sha d8bfddbe4f276f49...):

  ```
  "\u2028ÿ/Ā￿"
  ```
- **rust** (len 16, sha 0d0dc07704361479...):

  ```
  " ÿ/Ā￿"
  ```

### Example 3

- generator: `object_unicode_keys`
- input: `{">￿\" ": 7, " \\": 5}`

Canonical per implementation:
- **python** (len 28, sha 01abacd0f17b2021...):

  ```
  {">￿\" ":7," \\":5}
  ```
- **go** (len 34, sha b7d875c1a6bca8b4...):

  ```
  {">￿\"\u2028":7,"\u2028\\":5}
  ```
- **rust** (len 28, sha 01abacd0f17b2021...):

  ```
  {">￿\" ":7," \\":5}
  ```
