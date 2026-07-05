# Forge Shared Skills

Forge skills are reusable invocation layers for Forge modes.

They make Forge workflows easier to invoke from Claude, Codex, GitHub Copilot, Cursor, and future AI tools while keeping repository cognition in `.forge/context`.

## Philosophy

Skills are:
- Shared mode entrypoints.
- Lightweight loading and output prompts.
- Tool-neutral invocation contracts.
- Thin wrappers around Forge lifecycle behavior.

Skills are not:
- Cognition sources.
- Adapters.
- Runtime systems.
- Orchestration units.
- Memory stores.
- Execution platforms.

`.forge/context` remains the source of truth for repository intelligence, lifecycle semantics, governance rules, artifact boundaries, and mode-owned behavior.

## Final Core Skills

| Mode | Skill |
|---|---|
| `init` | `forge-init` |
| `ask` | `forge-ask` |
| `plan` | `forge-plan` |
| `implementation` | `forge-implementation` |
| `execute` | `forge-execute` |
| `review` | `forge-review` |
| `ai-readiness` | `forge-ai-readiness` |
| `verify-context` | `forge-verify-context` |
| `update-context` | `forge-update-context` |

Scenario compatibility skills such as `forge-test`, `forge-incident`, and `forge-refactor` route into the core lifecycle. They are not core modes.

## Loading

Each skill must:
- Read `.forge/forge.config.yaml` first.
- Apply `run.interaction`, `run.output`, `run.output_detail`, `run.write_behavior`, and `run.failure_behavior`.
- Load `.forge/runtime/meta/conventions.md`.
- Use `.forge/runtime/meta/context-manifest.md` only as a routing index.
- Load the matching `.forge/runtime/modes/<mode>.md`.
- Load only task-relevant scoped context.

Skills must not broad-load `.forge/context` by default.

## Boundary

Adapters reference skills. Skills invoke Forge modes. Forge context remains authoritative.

```text
tool syntax -> tool UX layer -> adapter -> shared skill -> .forge/context mode -> scoped repository evidence
```

Skills may reduce invocation friction. They must not add autonomous chaining, schedulers, DAGs, CI/CD behavior, deploy logic, agent loops, persistent memory, or hidden execution state.
