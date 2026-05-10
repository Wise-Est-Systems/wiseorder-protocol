// Package fingerprints reproduces the three frozen v0.1.0 anchors.
//
// Independence note (WORK ORDER 013):
//
//   This package does NOT import the Python intellagent_runtime, does NOT
//   shell out to python, and does NOT depend on the Rust verifier track.
//   The formulas below are re-derived from SPEC_LOCK_v0.1.md and the
//   committed evidence under reports/, interop/, and canonicalization/.
//
// Formulas:
//
//   vectors_suite_sha256
//     For each file under vectors/*.json:
//       - parse to obtain its vector_id
//       - compute SHA-256 of the raw file bytes (lowercase hex, NO prefix)
//     Sort by vector_id. Join the bare hex digests with a single '\n'
//     (no trailing newline). UTF-8 encode. SHA-256. Output with "sha256:" prefix.
//
//   manifests_suite_sha256
//     Same shape, over interop/fixtures/<impl>/*.manifest.json sorted by
//     fixture_id. Difference: the per-manifest digest is emitted in the
//     "sha256:<hex>" PREFIXED form before joining.
//
//   corpus_sha256
//     For each canonicalization/corpus/*.json in lexicographic filename order:
//       file_id := filename without extension
//       canonical := canonical bytes under the tooling-internal scheme
//     Feed (file_id_utf8 || 0x00 || canonical || 0x00) into a single
//     running SHA-256. Output with "sha256:" prefix.

package fingerprints

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"wiseorder/go_verifier/internal/jcs"
)

// Report is the aggregated result of computing all three fingerprints.
type Report struct {
	VectorsSuiteSHA256   string
	ManifestsSuiteSHA256 string
	CorpusSHA256         string
	VectorCount          int
	ManifestCount        int
	CorpusEntryCount     int
}

func listJSON(dir string) ([]string, error) {
	entries, err := os.ReadDir(dir)
	if err != nil {
		return nil, err
	}
	var out []string
	for _, e := range entries {
		if e.IsDir() {
			continue
		}
		if strings.HasSuffix(e.Name(), ".json") {
			out = append(out, filepath.Join(dir, e.Name()))
		}
	}
	sort.Strings(out)
	return out, nil
}

func listSuffixRecursive(root, suffix string) ([]string, error) {
	var out []string
	err := filepath.WalkDir(root, func(p string, d os.DirEntry, err error) error {
		if err != nil {
			return err
		}
		if d.IsDir() {
			return nil
		}
		if strings.HasSuffix(p, suffix) {
			out = append(out, p)
		}
		return nil
	})
	if err != nil {
		return nil, err
	}
	sort.Strings(out)
	return out, nil
}

// VectorsSuiteSHA256 computes "sha256:<hex>" over the sorted-by-vector_id
// concatenation of per-file bare-hex SHA-256 digests, newline-joined.
func VectorsSuiteSHA256(vectorsDir string) (string, int, error) {
	paths, err := listJSON(vectorsDir)
	if err != nil {
		return "", 0, err
	}
	type pair struct {
		id, digest string
	}
	var pairs []pair
	for _, p := range paths {
		raw, err := os.ReadFile(p)
		if err != nil {
			return "", 0, err
		}
		v, err := jcs.ParseValue(raw)
		if err != nil {
			return "", 0, fmt.Errorf("parse %s: %w", p, err)
		}
		obj, _ := v.(map[string]interface{})
		id, _ := obj["vector_id"].(string)
		if id == "" {
			return "", 0, fmt.Errorf("missing vector_id in %s", p)
		}
		pairs = append(pairs, pair{id: id, digest: jcs.SHA256Hex(raw)})
	}
	sort.Slice(pairs, func(i, j int) bool { return pairs[i].id < pairs[j].id })

	var hashes []string
	for _, pr := range pairs {
		hashes = append(hashes, pr.digest)
	}
	suiteInput := strings.Join(hashes, "\n")
	sum := sha256.Sum256([]byte(suiteInput))
	return "sha256:" + hex.EncodeToString(sum[:]), len(pairs), nil
}

