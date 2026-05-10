# Authorization Policies (v0.1)

Each `<source_id>.json` file in this directory describes a policy enforced by
that authorization source. The runtime's `AuthorizationGate` resolves a
declared `authorization.source_id` to one of these files and applies the
policy against an action-bearing transition.

v0.1 supports two policy kinds:

- **`always_deny`** — refuses every action. Useful for tests.
- **`allowlist`** — allows only `(action.kind, action.target)` pairs in `allowed`.

Adding a new policy file does not modify the runtime; the policy is loaded by
`source_id` at evaluation time.
