# Disagreement signature 28

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C1-control,contains-U+2029`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C1-control, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - mixed_object: 1

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
