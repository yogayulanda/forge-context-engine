# Forge Context Engine

Forge is an AI-native engineering workflow system focused on bounded engineering cognition for real-world software development.

It helps engineers and AI assistants work with repository context in a disciplined way: scoped evidence, clear lifecycle modes, explicit uncertainty, and reviewable engineering outputs. Forge is for teams that want AI-assisted planning, implementation guidance, execution reporting, testing, review, incident diagnosis, and refactoring with visible human control.

Forge v1 is the lifecycle foundation: a context structure, mode protocol, validation rules, and lightweight handoff artifacts. It is ready for real-world pilot usage and evidence-based refinement.

## Quick Mental Model

Forge is a repository-native way to work with AI assistants without giving up engineering control.

Think of Forge as:

```text
repository evidence -> scoped context -> one lifecycle mode -> reviewable engineering output
```

A human asks for one kind of work, Forge loads the matching context, and the output stays tied to code, docs, ADRs, explicit confirmations, and visible unknowns.

The practical rule is simple:

- Use `ask` to understand.
- Use `planning` to shape a change.
- Use `implementation` to turn approved intent into executable task cards.
- Use `execute` to modify the repository within those approved boundaries.
- Use `testing` to validate.
- Use `review` to decide MR readiness.
- Use `incident` when something is broken.
- Use `refactor` for bounded behavior-preserving cleanup.

## How Forge Works Operationally

Forge has three lightweight parts:

| Part | Role | Boundary |
|---|---|---|
| `.forge/context` | Repo-local conventions, mode files, scoped knowledge, and generated handoff artifacts. | Code, docs, ADRs, and human decisions still win. |
| Lifecycle modes | Separate understanding, planning, implementation breakdown, execution, testing, review, incident diagnosis, and refactoring. | Each mode owns one kind of work. |
| Skills and adapters | Let Claude, Codex, GitHub Copilot, Cursor, and other tools invoke the same Forge behavior. | Tool files stay thin invocation surfaces. |

In normal use, the assistant reads the Forge config, reads the requested mode, loads only task-relevant context, checks current repository evidence, and returns a concise engineering output for that mode.

## 5-Minute Quick Start

1. Start from the `runtime/` template when adding Forge to a repository.
2. Ask a scoped question with `ask`, such as "How does this service handle retries?"
3. For a change, use `planning` before code when scope, risk, validation, or rollback matters.
4. Use `implementation` to produce task cards before `execute` changes files.
5. Review the result: changed files, validation, rollback notes, unknowns, and next action.

## Typical Engineering Workflow

Most feature and bug work follows this shape:

```text
Bug or feature request
-> ask: understand current behavior and evidence
-> planning: propose the engineering change plan
-> implementation: produce task cards and stop conditions
-> execute: apply the approved repository changes
-> testing: run or define validation
-> review: assess MR readiness
-> merge: handled by the team outside Forge
```

Small changes may skip `planning` when the scope is obvious. `incident` and `refactor` are entry modes for diagnosis and bounded cleanup.

Forge helps each step produce the next useful engineering artifact. It does not automatically advance from one step to another, approve risky choices, open PRs, deploy code, or merge changes.

## Forge Working States

Forge outputs should make the current state obvious:

```text
Understanding -> Planning -> Ready -> Executing -> Validating -> Reviewing -> Completed
```

| State | What it means | Common next move |
|---|---|---|
| Understanding | The team is trying to learn current behavior or missing evidence. | Use `ask`, or move to `planning` when the change is clear. |
| Planning | The change needs scope, impact, risk, validation, or rollback thinking. | Confirm the plan or resolve unknowns. |
| Ready | Implementation has concrete task cards, dependencies, guardrails, and execution values. | Use `execute` for the approved task set. |
| Executing | Repository changes are being applied inside approved boundaries. | Validate, report changed files, and surface blockers. |
| Validating | Tests, manual checks, or environment-dependent checks are being run or specified. | Use `testing`, then fix failures or continue to review. |
| Reviewing | The team is checking correctness, risk, validation honesty, and MR readiness. | Address findings or merge outside Forge. |
| Completed | The scoped work is implemented, validated enough for its risk, and review-ready or accepted. | Keep artifacts only if they help future handoff. |

These are human working states, not a hidden state machine. Generated artifacts may record handoffs, but they do not trigger execution or become source of truth.

