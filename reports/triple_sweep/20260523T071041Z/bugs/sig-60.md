# Disagreement signature 60

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-U+2028,contains-U+2029,contains-emoji`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-U+2028, contains-U+2029, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"<\u001f\u0007<": 190, "  >�\\": 560, " \u001f\" > ": 474, "😀< ": -68}`

Canonical per implementation:
- **python** (len 79, sha 725c7b3470a2b627...):

  ```
  {"  >�\\":560,"<\u001f\u0007<":190," \u001f\" > ":474,"😀< ":-68}
  ```
- **go** (len 94, sha 48ef645960c3ef03...):

  ```
  {" \u2028>�\\":560,"<\u001f\u0007<":190,"\u2029\u001f\"\u2028>\u2029":474,"😀<\u2029":-68}
  ```
- **rust** (len 79, sha 725c7b3470a2b627...):

  ```
  {"  >�\\":560,"<\u001f\u0007<":190," \u001f\" > ":474,"😀< ":-68}
  ```
