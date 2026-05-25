# /forge-incident

Use shared skill:
`runtime/skills/forge-incident/SKILL.md`

This is a GitHub Copilot prompt wrapper for Forge incident mode.

Focus on:
- Evidence-backed diagnosis and impact framing.
- Immediate mitigation, rollback, and containment options.
- Unknowns, missing signals, and next verification steps.
- No broad remediation plan beyond the incident scope.

Repository behavior and lifecycle semantics come from:
- `.forge/context`
- `.forge/context/modes/incident.md`
- current repository evidence

Use scoped repository loading only.

Do not add repository cognition, orchestration, memory, or duplicated lifecycle semantics here.
