# Disagreement signature 80

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C1-control,contains-SMP,contains-U+2028,contains-U+2029`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C1-control, contains-SMP, contains-U+2028, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - array_order: 1

## Examples

### Example 1

- generator: `array_order`
- input: `["ÿ&< Ā􏿿\\", -22, "߿ ", -9, "\\  ", 10000000000.0, -91]`

Canonical per implementation:
- **python** (len 65, sha 390fda2526aa4cad...):

  ```
  ["ÿ&< Ā􏿿\\",-22,"߿ ",-9,"\\  ",10000000000.0,-91]
  ```
- **go** (len 77, sha 5665ea323b52a4eb...):

  ```
  ["ÿ&<\u2029Ā􏿿\\",-22,"߿\u2029",-9,"\\\u2028\u2029",10000000000.0,-91]
  ```
- **rust** (len 65, sha 390fda2526aa4cad...):

  ```
  ["ÿ&< Ā􏿿\\",-22,"߿ ",-9,"\\  ",10000000000.0,-91]
  ```
