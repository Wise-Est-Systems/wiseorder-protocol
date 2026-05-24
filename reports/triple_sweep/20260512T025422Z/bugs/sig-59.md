# Disagreement signature 59

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-SMP,contains-U+2029,contains-emoji`

**Count:** 8

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-SMP, contains-U+2029, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - array_order: 3
  - unicode_string: 2
  - nested: 1
  - object_unicode_keys: 1
  - mixed_object: 1

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

### Example 2

- generator: `unicode_string`
- input: `" 􏿿😀"`

Canonical per implementation:
- **python** (len 13, sha 1b526521245553f1...):

  ```
  " 􏿿😀"
  ```
- **go** (len 16, sha f6f20fe0c102e84d...):

  ```
  "\u2029􏿿😀"
  ```
- **rust** (len 13, sha 1b526521245553f1...):

  ```
  " 􏿿😀"
  ```

### Example 3

- generator: `nested`
- input: `[{" 😀𐀀&": 0.1, "tag": 0}, -0.0, "Ā �𐀀 "]`

Canonical per implementation:
- **python** (len 51, sha 1fb894706deec0cf...):

  ```
  [{"tag":0," 😀𐀀&":0.1},-0.0,"Ā �𐀀 "]
  ```
- **go** (len 57, sha 7e6306bb80040970...):

  ```
  [{"tag":0,"\u2029😀𐀀&":0.1},-0.0,"Ā\u2029�𐀀 "]
  ```
- **rust** (len 51, sha 1fb894706deec0cf...):

  ```
  [{"tag":0," 😀𐀀&":0.1},-0.0,"Ā �𐀀 "]
  ```
