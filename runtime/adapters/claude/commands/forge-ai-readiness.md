# /forge-ai-readiness

Use shared skill:
`runtime/skills/forge-ai-readiness/SKILL.md`

This is a Claude slash-command wrapper for Forge ai-readiness mode.

Focus on:
- Repository AI-readiness, context fitness, and ambiguity.
- Severity-grouped readiness findings and practical remediation.
- Context drift, wrapper readiness, validation readiness, and safe AI change boundaries.
- Report and roadmap output without implementing changes.

Repository behavior and lifecycle semantics come from:
- `.forge/context`
- `.forge/context/modes/ai-readiness.md`
- current repository evidence

Use scoped repository loading only.

Do not add repository cognition, orchestration, memory, or duplicated lifecycle semantics here.
