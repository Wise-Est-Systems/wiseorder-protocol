# Disagreement signature 21

**Signature:** `all-three-different | longest:go,shortest:python | markers:contains-C0-control,contains-DEL,contains-SMP,contains-U+2028,contains-U+2029,contains-bigint>2^53,contains-bigint>=2^64,contains-bigint>i64`

**Count:** 2

**Partition:** all-three-different

**Outlier:** all-three-different

**Markers:** contains-C0-control, contains-DEL, contains-SMP, contains-U+2028, contains-U+2029, contains-bigint>2^53, contains-bigint>=2^64, contains-bigint>i64

**Length pattern:** longest:go,shortest:python

**By generator:**
  - array_order: 1
  - mixed_object: 1

## Examples

### Example 1

- generator: `array_order`
- input: `[9007199254740991, "<𐀀ÿ   ", "Ā\\ \"ÿ", "\u0000𐀀/&  ", 18446744073709551616, -0.0, 9007199254740992]`

Canonical per implementation:
- **python** (len 115, sha d3bbdf7b24aab385...):

  ```
  [9007199254740991,"<𐀀ÿ   ","Ā\\ \"ÿ","\u0000𐀀/&  ",18446744073709551616,-0.0,9007199254740992]
  ```
- **go** (len 130, sha 492c2713ca7a37db...):

  ```
  [9007199254740991,"<𐀀ÿ\u2028\u2029\u2028","Ā\\\u2029\"ÿ","\u0000𐀀/&\u2029 ",18446744073709551616,-0.0,9007199254740992]
  ```
- **rust** (len 117, sha bb9b957c7bf00144...):

  ```
  [9007199254740991,"<𐀀ÿ   ","Ā\\ \"ÿ","\u0000𐀀/&  ",1.8446744073709552e+19,-0.0,9007199254740992]
  ```

### Example 2

- generator: `mixed_object`
- input: `{"k2": -1, "k3": "�/￿\u0007\\> \u0000", "k0": 18446744073709551616, "k1": " &𐀀￿\\ "}`

Canonical per implementation:
- **python** (len 91, sha 691bdf64de9acd18...):

  ```
  {"k0":18446744073709551616,"k1":" &𐀀￿\\ ","k2":-1,"k3":"�/￿\u0007\\> \u0000"}
  ```
- **go** (len 97, sha 30184af3c34da82e...):

  ```
  {"k0":18446744073709551616,"k1":" &𐀀￿\\\u2029","k2":-1,"k3":"�/￿\u0007\\>\u2028\u0000"}
  ```
- **rust** (len 93, sha 6628565e6ebf729a...):

  ```
  {"k0":1.8446744073709552e+19,"k1":" &𐀀￿\\ ","k2":-1,"k3":"�/￿\u0007\\> \u0000"}
  ```
