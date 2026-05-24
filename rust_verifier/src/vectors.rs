// Vector verification — re-derived from SPEC.md and SPEC_LOCK_v0.1.md.
//
// This module is an independent re-implementation of the verdict logic for
// Class A/B/C/D conformance vectors. It MUST NOT import, link against, or
// call out to the Python intellagent_runtime; rules are derived from the
// committed specification documents.
//
// Required behaviors per WORK ORDER 012:
//   - read every file under vectors/*.json
//   - reject malformed structure
//   - reject unsupported protocol versions
//   - re-derive the expected verdict for each vector
//   - report passed / failed counts

use serde::Deserialize;
use serde_json::Value;
use std::collections::HashSet;
use std::fs;
use std::path::{Path, PathBuf};

pub const PROTOCOL_VERSION: &str = "0.1.0";
pub const CANONICAL_SCHEME: &str = "RFC8785-JCS";
pub const CANONICAL_ALGORITHM: &str = "SHA-256";

// v0.2.0 §2.5 (D6): preimage size caps. Measured in canonical JSON bytes.
pub const PREIMAGE_PER_STAGE_CAP_BYTES: usize = 1_048_576; // 1 MiB
pub const PREIMAGE_PER_ARTIFACT_CAP_BYTES: usize = 4_194_304; // 4 MiB

const TELEMETRY_TOKENS: &[&str] = &["CALIBRATION_IMPROVED", "CALIBRATION_DEGRADED"];

const REQUIRED_A: &[&str] = &[
    "class", "regime", "claim", "canonicalization", "algorithm",
    "expected_digest", "observed_digest", "proof",
];
const REQUIRED_B: &[&str] = &[
    "class", "regime", "claim", "sources", "observations",
    "structural_diff", "proof",
];
const REQUIRED_C: &[&str] = &[
    "class", "regime", "claim", "protocol", "evidence",
    "action_policy", "proof",
];
const REQUIRED_D: &[&str] = &[
    "class", "regime", "claim", "values_frame", "alternatives",
    "reasoning_trace", "recommended_action", "reversibility_score",
    "challenge_surface", "calibration", "commit_chain", "meta_proof",
];

#[derive(Debug, Clone)]
pub struct Vector {
    // Diagnostic-only: populated at load time, surfaced via the Debug
    // derive when needed but not read by the verifier's verdict logic.
    #[allow(dead_code)]
    pub file: PathBuf,
    pub vector_id: String,
    pub class: String,
    pub expected_status: String,
    pub input: Value,
    #[allow(dead_code)]
    pub protocol_version: String,
}

#[derive(Debug, Clone)]
pub struct VectorOutcome {
    pub vector_id: String,
    pub class: String,
    pub expected: String,
    pub derived: String,
    pub passed: bool,
    pub reasons: Vec<String>,
}

#[derive(Debug)]
pub enum LoadError {
    Io(std::io::Error),
    Json(serde_json::Error, PathBuf),
    MissingField(&'static str, PathBuf),
    UnsupportedProtocolVersion(String, PathBuf),
    UnknownClass(String, PathBuf),
}

impl std::fmt::Display for LoadError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            LoadError::Io(e) => write!(f, "io: {}", e),
            LoadError::Json(e, p) => write!(f, "json {}: {}", p.display(), e),
            LoadError::MissingField(field, p) => {
                write!(f, "missing field '{}' in {}", field, p.display())
            }
            LoadError::UnsupportedProtocolVersion(v, p) => {
                write!(f, "unsupported protocol_version '{}' in {}", v, p.display())
            }
            LoadError::UnknownClass(c, p) => {
                write!(f, "unknown class '{}' in {}", c, p.display())
            }
        }
    }
}

#[derive(Deserialize)]
struct RawVector {
    vector_id: Option<String>,
    protocol_version: Option<String>,
    class: Option<String>,
    expected_status: Option<String>,
    input: Option<Value>,
}

