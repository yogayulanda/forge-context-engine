# /forge-implement

Use shared skill:
`runtime/skills/forge-implement/SKILL.md`

This is a GitHub Copilot prompt wrapper for Forge implementation mode.

Focus on:
- Execution-ready task cards from approved planning context.
- Explicit dependencies, blockers, and validation expectations.
- Concrete execution values before readiness.
- Stop conditions when confirmation is still required.

Repository behavior and lifecycle semantics come from:
- `.forge/context`
- `.forge/context/modes/implementation.md`
- current repository evidence

Use scoped repository loading only.

Do not add repository cognition, orchestration, memory, or duplicated lifecycle semantics here.
