# /forge-verify-context

Use shared skill:
`.forge/skills/forge-verify-context/SKILL.md`

This is a Claude slash-command wrapper for Forge verify-context mode.

Verify-context checks `.forge/context` health/freshness only. It must not verify plan readiness, ECP completeness, code diff result, MR readiness, or general validation.

Repository behavior and lifecycle semantics come from:
- `.forge/context`
- `.forge/context/modes/verify-context.md`
- current repository evidence

Use scoped repository loading only. Do not add repository cognition, orchestration, memory, or duplicated lifecycle semantics here.
