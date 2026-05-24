# Disagreement signature 13

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-U+2029`

**Count:** 3

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 1
  - mixed_object: 1
  - array_order: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"￿￿Ā/߿": 972, "ࠀ\u0000\u0000\" ￿ >": 229}`

Canonical per implementation:
- **python** (len 51, sha 0da54fbfd54d5cb8...):

  ```
  {"ࠀ\u0000\u0000\" ￿ >":229,"￿￿Ā/߿":972}
  ```
- **go** (len 54, sha 8138f1fe6d5d2632...):

  ```
  {"ࠀ\u0000\u0000\" ￿\u2029>":229,"￿￿Ā/߿":972}
  ```
- **rust** (len 51, sha 0da54fbfd54d5cb8...):

  ```
  {"ࠀ\u0000\u0000\" ￿ >":229,"￿￿Ā/߿":972}
  ```

### Example 2

- generator: `mixed_object`
- input: `{"k0": null, "k1": " \u0000", "k2": [3.14159, 0.001]}`

Canonical per implementation:
- **python** (len 49, sha b69500d9d9c54110...):

  ```
  {"k0":null,"k1":" \u0000","k2":[3.14159,0.001]}
  ```
- **go** (len 52, sha 25b8c3c01e06d760...):

  ```
  {"k0":null,"k1":"\u2029\u0000","k2":[3.14159,0.001]}
  ```
- **rust** (len 49, sha b69500d9d9c54110...):

  ```
  {"k0":null,"k1":" \u0000","k2":[3.14159,0.001]}
  ```

### Example 3

- generator: `array_order`
- input: `[16, 10000000000.0, -2.5, -31, "�Ā\u001f \\", " ", 2147483647]`

Canonical per implementation:
- **python** (len 63, sha b9b4ac9fba53dba3...):

  ```
  [16,10000000000.0,-2.5,-31,"�Ā\u001f \\"," ",2147483647]
  ```
- **go** (len 69, sha b57b10264aa19045...):

  ```
  [16,10000000000.0,-2.5,-31,"�Ā\u001f\u2029\\","\u2029",2147483647]
  ```
- **rust** (len 63, sha b9b4ac9fba53dba3...):

  ```
  [16,10000000000.0,-2.5,-31,"�Ā\u001f \\"," ",2147483647]
  ```
