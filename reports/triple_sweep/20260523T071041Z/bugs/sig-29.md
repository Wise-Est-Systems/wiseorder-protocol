# Disagreement signature 29

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-SMP,contains-U+2029`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-SMP, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{" ÿ￿Ā﻿\u0007>ÿ": 141, "/&/ \u001f􏿿/": -425}`

Canonical per implementation:
- **python** (len 55, sha b907b159dac37b08...):

  ```
  {"/&/ \u001f􏿿/":-425," ÿ￿Ā﻿\u0007>ÿ":141}
  ```
- **go** (len 61, sha 9642ae3941b06b57...):

  ```
  {"/&/\u2029\u001f􏿿/":-425,"\u2029ÿ￿Ā﻿\u0007>ÿ":141}
  ```
- **rust** (len 55, sha b907b159dac37b08...):

  ```
  {"/&/ \u001f􏿿/":-425," ÿ￿Ā﻿\u0007>ÿ":141}
  ```
