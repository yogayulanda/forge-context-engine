# /forge-incident

Use shared skill:
`runtime/skills/forge-incident/SKILL.md`

This is a Claude slash-command wrapper for Forge incident mode.

Focus on:
- Observed symptoms, impact, and current evidence.
- Likely causes, possible causes, and explicit unknowns.
- Mitigation, rollback possibility, and next checks.
- No speculative redesign or incident automation.

Repository behavior and lifecycle semantics come from:
- `.forge/context`
- `.forge/context/modes/incident.md`
- current repository evidence

Use scoped repository loading only.

Do not add repository cognition, orchestration, memory, or duplicated lifecycle semantics here.
