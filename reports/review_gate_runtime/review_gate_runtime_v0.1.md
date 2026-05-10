# Review Gate Runtime v0.1 self-check

- timestamp: `2026-05-09T00:48:04.756846Z`
- all_passed: `True`

## Fixtures

- `valid_proposal_approved` — **PASS** — decision=`approved`
  - review_id: `review-review_gate_01-proposal-canon_guardian_01-WO-FIX-REVIEW-VALID-001-FIXED-20260509T004804753815Z`
  - review_hash: `sha256:d09364db528cb9cf77c772aaa5a5a36aee5682f21599df43080d8d45f1156528`
  - detail: decision=approved, scope=3, reasons=[], exit=0
- `bad_hash_rejected` — **PASS** — decision=`rejected`
  - review_id: `review-review_gate_01-proposal-canon_guardian_01-WO-FIX-REVIEW-VALID-001-FIXED-20260509T004804754877Z`
  - review_hash: `sha256:68c0e268b57161849cdca89188b5f312f1c2b2f72bfe0febcfda702bc5a89db4`
  - detail: decision=rejected, hash_verified=False, reasons=['deterministic_hash_mismatch']
- `forbidden_command_rejected` — **PASS** — decision=`rejected`
  - review_id: `review-review_gate_01-proposal-canon_guardian_01-WO-FIX-REVIEW-FORBIDDEN-003-FIXED-20260509T004804755209Z`
  - review_hash: `sha256:1be746ebbb751c3063dbfc936069c3b7afab87fa8b9a7fde66126760254f815a`
  - detail: decision=rejected, reasons=['forbidden_command']
- `too_many_commands_rejected` — **PASS** — decision=`rejected`
  - review_id: `review-review_gate_01-proposal-canon_guardian_01-WO-FIX-REVIEW-TOOMANY-004-FIXED-20260509T004804755505Z`
  - review_hash: `sha256:06b42a130af1c33bdde9eb4babeeb6258dc752c266553d5068e01ea41fe6a848`
  - detail: decision=rejected, reasons=['too_many_commands']
- `empty_rationale_rejected` — **PASS** — decision=`rejected`
  - review_id: `review-review_gate_01-proposal-canon_guardian_01-WO-FIX-REVIEW-NORATIONALE-005-FIXED-20260509T004804755772Z`
  - review_hash: `sha256:7bb95207699d77af82437339aed1c772a269d57e91e91341439cf94f970e76f2`
  - detail: decision=rejected, reasons=['empty_rationale']
- `wrong_work_order_id_rejected` — **PASS** — decision=`rejected`
  - review_id: `review-review_gate_01-proposal-canon_guardian_01-WO-FIX-REVIEW-WRONGWO-006-FIXED-20260509T004804756097Z`
  - review_hash: `sha256:7ddeb001291d3220018ce7c71ce8e7a8d40445e0a116dde7fb89dd3b7bf7ef0e`
  - detail: decision=rejected, reasons=['wrong_work_order_id']
- `unknown_proposer_rejected` — **PASS** — decision=`rejected`
  - review_id: `review-review_gate_01-proposal-unknown_99-WO-FIX-REVIEW-UNKNOWN-007-FIXED-20260509T004804756337Z`
  - review_hash: `sha256:8817f430297e7b925097d21343b4d441f0d388364071a4650a00e9bc7de52e00`
  - detail: decision=rejected, reasons=['unknown_proposer']
- `review_artifact_hash_stable` — **PASS** — decision=`approved`
  - review_id: `review-review_gate_01-proposal-canon_guardian_01-WO-FIX-REVIEW-STABLE-008-FIXED-20260509T004804756550Z`
  - review_hash: `sha256:bb4968fc843847934aa3f2bebfa10287d73ec12e48b35b976dbc62dd2bdce491`
  - detail: first_hash=sha256:bb4968fc843847934aa3f2bebfa10287d73ec12e48b35b976dbc62dd2bdce491, second_hash=sha256:bb4968fc843847934aa3f2bebfa10287d73ec12e48b35b976dbc62dd2bdce491, ids_differ=True, timestamps_differ=True

## Reviewer authority law

> The reviewer gate has approval authority only over proposal admissibility. It has zero execution authority. Executor admission remains controlled by the real-agent runtime.
