# Disagreement signature 14

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-U+2029`

**Count:** 17

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - unicode_string: 14
  - mixed_object: 2
  - array_order: 1

## Examples

### Example 1

- generator: `unicode_string`
- input: `"Āࠀ/ \\ \""`

Canonical per implementation:
- **python** (len 16, sha 839a1f0c272ca17f...):

  ```
  "Āࠀ/ \\ \""
  ```
- **go** (len 19, sha 5757ffdedf629fdf...):

  ```
  "Āࠀ/ \\\u2029\""
  ```
- **rust** (len 16, sha 839a1f0c272ca17f...):

  ```
  "Āࠀ/ \\ \""
  ```

### Example 2

- generator: `mixed_object`
- input: `{"k0": " ", "k1": [], "k2": [], "k3": 1e+17}`

Canonical per implementation:
- **python** (len 39, sha ffa49a1bb9e08434...):

  ```
  {"k0":" ","k1":[],"k2":[],"k3":1e+17}
  ```
- **go** (len 42, sha 3e22a6454f49c2a2...):

  ```
  {"k0":"\u2029","k1":[],"k2":[],"k3":1e+17}
  ```
- **rust** (len 39, sha ffa49a1bb9e08434...):

  ```
  {"k0":" ","k1":[],"k2":[],"k3":1e+17}
  ```

### Example 3

- generator: `unicode_string`
- input: `"/< ߿&"`

Canonical per implementation:
- **python** (len 10, sha 61db68df58d3a7d1...):

  ```
  "/< ߿&"
  ```
- **go** (len 13, sha 39d00a7e6ec09c16...):

  ```
  "/<\u2029߿&"
  ```
- **rust** (len 10, sha 61db68df58d3a7d1...):

  ```
  "/< ߿&"
  ```
