# INTELLAGENT

## A Post-Attention Architecture for Governed Intelligence

**Status:** Architecture proposal, draft.
**Companion to:** WiseOrder Protocol v0.1.0 (this repository).
**Position:** *Proposed successor architecture, not finished universal intelligence.*

> Prediction is not intelligence.
> Attention is not judgment.
> Generation is not consequence.
>
> Transformers model probabilistic continuation.
> Intellagent models governed consequence formation.

---

## 1. Abstract

The current frontier of machine cognition is a probabilistic continuation engine: given a prefix, sample a next token; given a context, attend over it; given a prompt, generate a fluent reply. This architecture has been astonishingly productive. It has also been silently load-bearing on an assumption it does not enforce — that the next plausible token is also a *good* token, that the most attended-to context is also the most *load-bearing* context, that fluent output is also *correct* output. The assumption is not the architecture's fault. The assumption is what the architecture cannot, in principle, distinguish.

**Intellagent** is an intelligence architecture in which cognition is represented as **governed transitions between epistemic states**, constrained by evidence, uncertainty class, authorization, provenance, and consequence policy. It does not replace the transformer. It places the transformer as a *proposer* inside a governed state machine whose transitions must satisfy a kernel of legitimacy rules before they affect anything. The kernel is **WiseOrder Protocol v0.1.0**, defined in [`SPEC.md`](./SPEC.md) of this repository.

The thesis is narrow and falsifiable. It is not that transformers are wrong; it is that *prediction* is the wrong primitive for the part of intelligence that has to be answered for. We propose a different primitive: a typed transition between epistemic states, bound to the regime under which it can be verified, the authorization under which it can act, and the audit record under which it can be reviewed. Cognition becomes a search for legitimate paths, not a sample from a distribution.

This document defines the architecture's primitives, its kernel, its substrate, its runtime layout, and a prototype path. It claims nothing it cannot ground. Truth is not solved. Authorization is not solved. Implementation is not complete. There is no AGI here. What is here is a proposal — that the next architecture for intelligence should treat *consequence formation* as its central concern, and that the protocol-level scaffolding to do so already exists in `SPEC.md`.

---

## 2. The Transformer Assumption

The transformer architecture, as deployed today, factors cognition into three operations: **embed → attend → generate**. Inputs become vectors; vectors interact through scaled dot-product attention; the resulting distribution over next tokens is sampled. Stacked, this is a remarkably general continuation engine. It has produced the fluent generation, code synthesis, dialogue, translation, and tool-use behavior that defines the current era of AI.

The assumption — and it is genuinely an assumption, not a theorem — is that **the next-most-likely continuation under the training distribution is, often enough, a continuation that is true, useful, authorized, and safe**. This assumption has not failed catastrophically because:

1. The training distribution is enormous and reflects (imperfectly) the empirical world.
2. Reinforcement from human feedback layers preference into the distribution.
3. Constitutional and policy layers reject classes of generation post-hoc.
4. Tool use grounds some generations in deterministic systems.

These mitigations work. They are not the same as intelligence. They are *probability shaping* on top of a continuation engine that, by construction, has no internal concept of:

- A claim that has not yet been verified.
- A claim that *cannot* be verified, only conducted-toward.
- An action that is permitted versus an action that is authorized.
- A history of decisions that must remain auditable after the model parameters change.
- The difference between a high-probability sentence and a defended one.

Transformers are not lacking these distinctions because the engineers haven't gotten around to it. They are lacking them because the architecture has no surface on which to put them. The transformer's output is one type: a probability distribution over tokens. Everything we want to say about whether that output should affect reality has to be bolted on after the fact — through prompts, classifiers, gates, fine-tuning, post-hoc explanations.

This works. This is also why it does not scale to the parts of cognition that have to be answered for.

---

## 3. Why Prediction Is Not Intelligence

Three confusions sit inside the equation *prediction = cognition*. We name each, then say what is missing.

### 3.1 Prediction confuses *what would come next* with *what should come next*

A continuation engine is a **descriptive** function: given the world's text, what comes next? But cognition is also **prescriptive**: given the world, what should the next move be? The two coincide often. They are not the same. A transformer trained on a corpus of confidently-stated wrong answers will confidently state wrong answers. The prediction is correct (it matches the corpus). The cognition is broken (it propagates the wrong answer).

Intelligence requires being able to say: *this is the most likely next sentence under my training, and I am rejecting it, because the world does not support it.* That is a refusal grounded in evidence. A transformer can be made to *generate* such a refusal — it is just another continuation. It cannot, by construction, *be* such a refusal.

