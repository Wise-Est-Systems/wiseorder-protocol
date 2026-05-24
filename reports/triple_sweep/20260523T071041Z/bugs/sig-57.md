# Disagreement signature 57

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-DEL,contains-SMP,contains-U+2029`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-DEL, contains-SMP, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"􏿿\u001f>\u0007>￿ࠀ": -469, "&": -453, "􏿿\u0007ࠀ\u0000 ": 746}`

Canonical per implementation:
- **python** (len 72, sha e3c84479bed3d569...):

  ```
  {"&":-453,"􏿿\u0007ࠀ\u0000 ":746,"􏿿\u001f>\u0007>￿ࠀ":-469}
  ```
- **go** (len 75, sha 1362e98bb6e52875...):

  ```
  {"&":-453,"􏿿\u0007ࠀ\u0000\u2029":746,"􏿿\u001f>\u0007>￿ࠀ":-469}
  ```
- **rust** (len 72, sha e3c84479bed3d569...):

  ```
  {"&":-453,"􏿿\u0007ࠀ\u0000 ":746,"􏿿\u001f>\u0007>￿ࠀ":-469}
  ```
