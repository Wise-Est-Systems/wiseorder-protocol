# Disagreement signature 91

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-C1-control,contains-DEL,contains-U+2028,contains-U+2029`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-C1-control, contains-DEL, contains-U+2028, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 1

## Examples

### Example 1

- generator: `nested`
- input: `[{"\u001f << ࠀ >": {"�\u001f ࠀ": {" ߿￿\"\u001f\u0007": {" ￿ࠀ": 0, "tag": 8}, "tag": 1}, "tag": 6}, "tag": 3}, -2147483648, ""]`

Canonical per implementation:
- **python** (len 138, sha 45abde6604dadaff...):

  ```
  [{"\u001f << ࠀ >":{"tag":6,"�\u001f ࠀ":{"tag":1," ߿￿\"\u001f\u0007":{" ￿ࠀ":0,"tag":8}}},"tag":3},-2147483648,""]
  ```
- **go** (len 150, sha bab3edd8be66ac18...):

  ```
  [{"\u001f\u2029<<\u2029ࠀ\u2029>":{"tag":6,"�\u001f ࠀ":{"tag":1,"\u2028߿￿\"\u001f\u0007":{" ￿ࠀ":0,"tag":8}}},"tag":3},-2147483648,""]
  ```
- **rust** (len 138, sha 45abde6604dadaff...):

  ```
  [{"\u001f << ࠀ >":{"tag":6,"�\u001f ࠀ":{"tag":1," ߿￿\"\u001f\u0007":{" ￿ࠀ":0,"tag":8}}},"tag":3},-2147483648,""]
  ```