### 3.2 Attention confuses *relevance* with *judgment*

Self-attention identifies which tokens in context bear most heavily on each output token. The interpretive temptation is to call this judgment. It is not. Attention scores tell you which past tokens the model is *using*; they do not tell you which past tokens *should* be used. A model that attends heavily to a hallucination from earlier in its own output is not exercising judgment; it is reinforcing its own confabulation.

Judgment requires more than attention; it requires a **boundary** that says *this evidence is admissible; that evidence is not.* The boundary cannot be learned in the same channel as the inference, because the inference will route around it.

### 3.3 Generation confuses *output* with *consequence*

In a transformer pipeline, "the model said X" and "the model did X" are the same operation in different framings. There is no architectural difference between a token that becomes a comment in a chat window and a token that becomes a function call to a deployment system. The generation is identical; only the *consumer* differs. This is the failure mode that makes agentic frameworks fragile: the model never had a separate concept of *acting*, only of *generating*, and so the generation slips into action whenever a consumer is wired to interpret it as such.

### 3.4 What is missing

The missing piece is **negative space**: the architectural ability to *not* generate, to *defer*, to *flag*, to *conflict-preserve*, to *refuse on principled grounds*. A system that always generates fluently has no negative space. A system that has no negative space cannot, in any nontrivial sense, judge. It can only continue.

Intelligence — the kind a civilization can build on — is not the maximum probability continuation. It is the legitimate continuation, where legitimacy is itself a structured, declarable, refusable property of the move.

---

## 4. The Intellagent Thesis

We propose:

> **Cognition is a sequence of governed transitions between epistemic states.**

In full:

- **Cognition** is not a generator. It is a state machine.
- **The state** is not an attention buffer. It is an **epistemic state**: a structured record of what is currently held to be verified, supported, contested, or interpreted.
- **A step** is not a sampled token. It is an **epistemic transition**: a typed move from one epistemic state to the next, classified by the regime under which it can be evaluated.
- **Legitimacy** is not measured by likelihood. It is measured against a **governance kernel** that defines, per regime, what makes a transition admissible.
- **Reasoning** is not autoregressive sampling. It is **legitimate transition search**: finding a path through the space of epistemic states that satisfies the query and respects the kernel.
- **Action** is not generation. It is a **separately-authorized** transition into a state where the world is permitted to change.

This reframe is not a bolt-on. It is a different object. Where the transformer's primitive is a token, Intellagent's primitive is a *typed, governed, audited* state change. Where the transformer's loss is cross-entropy against the next token, Intellagent's correctness criterion is *did the path through the state graph respect the kernel at every step*. Truth is not a property of the generated text; it is a property of the path, regime by regime.

Importantly, **the transformer is not discarded**. A transformer is excellent at proposing candidate transitions — at saying "given this state, here is a plausible next move." Intellagent uses such proposals freely. What it does not do is *commit* a proposal without checking it against the governance kernel. The transformer becomes a *generator of candidates*; Intellagent is the *verifier-state-machine* that decides which candidates become the actual cognitive trajectory.

The thesis is therefore narrow:

> **Where transformers model probabilistic continuation, Intellagent models governed consequence formation. Both are real architectures. Only the second admits the existence of judgment.**

---

## 5. Formal Primitives

Intellagent is defined over nine primitives. Each is given a precise enough definition that an engineer can implement it, and a loose enough definition that the next paper can refine it.

### 5.1 Epistemic Object

An **epistemic object** $o$ is a structured assertion together with the metadata required to evaluate it.

$$
o = (\text{class}, \text{claim}, \text{evidence}, \text{provenance}, \text{lineage}, \text{status})
$$

- **class** ∈ {A, B, C, D} — the WiseOrder regime under which the object is evaluable (deterministic / empirical / consensus / interpretive).
- **claim** — the proposition being asserted, in a structured form.
- **evidence** — the records, observations, attestations, or commit-chain stages supporting the claim, regime-appropriate.
- **provenance** — who/what produced the object, when, and against what prior state.
- **lineage** — the chain of prior epistemic objects from which this one was derived, along with the transitions that produced it.
- **status** — the regime-appropriate verdict (`VERIFIED`, `SUPPORTED`, `CONFLICTED`, `CONSENSUS_VALID`, `CONDUCT_VALID`, etc., per the WiseOrder status registry in [`STATUS-REGISTRY.md`](./STATUS-REGISTRY.md)).

An epistemic object is the smallest unit Intellagent reasons over. It is *not* a sentence; a sentence may correspond to many objects.

### 5.2 Epistemic State

