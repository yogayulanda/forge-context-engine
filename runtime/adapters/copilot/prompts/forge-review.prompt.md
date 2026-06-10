# /forge-review

Use shared skill:
`.forge/skills/forge-review/SKILL.md`

This is a GitHub Copilot prompt wrapper for Forge review mode.

Review mode is read-only by default. Users do not need to add `Do not edit files` for normal usage.

Focus on:
- Bugs, correctness risks, and missing validation.
- Boundary drift, hidden scope, plan/ECP adherence, and context impact.
- Unsafe secrets, PII, rollback, or operational risk.
- Review status, MR readiness, validation evidence, security review, and next mode.

Repository behavior and lifecycle semantics come from:
- `.forge/context`
- `.forge/context/modes/review.md`
- current repository evidence

Use scoped repository loading only.

Do not add repository cognition, orchestration, memory, or duplicated lifecycle semantics here.
