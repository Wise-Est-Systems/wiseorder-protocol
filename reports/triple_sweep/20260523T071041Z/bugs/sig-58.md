# Disagreement signature 58

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-DEL,contains-SMP,contains-U+2028,contains-U+2029`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-DEL, contains-SMP, contains-U+2028, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"𐀀\"􏿿�￿ \u001f ": 599, "ÿ<ࠀࠀ": -669}`

Canonical per implementation:
- **python** (len 54, sha bdda41706bba8fa4...):

  ```
  {"ÿ<ࠀࠀ":-669,"𐀀\"􏿿�￿ \u001f ":599}
  ```
- **go** (len 60, sha ec7df19200b1deab...):

  ```
  {"ÿ<ࠀࠀ":-669,"𐀀\"􏿿�￿\u2029\u001f\u2028":599}
  ```
- **rust** (len 54, sha bdda41706bba8fa4...):

  ```
  {"ÿ<ࠀࠀ":-669,"𐀀\"􏿿�￿ \u001f ":599}
  ```