An **epistemic state** $S$ is the multiset of epistemic objects currently held by the cognizing system, together with the audit-memory pointer establishing the state's history.

$$
S = (O, h)
$$

where $O$ is a set of epistemic objects with their statuses, and $h$ is the SHA-256 hash of the audit memory at the moment $S$ was sealed.

Two systems with the same $O$ but different $h$ are *not* in the same state — they have arrived at the same belief set through different histories, and the lineage matters.

### 5.3 Epistemic Transition

An **epistemic transition** $\tau$ is a typed move from $S$ to $S'$:

$$
\tau : S \xrightarrow{\text{regime, evidence, authorization}} S'
$$

with:

- **regime** ∈ {A, B, C, D} — the WiseOrder class governing this transition.
- **evidence** — the regime-appropriate justification for the transition.
- **authorization** — for transitions that change external state, the declared authorization source (per `AG3`).

A transition is not a token, not a sentence, not a generation. It is a structured proposal: *given the current state, move to this next state, under this regime, with this evidence.*

### 5.4 Transition Legitimacy

A transition $\tau$ is **legitimate** with respect to a governance kernel $K$ if and only if every invariant $K$ declares for $\tau$'s regime is satisfied. We write:

$$
\text{Legitimate}_K(\tau) \iff \bigwedge_{i \in K_{\text{regime}(\tau)}} i(\tau) = \top
$$

For Class A transitions, $i$ ranges over WiseOrder invariants A1–A3 and CS1–CS3. For Class B, B1–B3. For Class C, C1–C4. For Class D, D1–D5 plus CC1–CC4. For action-bearing transitions, AG1–AG3. The exact invariants are defined in [`SPEC.md`](./SPEC.md) and enforced by the conformance vectors under [`vectors/`](./vectors/).

Legitimacy is **mechanically checkable**, not merely declared. This is the point.

### 5.5 Consequence Boundary

A **consequence boundary** is the architectural division between transitions that change the **epistemic state only** and transitions that change **the world outside the cognizing system**. The two are governed differently.

- **Internal transitions** (state change): governed by classification, evidence, and audit.
- **External transitions** (action): additionally governed by authorization (`AG1`–`AG3`).

`VERIFIED`, `SUPPORTED`, `CONSENSUS_VALID`, and `CONDUCT_VALID` are properties of the *epistemic* path. None of them, on their own, cross the consequence boundary. Crossing requires a separate authorization transition with its own evidence and rationale.

This is not a minor architectural detail. It is what an Intellagent system has and a transformer-driven agent does not.

### 5.6 Governance Kernel

The **governance kernel** $K$ is the set of rules that define legitimacy. In this proposal, $K$ = WiseOrder Protocol v0.1.0 plus its registered conformance vectors:

$$
K = (\text{SPEC v0.1.0}, \text{vectors/} ,\ \text{schemas/},\ \text{rules in tools/})
$$

The kernel is finite, versioned, and class-scoped. It does not encode all of moral reasoning, all of empirical method, or all of formal proof. It encodes the smallest universally-required scaffolding under which those finer disciplines can compose: how to classify a claim, how to evaluate it under its class, how to govern action, how to audit conduct, and how to refuse.

The kernel is intentionally narrow. Future versions may register additional classes, schemes, or invariants. The current version locks the floor.

### 5.7 Audit Memory

**Audit memory** $\mathcal{M}$ is the append-only sealed record of every legitimate transition the system has performed.

$$
\mathcal{M} = [(\tau_0, S_0, S_1, h_0), (\tau_1, S_1, S_2, h_1), \ldots]
$$

Each entry pins:

- The transition that fired.
- The state before and after.
- The hash $h_i$ that links this entry to the previous (commit-chain semantics, `CC1`–`CC4`).

Audit memory is **not** model parameters. It cannot be retrained away. It cannot be silently rewritten. Forgetting is itself a transition, recorded as such, with the preimage of what was forgotten where forgetting is admissible (`CC1`).

This is the property that lets an Intellagent system be *answered for* across time.

### 5.8 Authorization Boundary

The **authorization boundary** is the surface at which proposed transitions become committed transitions, and at which committed internal transitions are cleared (or refused) for external action.

Two authorization checks are involved:

1. **Commit authorization**: which entities may extend $\mathcal{M}$ at all? (Often the cognizing system itself, but for shared audit memories, multiple entities may write under quorum rules — Class C territory.)
2. **Action authorization**: even given a committed `VERIFIED` / `CONSENSUS_VALID` / `CONDUCT_VALID` result, which entities may consume that result to take external action? (Strictly separately governed, per `AG1`.)

