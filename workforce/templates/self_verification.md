# Self-Verification — <action_id>

Work order: `<work_order_id>`
Agent role: `<agent_role>`
Agent identity: `<assigned_to>`
Timestamp (UTC): `<ISO-8601>`

Each question must be answered explicitly with `yes` or `no` plus a one-sentence justification.
"Not applicable" is not an answer. If the question does not apply, state why.

1. Did I stay within the scope of the work order?
   - Answer: `yes` | `no`
   - Justification:

2. Did I modify only files in `allowed_files`?
   - Answer: `yes` | `no`
   - Justification:

3. Did I avoid every file in `forbidden_files`, including reads?
   - Answer: `yes` | `no`
   - Justification:

4. Did I run every gate listed in `required_gates` and capture the result?
   - Answer: `yes` | `no`
   - Justification:

5. Did I introduce pseudocode anywhere — code, comments, spec, docs?
   - Answer: `yes` | `no`
   - Justification:

6. Did I create semantic drift in any term, invariant, refusal scope, or replay behavior?
   - Answer: `yes` | `no`
   - Justification:

7. Did I alter canon, including implicit changes via documentation phrasing?
   - Answer: `yes` | `no`
   - Justification:

8. Did I alter the security posture, including by adding a permission, network call, or secret path?
   - Answer: `yes` | `no`
   - Justification:

9. Did I disclose every residual risk I am aware of, including risks that did not block submission?
   - Answer: `yes` | `no`
   - Justification:

10. Is every entry in the action log consistent with what I actually did, with no omissions and no edits after submission?
    - Answer: `yes` | `no`
    - Justification:
