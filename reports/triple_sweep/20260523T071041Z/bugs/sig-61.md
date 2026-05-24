# Disagreement signature 61

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-DEL,contains-U+2029,contains-bigint>2^53`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-DEL, contains-U+2029, contains-bigint>2^53

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 1

## Examples

### Example 1

- generator: `nested`
- input: `{"\" & ÿ": [9007199254740992, 9007199254740993, "߿ÿ\u0007>ÿ"], "tag": 8}`

Canonical per implementation:
- **python** (len 76, sha 056be5670fdcf2e7...):

  ```
  {"\" & ÿ":[9007199254740992,9007199254740993,"߿ÿ\u0007>ÿ"],"tag":8}
  ```
- **go** (len 82, sha 6534cd0934de8d93...):

  ```
  {"\"\u2029&\u2029ÿ":[9007199254740992,9007199254740993,"߿ÿ\u0007>ÿ"],"tag":8}
  ```
- **rust** (len 76, sha 056be5670fdcf2e7...):

  ```
  {"\" & ÿ":[9007199254740992,9007199254740993,"߿ÿ\u0007>ÿ"],"tag":8}
  ```