pub fn load_vector(path: &Path) -> Result<Vector, LoadError> {
    let raw = fs::read(path).map_err(LoadError::Io)?;
    let parsed: RawVector = serde_json::from_slice(&raw)
        .map_err(|e| LoadError::Json(e, path.to_path_buf()))?;
    let vector_id = parsed
        .vector_id
        .ok_or(LoadError::MissingField("vector_id", path.to_path_buf()))?;
    let class = parsed
        .class
        .ok_or(LoadError::MissingField("class", path.to_path_buf()))?;
    let expected_status = parsed
        .expected_status
        .ok_or(LoadError::MissingField("expected_status", path.to_path_buf()))?;
    let input = parsed
        .input
        .ok_or(LoadError::MissingField("input", path.to_path_buf()))?;
    let protocol_version = parsed
        .protocol_version
        .ok_or(LoadError::MissingField(
            "protocol_version",
            path.to_path_buf(),
        ))?;
    if protocol_version != PROTOCOL_VERSION {
        return Err(LoadError::UnsupportedProtocolVersion(
            protocol_version,
            path.to_path_buf(),
        ));
    }
    if !matches!(class.as_str(), "A" | "B" | "C" | "D") {
        return Err(LoadError::UnknownClass(class, path.to_path_buf()));
    }
    Ok(Vector {
        file: path.to_path_buf(),
        vector_id,
        class,
        expected_status,
        input,
        protocol_version,
    })
}

pub fn discover_vectors(dir: &Path) -> Result<Vec<PathBuf>, std::io::Error> {
    let mut paths: Vec<PathBuf> = fs::read_dir(dir)?
        .filter_map(|e| e.ok())
        .filter(|e| e.path().is_file())
        .filter(|e| e.path().extension().is_some_and(|x| x == "ext".to_string().as_str() || x == "json"))
        .map(|e| e.path())
        .filter(|p| p.extension().and_then(|s| s.to_str()) == Some("json"))
        .collect();
    paths.sort();
    Ok(paths)
}

// -- helpers ----------------------------------------------------------------

fn has_telemetry_status(input: &Value) -> bool {
    if let Some(s) = input.get("status").and_then(|v| v.as_str()) {
        TELEMETRY_TOKENS.iter().any(|t| *t == s)
    } else {
        false
    }
}

fn missing_required(input: &Value, required: &[&str]) -> Vec<String> {
    let mut out: Vec<String> = Vec::new();
    for r in required {
        if input.get(r).is_none() {
            out.push((*r).to_string());
        }
    }
    out
}

fn is_sha256_hex(s: &str) -> bool {
    if let Some(rest) = s.strip_prefix("sha256:") {
        rest.len() == 64 && rest.chars().all(|c| c.is_ascii_hexdigit() && (!c.is_ascii_alphabetic() || c.is_ascii_lowercase()))
    } else {
        false
    }
}

// -- per-class verifiers ----------------------------------------------------

fn verify_class_a(input: &Value) -> (String, Vec<String>) {
    let mut reasons = Vec::new();
    if has_telemetry_status(input) {
        return ("INVALID".into(), vec!["telemetry status rejected".into()]);
    }
    let missing = missing_required(input, REQUIRED_A);
    if !missing.is_empty() {
        return ("INVALID".into(), vec![format!("missing field(s): {:?}", missing)]);
    }
    let canon = input.get("canonicalization").and_then(|v| v.as_str()).unwrap_or("");
    if canon != CANONICAL_SCHEME {
        return (
            "INVALID".into(),
            vec![format!(
                "canonicalization MUST be {:?}, got {:?}",
                CANONICAL_SCHEME, canon
            )],
        );
    }
    let alg = input.get("algorithm").and_then(|v| v.as_str()).unwrap_or("");
    if alg != CANONICAL_ALGORITHM {
        return (
            "INVALID".into(),
            vec![format!(
                "algorithm MUST be {:?}, got {:?}",
                CANONICAL_ALGORITHM, alg
            )],
        );
    }
    let expected = input.get("expected_digest").and_then(|v| v.as_str()).unwrap_or("");
    let observed = input.get("observed_digest").and_then(|v| v.as_str()).unwrap_or("");
    if !is_sha256_hex(expected) {
        return (
            "INVALID".into(),
            vec![format!("expected_digest format invalid: {:?}", expected)],
        );
    }
    if !is_sha256_hex(observed) {
        return (
            "INVALID".into(),
            vec![format!("observed_digest format invalid: {:?}", observed)],
        );
    }
    if expected == observed {
        ("VERIFIED".into(), reasons)
    } else {
        reasons.push("expected_digest != observed_digest".into());
        ("TAMPERED".into(), reasons)
    }
}

