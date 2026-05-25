# ADOPTION_REALITY

What `wiseorder-protocol` and `wiseorder` are good for today, who experiences the pain they solve, and what would break under scale. No hype. No fantasy. The honest answer for someone considering depending on this code.

## The pain each layer solves

### `wiseorder-protocol`

**Solves:** the operator who runs LLM-driven actions in any domain where "what did the LLM actually do, under which rules, who authorized it, and how do I prove it later" is a real question.

**Concrete examples of the pain:**
- A regulator asks an operator to produce a tamper-evident audit log of every LLM-driven action that affected a customer's records over the past 90 days.
- A compliance officer wants to know whether a model output that triggered a downstream side effect was approved under the policy in force at the time, or under a since-deprecated policy.
- A protocol designer wants a primitive for "this action was rejected, here's the structured reason, sealed and verifiable."
- A research engineer needs to replay a multi-step LLM-driven decision deterministically and inspect every transition.

**Not solving:** "make my LLM smarter." "Detect hallucinations." "Score model accuracy." These are different problems.

### `wiseorder` (runtime)

**Solves:** the engineer who runs git-event-driven workflows that need (a) human approval gates, (b) idempotency across duplicate events, (c) crash safety with bounded resource use, (d) inspectable failure modes.

**Concrete examples of the pain:**
- A small ops team wants every commit to a production repo to trigger an engineering summary + approval card before downstream deploys.
- A solo developer wants a local "what's changed and is it OK" gate before pushing code to public clients.
- A platform team wants a templated workflow engine that survives `kill -9` and Postgres restart without losing or duplicating work.

**Not solving:** "deploy my containers." "Replace my CI/CD." "Be Temporal/Airflow/Prefect." The runtime is intentionally narrower than any of those.

## Who experiences this pain today

A small but real set. Honest ordering by today's likely fit:

1. **Solo / small-team operators of LLM-driven workflows** in regulated industries (legal, finance, healthcare, gov-adjacent). They need provenance and don't have SOC-2-grade vendor budget. **The protocol's chain + the runtime's approval gate are designed for them.** ~hundreds of orgs globally; growing as regulation lands.
2. **Internal-tools engineers at AI product companies** who want a hash-chained audit log without buying a third-party governance vendor. **The protocol is the answer; the runtime is optional.** ~dozens of teams today; thousands in 12-24 months.
3. **Protocol researchers** studying governance kernels as a primitive separate from agent frameworks. **The protocol's class-based regime system + audit chain is the research artifact.** ~10–50 researchers today.
4. **Reliability engineers** at small AI infrastructure teams who need a workflow engine narrower than Temporal but more inspectable than a homegrown FastAPI app. **The runtime is the answer.** ~hundreds of teams; this is a niche but real fit.

What this NOT fits today:
- Large enterprises with existing governance investments (Datadog, SIEM, etc.). They have inertia; this protocol doesn't displace it.
- Hobbyists who want a one-click AI safety wrapper. The setup cost is real (Postgres + Redis + Python + LLM key).
- Anyone who wants the chain primitive to be cryptographically certified against an adversary with multi-year compute budgets. **WiseDigest-3 cryptanalysis is deferred.** Use SHA-256 if you need a verified primitive today.

## Operational workflows that fit

- **Pre-deployment review gate.** Watch a repo; every commit produces an approval card; nothing reaches prod until a human clicks. This is the runtime's default workflow.
- **Compliance audit trail.** Each consequential LLM action is sealed as a transition in the chain. A future regulator request hits a hash-chained log, not a database table that can be modified.
- **Protocol research.** Run experimental governance scenarios with deterministic clock injection; replay them byte-for-byte.
- **AI tool authoring.** Wrap your tool's actions in `governed-run` from the CLI; refuse the dangerous ones; seal the rest.

## Operational workflows that do NOT fit

