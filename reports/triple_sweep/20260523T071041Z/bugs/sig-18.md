# Disagreement signature 18

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-SMP,contains-U+2029,contains-bigint>2^53`

**Count:** 2

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-SMP, contains-U+2029, contains-bigint>2^53

**Length pattern:** longest:go,shortest:python

**By generator:**
  - array_order: 1
  - mixed_object: 1

## Examples

### Example 1

- generator: `array_order`
- input: `[-80, "߿\\/Āÿ߿\u001f􏿿", 9223372036854775807, -61, -0.0, "\\ ", 8, -95]`

Canonical per implementation:
- **python** (len 72, sha 844bda085f868db3...):

  ```
  [-80,"߿\\/Āÿ߿\u001f􏿿",9223372036854775807,-61,-0.0,"\\ ",8,-95]
  ```
- **go** (len 75, sha 722459cc61288685...):

  ```
  [-80,"߿\\/Āÿ߿\u001f􏿿",9223372036854775807,-61,-0.0,"\\\u2029",8,-95]
  ```
- **rust** (len 72, sha 844bda085f868db3...):

  ```
  [-80,"߿\\/Āÿ߿\u001f􏿿",9223372036854775807,-61,-0.0,"\\ ",8,-95]
  ```

### Example 2

- generator: `mixed_object`
- input: `{"k0": "  \u001f􏿿�&", "k2": "\"<", "k1": [2.718281828459045, 9007199254740993, -0.0]}`

Canonical per implementation:
- **python** (len 87, sha 9f456c67685cb401...):

  ```
  {"k0":"  \u001f􏿿�&","k1":[2.718281828459045,9007199254740993,-0.0],"k2":"\"<"}
  ```
- **go** (len 93, sha 6183a8bdcaed0a38...):

  ```
  {"k0":"\u2029\u2029\u001f􏿿�&","k1":[2.718281828459045,9007199254740993,-0.0],"k2":"\"<"}
  ```
- **rust** (len 87, sha 9f456c67685cb401...):

  ```
  {"k0":"  \u001f􏿿�&","k1":[2.718281828459045,9007199254740993,-0.0],"k2":"\"<"}
  ```
