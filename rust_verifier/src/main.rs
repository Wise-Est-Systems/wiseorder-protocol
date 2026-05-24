// WiseOrder Protocol v0.1.0 — first-party independent Rust verifier track.
//
// Subcommands:
//   verify-vectors   Re-derive verdicts for every file under vectors/*.json.
//   verify-corpus    Reproduce SHA-256 over canonicalized corpus bytes.
//   fingerprints     Compute all three v0.1.0 frozen fingerprints.
//   canonicalize     Canonicalize one JSON file; emit canonical bytes + sha256.
//
// Exit codes:
//   0  every assertion under the chosen subcommand passed
//   1  one or more divergences
//   2  usage / I/O / JSON error
//
// Independence rule: this crate MUST NOT import or shell out to the Python
// runtime. Allowed dependencies are documented in Cargo.toml.

use std::path::PathBuf;

mod fingerprints;
mod jcs;
mod vectors;

const EXPECTED_VECTORS_SUITE: &str =
    "sha256:6168d2075931baa98bba763f9cd537142554aae7b26f19e3e93a60de2ee5bb0f";
const EXPECTED_MANIFESTS_SUITE: &str =
    "sha256:74eaaa62271f23172232bda43ba3340543e66c46ba1e2f5e6da18d3447a6ba29";
const EXPECTED_CORPUS_SHA: &str =
    "sha256:c95685bff48c15abc313c462908b05ac309250bc660c2d802ae51af5a8038b09";

fn repo_root() -> PathBuf {
    // Crate manifest lives in rust_verifier/Cargo.toml; the repo root is the
    // parent of CARGO_MANIFEST_DIR.
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .map(|p| p.to_path_buf())
        .expect("rust_verifier/ has a parent (repo root)")
}

fn cmd_verify_vectors() -> i32 {
    let root = repo_root();
    let outcomes = match vectors::verify_all(&root.join("vectors")) {
        Ok(o) => o,
        Err(e) => {
            eprintln!("error: {}", e);
            return 2;
        }
    };
    let total = outcomes.len();
    let passed = outcomes.iter().filter(|o| o.passed).count();
    let failed = total - passed;
    println!("WiseOrder Protocol v0.1.0 — Rust verifier: verify-vectors");
    println!("{}", "=".repeat(60));
    let id_width = outcomes.iter().map(|o| o.vector_id.len()).max().unwrap_or(20);
    for o in &outcomes {
        let verdict = if o.passed { "PASS" } else { "FAIL" };
        println!(
            "{} | {:<width$} | {} | expected={:<22} derived={}",
            verdict,
            o.vector_id,
            o.class,
            o.expected,
            o.derived,
            width = id_width
        );
        if !o.passed {
            for r in &o.reasons {
                println!("       ↳ {}", r);
            }
        }
    }
    println!("{}", "=".repeat(60));
    println!(
        "Summary: {} vectors, {} passed, {} failed",
        total, passed, failed
    );
    if failed == 0 && total > 0 {
        0
    } else {
        1
    }
}

fn cmd_verify_corpus() -> i32 {
    let root = repo_root();
    let corpus_dir = root.join("canonicalization").join("corpus");
    let mut entries: Vec<PathBuf> = match std::fs::read_dir(&corpus_dir) {
        Ok(rd) => rd
            .filter_map(|e| e.ok())
            .map(|e| e.path())
            .filter(|p| p.is_file() && p.extension().and_then(|s| s.to_str()) == Some("json"))
            .collect(),
        Err(e) => {
            eprintln!("error: {}", e);
            return 2;
        }
    };
    entries.sort();
    println!("WiseOrder Protocol v0.1.0 — Rust verifier: verify-corpus");
    println!("{}", "=".repeat(60));
    // Per-entry expected digests from canonicalization/golden/golden-digests.json.
    let golden_path = root
        .join("canonicalization")
        .join("golden")
        .join("golden-digests.json");
    let golden: serde_json::Value = match std::fs::read(&golden_path) {
        Ok(b) => match serde_json::from_slice(&b) {
            Ok(v) => v,
            Err(e) => {
                eprintln!("error reading golden-digests.json: {}", e);
                return 2;
            }
        },
        Err(e) => {
            eprintln!("error reading {}: {}", golden_path.display(), e);
            return 2;
        }
    };
    let expected_digests = golden.get("digests").cloned().unwrap_or(serde_json::Value::Null);

    let mut total = 0;
    let mut passed = 0;
    for p in entries {
        total += 1;
        let raw = match std::fs::read(&p) {
            Ok(b) => b,
            Err(e) => {
                eprintln!("error reading {}: {}", p.display(), e);
                return 2;
            }
        };
        let value: serde_json::Value = match serde_json::from_slice(&raw) {
            Ok(v) => v,
            Err(e) => {
                eprintln!("error parsing {}: {}", p.display(), e);
                return 2;
            }
        };
        let file_id = p.file_stem().and_then(|s| s.to_str()).unwrap_or("");
        let canonical = jcs::canonical_bytes(&value);
        let observed = format!("sha256:{}", jcs::sha256_hex(&canonical));
        let expected = expected_digests
            .get(file_id)
            .and_then(|v| v.as_str())
            .unwrap_or("");
        let ok = !expected.is_empty() && observed == expected;
        if ok {
            passed += 1;
        }
        let verdict = if ok { "PASS" } else { "FAIL" };
        println!(
            "{} | {:<25} | observed={} expected={}",
            verdict, file_id, observed, expected
        );
    }
    println!("{}", "=".repeat(60));
    println!(
        "Summary: {} corpus entries, {} passed, {} failed",
        total,
        passed,
        total - passed
    );
    if total > 0 && passed == total {
        0
    } else {
        1
    }
}

