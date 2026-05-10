// Package jcs implements the tooling-internal canonicalization scheme used
// by WiseOrder v0.1.0 for fingerprinting (corpus_sha256 and friends).
//
// Independence note (WORK ORDER 013 §primary_rule):
//
//   This package does NOT import the Python intellagent_runtime, does NOT
//   shell out to python, and does NOT depend on the Rust verifier track.
//   Logic is re-derived from SPEC.md and the canonicalization corpus.
//
// Scheme (committed as "python-json-sortkeys-compact-utf8" in
// canonicalization/golden/golden-digests.json):
//
//   1. Object members serialized in sorted-key order (UTF-8 byte
//      order, which equals Unicode code-point order for valid UTF-8).
//   2. No insignificant whitespace; separators are "," and ":".
//   3. Strings emitted as raw UTF-8 bytes (no \uXXXX escaping for
//      non-ASCII; the JSON minimum escapes for `"` and `\` and the
//      C0 control range are still applied).
//   4. HTML-special characters `<`, `>`, `&` are NOT escaped (Go's
//      encoding/json escapes them by default; we disable that via
//      json.Encoder.SetEscapeHTML(false)).
//   5. Numbers serialized exactly as they appear in the source JSON.
//      We use json.Decoder.UseNumber() so number literals survive as
//      strings; on re-encoding, json.Number values are emitted verbatim.
//   6. UTF-8 output, no BOM.
//
// The exact-numeric pass-through (5) sidesteps any divergence between
// Python's repr(float) and Go's strconv.FormatFloat. It also means this
// canonicalizer is correct for any JSON number the parser accepts,
// regardless of magnitude or precision — the bytes that came in are
// the bytes that go out.

package jcs

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"strings"
)

// ParseValue parses raw JSON bytes preserving number literals as
// json.Number values, returning the generic Go representation
// (map[string]interface{}, []interface{}, string, bool, nil, json.Number).
func ParseValue(raw []byte) (interface{}, error) {
	dec := json.NewDecoder(bytes.NewReader(raw))
	dec.UseNumber()
	var v interface{}
	if err := dec.Decode(&v); err != nil {
		return nil, fmt.Errorf("parse: %w", err)
	}
	// Reject trailing non-whitespace tokens.
	if dec.More() {
		return nil, fmt.Errorf("parse: trailing tokens after top-level value")
	}
	return v, nil
}

// CanonicalBytes returns the canonical UTF-8 encoding of v under the
// tooling-internal scheme. v should be the result of ParseValue (or
// equivalent) so that number literals survive as json.Number.
func CanonicalBytes(v interface{}) ([]byte, error) {
	var buf bytes.Buffer
	enc := json.NewEncoder(&buf)
	enc.SetEscapeHTML(false)
	if err := enc.Encode(v); err != nil {
		return nil, fmt.Errorf("encode: %w", err)
	}
	out := buf.Bytes()
	// json.Encoder.Encode appends a trailing newline; strip it so the
	// output matches Python json.dumps without trailing whitespace.
	if n := len(out); n > 0 && out[n-1] == '\n' {
		out = out[:n-1]
	}
	return out, nil
}

// CanonicalString is a convenience wrapper around CanonicalBytes.
func CanonicalString(v interface{}) (string, error) {
	b, err := CanonicalBytes(v)
	if err != nil {
		return "", err
	}
	return string(b), nil
}

// SHA256Hex returns the lowercase hex digest of data (no "sha256:" prefix).
func SHA256Hex(data []byte) string {
	sum := sha256.Sum256(data)
	return hex.EncodeToString(sum[:])
}

// SHA256Prefixed returns "sha256:" + lowercase hex digest of data.
func SHA256Prefixed(data []byte) string {
	return "sha256:" + SHA256Hex(data)
}

// IsSHA256Hex reports whether s is a 64-char lowercase hex SHA-256 with
// the "sha256:" prefix (e.g. "sha256:abcd...01").
func IsSHA256Hex(s string) bool {
	const prefix = "sha256:"
	if !strings.HasPrefix(s, prefix) {
		return false
	}
	rest := s[len(prefix):]
	if len(rest) != 64 {
		return false
	}
	for _, c := range rest {
		switch {
		case c >= '0' && c <= '9':
		case c >= 'a' && c <= 'f':
		default:
			return false
		}
	}
	return true
}
