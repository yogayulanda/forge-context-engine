# Codex Adapter

Codex uses the shared `AGENTS.md` repository-native Forge entrypoint. Codex is skills-first for Forge usage: prompts and command-like invocations resolve to shared skills under `.forge/skills/*/SKILL.md` in target repositories.

The adapter is a thin instruction bridge, not a second Forge runtime and not a Codex-specific command-wrapper layer. `AGENTS.md` may also be used by other AGENTS-compatible tools such as OpenCode, but Codex invocation notes remain adapter-specific here.

## Responsibility

- Point Codex to `.forge/forge.config.yaml`.
- Apply `run.interaction` and related final run config fields.
- Point Codex to shared skills under `.forge/skills/`.
- Let each shared skill invoke `.forge/context/modes/<mode>.md`.
- Load only relevant scoped repository context.
- Keep commands and natural language requests as thin operational prompts.
- Do not duplicate lifecycle semantics, governance rules, mode behavior, or repo-specific cognition.

## Natural Use

Codex should treat these as Forge skill entrypoints:

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

## Command Use

Codex-facing invocation may use names such as:

- `$forge-review`
- `/skill forge-review`
- natural prompts such as "Use Forge review mode"

Command behavior must come from shared skills, local `.forge/context`, and current repository evidence, not from Codex-specific adapter files.

Do not materialize Codex command-wrapper files unless the Codex runtime explicitly requires them later. If that becomes necessary, wrappers must remain pointers to shared skills.

Execute mode requires an approved ECP. If scope is unclear or a policy/high-risk decision lacks human approval, Codex should stop and report the blocker.

## Responsibility Chain

```text
tool syntax -> tool UX layer -> adapter -> shared skill -> .forge/context mode -> scoped repository evidence
```
