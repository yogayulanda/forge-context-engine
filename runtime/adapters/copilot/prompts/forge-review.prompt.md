# /forge-review

Use shared skill:
`runtime/skills/forge-review/SKILL.md`

This is a GitHub Copilot prompt wrapper for Forge review mode.

Focus on:
- Bugs, correctness risks, and missing validation.
- Boundary drift, hidden scope, and approved-contract adherence.
- Unsafe secrets, PII, rollback, or operational risk.
- MR-style findings and readiness signals.

Repository behavior and lifecycle semantics come from:
- `.forge/context`
- `.forge/context/modes/review.md`
- current repository evidence

Use scoped repository loading only.

Do not add repository cognition, orchestration, memory, or duplicated lifecycle semantics here.
