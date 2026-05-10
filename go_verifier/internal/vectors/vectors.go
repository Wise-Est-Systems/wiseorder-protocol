// Package vectors implements vector verdict logic for WiseOrder v0.1.0
// re-derived from SPEC.md and SPEC_LOCK_v0.1.md.
//
// Independence note (WORK ORDER 013):
//
//   This package does NOT import the Python intellagent_runtime, does NOT
//   shell out to python, and does NOT depend on the Rust verifier track.
//   Verdict rules are derived from the committed specification documents.
//
// Classes A / B / C / D are implemented in separate verify_class_X
// functions. Each returns (derived_status, reasons).

package vectors

import (
	"bytes"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"wiseorder/go_verifier/internal/jcs"
)

const (
	ProtocolVersion    = "0.1.0"
	CanonicalScheme    = "RFC8785-JCS"
	CanonicalAlgorithm = "SHA-256"
)

var telemetryTokens = map[string]struct{}{
	"CALIBRATION_IMPROVED": {},
	"CALIBRATION_DEGRADED": {},
}

var (
	requiredA = []string{"class", "regime", "claim", "canonicalization", "algorithm", "expected_digest", "observed_digest", "proof"}
	requiredB = []string{"class", "regime", "claim", "sources", "observations", "structural_diff", "proof"}
	requiredC = []string{"class", "regime", "claim", "protocol", "evidence", "action_policy", "proof"}
	requiredD = []string{"class", "regime", "claim", "values_frame", "alternatives", "reasoning_trace", "recommended_action", "reversibility_score", "challenge_surface", "calibration", "commit_chain", "meta_proof"}
)

// Vector is the parsed form of a vectors/*.json file.
type Vector struct {
	File            string
	VectorID        string
	Class           string
	ExpectedStatus  string
	Input           map[string]interface{}
	ProtocolVersion string
}

// Outcome is the result of running the verdict logic on a single vector.
type Outcome struct {
	VectorID string
	Class    string
	Expected string
	Derived  string
	Passed   bool
	Reasons  []string
}

// LoadError is returned by Load on malformed or unsupported vector files.
type LoadError struct {
	Kind string
	Path string
	Msg  string
}

func (e *LoadError) Error() string {
	if e.Path == "" {
		return fmt.Sprintf("%s: %s", e.Kind, e.Msg)
	}
	return fmt.Sprintf("%s: %s: %s", e.Kind, e.Path, e.Msg)
}

// Load reads and validates a single vector file from disk.
func Load(path string) (*Vector, error) {
	raw, err := os.ReadFile(path)
	if err != nil {
		return nil, &LoadError{Kind: "io", Path: path, Msg: err.Error()}
	}
	val, err := jcs.ParseValue(raw)
	if err != nil {
		return nil, &LoadError{Kind: "json", Path: path, Msg: err.Error()}
	}
	obj, ok := val.(map[string]interface{})
	if !ok {
		return nil, &LoadError{Kind: "malformed", Path: path, Msg: "top-level value must be an object"}
	}
	vectorID, _ := obj["vector_id"].(string)
	class, _ := obj["class"].(string)
	expected, _ := obj["expected_status"].(string)
	pv, _ := obj["protocol_version"].(string)
	input, _ := obj["input"].(map[string]interface{})

	if vectorID == "" {
		return nil, &LoadError{Kind: "missing_field", Path: path, Msg: "vector_id"}
	}
	if class == "" {
		return nil, &LoadError{Kind: "missing_field", Path: path, Msg: "class"}
	}
	if expected == "" {
		return nil, &LoadError{Kind: "missing_field", Path: path, Msg: "expected_status"}
	}
	if input == nil {
		return nil, &LoadError{Kind: "missing_field", Path: path, Msg: "input"}
	}
	if pv == "" {
		return nil, &LoadError{Kind: "missing_field", Path: path, Msg: "protocol_version"}
	}
	if pv != ProtocolVersion {
		return nil, &LoadError{Kind: "unsupported_protocol_version", Path: path, Msg: pv}
	}
	switch class {
	case "A", "B", "C", "D":
		// ok
	default:
		return nil, &LoadError{Kind: "unknown_class", Path: path, Msg: class}
	}

	return &Vector{
		File:            path,
		VectorID:        vectorID,
		Class:           class,
		ExpectedStatus:  expected,
		Input:           input,
		ProtocolVersion: pv,
	}, nil
}

// Discover returns vectors/*.json paths in lexicographic filename order.
func Discover(dir string) ([]string, error) {
	entries, err := os.ReadDir(dir)
	if err != nil {
		return nil, err
	}
	var out []string
	for _, e := range entries {
		if e.IsDir() {
			continue
		}
		name := e.Name()
		if strings.HasSuffix(name, ".json") {
			out = append(out, filepath.Join(dir, name))
		}
	}
	sort.Strings(out)
	return out, nil
}