fn verify_class_b(input: &Value) -> (String, Vec<String>) {
    if has_telemetry_status(input) {
        return ("INVALID".into(), vec!["telemetry status rejected".into()]);
    }
    let missing = missing_required(input, REQUIRED_B);
    if !missing.is_empty() {
        return ("INVALID".into(), vec![format!("missing field(s): {:?}", missing)]);
    }
    let sources = input.get("sources").and_then(|v| v.as_array()).cloned().unwrap_or_default();
    if sources.is_empty() {
        return ("INVALID".into(), vec!["sources missing or empty (B1)".into()]);
    }
    let observations = input.get("observations").and_then(|v| v.as_array()).cloned().unwrap_or_default();
    let timestamps = input.get("timestamps").and_then(|v| v.as_array()).cloned().unwrap_or_default();
    if observations.len() < sources.len() && timestamps.len() >= sources.len() {
        return (
            "INVALID".into(),
            vec!["selective omission: declared sources/timestamps exceed observations (B1/B2)".into()],
        );
    }
    // Replay drift: same input_digest, different observed_result_digest.
    let mut seen_inputs: std::collections::HashMap<String, String> = std::collections::HashMap::new();
    for obs in &observations {
        if let (Some(inp), Some(out)) = (
            obs.get("input_digest").and_then(|v| v.as_str()),
            obs.get("observed_result_digest").and_then(|v| v.as_str()),
        ) {
            if let Some(prev) = seen_inputs.get(inp) {
                if prev != out {
                    return (
                        "CONFLICTED".into(),
                        vec![format!("replay drift: input_digest {} produced different observed_result_digest values", inp)],
                    );
                }
            }
            seen_inputs.insert(inp.to_string(), out.to_string());
        }
    }
    // supports_claim distribution.
    let sc: Vec<Option<bool>> = observations
        .iter()
        .map(|o| o.get("supports_claim").map(|v| v.as_bool()).flatten().map(Some).unwrap_or(None))
        .map(|b| match b {
            Some(true) => Some(true),
            Some(false) => Some(false),
            None => None,
        })
        .collect();
    // More careful: distinguish missing-key vs explicit null.
    let mut has_true = false;
    let mut has_false = false;
    let mut has_null = false;
    for obs in &observations {
        match obs.get("supports_claim") {
            Some(v) if v.is_boolean() && v.as_bool() == Some(true) => has_true = true,
            Some(v) if v.is_boolean() && v.as_bool() == Some(false) => has_false = true,
            Some(v) if v.is_null() => has_null = true,
            _ => {}
        }
    }
    if has_true && has_false {
        return (
            "CONFLICTED".into(),
            vec!["observations contain both supports_claim=true and false".into()],
        );
    }
    let only_null = !sc.is_empty() && !has_true && !has_false && has_null;
    if only_null {
        return (
            "INSUFFICIENT_EVIDENCE".into(),
            vec!["all observations have supports_claim=null".into()],
        );
    }
    if has_true && !has_false && !has_null {
        return ("SUPPORTED".into(), Vec::new());
    }
    (
        "INSUFFICIENT_EVIDENCE".into(),
        vec!["unable to derive positive support".into()],
    )
}

fn verify_class_c(input: &Value) -> (String, Vec<String>) {
    if has_telemetry_status(input) {
        return ("INVALID".into(), vec!["telemetry status rejected".into()]);
    }
    let missing = missing_required(input, REQUIRED_C);
    if !missing.is_empty() {
        return ("INVALID".into(), vec![format!("missing field(s): {:?}", missing)]);
    }
    let protocol = match input.get("protocol").and_then(|v| v.as_object()) {
        Some(o) => o,
        None => return ("INVALID".into(), vec!["protocol field malformed".into()]),
    };
    let version = protocol.get("version").and_then(|v| v.as_str()).unwrap_or("");
    if version != PROTOCOL_VERSION {
        return (
            "INVALID".into(),
            vec![format!(
                "protocol.version MUST be {:?}, got {:?}",
                PROTOCOL_VERSION, version
            )],
        );
    }
    let eligible: Vec<String> = match protocol.get("eligible_attesters").and_then(|v| v.as_array()) {
        Some(a) => a.iter().filter_map(|x| x.as_str().map(String::from)).collect(),
        None => return ("INVALID".into(), vec!["eligible_attesters missing".into()]),
    };
    if eligible.is_empty() {
        return ("INVALID".into(), vec!["eligible_attesters empty".into()]);
    }
    let required_quorum = match protocol.get("required_quorum").and_then(|v| v.as_i64()) {
        Some(q) if q > 0 => q as usize,
        _ => return ("INVALID".into(), vec!["required_quorum missing or non-positive".into()]),
    };
    let evidence = input.get("evidence").and_then(|v| v.as_array()).cloned().unwrap_or_default();
    let eligible_set: HashSet<&str> = eligible.iter().map(|s| s.as_str()).collect();
    let mut seen_attesters: HashSet<String> = HashSet::new();
    let mut approve_count = 0;
    for ev in &evidence {
        let ev_obj = match ev.as_object() {
            Some(o) => o,
            None => return ("INVALID".into(), vec!["evidence entry malformed".into()]),
        };
        let aid = ev_obj.get("attester_id").and_then(|v| v.as_str()).unwrap_or("");
        if !eligible_set.contains(aid) {
            return (
                "INVALID".into(),
                vec![format!("unauthorized attester: {:?}", aid)],
            );
        }
        if let Some(b) = ev_obj.get("eligible").and_then(|v| v.as_bool()) {
            if !b {
                return (
                    "INVALID".into(),
                    vec![format!("evidence claims ineligibility for {:?}", aid)],
                );
            }
        }
        if seen_attesters.contains(aid) {
            return (
                "INVALID".into(),
                vec![format!(
                    "duplicate attestation from {:?} (replay poisoning)",
                    aid
                )],
            );
        }
        seen_attesters.insert(aid.to_string());
        if ev_obj.get("attestation").and_then(|v| v.as_str()) == Some("approve") {
            approve_count += 1;
        }
    }
    // Authorization separation: action_allowed=true requires authorization_source.
    let action_policy = match input.get("action_policy").and_then(|v| v.as_object()) {
        Some(o) => o,
        None => return ("INVALID".into(), vec!["action_policy malformed".into()]),
    };
    let action_allowed = action_policy
        .get("action_allowed")
        .and_then(|v| v.as_bool())
        .unwrap_or(false);
    let auth_source = action_policy
        .get("authorization_source")
        .and_then(|v| v.as_str())
        .filter(|s| !s.is_empty());
    if action_allowed && auth_source.is_none() {
        return (
            "INVALID".into(),
            vec!["action_allowed=true REQUIRES authorization_source (AG2/AG3)".into()],
        );
    }
    if action_allowed && approve_count < required_quorum {
        return (
            "INVALID".into(),
            vec!["action_allowed=true with quorum below required_quorum (authority escalation)".into()],
        );
    }
    if approve_count >= required_quorum {
        return ("CONSENSUS_VALID".into(), Vec::new());
    }
    if input.get("process_closed_at").is_some() {
        return (
            "CONSENSUS_FAILED".into(),
            vec![format!(
                "process closed with {}/{} approvals",
                approve_count, required_quorum
            )],
        );
    }
    (
        "CONSENSUS_PENDING".into(),
        vec![format!(
            "{}/{} approvals collected",
            approve_count, required_quorum
        )],
    )
}

