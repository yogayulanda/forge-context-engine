# Adapter Onboarding

Forge adapters are thin invocation bridges for AI tools.

Start with the adapter for your tool:

| Tool | Doc |
|---|---|
| Claude | [claude.md](claude.md) |
| Codex | [codex.md](codex.md) |
| GitHub Copilot | [github-copilot.md](github-copilot.md) |
| OpenCode | [opencode.md](opencode.md) |

Adapter rule:

```text
tool syntax -> tool UX layer -> adapter -> shared skill -> .forge/context mode -> scoped repository evidence
```

Adapters do not store repository cognition, define lifecycle semantics, or add runtime behavior. They reduce invocation friction only.