These two are distinct. Conflating them is the bug that produces "the agent did the thing because the model said so." Separating them is what Intellagent architecturally requires.

### 5.9 Wisestemic Layer

The **wisestemic layer** is the substrate on which epistemic objects are inscribed.

Where the governance kernel says *what makes a transition legitimate*, the wisestemic layer says *in what form transitions and objects are recorded such that they carry their own provenance*. It is the substrate-level grammar — the layer at which an epistemic object cannot exist without being witnessed, and the witness's hand cannot be erased without breaking the object.

In this proposal, the wisestemic layer is provided by the Wisest substrate (a separate companion project: a first-person witnessed-substrate language). Intellagent does not require Wisest specifically; it requires *some* substrate at which the witness is structurally inseparable from the witnessed. Without such a substrate, "audit memory" becomes editable text and the rest of the architecture collapses.

The composition is:

$$
\text{Wisestemic substrate} \prec \text{Governance kernel (WiseOrder)} \prec \text{Cognition layer (Intellagent)} \prec \text{Action systems}
$$

Each lower layer constrains what the upper can claim.

---

## 6. Epistemic State Transition Graphs

Cognition under Intellagent is a directed graph $G = (V, E)$:

- $V$ — the set of reachable epistemic states.
- $E$ — the set of legitimate transitions, each typed by regime and bound to its evidence and authorization.

A specific cognitive *trajectory* is a path

$$
S_0 \xrightarrow{\tau_0} S_1 \xrightarrow{\tau_1} S_2 \xrightarrow{\tau_2} \cdots \xrightarrow{\tau_{n-1}} S_n
$$

where every $\tau_i$ satisfies $\text{Legitimate}_K(\tau_i)$.

Several properties follow:

1. **Truth is path-bound.** A claim at $S_n$ can only be defended by walking back through $\tau_{n-1}, \tau_{n-2}, \ldots, \tau_0$. There is no "the model just knows it." Knowing is always knowing-via.
2. **Branching is first-class.** Where a transformer collapses possibilities through softmax, Intellagent records branches when the kernel admits more than one legitimate continuation. The choice is itself a Class D transition (interpretive governance) and must carry its conduct artifact.
3. **Refusal is a node.** A state where no legitimate transition extends the path toward the query is a terminal state with status *refused*. Refusal is not a stylistic property of generated text; it is a graph-theoretic property of the legitimate transition graph.
4. **Hallucination is a kernel violation.** A generated continuation that does not correspond to a legitimate transition is, by definition, not part of $G$. It can be *proposed* but cannot be *committed*. The architectural prevention of hallucination is not better training; it is the kernel's refusal to extend $\mathcal{M}$.
5. **Conflict is preserved.** When two legitimate transitions disagree (Class B `CONFLICTED`), both branches stay in $G$ and the resolution becomes a separate, declared Class C or Class D move.

Inference is path search through this graph. Search heuristics may be learned. The legitimacy check is not.

---

## 7. WiseOrder as the Governance Kernel

Intellagent does not invent its kernel. The kernel is **WiseOrder Protocol v0.1.0**, already specified, vector-bound, and tool-enforced in this repository.

The mapping is direct:

| Intellagent concept | WiseOrder construct | Where in spec |
| --- | --- | --- |
| Class A transition | Class A — Deterministic Verification | `SPEC.md` §3 Class A |
| Class B transition | Class B — Instrumented Empirical Verification | `SPEC.md` §3 Class B |
| Class C transition | Class C — Protocol-Bound Consensus | `SPEC.md` §3 Class C |
| Class D transition | Class D — Interpretive Governance | `SPEC.md` §3 Class D |
| Consequence boundary | Action Governance (AG1–AG3) | `SPEC.md` §7 |
| Audit memory commit chain | Commit-Chain Semantics (CC1–CC4) | `SPEC.md` §5 |
| Transition legitimacy check | Conformance vectors | `vectors/`, `schemas/` |
| Drift detection across cognitive history | Suite fingerprints (vectors_suite_sha256, manifests_suite_sha256) | `TOOLS.md` |

Three properties of WiseOrder are load-bearing for Intellagent:

1. **Class scoping.** Not every transition is verifiable in the same way. A factual claim about a file's bytes (Class A), an empirical claim about an execution (Class B), an attested approval (Class C), and a strategic recommendation (Class D) all live in the same architecture but answer to different invariants. Intellagent inherits this stratification wholesale.
2. **Proof separation.** Process proof and integrity proof are distinct (`SPEC.md` §6). A correctly-formed cognitive trajectory does not, on its own, mean the conclusion is true; it means the conduct was admissible. Conversely, a true-by-coincidence conclusion arrived at through illegitimate transitions is not admitted as known. Intellagent uses both proofs, separately.
3. **Action-governance separation.** AG1 is the cornerstone: *verification status MUST NOT automatically authorize execution*. This is exactly the property a transformer-driven agent does not have, and exactly the property that makes a cognitive system answerable for its actions.

