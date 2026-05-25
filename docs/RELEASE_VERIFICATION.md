# RELEASE_VERIFICATION

How a third party verifies a Wise.Est Systems release. No hidden trust assumptions: every step is reproducible from the public repo + the release artifacts.

## Trust model

A release artifact is trustworthy iff:

1. It exists at a specific git tag whose commit hash you can independently fetch.
2. The tag is annotated (carries a message body) or, preferably, **signed** (carries a verifiable signature).
3. The artifact's `consequence_proof` (for chain triples) or SHA-256 hash (for files) re-derives from the artifact's canonical body.
4. CI on the tagged commit was green.

That is the entire trust chain. There is no central authority, no hidden allowlist, no "trust because we said so." If any of the four items above fails, the release is not trustworthy.

## Verifying a git tag

### Annotated (the minimum)

```bash
git tag -v v0.1.0
```

Expected output for an annotated-but-unsigned tag:
```
object <commit-sha>
type commit
tag v0.1.0
tagger <name> <email> <timestamp>

release v0.1.0: <summary>
```

If you see "error: no signature found" that is **expected** for tags shipped before signing was configured. Pre-v0.1.0 tags are annotated-only by design.

### Signed (the goal for v0.1.0 final and beyond)

We support two signing paths. A release is signed iff at least one is verifiable.

#### Path A — GPG (traditional)

```bash
git tag -v v0.1.0
```

Expected (with a valid GPG signature):
```
object <commit-sha>
...
gpg: Signature made <date> using <algo> key <key-id>
gpg: Good signature from "Wise.Est Systems <wise.est.systems@proton.me>"
```

The public key for verification is published at: **(deferred; first signed release will publish the key alongside the GitHub Releases entry.)**

#### Path B — Sigstore / cosign (keyless)

```bash
cosign verify-blob \
  --certificate-identity-regexp "https://github.com/Wise-Est-Systems/" \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \
  --signature <release-tarball>.sig \
  --certificate <release-tarball>.crt \
  <release-tarball>.tar.gz
```

The signature + cert are attached to the GitHub Releases entry. Cosign uses Sigstore's transparency log; a verified signature proves the artifact was produced by a workflow running under the `Wise-Est-Systems` GitHub identity at the time the certificate was issued.

This path requires no key management on Wise.Est Systems' side — the OIDC token from the GitHub Actions workflow is the proof.

## Verifying a chain triple (`.win` file)

A `.win` file is one triple. The verifier re-derives `consequence_proof` from the canonical body of the triple with that field removed:

```bash
PYTHONPATH=/path/to/wiseorder-protocol python3 - <<'PY'
import json, sys
from pathlib import Path
from intellagent_runtime.iii import iii

triple = json.loads(Path("path/to/genesis.win").read_text())
core = {k: v for k, v in triple.items() if k != "consequence_proof"}
canonical = json.dumps(core, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
recomputed = iii(canonical)
if recomputed == triple["consequence_proof"]:
    print(f"OK: consequence_proof matches ({recomputed[:32]}...)")
else:
    print(f"FAIL: declared {triple['consequence_proof']}, recomputed {recomputed}")
    sys.exit(1)
PY
```

For an entire chain:

```bash
PYTHONPATH=/path/to/wiseorder-protocol python3 -c "
from pathlib import Path
from intellagent_runtime.chain import verify_chain
status = verify_chain(Path('chain'))
print(f'{status.status} count={status.count} head={status.head}')
" || echo "CHAIN_INVALID or CHAIN_TAMPERED"
```

Expected for a valid chain:
```
CHAIN_VALID count=3 head=5964497c48c877946e2c92d15e3116f5991c1d8a4c99dc7eadb477cec558dd81
```

The verifier exists in three independent languages: Python (`intellagent_runtime/chain.py`), Rust (`rust_verifier/`), Go (`go_verifier/`). All three must return the same head hash for any release. **Single-language verification is single-source assurance**; cross-language parity is the actual proof.

## Verifying a release manifest

For `wop` releases, the manifest pattern is:

```bash
# from a release directory
cat release-v0.1.1.manifest                            # list of files + hashes
shasum -a 256 -c release-v0.1.1.manifest               # verify all listed files
cat release-v0.1.1.manifest.wiseproof                  # the signature over the manifest
```

For `demo-forge` releases (e.g., RELEASE_001_SIGKILL):

```bash
cd outputs/RELEASE_001_SIGKILL/
python3 -c "
import hashlib, json
m = json.load(open('artifact_manifest.json'))
for a in m['artifacts']:
    actual = hashlib.sha256(open(a['name'],'rb').read()).hexdigest()
    print(f'{actual==a[\"sha256\"]}  {a[\"name\"]}')
"
```

Every line must print `True`.

## Verifying CI was green at the tagged commit

```bash
gh run list --repo Wise-Est-Systems/wiseorder-protocol --commit <commit-sha> --json status,conclusion,name
```

Expected: every workflow that ran on the commit must show `"conclusion": "success"`.

This step is one a reviewer can run themselves; it does not rely on Wise.Est Systems trustworthiness — only on GitHub's API integrity.

## What this document does NOT cover

- **Verifying WiseDigest-3 cryptographic strength.** This is a separate, deferred cryptanalysis. The verifier code's correctness is testable; the algorithm's collision resistance against an adversary with multi-year compute budgets is not yet externally established.
- **Verifying the LLM-generated content in `wiseorder` demos.** LLM output is inherently non-deterministic; reviewers should treat the SHAPE of the workflow as the verifiable claim, not the specific words in the engineering summary.
- **Verifying the operator's intent.** A signed tag proves who signed; it does not prove the signer is who they claim to be in the real world. Identity verification is out of scope.

## Status of signing infrastructure (2026-05-25)

| component | status |
|---|---|
| Annotated tags | ✅ supported on every release |
| GPG signing | ⚠ deferred — no key configured yet on the release operator's environment |
| Sigstore / cosign keyless | ✅ tooling installed (`cosign 2.x` on the operator machine); not yet wired into release workflow |
| Three-language verifier parity | ✅ Python + Rust + Go, all first-party tracks |
| Transparency-log entry (Rekor) | ⚠ will be present automatically when cosign keyless is wired in |

**First signed release**: planned for `v0.1.0` final. `v0.1.0-rc1` is intentionally annotated-only — it is a release candidate, not a release.

The reviewer should treat unsigned-but-annotated tags as "verifiable via CI run + tag annotation + chain re-derivation"; not as "verifiable via cryptographic signature." That distinction is documented honestly here and in every CHANGELOG entry.
