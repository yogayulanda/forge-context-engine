# Claude Adapter

Claude uses `CLAUDE.md` as the root Forge adapter.

## Responsibility

- Point Claude to `.forge/forge.config.yaml`.
- Apply `run.interaction` and related final run config fields.
- Point Claude slash commands to shared skills under `runtime/skills/`.
- Let each shared skill invoke `.forge/context/modes/<mode>.md`.
- Keep slash commands thin if materialized.

## Slash Commands

Claude slash commands live under `commands/` when materialized. They wrap shared Forge skills:

- `/forge-init` -> `runtime/skills/forge-init/SKILL.md`
- `/forge-ask` -> `runtime/skills/forge-ask/SKILL.md`
- `/forge-plan` -> `runtime/skills/forge-plan/SKILL.md`
- `/forge-implementation` -> `runtime/skills/forge-implementation/SKILL.md`
- `/forge-execute` -> `runtime/skills/forge-execute/SKILL.md`
- `/forge-review` -> `runtime/skills/forge-review/SKILL.md`
- `/forge-verify-context` -> `runtime/skills/forge-verify-context/SKILL.md`

Compatibility wrappers such as `/forge-implement`, `/forge-test`, `/forge-incident`, and `/forge-refactor` must route into the final lifecycle and must not define core modes.

Slash commands must not duplicate repository cognition, lifecycle rules, governance policy, runtime semantics, or artifact semantics.

Available command adapters include the final core commands and compatibility scenario commands.
