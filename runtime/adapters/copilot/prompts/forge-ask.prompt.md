# /forge-ask

Use shared skill:
`runtime/skills/forge-ask/SKILL.md`

This is a GitHub Copilot prompt wrapper for Forge ask mode.

Focus on:
- Repository understanding grounded in current evidence.
- Clear separation of evidence, assumptions, and unknowns.
- Concise answers with scoped context loading.
- No planning, implementation, or lifecycle expansion unless requested.

Repository behavior and lifecycle semantics come from:
- `.forge/context`
- `.forge/context/modes/ask.md`
- current repository evidence

Use scoped repository loading only.

Do not add repository cognition, orchestration, memory, or duplicated lifecycle semantics here.