fn verify_class_d(input: &Value) -> (String, Vec<String>) {
    if has_telemetry_status(input) {
        return ("CONDUCT_INVALID".into(), vec!["telemetry status rejected".into()]);
    }
    // D4: any non-Class-D status on input is a structural error.
    let bad_status = ["VERIFIED", "TAMPERED", "SUPPORTED", "CONSENSUS_VALID"];
    if let Some(s) = input.get("status").and_then(|v| v.as_str()) {
        if bad_status.contains(&s) {
            return (
                "CONDUCT_INVALID".into(),
                vec![format!("non-Class-D status {:?} forbidden by D4", s)],
            );
        }
    }
    let missing = missing_required(input, REQUIRED_D);
    if !missing.is_empty() {
        return (
            "CONDUCT_INVALID".into(),
            vec![format!("missing field(s): {:?}", missing)],
        );
    }
    let alternatives = input.get("alternatives").and_then(|v| v.as_array());
    if alternatives.map(|a| a.is_empty()).unwrap_or(true) {
        return ("CONDUCT_INVALID".into(), vec!["alternatives empty (D2)".into()]);
    }
    let challenge = input.get("challenge_surface").and_then(|v| v.as_array());
    if challenge.map(|a| a.is_empty()).unwrap_or(true) {
        return ("CONDUCT_INVALID".into(), vec!["challenge_surface empty (D3)".into()]);
    }
    // Forbidden coupling: compelled action with low reversibility (AG2).
    let rev = input
        .get("reversibility_score")
        .and_then(|v| v.as_f64())
        .unwrap_or(1.0);
    let recommended = input
        .get("recommended_action")
        .and_then(|v| v.as_object());
    let compelled = recommended
        .and_then(|o| o.get("compelled").and_then(|v| v.as_bool()))
        .unwrap_or(false);
    if compelled && rev < 0.1 {
        return (
            "CONDUCT_INVALID".into(),
            vec![
                "recommended_action.compelled=true with reversibility_score<0.1 is a forbidden coupling (AG2)"
                    .into(),
            ],
        );
    }
    // Commit chain: CC1..CC4 invariants.
    let chain = match input.get("commit_chain").and_then(|v| v.as_array()) {
        Some(a) if !a.is_empty() => a.clone(),
        _ => return ("CONDUCT_INVALID".into(), vec!["commit_chain empty (CC3)".into()]),
    };
    let mut prev_stage: i64 = 0;
    let mut prev_hash: Option<String> = None;
    let mut prev_time = String::new();
    let mut seen_hash_content: std::collections::HashMap<String, String> =
        std::collections::HashMap::new();
    let mut total_canonical_bytes: usize = 0;
    for entry in &chain {
        let obj = match entry.as_object() {
            Some(o) => o,
            None => return ("CONDUCT_INVALID".into(), vec!["commit_chain entry malformed".into()]),
        };
        let stage = obj.get("stage").and_then(|v| v.as_i64()).unwrap_or(0);
        if stage <= 0 {
            return ("CONDUCT_INVALID".into(), vec!["stage missing or non-positive".into()]);
        }
        if stage != prev_stage + 1 {
            return (
                "CONDUCT_INVALID".into(),
                vec![format!(
                    "stage numbers non-contiguous: expected {}, got {} (CC3/CC4)",
                    prev_stage + 1,
                    stage
                )],
            );
        }
        let hash = match obj.get("hash").and_then(|v| v.as_str()) {
            Some(h) if is_sha256_hex(h) => h.to_string(),
            _ => return ("CONDUCT_INVALID".into(), vec!["stage hash format invalid".into()]),
        };
        let content = obj.get("content");
        let is_empty_content = match content {
            None => true,
            Some(Value::Null) => true,
            Some(Value::Object(m)) => m.is_empty(),
            Some(Value::Array(a)) => a.is_empty(),
            Some(_) => false,
        };
        if is_empty_content {
            return (
                "CONDUCT_INVALID".into(),
                vec![format!("stage {} preimage content missing or empty (CC1)", stage)],
            );
        }
        // v0.2.0 §2.5 D6: per-stage and per-artifact preimage size caps.
        let canonical_content_bytes = crate::jcs::canonical_bytes(
            content.unwrap_or(&Value::Null),
        )
        .len();
        if canonical_content_bytes > PREIMAGE_PER_STAGE_CAP_BYTES {
            return (
                "CONDUCT_INVALID".into(),
                vec![format!(
                    "PREIMAGE_OVERSIZED: stage {} canonical content {} bytes exceeds per-stage cap {} (D6)",
                    stage, canonical_content_bytes, PREIMAGE_PER_STAGE_CAP_BYTES
                )],
            );
        }
        total_canonical_bytes += canonical_content_bytes;
        if total_canonical_bytes > PREIMAGE_PER_ARTIFACT_CAP_BYTES {
            return (
                "CONDUCT_INVALID".into(),
                vec![format!(
                    "PREIMAGE_OVERSIZED: artifact canonical preimage total {} bytes exceeds per-artifact cap {} (D6)",
                    total_canonical_bytes, PREIMAGE_PER_ARTIFACT_CAP_BYTES
                )],
            );
        }
        let depends_on = obj.get("depends_on");
        if stage == 1 {
            if !matches!(depends_on, Some(Value::Null) | None) {
                return (
                    "CONDUCT_INVALID".into(),
                    vec![format!(
                        "stage 1 depends_on MUST be null, got {:?}",
                        depends_on
                    )],
                );
            }
        } else {
            let dep_str = depends_on.and_then(|v| v.as_str()).unwrap_or("");
            if Some(dep_str.to_string()) != prev_hash {
                return (
                    "CONDUCT_INVALID".into(),
                    vec![format!(
                        "stage {} depends_on does not equal prior stage hash (CC2)",
                        stage
                    )],
                );
            }
        }
        let ts = obj.get("created_at").and_then(|v| v.as_str()).unwrap_or("");
        if ts < prev_time.as_str() {
            return (
                "CONDUCT_INVALID".into(),
                vec![format!("stage {} created_at not monotonic (CC4)", stage)],
            );
        }
        let serial = serde_json::to_string(content.unwrap_or(&Value::Null)).unwrap_or_default();
        if let Some(existing) = seen_hash_content.get(&hash) {
            if existing != &serial {
                return (
                    "CONDUCT_INVALID".into(),
                    vec![format!(
                        "forged commit chain: identical hash {} under differing content",
                        hash
                    )],
                );
            }
        }
        seen_hash_content.insert(hash.clone(), serial);
        prev_stage = stage;
        prev_hash = Some(hash);
        prev_time = ts.to_string();
    }
    ("CONDUCT_VALID".into(), Vec::new())
}