A future kernel evolution (WiseOrder v0.2.0 or beyond) may register additional regimes — for example, a Class E for time-bounded provisional claims that automatically expire. Intellagent's architecture is unchanged by such additions; only the kernel grows.

---

## 8. Wisestemic Model

The wisestemic layer answers the question: *in what form does an epistemic object exist such that its provenance cannot be silently severed?*

A satisfying wisestemic layer has four properties:

1. **Witnessed inscription.** No object exists without a recorded witness — the entity that produced it. The witness is not metadata; it is structural.
2. **Lossy honesty.** The substrate admits that any inscription captures less than the moment it inscribes. Errors are surfaced as *the substrate could not return this clearly*, not as malformations.
3. **Hand inseparability.** The witness's identifying mark is computed in such a way that removing it breaks the inscription. There is no anonymous epistemic object.
4. **Append-only history.** Past inscriptions are immutable. Updates inscribe new objects; they do not silently overwrite old ones.

These properties are not Intellagent's invention. They are the spine of the Wisest project, which exists as a separate companion. Intellagent **depends on a wisestemic substrate** but does not legislate which one.

What Intellagent requires the wisestemic layer to deliver is a guarantee:

> **Every epistemic object passing through Intellagent carries its hand. Every transition's record carries the hand of the proposer, the hand of the kernel, and (where applicable) the hand of the authorizer.**

Without this guarantee, "audit memory" is editable; with it, audit memory is structurally append-only at the substrate level, and the rest of the architecture's promises become defensible.

The composition we propose is:

```
Wisestemic substrate    →   guarantees: no anonymous claim exists
        ↓
Governance kernel       →   guarantees: only legitimate transitions extend memory
        ↓
Cognition layer         →   guarantees: search for legitimate paths is the inference primitive
        ↓
Action systems          →   constrained: only authorized paths can change the world
```

This is a stack, not a pipeline. Each layer's guarantee depends on the layer below.

---

## 9. Memory as Governed State

A transformer's "memory" is two things: parameters (frozen knowledge after training) and the KV cache (running attention over the current context). Both are **opaque** to the system using them. Neither is auditable in the sense that a court, a regulator, a peer reviewer, or a self-reflection routine could inspect.

Intellagent's memory is two things: **working epistemic state** $S$ and **audit memory** $\mathcal{M}$.

- **Working state $S$** is the set of currently-held epistemic objects with their statuses. It is structured, inspectable, and present-tense. It is the "what I currently believe" of the system.
- **Audit memory $\mathcal{M}$** is the append-only, commit-chain-sealed record of every legitimate transition that produced the current state. It is structured, inspectable, and historical. It is the "how I came to believe it" of the system.

Several consequences:

1. **Forgetting is a transition.** Removing an object from $S$ is not a side-effect; it is a typed move that goes into $\mathcal{M}$ with its own evidence and (if the regime requires it) authorization.
2. **Drift is detectable.** A cognitive system whose working state has shifted has a transition in $\mathcal{M}$ explaining the shift. If no such transition exists, the system has been tampered with at the substrate level.
3. **Calibration is auditable.** Class D conduct artifacts include calibration windows. After-the-fact comparison of predicted vs. observed outcomes is mechanical, not interpretive.
4. **Models are not memory.** Parameters of a learned proposer (a transformer, a search policy, a planner) are *part of the proposer*, not part of memory. Replacing the proposer does not erase $\mathcal{M}$.

This is what makes Intellagent a candidate architecture for **systems that have to remain themselves across model updates**. A transformer-based agent loses continuity when its underlying model is retrained; an Intellagent system carries $\mathcal{M}$ through retraining as a separate, governed artifact.

---

## 10. Authorization-Bounded Cognition

The cleanest single statement of Intellagent's architectural claim is:

> **No cognition is automatically authorization.**

In WiseOrder terms (`AG1`):

> *A conformant implementation MUST NOT treat `VERIFIED`, `CONSENSUS_VALID`, `CONDUCT_VALID`, valid hashes, valid signatures, or valid attestations as automatic execution authorization.*

