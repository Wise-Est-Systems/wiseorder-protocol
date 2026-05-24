# Disagreement signature 19

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-DEL,contains-SMP,contains-U+2028,contains-emoji`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-DEL, contains-SMP, contains-U+2028, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - array_order: 1

## Examples

### Example 1

- generator: `array_order`
- input: `["\u0007\u001f�>ÿ 😀", "𐀀&"]`

Canonical per implementation:
- **python** (len 38, sha ea24f7b7b75b7567...):

  ```
  ["\u0007\u001f�>ÿ 😀","𐀀&"]
  ```
- **go** (len 41, sha c2e0cbf0a7522a38...):

  ```
  ["\u0007\u001f�>ÿ\u2028😀","𐀀&"]
  ```
- **rust** (len 38, sha ea24f7b7b75b7567...):

  ```
  ["\u0007\u001f�>ÿ 😀","𐀀&"]
  ```
