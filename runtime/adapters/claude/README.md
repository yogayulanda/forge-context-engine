# Claude Adapter

Claude uses `CLAUDE.md` as the root Forge adapter.

## Responsibility

- Point Claude to `.forge/forge.config.yaml`.
- Point Claude slash commands to shared skills under `runtime/skills/`.
- Let each shared skill invoke `.forge/context/modes/<mode>.md`.
- Keep slash commands thin if materialized.

## Slash Commands

Claude slash commands live under `commands/` when materialized. They wrap shared Forge skills:

- `/forge-ask` -> `runtime/skills/forge-ask/SKILL.md`
- `/forge-plan` -> `runtime/skills/forge-plan/SKILL.md`
- `/forge-implement` -> `runtime/skills/forge-implement/SKILL.md`
- `/forge-execute` -> `runtime/skills/forge-execute/SKILL.md`
- `/forge-test` -> `runtime/skills/forge-test/SKILL.md`
- `/forge-review` -> `runtime/skills/forge-review/SKILL.md`
- `/forge-incident` -> `runtime/skills/forge-incident/SKILL.md`
- `/forge-refactor` -> `runtime/skills/forge-refactor/SKILL.md`

Slash commands must not duplicate repository cognition, lifecycle rules, governance policy, runtime semantics, or artifact semantics.

Available command adapters:

- `forge-ask.md`
- `forge-plan.md`
- `forge-implement.md`
- `forge-execute.md`
- `forge-test.md`
- `forge-review.md`
- `forge-incident.md`
- `forge-refactor.md`