In Intellagent terms: a path $S_0 \to \cdots \to S_n$ that legitimately concludes "the right action is X" is not, by itself, permission to perform X. Performing X requires an additional transition into a state where authorization is recorded, sourced, and accountable.

This sounds like a restriction. It is in fact the architectural feature that allows cognition to be *trusted with authority*. Three reasons:

1. **Authorization can be revoked.** If the cognitive layer's verdict is provisional, its consequences can be governed independently. Withdrawing authorization does not require unlearning a model; it requires a Class C transition in $\mathcal{M}$.
2. **Authorization can be split.** Different consequences (read access, write access, broadcast, money movement) can be authorized by different parties under different regimes, each producing their own commitable transition. The cognitive layer doesn't know the difference; it just produces the verdict.
3. **Authorization can be audited.** Every action carries its authorization source as auditable metadata (`AG3`). "Why did the system do that?" becomes a path query through $\mathcal{M}$, terminating at a named, declared authorization.

The corresponding failure modes the architecture explicitly prevents:

- **Auto-authorization on consensus.** A `CONSENSUS_VALID` verdict that the action_policy lifts to `action_allowed: true` *without* a separately declared authorization source is rejected as `INVALID` by the kernel. (See `vectors/class-c-auto-authorize-rejected.json`.)
- **Authorization without source.** An `action_allowed: true` artifact lacking `authorization_source` is `INVALID`. (See `vectors/class-c-authorization-source-required.json`.)
- **Conduct masquerading as truth.** A Class D conduct artifact attempting `VERIFIED` status is `CONDUCT_INVALID`. (See `vectors/class-d-verified-status-rejected.json`.)

These vectors are not merely tests. They are the operational expression of the architecture's guarantees.

---

## 11. Inference as Legitimate Transition Search

The inference loop in a transformer is autoregressive sampling: at each step, sample the next token from the conditional distribution given the prefix.

The inference loop in Intellagent is **legitimate transition search**:

```
state := S₀                                  # current epistemic state
goal  := φ(query)                            # predicate over states satisfying the query
M     := []                                  # audit memory

while not φ(state):
    candidates := propose(state, query)      # proposer (transformer, search, solver, human)
    for τ in candidates ranked by heuristic:
        if Legitimate_K(state ⟶ τ ⟶ state'):
            commit(τ); M.append(τ); state := state'
            break
        else:
            record_challenge(τ, reason)      # D3 challenge surface
    else:
        return refuse(state, reasons_collected)

return state, M
```

Several observations:

1. **The proposer is replaceable.** A transformer is one excellent proposer. So is beam search over a planner, a SAT solver, a retrieval system, a human in the loop, or an ensemble. The kernel does not care; it checks legitimacy.
2. **Legitimacy checks are local.** Each transition is checked against the regime's invariants and the current state. No global re-evaluation is needed.
3. **Refusal is structural.** When no candidate transition is legitimate, the loop returns a refusal — *with the recorded challenge surface explaining why every candidate failed*. This is what `class-d-no-counterarguments` exists to prevent the negative case of: refusal with no recorded reasons is not refusal, it is silence.
4. **Search budget is observable.** Every committed transition has a record. The cost of a cognitive trajectory is measurable, reportable, and auditable across runs.
5. **Hallucination is a category error.** A "hallucinated" output is a candidate that the proposer emitted and the kernel rejected. It cannot enter $\mathcal{M}$. The architectural question is no longer "how do we reduce hallucination rate?" but "what was the rejection rate, and what does the challenge surface say?"

The interesting research surface this opens is the **proposer/verifier interface**. Proposers want to make many candidates fast; verifiers want to be cheap per check. Designing this interface — what context the proposer sees, how the verifier provides feedback that improves the proposer's distribution — is the practical engineering problem. It is also exactly the kind of problem where transformers, fine-tuned to propose under kernel feedback, could be enormously useful.

---

## 12. Runtime Architecture

A minimal Intellagent runtime has four components:

```
┌────────────────────────────────────────────────────────────┐
│                       Action Systems                       │
│            (deployed services, files, external APIs)       │
└────────────────────────────────────────────────────────────┘
                            ▲
                            │  (only via authorized transitions)
                            │
┌────────────────────────────────────────────────────────────┐
│                     Authorization Layer                    │
│       (action_policy, authorization_source, audit_log)     │
└────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌────────────────────────────────────────────────────────────┐
│                       Cognition Layer                      │
│  (state S, transition search, proposer ↔ verifier loop)    │
└────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌────────────────────────────────────────────────────────────┐
│                Governance Kernel  (WiseOrder)              │
│          (regimes A/B/C/D, vectors, schemas, AGn)          │
└────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌────────────────────────────────────────────────────────────┐
│                    Wisestemic Substrate                    │
│         (witnessed inscription, append-only history)       │
└────────────────────────────────────────────────────────────┘
```

