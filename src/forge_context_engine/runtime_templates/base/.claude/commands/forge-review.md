# /forge-review

Use shared skill:
`runtime/skills/forge-review/SKILL.md`

This is a Claude slash-command wrapper for Forge review mode.

Focus on:
- MR-style correctness and risk review.
- Severity-grouped findings and validation honesty.
- Boundary drift, secrets/PII safety, and rollback risk.
- Review readiness without implementing changes.

Repository behavior and lifecycle semantics come from:
- `.forge/context`
- `.forge/context/modes/review.md`
- current repository evidence

Use scoped repository loading only.

Do not add repository cognition, orchestration, memory, or duplicated lifecycle semantics here.
