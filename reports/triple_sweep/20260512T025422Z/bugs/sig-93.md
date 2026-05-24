# Disagreement signature 93

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C1-control,contains-DEL,contains-SMP,contains-U+2029`

**Count:** 5

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C1-control, contains-DEL, contains-SMP, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 2
  - object_unicode_keys: 1
  - unicode_string: 1
  - mixed_object: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{" ߿": 155, "Ā𐀀߿\"𐀀\\": -154, "Ā": -707}`

Canonical per implementation:
- **python** (len 52, sha 7b006729a85f5850...):

  ```
  {"Ā":-707," ߿":155,"Ā𐀀߿\"𐀀\\":-154}
  ```
- **go** (len 55, sha 2e35a5a3ce373b9b...):

  ```
  {"Ā":-707,"\u2029߿":155,"Ā𐀀߿\"𐀀\\":-154}
  ```
- **rust** (len 52, sha 7b006729a85f5850...):

  ```
  {"Ā":-707," ߿":155,"Ā𐀀߿\"𐀀\\":-154}
  ```

### Example 2

- generator: `unicode_string`
- input: `"/ ࠀ􏿿Ā<"`

Canonical per implementation:
- **python** (len 19, sha 39fb9638e82a1267...):

  ```
  "/ ࠀ􏿿Ā<"
  ```
- **go** (len 22, sha 2d3f0a442aa14ffc...):

  ```
  "/\u2029ࠀ􏿿Ā<"
  ```
- **rust** (len 19, sha 39fb9638e82a1267...):

  ```
  "/ ࠀ􏿿Ā<"
  ```

### Example 3

- generator: `mixed_object`
- input: `{"k1": {"nk0": -0.0}, "k0": "ࠀ �𐀀<<", "k2": "  �߿"}`

Canonical per implementation:
- **python** (len 64, sha d42a9de49083adac...):

  ```
  {"k0":"ࠀ �𐀀<<","k1":{"nk0":-0.0},"k2":"  �߿"}
  ```
- **go** (len 73, sha 241703550469405a...):

  ```
  {"k0":"ࠀ\u2029�𐀀<<","k1":{"nk0":-0.0},"k2":"\u2029\u2029�߿"}
  ```
- **rust** (len 64, sha d42a9de49083adac...):

  ```
  {"k0":"ࠀ �𐀀<<","k1":{"nk0":-0.0},"k2":"  �߿"}
  ```
