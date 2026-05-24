# Disagreement signature 92

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C1-control,contains-SMP,contains-U+2028,contains-emoji`

**Count:** 5

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C1-control, contains-SMP, contains-U+2028, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - object_unicode_keys: 3
  - array_order: 1
  - nested: 1

## Examples

### Example 1

- generator: `array_order`
- input: `[-95, "\"Ā", -93, 0.3333333333333333, 10000000000.0, -59, -96, "ࠀ 😀􏿿Ā"]`

Canonical per implementation:
- **python** (len 78, sha 9df5b982590dc3dd...):

  ```
  [-95,"\"Ā",-93,0.3333333333333333,10000000000.0,-59,-96,"ࠀ 😀􏿿Ā"]
  ```
- **go** (len 81, sha 112bd46ddef91a30...):

  ```
  [-95,"\"Ā",-93,0.3333333333333333,10000000000.0,-59,-96,"ࠀ\u2028😀􏿿Ā"]
  ```
- **rust** (len 78, sha 9df5b982590dc3dd...):

  ```
  [-95,"\"Ā",-93,0.3333333333333333,10000000000.0,-59,-96,"ࠀ 😀􏿿Ā"]
  ```

### Example 2

- generator: `object_unicode_keys`
- input: `{"􏿿\"": 764, "😀Ā𐀀": 526, "\\ >": -386}`

Canonical per implementation:
- **python** (len 49, sha f6641b312a41192a...):

  ```
  {"\\ >":-386,"􏿿\"":764,"😀Ā𐀀":526}
  ```
- **go** (len 52, sha eaa36cfaef154376...):

  ```
  {"\\\u2028>":-386,"􏿿\"":764,"😀Ā𐀀":526}
  ```
- **rust** (len 49, sha f6641b312a41192a...):

  ```
  {"\\ >":-386,"􏿿\"":764,"😀Ā𐀀":526}
  ```

### Example 3

- generator: `object_unicode_keys`
- input: `{"￿�􏿿￿ࠀ": -757, "�": -334, "߿� 𐀀😀 &": -85, "￿􏿿�": 924}`

Canonical per implementation:
- **python** (len 80, sha bd042bb59ebf550a...):

  ```
  {"߿� 𐀀😀 &":-85,"�":-334,"￿�􏿿￿ࠀ":-757,"￿􏿿�":924}
  ```
- **go** (len 83, sha 548bcf03363e1589...):

  ```
  {"߿�\u2028𐀀😀 &":-85,"�":-334,"￿�􏿿￿ࠀ":-757,"￿􏿿�":924}
  ```
- **rust** (len 80, sha bd042bb59ebf550a...):

  ```
  {"߿� 𐀀😀 &":-85,"�":-334,"￿�􏿿￿ࠀ":-757,"￿􏿿�":924}
  ```
