package vectors

import (
	"testing"

	"wiseorder/go_verifier/internal/jcs"
)

// --- helpers ---

func parseInput(t *testing.T, raw string) map[string]interface{} {
	t.Helper()
	v, err := jcs.ParseValue([]byte(raw))
	if err != nil {
		t.Fatalf("parse: %v", err)
	}
	obj, ok := v.(map[string]interface{})
	if !ok {
		t.Fatalf("expected object, got %T", v)
	}
	return obj
}

func aBaseInput() string {
	return `{
		"class": "A", "regime": "deterministic_verification", "claim": "x",
		"canonicalization": "RFC8785-JCS", "algorithm": "SHA-256",
		"expected_digest": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
		"observed_digest": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
		"proof": {"type": "integrity_proof", "created_at": "2026-05-10T11:00:00Z"}
	}`
}

// --- Class A ---

func TestClassAVerified(t *testing.T) {
	if d, _ := verifyClassA(parseInput(t, aBaseInput())); d != "VERIFIED" {
		t.Fatalf("want VERIFIED, got %q", d)
	}
}

func TestClassATamperedOnDigestMismatch(t *testing.T) {
	in := parseInput(t, aBaseInput())
	in["observed_digest"] = "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
	if d, _ := verifyClassA(in); d != "TAMPERED" {
		t.Fatalf("want TAMPERED, got %q", d)
	}
}

func TestClassAInvalidOnBadCanonicalization(t *testing.T) {
	in := parseInput(t, aBaseInput())
	in["canonicalization"] = "RFC8785-JCS-v2"
	if d, _ := verifyClassA(in); d != "INVALID" {
		t.Fatalf("want INVALID, got %q", d)
	}
}

func TestClassATelemetryRejected(t *testing.T) {
	in := parseInput(t, aBaseInput())
	in["status"] = "CALIBRATION_IMPROVED"
	if d, _ := verifyClassA(in); d != "INVALID" {
		t.Fatalf("want INVALID, got %q", d)
	}
}

// --- Class B ---

func TestClassBSupported(t *testing.T) {
	in := parseInput(t, `{
		"class":"B","regime":"x","claim":"x",
		"sources":[{"id":"s1"}],
		"timestamps":[{"source_id":"s1","value":"t"}],
		"observations":[{"source_id":"s1","supports_claim":true}],
		"structural_diff":{}, "proof":{"type":"x","created_at":"x"}
	}`)
	if d, _ := verifyClassB(in); d != "SUPPORTED" {
		t.Fatalf("want SUPPORTED, got %q", d)
	}
}

func TestClassBConflicted(t *testing.T) {
	in := parseInput(t, `{
		"class":"B","regime":"x","claim":"x",
		"sources":[{"id":"s1"},{"id":"s2"}],
		"timestamps":[{"source_id":"s1"},{"source_id":"s2"}],
		"observations":[
			{"source_id":"s1","supports_claim":true},
			{"source_id":"s2","supports_claim":false}
		],
		"structural_diff":{}, "proof":{"type":"x","created_at":"x"}
	}`)
	if d, _ := verifyClassB(in); d != "CONFLICTED" {
		t.Fatalf("want CONFLICTED, got %q", d)
	}
}

func TestClassBMissingSourcesInvalid(t *testing.T) {
	in := parseInput(t, `{
		"class":"B","regime":"x","claim":"x",
		"timestamps":[],"observations":[],
		"structural_diff":{},"proof":{"type":"x","created_at":"x"}
	}`)
	if d, _ := verifyClassB(in); d != "INVALID" {
		t.Fatalf("want INVALID, got %q", d)
	}
}

// --- Class C ---

func TestClassCConsensusValid(t *testing.T) {
	in := parseInput(t, `{
		"class":"C","regime":"x","claim":"x",
		"protocol":{"name":"q","version":"0.1.0","required_quorum":2,"eligible_attesters":["a","b","c"]},
		"evidence":[
			{"attester_id":"a","attestation":"approve","eligible":true},
			{"attester_id":"b","attestation":"approve","eligible":true}
		],
		"action_policy":{"action_allowed":false,"action_compelled":false,"reason":""},
		"proof":{"type":"x","created_at":"x"}
	}`)
	if d, _ := verifyClassC(in); d != "CONSENSUS_VALID" {
		t.Fatalf("want CONSENSUS_VALID, got %q", d)
	}
}

func TestClassCReplayInvalid(t *testing.T) {
	in := parseInput(t, `{
		"class":"C","regime":"x","claim":"x",
		"protocol":{"name":"q","version":"0.1.0","required_quorum":2,"eligible_attesters":["a","b"]},
		"evidence":[
			{"attester_id":"a","attestation":"approve","eligible":true},
			{"attester_id":"a","attestation":"approve","eligible":true}
		],
		"action_policy":{"action_allowed":false,"action_compelled":false,"reason":""},
		"proof":{"type":"x","created_at":"x"}
	}`)
	if d, _ := verifyClassC(in); d != "INVALID" {
		t.Fatalf("want INVALID, got %q", d)
	}
}

