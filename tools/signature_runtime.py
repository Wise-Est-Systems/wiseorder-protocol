#!/usr/bin/env python3
"""WiseOrder/Intellagent — SIGNATURE RUNTIME v0.1.

Local symmetric signing of WiseOrder runtime artifacts via HMAC-SHA256.

This runtime adds a per-artifact authenticity record so that proposer JSON,
review artifacts, executor manifests, pipeline aggregates, isolation
manifests, and resource-limit manifests can be verified as authored by a
declared local signing identity. v0.1 uses HMAC-SHA256 keyed by a per-
identity secret stored under ``.wiseorder_keys/`` (gitignored). HMAC is a
LOCAL SYMMETRIC primitive — it binds artifact bytes to a key, not to a
public-key identity, and it does not produce distributed trust. Public-key
attestation (Ed25519) is future work.

Architecture: ``artifact -> sign -> <artifact>.sig.json``. Verification
re-derives the canonical signing input from the artifact on disk and
compares the recomputed HMAC byte-for-byte against the recorded
``signature``. Any mutation of the signed bytes, any mismatch in the
claimed signer (against the verifier-supplied ``--expected-signer-id``),
any missing key, or any missing signature record fails verification.

Spec: SIGNATURE-RUNTIME-v0.1.md (top-level).
Companion: REAL-AGENT-RUNTIME-v0.2.md, PIPELINE-RUNTIME-v0.1.md,
OS-ISOLATION-RUNTIME-v0.1.md, RESOURCE-LIMIT-RUNTIME-v0.1.md,
PROPOSER-RUNTIME-v0.1.md, REVIEW-GATE-RUNTIME-v0.1.md.

CLI verbs:
  signature_runtime.py generate-identity --signer-id ID [--overwrite]
  signature_runtime.py sign --artifact PATH --signer-id ID
                            [--excluded-fields F1,F2,...]
  signature_runtime.py verify --artifact PATH [--sig PATH]
                              [--expected-signer-id ID]
  signature_runtime.py self-check
  signature_runtime.py run-fixture

NOT included in `make ci`. Targets are opt-in.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import hmac
import json
import os
import secrets
import shutil
import stat
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Sequence

REPO_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = REPO_ROOT / "reports" / "signature_runtime"
RUNS_DIR = REPORTS_DIR / "runs"
FIXTURES_DIR = REPORTS_DIR / "_fixtures"
DEFAULT_KEY_DIR = REPO_ROOT / ".wiseorder_keys"

RUNTIME_VERSION = "v0.1"
SIGNATURE_VERSION = "v0.1"
ALGORITHM = "HMAC-SHA256"
SIGNING_DOMAIN = "WISEORDER-SIG-v0.1"

DEFAULT_EXCLUDED_FIELDS: tuple[str, ...] = ("timestamp",)
KEY_BYTES = 32  # 256-bit HMAC key
KEY_ID_HEX_LEN = 16  # 64-bit truncated key fingerprint

# Identity allowlist for signing. Aligned with REAL-AGENT-RUNTIME executor
# identities plus the review-gate identity. Any signer outside this set is
# refused at sign time (and at verify time when --expected-signer-id is set).
SIGNING_IDENTITIES: tuple[str, ...] = (
    "canon_guardian-01",
    "reviewer-01",
    "builder-01",
    "release-01",
    "review-gate-01",
)

# Verification-status verdicts. Each is terminal for a single verify call.
VERIFIED = "verified"
TAMPERED_ARTIFACT = "tampered_artifact"
WRONG_SIGNER = "wrong_signer"
MISSING_KEY = "missing_key"
MISSING_SIGNATURE = "missing_signature"
MALFORMED_SIGNATURE = "malformed_signature"
UNKNOWN_SIGNER = "unknown_signer"
UNSUPPORTED_VERSION = "unsupported_signature_version"
UNSUPPORTED_ALGORITHM = "unsupported_algorithm"
ARTIFACT_MISSING = "artifact_missing"
ARTIFACT_UNPARSEABLE = "artifact_unparseable"

# Sig record marker that the runtime writes upon a successful sign. The
# signer never claims "verified" — verification is the verifier's verdict.
SIG_RECORD_STATUS_SIGNED = "signed"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _canonical_artifact_bytes(artifact: object, excluded: Sequence[str]) -> bytes:
    """Return canonical signing input for an artifact.

    For top-level dicts: drop excluded keys, JSON-serialize sorted with
    indent=2, and append a trailing newline. For non-dict roots (lists,
    primitives), the excluded list does not apply; the input is serialized
    as-is. The output convention matches the rest of the runtime stack
    (reports/* are written sorted, indent 2, trailing newline).
    """
    if isinstance(artifact, dict):
        excluded_set = set(excluded)
        filtered = {k: v for k, v in artifact.items() if k not in excluded_set}
        canonical = json.dumps(filtered, sort_keys=True, indent=2, ensure_ascii=False)
    else:
        canonical = json.dumps(artifact, sort_keys=True, indent=2, ensure_ascii=False)
    if not canonical.endswith("\n"):
        canonical += "\n"
    return canonical.encode("utf-8")


def _sha256_hex(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _signing_string(
    *,
    signer_id: str,
    artifact_sha256: str,
    excluded_fields: Sequence[str],
) -> bytes:
    """Build the domain-separated string the HMAC is computed over.

    Format (newline-separated, UTF-8):
        WISEORDER-SIG-v0.1
        HMAC-SHA256
        <signer_id>
        <artifact_sha256>
        <comma-joined sorted excluded fields>
    """
    parts = [
        SIGNING_DOMAIN,
        ALGORITHM,
        signer_id,
        artifact_sha256,
        ",".join(sorted(excluded_fields)),
    ]
    return ("\n".join(parts) + "\n").encode("utf-8")


def _hmac_hex(key: bytes, message: bytes) -> str:
    return hmac.new(key, message, hashlib.sha256).hexdigest()


def _key_id_for(key_bytes: bytes) -> str:
    """Return ``key_id:<16-hex>`` — a deterministic, key-non-revealing id.

    HMAC keys are SECRETS. Publishing them defeats the scheme. The key id is
    a truncated sha256 of the key bytes; it identifies *which* key produced
    a signature without exposing the key. Its purpose is replay equivalence
    of signatures, not key recovery.
    """
    return "key_id:" + hashlib.sha256(key_bytes).hexdigest()[:KEY_ID_HEX_LEN]


def _key_path(key_dir: Path, signer_id: str) -> Path:
    return key_dir / f"{signer_id}.key"


def _ensure_key_dir(key_dir: Path) -> None:
    key_dir.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(key_dir, 0o700)
    except OSError:
        # Best-effort. The runtime does not refuse on chmod failure; the
        # ignore-rule in .gitignore is the load-bearing protection.
        pass


def _write_key_file(path: Path, key_bytes: bytes) -> None:
    # Write atomically with restrictive perms.
    tmp_path = path.with_suffix(".key.tmp")
    tmp_path.write_bytes(key_bytes.hex().encode("utf-8") + b"\n")
    try:
        os.chmod(tmp_path, 0o600)
    except OSError:
        pass
    tmp_path.replace(path)


def _read_key_file(path: Path) -> bytes:
    raw = path.read_text(encoding="utf-8").strip()
    try:
        return bytes.fromhex(raw)
    except ValueError as exc:  # malformed key file
        raise ValueError(f"key file at {path} is not valid hex") from exc


def _is_known_signer(signer_id: str) -> bool:
    return signer_id in SIGNING_IDENTITIES


def _relpath(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path.resolve())


# ---------------------------------------------------------------------------
# Public API: identity / key management
# ---------------------------------------------------------------------------


def generate_identity(
    signer_id: str,
    *,
    key_dir: Path = DEFAULT_KEY_DIR,
    overwrite: bool = False,
) -> Path:
    """Create a fresh 32-byte HMAC key for ``signer_id`` under ``key_dir``.

    Refuses an unknown signer (not in SIGNING_IDENTITIES). Refuses to
    overwrite an existing key file unless ``overwrite=True``. The key file
    is written 0o600.
    """
    if not _is_known_signer(signer_id):
        raise ValueError(
            f"unknown signer_id {signer_id!r}; "
            f"must be one of {SIGNING_IDENTITIES}"
        )
    _ensure_key_dir(key_dir)
    path = _key_path(key_dir, signer_id)
    if path.exists() and not overwrite:
        raise FileExistsError(
            f"key already exists at {path}; pass overwrite=True to rotate"
        )
    key_bytes = secrets.token_bytes(KEY_BYTES)
    _write_key_file(path, key_bytes)
    return path


def load_key(signer_id: str, *, key_dir: Path = DEFAULT_KEY_DIR) -> bytes:
    path = _key_path(key_dir, signer_id)
    if not path.exists():
        raise FileNotFoundError(f"no key for signer {signer_id} at {path}")
    return _read_key_file(path)


def key_exists(signer_id: str, *, key_dir: Path = DEFAULT_KEY_DIR) -> bool:
    return _key_path(key_dir, signer_id).exists()


# ---------------------------------------------------------------------------
# Public API: sign / verify
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SignResult:
    record: dict
    sig_path: Path


def sign_artifact(
    artifact_path: Path,
    signer_id: str,
    *,
    key_dir: Path = DEFAULT_KEY_DIR,
    excluded_fields: Optional[Sequence[str]] = None,
    sig_path: Optional[Path] = None,
) -> SignResult:
    """Produce a detached signature for ``artifact_path``.

    Reads ``artifact_path`` as JSON, drops top-level ``excluded_fields``
    (default: ``("timestamp",)``), serializes canonically, computes the
    artifact sha256, builds the domain-separated signing string, HMACs it
    with the signer's key, and writes a sig record at
    ``<artifact_path>.sig.json``. The returned ``SignResult.record`` is the
    JSON-serializable dict that was written.
    """
    if not _is_known_signer(signer_id):
        raise ValueError(
            f"unknown signer_id {signer_id!r}; "
            f"must be one of {SIGNING_IDENTITIES}"
        )
    artifact_path = Path(artifact_path)
    if not artifact_path.exists():
        raise FileNotFoundError(f"artifact missing at {artifact_path}")

    excluded = list(excluded_fields) if excluded_fields is not None else list(
        DEFAULT_EXCLUDED_FIELDS
    )
    excluded_sorted = sorted(set(excluded))

    raw_text = artifact_path.read_text(encoding="utf-8")
    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"artifact at {artifact_path} is not valid JSON") from exc

    canonical = _canonical_artifact_bytes(parsed, excluded_sorted)
    artifact_sha256 = _sha256_hex(canonical)

    key_bytes = load_key(signer_id, key_dir=key_dir)
    signing_string = _signing_string(
        signer_id=signer_id,
        artifact_sha256=artifact_sha256,
        excluded_fields=excluded_sorted,
    )
    signature_hex = _hmac_hex(key_bytes, signing_string)

    record = {
        "signature_version": SIGNATURE_VERSION,
        "algorithm": ALGORITHM,
        "signer_id": signer_id,
        "artifact_path": _relpath(artifact_path),
        "artifact_sha256": artifact_sha256,
        "signature": signature_hex,
        "timestamp": _now_iso(),
        "public_material_or_key_id": _key_id_for(key_bytes),
        "unsigned_fields_excluded": excluded_sorted,
        "verification_status": SIG_RECORD_STATUS_SIGNED,
    }

    final_sig_path = sig_path if sig_path is not None else artifact_path.with_suffix(
        artifact_path.suffix + ".sig.json"
    )
    final_sig_path.parent.mkdir(parents=True, exist_ok=True)
    final_sig_path.write_text(
        json.dumps(record, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return SignResult(record=record, sig_path=final_sig_path)


@dataclass(frozen=True)
class VerifyResult:
    verification_status: str
    artifact_path: str
    sig_path: Optional[str]
    signer_id: str
    expected_signer_id: Optional[str]
    artifact_sha256_recorded: Optional[str]
    artifact_sha256_recomputed: Optional[str]
    signature_recorded: Optional[str]
    signature_recomputed: Optional[str]
    key_id_recorded: Optional[str]
    key_id_loaded: Optional[str]
    unsigned_fields_excluded: list
    detail: str


def _empty_verify_result(
    *,
    status: str,
    artifact_path: Path,
    sig_path: Optional[Path],
    detail: str,
    signer_id: str = "",
    expected_signer_id: Optional[str] = None,
    artifact_sha256_recorded: Optional[str] = None,
    artifact_sha256_recomputed: Optional[str] = None,
    signature_recorded: Optional[str] = None,
    signature_recomputed: Optional[str] = None,
    key_id_recorded: Optional[str] = None,
    key_id_loaded: Optional[str] = None,
    unsigned_fields_excluded: Optional[list] = None,
) -> VerifyResult:
    return VerifyResult(
        verification_status=status,
        artifact_path=str(artifact_path),
        sig_path=str(sig_path) if sig_path is not None else None,
        signer_id=signer_id,
        expected_signer_id=expected_signer_id,
        artifact_sha256_recorded=artifact_sha256_recorded,
        artifact_sha256_recomputed=artifact_sha256_recomputed,
        signature_recorded=signature_recorded,
        signature_recomputed=signature_recomputed,
        key_id_recorded=key_id_recorded,
        key_id_loaded=key_id_loaded,
        unsigned_fields_excluded=list(unsigned_fields_excluded or []),
        detail=detail,
    )


def verify_artifact(
    artifact_path: Path,
    *,
    sig_path: Optional[Path] = None,
    key_dir: Path = DEFAULT_KEY_DIR,
    expected_signer_id: Optional[str] = None,
) -> VerifyResult:
    """Verify a detached signature against an artifact on disk.

    Returns a :class:`VerifyResult` whose ``verification_status`` is one of
    the module-level VERIFIED/* constants. The function never raises on a
    legitimate verification failure — it returns the structured result so
    a caller can act on the verdict deterministically. Programming errors
    (e.g., wrong types passed in) still raise.
    """
    artifact_path = Path(artifact_path)
    sig_path_resolved = (
        Path(sig_path)
        if sig_path is not None
        else artifact_path.with_suffix(artifact_path.suffix + ".sig.json")
    )

    if not artifact_path.exists():
        return _empty_verify_result(
            status=ARTIFACT_MISSING,
            artifact_path=artifact_path,
            sig_path=sig_path_resolved if sig_path_resolved.exists() else None,
            expected_signer_id=expected_signer_id,
            detail=f"artifact not found at {artifact_path}",
        )

    if not sig_path_resolved.exists():
        return _empty_verify_result(
            status=MISSING_SIGNATURE,
            artifact_path=artifact_path,
            sig_path=sig_path_resolved,
            expected_signer_id=expected_signer_id,
            detail=f"signature record not found at {sig_path_resolved}",
        )

    try:
        record = json.loads(sig_path_resolved.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return _empty_verify_result(
            status=MALFORMED_SIGNATURE,
            artifact_path=artifact_path,
            sig_path=sig_path_resolved,
            expected_signer_id=expected_signer_id,
            detail=f"signature record JSON parse failed: {exc.msg}",
        )

    required_fields = (
        "signature_version",
        "algorithm",
        "signer_id",
        "artifact_path",
        "artifact_sha256",
        "signature",
        "timestamp",
        "public_material_or_key_id",
        "unsigned_fields_excluded",
        "verification_status",
    )
    for f in required_fields:
        if f not in record:
            return _empty_verify_result(
                status=MALFORMED_SIGNATURE,
                artifact_path=artifact_path,
                sig_path=sig_path_resolved,
                expected_signer_id=expected_signer_id,
                detail=f"signature record missing required field {f!r}",
            )

    if record.get("signature_version") != SIGNATURE_VERSION:
        return _empty_verify_result(
            status=UNSUPPORTED_VERSION,
            artifact_path=artifact_path,
            sig_path=sig_path_resolved,
            expected_signer_id=expected_signer_id,
            detail=(
                f"signature_version {record.get('signature_version')!r} "
                f"unsupported; expected {SIGNATURE_VERSION!r}"
            ),
        )

    if record.get("algorithm") != ALGORITHM:
        return _empty_verify_result(
            status=UNSUPPORTED_ALGORITHM,
            artifact_path=artifact_path,
            sig_path=sig_path_resolved,
            expected_signer_id=expected_signer_id,
            detail=(
                f"algorithm {record.get('algorithm')!r} unsupported; "
                f"expected {ALGORITHM!r}"
            ),
        )

    signer_id_recorded = str(record.get("signer_id", ""))

    if not _is_known_signer(signer_id_recorded):
        return _empty_verify_result(
            status=UNKNOWN_SIGNER,
            artifact_path=artifact_path,
            sig_path=sig_path_resolved,
            signer_id=signer_id_recorded,
            expected_signer_id=expected_signer_id,
            detail=(
                f"signer {signer_id_recorded!r} not in SIGNING_IDENTITIES"
            ),
        )

    if expected_signer_id is not None and signer_id_recorded != expected_signer_id:
        return _empty_verify_result(
            status=WRONG_SIGNER,
            artifact_path=artifact_path,
            sig_path=sig_path_resolved,
            signer_id=signer_id_recorded,
            expected_signer_id=expected_signer_id,
            detail=(
                f"sig record claims signer_id={signer_id_recorded!r} but "
                f"caller required {expected_signer_id!r}"
            ),
        )

    if not key_exists(signer_id_recorded, key_dir=key_dir):
        return _empty_verify_result(
            status=MISSING_KEY,
            artifact_path=artifact_path,
            sig_path=sig_path_resolved,
            signer_id=signer_id_recorded,
            expected_signer_id=expected_signer_id,
            detail=(
                f"no key for signer {signer_id_recorded!r} under {key_dir}"
            ),
        )

    excluded = list(record.get("unsigned_fields_excluded") or [])

    try:
        parsed = json.loads(artifact_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return _empty_verify_result(
            status=ARTIFACT_UNPARSEABLE,
            artifact_path=artifact_path,
            sig_path=sig_path_resolved,
            signer_id=signer_id_recorded,
            expected_signer_id=expected_signer_id,
            detail=f"artifact JSON parse failed: {exc.msg}",
        )

    canonical = _canonical_artifact_bytes(parsed, sorted(set(excluded)))
    artifact_sha_recomputed = _sha256_hex(canonical)
    artifact_sha_recorded = str(record.get("artifact_sha256", ""))

    key_bytes = load_key(signer_id_recorded, key_dir=key_dir)
    key_id_loaded = _key_id_for(key_bytes)
    key_id_recorded = str(record.get("public_material_or_key_id", ""))

    signing_string = _signing_string(
        signer_id=signer_id_recorded,
        artifact_sha256=artifact_sha_recomputed,
        excluded_fields=sorted(set(excluded)),
    )
    sig_recomputed = _hmac_hex(key_bytes, signing_string)
    sig_recorded = str(record.get("signature", ""))

    if artifact_sha_recomputed != artifact_sha_recorded:
        return _empty_verify_result(
            status=TAMPERED_ARTIFACT,
            artifact_path=artifact_path,
            sig_path=sig_path_resolved,
            signer_id=signer_id_recorded,
            expected_signer_id=expected_signer_id,
            artifact_sha256_recorded=artifact_sha_recorded,
            artifact_sha256_recomputed=artifact_sha_recomputed,
            signature_recorded=sig_recorded,
            signature_recomputed=sig_recomputed,
            key_id_recorded=key_id_recorded,
            key_id_loaded=key_id_loaded,
            unsigned_fields_excluded=excluded,
            detail="artifact sha256 changed since signing",
        )

    if not hmac.compare_digest(sig_recomputed, sig_recorded):
        return _empty_verify_result(
            status=TAMPERED_ARTIFACT,
            artifact_path=artifact_path,
            sig_path=sig_path_resolved,
            signer_id=signer_id_recorded,
            expected_signer_id=expected_signer_id,
            artifact_sha256_recorded=artifact_sha_recorded,
            artifact_sha256_recomputed=artifact_sha_recomputed,
            signature_recorded=sig_recorded,
            signature_recomputed=sig_recomputed,
            key_id_recorded=key_id_recorded,
            key_id_loaded=key_id_loaded,
            unsigned_fields_excluded=excluded,
            detail="HMAC mismatch",
        )

    return _empty_verify_result(
        status=VERIFIED,
        artifact_path=artifact_path,
        sig_path=sig_path_resolved,
        signer_id=signer_id_recorded,
        expected_signer_id=expected_signer_id,
        artifact_sha256_recorded=artifact_sha_recorded,
        artifact_sha256_recomputed=artifact_sha_recomputed,
        signature_recorded=sig_recorded,
        signature_recomputed=sig_recomputed,
        key_id_recorded=key_id_recorded,
        key_id_loaded=key_id_loaded,
        unsigned_fields_excluded=excluded,
        detail="artifact bytes bind to recorded signature under loaded key",
    )


# ---------------------------------------------------------------------------
# Self-check fixtures
# ---------------------------------------------------------------------------


@dataclass
class FixtureResult:
    name: str
    passed: bool
    detail: str
    run_record: Optional[Path] = None


def _write_fixture_record(name: str, payload: dict) -> Path:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    out = RUNS_DIR / f"run-{stamp}-{name}.json"
    out.write_text(
        json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return out


def _make_artifact(workdir: Path, name: str, contents: dict) -> Path:
    workdir.mkdir(parents=True, exist_ok=True)
    p = workdir / f"{name}.json"
    p.write_text(
        json.dumps(contents, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return p


def _sample_artifact(work_order_id: str, timestamp: str) -> dict:
    """Return a representative WiseOrder-shaped artifact for testing.

    The shape mimics a small executor-style record (a real WiseOrder
    artifact has many more fields). We only need enough to verify
    canonicalization and exclusion behavior.
    """
    return {
        "work_order_id": work_order_id,
        "agent_id": "builder-01",
        "runtime_version": "v0.2",
        "commands_executed": ["pwd"],
        "timestamp": timestamp,
        "exit_status": 0,
    }


def _fx_sign_valid_artifact(workdir: Path, key_dir: Path) -> FixtureResult:
    artifact = _make_artifact(
        workdir,
        "fx1-valid",
        _sample_artifact("WO-FX1", "2026-05-09T00:00:00Z"),
    )
    res = sign_artifact(artifact, "canon_guardian-01", key_dir=key_dir)
    record = res.record
    record_path = _write_fixture_record(
        "sign_valid_artifact",
        {
            "fixture": "sign_valid_artifact",
            "sig_path": str(res.sig_path),
            "record": record,
        },
    )
    ok = (
        res.sig_path.exists()
        and record.get("signer_id") == "canon_guardian-01"
        and record.get("algorithm") == ALGORITHM
        and record.get("signature_version") == SIGNATURE_VERSION
        and record.get("artifact_sha256", "").startswith("sha256:")
        and len(record.get("signature", "")) == 64
        and record.get("verification_status") == SIG_RECORD_STATUS_SIGNED
    )
    detail = (
        f"sig_path_exists={res.sig_path.exists()}, "
        f"signer_id={record.get('signer_id')}, "
        f"sig_hex_len={len(record.get('signature', ''))}"
    )
    return FixtureResult("sign_valid_artifact", ok, detail, record_path)


def _fx_verify_valid_artifact(workdir: Path, key_dir: Path) -> FixtureResult:
    artifact = _make_artifact(
        workdir,
        "fx2-verify",
        _sample_artifact("WO-FX2", "2026-05-09T00:00:01Z"),
    )
    sign_artifact(artifact, "reviewer-01", key_dir=key_dir)
    result = verify_artifact(artifact, key_dir=key_dir)
    record_path = _write_fixture_record(
        "verify_valid_artifact",
        {
            "fixture": "verify_valid_artifact",
            "result": _verify_result_to_dict(result),
        },
    )
    ok = result.verification_status == VERIFIED
    return FixtureResult(
        "verify_valid_artifact",
        ok,
        f"status={result.verification_status}, signer={result.signer_id}",
        record_path,
    )


def _fx_tampered_artifact_rejected(workdir: Path, key_dir: Path) -> FixtureResult:
    contents = _sample_artifact("WO-FX3", "2026-05-09T00:00:02Z")
    artifact = _make_artifact(workdir, "fx3-tamper", contents)
    sign_artifact(artifact, "builder-01", key_dir=key_dir)
    # Mutate a signed field (work_order_id) AFTER signing.
    contents["work_order_id"] = "WO-FX3-MUTATED"
    artifact.write_text(
        json.dumps(contents, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    result = verify_artifact(artifact, key_dir=key_dir)
    record_path = _write_fixture_record(
        "tampered_artifact_rejected",
        {
            "fixture": "tampered_artifact_rejected",
            "result": _verify_result_to_dict(result),
        },
    )
    ok = result.verification_status == TAMPERED_ARTIFACT
    return FixtureResult(
        "tampered_artifact_rejected",
        ok,
        f"status={result.verification_status}, "
        f"sha_recorded={result.artifact_sha256_recorded}, "
        f"sha_recomputed={result.artifact_sha256_recomputed}",
        record_path,
    )


def _fx_wrong_signer_rejected(workdir: Path, key_dir: Path) -> FixtureResult:
    artifact = _make_artifact(
        workdir,
        "fx4-wrongsigner",
        _sample_artifact("WO-FX4", "2026-05-09T00:00:03Z"),
    )
    sign_artifact(artifact, "canon_guardian-01", key_dir=key_dir)
    result = verify_artifact(
        artifact,
        key_dir=key_dir,
        expected_signer_id="release-01",
    )
    record_path = _write_fixture_record(
        "wrong_signer_rejected",
        {
            "fixture": "wrong_signer_rejected",
            "result": _verify_result_to_dict(result),
        },
    )
    ok = result.verification_status == WRONG_SIGNER
    return FixtureResult(
        "wrong_signer_rejected",
        ok,
        f"status={result.verification_status}, "
        f"recorded={result.signer_id}, expected={result.expected_signer_id}",
        record_path,
    )


def _fx_missing_key_rejected(workdir: Path, key_dir: Path) -> FixtureResult:
    # Sign with a real key, then delete the key file before verify.
    artifact = _make_artifact(
        workdir,
        "fx5-missingkey",
        _sample_artifact("WO-FX5", "2026-05-09T00:00:04Z"),
    )
    sign_artifact(artifact, "review-gate-01", key_dir=key_dir)
    key_file = _key_path(key_dir, "review-gate-01")
    if key_file.exists():
        key_file.unlink()
    result = verify_artifact(artifact, key_dir=key_dir)
    record_path = _write_fixture_record(
        "missing_key_rejected",
        {
            "fixture": "missing_key_rejected",
            "result": _verify_result_to_dict(result),
        },
    )
    ok = result.verification_status == MISSING_KEY
    return FixtureResult(
        "missing_key_rejected",
        ok,
        f"status={result.verification_status}, key_file_exists={key_file.exists()}",
        record_path,
    )


def _fx_missing_signature_rejected(
    workdir: Path, key_dir: Path
) -> FixtureResult:
    artifact = _make_artifact(
        workdir,
        "fx6-nosig",
        _sample_artifact("WO-FX6", "2026-05-09T00:00:05Z"),
    )
    # Do NOT sign. Verify directly.
    result = verify_artifact(artifact, key_dir=key_dir)
    record_path = _write_fixture_record(
        "missing_signature_rejected",
        {
            "fixture": "missing_signature_rejected",
            "result": _verify_result_to_dict(result),
        },
    )
    ok = result.verification_status == MISSING_SIGNATURE
    return FixtureResult(
        "missing_signature_rejected",
        ok,
        f"status={result.verification_status}",
        record_path,
    )


def _fx_signature_file_hash_stable(
    workdir: Path, key_dir: Path
) -> FixtureResult:
    artifact = _make_artifact(
        workdir,
        "fx7-stable",
        _sample_artifact("WO-FX7", "2026-05-09T00:00:06Z"),
    )
    res1 = sign_artifact(artifact, "builder-01", key_dir=key_dir)
    sig1 = res1.record["signature"]
    sha1 = res1.record["artifact_sha256"]
    # Re-sign (overwrites). Signature must be byte-identical because the
    # signing input is deterministic — same key, same canonical bytes,
    # same signing string.
    res2 = sign_artifact(artifact, "builder-01", key_dir=key_dir)
    sig2 = res2.record["signature"]
    sha2 = res2.record["artifact_sha256"]
    record_path = _write_fixture_record(
        "signature_file_hash_stable",
        {
            "fixture": "signature_file_hash_stable",
            "first_signature": sig1,
            "second_signature": sig2,
            "first_sha256": sha1,
            "second_sha256": sha2,
            "timestamps_differ": res1.record["timestamp"] != res2.record["timestamp"],
        },
    )
    ok = sig1 == sig2 and sha1 == sha2
    return FixtureResult(
        "signature_file_hash_stable",
        ok,
        f"sig_equal={sig1 == sig2}, "
        f"timestamps_differ={res1.record['timestamp'] != res2.record['timestamp']}",
        record_path,
    )


def _fx_unsigned_fields_excluded_deterministically(
    workdir: Path, key_dir: Path
) -> FixtureResult:
    contents = _sample_artifact("WO-FX8", "2026-05-09T00:00:07Z")
    artifact = _make_artifact(workdir, "fx8-exclude", contents)
    res1 = sign_artifact(artifact, "release-01", key_dir=key_dir)
    sig1 = res1.record["signature"]
    sha1 = res1.record["artifact_sha256"]
    # Mutate ONLY the timestamp (which is in DEFAULT_EXCLUDED_FIELDS).
    contents["timestamp"] = "2099-12-31T23:59:59Z"
    artifact.write_text(
        json.dumps(contents, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    res2 = sign_artifact(artifact, "release-01", key_dir=key_dir)
    sig2 = res2.record["signature"]
    sha2 = res2.record["artifact_sha256"]

    # And verify still succeeds (the recorded sha excludes timestamp).
    verify_result = verify_artifact(artifact, key_dir=key_dir)

    record_path = _write_fixture_record(
        "unsigned_fields_excluded_deterministically",
        {
            "fixture": "unsigned_fields_excluded_deterministically",
            "first_signature": sig1,
            "second_signature": sig2,
            "first_sha256": sha1,
            "second_sha256": sha2,
            "verify_status": verify_result.verification_status,
            "excluded": res2.record["unsigned_fields_excluded"],
        },
    )
    ok = (
        sig1 == sig2
        and sha1 == sha2
        and verify_result.verification_status == VERIFIED
        and res2.record["unsigned_fields_excluded"] == ["timestamp"]
    )
    return FixtureResult(
        "unsigned_fields_excluded_deterministically",
        ok,
        f"sig_stable={sig1 == sig2}, sha_stable={sha1 == sha2}, "
        f"verify_status={verify_result.verification_status}",
        record_path,
    )


def _fx_no_private_key_committed() -> FixtureResult:
    """Verify .gitignore covers .wiseorder_keys/ and no .key files leak."""
    gitignore_path = REPO_ROOT / ".gitignore"
    has_ignore_line = False
    if gitignore_path.exists():
        for line in gitignore_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped in {".wiseorder_keys/", ".wiseorder_keys"}:
                has_ignore_line = True
                break

    # Walk the repo for any *.key files. Skip the ignored directory and the
    # standard caches. Any key file outside .wiseorder_keys/ is a leak.
    skip_dirs = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        "node_modules",
        ".wiseorder_keys",
    }
    leaked: list[str] = []
    for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
        # Prune in place.
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        for fn in filenames:
            if fn.endswith(".key"):
                full = Path(dirpath) / fn
                rel = str(full.relative_to(REPO_ROOT))
                # Ignore .key files that live under any nested .wiseorder_keys.
                if ".wiseorder_keys/" in rel or rel.startswith(".wiseorder_keys/"):
                    continue
                leaked.append(rel)

    record_path = _write_fixture_record(
        "no_private_key_committed",
        {
            "fixture": "no_private_key_committed",
            "gitignore_has_ignore_line": has_ignore_line,
            "leaked_key_files": leaked,
        },
    )
    ok = has_ignore_line and not leaked
    return FixtureResult(
        "no_private_key_committed",
        ok,
        f"gitignore_line={has_ignore_line}, leaked={len(leaked)}",
        record_path,
    )


def _fx_reports_generated() -> FixtureResult:
    """The runtime report files (md+json) exist and are non-empty."""
    md = REPORTS_DIR / f"signature_runtime_{RUNTIME_VERSION}.md"
    js = REPORTS_DIR / f"signature_runtime_{RUNTIME_VERSION}.json"
    md_ok = md.exists() and md.stat().st_size > 0
    js_ok = js.exists() and js.stat().st_size > 0
    record_path = _write_fixture_record(
        "reports_generated",
        {
            "fixture": "reports_generated",
            "md_path": str(md),
            "md_exists": md_ok,
            "json_path": str(js),
            "json_exists": js_ok,
        },
    )
    return FixtureResult(
        "reports_generated",
        md_ok and js_ok,
        f"md_exists={md_ok}, json_exists={js_ok}",
        record_path,
    )


# ---------------------------------------------------------------------------
# Result serialization
# ---------------------------------------------------------------------------


def _verify_result_to_dict(r: VerifyResult) -> dict:
    return {
        "verification_status": r.verification_status,
        "artifact_path": r.artifact_path,
        "sig_path": r.sig_path,
        "signer_id": r.signer_id,
        "expected_signer_id": r.expected_signer_id,
        "artifact_sha256_recorded": r.artifact_sha256_recorded,
        "artifact_sha256_recomputed": r.artifact_sha256_recomputed,
        "signature_recorded": r.signature_recorded,
        "signature_recomputed": r.signature_recomputed,
        "key_id_recorded": r.key_id_recorded,
        "key_id_loaded": r.key_id_loaded,
        "unsigned_fields_excluded": r.unsigned_fields_excluded,
        "detail": r.detail,
    }


# ---------------------------------------------------------------------------
# Self-check orchestrator
# ---------------------------------------------------------------------------


def run_self_check() -> dict:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)

    # Use a dedicated, isolated key dir for self-check so the user's local
    # .wiseorder_keys/ is never touched.
    sc_key_dir = Path(tempfile.mkdtemp(prefix="wiseorder-sigcheck-"))

    fixtures: list[FixtureResult] = []
    try:
        # Pre-generate keys for the identities the fixtures use.
        for sid in ("canon_guardian-01", "reviewer-01", "builder-01",
                    "release-01", "review-gate-01"):
            generate_identity(sid, key_dir=sc_key_dir)

        workdir = FIXTURES_DIR

        fixtures.append(_fx_sign_valid_artifact(workdir, sc_key_dir))
        fixtures.append(_fx_verify_valid_artifact(workdir, sc_key_dir))
        fixtures.append(_fx_tampered_artifact_rejected(workdir, sc_key_dir))
        fixtures.append(_fx_wrong_signer_rejected(workdir, sc_key_dir))
        fixtures.append(_fx_missing_key_rejected(workdir, sc_key_dir))
        fixtures.append(_fx_missing_signature_rejected(workdir, sc_key_dir))
        fixtures.append(_fx_signature_file_hash_stable(workdir, sc_key_dir))
        fixtures.append(
            _fx_unsigned_fields_excluded_deterministically(workdir, sc_key_dir)
        )
        fixtures.append(_fx_no_private_key_committed())
        # The reports_generated fixture must run AFTER the report writer below,
        # so we write the report first, then re-check. We do that in two
        # passes: write a placeholder report, run the check, then rewrite.
    finally:
        shutil.rmtree(sc_key_dir, ignore_errors=True)

    # Write runtime report (initial).
    all_passed_pre = all(f.passed for f in fixtures)
    _write_runtime_report(fixtures + [], all_passed_pre)

    # Now the reports_generated fixture can verify the report exists.
    fixtures.append(_fx_reports_generated())
    all_passed = all(f.passed for f in fixtures)

    # Rewrite to include the final fixture's outcome.
    _write_runtime_report(fixtures, all_passed)

    return {
        "all_passed": all_passed,
        "fixture_count": len(fixtures),
        "fixtures": [
            {
                "name": f.name,
                "passed": f.passed,
                "detail": f.detail,
                "run_record": str(f.run_record) if f.run_record else None,
            }
            for f in fixtures
        ],
    }


def _write_runtime_report(fixtures: list[FixtureResult], all_passed: bool) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = _now_iso()

    json_path = REPORTS_DIR / f"signature_runtime_{RUNTIME_VERSION}.json"
    md_path = REPORTS_DIR / f"signature_runtime_{RUNTIME_VERSION}.md"

    json_payload = {
        "runtime": "signature_runtime",
        "runtime_version": RUNTIME_VERSION,
        "algorithm": ALGORITHM,
        "signature_version": SIGNATURE_VERSION,
        "all_passed": all_passed,
        "timestamp": timestamp,
        "fixture_count": len(fixtures),
        "fixtures": [
            {
                "name": f.name,
                "passed": f.passed,
                "detail": f.detail,
                "run_record": str(f.run_record) if f.run_record else None,
            }
            for f in fixtures
        ],
        "signing_identities": list(SIGNING_IDENTITIES),
        "default_excluded_fields": list(DEFAULT_EXCLUDED_FIELDS),
        "key_directory": str(DEFAULT_KEY_DIR.relative_to(REPO_ROOT)),
    }
    json_path.write_text(
        json.dumps(json_payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    md_lines: list[str] = []
    md_lines.append(f"# Signature Runtime {RUNTIME_VERSION} — Self-Check Report")
    md_lines.append("")
    md_lines.append(f"- Algorithm: `{ALGORITHM}`")
    md_lines.append(f"- Signature version: `{SIGNATURE_VERSION}`")
    md_lines.append(f"- All passed: `{all_passed}`")
    md_lines.append(f"- Fixture count: `{len(fixtures)}`")
    md_lines.append(f"- Timestamp: `{timestamp}`")
    md_lines.append(
        f"- Key directory (gitignored): `{DEFAULT_KEY_DIR.relative_to(REPO_ROOT)}/`"
    )
    md_lines.append("")
    md_lines.append("## Fixtures")
    md_lines.append("")
    md_lines.append("| Name | Passed | Detail |")
    md_lines.append("| --- | --- | --- |")
    for f in fixtures:
        md_lines.append(f"| `{f.name}` | `{f.passed}` | {f.detail} |")
    md_lines.append("")
    md_lines.append("## Signing identities")
    md_lines.append("")
    for sid in SIGNING_IDENTITIES:
        md_lines.append(f"- `{sid}`")
    md_lines.append("")
    md_lines.append("Spec: `SIGNATURE-RUNTIME-v0.1.md`.")
    md_lines.append("")
    md_path.write_text("\n".join(md_lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _cmd_generate_identity(args: argparse.Namespace) -> int:
    try:
        path = generate_identity(
            args.signer_id,
            key_dir=Path(args.key_dir) if args.key_dir else DEFAULT_KEY_DIR,
            overwrite=args.overwrite,
        )
    except (ValueError, FileExistsError) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 1
    print(f"key written: {path}")
    return 0


def _cmd_sign(args: argparse.Namespace) -> int:
    excluded = (
        [e.strip() for e in args.excluded_fields.split(",") if e.strip()]
        if args.excluded_fields
        else None
    )
    try:
        res = sign_artifact(
            Path(args.artifact),
            args.signer_id,
            key_dir=Path(args.key_dir) if args.key_dir else DEFAULT_KEY_DIR,
            excluded_fields=excluded,
        )
    except (ValueError, FileNotFoundError) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(res.record, sort_keys=True, indent=2, ensure_ascii=False))
    return 0


def _cmd_verify(args: argparse.Namespace) -> int:
    res = verify_artifact(
        Path(args.artifact),
        sig_path=Path(args.sig) if args.sig else None,
        key_dir=Path(args.key_dir) if args.key_dir else DEFAULT_KEY_DIR,
        expected_signer_id=args.expected_signer_id,
    )
    print(
        json.dumps(_verify_result_to_dict(res), sort_keys=True, indent=2, ensure_ascii=False)
    )
    return 0 if res.verification_status == VERIFIED else 1


def _cmd_self_check(_args: argparse.Namespace) -> int:
    summary = run_self_check()
    print(json.dumps(summary, sort_keys=True, indent=2, ensure_ascii=False))
    return 0 if summary["all_passed"] else 1


def _cmd_run_fixture(_args: argparse.Namespace) -> int:
    """Run a single canonical sign+verify cycle against an in-memory fixture.

    Uses an isolated temp key dir so the user's .wiseorder_keys/ is never
    touched. Prints the sign record and the verify result.
    """
    sc_key_dir = Path(tempfile.mkdtemp(prefix="wiseorder-sigfx-"))
    try:
        FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
        generate_identity("canon_guardian-01", key_dir=sc_key_dir)
        artifact = _make_artifact(
            FIXTURES_DIR,
            "run-fixture-canonical",
            _sample_artifact("WO-FIXTURE-CANON", _now_iso()),
        )
        sign_res = sign_artifact(artifact, "canon_guardian-01", key_dir=sc_key_dir)
        verify_res = verify_artifact(artifact, key_dir=sc_key_dir)
        out = {
            "fixture": "canonical_sign_verify",
            "sign_record": sign_res.record,
            "verify_result": _verify_result_to_dict(verify_res),
        }
        print(json.dumps(out, sort_keys=True, indent=2, ensure_ascii=False))
        return 0 if verify_res.verification_status == VERIFIED else 1
    finally:
        shutil.rmtree(sc_key_dir, ignore_errors=True)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="signature_runtime.py")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_gen = sub.add_parser("generate-identity")
    p_gen.add_argument("--signer-id", required=True)
    p_gen.add_argument("--key-dir", default=None)
    p_gen.add_argument("--overwrite", action="store_true")
    p_gen.set_defaults(func=_cmd_generate_identity)

    p_sign = sub.add_parser("sign")
    p_sign.add_argument("--artifact", required=True)
    p_sign.add_argument("--signer-id", required=True)
    p_sign.add_argument("--key-dir", default=None)
    p_sign.add_argument(
        "--excluded-fields",
        default=None,
        help="Comma-separated top-level field names to exclude from the "
        "signing input. Defaults to 'timestamp'.",
    )
    p_sign.set_defaults(func=_cmd_sign)

    p_verify = sub.add_parser("verify")
    p_verify.add_argument("--artifact", required=True)
    p_verify.add_argument("--sig", default=None)
    p_verify.add_argument("--key-dir", default=None)
    p_verify.add_argument("--expected-signer-id", default=None)
    p_verify.set_defaults(func=_cmd_verify)

    p_check = sub.add_parser("self-check")
    p_check.set_defaults(func=_cmd_self_check)

    p_fx = sub.add_parser("run-fixture")
    p_fx.set_defaults(func=_cmd_run_fixture)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