pub fn verify_input(class: &str, input: &Value) -> (String, Vec<String>) {
    match class {
        "A" => verify_class_a(input),
        "B" => verify_class_b(input),
        "C" => verify_class_c(input),
        "D" => verify_class_d(input),
        _ => ("INVALID".into(), vec![format!("unknown class: {}", class)]),
    }
}

pub fn verify_vector(v: &Vector) -> VectorOutcome {
    let (derived, reasons) = verify_input(&v.class, &v.input);
    VectorOutcome {
        vector_id: v.vector_id.clone(),
        class: v.class.clone(),
        expected: v.expected_status.clone(),
        passed: derived == v.expected_status,
        derived,
        reasons,
    }
}

pub fn verify_all(dir: &Path) -> Result<Vec<VectorOutcome>, LoadError> {
    let mut outcomes = Vec::new();
    let mut paths = discover_vectors(dir).map_err(LoadError::Io)?;
    paths.sort();
    for p in paths {
        let v = load_vector(&p)?;
        outcomes.push(verify_vector(&v));
    }
    outcomes.sort_by(|a, b| a.vector_id.cmp(&b.vector_id));
    Ok(outcomes)
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    fn class_a_base() -> Value {
        json!({
            "class": "A", "regime": "deterministic_verification", "claim": "x",
            "canonicalization": "RFC8785-JCS", "algorithm": "SHA-256",
            "expected_digest": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "observed_digest": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "proof": {"type": "integrity_proof", "created_at": "2026-05-10T11:00:00Z"}
        })
    }

    #[test]
    fn class_a_verified_round_trip() {
        let (v, _) = verify_class_a(&class_a_base());
        assert_eq!(v, "VERIFIED");
    }

    #[test]
    fn class_a_tampered_on_digest_mismatch() {
        let mut a = class_a_base();
        a["observed_digest"] = json!("sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb");
        let (v, _) = verify_class_a(&a);
        assert_eq!(v, "TAMPERED");
    }

    #[test]
    fn class_a_invalid_on_bad_canon() {
        let mut a = class_a_base();
        a["canonicalization"] = json!("RFC8785-JCS-v2");
        let (v, _) = verify_class_a(&a);
        assert_eq!(v, "INVALID");
    }

    #[test]
    fn class_a_telemetry_rejected() {
        let mut a = class_a_base();
        a["status"] = json!("CALIBRATION_IMPROVED");
        let (v, _) = verify_class_a(&a);
        assert_eq!(v, "INVALID");
    }
}
