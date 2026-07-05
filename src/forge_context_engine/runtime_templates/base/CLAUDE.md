# CLAUDE.md - Forge Claude Wrapper

Thin Claude-compatible entrypoint.

Read `.forge/adapter.md` and follow it. `.forge/context/` is the active curated repository context.

Claude may receive Forge requests through natural prompts or `/forge-<mode>` slash commands when available. Resolve those invocations through `.forge/adapter.md`, `.forge/runtime/`, and the installed Forge skills.

Keep Claude-specific mechanics in `.claude/commands/` or clearly labeled `Target Tool Notes`.

Do not store repository cognition, lifecycle logic, validation policy, or artifact policy in this file.
