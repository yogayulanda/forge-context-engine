# AGENTS.md - Forge Codex Wrapper

Thin Codex-compatible entrypoint.

Read `.forge/adapter.md` and follow it. `.forge/context` remains the curated source of truth.

Codex may receive Forge requests through natural prompts, `$forge-<mode>`, or `/skill forge-<mode>` syntax depending on surface/version. Resolve those invocations to the active Forge core lifecycle or clearly labeled compatibility/scenario guidance.

Keep Codex-specific edit mechanics out of universal artifacts unless they appear under a clearly labeled `Target Tool Notes` section.

Do not store repository cognition, lifecycle logic, validation policy, or artifact policy in this file.
