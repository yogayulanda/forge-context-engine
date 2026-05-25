# /forge-execute

Use shared skill:
`runtime/skills/forge-execute/SKILL.md`

This is a Claude slash-command wrapper for Forge execute mode.

Focus on:
- Approved task cards or execution contract only.
- Bounded repository changes and hidden-change checks.
- Stop on unclear scope or missing execution values.
- Stop on HIGH-risk decisions without human approval.
- Distinguish implementation failure from environment/tooling failure.

Repository behavior and lifecycle semantics come from:
- `.forge/context`
- `.forge/context/modes/execute.md`
- current repository evidence

Use scoped repository loading only.

Do not add repository cognition, orchestration, memory, duplicated lifecycle semantics, CI/CD, deploy behavior, runtime execution, or autonomous chaining here.
