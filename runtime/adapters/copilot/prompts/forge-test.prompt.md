# /forge-test

Use shared skill:
`runtime/skills/forge-test/SKILL.md`

This is a GitHub Copilot prompt wrapper for Forge testing mode.

Focus on:
- Test strategy and validation evidence for the requested scope.
- Automated and manual checks with honest gaps.
- Failure interpretation grounded in repository behavior.
- No review-mode expansion or implementation drift unless requested.

Repository behavior and lifecycle semantics come from:
- `.forge/context`
- `.forge/context/modes/testing.md`
- current repository evidence

Use scoped repository loading only.

Do not add repository cognition, orchestration, memory, or duplicated lifecycle semantics here.