// ManifestsSuiteSHA256 computes "sha256:<hex>" over the sorted-by-fixture_id
// concatenation of per-manifest prefixed-hex SHA-256 digests, newline-joined.
func ManifestsSuiteSHA256(fixturesDir string) (string, int, error) {
	paths, err := listSuffixRecursive(fixturesDir, ".manifest.json")
	if err != nil {
		return "", 0, err
	}
	type pair struct {
		id, digest string
	}
	var pairs []pair
	for _, p := range paths {
		raw, err := os.ReadFile(p)
		if err != nil {
			return "", 0, err
		}
		v, err := jcs.ParseValue(raw)
		if err != nil {
			return "", 0, fmt.Errorf("parse %s: %w", p, err)
		}
		obj, _ := v.(map[string]interface{})
		id, _ := obj["fixture_id"].(string)
		if id == "" {
			return "", 0, fmt.Errorf("missing fixture_id in %s", p)
		}
		pairs = append(pairs, pair{id: id, digest: jcs.SHA256Prefixed(raw)})
	}
	sort.Slice(pairs, func(i, j int) bool { return pairs[i].id < pairs[j].id })

	var hashes []string
	for _, pr := range pairs {
		hashes = append(hashes, pr.digest)
	}
	suiteInput := strings.Join(hashes, "\n")
	sum := sha256.Sum256([]byte(suiteInput))
	return "sha256:" + hex.EncodeToString(sum[:]), len(pairs), nil
}

// CorpusSHA256 streams (file_id || 0x00 || canonical_bytes || 0x00) for
// every canonicalization/corpus/*.json file (lexicographic filename order)
// into a single SHA-256.
func CorpusSHA256(corpusDir string) (string, int, error) {
	paths, err := listJSON(corpusDir)
	if err != nil {
		return "", 0, err
	}
	h := sha256.New()
	count := 0
	for _, p := range paths {
		raw, err := os.ReadFile(p)
		if err != nil {
			return "", 0, err
		}
		v, err := jcs.ParseValue(raw)
		if err != nil {
			return "", 0, fmt.Errorf("parse %s: %w", p, err)
		}
		canonical, err := jcs.CanonicalBytes(v)
		if err != nil {
			return "", 0, fmt.Errorf("canonicalize %s: %w", p, err)
		}
		fileID := strings.TrimSuffix(filepath.Base(p), ".json")
		h.Write([]byte(fileID))
		h.Write([]byte{0})
		h.Write(canonical)
		h.Write([]byte{0})
		count++
	}
	return "sha256:" + hex.EncodeToString(h.Sum(nil)), count, nil
}

// ComputeAll runs all three fingerprint computations against the standard
// layout under repoRoot.
func ComputeAll(repoRoot string) (*Report, error) {
	vec, vN, err := VectorsSuiteSHA256(filepath.Join(repoRoot, "vectors"))
	if err != nil {
		return nil, fmt.Errorf("vectors_suite_sha256: %w", err)
	}
	man, mN, err := ManifestsSuiteSHA256(filepath.Join(repoRoot, "interop", "fixtures"))
	if err != nil {
		return nil, fmt.Errorf("manifests_suite_sha256: %w", err)
	}
	cor, cN, err := CorpusSHA256(filepath.Join(repoRoot, "canonicalization", "corpus"))
	if err != nil {
		return nil, fmt.Errorf("corpus_sha256: %w", err)
	}
	return &Report{
		VectorsSuiteSHA256:   vec,
		ManifestsSuiteSHA256: man,
		CorpusSHA256:         cor,
		VectorCount:          vN,
		ManifestCount:        mN,
		CorpusEntryCount:     cN,
	}, nil
}
