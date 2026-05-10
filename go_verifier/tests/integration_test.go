// Integration tests for the Go verifier binary.
//
// Covers the required behaviors enumerated in WORK ORDER 013:
//   - reads all 33 vectors
//   - rejects malformed vector structure
//   - rejects unsupported protocol version
//   - reproduces all vector verdicts
//   - reads all 10 canonicalization corpus entries
//   - reproduces corpus hashes
//   - reproduces all three frozen fingerprints
//   - produces deterministic output across two runs
//   - does not import, shell out to, or depend on the Python or Rust runtime
//
// The tests drive the binary via `go run`, mirroring the user-facing
// invocation `go run ./go_verifier ...` from the repo root.

package tests

import (
	"bytes"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"

	"wiseorder/go_verifier/internal/jcs"
	"wiseorder/go_verifier/internal/vectors"
)

const (
	expectedVectorsSuite   = "sha256:6168d2075931baa98bba763f9cd537142554aae7b26f19e3e93a60de2ee5bb0f"
	expectedManifestsSuite = "sha256:74eaaa62271f23172232bda43ba3340543e66c46ba1e2f5e6da18d3447a6ba29"
	expectedCorpusSHA      = "sha256:c95685bff48c15abc313c462908b05ac309250bc660c2d802ae51af5a8038b09"
)

func repoRoot(t *testing.T) string {
	t.Helper()
	wd, err := filepath.Abs(".")
	if err != nil {
		t.Fatal(err)
	}
	// go_verifier/tests -> go_verifier -> repo root
	return filepath.Dir(filepath.Dir(wd))
}

func runGoVerifier(t *testing.T, sub string) (int, string) {
	t.Helper()
	root := repoRoot(t)
	cmd := exec.Command("go", "run", "./go_verifier", sub)
	cmd.Dir = root
	var stdout bytes.Buffer
	var stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr
	err := cmd.Run()
	rc := 0
	if err != nil {
		if exitErr, ok := err.(*exec.ExitError); ok {
			rc = exitErr.ExitCode()
		} else {
			t.Fatalf("go run failed to launch: %v (stderr: %s)", err, stderr.String())
		}
	}
	return rc, stdout.String()
}

// Required: reads all vectors.
func TestReadsAllVectors(t *testing.T) {
	rc, out := runGoVerifier(t, "verify-vectors")
	if rc != 0 {
		t.Fatalf("verify-vectors rc=%d\nout:\n%s", rc, out)
	}
	if !strings.Contains(out, "33 vectors, 33 passed, 0 failed") {
		t.Fatalf("expected 33/33 pass, got:\n%s", out)
	}
}

// Required: rejects malformed vector structure.
func TestRejectsMalformedVectorStructure(t *testing.T) {
	tmp, err := os.CreateTemp("", "wo-go-malformed-*.json")
	if err != nil {
		t.Fatal(err)
	}
	defer os.Remove(tmp.Name())
	if _, err := tmp.Write([]byte("{not valid json")); err != nil {
		t.Fatal(err)
	}
	tmp.Close()
	// Direct unit-level: parse must fail.
	raw, _ := os.ReadFile(tmp.Name())
	if _, err := jcs.ParseValue(raw); err == nil {
		t.Fatal("malformed JSON must fail to parse")
	}
	// Direct unit-level on Load: also fails.
	if _, err := vectors.Load(tmp.Name()); err == nil {
		t.Fatal("Load on malformed JSON must fail")
	}
}

// Required: rejects unsupported protocol version.
func TestRejectsUnsupportedProtocolVersion(t *testing.T) {
	tmp, err := os.CreateTemp("", "wo-go-pv-*.json")
	if err != nil {
		t.Fatal(err)
	}
	defer os.Remove(tmp.Name())
	body := `{
		"vector_id": "bad-pv-001",
		"protocol_version": "0.2.0",
		"class": "A",
		"description": "x",
		"input": {},
		"expected_status": "VERIFIED",
		"expected_artifact_fields": ["class"],
		"why": "x"
	}`
	if _, err := tmp.WriteString(body); err != nil {
		t.Fatal(err)
	}
	tmp.Close()
	if _, err := vectors.Load(tmp.Name()); err == nil {
		t.Fatal("expected Load to reject protocol_version != 0.1.0")
	} else if le, ok := err.(*vectors.LoadError); ok && le.Kind != "unsupported_protocol_version" {
		t.Fatalf("expected unsupported_protocol_version, got %v", le.Kind)
	}
}

// Required: reproduces all vector verdicts.
func TestReproducesAllVectorVerdicts(t *testing.T) {
	rc, out := runGoVerifier(t, "verify-vectors")
	if rc != 0 {
		t.Fatalf("rc=%d", rc)
	}
	for _, line := range strings.Split(out, "\n") {
		if strings.HasPrefix(line, "FAIL") {
			t.Fatalf("at least one verdict diverges: %s", line)
		}
	}
}

// Required: reads all canonicalization corpus entries.
func TestReadsAllCanonicalizationCorpusEntries(t *testing.T) {
	rc, out := runGoVerifier(t, "verify-corpus")
	if rc != 0 {
		t.Fatalf("rc=%d", rc)
	}
	if !strings.Contains(out, "10 corpus entries") {
		t.Fatalf("expected 10 corpus entries; got:\n%s", out)
	}
}

// Required: reproduces corpus hashes.
func TestReproducesCorpusHashes(t *testing.T) {
	rc, out := runGoVerifier(t, "verify-corpus")
	if rc != 0 {
		t.Fatalf("rc=%d", rc)
	}
	if !strings.Contains(out, "10 corpus entries, 10 passed, 0 failed") {
		t.Fatalf("expected 10/10 pass; got:\n%s", out)
	}
}

