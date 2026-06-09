# /forge-ai-readiness

Use shared skill:
`runtime/skills/forge-ai-readiness/SKILL.md`

This is a GitHub Copilot prompt wrapper for Forge ai-readiness mode.

AI-readiness mode is read-only by definition. Users do not need to add `Do not edit files` for normal usage.

Focus on:
- Repository AI-readiness, context fitness, and ambiguity.
- Severity-grouped readiness findings, strengths, and practical remediation.
- Context drift, validation readiness, change-safety hotspots, and wrapper readiness.
- Report and roadmap output without implementing changes.

Repository behavior and lifecycle semantics come from:
- `.forge/context`
- `.forge/context/modes/ai-readiness.md`
- current repository evidence

Use scoped repository loading only.

Do not add repository cognition, orchestration, memory, or duplicated lifecycle semantics here.
