"""Canonical encoding, hashing, and atomic file primitives.

Canonical JSON here is *tooling-internal* canonicalization for fingerprinting
and content-addressing. It is NOT a Class A canonicalization scheme; that
remains RFC 8785 JCS only, per SPEC.md §4.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import os
import secrets
import time
from pathlib import Path
from typing import Any, Callable

# ---- Clock injection (for deterministic replay tests) ---------------------

_NOW_FN: Callable[[], float] = time.time


def utcnow_iso8601() -> str:
    """Return current UTC time as a fixed-format ISO-8601 string.

    Honors a clock injected via :func:`set_clock` (used by replay tests).
    """
    ts = _NOW_FN()
    dt = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def set_clock(fn: Callable[[], float]) -> None:
    """Override the clock function (replay tests, deterministic builds)."""
    global _NOW_FN
    _NOW_FN = fn


def reset_clock() -> None:
    """Restore the real wall clock."""
    global _NOW_FN
    _NOW_FN = time.time


# ---- ID generation --------------------------------------------------------

_ID_FN: Callable[[], str] = lambda: secrets.token_hex(4)


def short_id() -> str:
    """Generate a short opaque ID. Override via :func:`set_id_fn` for tests."""
    return _ID_FN()


def set_id_fn(fn: Callable[[], str]) -> None:
    """Override the short-ID generator."""
    global _ID_FN
    _ID_FN = fn


def reset_id_fn() -> None:
    """Restore the random short-ID generator."""
    global _ID_FN
    _ID_FN = lambda: secrets.token_hex(4)


# ---- Canonical JSON -------------------------------------------------------


def canonical_json_bytes(obj: Any) -> bytes:
    """Deterministic JSON: sorted keys, compact separators, UTF-8.

    Used for content-addressing and fingerprinting. Identical Python values
    yield byte-identical output across runs and machines.
    """
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def canonical_pretty(obj: Any) -> str:
    """Pretty-printed canonical form for committed files (sorted keys, 2-space)."""
    return json.dumps(obj, sort_keys=True, indent=2, ensure_ascii=False) + "\n"


# ---- Hashing --------------------------------------------------------------


def sha256_hex(data: bytes) -> str:
    """Return ``sha256:<64 lowercase hex>``."""
    return "sha256:" + hashlib.sha256(data).hexdigest()


# ---- Atomic file writes ---------------------------------------------------


def write_atomic(path: Path, content: str | bytes) -> None:
    """Write ``content`` to ``path`` atomically (temp + rename).

    Crash mid-write does not leave a half-written file visible to readers.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    if isinstance(content, str):
        tmp.write_text(content, encoding="utf-8")
    else:
        tmp.write_bytes(content)
    os.replace(tmp, path)


# ---- SHA-256 pattern check ------------------------------------------------

import re

_SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def is_sha256(value: object) -> bool:
    return isinstance(value, str) and bool(_SHA256_RE.match(value))
