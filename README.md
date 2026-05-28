# Forge Context Engine

Forge is an AI-native engineering workflow system focused on bounded engineering cognition for real-world software development.

It helps engineers and AI assistants work with repository context in a disciplined way: scoped evidence, clear lifecycle modes, explicit uncertainty, and reviewable engineering outputs. Forge is for teams that want AI-assisted planning, implementation guidance, execution reporting, testing, review, incident diagnosis, and refactoring with visible human control.

Forge v1 is the lifecycle foundation: a context structure, mode protocol, validation rules, shared skills, thin adapters, and lightweight handoff artifacts.

## Quick Mental Model

Forge is a repository-native way to work with AI assistants without giving up engineering control.

```text
repository evidence -> scoped context -> one lifecycle mode -> reviewable engineering output
```

A human asks for one kind of work, Forge loads the matching context, and the output stays tied to code, docs, ADRs, explicit confirmations, and visible unknowns.

The practical rule is simple:

- Use `ask` to understand.
- Use `planning` to shape a change.
- Use `implementation` to turn approved intent into executable task cards.
- Use `execute` to modify the repository within approved boundaries.
- Use `testing` to validate.
- Use `review` to decide MR readiness.
- Use `incident` when something is broken.
- Use `refactor` for bounded behavior-preserving cleanup.

## How Forge Works Operationally

Forge has three lightweight parts:

| Part | Role | Boundary |
|---|---|---|
| `.forge/context` | Repo-local conventions, mode files, scoped knowledge, and optional handoff artifacts. | Code, docs, ADRs, and human decisions still win. |
| Lifecycle modes | Separate understanding, planning, implementation breakdown, execution, testing, review, incident diagnosis, and refactoring. | Each mode owns one kind of work. |
| Skills and adapters | Let Claude, Codex, GitHub Copilot, Cursor, and other tools invoke the same Forge behavior. | Tool files stay thin invocation surfaces. |

In normal use, the assistant reads the Forge config, reads the requested mode, loads only task-relevant context, checks current repository evidence, and returns a concise engineering output for that mode.

## 10-Minute First Use

1. Copy the `runtime/` template into the target repository root.
2. Keep `runtime/.forge/context` as the starting `.forge/context` structure for that repository.
3. Keep `CLAUDE.md` and/or `AGENTS.md` as thin tool entrypoints when those tools are used.
4. Ask a scoped first question, such as: `Use Forge ask mode to explain how this service handles retries.`
5. For a change, move through the smallest useful lifecycle path, usually `ask -> planning -> implementation -> execute -> testing -> review`.

For a practical setup walkthrough, see [Getting Started](docs/getting-started.md).

## Documentation

| Need | Start here |
|---|---|
| Set up Forge in a repository and get the first successful invocation. | [Getting Started](docs/getting-started.md) |
| See one end-to-end engineering workflow. | [First Workflow](docs/first-workflow.md) |
| Decide which lifecycle mode to use right now. | [Mode Selection](docs/mode-selection.md) |
| Copy short realistic request patterns. | [Examples](docs/examples/) |
| Use Forge from Claude, Codex, or GitHub Copilot. | [Adapters](docs/adapters/) |
| Understand the cognition, lifecycle, and adapter models. | [Architecture Notes](docs/architecture/) |

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

Forge does not automatically advance from one step to another, approve risky choices, open PRs, deploy code, or merge changes.

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

High-risk decisions require human approval. In automation-safe flows, Forge uses blocking or approval statuses instead of inventing answers.

## Repository Structure

| Path | Purpose |
|---|---|
| `runtime/` | Runtime template copied into target repositories during initialization. |
| `runtime/skills/` | Shared Forge skill entrypoints for Claude, Codex, GitHub Copilot, Cursor, and future tools. |
| `runtime/CLAUDE.md` | Thin Claude-compatible adapter pointing to `.forge/`. |
| `runtime/AGENTS.md` | Thin Codex-compatible adapter pointing to `.forge/`. |
| `runtime/adapters/` | Thin tool compatibility notes and shared command conventions. |
| `runtime/.forge/context/` | Canonical Forge context skeleton. |
| `runtime/.forge/context/generated/artifacts/` | Optional lifecycle handoff artifacts, created on demand. |
| `docs/` | First-use guides, examples, adapter onboarding, and concise architecture notes. |
| `specs/` | Normative specifications for initialization, validation, mode invocation, artifacts, migration, lifecycle, and adapters. |
| `validation-cases/` | Focused cases used to validate Forge cognition patterns. |
| `FORGE-CONTEXT-ARCHITECTURE.md` | Architecture foundation and design rationale. |

## Current Status

Forge v1 status:

- lifecycle foundation complete
- mode boundaries stabilized
- runtime profile and non-interactive semantics bounded
- artifact lifecycle defined
- validation rules consolidated
- ready for real-world pilot usage
- entering evidence-based refinement

Forge v1 is not claiming complete automation, benchmarked behavior across all repositories, or production runtime tooling.

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

Good refinements reduce ambiguity seen in real usage, improve mode output clarity, tighten validation rules around observed failures, preserve repository-first truth, keep lifecycle responsibilities distinct, and improve safety without adding bureaucracy.

Avoid changes that add theoretical architecture, broad automation semantics, hidden state, or new lifecycle concepts without repeated evidence from real projects.

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Security

Please report security concerns privately. Do not post production credentials, customer data, tokens, or sensitive incident details in public issues.

See [SECURITY.md](SECURITY.md).

## License

Forge Context Engine is licensed under the Apache License 2.0.

See [LICENSE](LICENSE).
