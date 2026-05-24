# Disagreement signature 10

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-U+2028`

**Count:** 3

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-U+2028

**Length pattern:** longest:go,shortest:python

**By generator:**
  - unicode_string: 1
  - mixed_object: 1
  - array_order: 1

## Examples

### Example 1

- generator: `unicode_string`
- input: `"& �"`

Canonical per implementation:
- **python** (len 9, sha e7de4a28f90e74b3...):

  ```
  "& �"
  ```
- **go** (len 12, sha ac4b57a578364bf0...):

  ```
  "&\u2028�"
  ```
- **rust** (len 9, sha e7de4a28f90e74b3...):

  ```
  "& �"
  ```

### Example 2

- generator: `mixed_object`
- input: `{"k5": "\\ /", "k0": {}, "k2": [], "k4": {}, "k3": [1e+16], "k1": [0.1, 0.001]}`

Canonical per implementation:
- **python** (len 69, sha 7f4f8b1c3120cdd0...):

  ```
  {"k0":{},"k1":[0.1,0.001],"k2":[],"k3":[1e+16],"k4":{},"k5":"\\ /"}
  ```
- **go** (len 72, sha 91880626765b2ad7...):

  ```
  {"k0":{},"k1":[0.1,0.001],"k2":[],"k3":[1e+16],"k4":{},"k5":"\\\u2028/"}
  ```
- **rust** (len 69, sha 7f4f8b1c3120cdd0...):

  ```
  {"k0":{},"k1":[0.1,0.001],"k2":[],"k3":[1e+16],"k4":{},"k5":"\\ /"}
  ```

### Example 3

- generator: `array_order`
- input: `[-76, " ߿", 97, -2147483648, -29]`

Canonical per implementation:
- **python** (len 32, sha ef33bf1a42458426...):

  ```
  [-76," ߿",97,-2147483648,-29]
  ```
- **go** (len 35, sha a3bcd4a72417db84...):

  ```
  [-76,"\u2028߿",97,-2147483648,-29]
  ```
- **rust** (len 32, sha ef33bf1a42458426...):

  ```
  [-76," ߿",97,-2147483648,-29]
  ```
