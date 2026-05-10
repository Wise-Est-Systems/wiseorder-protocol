// Canonicalization for fingerprinting (tooling-internal scheme).
//
// WiseOrder Protocol v0.1.0 distinguishes:
//   - Class A canonicalization: RFC 8785 JCS (per SPEC.md §4)
//   - Tooling-internal canonicalization for fingerprinting (corpus_sha256,
//     manifests_suite_sha256, vectors_suite_sha256).
//
// The canonicalization corpus committed under canonicalization/corpus/ uses
// the *tooling-internal* scheme, declared as
// "python-json-sortkeys-compact-utf8" in canonicalization/golden/.
// That scheme's rules:
//
//   1. Object members serialized in sorted-key order (UTF-8 code-point /
//      lexicographic byte order; for the ASCII-and-BMP corpus committed
//      under v0.1.0 this equals Python's str default-sort order).
//   2. No insignificant whitespace; separators are "," and ":".
//   3. Strings emitted as UTF-8 bytes (no \uXXXX escaping for non-ASCII).
//      Control characters (U+0000..U+001F), `"`, and `\` are escaped per
//      JSON minimum requirements.
//   4. Numbers serialized using the shortest decimal representation that
//      round-trips through IEEE-754 binary64 (Ryu / Grisu3 algorithm —
//      matches Python's repr() for the floats committed in the v0.1.0
//      corpus: 3.14159, 0.001, -2.5, 0.1; and matches integer
//      stringification for the integer-typed entries).
//   5. UTF-8 output, no BOM.
//
// We implement this canonicalization by:
//   (a) parsing each corpus file with serde_json (which preserves
//       arbitrary precision via Number),
//   (b) serializing the parsed Value with serde_json::to_string. With
//       serde_json's default feature set, Map<String, Value> is a
//       BTreeMap which iterates in sorted key order, and to_string
//       emits compact separators without whitespace, escapes the JSON
//       minimum set, and emits non-ASCII as UTF-8 bytes — exactly the
//       scheme above.
//
// Independence note: this file does not depend on Python, intellagent_*,
// or any first-party Rust runtime. It depends only on serde_json's
// documented default canonical behavior.

use sha2::{Digest, Sha256};

/// Canonical bytes for fingerprinting. Returns the UTF-8 bytes of the
/// canonical serialization of `value`.
pub fn canonical_bytes(value: &serde_json::Value) -> Vec<u8> {
    // serde_json::to_string with default features:
    //   - sorted keys (BTreeMap-backed Map)
    //   - compact separators (no whitespace)
    //   - UTF-8 (no \uXXXX escaping for non-ASCII)
    serde_json::to_string(value)
        .expect("infallible: serializing a parsed Value cannot fail")
        .into_bytes()
}

/// Convenience: SHA-256 hex (lowercase, no prefix) of canonical bytes.
pub fn canonical_sha256_hex(value: &serde_json::Value) -> String {
    let bytes = canonical_bytes(value);
    let mut hasher = Sha256::new();
    hasher.update(&bytes);
    hex_lower(&hasher.finalize())
}

/// SHA-256 hex (lowercase, no prefix) of arbitrary bytes.
pub fn sha256_hex(bytes: &[u8]) -> String {
    let mut hasher = Sha256::new();
    hasher.update(bytes);
    hex_lower(&hasher.finalize())
}

/// SHA-256 with the protocol's "sha256:" prefix.
pub fn sha256_prefixed(bytes: &[u8]) -> String {
    format!("sha256:{}", sha256_hex(bytes))
}

fn hex_lower(bytes: &[u8]) -> String {
    const HEX: &[u8; 16] = b"0123456789abcdef";
    let mut out = String::with_capacity(bytes.len() * 2);
    for &b in bytes {
        out.push(HEX[(b >> 4) as usize] as char);
        out.push(HEX[(b & 0x0F) as usize] as char);
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn canonical_sorts_object_keys() {
        let v = json!({"b": 2, "a": 1});
        assert_eq!(canonical_bytes(&v), b"{\"a\":1,\"b\":2}");
    }

    #[test]
    fn canonical_compact_separators() {
        let v = json!({"a": 1, "b": [10, 20, 30]});
        assert_eq!(canonical_bytes(&v), b"{\"a\":1,\"b\":[10,20,30]}");
    }

    #[test]
    fn canonical_preserves_array_order() {
        let v = json!([3, 1, 2, "a", "b"]);
        assert_eq!(canonical_bytes(&v), b"[3,1,2,\"a\",\"b\"]");
    }

    #[test]
    fn canonical_emits_utf8_not_escapes() {
        let v = json!({"emoji": "🌍", "math": "α"});
        let bytes = canonical_bytes(&v);
        let s = std::str::from_utf8(&bytes).unwrap();
        assert!(s.contains("🌍"));
        assert!(s.contains("α"));
    }

    #[test]
    fn canonical_nested_sorts_recursively() {
        let v = json!({"outer": {"z": 1, "a": 2}, "inner": [{"k": 3, "j": 4}, {"m": 5}]});
        assert_eq!(
            canonical_bytes(&v),
            br#"{"inner":[{"j":4,"k":3},{"m":5}],"outer":{"a":2,"z":1}}"#
        );
    }

    #[test]
    fn sha256_hex_known_vector() {
        // "abc" → SHA-256 hex per FIPS 180-2.
        assert_eq!(
            sha256_hex(b"abc"),
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
        );
    }

    #[test]
    fn sha256_prefixed_includes_marker() {
        let h = sha256_prefixed(b"abc");
        assert!(h.starts_with("sha256:"));
        assert_eq!(h.len(), "sha256:".len() + 64);
    }
}