fn cmd_fingerprints() -> i32 {
    let root = repo_root();
    let report = match fingerprints::compute_all(&root) {
        Ok(r) => r,
        Err(e) => {
            eprintln!("error: {}", e);
            return 2;
        }
    };
    println!("WiseOrder Protocol v0.1.0 — Rust verifier: fingerprints");
    println!("{}", "=".repeat(72));
    let lines: [(&str, &str, &str); 3] = [
        (
            "vectors_suite_sha256",
            EXPECTED_VECTORS_SUITE,
            &report.vectors_suite_sha256,
        ),
        (
            "manifests_suite_sha256",
            EXPECTED_MANIFESTS_SUITE,
            &report.manifests_suite_sha256,
        ),
        (
            "corpus_sha256",
            EXPECTED_CORPUS_SHA,
            &report.corpus_sha256,
        ),
    ];
    let mut all_match = true;
    for (label, expected, observed) in lines.iter() {
        let ok = expected == observed;
        if !ok {
            all_match = false;
        }
        let verdict = if ok { "MATCH" } else { "DIVERGENT" };
        println!("{:<22} {}", label, verdict);
        println!("  expected: {}", expected);
        println!("  observed: {}", observed);
    }
    println!("{}", "=".repeat(72));
    println!(
        "Counts: vectors={} manifests={} corpus_entries={}",
        report.vector_count, report.manifest_count, report.corpus_entry_count
    );
    println!(
        "OVERALL: {}",
        if all_match { "MATCH" } else { "DIVERGENT" }
    );
    if all_match {
        0
    } else {
        1
    }
}

fn print_help() {
    println!(
        "WiseOrder Protocol v0.1.0 — first-party independent Rust verifier track\n\
         \n\
         USAGE:\n\
           rust_verifier <SUBCOMMAND>\n\
         \n\
         SUBCOMMANDS:\n\
           verify-vectors        Re-derive verdicts for every vectors/*.json\n\
           verify-corpus         Reproduce canonicalization corpus digests\n\
           fingerprints          Compute and compare all three v0.1.0 frozen fingerprints\n\
           canonicalize <file>   Canonicalize one JSON file; emit canonical bytes + sha256\n\
           help                  This message\n\
         \n\
         INDEPENDENCE:\n\
           This crate does not import or shell out to Python. The classification\n\
           is FIRST_PARTY_INDEPENDENT_IMPLEMENTATION_TRACK; it is not third-party\n\
           validation."
    );
}

// --- canonicalize ----------------------------------------------------------

// cmd_canonicalize reads one JSON file, canonicalizes it via jcs::canonical_bytes,
// and prints a single-line JSON report on stdout. Used by tools/triple_sweep.py
// to diff Python vs Go vs Rust canonical bytes.
//
//   output: {"canonical_b64":"...","sha256_hex":"...","length":N}
fn cmd_canonicalize(args: &[String]) -> i32 {
    use base64::Engine as _;
    if args.len() != 1 {
        eprintln!("usage: rust_verifier canonicalize <input.json>");
        return 2;
    }
    let path = std::path::PathBuf::from(&args[0]);
    let raw = match std::fs::read(&path) {
        Ok(b) => b,
        Err(e) => {
            eprintln!("error reading {}: {}", path.display(), e);
            return 2;
        }
    };
    let value: serde_json::Value = match serde_json::from_slice(&raw) {
        Ok(v) => v,
        Err(e) => {
            eprintln!("error parsing {}: {}", path.display(), e);
            return 2;
        }
    };
    let canonical = jcs::canonical_bytes(&value);
    let report = serde_json::json!({
        "canonical_b64": base64::engine::general_purpose::STANDARD.encode(&canonical),
        "sha256_hex": jcs::sha256_hex(&canonical),
        "length": canonical.len(),
    });
    println!("{}", serde_json::to_string(&report).expect("serialize report"));
    0
}

fn main() {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let rc = match args.first().map(|s| s.as_str()).unwrap_or("help") {
        "verify-vectors" => cmd_verify_vectors(),
        "verify-corpus" => cmd_verify_corpus(),
        "fingerprints" => cmd_fingerprints(),
        "canonicalize" => cmd_canonicalize(&args[1..]),
        "help" | "--help" | "-h" => {
            print_help();
            0
        }
        other => {
            eprintln!("error: unknown subcommand: {}", other);
            print_help();
            2
        }
    };
    std::process::exit(rc);
}