## Core Philosophy

- **Repository first:** code, repository docs, ADRs, and explicit human confirmations remain the source of truth.
- **Bounded cognition:** Forge loads only the context needed for the task and keeps claims tied to evidence.
- **Operational workflows:** modes produce practical engineering outputs, not abstract reasoning dumps.
- **Human-review-aware:** implementation and execution boundaries are designed for review, validation, rollback, and MR readiness.
- **No autonomous engineering claims:** Forge can guide, structure, and report work; it does not silently approve high-risk decisions or run an engineering organization by itself.

## What Forge Is Not

Forge is not an autonomous agent framework, orchestration engine, workflow DAG system, CI/CD runner, deploy platform, or persistent AI memory system.

It provides lifecycle discipline for AI-assisted engineering work; it does not run the engineering organization or hide automation behind repository context.

## When To Use Each Lifecycle Mode

| Mode | Purpose | Expected Output | Boundaries | Use When |
|---|---|---|---|---|
| `ask` | Answer scoped repository or context questions. | Concise evidence-based explanation, unknowns, missing evidence. | No planning, mutation, redesign, or broad audit. | You need to understand current behavior or context. |
| `planning` | Produce an Engineering Change Plan. | ECP-style plan with impact, phases, risks, validation, rollback, blockers. | No code changes or detailed executable task cards. | A change needs design, sequencing, or risk analysis. |
| `implementation` | Convert approved intent into executable tasks. | Readiness status, concrete values, task cards, dependencies, stop conditions. | Does not modify code or redesign the plan. | A human-reviewable execution boundary is needed before coding. |
| `execute` | Apply approved repository changes. | Execution result, changed files, validation, rollback, reviewer focus. | Does not redefine architecture or absorb full testing/review responsibilities. | Approved tasks are ready to implement. |
| `testing` | Own structured validation and test-focused work. | Testing result, validated scope, automated/manual checks, blockers, gaps. | Does not become review mode or generic architecture planning. | You need test strategy, test changes, or validation reporting. |
| `review` | Evaluate correctness, risk, and MR readiness. | Review result, MR readiness, severity-grouped findings, safety notes. | Does not replace testing or become an implementation task list. | You need senior MR-style review. |
| `incident` | Diagnose bugs, issues, or incidents from evidence. | Symptoms, impact, likely/possible cause, mitigation, rollback, next checks. | No speculative redesign or unsupported root-cause claims. | Something is broken or unclear in operation. |
| `refactor` | Improve technical debt conservatively. | Bounded refactor result/proposal, risk classification, validation expectations. | No architecture rewrite, paradigm migration, or hidden behavior change. | You need behavior-preserving cleanup or simplification. |

The recommended full workflow is:

```text
ask -> planning -> implementation -> execute -> testing -> review
```

Use the smallest mode that fits the current decision. Do not use `execute` when scope, approval, or execution values are still unclear; use `implementation` or `planning` first.

## Day-To-Day Usage Examples

| Situation | Good Forge request | Why this mode fits |
|---|---|---|
| A backend engineer needs to understand retries. | "Use Forge ask mode to explain how this service retries failed events." | `ask` stays evidence-based and does not turn the answer into a change plan. |
| A frontend engineer wants to change a shared state flow. | "Use Forge planning mode for this UI state change." | `planning` surfaces affected files, risks, validation, and unknowns before code changes. |
| A technical lead approved a plan. | "Use Forge implementation mode to create task cards for the approved plan." | `implementation` checks readiness and stops on missing execution values. |
| An AI-assisted coding session is ready to modify files. | "Use Forge execute mode for these approved task cards." | `execute` applies bounded changes and reports validation honestly. |
| A contributor opened an MR. | "Use Forge review mode on this branch." | `review` focuses on correctness, risk, validation gaps, and MR readiness. |
| Production behavior is unclear or broken. | "Use Forge incident mode for this symptom." | `incident` separates symptoms, evidence, likely causes, mitigation, and unknowns. |
| A module needs cleanup without behavior changes. | "Use Forge refactor mode for this package." | `refactor` keeps cleanup bounded and behavior-preserving. |

## How Teams Use Forge

Teams usually adopt Forge as a shared engineering habit:

