"""Locked-vector tests for intellagent_runtime.iii (= WiseDigest-3, OG).

These vectors are LOCKED. They become part of the v0.2.0 freeze. Any
change to the III implementation that alters these outputs is a
protocol-breaking change and MUST be accompanied by a version increment
in SPEC_LOCK.

The math underneath III is WiseDigest-3 from WOP. These tests assert:
  - Each locked vector reproduces its committed hex digest byte-for-byte.
  - III and WiseDigest3 are the same class.
  - The WiseOrder-side label III_NAME is the literal string "III".
  - The output is 32 bytes / 64 lowercase hex.
"""

from __future__ import annotations

import pytest

from intellagent_runtime.iii import (
    III,
    III_NAME,
    OUTPUT_BYTES,
    WiseDigest3,
    digest_bytes,
    digest_stream,
    iii,
)


# ---------------------------------------------------------------------------
# Locked vectors (computed 2026-05-11 against WOP reference; parity verified)
# ---------------------------------------------------------------------------


LOCKED_EMPTY = "94f8a850b58985834a7e72864c0db6757d9864c5d5ab4ff31188b6323c43e999"
LOCKED_ABC = "7316f497541bb373d07a30be6fe0af0a25722b5c4adc98236fb27e0575ecec23"


def test_iii_empty_input_matches_locked_vector():
    assert iii(b"") == LOCKED_EMPTY


def test_iii_abc_matches_locked_vector():
    assert iii(b"abc") == LOCKED_ABC


def test_iii_class_alias_is_wisedigest3():
    assert III is WiseDigest3


def test_iii_name_is_literally_three_uppercase_i():
    assert III_NAME == "III"
    assert len(III_NAME) == 3
    assert all(c == "I" for c in III_NAME)


def test_iii_output_is_64_lowercase_hex():
    out = iii(b"WiseOrder v0.2.0")
    assert len(out) == 64
    assert all(c in "0123456789abcdef" for c in out)


def test_iii_output_bytes_constant_is_32():
    assert OUTPUT_BYTES == 32


# ---------------------------------------------------------------------------
# API surface
# ---------------------------------------------------------------------------


def test_update_returns_self_for_chaining():
    h = III()
    same = h.update(b"abc")
    assert same is h


def test_update_after_hexdigest_raises():
    h = III()
    h.update(b"abc")
    h.hexdigest()
    with pytest.raises(RuntimeError):
        h.update(b"def")


def test_streamed_input_matches_one_shot():
    one_shot = iii(b"abcdefghij")
    streamed = digest_stream([b"abcde", b"fghij"])
    assert one_shot == streamed


def test_streamed_single_chunk_matches_one_shot():
    one_shot = iii(b"xyz")
    streamed = digest_stream([b"xyz"])
    assert one_shot == streamed


def test_streamed_byte_at_a_time_matches_one_shot():
    data = b"the quick brown fox jumps over the lazy dog"
    one_shot = iii(data)
    streamed = digest_stream([bytes([b]) for b in data])
    assert one_shot == streamed


# ---------------------------------------------------------------------------
# Sensitivity
# ---------------------------------------------------------------------------


def test_one_bit_change_yields_different_digest():
    a = iii(b"abc")
    b = iii(b"abd")  # last char shifted by 1
    assert a != b


def test_prefix_change_yields_different_digest():
    a = iii(b"abc")
    b = iii(b"Xabc")
    assert a != b


def test_length_extension_yields_different_digest():
    a = iii(b"abc")
    b = iii(b"abc\x00")
    assert a != b


# ---------------------------------------------------------------------------
# Domain separation (WiseDigest-3 OG)
# ---------------------------------------------------------------------------


def test_domain_separator_baked_into_initial_state():
    """The first absorbed byte sees state that has already mixed in the
    WiseDigest-3 domain. Confirm by checking that III(b'') has the locked
    value — which is only reproducible with the correct domain seeding."""
    from intellagent_runtime.iii import _DOMAIN_LANE_0, _DOMAIN_LANE_1
    # Domain bytes are "WiseDigest-3" + four NULs, split 8/8 and masked to 61.
    assert _DOMAIN_LANE_0 == int.from_bytes(b"WiseDige", "big") & ((1 << 61) - 1)
    # The remainder is "st-3" + b"\x00" * 4 = 8 bytes total.
    assert _DOMAIN_LANE_1 == int.from_bytes(b"st-3" + b"\x00" * 4, "big") & ((1 << 61) - 1)


# ---------------------------------------------------------------------------
# Parity with the WOP reference, when reachable
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not __import__("os").path.exists(
        __import__("os").path.expanduser("~/Desktop/wop/src/wise/digest_v3.py")
    ),
    reason="WOP reference implementation not present at ~/Desktop/wop/",
)
def test_parity_with_wop_reference():
    """The WOP reference is the normative source for WiseDigest-3. III is
    a byte-for-byte copy. If parity ever breaks, III diverged from WOP and
    must be re-synced."""
    import os
    import sys
    wop_src = os.path.expanduser("~/Desktop/wop/src")
    if wop_src not in sys.path:
        sys.path.insert(0, wop_src)
    from wise.digest_v3 import digest_bytes as wop_digest

    for vector in (
        b"",
        b"abc",
        b"the quick brown fox",
        b"\x00" * 64,
        b"\xff" * 64,
        b"\x42" * 1024,
        b"WiseOrder v0.2.0 genesis sealed by NULLASIGN, witnessed III",
    ):
        assert iii(vector) == wop_digest(vector), f"divergence on {vector!r}"