// VerifyAll loads every vector under dir, derives its verdict, and returns
// outcomes sorted by vector_id.
func VerifyAll(dir string) ([]Outcome, error) {
	paths, err := Discover(dir)
	if err != nil {
		return nil, err
	}
	var outcomes []Outcome
	for _, p := range paths {
		v, err := Load(p)
		if err != nil {
			return nil, err
		}
		outcomes = append(outcomes, VerifyVector(v))
	}
	sort.Slice(outcomes, func(i, j int) bool {
		return outcomes[i].VectorID < outcomes[j].VectorID
	})
	return outcomes, nil
}

// VerifyVector applies the per-class rules and reports the outcome.
func VerifyVector(v *Vector) Outcome {
	derived, reasons := VerifyInput(v.Class, v.Input)
	return Outcome{
		VectorID: v.VectorID,
		Class:    v.Class,
		Expected: v.ExpectedStatus,
		Derived:  derived,
		Passed:   derived == v.ExpectedStatus,
		Reasons:  reasons,
	}
}

// VerifyInput is the per-class dispatcher.
func VerifyInput(class string, input map[string]interface{}) (string, []string) {
	switch class {
	case "A":
		return verifyClassA(input)
	case "B":
		return verifyClassB(input)
	case "C":
		return verifyClassC(input)
	case "D":
		return verifyClassD(input)
	default:
		return "INVALID", []string{fmt.Sprintf("unknown class: %q", class)}
	}
}

// --- helpers ---------------------------------------------------------------

func hasTelemetryStatus(input map[string]interface{}) bool {
	s, _ := input["status"].(string)
	_, ok := telemetryTokens[s]
	return ok
}

func missingRequired(input map[string]interface{}, required []string) []string {
	var missing []string
	for _, r := range required {
		if _, ok := input[r]; !ok {
			missing = append(missing, r)
		}
	}
	return missing
}

func asString(v interface{}) string {
	s, _ := v.(string)
	return s
}

func asBool(v interface{}) (bool, bool) {
	b, ok := v.(bool)
	return b, ok
}

func asArray(v interface{}) []interface{} {
	a, _ := v.([]interface{})
	return a
}

func asObject(v interface{}) map[string]interface{} {
	o, _ := v.(map[string]interface{})
	return o
}

func asInt64(v interface{}) (int64, bool) {
	switch n := v.(type) {
	case json.Number:
		i, err := n.Int64()
		if err != nil {
			return 0, false
		}
		return i, true
	case int:
		return int64(n), true
	case int64:
		return n, true
	}
	return 0, false
}

func asFloat64(v interface{}) (float64, bool) {
	switch n := v.(type) {
	case json.Number:
		f, err := n.Float64()
		if err != nil {
			return 0, false
		}
		return f, true
	case float64:
		return n, true
	}
	return 0, false
}

// --- Class A ---------------------------------------------------------------

func verifyClassA(input map[string]interface{}) (string, []string) {
	if hasTelemetryStatus(input) {
		return "INVALID", []string{"telemetry status rejected"}
	}
	if missing := missingRequired(input, requiredA); len(missing) > 0 {
		return "INVALID", []string{fmt.Sprintf("missing field(s): %v", missing)}
	}
	canon := asString(input["canonicalization"])
	if canon != CanonicalScheme {
		return "INVALID", []string{fmt.Sprintf("canonicalization MUST be %q, got %q", CanonicalScheme, canon)}
	}
	alg := asString(input["algorithm"])
	if alg != CanonicalAlgorithm {
		return "INVALID", []string{fmt.Sprintf("algorithm MUST be %q, got %q", CanonicalAlgorithm, alg)}
	}
	expected := asString(input["expected_digest"])
	observed := asString(input["observed_digest"])
	if !jcs.IsSHA256Hex(expected) {
		return "INVALID", []string{fmt.Sprintf("expected_digest format invalid: %q", expected)}
	}
	if !jcs.IsSHA256Hex(observed) {
		return "INVALID", []string{fmt.Sprintf("observed_digest format invalid: %q", observed)}
	}
	if expected == observed {
		return "VERIFIED", nil
	}
	return "TAMPERED", []string{"expected_digest != observed_digest"}
}

// --- Class B ---------------------------------------------------------------

