# Disagreement signature 79

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-C1-control,contains-DEL,contains-SMP,contains-U+2028,contains-U+2029`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-C1-control, contains-DEL, contains-SMP, contains-U+2028, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"�<Ā\u0007�": -12, "\u0007/ /\u001f&\u0000": 277, "􏿿߿ ": -584, "￿\u001f\u0007Ā\"�": -524}`

Canonical per implementation:
- **python** (len 106, sha 43b29c588f90b9f9...):

  ```
  {"\u0007/ /\u001f&\u0000":277,"�<Ā\u0007�":-12,"￿\u001f\u0007Ā\"�":-524,"􏿿߿ ":-584}
  ```
- **go** (len 112, sha 62a3d6ace7d7b1a9...):

  ```
  {"\u0007/\u2028/\u001f&\u0000":277,"�<Ā\u0007�":-12,"￿\u001f\u0007Ā\"�":-524,"􏿿߿\u2029":-584}
  ```
- **rust** (len 106, sha 43b29c588f90b9f9...):

  ```
  {"\u0007/ /\u001f&\u0000":277,"�<Ā\u0007�":-12,"￿\u001f\u0007Ā\"�":-524,"􏿿߿ ":-584}
  ```