### 12.1 Wisestemic substrate

Provides the storage primitives: append-only inscription, witness-bound objects, hand-inseparability, and lossy honesty. In a prototype this can be a flat directory of signed JSON files; in a hardened deployment it is a versioned, content-addressed store with witness signatures.

### 12.2 Governance kernel

Loads the WiseOrder schemas, vectors, and conformance tools from this repository. The kernel exposes a single API surface: `legitimate?(transition, prior_state) → (yes | no, evidence_or_failures)`.

### 12.3 Cognition layer

Holds the working state $S$. Receives queries. Coordinates the proposer/verifier loop. Commits legitimate transitions to audit memory. Returns the resulting state plus the path that produced it.

### 12.4 Authorization layer

Sits between the cognition layer and any external action system. Inspects each proposed external transition. Resolves the declared `authorization_source`, applies the policy, records the decision (allow / deny / defer) into audit memory, and — on allow — invokes the external action.

The boundary between (3) and (4) is the consequence boundary. It is the architectural feature that lets you give a cognitive system real responsibility without giving it unconditional reach.

### 12.5 What is not in the runtime

- No distributed consensus protocol for the audit memory itself (that's a future engineering layer).
- No specific learned proposer (transformer, planner, retrieval system — pluggable).
- No specific UI (the runtime is library-shaped).
- No language-model-specific assumptions (a search-based proposer would work equally well).

---

## 13. Comparison to Transformers

| Property | Transformer | Intellagent |
| --- | --- | --- |
| **Cognitive primitive** | Probability over next token | Typed governed transition |
| **Output type** | Distribution over tokens | Path through epistemic state graph |
| **Truth criterion** | Likelihood under training distribution | Path-legitimacy under governance kernel |
| **Refusal** | Stylistic or RLHF-shaped | Graph-theoretic terminal state |
| **Hallucination** | Inevitable failure mode | Architectural category error (rejected candidate) |
| **Action vs. generation** | Same operation, different consumer | Architecturally separate, separately authorized |
| **Memory** | Parameters + KV cache (opaque) | Audit memory + working state (structured, inspectable) |
| **Drift across model updates** | Continuity lost | Continuity preserved in audit memory |
| **Inference loop** | Autoregressive sampling | Legitimate transition search |
| **Failure mode** | Confident wrong continuation | Recorded refusal with challenge surface |
| **Auditability** | Post-hoc interpretability research | Built-in by construction |
| **Composability with formal methods** | Loose; bolted on | Native; kernel is the interface |
| **Composability with transformers** | n/a (it *is* the transformer) | Native; transformers serve as proposers |

The framing is not transformers-versus-Intellagent. The framing is: *transformers are excellent components inside Intellagent; they are insufficient as the architecture of intelligence.*

---

## 14. Prototype Path

We describe a minimum prototype that exercises the architecture end-to-end without requiring novel algorithms. The point is not performance; the point is to demonstrate that the surface is implementable.

### Stage 1 — Kernel-only verifier (already exists in this repo)

- WiseOrder Protocol v0.1.0 in [`SPEC.md`](./SPEC.md).
- 23 conformance vectors in [`vectors/`](./vectors/).
- Validators and reports in [`tools/`](./tools/) and [`reports/`](./reports/).
- Interop fixtures and manifests in [`interop/`](./interop/).

This is the kernel. Nothing in Intellagent's runtime invents new protocol semantics; everything reuses this.

### Stage 2 — Working state and audit memory

- A small Python package: `intellagent/`
  - `state.py` — epistemic state representation, JSON-serializable.
  - `memory.py` — append-only audit memory backed by a directory of sealed records.
  - `transitions.py` — typed transition objects (one per WiseOrder class).

No proposer. No transformer. The runtime can be exercised by hand-written transitions and the kernel verifies them. This is enough to prove that the state machine works.

### Stage 3 — Static proposer

- A retrieval-based proposer: given a state and a query, look up a prior similar state in audit memory and propose its successor as a candidate.
- The kernel verifies. The challenge surface gathers reasons for rejection.
- Useful, deterministic, auditable. Not yet "intelligent" in any interesting sense.

### Stage 4 — Learned proposer

- Wrap a transformer (any pre-trained model) as a proposer.
- Prompt format: serialize the current state, the query, and the recent audit memory into a prompt; ask for a typed transition.
- Parse the output; submit to kernel; iterate.
- Train against rejection feedback if compute permits.

This is the interesting research stage. It does not claim that the resulting system is intelligent; it claims that the system has structurally separated *what the model proposes* from *what the system commits to*.

### Stage 5 — Authorization layer + first real action

- Pick a single low-stakes external action (e.g., write a file in a sandbox).
- Add the authorization layer: the action requires a Class C transition with declared authorization source.
- Demonstrate that the cognitive layer's verdict by itself does not perform the action; only an authorized transition does.

### Stage 6 — Distributed audit memory

- Multi-party append. Class C consensus rules govern who can extend $\mathcal{M}$.
- Out of scope for v0.1.0 of this proposal.

The architecture's correctness is testable at each stage. Stage 1 already passes its own conformance suite (38/38 tests, 23 vectors, 2 implementations, 3 interop fixtures all green). Subsequent stages add components without modifying the kernel.

---

## 15. Non-Goals

This proposal explicitly does **not** claim:

1. **That transformers are useless.** They are excellent proposers, and excellent proposers are essential to a usable Intellagent runtime.
2. **That truth is solved.** Class D exists precisely because some claims cannot be mechanically verified, and the architecture governs *conduct* rather than asserting *truth* on those claims.
3. **That implementation is complete.** Stages 2–6 above are open work. This document specifies the architecture, not the implementation.
4. **That this is AGI.** It is not. It is a proposed substrate on which more capable cognitive systems could be built without losing the ability to be answered for.
5. **That the kernel encodes morality, ethics, or politics.** It does not. The kernel encodes *the form of justification that a claim's class requires*. The substantive content of any specific judgment lives in the conduct artifacts and is governed there.
6. **That this replaces empirical AI research.** The proposer/verifier interface, the calibration of conduct artifacts, the efficiency of legitimacy checks — all are open empirical questions.
7. **That Intellagent is a model of human cognition.** Humans do not inscribe their thoughts into commit-chains. The architecture is not biology; it is a *successor protocol* for machine cognition that has to be answered for at scale.
8. **That every decision a deployed system makes must traverse the full kernel.** Many low-stakes decisions in real systems are deliberately ungoverned, and that is fine. The claim is that *the decisions that have to be answered for* are the ones the architecture is designed for.

We will know we were wrong if any of the following turns out to be true:

- The kernel's class structure is fundamentally insufficient to classify some load-bearing class of cognition.
- The legitimacy check is so expensive that it makes inference intractable even at modest scale.
- A proposer/verifier interface cannot be made to converge under feedback (proposers stay miscalibrated indefinitely).
- The wisestemic substrate's witness-inseparability cannot be made cryptographically practical.
- The architecture admits the same failure modes as transformers in some non-obvious way (some class of bypass we did not foresee).

These would falsify the thesis. We invite the falsifications.

---

## 16. Conclusion

The current architecture of frontier AI is a continuation engine with policy decoration. It is astonishing at what it does. It is being asked to do work it was not designed for: to be *answered for*. The mismatch between what transformers are and what we are using them as is the source of the most uncomfortable failure modes of the current era — confident hallucination, agentic action without authorization, preference drift across model updates, and the structural inability to refuse on principled grounds.

The Intellagent thesis is that the next architecture for intelligence should not be more attention. It should be *governance*. Cognition modeled as governed transitions between epistemic states. Reasoning modeled as legitimate path search. Truth modeled as a property of paths, not of outputs. Action modeled as separately authorized. Memory modeled as append-only audit, not as opaque parameters.

The kernel for such governance already exists, in narrow but solid form: WiseOrder Protocol v0.1.0, in this repository. It is not the whole architecture. It is the floor. The architecture above it — the cognition layer, the authorization layer, the proposer/verifier interface — is what this paper proposes and what the next stages of work would build.

The framing is direct.

Transformers model probabilistic continuation. They will continue to be useful, possibly indispensable, as proposers within larger systems. **Intellagent models governed consequence formation.** That is a different problem. It admits judgment, refusal, deferral, conflict, and authorization as first-class architectural primitives, because it builds the substrate that requires them.

Both architectures are real. Only the second admits the existence of judgment.

This is a proposal. It is unfinished. It is bold and we know it is bold. It is also small enough to implement and falsify within a year of focused work, on top of a kernel that is already on disk in this repository, already tested by 38 self-tests and 23 conformance vectors, and already running green.

The next step is the prototype.

---

*Architecture proposal, draft. WiseOrder Protocol v0.1.0 governs the kernel. Intellagent governs nothing yet — it is, for now, an architecture diagram and a thesis. The work begins where the diagram ends.*
