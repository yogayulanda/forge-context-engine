# /forge-implement

Use shared skill:
`runtime/skills/forge-implement/SKILL.md`

This is a Claude slash-command wrapper for Forge implementation mode.

Focus on:
- Readiness status and execution values.
- Task cards for approved scope.
- Blockers, dependencies, and stop conditions.
- Human confirmation for unresolved or HIGH-risk decisions.

Repository behavior and lifecycle semantics come from:
- `.forge/context`
- `.forge/context/modes/implementation.md`
- current repository evidence

Use scoped repository loading only.

Do not add repository cognition, orchestration, memory, or duplicated lifecycle semantics here.
