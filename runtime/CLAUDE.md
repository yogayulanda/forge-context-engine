# CLAUDE.md - Forge Claude Adapter

Thin Claude entrypoint for Forge repositories. This file stores no repository cognition and defines no independent runtime behavior; `.forge/context` and `specs/*` remain the source of truth.

## Bootstrap

1. Read `.forge/forge.config.yaml` first.
2. Apply `run.interaction` and related final run config fields.
3. Read `.forge/context/00-meta/context-manifest.md` as the routing index.
4. Follow `.forge/context/00-meta/conventions.md` as the normative operational contract.
5. Treat `00-meta/*` and `01-core/*` as always-loaded core.
6. Read the requested mode file from `.forge/context/modes/<mode>.md`.
7. Load only task-relevant context from that mode's `include`, `on_demand`, `exclude`, `token_budget`, and notes.

Keep bootstrap details quiet in normal replies. When useful, say only `Scoped context loaded` plus the few areas that affected the answer.

## Skill Entry

Claude slash commands and natural language requests invoke shared Forge skills, which then invoke Forge modes: `init`, `ask`, `plan`, `implementation`, `execute`, `review`, and `verify-context`.

Shared skills live under `skills/<skill>/SKILL.md`: `forge-init`, `forge-ask`, `forge-plan`, `forge-implementation`, `forge-execute`, `forge-review`, and `forge-verify-context`.

Scenario compatibility skills such as `forge-test`, `forge-incident`, and `forge-refactor` route validation, incident, or refactor requests through the core lifecycle. They are not core modes.

Materialized slash command wrappers live under `adapters/claude/commands/` and map to those skills. They are invocation helpers only.

## Claude Hints

- Preserve evidence, inference, assumption, proposed-default, and unknown boundaries from Forge core.
- Redact secrets before output or context writes.
- Keep responses concise, operational, repository-native, and aligned to the active mode.
- Prefer targeted context expansion over broad-loading `.forge/context`.
- If required evidence is missing, report the blocker or scoped expansion need instead of guessing.

## Source Of Truth

Reference Forge core instead of duplicating it:

- `.forge/context/00-meta/conventions.md` for runtime behavior and governance.
- `.forge/context/modes/<mode>.md` for mode behavior and scoped loading.
- `specs/mode-invocation.md`, `specs/context-validation.md`, `specs/framework-lifecycle.md`, `specs/artifact-lifecycle.md`, and `specs/adapter-command-foundation.md` for normative lifecycle, validation, artifact, and adapter rules.

`AGENTS.md` is the universal sibling adapter for Codex-compatible assistants. Tool-specific adapter notes may live under `adapters/<tool>/`. Shared skills live under `skills/`. Adapters and skills never replace `.forge/context` or specs.
