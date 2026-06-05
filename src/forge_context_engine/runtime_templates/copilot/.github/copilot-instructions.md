# GitHub Copilot Forge Wrapper

Thin GitHub Copilot-compatible entrypoint.

Read `.forge/adapter.md` and follow it. `.forge/context` remains the curated source of truth.

Copilot may receive Forge requests through natural prompts or tool-specific `/forge-<mode>` syntax when available. Resolve those invocations to the active Forge core lifecycle or clearly labeled compatibility/scenario guidance.

Do not store repository cognition, lifecycle logic, validation policy, or artifact policy in this file.
