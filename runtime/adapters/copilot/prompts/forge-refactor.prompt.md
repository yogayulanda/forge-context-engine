# /forge-refactor

Use shared skill:
`runtime/skills/forge-refactor/SKILL.md`

This is a GitHub Copilot prompt wrapper for Forge refactor mode.

Focus on:
- Behavior-preserving technical debt reduction.
- Bounded risk classification and validation expectations.
- Existing contracts, tests, and repository conventions.
- No architecture rewrite, paradigm migration, or hidden behavior change.

Repository behavior and lifecycle semantics come from:
- `.forge/context`
- `.forge/context/modes/refactor.md`
- current repository evidence

Use scoped repository loading only.

Do not add repository cognition, orchestration, memory, or duplicated lifecycle semantics here.
