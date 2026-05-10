# Pipeline Runtime v0.1 self-check

- timestamp: `2026-05-10T15:50:49.080393Z`
- all_passed: `True`

## Fixtures

- `valid_pipeline_executes_allowed_command` — **PASS** — final_status=`executed` — executor_invoked=`True`
  - pipeline_id: `pipeline-20260510T155048325905Z`
  - pipeline_hash: `sha256:170d8651c4e109f1bd8b25c4dbbdc1f418f01be53b3f1f6c77520c7048c4a83e`
  - detail: final_status=executed, executed=['pwd'], executor_manifest=present
- `reviewer_rejection_prevents_executor_call` — **PASS** — final_status=`refused_at_review` — executor_invoked=`False`
  - pipeline_id: `pipeline-20260510T155048507258Z`
  - pipeline_hash: `sha256:5b1be0a17b9dbef7cb8a18a705aff89a79bee2dc9228d7377d6cac51d33e5efb`
  - detail: final_status=refused_at_review, refusal=wrong_work_order_id, executor_invoked=False
- `mutated_proposal_hash_rejected` — **PASS** — final_status=`refused_at_review` — executor_invoked=`False`
  - pipeline_id: `pipeline-20260510T155048508304Z`
  - pipeline_hash: `sha256:3c256891c5dde0401ccf869d01dec92e226a42b185d923ad57d98df56cdf5245`
  - detail: review_decision=rejected, hash_verified=False, reasons=['deterministic_hash_mismatch']
- `forbidden_command_proposal_rejected` — **PASS** — final_status=`refused_at_review` — executor_invoked=`False`
  - pipeline_id: `pipeline-20260510T155048509244Z`
  - pipeline_hash: `sha256:fa84f8c70afcf672004d1b5bb7801c440a056e20d1eee3ea579607202327dd2d`
  - detail: final_status=refused_at_review, refusal=no_commands_to_approve, proposed=[], executor_invoked=False
- `wrong_executor_identity_refused` — **PASS** — final_status=`refused_at_executor` — executor_invoked=`True`
  - pipeline_id: `pipeline-20260510T155048509981Z`
  - pipeline_hash: `sha256:c09d74baf0afd588296ec9bfc5c49ec5c7de4303dfac7707a259ffa5092917d0`
  - detail: final_status=refused_at_executor, executed=[], violations=['assigned_to_mismatch']
- `source_repo_unchanged_after_pipeline` — **PASS** — final_status=`executed` — executor_invoked=`True`
  - pipeline_id: `pipeline-20260510T155048511279Z`
  - pipeline_hash: `sha256:047a72ae361ba10f07bd2840cb897b55fb4a02fec75b95b784b332fe810c6965`
  - detail: fp_pipeline_match=True, fp_outer_match=True, final_status=executed
- `aggregate_manifest_hash_stable` — **PASS** — final_status=`executed` — executor_invoked=`True`
  - pipeline_id: `pipeline-20260510T155048699892Z`
  - pipeline_hash: `sha256:830e784bed16c8f6ef2c799611943b86bbfd30485ec42868d5a1e76865fe31fe`
  - detail: first_hash=sha256:830e784bed16c8f6ef2c799611943b86bbfd30485ec42868d5a1e76865fe31fe, second_hash=sha256:830e784bed16c8f6ef2c799611943b86bbfd30485ec42868d5a1e76865fe31fe, ids_differ=True
- `no_execution_occurs_without_approved_review_artifact` — **PASS** — final_status=`n/a` — executor_invoked=`False`
  - pipeline_id: `(structural)`
  - pipeline_hash: `(structural)`
  - detail: checked=3/3 rejection fixtures, violations=[]

## Pipeline boundary law

> The pipeline does not create autonomy. The pipeline creates deterministic governed handoff between proposal, review, and execution. Execution remains bounded by real-agent runtime policy. Reviewer approval is necessary but not sufficient; executor admission still governs execution.
