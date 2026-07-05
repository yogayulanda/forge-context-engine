# GitHub Copilot Adapter

GitHub Copilot enters Forge through repository instructions plus repo-local Forge skill exports.

Copilot support is opt-in. Default target-repo output includes `AGENTS.md`, `.github/copilot-instructions.md`, `.github/skills/**/SKILL.md`, and `.forge/skills/**/SKILL.md`. Claude files remain optional and are installed only when Claude is selected.

## How Invocation Works

Common invocation style:

```text
Use Forge ask mode
/forge-plan
/forge-review
/forge-ai-readiness
```

The expected path is:

```text
Copilot instruction surface -> .github/skills/<skill>/SKILL.md -> shared Forge mode -> scoped repository evidence
```

Runtime adapter files live under:

```text
runtime/.github/copilot-instructions.md
runtime/skills/
```

When materialized into a target repository, `.github/copilot-instructions.md` and `.github/skills/**/SKILL.md` are created only when that repository selects Copilot. Legacy `.github/prompts/**` wrappers are obsolete and are not current output.

## What The Adapter Does

The Copilot adapter:

- explains how Copilot invokes Forge modes
- maps Copilot usage to shared repo-local skills
- reminds Copilot to load scoped context
- keeps `.forge/context` authoritative

Copilot instructions stay thin. Repo-local skill exports should point to canonical Forge skills instead of copying full mode behavior.

## Expected Usage Style

Use focused prompts:

```text
/forge-plan
Plan a bounded retry improvement for this consumer.
Preserve the event schema and list validation needed.
```

```text
/forge-review
Review this MR for correctness, validation honesty, and rollback readiness.
```

```text
/forge-ai-readiness
Audit whether this repository is ready for safe AI-assisted changes.
```

## Boundaries

The Copilot adapter must not:

- contain repo-specific cognition
- duplicate Forge mode semantics
- create tool-specific orchestration
- imply command chaining
- define execution triggers or scheduler behavior

The same prompt should produce different answers in different repositories only because local `.forge/context` and repository evidence differ.
