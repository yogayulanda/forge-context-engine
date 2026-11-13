# /forge-orchestrate

Use shared skill:
`.forge/skills/forge-orchestrate/SKILL.md`

This is a Claude slash-command wrapper for Forge orchestrate mode.

Focus on:
- One request per invocation: `/forge-orchestrate [--as backend,security] <request or saved plan path>`.
- Claude Code subagents from `.claude/agents/forge-planner.md`, `forge-executor.md`, `forge-tester.md`, and `forge-reviewer.md` when `run.worker: subagent`.
- A fresh tester and reviewer subagent on every round.
- Stop and report on the stop conditions in the mode file.

Repository behavior and lifecycle semantics come from:
- `.forge/context`
- `.forge/runtime/modes/orchestrate.md`
- current repository evidence

Do not add repository cognition, duplicated lifecycle semantics, merge, tag, deploy, or CI/CD behavior here.