// Required: reproduces all three fingerprints.
func TestReproducesAllThreeFingerprints(t *testing.T) {
	rc, out := runGoVerifier(t, "fingerprints")
	if rc != 0 {
		t.Fatalf("rc=%d\nout:\n%s", rc, out)
	}
	for _, expect := range []string{
		expectedVectorsSuite,
		expectedManifestsSuite,
		expectedCorpusSHA,
		"OVERALL: MATCH",
	} {
		if !strings.Contains(out, expect) {
			t.Fatalf("fingerprints output missing %q\nout:\n%s", expect, out)
		}
	}
}

// Required: deterministic output across two runs.
func TestDeterministicOutputAcrossTwoRuns(t *testing.T) {
	rc1, out1 := runGoVerifier(t, "fingerprints")
	rc2, out2 := runGoVerifier(t, "fingerprints")
	if rc1 != 0 || rc2 != 0 {
		t.Fatalf("rc1=%d rc2=%d", rc1, rc2)
	}
	if out1 != out2 {
		t.Fatal("fingerprints output diverges across runs")
	}
	rc3, out3 := runGoVerifier(t, "verify-vectors")
	rc4, out4 := runGoVerifier(t, "verify-vectors")
	if rc3 != 0 || rc4 != 0 {
		t.Fatalf("rc3=%d rc4=%d", rc3, rc4)
	}
	if out3 != out4 {
		t.Fatal("verify-vectors output diverges across runs")
	}
	rc5, out5 := runGoVerifier(t, "verify-corpus")
	rc6, out6 := runGoVerifier(t, "verify-corpus")
	if rc5 != 0 || rc6 != 0 {
		t.Fatalf("rc5=%d rc6=%d", rc5, rc6)
	}
	if out5 != out6 {
		t.Fatal("verify-corpus output diverges across runs")
	}
}

// Required: no Python or Rust runtime dependency.
//
// Strict static guarantee: scan go.mod and every internal/**/*.go and
// main.go for actual import declarations that reference Python, the
// Python runtime crate, or the Rust verifier track.
func TestDoesNotImportOrDependOnPythonOrRust(t *testing.T) {
	root := repoRoot(t)
	mod := filepath.Join(root, "go_verifier")

	// go.mod: must not require anything outside stdlib.
	gomod, err := os.ReadFile(filepath.Join(mod, "go.mod"))
	if err != nil {
		t.Fatal(err)
	}
	gomodStr := string(gomod)
	for _, forbidden := range []string{
		"intellagent_runtime", "intellagent-runtime",
		"rust_verifier", "wiseorder_rust_verifier",
		"github.com/wiseata", "github.com/winstack",
		"python", "cpython", "pyo3",
	} {
		// Look at non-comment, non-blank lines for actual require entries.
		for _, line := range strings.Split(gomodStr, "\n") {
			trimmed := strings.TrimSpace(line)
			if trimmed == "" || strings.HasPrefix(trimmed, "//") {
				continue
			}
			if strings.Contains(strings.ToLower(trimmed), forbidden) {
				t.Fatalf("go.mod active line references forbidden token %q: %q", forbidden, trimmed)
			}
		}
	}

	// Source files: scan import declarations only.
	var goFiles []string
	walkErr := filepath.WalkDir(mod, func(p string, d os.DirEntry, err error) error {
		if err != nil {
			return err
		}
		if d.IsDir() {
			return nil
		}
		if strings.HasSuffix(p, ".go") {
			goFiles = append(goFiles, p)
		}
		return nil
	})
	if walkErr != nil {
		t.Fatal(walkErr)
	}
	for _, f := range goFiles {
		body, err := os.ReadFile(f)
		if err != nil {
			t.Fatal(err)
		}
		// Detect import lines only (skip comments and string literals).
		inImport := false
		for _, line := range strings.Split(string(body), "\n") {
			trimmed := strings.TrimSpace(line)
			if strings.HasPrefix(trimmed, "//") {
				continue
			}
			if strings.HasPrefix(trimmed, "import (") {
				inImport = true
				continue
			}
			if strings.HasPrefix(trimmed, "import ") {
				// single import line
				checkImportLine(t, f, trimmed)
				continue
			}
			if inImport {
				if trimmed == ")" {
					inImport = false
					continue
				}
				checkImportLine(t, f, trimmed)
			}
		}
	}
}

func checkImportLine(t *testing.T, file, line string) {
	t.Helper()
	lower := strings.ToLower(line)
	for _, forbidden := range []string{
		"intellagent_runtime", "intellagent-runtime",
		"rust_verifier", "wiseorder_rust_verifier",
		"\"python", "\"cpython", "pyo3",
		"os/exec", // disallowed because we MUST NOT shell out to python or rust
	} {
		// `os/exec` is allowed in *this test file*, which calls `go run`.
		// Skip the check for the test file itself.
		if forbidden == "os/exec" && strings.HasSuffix(file, "_test.go") {
			continue
		}
		if strings.Contains(lower, forbidden) {
			t.Fatalf("%s: forbidden import token %q in line: %q", file, forbidden, line)
		}
	}
}

// Sanity: the binary's help command lists the three subcommands.
func TestHelpListsSubcommands(t *testing.T) {
	rc, out := runGoVerifier(t, "help")
	if rc != 0 {
		t.Fatalf("rc=%d", rc)
	}
	for _, sub := range []string{"verify-vectors", "verify-corpus", "fingerprints"} {
		if !strings.Contains(out, sub) {
			t.Fatalf("help missing subcommand %q", sub)
		}
	}
}
