# Forge Adapters

Adapters are thin invocation bridges for AI tools.

They point tools to shared Forge skills and Forge context. They do not contain repository cognition, lifecycle semantics, governance semantics, runtime state, orchestration behavior, or memory.

## Layout

```text
adapters/
+-- claude/
+-- codex/
+-- copilot/
+-- cursor/
+-- shared/
```

## Boundary

Adapters may:
- Explain how a tool enters Forge.
- Map tool-specific command surfaces to shared skills.
- Provide loading hints.
- Define concise command wrappers.

Adapters must not:
- Duplicate `.forge/context` content.
- Define repository-specific behavior.
- Reimplement mode semantics.
- Add workflow DAGs, execution engines, schedulers, triggers, agent loops, plugin marketplaces, or memory systems.

The same adapter command must behave differently across repositories only because local `.forge/context` differs.

## Skill Bridge

Shared skills live under `runtime/skills/<skill>/SKILL.md`.

Adapters should reference those files instead of copying reusable workflow logic. The intended flow is:

```text
tool syntax -> tool UX layer -> adapter -> shared skill -> .forge/context mode -> scoped repository evidence
```

Tool syntax may differ, including Claude slash commands, Codex skill prompts, Cursor rules, or GitHub Copilot prompt files, but skill behavior remains shared.
