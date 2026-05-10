// WiseOrder Protocol v0.1.0 — first-party independent Go verifier track.
//
// Subcommands:
//   verify-vectors   Re-derive verdicts for every file under vectors/*.json.
//   verify-corpus    Reproduce SHA-256 over canonicalized corpus bytes.
//   fingerprints     Compute all three v0.1.0 frozen fingerprints.
//
// Exit codes:
//   0  every assertion under the chosen subcommand passed
//   1  one or more divergences
//   2  usage / I/O / JSON error
//
// Independence rule: this module MUST NOT import or shell out to Python or
// to the Rust verifier track. Allowed dependencies are stdlib only.

package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"wiseorder/go_verifier/internal/fingerprints"
	"wiseorder/go_verifier/internal/jcs"
	"wiseorder/go_verifier/internal/vectors"
)

const (
	expectedVectorsSuite   = "sha256:6168d2075931baa98bba763f9cd537142554aae7b26f19e3e93a60de2ee5bb0f"
	expectedManifestsSuite = "sha256:74eaaa62271f23172232bda43ba3340543e66c46ba1e2f5e6da18d3447a6ba29"
	expectedCorpusSHA      = "sha256:c95685bff48c15abc313c462908b05ac309250bc660c2d802ae51af5a8038b09"
)

// repoRoot finds the repo root by walking upward from the running binary's
// working directory (or its source file) until it finds a directory that
// contains both `vectors/` and `canonicalization/`.
func repoRoot() (string, error) {
	dir, err := os.Getwd()
	if err != nil {
		return "", err
	}
	abs, err := filepath.Abs(dir)
	if err != nil {
		return "", err
	}
	// Try the current working directory first (for `go run ./go_verifier`
	// invoked from the repo root, cwd IS the repo root).
	for _, d := range []string{abs, filepath.Dir(abs)} {
		if dirHasMarkers(d) {
			return d, nil
		}
	}
	// Fall back to walking upward.
	cur := abs
	for {
		if dirHasMarkers(cur) {
			return cur, nil
		}
		parent := filepath.Dir(cur)
		if parent == cur {
			return "", fmt.Errorf("repo root not found: no ancestor of %s contains vectors/ and canonicalization/", abs)
		}
		cur = parent
	}
}

func dirHasMarkers(d string) bool {
	a, err := os.Stat(filepath.Join(d, "vectors"))
	if err != nil || !a.IsDir() {
		return false
	}
	b, err := os.Stat(filepath.Join(d, "canonicalization"))
	if err != nil || !b.IsDir() {
		return false
	}
	return true
}

// --- verify-vectors --------------------------------------------------------

func cmdVerifyVectors() int {
	root, err := repoRoot()
	if err != nil {
		fmt.Fprintln(os.Stderr, "error:", err)
		return 2
	}
	outcomes, err := vectors.VerifyAll(filepath.Join(root, "vectors"))
	if err != nil {
		fmt.Fprintln(os.Stderr, "error:", err)
		return 2
	}
	fmt.Println("WiseOrder Protocol v0.1.0 — Go verifier: verify-vectors")
	fmt.Println(strings.Repeat("=", 60))
	width := 0
	for _, o := range outcomes {
		if len(o.VectorID) > width {
			width = len(o.VectorID)
		}
	}
	passed := 0
	for _, o := range outcomes {
		verdict := "FAIL"
		if o.Passed {
			verdict = "PASS"
			passed++
		}
		fmt.Printf("%s | %-*s | %s | expected=%-22s derived=%s\n",
			verdict, width, o.VectorID, o.Class, o.Expected, o.Derived)
		if !o.Passed {
			for _, r := range o.Reasons {
				fmt.Printf("       ↳ %s\n", r)
			}
		}
	}
	fmt.Println(strings.Repeat("=", 60))
	fmt.Printf("Summary: %d vectors, %d passed, %d failed\n",
		len(outcomes), passed, len(outcomes)-passed)
	if len(outcomes) == 0 || passed != len(outcomes) {
		return 1
	}
	return 0
}

// --- verify-corpus ---------------------------------------------------------

type goldenDigests struct {
	Digests map[string]string `json:"digests"`
}