- Backend engineers use it to keep service, data, retry, idempotency, rollback, and contract changes explicit.
- Frontend engineers use it to scope UI behavior, state flow, accessibility, API assumptions, and regression validation.
- Technical leads use it to preserve reviewable plans, task boundaries, and approval points across AI-assisted work.
- OSS contributors use it to understand what kind of answer or change is expected before touching code.
- AI-assisted engineering users use it to keep assistants inside evidence and visible lifecycle boundaries.

The value is consistency: the same request shape works across different tools, while the repository remains the source of truth.

## Runtime Profiles

Forge uses one controlling interaction flag:

| Setting | Behavior |
|---|---|
| `runtime.non_interactive: false` | Local, interactive work. Forge may ask concise clarification questions for blocking decisions. |
| `runtime.non_interactive: true` | Automation-safe behavior. Forge does not ask conversational questions; it emits structured statuses and required decisions. |

`runtime.profile` is metadata:

| Profile | Meaning |
|---|---|
| `local` | Normal human-in-the-loop profile. |
| `automation` | Automation-safe usage. |
| `ci` | Reserved metadata only; it does not add CI/CD or executor behavior. |

High-risk decisions require human approval. In automation-safe flows, Forge uses `NEEDS_HUMAN_APPROVAL` for security/compliance, PII/secrets, financial correctness, destructive migration, production topology, contract authority, or rollback-risky decisions.

In interactive local work, Forge should ask the smallest useful clarification question when a blocking decision is missing. In non-interactive work, Forge should stop with the appropriate status instead of inventing an answer.

## Human Approval And Bounded Execution

Forge separates "the assistant can explain or prepare this" from "the assistant may change the repository."

Execution should be bounded by:

- approved scope or task cards
- concrete execution values
- explicit do-not-change boundaries
- known dependencies and stop conditions
- validation expectations
- rollback or manual follow-up notes when risk requires them

`implementation` mode prepares that boundary. `execute` mode applies changes only inside it. If contract authority, security, financial correctness, destructive migration approval, production topology, or rollback-risky behavior is unresolved, Forge should stop or ask for human approval instead of continuing.

## Artifact Lifecycle

Lifecycle artifacts are small engineering handoff records stored under:

```text
.forge/context/generated/artifacts/
```

| Artifact | Captures |
|---|---|
| ECP | Approved planning intent, decisions, blockers, and boundaries. |
| Execution Contract | Implementation-ready task cards and stop conditions. |
| Execute Result | Changed scope, validation status, rollback notes, and unchanged boundaries. |
| Testing Result | Validation evidence, blockers, coverage gaps, and runtime-sensitive checks. |
| Review Result | MR readiness, findings, reviewer focus, and safety notes. |
| Incident | Diagnosis, mitigation, rollback possibility, and next checks. |
| Refactor | Problem areas, safe improvements, risks, and out-of-scope redesigns. |

Artifacts are bounded engineering records. They help with handoff, but they are not source of truth, workflow state, execution triggers, or persistent AI memory. If an artifact conflicts with current repository evidence, repository evidence wins.

## Shared Skills, Adapters, And Commands

Forge shared skills are reusable invocation layers for Forge workflows. Adapters are thin tool-specific bridges. Together, they reduce invocation friction across Claude, Codex, GitHub Copilot, Cursor, and future AI tools while keeping repository intelligence in local `.forge/context`.

Final architecture:

```text
tool syntax -> tool UX layer -> adapter -> shared skill -> .forge/context mode -> scoped repository evidence
```

| Surface | Purpose |
|---|---|
| `.forge/context` | Cognition source of truth. |
| `runtime/skills/*/SKILL.md` | Reusable Forge workflow behavior. |
| `runtime/adapters/*` | Tool-specific bridges and loading notes. |
| `CLAUDE.md` | Claude-compatible entrypoint. |
| `AGENTS.md` | Codex-compatible entrypoint. |
| `runtime/adapters/copilot/` | GitHub Copilot instructions and prompt wrappers. |
| `runtime/adapters/shared/` | Portable command conventions. |

Skills use a small operational structure: `Purpose`, `Load`, `Invocation`, `Focus`, `Output`, and `Do NOT`.

Shared skills are available for ask, planning, implementation, execute, testing, review, incident, and refactor:

- `forge-ask`
- `forge-plan`
- `forge-implement`
- `forge-execute`
- `forge-test`
- `forge-review`
- `forge-incident`
- `forge-refactor`

