# Disagreement signature 15

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-U+2028,contains-emoji`

**Count:** 2

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-U+2028, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - mixed_object: 1
  - unicode_string: 1

## Examples

### Example 1

- generator: `mixed_object`
- input: `{"k0": " 😀", "k2": {}, "k4": {"nk0": 0.3, "nk1": 0.30000000000000004, "nk2": 0.0}, "k1": null, "k3": {"nk0": 1000000000000000.0, "nk1": 0.3}}`

Canonical per implementation:
- **python** (len 129, sha 7a1993cf3aa7f4eb...):

  ```
  {"k0":" 😀","k1":null,"k2":{},"k3":{"nk0":1000000000000000.0,"nk1":0.3},"k4":{"nk0":0.3,"nk1":0.30000000000000004,"nk2":0.0}}
  ```
- **go** (len 132, sha c52b8c41a9a5a5dd...):

  ```
  {"k0":"\u2028😀","k1":null,"k2":{},"k3":{"nk0":1000000000000000.0,"nk1":0.3},"k4":{"nk0":0.3,"nk1":0.30000000000000004,"nk2":0.0}}
  ```
- **rust** (len 129, sha 7a1993cf3aa7f4eb...):

  ```
  {"k0":" 😀","k1":null,"k2":{},"k3":{"nk0":1000000000000000.0,"nk1":0.3},"k4":{"nk0":0.3,"nk1":0.30000000000000004,"nk2":0.0}}
  ```

### Example 2

- generator: `unicode_string`
- input: `" 😀�Ā😀"`

Canonical per implementation:
- **python** (len 18, sha fd009fd964d56851...):

  ```
  " 😀�Ā😀"
  ```
- **go** (len 21, sha e30591ca4db3bb1b...):

  ```
  "\u2028😀�Ā😀"
  ```
- **rust** (len 18, sha fd009fd964d56851...):

  ```
  " 😀�Ā😀"
  ```
