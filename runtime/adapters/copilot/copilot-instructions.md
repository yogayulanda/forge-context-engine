# Forge GitHub Copilot Instructions

This repository uses Forge through shared skills and `.forge/context`.

GitHub Copilot prompts are an invocation UX layer only. They route requests such as `/forge-review` or `/forge-plan` to shared Forge skills under `runtime/skills/*/SKILL.md`.

## Responsibility Chain

```text
tool syntax -> tool UX layer -> adapter -> shared skill -> .forge/context mode -> scoped repository evidence
```

## Rules

- Treat `.forge/context` as the repository source of truth.
- Treat `runtime/skills/*/SKILL.md` as reusable Forge workflow behavior.
- Treat `.github/prompts/*.prompt.md` as thin Copilot prompt wrappers.
- Read `.forge/forge.config.yaml` first when entering Forge.
- Load `.forge/context/00-meta/conventions.md` and use `.forge/context/00-meta/context-manifest.md` only as a routing index.
- Load the matching `.forge/context/modes/<mode>.md` before mode-specific work.
- Load only scoped repository evidence required for the request.

## Do Not

- Do not add repository cognition, lifecycle semantics, governance rules, or mode behavior to Copilot prompts.
- Do not create a separate Copilot workflow system.
- Do not introduce orchestration, schedulers, DAGs, runtime executors, CI/CD, deploy behavior, memory systems, or autonomous chaining.
- Do not treat prompt files as source of truth when `.forge/context` or repository evidence differs.
