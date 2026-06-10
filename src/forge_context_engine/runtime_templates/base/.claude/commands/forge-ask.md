# /forge-ask

Use shared skill:
`.forge/skills/forge-ask/SKILL.md`

This is a Claude slash-command wrapper for Forge ask mode.

Focus on:
- Scoped repository understanding.
- Evidence-backed explanations.
- Explicit assumptions, inferences, and unknowns.
- No planning, mutation, or broad audit.

Repository behavior and lifecycle semantics come from:
- `.forge/context`
- `.forge/context/modes/ask.md`
- current repository evidence

Use scoped repository loading only.

Do not add repository cognition, orchestration, memory, or duplicated lifecycle semantics here.
