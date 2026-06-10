# Shared Adapter Conventions

Shared adapter content applies to every tool-specific adapter.

## Rules

- Forge core owns cognition.
- `.forge/context` owns repository-native truth.
- Mode files own lifecycle loading deltas.
- Adapters own invocation only.
- Shared skills own reusable operational prompt structure.
- Commands are tool-specific wrappers around shared skills.
- GitHub Copilot prompt files are tool UX wrappers around shared skills.
- Tool-specific files must point back to Forge core instead of copying policy text.

## Shared Skills

Generated target repositories keep shared Forge skills under `.forge/skills/`.

They are reusable invocation layers, not cognition sources, adapters, runtime systems, or orchestration units.

Use this bridge:

```text
tool syntax -> tool UX layer -> adapter -> shared skill -> .forge/context mode -> scoped repository evidence
```

## Required Skill Sections

- `Purpose`
- `Load`
- `Invocation`
- `Focus`
- `Output`
- `Do NOT`

## Anti-Drift

Adapters, commands, and skills must not become:
- Orchestration systems.
- Alternate runtime layers.
- Repository knowledge stores.
- Memory systems.
- Autonomous-agent frameworks.
- CI/CD or deploy systems.

When behavior needs more detail, load the relevant Forge mode and conventions from `.forge/context`.
