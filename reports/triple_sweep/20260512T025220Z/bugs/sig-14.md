# Disagreement signature 14

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-SMP,contains-U+2029,contains-emoji`

**Count:** 1

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-SMP, contains-U+2029, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - array_order: 1

## Examples

### Example 1

- generator: `array_order`
- input: `["􏿿\" <", 3, "😀", 0.2]`

Canonical per implementation:
- **python** (len 27, sha 645c89a3fa5e5ef1...):

  ```
  ["􏿿\" <",3,"😀",0.2]
  ```
- **go** (len 30, sha 64e48b55ad1ec29f...):

  ```
  ["􏿿\"\u2029<",3,"😀",0.2]
  ```
- **rust** (len 27, sha 645c89a3fa5e5ef1...):

  ```
  ["􏿿\" <",3,"😀",0.2]
  ```
