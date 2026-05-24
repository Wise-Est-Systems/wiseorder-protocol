# Disagreement signature 87

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-SMP,contains-U+2028,contains-emoji`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-SMP, contains-U+2028, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - mixed_object: 1

## Examples

### Example 1

- generator: `mixed_object`
- input: `{"k3": 2.718281828459045, "k0": true, "k4": {"nk0": 0.0, "nk1": 3.141592653589793}, "k2": "􏿿&<Ā \\􏿿😀", "k1": [], "k5": [1e+100, 10000000000.0]}`

Canonical per implementation:
- **python** (len 140, sha a5bf8a4b30f94619...):

  ```
  {"k0":true,"k1":[],"k2":"􏿿&<Ā \\􏿿😀","k3":2.718281828459045,"k4":{"nk0":0.0,"nk1":3.141592653589793},"k5":[1e+100,10000000000.0]}
  ```
- **go** (len 143, sha d63863c5540a88e2...):

  ```
  {"k0":true,"k1":[],"k2":"􏿿&<Ā\u2028\\􏿿😀","k3":2.718281828459045,"k4":{"nk0":0.0,"nk1":3.141592653589793},"k5":[1e+100,10000000000.0]}
  ```
- **rust** (len 140, sha a5bf8a4b30f94619...):

  ```
  {"k0":true,"k1":[],"k2":"􏿿&<Ā \\􏿿😀","k3":2.718281828459045,"k4":{"nk0":0.0,"nk1":3.141592653589793},"k5":[1e+100,10000000000.0]}
  ```
