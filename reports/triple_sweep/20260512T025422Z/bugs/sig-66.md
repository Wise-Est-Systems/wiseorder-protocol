# Disagreement signature 66

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-C1-control,contains-DEL,contains-U+2029`

**Count:** 7

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-C1-control, contains-DEL, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - array_order: 3
  - object_unicode_keys: 2
  - nested: 1
  - unicode_string: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"\">�\\": 529, "\u0007ࠀ >ÿÿ": 633}`

Canonical per implementation:
- **python** (len 43, sha f5abe13b38091f4b...):

  ```
  {"\">�\\":529,"\u0007ࠀ >ÿÿ":633}
  ```
- **go** (len 46, sha e5f2b4bb831dd4fb...):

  ```
  {"\">�\\":529,"\u0007ࠀ\u2029>ÿÿ":633}
  ```
- **rust** (len 43, sha f5abe13b38091f4b...):

  ```
  {"\">�\\":529,"\u0007ࠀ >ÿÿ":633}
  ```

### Example 2

- generator: `array_order`
- input: `[-4, "/", 0.3333333333333333, "\u0007ÿ\u0007 ", 0.001, 0.3333333333333333, "߿￿"]`

Canonical per implementation:
- **python** (len 85, sha bc30ae550b1e36d9...):

  ```
  [-4,"/",0.3333333333333333,"\u0007ÿ\u0007 ",0.001,0.3333333333333333,"߿￿"]
  ```
- **go** (len 88, sha bdfaedd85b52539d...):

  ```
  [-4,"/",0.3333333333333333,"\u0007ÿ\u0007\u2029",0.001,0.3333333333333333,"߿￿"]
  ```
- **rust** (len 85, sha bc30ae550b1e36d9...):

  ```
  [-4,"/",0.3333333333333333,"\u0007ÿ\u0007 ",0.001,0.3333333333333333,"߿￿"]
  ```

### Example 3

- generator: `object_unicode_keys`
- input: `{"ࠀ\"": 836, " ": -756, "Ā&� ": -517, "ࠀ�\u0007ĀĀÿ": -377}`

Canonical per implementation:
- **python** (len 68, sha 69e9b3956d2a74cd...):

  ```
  {" ":-756,"ࠀ�\u0007ĀĀÿ":-377,"Ā&� ":-517,"ࠀ\"":836}
  ```
- **go** (len 71, sha de2e98eab7c5bf85...):

  ```
  {" ":-756,"ࠀ�\u0007ĀĀÿ":-377,"Ā&�\u2029":-517,"ࠀ\"":836}
  ```
- **rust** (len 68, sha 69e9b3956d2a74cd...):

  ```
  {" ":-756,"ࠀ�\u0007ĀĀÿ":-377,"Ā&� ":-517,"ࠀ\"":836}
  ```
