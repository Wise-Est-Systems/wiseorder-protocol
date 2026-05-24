# Disagreement signature 15

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C1-control,contains-DEL,contains-U+2028`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C1-control, contains-DEL, contains-U+2028

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 1

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
