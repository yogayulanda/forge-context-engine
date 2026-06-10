# OpenCode Adapter

OpenCode uses the shared `AGENTS.md` repository-native Forge entrypoint. OpenCode's own `/init` flow creates `AGENTS.md`, so Forge should treat that surface as the thin OpenCode bridge rather than introducing a second root wrapper.

The adapter is a thin invocation bridge. Forge requests should resolve to shared skills under `runtime/skills/*/SKILL.md`, which then load the relevant `.forge/context` mode and scoped repository evidence.

## Responsibility

- Point OpenCode to `.forge/forge.config.yaml`.
- Apply `run.interaction` and related final run config fields.
- Point OpenCode to shared skills under `runtime/skills/`.
- Let each shared skill invoke `.forge/context/modes/<mode>.md`.
- Load only relevant scoped repository context.
- Keep prompts and command-like requests as thin operational prompts.
- Do not duplicate lifecycle semantics, governance rules, mode behavior, or repo-specific cognition.

## Natural Use

OpenCode should treat these as Forge skill entrypoints:

| User wording | Shared skill |
|---|---|
| `Use Forge init mode` | `forge-init` |
| `Use Forge ask mode` | `forge-ask` |
| `Use Forge plan mode` | `forge-plan` |
| `Use Forge implementation mode` | `forge-implementation` |
| `Use Forge execute mode` | `forge-execute` |
| `Use Forge review mode` | `forge-review` |
| `Use Forge ai-readiness mode` | `forge-ai-readiness` |
| `Use Forge verify-context mode` | `forge-verify-context` |

`forge-test`, `forge-incident`, and `forge-refactor` are scenario compatibility skills, not core modes.

## Invocation

OpenCode-facing invocation may use:

- natural prompts such as `Use Forge review mode`
- command-like requests such as `/forge-review` when surfaced through an OpenCode command layer
- skill-like prompts such as `forge-review` when the active OpenCode surface supports them

Command behavior must come from shared skills, local `.forge/context`, and current repository evidence, not from OpenCode-specific adapter files.

OpenCode plan/build agent selection is a tool concern, not a Forge mode definition. Forge mode semantics still come from shared skills and `.forge/context`.

Execute mode requires an approved ECP. If scope is unclear or a policy/high-risk decision lacks human approval, OpenCode should stop and report the blocker.

## Responsibility Chain

```text
tool syntax -> tool UX layer -> adapter -> shared skill -> .forge/context mode -> scoped repository evidence
```
