package fingerprints

import (
	"path/filepath"
	"testing"
)

func repoRoot(t *testing.T) string {
	t.Helper()
	// internal/fingerprints/*.go -> module root is two levels up.
	wd, err := filepath.Abs(".")
	if err != nil {
		t.Fatal(err)
	}
	// Walk up from .../go_verifier/internal/fingerprints -> .../go_verifier -> repo root.
	module := filepath.Dir(filepath.Dir(wd))
	return filepath.Dir(module)
}

func TestVectorsCountIs33(t *testing.T) {
	_, n, err := VectorsSuiteSHA256(filepath.Join(repoRoot(t), "vectors"))
	if err != nil {
		t.Fatal(err)
	}
	if n != 33 {
		t.Fatalf("want 33 vectors, got %d", n)
	}
}

func TestManifestsCountIs3(t *testing.T) {
	_, n, err := ManifestsSuiteSHA256(filepath.Join(repoRoot(t), "interop", "fixtures"))
	if err != nil {
		t.Fatal(err)
	}
	if n != 3 {
		t.Fatalf("want 3 manifests, got %d", n)
	}
}

func TestCorpusCountIs10(t *testing.T) {
	_, n, err := CorpusSHA256(filepath.Join(repoRoot(t), "canonicalization", "corpus"))
	if err != nil {
		t.Fatal(err)
	}
	if n != 10 {
		t.Fatalf("want 10 corpus entries, got %d", n)
	}
}

func TestComputeAllReturnsAllThree(t *testing.T) {
	r, err := ComputeAll(repoRoot(t))
	if err != nil {
		t.Fatal(err)
	}
	if r.VectorsSuiteSHA256 == "" || r.ManifestsSuiteSHA256 == "" || r.CorpusSHA256 == "" {
		t.Fatalf("missing fingerprint(s): %+v", r)
	}
}
