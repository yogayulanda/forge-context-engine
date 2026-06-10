# AGENTS.md - Forge AGENTS-Compatible Wrapper

Thin AGENTS.md-compatible entrypoint.

Read `.forge/adapter.md` and follow it. `.forge/context` remains the curated source of truth.

Tools that read `AGENTS.md`, including Codex-compatible and OpenCode surfaces, may receive Forge requests through natural prompts, `$forge-<mode>`, or `/skill forge-<mode>` syntax depending on surface/version. Resolve those invocations to the active Forge core lifecycle or clearly labeled compatibility/scenario guidance.

Keep tool-specific edit mechanics out of universal artifacts unless they appear under a clearly labeled `Target Tool Notes` section.

Do not store repository cognition, lifecycle logic, validation policy, or artifact policy in this file.
