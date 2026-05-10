// Fingerprint reproduction for the three frozen v0.1.0 anchors.
//
// Formulas (re-derived from spec, NOT translated from Python):
//
//   vectors_suite_sha256
//     For each file under vectors/*.json:
//       - parse to obtain its vector_id
//       - compute SHA-256 of the raw file bytes (lowercase hex, no prefix)
//     Sort by vector_id.
//     Concatenate the hex digests with single '\n' between them (no
//     trailing newline). UTF-8 encode. SHA-256 the result.
//     Output: "sha256:<lowercase 64 hex>".
//
//   manifests_suite_sha256
//     Same shape, but over interop/fixtures/<impl>/*.manifest.json,
//     sorted by `fixture_id` field.
//
//   corpus_sha256
//     For each file under canonicalization/corpus/*.json in lexicographic
//     filename order:
//       file_id := filename without ".json"
//       canonical := canonical_bytes(parsed_value)  // tooling-internal
//     Feed each (file_id-as-UTF-8 || 0x00 || canonical || 0x00) into a
//     single running SHA-256.
//     Output: "sha256:<lowercase 64 hex>".
//
// The three formulas are independent of the Python runtime; only sha2 and
// serde_json from Rust crates.io are used. The canonicalization rule used
// by corpus_sha256 is implemented in jcs.rs.

use crate::jcs;
use serde_json::Value;
use sha2::{Digest, Sha256};
use std::fs;
use std::path::{Path, PathBuf};

#[derive(Debug, Clone)]
pub struct FingerprintReport {
    pub vectors_suite_sha256: String,
    pub manifests_suite_sha256: String,
    pub corpus_sha256: String,
    pub vector_count: usize,
    pub manifest_count: usize,
    pub corpus_entry_count: usize,
}

#[derive(Debug)]
pub enum FpError {
    Io(std::io::Error),
    Json(serde_json::Error, PathBuf),
    MissingIdField(&'static str, PathBuf),
}

impl std::fmt::Display for FpError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            FpError::Io(e) => write!(f, "io: {}", e),
            FpError::Json(e, p) => write!(f, "json {}: {}", p.display(), e),
            FpError::MissingIdField(field, p) => {
                write!(f, "missing {} in {}", field, p.display())
            }
        }
    }
}

fn list_json(dir: &Path) -> Result<Vec<PathBuf>, std::io::Error> {
    let mut paths: Vec<PathBuf> = fs::read_dir(dir)?
        .filter_map(|e| e.ok())
        .map(|e| e.path())
        .filter(|p| p.is_file() && p.extension().and_then(|s| s.to_str()) == Some("json"))
        .collect();
    paths.sort();
    Ok(paths)
}

fn list_json_recursive_for_suffix(dir: &Path, suffix: &str) -> Result<Vec<PathBuf>, std::io::Error> {
    let mut out: Vec<PathBuf> = Vec::new();
    let mut stack: Vec<PathBuf> = vec![dir.to_path_buf()];
    while let Some(d) = stack.pop() {
        if !d.is_dir() {
            continue;
        }
        for entry in fs::read_dir(&d)? {
            let entry = entry?;
            let p = entry.path();
            if p.is_dir() {
                stack.push(p);
            } else if p.is_file() {
                if let Some(name) = p.file_name().and_then(|s| s.to_str()) {
                    if name.ends_with(suffix) {
                        out.push(p);
                    }
                }
            }
        }
    }
    out.sort();
    Ok(out)
}

// ---------------- vectors_suite_sha256 ----------------

pub fn vectors_suite_sha256(vectors_dir: &Path) -> Result<(String, usize), FpError> {
    let paths = list_json(vectors_dir).map_err(FpError::Io)?;
    // (vector_id, raw-bytes-sha256-hex)
    let mut pairs: Vec<(String, String)> = Vec::with_capacity(paths.len());
    for p in paths {
        let raw = fs::read(&p).map_err(FpError::Io)?;
        let parsed: Value =
            serde_json::from_slice(&raw).map_err(|e| FpError::Json(e, p.clone()))?;
        let vector_id = parsed
            .get("vector_id")
            .and_then(|v| v.as_str())
            .ok_or(FpError::MissingIdField("vector_id", p.clone()))?
            .to_string();
        pairs.push((vector_id, jcs::sha256_hex(&raw)));
    }
    pairs.sort_by(|a, b| a.0.cmp(&b.0));
    let count = pairs.len();
    let suite_input = pairs
        .into_iter()
        .map(|(_, h)| h)
        .collect::<Vec<_>>()
        .join("\n");
    let mut hasher = Sha256::new();
    hasher.update(suite_input.as_bytes());
    Ok((format!("sha256:{}", jcs_hex(&hasher.finalize())), count))
}