Invocation syntax may differ by tool:

- Claude can use `/forge-review` or `/forge-plan`.
- Codex can use `$forge-review`, `/skill forge-review`, or natural prompts such as "Use Forge review skill", depending on Codex surface/version.
- GitHub Copilot can use prompt files such as `/forge-review`, `/forge-plan`, or `/forge-ask` under `.github/prompts/`.

In each case, behavior should resolve to the same shared skill. Claude command adapters live under `runtime/adapters/claude/commands/`; Copilot prompt wrappers live under `runtime/adapters/copilot/prompts/`; Codex remains skills-first through `AGENTS.md`.

The same skill behaves differently in a fintech service, frontend app, or infrastructure module because local `.forge/context` and repository evidence differ.

## Governance And Safety

Forge treats governance as practical engineering risk, not compliance theater.

Relevant modes surface concise risks around:

- financial correctness
- transaction consistency
- idempotency
- retry and replay safety
- rollback readiness
- secrets and PII safety
- operational validation honesty
- observability and blast radius

Payment, balance, ledger, settlement, reconciliation, and transaction correctness are never treated as low risk. Raw secrets and raw PII must not be logged, persisted, quoted, or copied into context or artifacts.

## Context And Token Philosophy

Forge is designed for scoped loading:

- Load the context needed for the current task.
- Prefer direct repository evidence over broad context scans.
- Treat `token_budget` as an operating range, not a blind cap.
- Use `CONTEXT_BUDGET_LIMITED` when safe work requires evidence beyond the normal scoped budget.
- Avoid loading all of `.forge/context` by default.

This keeps context useful, reviewable, and resistant to stale or speculative claims.

## Current Status

Forge v1 status:

- lifecycle foundation complete
- mode boundaries stabilized
- runtime profile and non-interactive semantics bounded
- artifact lifecycle defined
- validation rules consolidated
- ready for real-world pilot usage
- entering evidence-based refinement phase

Forge v1 is not claiming complete automation, benchmarked behavior across all repositories, or production runtime tooling.

## Repository Structure

| Path | Purpose |
|---|---|
| `runtime/` | Runtime template copied into target repositories during initialization. |
| `runtime/skills/` | Shared Forge skill entrypoints for Claude, Codex, GitHub Copilot, Cursor, and future tools. |
| `runtime/CLAUDE.md` | Thin Claude-compatible adapter pointing to `.forge/`. |
| `runtime/AGENTS.md` | Thin Codex-compatible adapter pointing to `.forge/`. |
| `runtime/adapters/` | Thin tool compatibility notes and shared command conventions. |
| `runtime/.forge/context/` | Canonical Forge context skeleton: meta, core, layers, systems, knowledge, modes, generated, and temp zones. |
| `runtime/.forge/context/generated/artifacts/` | Optional lifecycle handoff artifacts, created on demand. |
| `specs/` | Normative specifications for initialization, validation, mode invocation, artifact lifecycle, migration, framework lifecycle, and adapter/command foundation. |
| `validation-cases/` | Focused cases used to validate Forge cognition patterns. |
| `FORGE-CONTEXT-ARCHITECTURE.md` | Architecture foundation and design rationale. |

## Non-Goals

Forge intentionally does not provide:

- runtime executors
- autonomous agent loops
- workflow orchestration
- DAG execution
- CI/CD pipelines
- deploy or release automation
- persistent AI memory infrastructure
- RAG, vector search, or knowledge graph systems
- broad context loading as a default behavior
- adapter-owned repository cognition
- tool-specific orchestration or command chaining

## Contributing And Evolution

Forge should evolve from real engineering evidence.

Good refinements:

- reduce ambiguity seen in real usage
- improve mode output clarity
- tighten validation rules around observed failures
- preserve repository-first truth
- keep lifecycle responsibilities distinct
- improve safety without adding bureaucracy

Avoid changes that add theoretical architecture, broad automation semantics, hidden state, or new lifecycle concepts without repeated evidence from real projects.

The standard for Forge evolution is simple: make real engineering work clearer, safer, and easier to review while preserving bounded cognition.

## Security

Please report security concerns privately. Do not post production credentials, customer data, tokens, or sensitive incident details in public issues.

See [SECURITY.md](SECURITY.md).

## License

Forge Context Engine is licensed under the Apache License 2.0.

See [LICENSE](LICENSE).