- **High-throughput event streaming.** The runtime is event-driven but single-process; Redis SETNX dedup is correct but synchronous. >100 commits/sec to a single watched repo is not the design point.
- **Multi-tenant SaaS.** One Postgres database = one runtime's worth of state. There is no namespace isolation between tenants.
- **Distributed coordination.** The protocol is single-host. There is no `intellagent`-cluster mode and no design for one.
- **Real-time autonomous agents.** Every action requires human approval by default. An autonomous loop is possible but explicitly out of scope (and contrary to the protocol's "kernel + gate" philosophy).
- **Anything that cannot tolerate ~10-minute LLM-call latencies under provider strain.** The runtime caps LLM timeouts at 60s × 2 retries × backoff; worst case ~6 minutes per workflow before fail.

## What would break under scale

Honest answers, not aspirational marketing:

| scale | what breaks |
|---|---|
| Watch >5 repos simultaneously | nothing yet; tested with 1; should be fine to ~10 before Watchdog's recursive watching gets noisy. |
| >100 commits/hour | nothing yet; rate is well under any limit. |
| >100 commits/minute | Postgres connection pool tightens (default `pool_pre_ping=True` and `expire_on_commit=False`); may need pool tuning. |
| >2 worker processes | Redis SETNX dedup is correct. JSONB `workflows.logs` read-modify-write race becomes possible (FAILURE_MODEL.md F11). |
| Multi-host workers | Redis SETNX still works. The orphan reaper runs per-host; if host A reaps host B's workflows, host B might be mid-execution. Not designed for. |
| >10,000 chain triples | `verify_chain` is O(N) over the chain; would take ~10s at that size. Filename sort is the dominant factor. Pagination doesn't exist. |
| Postgres database approaching 1 GB | `workflows.logs` JSONB grows monotonically (no pruning). Add a retention policy or your database grows without bound. |

## What assumptions are unsafe at scale

- **"Wall-clock timestamps in chain triples are unique."** True at single-host single-thread; could collide under microsecond-level concurrency. The filename derivation `<sealed_at>-<head8>.win` adds the hash prefix as a safety net, but the collision is undocumented.
- **"`os.rename` is atomic across reboots."** True on a single POSIX filesystem; false across NFS, false across some FUSE implementations, undocumented across remote sync (Dropbox, iCloud).
- **"The protocol survives any crash."** Provably true under POSIX with `write_atomic` semantics and our staging-finalize pattern. NOT proven under kernel panic mid-`write_atomic` (the temp file might or might not flush; the rename might or might not commit). Real disk failure scenarios are out of scope.
- **"WiseDigest-3 is collision-resistant."** The math suggests it is; external cryptanalysis is deferred. Treat the primitive as research-grade until that completes.
- **"Two LLM providers produce equivalent governance behavior."** False. Prompt templates in `prompts/` were tuned against Claude Sonnet 4.6. Switching to OpenAI or Groq will work syntactically but may produce different `risk_level` assignments. The protocol layer is provider-agnostic; the runtime's prompt templates are not.

## What remains research-grade

- **WiseDigest-3 cryptanalysis.** Documented in `wop/research/`. No external review yet.
- **Cross-language verifier parity proof.** The three first-party tracks (Python, Rust, Go) all agree on three frozen fingerprints. A third-party verifier in a fourth language would change "verifier parity claim" from `NOT_COMPLETE` to `COMPLETE` (see `docs/release/THIRD_PARTY_VERIFIER_BRIEF_v0.1.md`).
- **`governed-run --execute` adversarial escape resistance.** `sandbox-exec` on macOS and bwrap-style isolation on Linux are exercised by `tests/test_sandbox_escape_check.py`, but the test set is illustrative, not exhaustive.
- **`Class C` Ed25519 attester identity model.** New in `vectors/v0.2.0/`. The model is documented but the vectors are not yet frozen at `SPEC_LOCK_v0.2.0`.

## What is production-capable today

Honest, narrow list:

- The Python verifier (`intellagent_runtime/chain.py`, `memory.py`) for chains containing < 1000 triples.
- The Rust and Go verifiers for the same constraint.
- The `intellagent governed-run --dry-run` flow for parsing markdown work orders and producing structured refusals or plans.
- The `wiseorder` runtime's single-process commit pipeline for ~100 commits/hour on a single watched repo.
- The `verify.sh` portable-drive verifier for offline integrity proofs.

These are the use cases an engineer could deploy today and bet a small team's work on. Outside this list, you are choosing experimental software; document that choice.

## What this document is NOT

- A pitch. Nobody adopts this because of a doc; they adopt because the pain matches and the proof is reproducible.
- A roadmap. See `docs/strategy/MASTER-ROADMAP-v0.1.md` if you want the long view.
- A guarantee. Adoption is the operator's risk; we document what we know.

The honest closing claim: **`wiseorder-protocol` and `wiseorder` are good infrastructure for a narrow but real set of problems, with explicit limits.** Use them where the limits don't bite. Use SHA-256 if the cryptanalysis status bothers you. Use Temporal if you need distributed coordination. Use this when "what happened, who approved it, can I prove it offline" is your actual question.
