# Disagreement signature 22

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-DEL,contains-SMP,contains-U+2028`

**Count:** 2

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-DEL, contains-SMP, contains-U+2028

**Length pattern:** longest:go,shortest:python

**By generator:**
  - unicode_string: 1
  - nested: 1

## Examples

### Example 1

- generator: `unicode_string`
- input: `"\u0007<𐀀\u001f �"`

Canonical per implementation:
- **python** (len 26, sha d67dd1429feb4708...):

  ```
  "\u0007<𐀀\u001f �"
  ```
- **go** (len 29, sha 1fd22a8a2dd81fbd...):

  ```
  "\u0007<𐀀\u001f\u2028�"
  ```
- **rust** (len 26, sha d67dd1429feb4708...):

  ```
  "\u0007<𐀀\u001f �"
  ```

### Example 2

- generator: `nested`
- input: `{"ÿ\u0000𐀀/": {"߿𐀀𐀀ࠀ/\u001f/": {"𐀀 ": 2.718281828459045, "tag": 6}, "tag": 8}, "tag": 5}`

Canonical per implementation:
- **python** (len 98, sha 5583af877cf9d5fd...):

  ```
  {"tag":5,"ÿ\u0000𐀀/":{"tag":8,"߿𐀀𐀀ࠀ/\u001f/":{"tag":6,"𐀀 ":2.718281828459045}}}
  ```
- **go** (len 101, sha 3e42c4b6ac47a7ae...):

  ```
  {"tag":5,"ÿ\u0000𐀀/":{"tag":8,"߿𐀀𐀀ࠀ/\u001f/":{"tag":6,"𐀀\u2028":2.718281828459045}}}
  ```
- **rust** (len 98, sha 5583af877cf9d5fd...):

  ```
  {"tag":5,"ÿ\u0000𐀀/":{"tag":8,"߿𐀀𐀀ࠀ/\u001f/":{"tag":6,"𐀀 ":2.718281828459045}}}
  ```
