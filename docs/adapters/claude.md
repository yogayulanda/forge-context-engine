# Claude Adapter

Claude enters Forge through `CLAUDE.md`, shared skills, and optional slash command wrappers.

## How Invocation Works

Common requests:

```text
/forge-plan
/forge-review
Use Forge ask mode to explain this service flow.
Use Forge verify-context mode to check context freshness.
```

The expected path is:

```text
Claude request -> CLAUDE.md or command wrapper -> shared skill -> .forge/context mode -> scoped repository evidence
```

## What The Adapter Does

`CLAUDE.md` tells Claude to:

- read `.forge/forge.config.yaml`
- apply `run.interaction` and related final run config fields
- read conventions and the routing manifest
- read the requested mode file
- load only task-relevant context
- keep output concise and mode-aligned

Slash command wrappers under `adapters/claude/commands/` are invocation helpers only.

## Expected Usage Style

Use natural, bounded prompts:

```text
Use Forge plan mode for this retry improvement.
Preserve the public event schema and list validation needed.
```

```text
Use Forge review mode on this branch.
Focus on correctness, validation honesty, security, context impact, and the exact diff reviewed.
```

## Boundaries

The Claude adapter must not:

- store repository cognition
- duplicate lifecycle semantics
- broad-load `.forge/context`
- imply autonomous execution
- introduce orchestration, schedulers, or persistent memory

Current code, docs, ADRs, and human confirmations win over adapter text.
