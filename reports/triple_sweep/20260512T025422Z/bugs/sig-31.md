# Disagreement signature 31

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-SMP,contains-U+2028,contains-U+2029`

**Count:** 13

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-SMP, contains-U+2028, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - array_order: 5
  - nested: 4
  - mixed_object: 2
  - unicode_string: 1
  - object_unicode_keys: 1

## Examples

### Example 1

- generator: `unicode_string`
- input: `"\\𐀀\\\u0000\u0007  "`

Canonical per implementation:
- **python** (len 28, sha 78a8a06f0119741f...):

  ```
  "\\𐀀\\\u0000\u0007  "
  ```
- **go** (len 34, sha 6608dd6369d264cd...):

  ```
  "\\𐀀\\\u0000\u0007\u2029\u2028"
  ```
- **rust** (len 28, sha 78a8a06f0119741f...):

  ```
  "\\𐀀\\\u0000\u0007  "
  ```

### Example 2

- generator: `array_order`
- input: `[14, 76, 0, -2.5, -42, "￿ \u0000ࠀ \"𐀀 ", "\u001f߿\\߿￿ "]`

Canonical per implementation:
- **python** (len 67, sha 78a56d3fc2e2b72c...):

  ```
  [14,76,0,-2.5,-42,"￿ \u0000ࠀ \"𐀀 ","\u001f߿\\߿￿ "]
  ```
- **go** (len 76, sha 1c2bc0965b3ca14d...):

  ```
  [14,76,0,-2.5,-42,"￿\u2029\u0000ࠀ \"𐀀\u2029","\u001f߿\\߿￿\u2028"]
  ```
- **rust** (len 67, sha 78a56d3fc2e2b72c...):

  ```
  [14,76,0,-2.5,-42,"￿ \u0000ࠀ \"𐀀 ","\u001f߿\\߿￿ "]
  ```

### Example 3

- generator: `mixed_object`
- input: `{"k3": false, "k1": "𐀀&\" \u001f ", "k4": null, "k0": [], "k2": 5e-324}`

Canonical per implementation:
- **python** (len 69, sha 2341f69433773fe4...):

  ```
  {"k0":[],"k1":"𐀀&\" \u001f ","k2":5e-324,"k3":false,"k4":null}
  ```
- **go** (len 75, sha 4b0a33c1b05f4178...):

  ```
  {"k0":[],"k1":"𐀀&\"\u2029\u001f\u2028","k2":5e-324,"k3":false,"k4":null}
  ```
- **rust** (len 69, sha 2341f69433773fe4...):

  ```
  {"k0":[],"k1":"𐀀&\" \u001f ","k2":5e-324,"k3":false,"k4":null}
  ```
