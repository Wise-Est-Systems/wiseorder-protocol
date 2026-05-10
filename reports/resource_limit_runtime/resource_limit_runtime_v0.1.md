# Resource Limit Runtime v0.1 self-check

- timestamp: `2026-05-09T00:48:15.994364Z`
- platform: `Darwin`
- isolation_mode: `sandbox-exec+rlimits`
- all_passed: `True`

## Fixtures

- `allowed_pwd_succeeds` — **PASS**
  - manifest: `/Users/thekingflame/Desktop/wiseorder-protocol/reports/resource_limit_runtime/runs/run-20260509T004814114655Z-allowed_pwd_succeeds.json`
  - detail: status=ok, exit=0, rlimits_applied={'cpu': True, 'memory': False, 'fd': True, 'nproc': True}
- `stdout_flood_truncates_deterministically` — **PASS**
  - manifest: `/Users/thekingflame/Desktop/wiseorder-protocol/reports/resource_limit_runtime/runs/run-20260509T004814122375Z-stdout_flood_truncates_deterministically.json`
  - detail: truncated=True, len=65536, hash=sha256:bf718b6f653bebc18…
- `sleep_timeout_kills_process_group` — **PASS**
  - manifest: `/Users/thekingflame/Desktop/wiseorder-protocol/reports/resource_limit_runtime/runs/run-20260509T004814144111Z-sleep_timeout_kills_process_group.json`
  - detail: status=timed_out, killed=True, duration=504ms
- `nested_child_must_not_survive_parent_death` — **PASS**
  - manifest: `/Users/thekingflame/Desktop/wiseorder-protocol/reports/resource_limit_runtime/runs/run-20260509T004814652073Z-nested_child_must_not_survive_parent_death.json`
  - detail: killed=True, child_pid=34179, child_alive=False
- `fd_exhaustion_rejected` — **PASS**
  - manifest: `/Users/thekingflame/Desktop/wiseorder-protocol/reports/resource_limit_runtime/runs/run-20260509T004815769917Z-fd_exhaustion_rejected.json`
  - detail: exit=7, fd_applied=True, stderr_head=OPEN-FAIL-AT-29: OSError: [Errno 24] Too many open files: 'fd_29.txt'
- `memory_exhaustion_handled` — **PASS**
  - manifest: `/Users/thekingflame/Desktop/wiseorder-protocol/reports/resource_limit_runtime/runs/run-20260509T004815830771Z-memory_exhaustion_handled.json`
  - detail: macOS/post-hoc path: applied=False, peak_rss=268222464, violations=['memory_overrun']
- `fork_attempt_rejected` — **PASS**
  - manifest: `/Users/thekingflame/Desktop/wiseorder-protocol/reports/resource_limit_runtime/runs/run-20260509T004815887179Z-fork_attempt_rejected.json`
  - detail: exit=8, nproc_applied=True, stderr_head=FORK-BLOCKED: [Errno 35] Resource temporarily unavailable
- `excessive_command_count_rejected_pre_exec` — **PASS**
  - detail: final_status=rejected_pre_exec, code=command_count_overflow, results_len=0
- `sandbox_size_over_limit_detected` — **PASS**
  - manifest: `/Users/thekingflame/Desktop/wiseorder-protocol/reports/resource_limit_runtime/runs/run-20260509T004815913386Z-sandbox_size_over_limit_detected.json`
  - detail: sandbox_size=2097152, limit=1048576, violations=['sandbox_size_overrun']
- `repo_fingerprint_unchanged` — **PASS**
  - manifest: `/Users/thekingflame/Desktop/wiseorder-protocol/reports/resource_limit_runtime/runs/run-20260509T004815936234Z-repo_fingerprint_unchanged.json`
  - detail: before==after: True, status=ok
- `manifest_resource_fields_populated` — **PASS**
  - manifest: `/Users/thekingflame/Desktop/wiseorder-protocol/reports/resource_limit_runtime/runs/run-20260509T004815944240Z-manifest_resource_fields_populated.json`
  - detail: missing_fields=[]
- `deterministic_truncation_hashes_stable` — **PASS**
  - detail: hash1=sha256:bf718b6f653bebc18…, hash2=sha256:bf718b6f653bebc18…, equal=True

## Bounded-runtime law

> Governance determines admissibility. Kernel isolation constrains scope. Resource limits constrain survivability.
