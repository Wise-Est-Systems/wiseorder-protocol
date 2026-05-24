# Disagreement signature 64

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-C1-control,contains-DEL,contains-SMP,contains-U+2028`

**Count:** 8

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-C1-control, contains-DEL, contains-SMP, contains-U+2028

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 5
  - nested: 3

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"\\�/\u0007ࠀ ": 392, "􏿿\\/\\ࠀ\u0000": 330, "𐀀\u0007<\"": -998}`

Canonical per implementation:
- **python** (len 75, sha f8b29e2b54f5b1eb...):

  ```
  {"\\�/\u0007ࠀ ":392,"𐀀\u0007<\"":-998,"􏿿\\/\\ࠀ\u0000":330}
  ```
- **go** (len 78, sha 74b677ccc0a2a1a9...):

  ```
  {"\\�/\u0007ࠀ\u2028":392,"𐀀\u0007<\"":-998,"􏿿\\/\\ࠀ\u0000":330}
  ```
- **rust** (len 75, sha f8b29e2b54f5b1eb...):

  ```
  {"\\�/\u0007ࠀ ":392,"𐀀\u0007<\"":-998,"􏿿\\/\\ࠀ\u0000":330}
  ```

### Example 2

- generator: `nested`
- input: `[[[{" Ā\u0007 ": {"ÿ ": 3.141592653589793, "tag": 0}, "tag": 5}, 5e-324, "𐀀\u0007<"], 2.718281828459045, ">߿𐀀􏿿/ \"\u0007"], 2147483647, "\"\u0007߿"]`

Canonical per implementation:
- **python** (len 160, sha 2892c6cdaceae8bf...):

  ```
  [[[{"tag":5," Ā\u0007 ":{"tag":0,"ÿ ":3.141592653589793}},5e-324,"𐀀\u0007<"],2.718281828459045,">߿𐀀􏿿/ \"\u0007"],2147483647,"\"\u0007߿"]
  ```
- **go** (len 166, sha 5f45c8c99aeb8175...):

  ```
  [[[{"tag":5,"\u2028Ā\u0007 ":{"tag":0,"ÿ\u2028":3.141592653589793}},5e-324,"𐀀\u0007<"],2.718281828459045,">߿𐀀􏿿/ \"\u0007"],2147483647,"\"\u0007߿"]
  ```
- **rust** (len 160, sha 2892c6cdaceae8bf...):

  ```
  [[[{"tag":5," Ā\u0007 ":{"tag":0,"ÿ ":3.141592653589793}},5e-324,"𐀀\u0007<"],2.718281828459045,">߿𐀀􏿿/ \"\u0007"],2147483647,"\"\u0007߿"]
  ```

### Example 3

- generator: `object_unicode_keys`
- input: `{"𐀀\u0007ࠀ\"\u001fĀ": 915, "\"\u0007 ࠀ\\\u001f<": -968, ">\"￿\u001f\"ÿ": -826}`

Canonical per implementation:
- **python** (len 89, sha 4df7eebc87cd71fc...):

  ```
  {"\"\u0007 ࠀ\\\u001f<":-968,">\"￿\u001f\"ÿ":-826,"𐀀\u0007ࠀ\"\u001fĀ":915}
  ```
- **go** (len 92, sha 0440e24e4cd09ff4...):

  ```
  {"\"\u0007\u2028ࠀ\\\u001f<":-968,">\"￿\u001f\"ÿ":-826,"𐀀\u0007ࠀ\"\u001fĀ":915}
  ```
- **rust** (len 89, sha 4df7eebc87cd71fc...):

  ```
  {"\"\u0007 ࠀ\\\u001f<":-968,">\"￿\u001f\"ÿ":-826,"𐀀\u0007ࠀ\"\u001fĀ":915}
  ```
