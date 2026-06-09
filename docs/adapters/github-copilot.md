# GitHub Copilot Adapter

GitHub Copilot enters Forge through Copilot instructions and prompt files that resolve to shared Forge skills.

Copilot support is opt-in. Default target-repo output stays `AGENTS.md`, `CLAUDE.md`, and `.forge/` unless the repository explicitly selects Copilot.

## How Invocation Works

Common prompt-file style:

```text
/forge-ask
/forge-plan
/forge-review
/forge-ai-readiness
```

The expected path is:

```text
Copilot prompt -> prompt wrapper -> shared skill -> .forge/context mode -> scoped repository evidence
```

Runtime adapter files live under:

```text
runtime/.github/copilot-instructions.md
runtime/adapters/copilot/prompts/
```

When materialized into a target repository, `.github/copilot-instructions.md` and prompt wrappers can live under `.github/` only if that repository uses Copilot prompt files.

## What The Adapter Does

The Copilot adapter:

- explains how Copilot invokes Forge modes
- maps prompt files to shared skills
- reminds Copilot to load scoped context
- keeps `.forge/context` authoritative

Prompt wrappers are thin. They should point to shared skills instead of copying full mode behavior.

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