// ---------------- manifests_suite_sha256 ----------------

pub fn manifests_suite_sha256(fixtures_dir: &Path) -> Result<(String, usize), FpError> {
    // Manifests are *.manifest.json under interop/fixtures/<impl>/.
    //
    // Per spec rule re-derived from interop/scripts/run_interop_checks.py:
    // per-manifest digest is the "sha256:" + hex form (NOT bare hex; this is
    // the one place where the suite-aggregation input uses the prefixed
    // form, distinct from vectors_suite_sha256 which uses bare hex).
    let paths = list_json_recursive_for_suffix(fixtures_dir, ".manifest.json")
        .map_err(FpError::Io)?;
    let mut pairs: Vec<(String, String)> = Vec::with_capacity(paths.len());
    for p in paths {
        let raw = fs::read(&p).map_err(FpError::Io)?;
        let parsed: Value =
            serde_json::from_slice(&raw).map_err(|e| FpError::Json(e, p.clone()))?;
        let fixture_id = parsed
            .get("fixture_id")
            .and_then(|v| v.as_str())
            .ok_or(FpError::MissingIdField("fixture_id", p.clone()))?
            .to_string();
        let prefixed = format!("sha256:{}", jcs::sha256_hex(&raw));
        pairs.push((fixture_id, prefixed));
    }
    pairs.sort_by(|a, b| a.0.cmp(&b.0));
    let count = pairs.len();
    let suite_input = pairs
        .into_iter()
        .map(|(_, h)| h)
        .collect::<Vec<_>>()
        .join("\n");
    let mut hasher = Sha256::new();
    hasher.update(suite_input.as_bytes());
    Ok((format!("sha256:{}", jcs_hex(&hasher.finalize())), count))
}

// ---------------- corpus_sha256 ----------------

pub fn corpus_sha256(corpus_dir: &Path) -> Result<(String, usize), FpError> {
    let paths = list_json(corpus_dir).map_err(FpError::Io)?;
    let mut hasher = Sha256::new();
    let mut count = 0;
    for p in paths {
        let raw = fs::read(&p).map_err(FpError::Io)?;
        let value: Value = serde_json::from_slice(&raw).map_err(|e| FpError::Json(e, p.clone()))?;
        let file_id = p
            .file_stem()
            .and_then(|s| s.to_str())
            .map(String::from)
            .ok_or(FpError::MissingIdField("file_stem", p.clone()))?;
        let canonical = jcs::canonical_bytes(&value);
        hasher.update(file_id.as_bytes());
        hasher.update(&[0u8]);
        hasher.update(&canonical);
        hasher.update(&[0u8]);
        count += 1;
    }
    Ok((format!("sha256:{}", jcs_hex(&hasher.finalize())), count))
}

// ---------------- combined ----------------

pub fn compute_all(repo_root: &Path) -> Result<FingerprintReport, FpError> {
    let (vec_fp, vec_n) = vectors_suite_sha256(&repo_root.join("vectors"))?;
    let (man_fp, man_n) = manifests_suite_sha256(&repo_root.join("interop").join("fixtures"))?;
    let (cor_fp, cor_n) = corpus_sha256(&repo_root.join("canonicalization").join("corpus"))?;
    Ok(FingerprintReport {
        vectors_suite_sha256: vec_fp,
        manifests_suite_sha256: man_fp,
        corpus_sha256: cor_fp,
        vector_count: vec_n,
        manifest_count: man_n,
        corpus_entry_count: cor_n,
    })
}

// ---------------- helpers ----------------

fn jcs_hex(bytes: &[u8]) -> String {
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

    fn repo_root() -> PathBuf {
        // tests run from rust_verifier/ — parent is the repo root.
        PathBuf::from(env!("CARGO_MANIFEST_DIR"))
            .parent()
            .unwrap()
            .to_path_buf()
    }

    #[test]
    fn vectors_count_is_33() {
        let (_, n) = vectors_suite_sha256(&repo_root().join("vectors")).unwrap();
        assert_eq!(n, 33);
    }

    #[test]
    fn manifests_count_is_3() {
        let (_, n) =
            manifests_suite_sha256(&repo_root().join("interop").join("fixtures")).unwrap();
        assert_eq!(n, 3);
    }

    #[test]
    fn corpus_count_is_10() {
        let (_, n) = corpus_sha256(&repo_root().join("canonicalization").join("corpus")).unwrap();
        assert_eq!(n, 10);
    }
}
