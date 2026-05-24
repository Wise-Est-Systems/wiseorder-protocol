# Disagreement signature 77

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-U+2029,contains-bigint>2^53,contains-emoji`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-U+2029, contains-bigint>2^53, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - mixed_object: 1

## Examples

### Example 1

- generator: `mixed_object`
- input: `{"k3": "😀\\ ࠀ/", "k1": null, "k5": [], "k2": [], "k4": [9007199254740993], "k0": []}`

Canonical per implementation:
- **python** (len 80, sha d965f21e59b3ca19...):

  ```
  {"k0":[],"k1":null,"k2":[],"k3":"😀\\ ࠀ/","k4":[9007199254740993],"k5":[]}
  ```
- **go** (len 83, sha 0451322a0bdb136b...):

  ```
  {"k0":[],"k1":null,"k2":[],"k3":"😀\\\u2029ࠀ/","k4":[9007199254740993],"k5":[]}
  ```
- **rust** (len 80, sha d965f21e59b3ca19...):

  ```
  {"k0":[],"k1":null,"k2":[],"k3":"😀\\ ࠀ/","k4":[9007199254740993],"k5":[]}
  ```
