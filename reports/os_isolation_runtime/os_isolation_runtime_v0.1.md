# OS Isolation Runtime v0.1 self-check

- timestamp: `2026-05-09T00:48:11.373969Z`
- isolation_mode: `sandbox-exec`
- sandbox-exec binary: `/usr/bin/sandbox-exec`
- all_passed: `True`

## Fixtures

- `allowed_pwd_command_succeeds_inside_isolation` — **PASS**
  - run_manifest: `/Users/thekingflame/Desktop/wiseorder-protocol/reports/os_isolation_runtime/runs/run-20260509T004810729120Z-allowed_pwd_command_succeeds_inside_isolation.json`
  - detail: status=ok, exit=0, kernel=True, hash=sha256:97da75900415dd546…
- `forbidden_curl_blocked_before_spawn` — **PASS**
  - run_manifest: `/Users/thekingflame/Desktop/wiseorder-protocol/reports/os_isolation_runtime/runs/run-20260509T004810736198Z-forbidden_curl_blocked_before_spawn.json`
  - detail: status=blocked_by_classifier, kernel=False, reason=matches forbidden pattern 'curl'
- `write_outside_sandbox_denied_by_kernel_policy` — **PASS**
  - run_manifest: `/Users/thekingflame/Desktop/wiseorder-protocol/reports/os_isolation_runtime/runs/run-20260509T004810736483Z-write_outside_sandbox_denied_by_kernel_policy.json`
  - detail: status=nonzero_exit, exit=1, target_exists=False, stderr_head=touch: /var/folders/jb/19ss9ry1019f1sz5_2x3dkt80000gn/T/_osisol_write_outside_34161_1778287690736: Operation not permitted
- `open_calculator_app_denied` — **PASS**
  - run_manifest: `/Users/thekingflame/Desktop/wiseorder-protocol/reports/os_isolation_runtime/runs/run-20260509T004810742987Z-open_calculator_app_denied.json`
  - detail: status=nonzero_exit, exit=1, stderr_head=Unable to find application named 'Calculator'
- `nested_subprocess_spawn_denied` — **PASS**
  - run_manifest: `/Users/thekingflame/Desktop/wiseorder-protocol/reports/os_isolation_runtime/runs/run-20260509T004810823575Z-nested_subprocess_spawn_denied.json`
  - detail: status=nonzero_exit, exit=126, denied_marker=True, stderr_head=/bin/sh: /bin/ls: Operation not permitted
- `repo_fingerprint_unchanged` — **PASS**
  - run_manifest: `/Users/thekingflame/Desktop/wiseorder-protocol/reports/os_isolation_runtime/runs/run-20260509T004810834283Z-repo_fingerprint_unchanged.json`
  - detail: before==after: True, status=ok
- `timeout_still_enforced` — **PASS**
  - run_manifest: `/Users/thekingflame/Desktop/wiseorder-protocol/reports/os_isolation_runtime/runs/run-20260509T004810841089Z-timeout_still_enforced.json`
  - detail: status=timed_out, timed_out=True, duration_ms=504
- `manifest_isolation_fields_populated` — **PASS**
  - run_manifest: `/Users/thekingflame/Desktop/wiseorder-protocol/reports/os_isolation_runtime/runs/run-20260509T004811349415Z-manifest_isolation_fields_populated.json`
  - detail: isolation_mode=sandbox-exec, hash_prefix=sha256:002366f1ca7f907fd…, path_exists=True, kernel=True
- `sandbox_profile_hash_stable` — **PASS**
  - detail: h1=sha256:7be98f42f230763a2…, h2=sha256:7be98f42f230763a2…, equal=True

## Isolation boundary law

> The kernel enforces the sandbox; the runtime enforces the policy. Governance determines admissibility; kernel isolation constrains damage radius.
