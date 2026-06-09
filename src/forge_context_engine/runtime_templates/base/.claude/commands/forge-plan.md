# /forge-plan

Use shared skill:
`runtime/skills/forge-plan/SKILL.md`

This is a Claude slash-command wrapper for Forge plan mode.

Plan mode produces a Quick Plan or SDD with an explicit reason and final status. It does not edit code or produce an ECP.

Repository behavior and lifecycle semantics come from:
- `.forge/context`
- `.forge/context/modes/plan.md`
- current repository evidence

Use scoped repository loading only. Do not add repository cognition, orchestration, memory, or duplicated lifecycle semantics here.
