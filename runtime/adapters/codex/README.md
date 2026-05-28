# Codex Adapter

Codex uses `AGENTS.md` as the repository-native Forge entrypoint. Codex is skills-first for Forge usage: prompts and command-like invocations resolve to shared skills under `runtime/skills/*/SKILL.md`.

The adapter is a thin instruction bridge, not a second Forge runtime and not a Codex-specific command-wrapper layer.

## Responsibility

- Point Codex to `.forge/forge.config.yaml`.
- Apply `runtime.non_interactive` and respect `runtime.profile`.
- Point Codex to shared skills under `runtime/skills/`.
- Let each shared skill invoke `.forge/context/modes/<mode>.md`.
- Load only relevant scoped repository context.
- Keep commands and natural language requests as thin operational prompts.
- Do not duplicate lifecycle semantics, governance rules, mode behavior, or repo-specific cognition.

## Natural Use

Codex should treat these as Forge skill entrypoints:

| User wording | Shared skill |
|---|---|
| `Use Forge ask mode` | `forge-ask` |
| `Use Forge planning mode` | `forge-plan` |
| `Use Forge implementation mode` | `forge-implement` |
| `Use Forge execute mode` | `forge-execute` |
| `Use Forge testing mode` | `forge-test` |
| `Use Forge review mode` | `forge-review` |
| `Use Forge incident mode` | `forge-incident` |
| `Use Forge refactor mode` | `forge-refactor` |

## Command Use

Codex-facing invocation may use names such as:

- `$forge-review`
- `/skill forge-review`
- natural prompts such as "Use Forge review mode"

Command behavior must come from shared skills, local `.forge/context`, and current repository evidence, not from Codex-specific adapter files.

Do not materialize Codex command-wrapper files unless the Codex runtime explicitly requires them later. If that becomes necessary, wrappers must remain pointers to shared skills.

Execute mode requires approved task cards or an execution contract. If scope is unclear or a HIGH-risk decision lacks human approval, Codex should stop and report the blocker.

## Responsibility Chain

```text
tool syntax -> tool UX layer -> adapter -> shared skill -> .forge/context mode -> scoped repository evidence
```
