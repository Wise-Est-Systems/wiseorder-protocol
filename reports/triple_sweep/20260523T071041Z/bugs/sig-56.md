# Disagreement signature 56

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-U+2028`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-U+2028

**Length pattern:** longest:go,shortest:python

**By generator:**
  - array_order: 1

## Examples

### Example 1

- generator: `array_order`
- input: `[1, 83, 25, -11, " /\u0000 >ࠀ> ", -68]`

Canonical per implementation:
- **python** (len 39, sha 7ef5b7dae88a2c88...):

  ```
  [1,83,25,-11," /\u0000 >ࠀ> ",-68]
  ```
- **go** (len 45, sha 3543efa6c057dedf...):

  ```
  [1,83,25,-11," /\u0000\u2028>ࠀ>\u2028",-68]
  ```
- **rust** (len 39, sha 7ef5b7dae88a2c88...):

  ```
  [1,83,25,-11," /\u0000 >ࠀ> ",-68]
  ```
