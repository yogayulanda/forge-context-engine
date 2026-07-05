# AGENTS.md - Forge AGENTS-Compatible Wrapper

Thin AGENTS.md-compatible entrypoint.

Read `.forge/adapter.md` and follow it. `.forge/context/` is the active curated repository context.

Tools that read `AGENTS.md`, including Codex-compatible, Copilot-compatible, and OpenCode-compatible surfaces, may receive Forge requests through natural prompts or tool-specific syntax depending on surface/version. Resolve those invocations through `.forge/adapter.md` and the installed Forge skills/modes.

Keep tool-specific edit mechanics out of universal artifacts unless they appear under a clearly labeled `Target Tool Notes` section.

Do not store repository cognition, lifecycle logic, validation policy, or artifact policy in this file.
