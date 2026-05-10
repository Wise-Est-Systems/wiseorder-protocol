package jcs

import (
	"crypto/sha256"
	"encoding/hex"
	"testing"
)

func TestCanonicalSortsObjectKeys(t *testing.T) {
	v, err := ParseValue([]byte(`{"b": 2, "a": 1}`))
	if err != nil {
		t.Fatal(err)
	}
	got, err := CanonicalString(v)
	if err != nil {
		t.Fatal(err)
	}
	if want := `{"a":1,"b":2}`; got != want {
		t.Fatalf("got %q want %q", got, want)
	}
}

func TestCanonicalCompactSeparators(t *testing.T) {
	v, _ := ParseValue([]byte(`{"a": 1, "b": [10, 20, 30]}`))
	got, _ := CanonicalString(v)
	if want := `{"a":1,"b":[10,20,30]}`; got != want {
		t.Fatalf("got %q want %q", got, want)
	}
}

func TestCanonicalPreservesArrayOrder(t *testing.T) {
	v, _ := ParseValue([]byte(`[3, 1, 2, "a", "b"]`))
	got, _ := CanonicalString(v)
	if want := `[3,1,2,"a","b"]`; got != want {
		t.Fatalf("got %q want %q", got, want)
	}
}

func TestCanonicalEmitsRawUTF8(t *testing.T) {
	v, _ := ParseValue([]byte(`{"emoji": "🌍", "math": "α"}`))
	got, _ := CanonicalString(v)
	if want := `{"emoji":"🌍","math":"α"}`; got != want {
		t.Fatalf("got %q want %q", got, want)
	}
}

func TestCanonicalPreservesNumberLiterals(t *testing.T) {
	// json.Number pass-through avoids any float-formatting divergence.
	v, _ := ParseValue([]byte(`{"pi": 3.14159, "small": 0.001, "neg": -2.5, "tenths": 0.1}`))
	got, _ := CanonicalString(v)
	if want := `{"neg":-2.5,"pi":3.14159,"small":0.001,"tenths":0.1}`; got != want {
		t.Fatalf("got %q want %q", got, want)
	}
}

func TestCanonicalPreservesLargeIntegers(t *testing.T) {
	v, _ := ParseValue([]byte(`{"max_safe": 9007199254740991, "min_safe": -9007199254740991}`))
	got, _ := CanonicalString(v)
	if want := `{"max_safe":9007199254740991,"min_safe":-9007199254740991}`; got != want {
		t.Fatalf("got %q want %q", got, want)
	}
}

func TestCanonicalNoHTMLEscape(t *testing.T) {
	// Go's default encoder escapes < > & — we must disable that.
	v, _ := ParseValue([]byte(`{"k": "a<b>c&d"}`))
	got, _ := CanonicalString(v)
	if want := `{"k":"a<b>c&d"}`; got != want {
		t.Fatalf("got %q want %q", got, want)
	}
}

func TestCanonicalNestedSortsRecursively(t *testing.T) {
	v, _ := ParseValue([]byte(`{"outer": {"z": 1, "a": 2}, "inner": [{"k": 3, "j": 4}, {"m": 5}]}`))
	got, _ := CanonicalString(v)
	if want := `{"inner":[{"j":4,"k":3},{"m":5}],"outer":{"a":2,"z":1}}`; got != want {
		t.Fatalf("got %q want %q", got, want)
	}
}

func TestSHA256HexKnownVector(t *testing.T) {
	got := SHA256Hex([]byte("abc"))
	if want := "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"; got != want {
		t.Fatalf("got %q want %q", got, want)
	}
}

func TestSHA256PrefixedFormat(t *testing.T) {
	got := SHA256Prefixed([]byte("abc"))
	sum := sha256.Sum256([]byte("abc"))
	want := "sha256:" + hex.EncodeToString(sum[:])
	if got != want {
		t.Fatalf("got %q want %q", got, want)
	}
}

func TestIsSHA256Hex(t *testing.T) {
	if !IsSHA256Hex("sha256:" + hex.EncodeToString(make([]byte, 32))) {
		t.Fatal("expected 64-char lowercase hex with prefix to be valid")
	}
	if IsSHA256Hex("sha256:abc") {
		t.Fatal("short hex must be rejected")
	}
	if IsSHA256Hex("md5:" + hex.EncodeToString(make([]byte, 32))) {
		t.Fatal("wrong algorithm prefix must be rejected")
	}
	if IsSHA256Hex("sha256:" + "Z" + hex.EncodeToString(make([]byte, 32))[1:]) {
		t.Fatal("non-hex char must be rejected")
	}
	if IsSHA256Hex("sha256:" + "A" + hex.EncodeToString(make([]byte, 32))[1:]) {
		t.Fatal("uppercase hex must be rejected (v0.1.0 declares lowercase)")
	}
}
