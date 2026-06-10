# Cursor Adapter

Cursor compatibility uses thin rules or prompts that point to Forge.

## Responsibility

- Point Cursor to `.forge/forge.config.yaml`.
- Point Cursor rules or prompts to shared skills under `.forge/skills/`.
- Let each shared skill invoke `.forge/context/modes/<mode>.md`.
- Keep Cursor rules portable and non-authoritative.

## Boundary

Cursor rules must not store repository intelligence or duplicate Forge lifecycle, governance, runtime, or artifact semantics.

If Cursor-specific syntax is added later, it must remain a wrapper around shared Forge skills.
