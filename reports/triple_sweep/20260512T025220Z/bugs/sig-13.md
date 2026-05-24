# Disagreement signature 13

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-BOM,contains-C0-control,contains-C1-control,contains-SMP,contains-U+2029`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-BOM, contains-C0-control, contains-C1-control, contains-SMP, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 1

## Examples

### Example 1

- generator: `nested`
- input: `[[{"﻿𐀀 \u0000": {"￿": 1.7976931348623157e+308, "tag": 0}, "tag": 5}, 1e+16, ""], -1, "ࠀࠀ￿ࠀ\u001f"]`

Canonical per implementation:
- **python** (len 109, sha 29698f2ad7060fbf...):

  ```
  [[{"tag":5,"﻿𐀀 \u0000":{"tag":0,"￿":1.7976931348623157e+308}},1e+16,""],-1,"ࠀࠀ￿ࠀ\u001f"]
  ```
- **go** (len 112, sha 85de3374fb9ef8ca...):

  ```
  [[{"tag":5,"﻿𐀀\u2029\u0000":{"tag":0,"￿":1.7976931348623157e+308}},1e+16,""],-1,"ࠀࠀ￿ࠀ\u001f"]
  ```
- **rust** (len 109, sha 29698f2ad7060fbf...):

  ```
  [[{"tag":5,"﻿𐀀 \u0000":{"tag":0,"￿":1.7976931348623157e+308}},1e+16,""],-1,"ࠀࠀ￿ࠀ\u001f"]
  ```
