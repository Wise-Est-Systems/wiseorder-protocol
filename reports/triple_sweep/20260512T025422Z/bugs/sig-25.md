# Disagreement signature 25

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-SMP,contains-U+2029`

**Count:** 14

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-SMP, contains-U+2029

**Length pattern:** longest:go,shortest:python

**By generator:**
  - unicode_string: 5
  - array_order: 5
  - object_unicode_keys: 2
  - mixed_object: 1
  - nested: 1

## Examples

### Example 1

- generator: `unicode_string`
- input: `"𐀀􏿿Ā𐀀 \\￿"`

Canonical per implementation:
- **python** (len 24, sha 70d9112aa89b0101...):

  ```
  "𐀀􏿿Ā𐀀 \\￿"
  ```
- **go** (len 27, sha c616284c4ca1b125...):

  ```
  "𐀀􏿿Ā𐀀\u2029\\￿"
  ```
- **rust** (len 24, sha 70d9112aa89b0101...):

  ```
  "𐀀􏿿Ā𐀀 \\￿"
  ```

### Example 2

- generator: `unicode_string`
- input: `" Ā\\ࠀ􏿿 ￿Ā"`

Canonical per implementation:
- **python** (len 22, sha eb8229f3bfd8d530...):

  ```
  " Ā\\ࠀ􏿿 ￿Ā"
  ```
- **go** (len 25, sha 47c01fd83d0f887b...):

  ```
  "\u2029Ā\\ࠀ􏿿 ￿Ā"
  ```
- **rust** (len 22, sha eb8229f3bfd8d530...):

  ```
  " Ā\\ࠀ􏿿 ￿Ā"
  ```

### Example 3

- generator: `array_order`
- input: `["𐀀", 96, -0.0, 9007199254740992, " <��", -75]`

Canonical per implementation:
- **python** (len 50, sha bc38340b439b6c05...):

  ```
  ["𐀀",96,-0.0,9007199254740992," <��",-75]
  ```
- **go** (len 53, sha 74ad9cb85ea87b99...):

  ```
  ["𐀀",96,-0.0,9007199254740992,"\u2029<��",-75]
  ```
- **rust** (len 50, sha bc38340b439b6c05...):

  ```
  ["𐀀",96,-0.0,9007199254740992," <��",-75]
  ```
