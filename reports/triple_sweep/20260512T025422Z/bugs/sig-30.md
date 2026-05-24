# Disagreement signature 30

**Signature:** `agree:python+rust|outlier:go | longest:go,shortest:python | markers:contains-C0-control,contains-DEL,contains-SMP,contains-U+2029,contains-emoji`

**Count:** 13

**Partition:** agree:python+rust|outlier:go

**Outlier:** go

**Markers:** contains-C0-control, contains-DEL, contains-SMP, contains-U+2029, contains-emoji

**Length pattern:** longest:go,shortest:python

**By generator:**
  - nested: 7
  - object_unicode_keys: 5
  - array_order: 1

## Examples

### Example 1

- generator: `object_unicode_keys`
- input: `{"/\u001f􏿿&\u001f&\u0000": -563, ">ࠀ/<\u001f": 90, "\\߿ 𐀀": -925, "/\u0007 ": -680, "😀￿\\Ā𐀀": -254, "\u0007 ÿ": -757}`

Canonical per implementation:
- **python** (len 131, sha 3bc2ce08570685fd...):

  ```
  {"\u0007 ÿ":-757,"/\u0007 ":-680,"/\u001f􏿿&\u001f&\u0000":-563,">ࠀ/<\u001f":90,"\\߿ 𐀀":-925,"😀￿\\Ā𐀀":-254}
  ```
- **go** (len 137, sha 625080a6c823e459...):

  ```
  {"\u0007\u2029ÿ":-757,"/\u0007\u2029":-680,"/\u001f􏿿&\u001f&\u0000":-563,">ࠀ/<\u001f":90,"\\߿ 𐀀":-925,"😀￿\\Ā𐀀":-254}
  ```
- **rust** (len 131, sha 3bc2ce08570685fd...):

  ```
  {"\u0007 ÿ":-757,"/\u0007 ":-680,"/\u001f􏿿&\u001f&\u0000":-563,">ࠀ/<\u001f":90,"\\߿ 𐀀":-925,"😀￿\\Ā𐀀":-254}
  ```

### Example 2

- generator: `nested`
- input: `{"\u001f𐀀߿ÿ􏿿": {"<": {"\u0000<�😀\u0007>Ā￿": [{"ࠀ": 1.7976931348623157e+308, "tag": 2}, 0, "< ￿\u0000"], "tag": 9}, "tag": 4}, "tag": 0}`

Canonical per implementation:
- **python** (len 144, sha 14e0a950ee3092d7...):

  ```
  {"\u001f𐀀߿ÿ􏿿":{"<":{"\u0000<�😀\u0007>Ā￿":[{"tag":2,"ࠀ":1.7976931348623157e+308},0,"< ￿\u0000"],"tag":9},"tag":4},"tag":0}
  ```
- **go** (len 147, sha 181f90c3a4e60c6e...):

  ```
  {"\u001f𐀀߿ÿ􏿿":{"<":{"\u0000<�😀\u0007>Ā￿":[{"tag":2,"ࠀ":1.7976931348623157e+308},0,"<\u2029￿\u0000"],"tag":9},"tag":4},"tag":0}
  ```
- **rust** (len 144, sha 14e0a950ee3092d7...):

  ```
  {"\u001f𐀀߿ÿ􏿿":{"<":{"\u0000<�😀\u0007>Ā￿":[{"tag":2,"ࠀ":1.7976931348623157e+308},0,"< ￿\u0000"],"tag":9},"tag":4},"tag":0}
  ```

### Example 3

- generator: `object_unicode_keys`
- input: `{"😀\u0007\"\u0000 𐀀> ": 426, "\"\\ÿÿ> 😀": -197}`

Canonical per implementation:
- **python** (len 60, sha 957c400749c15e8c...):

  ```
  {"\"\\ÿÿ> 😀":-197,"😀\u0007\"\u0000 𐀀> ":426}
  ```
- **go** (len 66, sha e6cdd4a7f62a6779...):

  ```
  {"\"\\ÿÿ>\u2029😀":-197,"😀\u0007\"\u0000\u2029𐀀> ":426}
  ```
- **rust** (len 60, sha 957c400749c15e8c...):

  ```
  {"\"\\ÿÿ> 😀":-197,"😀\u0007\"\u0000 𐀀> ":426}
  ```
