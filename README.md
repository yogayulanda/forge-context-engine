# Forge Context Engine

Forge is an AI-native engineering workflow system focused on bounded engineering cognition for real-world software development.

It helps engineers and AI assistants work with repository context in a disciplined way: scoped evidence, clear lifecycle modes, explicit uncertainty, and reviewable engineering outputs. Forge is for teams that want AI-assisted planning, implementation guidance, execution reporting, testing, review, incident diagnosis, and refactoring without turning their repository into an autonomous automation system.

Forge v1 is the lifecycle foundation: a context structure, mode protocol, validation rules, and lightweight handoff artifacts. It is ready for real-world pilot usage and evidence-based refinement.

## Core Philosophy

- **Repository first:** code, repository docs, ADRs, and explicit human confirmations remain the source of truth.
- **Bounded cognition:** Forge loads only the context needed for the task and keeps claims tied to evidence.
- **Operational workflows:** modes produce practical engineering outputs, not abstract reasoning dumps.
- **Human-review-aware:** implementation and execution boundaries are designed for review, validation, rollback, and MR readiness.
- **No autonomous engineering claims:** Forge can guide, structure, and report work; it does not silently approve high-risk decisions or run an engineering organization by itself.

## What Forge Is Not

Forge is not:

- an autonomous agent framework
- an orchestration engine
- a workflow DAG system
- a CI/CD runner
- a deploy automation platform
- a memory operating system
- a persistent AI brain

Forge intentionally avoids hidden automation semantics, runtime executors, agent loops, deploy workflows, and broad memory systems.

## Lifecycle Modes

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

The normal workflow is:

```text
ask -> planning -> implementation -> execute -> testing -> review
```

`incident` and `refactor` are entry modes for operational diagnosis and bounded cleanup.

## Runtime Profiles

Forge uses one controlling interaction flag:

- `runtime.non_interactive: false` means local, interactive work. Forge may ask concise clarification questions for blocking decisions.
- `runtime.non_interactive: true` means automation-safe behavior. Forge does not ask conversational questions; it emits structured statuses and required decisions.

`runtime.profile` is metadata:

- `local` is the normal human-in-the-loop profile.
- `automation` marks automation-safe usage.
- `ci` is reserved metadata only; it does not add CI/CD or executor behavior.

High-risk decisions require human approval. In automation-safe flows, Forge uses `NEEDS_HUMAN_APPROVAL` for security/compliance, PII/secrets, financial correctness, destructive migration, production topology, contract authority, or rollback-risky decisions.

## Artifact Lifecycle

Lifecycle artifacts are small engineering handoff records stored under:

```text
.forge/context/generated/artifacts/
```

Artifact types:

- **ECP Artifact:** approved planning intent, decisions, blockers, and boundaries.
- **Execution Contract Artifact:** implementation-ready task cards and stop conditions.
- **Execute Result Artifact:** actual changed scope, validation status, rollback notes, and unchanged boundaries.
- **Testing Result Artifact:** validation evidence, blockers, coverage gaps, and runtime-sensitive checks.
- **Review Result Artifact:** MR readiness, findings, reviewer focus, and safety notes.
- **Incident Artifact:** diagnosis, mitigation, rollback possibility, and next checks.
- **Refactor Artifact:** problem areas, safe improvements, risks, and out-of-scope redesigns.

Artifacts are bounded engineering records. They are not source of truth, workflow state, dependency graphs, execution triggers, or persistent AI memory. If an artifact conflicts with current repository evidence, repository evidence wins.

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

## Example Workflow

1. `ask`: "How does this service currently publish transaction events?"
2. `planning`: produce an ECP for changing event retry behavior.
3. `implementation`: turn the approved plan into task cards with concrete execution values.
4. `execute`: implement the approved tasks and report changed files, validation, rollback, and reviewer focus.
5. `testing`: run or design structured validation for retry, DLQ, replay, and regression coverage.
6. `review`: assess MR readiness, correctness, safety, validation honesty, and remaining risk.

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
| `runtime/.forge/context/` | Canonical Forge context skeleton: meta, core, layers, systems, knowledge, modes, generated, and temp zones. |
| `runtime/.forge/context/generated/artifacts/` | Optional lifecycle handoff artifacts, created on demand. |
| `specs/` | Normative specifications for initialization, validation, mode invocation, artifact lifecycle, migration, and framework lifecycle. |
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

Future tooling may validate or assist the lifecycle, but it must preserve these boundaries.

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
