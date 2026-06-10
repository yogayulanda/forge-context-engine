# /forge-implementation

Use shared skill:
`.forge/skills/forge-implementation/SKILL.md`

This is a Claude slash-command wrapper for Forge implementation mode.

Implementation mode produces an ECP from an approved plan and must not edit code.

Repository behavior and lifecycle semantics come from:
- `.forge/context`
- `.forge/context/modes/implementation.md`
- current repository evidence

Use scoped repository loading only. Do not add repository cognition, orchestration, memory, or duplicated lifecycle semantics here.