func cmdVerifyCorpus() int {
	root, err := repoRoot()
	if err != nil {
		fmt.Fprintln(os.Stderr, "error:", err)
		return 2
	}
	corpusDir := filepath.Join(root, "canonicalization", "corpus")
	goldenPath := filepath.Join(root, "canonicalization", "golden", "golden-digests.json")

	entries, err := os.ReadDir(corpusDir)
	if err != nil {
		fmt.Fprintln(os.Stderr, "error:", err)
		return 2
	}
	var paths []string
	for _, e := range entries {
		if e.IsDir() {
			continue
		}
		if strings.HasSuffix(e.Name(), ".json") {
			paths = append(paths, filepath.Join(corpusDir, e.Name()))
		}
	}
	sort.Strings(paths)

	goldenRaw, err := os.ReadFile(goldenPath)
	if err != nil {
		fmt.Fprintln(os.Stderr, "error reading golden-digests.json:", err)
		return 2
	}
	var golden goldenDigests
	if err := json.Unmarshal(goldenRaw, &golden); err != nil {
		fmt.Fprintln(os.Stderr, "error parsing golden-digests.json:", err)
		return 2
	}

	fmt.Println("WiseOrder Protocol v0.1.0 — Go verifier: verify-corpus")
	fmt.Println(strings.Repeat("=", 60))
	total := 0
	passed := 0
	for _, p := range paths {
		total++
		raw, err := os.ReadFile(p)
		if err != nil {
			fmt.Fprintln(os.Stderr, "error reading", p, err)
			return 2
		}
		v, err := jcs.ParseValue(raw)
		if err != nil {
			fmt.Fprintln(os.Stderr, "error parsing", p, err)
			return 2
		}
		canonical, err := jcs.CanonicalBytes(v)
		if err != nil {
			fmt.Fprintln(os.Stderr, "error canonicalizing", p, err)
			return 2
		}
		fileID := strings.TrimSuffix(filepath.Base(p), ".json")
		observed := jcs.SHA256Prefixed(canonical)
		expected, _ := golden.Digests[fileID]
		ok := expected != "" && observed == expected
		if ok {
			passed++
		}
		verdict := "FAIL"
		if ok {
			verdict = "PASS"
		}
		fmt.Printf("%s | %-25s | observed=%s expected=%s\n",
			verdict, fileID, observed, expected)
	}
	fmt.Println(strings.Repeat("=", 60))
	fmt.Printf("Summary: %d corpus entries, %d passed, %d failed\n",
		total, passed, total-passed)
	if total == 0 || passed != total {
		return 1
	}
	return 0
}

// --- fingerprints ----------------------------------------------------------

func cmdFingerprints() int {
	root, err := repoRoot()
	if err != nil {
		fmt.Fprintln(os.Stderr, "error:", err)
		return 2
	}
	r, err := fingerprints.ComputeAll(root)
	if err != nil {
		fmt.Fprintln(os.Stderr, "error:", err)
		return 2
	}
	fmt.Println("WiseOrder Protocol v0.1.0 — Go verifier: fingerprints")
	fmt.Println(strings.Repeat("=", 72))
	rows := [][3]string{
		{"vectors_suite_sha256", expectedVectorsSuite, r.VectorsSuiteSHA256},
		{"manifests_suite_sha256", expectedManifestsSuite, r.ManifestsSuiteSHA256},
		{"corpus_sha256", expectedCorpusSHA, r.CorpusSHA256},
	}
	allMatch := true
	for _, row := range rows {
		label, expected, observed := row[0], row[1], row[2]
		match := expected == observed
		verdict := "DIVERGENT"
		if match {
			verdict = "MATCH"
		} else {
			allMatch = false
		}
		fmt.Printf("%-22s %s\n", label, verdict)
		fmt.Printf("  expected: %s\n", expected)
		fmt.Printf("  observed: %s\n", observed)
	}
	fmt.Println(strings.Repeat("=", 72))
	fmt.Printf("Counts: vectors=%d manifests=%d corpus_entries=%d\n",
		r.VectorCount, r.ManifestCount, r.CorpusEntryCount)
	if allMatch {
		fmt.Println("OVERALL: MATCH")
		return 0
	}
	fmt.Println("OVERALL: DIVERGENT")
	return 1
}

// --- help / dispatch -------------------------------------------------------

func printHelp() {
	fmt.Println(`WiseOrder Protocol v0.1.0 — first-party independent Go verifier track

USAGE:
  go_verifier <SUBCOMMAND>

SUBCOMMANDS:
  verify-vectors   Re-derive verdicts for every vectors/*.json
  verify-corpus    Reproduce canonicalization corpus digests
  fingerprints     Compute and compare all three v0.1.0 frozen fingerprints
  help             This message

INDEPENDENCE:
  This module does not import or shell out to Python or to the Rust verifier
  track. Classification is FIRST_PARTY_INDEPENDENT_IMPLEMENTATION_TRACK; it is
  NOT third-party validation.`)
}

func main() {
	// Suppress the default flag-usage on -h.
	flag.Usage = printHelp
	args := os.Args[1:]
	if len(args) == 0 {
		printHelp()
		os.Exit(0)
	}
	switch args[0] {
	case "verify-vectors":
		os.Exit(cmdVerifyVectors())
	case "verify-corpus":
		os.Exit(cmdVerifyCorpus())
	case "fingerprints":
		os.Exit(cmdFingerprints())
	case "help", "--help", "-h":
		printHelp()
		os.Exit(0)
	default:
		fmt.Fprintln(os.Stderr, "error: unknown subcommand:", args[0])
		printHelp()
		os.Exit(2)
	}
}
