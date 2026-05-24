# Disagreement signature 75

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C1-control,contains-U+2029`

**Count:** 6

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C1-control, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - unicode_string: 3
  - mixed_object: 2
  - array_order: 1

## Examples

### Example 1

- generator: `mixed_object`
- input: `{"k5": {"nk0": 0, "nk1": 9007199254740991, "nk2": 0}, "k3": true, "k2": "<߿ Ā>/ࠀ", "k4": {"nk0": 0, "nk1": -0.0}, "k0": true, "k1": 0.30000000000000004}`

Canonical per implementation:
- **python** (len 141, sha d45cfbfe02c3fec1...):

  ```
  {"k0":true,"k1":0.30000000000000004,"k2":"<߿ Ā>/ࠀ","k3":true,"k4":{"nk0":0,"nk1":-0.0},"k5":{"nk0":0,"nk1":9007199254740991,"nk2":0}}
  ```
- **go** (len 144, sha adfa14ec56e77f25...):

  ```
  {"k0":true,"k1":0.30000000000000004,"k2":"<߿\u2029Ā>/ࠀ","k3":true,"k4":{"nk0":0,"nk1":-0.0},"k5":{"nk0":0,"nk1":9007199254740991,"nk2":0}}
  ```
- **rust** (len 141, sha d45cfbfe02c3fec1...):

  ```
  {"k0":true,"k1":0.30000000000000004,"k2":"<߿ Ā>/ࠀ","k3":true,"k4":{"nk0":0,"nk1":-0.0},"k5":{"nk0":0,"nk1":9007199254740991,"nk2":0}}
  ```

### Example 2

- generator: `unicode_string`
- input: `"\\ > "`

Canonical per implementation:
- **python** (len 11, sha e5d8e8628e8cbc25...):

  ```
  "\\ > "
  ```
- **go** (len 14, sha c6a1261c2e2f7772...):

  ```
  "\\ >\u2029"
  ```
- **rust** (len 11, sha e5d8e8628e8cbc25...):

  ```
  "\\ > "
  ```

### Example 3

- generator: `mixed_object`
- input: `{"k0": "  ÿ/Ā "}`

Canonical per implementation:
- **python** (len 25, sha 7778b60b6ed88c45...):

  ```
  {"k0":"  ÿ/Ā "}
  ```
- **go** (len 34, sha 838f260a01dac72f...):

  ```
  {"k0":"\u2029\u2029ÿ/Ā\u2029"}
  ```
- **rust** (len 25, sha 7778b60b6ed88c45...):

  ```
  {"k0":"  ÿ/Ā "}
  ```
