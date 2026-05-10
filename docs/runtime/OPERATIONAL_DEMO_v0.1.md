# Operational Demo — Replayable Governed Workflow (v0.1)

**Status:** Implemented. Single command runs the full demo. 8 deterministic fixtures cover safe-execution and unsafe-refusal branches.
**Adopted:** 2026-05-10
**Authority:** `PIPELINE-RUNTIME-v0.1.md` is the spec. `tools/pipeline_runtime.py` is the implementation. This document captures a live replay of the demo with real hashes.

---

## 1. What the Demo Proves

The pipeline runtime executes a fully governed workflow:

```
Work Order
   ↓
Proposer (governed candidate generation, zero execution authority)
   ↓
Review Gate (deterministic admission, zero execution authority)
   ↓
Executor (bounded execution, only on admitted proposals)
   ↓
Replay Manifest (proposer hash + review hash + executor manifest hash + pipeline hash)
   ↓
Independent verification (re-run produces byte-identical hashes)
```

For a proposal to reach the executor, the review gate MUST verify:
- The proposal artifact's deterministic hash has not been mutated.
- The work order ID matches.
- The proposed commands are admitted by policy.
- The executor identity is the declared agent.

A proposal failing any check produces a **sealed refusal artifact** at the stage that rejected it. The executor is NOT invoked. The repo fingerprint MUST equal before/after the pipeline run.

This is the work-order-006 minimum demo: **AI proposes a patch inside a bounded runtime; unsafe proposals produce a lawful refusal artifact; safe proposals produce a replayable execution manifest.**

---

## 2. Single Command

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
make pipeline-check          # 8 deterministic fixtures, both branches
make pipeline-run-fixture    # one valid run end-to-end with hashes
```

---

## 3. Captured Live Run (2026-05-10)

The 8-fixture self-check executes both safe and unsafe branches. Captured pipeline hashes (post-adversarial-vector lock):

| Fixture | Branch | Final status | Pipeline hash |
|---|---|---|---|
| `valid_pipeline_executes_allowed_command` | safe | `executed` | `sha256:170d8651c4e109f1bd8b25c4dbbdc1f418f01be53b3f1f6c77520c7048c4a83e` |
| `reviewer_rejection_prevents_executor_call` | unsafe | `refused_at_review` | `sha256:5b1be0a17b9dbef7cb8a18a705aff89a79bee2dc9228d7377d6cac51d33e5efb` |
| `mutated_proposal_hash_rejected` | unsafe | `refused_at_review` | `sha256:3c256891c5dde0401ccf869d01dec92e226a42b185d923ad57d98df56cdf5245` |
| `forbidden_command_proposal_rejected` | unsafe | `refused_at_review` | `sha256:fa84f8c70afcf672004d1b5bb7801c440a056e20d1eee3ea579607202327dd2d` |
| `wrong_executor_identity_refused` | unsafe | `refused_at_executor` | `sha256:c09d74baf0afd588296ec9bfc5c49ec5c7de4303dfac7707a259ffa5092917d0` |
| `source_repo_unchanged_after_pipeline` | safe | `executed` | `sha256:047a72ae361ba10f07bd2840cb897b55fb4a02fec75b95b784b332fe810c6965` |
| `aggregate_manifest_hash_stable` | safe | `executed` | `sha256:830e784bed16c8f6ef2c799611943b86bbfd30485ec42868d5a1e76865fe31fe` |
| `no_execution_occurs_without_approved_review_artifact` | structural | n/a | (structural; no executor call possible) |

A reproducer running `make pipeline-check` MUST observe these eight pipeline hashes byte-for-byte. A divergence is a non-conformance.

---

## 4. Sample Replay Manifest (Safe Branch)

The `pipeline-run-fixture` target produces one canonical valid run. Live capture:

```text
PIPELINE pipeline-20260510T155011233962Z final_status=executed exit_status=0
  proposer_hash:           sha256:ae5990c6575838f193e21334e8e295d591aaf102dbb1e736b1fe786c4f7e8717
  review_hash:             sha256:595c6b4358adaaacde161cfadefa14dc2ad2d5a2bbcd1263fd2ed194230790bb
  executor_manifest_hash:  sha256:2496fae759f4b8c4337f5f4c6b52c692ea33f3df948702ca3868dd3460af9473
  pipeline_hash:           sha256:6d5a9c38aeafc02ccb15734c74122cd24e39466ccc675e0d7138ed0f5cadd0ca
  commands_proposed: ['pwd']
  commands_approved: ['pwd']
  commands_executed: ['pwd']