func TestClassCAutoAuthorizeInvalid(t *testing.T) {
	in := parseInput(t, `{
		"class":"C","regime":"x","claim":"x",
		"protocol":{"name":"q","version":"0.1.0","required_quorum":2,"eligible_attesters":["a","b"]},
		"evidence":[
			{"attester_id":"a","attestation":"approve","eligible":true},
			{"attester_id":"b","attestation":"approve","eligible":true}
		],
		"action_policy":{"action_allowed":true,"action_compelled":false,"reason":"x"},
		"proof":{"type":"x","created_at":"x"}
	}`)
	if d, _ := verifyClassC(in); d != "INVALID" {
		t.Fatalf("want INVALID, got %q", d)
	}
}

func TestClassCProtocolVersionMismatchInvalid(t *testing.T) {
	in := parseInput(t, `{
		"class":"C","regime":"x","claim":"x",
		"protocol":{"name":"q","version":"0.2.0-experimental","required_quorum":2,"eligible_attesters":["a","b"]},
		"evidence":[
			{"attester_id":"a","attestation":"approve","eligible":true},
			{"attester_id":"b","attestation":"approve","eligible":true}
		],
		"action_policy":{"action_allowed":false,"action_compelled":false,"reason":""},
		"proof":{"type":"x","created_at":"x"}
	}`)
	if d, _ := verifyClassC(in); d != "INVALID" {
		t.Fatalf("want INVALID, got %q", d)
	}
}

// --- Class D ---

func dBaseInput() string {
	return `{
		"class":"D","regime":"interpretive_governance","claim":"x",
		"values_frame":{"optimizing_for":["a"],"not_optimizing_for":["b"]},
		"alternatives":[{"id":"alt-1","summary":"x","rejected_because":"y"}],
		"reasoning_trace":[{"step":1,"claim":"x"}],
		"recommended_action":{"kind":"noop","summary":"x"},
		"reversibility_score":0.8,
		"challenge_surface":[{"id":"ch-1","argument":"x"}],
		"calibration":{"calibration_id":"c","review_after":"x","success_signals":[],"failure_signals":[]},
		"commit_chain":[
			{"stage":1,"name":"vf","hash":"sha256:1111111111111111111111111111111111111111111111111111111111111111","content":{"x":1},"depends_on":null,"created_at":"2026-01-01T00:00:00Z"},
			{"stage":2,"name":"alt","hash":"sha256:2222222222222222222222222222222222222222222222222222222222222222","content":{"x":2},"depends_on":"sha256:1111111111111111111111111111111111111111111111111111111111111111","created_at":"2026-01-01T00:00:01Z"}
		],
		"meta_proof":{"process_status":"CONDUCT_VALID","artifact_hash":"sha256:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"}
	}`
}

func TestClassDConductValid(t *testing.T) {
	if d, _ := verifyClassD(parseInput(t, dBaseInput())); d != "CONDUCT_VALID" {
		t.Fatalf("want CONDUCT_VALID, got %q", d)
	}
}

func TestClassDNoAlternativesInvalid(t *testing.T) {
	in := parseInput(t, dBaseInput())
	in["alternatives"] = []interface{}{}
	if d, _ := verifyClassD(in); d != "CONDUCT_INVALID" {
		t.Fatalf("want CONDUCT_INVALID, got %q", d)
	}
}

func TestClassDBrokenDependsOnInvalid(t *testing.T) {
	in := parseInput(t, dBaseInput())
	chain := in["commit_chain"].([]interface{})
	chain[1].(map[string]interface{})["depends_on"] = "sha256:9999999999999999999999999999999999999999999999999999999999999999"
	if d, _ := verifyClassD(in); d != "CONDUCT_INVALID" {
		t.Fatalf("want CONDUCT_INVALID, got %q", d)
	}
}

func TestClassDStageSkipInvalid(t *testing.T) {
	in := parseInput(t, dBaseInput())
	chain := in["commit_chain"].([]interface{})
	chain[1].(map[string]interface{})["stage"] = 3 // skip stage 2
	if d, _ := verifyClassD(in); d != "CONDUCT_INVALID" {
		t.Fatalf("want CONDUCT_INVALID, got %q", d)
	}
}

func TestClassDActionCompelledWithoutQuorum(t *testing.T) {
	in := parseInput(t, dBaseInput())
	in["recommended_action"] = map[string]interface{}{
		"kind": "compelled_irreversible", "summary": "x",
		"compelled": true, "authorization_source": nil,
	}
	in["reversibility_score"] = 0.05
	if d, _ := verifyClassD(in); d != "CONDUCT_INVALID" {
		t.Fatalf("want CONDUCT_INVALID, got %q", d)
	}
}
