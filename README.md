# Forge Context Engine

Forge is a developer workflow framework for AI coding tools.

It helps engineers and AI assistants work with repository context in a disciplined way: scoped evidence, explicit lifecycle modes, ambiguity and risk gates, AI-tool-ready Execution Context Packages, bounded execution, security-aware review, and context health verification.

Forge v1 is the lifecycle foundation: a context structure, mode protocol, validation rules, shared skills, thin adapters, and lightweight handoff artifacts.

## Quick Mental Model

Forge is a repository-native way to work with AI assistants without giving up engineering control.

```text
repository evidence -> scoped context -> one lifecycle mode -> reviewable engineering output
```

A human asks for one kind of work, Forge loads the matching context, and the output stays tied to code, docs, ADRs, explicit confirmations, and visible unknowns.

The standard lifecycle is:

```text
init -> ask -> plan -> implementation -> execute -> review -> verify-context
```

The practical rule is simple:

- Use `init` to create confirmed repository context and config.
- Use `ask` to understand current behavior from context and scoped evidence.
- Use `plan` to shape a Quick Plan or SDD.
- Use `implementation` to turn an approved plan into an Execution Context Package.
- Use `execute` to apply an approved ECP within explicit boundaries.
- Use `review` to inspect the executed result, validation evidence, security, and context impact.
- Use `verify-context` to check `.forge/context` health and freshness only.

## How Forge Works Operationally

Forge has three lightweight parts:

| Part | Role | Boundary |
|---|---|---|
| `.forge/context` | Repo-local conventions, mode files, scoped knowledge, and optional handoff artifacts. | Code, docs, ADRs, and human decisions still win. |
| Lifecycle modes | Separate init, understanding, planning, ECP preparation, execution, review, and context verification. | Each mode owns one kind of work. |
| Skills and adapters | Let Claude, Codex, GitHub Copilot, Cursor, and other tools invoke the same Forge behavior. | Tool files stay thin invocation surfaces. |

In normal use, the assistant reads the Forge config, reads the requested mode, loads only task-relevant context, checks current repository evidence, and returns a concise engineering output for that mode.

## 10-Minute First Use

1. Copy the `runtime/` template into the target repository root.
2. Keep `runtime/.forge/context` as the starting `.forge/context` structure for that repository.
3. Keep `CLAUDE.md` and/or `AGENTS.md` as thin tool entrypoints when those tools are used.
4. Ask a scoped first question, such as: `Use Forge ask mode to explain how this service handles retries.`
5. For a change, move through the smallest useful lifecycle path, usually `ask -> plan -> implementation -> execute -> review`.

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
-> plan: propose the engineering change plan
-> implementation: produce the ECP and stop conditions
-> execute: apply the approved repository changes
-> review: assess MR readiness, validation evidence, security, and context impact
-> verify-context: check context health when context may be stale or affected
-> merge: handled by the team outside Forge
```

Small changes may skip `plan` when the scope is obvious. Incident response, refactoring, and test-focused work are workflow scenarios that use the same core lifecycle modes rather than separate core modes.

Forge does not automatically advance from one step to another, approve risky choices, open PRs, deploy code, or merge changes.

## Runtime Behavior

Forge uses `run.interaction` as the interaction control:

| Setting | Behavior |
|---|---|
| `run.interaction: manual` | Local, interactive work. Forge may ask concise clarification questions for blocking decisions. |
| `run.interaction: auto` | Automation-safe behavior. Forge does not ask conversational questions; it emits structured required decisions and blocking statuses. |

High-risk decisions require human approval by policy. In automation-safe flows, Forge uses blocking or approval statuses instead of inventing answers.

## Repository Structure

| Path | Purpose |
|---|---|
| `runtime/` | Runtime template copied into target repositories during initialization. |
| `runtime/skills/` | Shared Forge skill entrypoints for Claude, Codex, GitHub Copilot, Cursor, and future tools. |
| `runtime/CLAUDE.md` | Thin Claude-compatible adapter pointing to `.forge/`. |
| `runtime/AGENTS.md` | Thin Codex-compatible adapter pointing to `.forge/`. |
| `runtime/adapters/` | Thin tool compatibility notes and shared command conventions. |
| `runtime/.forge/context/` | Canonical Forge context skeleton. |
| `.forge/generated` | Generated artifacts, committed manually when relevant. |
| `.forge/context-patches` | Reviewable context update proposals. |
| `.forge/temp`, `.forge/cache` | Local-only temporary/cache data. |
| `docs/` | First-use guides, examples, adapter onboarding, and concise architecture notes. |
| `specs/` | Normative specifications for initialization, validation, mode invocation, artifacts, migration, lifecycle, and adapters. |
| `validation-cases/` | Focused cases used to validate Forge cognition patterns. |
| `FORGE-CONTEXT-ARCHITECTURE.md` | Architecture foundation and design rationale. |

## Current Status

Forge v1 status:

- full-version lifecycle foundation being aligned to `init`, `ask`, `plan`, `implementation`, `execute`, `review`, and `verify-context`
- mode boundaries stabilized
- manual and automation-safe interaction semantics bounded through `run.interaction`
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
