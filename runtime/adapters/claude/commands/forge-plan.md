# /forge-plan

Use shared skill:
`runtime/skills/forge-plan/SKILL.md`

This is a Claude slash-command wrapper for Forge planning mode.

Focus on:
- Evidence-led Engineering Change Plans.
- Repository constraints, risks, blockers, and unknowns.
- Proposed approach and validation expectations.
- No code changes or executable task-card expansion.

Repository behavior and lifecycle semantics come from:
- `.forge/context`
- `.forge/context/modes/planning.md`
- current repository evidence

Use scoped repository loading only.

Do not add repository cognition, orchestration, memory, or duplicated lifecycle semantics here.
