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

## Invocation

Tool syntax may differ, but behavior is shared:

| Tool | Examples |
|---|---|
| Claude | `/forge-review`, `/forge-plan` |
| Codex | `$forge-review`, `/skill forge-review`, future-compatible `/forge-review` |
| GitHub Copilot | `/forge-review`, `/forge-plan`, `/forge-ask` prompt files |
| Future tools | Tool-specific syntax that resolves to the same `runtime/skills/<skill>/SKILL.md` |

## Loading

Each skill must:
- Read `.forge/forge.config.yaml` first.
- Apply `runtime.non_interactive` and respect `runtime.profile`.
- Load `.forge/context/00-meta/conventions.md`.
- Use `.forge/context/00-meta/context-manifest.md` only as a routing index.
- Load the matching `.forge/context/modes/<mode>.md`.
- Load only task-relevant scoped context.

Skills must not broad-load `.forge/context` by default.

## Boundary

Adapters reference skills. Skills invoke Forge modes. Forge context remains authoritative.

```text
tool syntax -> tool UX layer -> adapter -> shared skill -> .forge/context mode -> scoped repository evidence
```

Skills may reduce invocation friction. They must not add autonomous chaining, schedulers, DAGs, CI/CD behavior, deploy logic, agent loops, persistent memory, or hidden execution state.