func verifyClassB(input map[string]interface{}) (string, []string) {
	if hasTelemetryStatus(input) {
		return "INVALID", []string{"telemetry status rejected"}
	}
	if missing := missingRequired(input, requiredB); len(missing) > 0 {
		return "INVALID", []string{fmt.Sprintf("missing field(s): %v", missing)}
	}
	sources := asArray(input["sources"])
	if len(sources) == 0 {
		return "INVALID", []string{"sources missing or empty (B1)"}
	}
	observations := asArray(input["observations"])
	timestamps := asArray(input["timestamps"])
	if len(observations) < len(sources) && len(timestamps) >= len(sources) {
		return "INVALID", []string{"selective omission: declared sources/timestamps exceed observations (B1/B2)"}
	}

	// Replay drift: same input_digest, different observed_result_digest.
	seenInputs := map[string]string{}
	for _, o := range observations {
		obs := asObject(o)
		if obs == nil {
			continue
		}
		inp := asString(obs["input_digest"])
		out := asString(obs["observed_result_digest"])
		if inp == "" || out == "" {
			continue
		}
		if prev, ok := seenInputs[inp]; ok && prev != out {
			return "CONFLICTED", []string{fmt.Sprintf("replay drift: input_digest %s produced different observed_result_digest values", inp)}
		}
		seenInputs[inp] = out
	}

	// supports_claim distribution.
	hasTrue, hasFalse, hasNull, anySC := false, false, false, false
	for _, o := range observations {
		obs := asObject(o)
		if obs == nil {
			continue
		}
		sc, present := obs["supports_claim"]
		if !present {
			continue
		}
		anySC = true
		switch v := sc.(type) {
		case bool:
			if v {
				hasTrue = true
			} else {
				hasFalse = true
			}
		case nil:
			hasNull = true
		}
	}
	if hasTrue && hasFalse {
		return "CONFLICTED", []string{"observations contain both supports_claim=true and false"}
	}
	if anySC && !hasTrue && !hasFalse && hasNull {
		return "INSUFFICIENT_EVIDENCE", []string{"all observations have supports_claim=null"}
	}
	if hasTrue && !hasFalse && !hasNull {
		return "SUPPORTED", nil
	}
	return "INSUFFICIENT_EVIDENCE", []string{"unable to derive positive support"}
}

// --- Class C ---------------------------------------------------------------

func verifyClassC(input map[string]interface{}) (string, []string) {
	if hasTelemetryStatus(input) {
		return "INVALID", []string{"telemetry status rejected"}
	}
	if missing := missingRequired(input, requiredC); len(missing) > 0 {
		return "INVALID", []string{fmt.Sprintf("missing field(s): %v", missing)}
	}
	protocol := asObject(input["protocol"])
	if protocol == nil {
		return "INVALID", []string{"protocol field malformed"}
	}
	version := asString(protocol["version"])
	if version != ProtocolVersion {
		return "INVALID", []string{fmt.Sprintf("protocol.version MUST be %q, got %q", ProtocolVersion, version)}
	}
	eligibleArr := asArray(protocol["eligible_attesters"])
	if len(eligibleArr) == 0 {
		return "INVALID", []string{"eligible_attesters missing or empty"}
	}
	eligibleSet := map[string]struct{}{}
	for _, e := range eligibleArr {
		if s := asString(e); s != "" {
			eligibleSet[s] = struct{}{}
		}
	}
	rq, ok := asInt64(protocol["required_quorum"])
	if !ok || rq <= 0 {
		return "INVALID", []string{"required_quorum missing or non-positive"}
	}

	evidence := asArray(input["evidence"])
	seen := map[string]struct{}{}
	approveCount := int64(0)
	for _, ev := range evidence {
		evObj := asObject(ev)
		if evObj == nil {
			return "INVALID", []string{"evidence entry malformed"}
		}
		aid := asString(evObj["attester_id"])
		if _, ok := eligibleSet[aid]; !ok {
			return "INVALID", []string{fmt.Sprintf("unauthorized attester: %q", aid)}
		}
		if b, present := asBool(evObj["eligible"]); present && !b {
			return "INVALID", []string{fmt.Sprintf("evidence claims ineligibility for %q", aid)}
		}
		if _, dup := seen[aid]; dup {
			return "INVALID", []string{fmt.Sprintf("duplicate attestation from %q (replay poisoning)", aid)}
		}
		seen[aid] = struct{}{}
		if asString(evObj["attestation"]) == "approve" {
			approveCount++
		}
	}

	// Authorization separation (AG2/AG3).
	policy := asObject(input["action_policy"])
	if policy == nil {
		return "INVALID", []string{"action_policy malformed"}
	}
	allowed, _ := asBool(policy["action_allowed"])
	authSource := asString(policy["authorization_source"])
	if allowed && authSource == "" {
		return "INVALID", []string{"action_allowed=true REQUIRES authorization_source (AG2/AG3)"}
	}
	if allowed && approveCount < rq {
		return "INVALID", []string{"action_allowed=true with quorum below required_quorum (authority escalation)"}
	}

	if approveCount >= rq {
		return "CONSENSUS_VALID", nil
	}
	if _, closed := input["process_closed_at"]; closed {
		return "CONSENSUS_FAILED", []string{fmt.Sprintf("process closed with %d/%d approvals", approveCount, rq)}
	}
	return "CONSENSUS_PENDING", []string{fmt.Sprintf("%d/%d approvals collected", approveCount, rq)}
}

