# /forge-test

Use shared skill:
`runtime/skills/forge-test/SKILL.md`

This is a Claude slash-command wrapper for Forge testing mode.

Focus on:
- Structured validation strategy or evidence.
- Automated, manual, blocked, and environment-dependent checks.
- Coverage gaps and unvalidated risk.
- No review-mode substitution or CI/CD semantics.

Repository behavior and lifecycle semantics come from:
- `.forge/context`
- `.forge/context/modes/testing.md`
- current repository evidence

Use scoped repository loading only.

Do not add repository cognition, orchestration, memory, or duplicated lifecycle semantics here.
