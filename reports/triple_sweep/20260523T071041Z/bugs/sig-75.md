# Disagreement signature 75

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-DEL,contains-SMP,contains-U+2028,contains-bigint>2^53`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-DEL, contains-SMP, contains-U+2028, contains-bigint>2^53

**Length pattern:** longest:go,shortest:python

**By generator:**
  - array_order: 1

## Examples

### Example 1

- generator: `array_order`
- input: `[" Ā Ā&ࠀ𐀀>", 0.3333333333333333, "߿ \u0000/ \u0000", 9223372036854775807]`

Canonical per implementation:
- **python** (len 81, sha 42420072c85248d9...):

  ```
  [" Ā Ā&ࠀ𐀀>",0.3333333333333333,"߿ \u0000/ \u0000",9223372036854775807]
  ```
- **go** (len 84, sha d9330c54735e9909...):

  ```
  ["\u2028Ā Ā&ࠀ𐀀>",0.3333333333333333,"߿ \u0000/ \u0000",9223372036854775807]
  ```
- **rust** (len 81, sha 42420072c85248d9...):

  ```
  [" Ā Ā&ࠀ𐀀>",0.3333333333333333,"߿ \u0000/ \u0000",9223372036854775807]
  ```
