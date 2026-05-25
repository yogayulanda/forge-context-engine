# /forge-refactor

Use shared skill:
`runtime/skills/forge-refactor/SKILL.md`

This is a Claude slash-command wrapper for Forge refactor mode.

Focus on:
- Bounded, behavior-preserving cleanup.
- Evidence for affected behavior, dependencies, and tests.
- Risk boundaries and validation expectations.
- No architecture rewrite or hidden behavior change.

Repository behavior and lifecycle semantics come from:
- `.forge/context`
- `.forge/context/modes/refactor.md`
- current repository evidence

Use scoped repository loading only.

Do not add repository cognition, orchestration, memory, or duplicated lifecycle semantics here.