// --- Class D ---------------------------------------------------------------

func verifyClassD(input map[string]interface{}) (string, []string) {
	if hasTelemetryStatus(input) {
		return "CONDUCT_INVALID", []string{"telemetry status rejected"}
	}
	// D4: any non-Class-D verdict appearing as a status on input is forbidden.
	badStatuses := map[string]struct{}{
		"VERIFIED":        {},
		"TAMPERED":        {},
		"SUPPORTED":       {},
		"CONSENSUS_VALID": {},
	}
	if s := asString(input["status"]); s != "" {
		if _, ok := badStatuses[s]; ok {
			return "CONDUCT_INVALID", []string{fmt.Sprintf("non-Class-D status %q forbidden by D4", s)}
		}
	}
	if missing := missingRequired(input, requiredD); len(missing) > 0 {
		return "CONDUCT_INVALID", []string{fmt.Sprintf("missing field(s): %v", missing)}
	}
	if len(asArray(input["alternatives"])) == 0 {
		return "CONDUCT_INVALID", []string{"alternatives empty (D2)"}
	}
	if len(asArray(input["challenge_surface"])) == 0 {
		return "CONDUCT_INVALID", []string{"challenge_surface empty (D3)"}
	}

	// Forbidden coupling: compelled action with low reversibility (AG2).
	rev, _ := asFloat64(input["reversibility_score"])
	recommended := asObject(input["recommended_action"])
	compelled, _ := asBool(recommended["compelled"])
	if compelled && rev < 0.1 {
		return "CONDUCT_INVALID", []string{"recommended_action.compelled=true with reversibility_score<0.1 is a forbidden coupling (AG2)"}
	}

	// Commit chain: CC1..CC4.
	chain := asArray(input["commit_chain"])
	if len(chain) == 0 {
		return "CONDUCT_INVALID", []string{"commit_chain empty (CC3)"}
	}
	var prevStage int64 = 0
	var prevHash string
	var prevTime string
	seenHash := map[string]string{} // hash -> canonical(content)

	for _, e := range chain {
		entry := asObject(e)
		if entry == nil {
			return "CONDUCT_INVALID", []string{"commit_chain entry malformed"}
		}
		stage, ok := asInt64(entry["stage"])
		if !ok || stage <= 0 {
			return "CONDUCT_INVALID", []string{"stage missing or non-positive"}
		}
		if stage != prevStage+1 {
			return "CONDUCT_INVALID", []string{fmt.Sprintf("stage numbers non-contiguous: expected %d, got %d (CC3/CC4)", prevStage+1, stage)}
		}
		h := asString(entry["hash"])
		if !jcs.IsSHA256Hex(h) {
			return "CONDUCT_INVALID", []string{"stage hash format invalid"}
		}
		content, present := entry["content"]
		emptyContent := false
		if !present || content == nil {
			emptyContent = true
		} else {
			switch c := content.(type) {
			case map[string]interface{}:
				if len(c) == 0 {
					emptyContent = true
				}
			case []interface{}:
				if len(c) == 0 {
					emptyContent = true
				}
			}
		}
		if emptyContent {
			return "CONDUCT_INVALID", []string{fmt.Sprintf("stage %d preimage content missing or empty (CC1)", stage)}
		}
		dep, depPresent := entry["depends_on"]
		if stage == 1 {
			// Must be null or absent.
			if depPresent && dep != nil {
				return "CONDUCT_INVALID", []string{fmt.Sprintf("stage 1 depends_on MUST be null, got %v", dep)}
			}
		} else {
			depStr, _ := dep.(string)
			if depStr != prevHash {
				return "CONDUCT_INVALID", []string{fmt.Sprintf("stage %d depends_on does not equal prior stage hash (CC2)", stage)}
			}
		}
		ts := asString(entry["created_at"])
		if prevTime != "" && ts < prevTime {
			return "CONDUCT_INVALID", []string{fmt.Sprintf("stage %d created_at not monotonic (CC4)", stage)}
		}
		// Forgery detection: same hash, different canonicalized content.
		var serial []byte
		if present {
			b, err := jcs.CanonicalBytes(content)
			if err == nil {
				serial = b
			}
		}
		if existing, ok := seenHash[h]; ok {
			if existing != string(serial) {
				return "CONDUCT_INVALID", []string{fmt.Sprintf("forged commit chain: identical hash %s under differing content", h)}
			}
		}
		seenHash[h] = string(serial)
		prevStage = stage
		prevHash = h
		prevTime = ts
	}

	return "CONDUCT_VALID", nil
}

// Compile-time guard that asString / json.Number imports stay used.
var _ = bytes.NewReader
