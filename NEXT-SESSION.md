# NEXT-SESSION

**Where we left off:** 2026-05-23, end-of-session after v0.2.0 expansion seal.

## State at handoff

- `make ci` is **GREEN** across all 18 gates.
- v0.2.0 lock has three new sealed subsections (§2.5 D6 / §2.6 B4–B7 / §2.7 C5–C7).
- New chain head: `chain/2026-05-23T071437_482327Z-5964497c.win`. Chain status: `CHAIN_VALID`.
- v0.1.0 is untouched (frozen).

## What landed this session

| Area | Surface | Files |
|---|---|---|
| D6 preimage size cap | spec §2.5 + vector + test + enforcement | `SPEC_LOCK_v0.2.0.md §2.5`, `vectors/v0.2.0/class-d-preimage-oversized.json`, `tests/test_d5_preimage_size_cap.py`, code in all 3 verifiers |
| Class B state machine | spec §2.6 + 3 vectors + 17-test module | `SPEC_LOCK_v0.2.0.md §2.6`, `vectors/v0.2.0/class-b-transition-*.json`, `tests/test_class_b_state_machine.py` |
| Identity model (Ed25519) | spec §2.7 + 2 vectors + 17-test module | `SPEC_LOCK_v0.2.0.md §2.7`, `vectors/v0.2.0/class-c-*-signed-attestation.json` and `class-c-invalid-signature.json`, `tests/test_identity_model.py` |
| Triple-sweep cross-impl fuzzer | committed work + first post-v0.2.0 run | `tools/triple_sweep.py`, `tools/classify_disagreements.py`, `reports/triple_sweep/20260523T071041Z/`, `reports/triple_sweep/KNOWN-CANONICALIZATION-GAPS-v0.2.0.md` |
| Work orders | 3 WO docs + 3 spec patches | `work_orders/WO-D5-SIZE-CAP.md`, `work_orders/WO-CLASS-B-STATE-MACHINE.md`, `work_orders/WO-IDENTITY-MODEL.md` and their `*-spec-patch.md` siblings |

## Open follow-ups (v0.3.0 candidates)

1. **Verifier enforcement of B4–B7** — 6 xfail-strict tests in `tests/test_class_b_state_machine.py`. When verifier learns the transition rules, those flip to plain pass and `xfail(strict=True)` forces the markers to be removed.

2. **Verifier enforcement of C5–C7** — 3 xfail-strict tests in `tests/test_identity_model.py`. Needs Ed25519 verification wired into Python + Rust + Go verifier tracks. Python: install `cryptography` as a runtime dep OR pull in a pure-stdlib Ed25519 implementation. Rust: `ed25519-dalek`. Go: stdlib `crypto/ed25519`.

3. **Cross-impl canonicalization gaps** — Task #8 in the task list. See `reports/triple_sweep/KNOWN-CANONICALIZATION-GAPS-v0.2.0.md`. Two paths (tighten canonicalizers vs narrow spec scope) — decision is a separate work order.

4. **Key rotation / revocation / expiry for Class C identity** — out of scope per §2.7.6. v0.3.0 work.

## Strategic next phase (Phase 2 from the roadmap)

Spec is sealed enough. The next push is **adoption-readiness** — making a stranger able to use WiseOrder in 60 seconds. From the roadmap:

- One-line install (`pip install wiseorder` or `npx wiseorder`)
- 5-minute Hello-World: pipe any AI output → get a sealed receipt back
- Landing sentence: *"Receipt printer for AI decisions"*
- Working examples for the 3 SDKs that matter (OpenAI, Anthropic, LangChain)

This is "make it adoptable," not "fix the spec." The spec is no longer the blocker.

## Notes for whoever picks this up

- **Worktree write-blocks happened mid-session** when spawning sub-agents via `Agent` tool with `isolation: worktree`. Three agents got far enough to design but couldn't write files. Workaround: spawn agents WITHOUT worktree isolation, or apply agent designs manually as I did here.
- **The Henry Wayne Wise III digest (`III`) is the v0.2.0 chain algorithm**, byte-for-byte parity with WOP's `WiseDigest-3`. Don't rename it. The chain depends on the literal string `"III"` in every triple.
- **`cryptography` library was installed in the venv this session** for Ed25519 vector generation only. It is NOT yet a declared runtime dep in `pyproject.toml`. If you wire Ed25519 verification into the verifier, decide first whether to add it to deps or use a stdlib-only implementation.

## To resume

```bash
cd ~/Desktop/wiseorder-protocol
make ci                                    # should be green
git status                                 # see uncommitted work for review
.venv/bin/python -m pytest tests/ -q       # full test pass
```