```

The `pipeline_hash` is computed over the canonicalized concatenation of `proposer_hash`, `review_hash`, and `executor_manifest_hash`. Any modification of any stage's artifact changes the pipeline hash.

`commands_proposed == commands_approved == commands_executed` is the safe-branch invariant. When they differ, the executor MUST NOT have invoked the rejected commands. The repo fingerprint at the end of the pipeline equals the fingerprint at the start.

Note: `pipeline-run-fixture` regenerates a fresh timestamped pipeline_id on every run. The four stage hashes (`proposer_hash`, `review_hash`, `executor_manifest_hash`, `pipeline_hash`) MUST be stable across runs given identical inputs; the timestamp is a non-content field.

---

## 5. Sample Refusal Artifact (Unsafe Branch — Forbidden Command)

When a proposer emits a command not in the admit-list, the review gate produces a sealed refusal:

```json
{
  "final_status": "refused_at_review",
  "policy_violations": [
    {
      "code": "no_commands_to_approve",
      "stage": "review_gate",
      "detail": []
    }
  ],
  "refusal_reason": "no_commands_to_approve",
  "executor_manifest": null,
  "executor_manifest_hash": null,
  "exit_status": 1,
  "repo_fingerprint_before": "sha256:94db1c54e446523993454c89413a6fc703108a0d45e3a4e3d0c3e15cb761bdb7",
  "repo_fingerprint_after":  "sha256:94db1c54e446523993454c89413a6fc703108a0d45e3a4e3d0c3e15cb761bdb7"
}
```

The repo fingerprint is identical before and after. The executor was NOT invoked. The refusal itself is a sealed artifact with its own hash, retained for audit. This is the work order's required behavior: **lawful refusal as a recorded outcome, not silent dropping**.

Other unsafe-branch refusal types observed in the demo:
- `wrong_work_order_id` — proposal references a different work order than the review gate expects.
- `deterministic_hash_mismatch` — proposal JSON was hand-mutated between propose() and review().
- `wrong_executor_identity` — admitted proposal handed to an executor whose declared identity does not match.

Each refusal type is a distinct sealed artifact; the executor is reached only when none fire.

---

## 6. What This Demo Establishes

**Establishes:**
- The runtime supports the proposal → review → execution flow under v0.1.
- Refusal is a structurally recorded outcome at every stage that can refuse.
- A safe pipeline produces deterministic, replayable hashes.
- The executor is not reachable without an admitted proposal.
- The repo fingerprint is invariant across refused pipelines.

**Does not establish:**
- That the executor's sandbox is unbreakable. The demo runs `pwd`, not arbitrary code; OS isolation under adversarial code is the subject of `OS-ISOLATION-RUNTIME-v0.1.md` (partial) and is out of scope for this demo.
- That the proposer cannot be social-engineered. The proposer is a deterministic stub in the demo; transformer-backed proposers are governed by `TRANSFORMER-PROPOSER-v0.1.md`.
- That the demo is exhaustive. 8 fixtures cover both branches structurally; they do not cover every possible adversarial input.

---

## 7. Reproduction by an Independent Reviewer

```bash
git clone <this repo>
cd wiseorder-protocol
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
make pipeline-check
python3 -c "
import json
r = json.load(open('reports/pipeline_runtime/pipeline_runtime_v0.1.json'))
for f in r['fixtures']:
    print(f\"{f['name']:55} | {f['final_status']:25} | {f['pipeline_hash']}\")
"
```

The eight pipeline hashes printed MUST match §3 byte-for-byte under v0.1.0. A divergence is filed under `AUDIT_SCOPE_v0.1.md §10`.
