# /forge-update-context

Use shared skill:
`.forge/skills/forge-update-context/SKILL.md`

This is a Claude slash-command wrapper for Forge context refresh.

Update active curated context only under `.forge/context/`. Do not modify application code, `.forge/runtime/`, `.forge/generated/`, `.forge/context-archive/`, `.forge/context-patches/`, or repo entrypoints.

Repository behavior and lifecycle semantics come from:
- `.forge/context`
- `.forge/runtime/modes/update-context.md`
- current repository evidence

Use scoped repository loading only, optimize token usage, and report changed context files plus remaining unknowns.
