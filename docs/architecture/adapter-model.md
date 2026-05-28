# Adapter Model

Forge adapters make tool invocation easier while keeping repository cognition in `.forge/context`.

## Responsibility Chain

```text
tool syntax -> tool UX layer -> adapter -> shared skill -> .forge/context mode -> scoped repository evidence
```

## Responsibilities

| Layer | Responsibility |
|---|---|
| Tool syntax | The command, prompt, or UI gesture supported by the tool. |
| Tool UX layer | Tool-specific prompt file, slash command, or skill invocation surface. |
| Adapter | Thin bridge text that points to shared skills and loading rules. |
| Shared skill | Reusable Forge workflow behavior for one mode. |
| `.forge/context` mode | Repository-local mode behavior and scoped loading delta. |
| Repository evidence | Code, docs, ADRs, tests, configs, and human confirmations. |

## Adapter Boundaries

Adapters may:

- explain how a tool enters Forge
- map tool-specific syntax to shared skills
- provide concise loading hints
- keep invocation consistent across tools

Adapters must not:

- duplicate repository cognition
- define new lifecycle semantics
- add governance rules
- create workflow DAGs
- run schedulers or triggers
- add agent loops
- store persistent memory

## Why Thin Adapters Matter

Claude, Codex, GitHub Copilot, Cursor, and future tools should differ only in invocation surface. The engineering behavior should come from shared skills, local Forge mode files, and current repository evidence.
