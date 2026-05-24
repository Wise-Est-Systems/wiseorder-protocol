# Disagreement signature 9

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-SMP,contains-U+2029`

**Count:** 3

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-SMP, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 1
  - mixed_object: 1
  - unicode_string: 1

## Examples

### Example 1

- generator: `nested`
- input: `[[1, 0, "�￿ÿ𐀀"], 3.141592653589793, " /ÿĀĀĀ "]`

Canonical per implementation:
- **python** (len 56, sha 9a3506b43ee1bb76...):

  ```
  [[1,0,"�￿ÿ𐀀"],3.141592653589793," /ÿĀĀĀ "]
  ```
- **go** (len 59, sha 301e200c7f63a609...):

  ```
  [[1,0,"�￿ÿ𐀀"],3.141592653589793,"\u2029/ÿĀĀĀ "]
  ```
- **rust** (len 56, sha 9a3506b43ee1bb76...):

  ```
  [[1,0,"�￿ÿ𐀀"],3.141592653589793," /ÿĀĀĀ "]
  ```

### Example 2

- generator: `mixed_object`
- input: `{"k2": [], "k4": false, "k5": [], "k3": " Ā 􏿿&Ā&", "k0": {}, "k1": []}`

Canonical per implementation:
- **python** (len 66, sha 0286c19ae355bbc7...):

  ```
  {"k0":{},"k1":[],"k2":[],"k3":" Ā 􏿿&Ā&","k4":false,"k5":[]}
  ```
- **go** (len 69, sha a7c90c83424d0729...):

  ```
  {"k0":{},"k1":[],"k2":[],"k3":"\u2029Ā 􏿿&Ā&","k4":false,"k5":[]}
  ```
- **rust** (len 66, sha 0286c19ae355bbc7...):

  ```
  {"k0":{},"k1":[],"k2":[],"k3":" Ā 􏿿&Ā&","k4":false,"k5":[]}
  ```

### Example 3

- generator: `unicode_string`
- input: `" \\ 𐀀ࠀ"`

Canonical per implementation:
- **python** (len 17, sha 043a75e5276b752d...):

  ```
  " \\ 𐀀ࠀ"
  ```
- **go** (len 23, sha 3fac7bd68b632cef...):

  ```
  "\u2029\\\u2029𐀀ࠀ"
  ```
- **rust** (len 17, sha 043a75e5276b752d...):

  ```
  " \\ 𐀀ࠀ"
  ```
