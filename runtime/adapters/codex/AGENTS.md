# Codex Forge Adapter

Codex is skills-first for Forge usage. `AGENTS.md` is the repository-native entrypoint, and Forge requests should resolve to shared skills under `runtime/skills/*/SKILL.md`:

- "Use Forge ask mode to explain this flow."
- "Use Forge planning mode for this change."
- "Use Forge implementation mode to create task cards."
- "Use Forge execute mode for the approved task cards."
- "Use Forge testing mode to validate this change."
- "Use Forge review mode for this MR."
- "Use Forge incident mode for this bug."
- "Use Forge refactor mode for this cleanup."

Codex invocation may be `$forge-review`, `/skill forge-review`, or a natural prompt such as "Use Forge review mode", depending on Codex surface or version. Do not create a parallel Codex command-wrapper layer unless the Codex runtime explicitly requires it later.

## Loading Contract

1. Resolve the requested Forge mode to `runtime/skills/<skill>/SKILL.md`.
2. Follow the skill's load section.
3. Read `.forge/forge.config.yaml` first.
4. Apply `runtime.non_interactive`; respect `runtime.profile`.
5. Load `.forge/context/00-meta/conventions.md`.
6. Use `.forge/context/00-meta/context-manifest.md` as an index, not as repository cognition.
7. Load `.forge/context/modes/<mode>.md`.
8. Load only relevant scoped repository context.

Do not broad-load `.forge/context`.

## Responsibility Chain

```text
tool syntax -> tool UX layer -> adapter -> shared skill -> .forge/context mode -> scoped repository evidence
```

Responsibilities:
- `.forge/context` is the cognition source of truth.
- `runtime/skills/*/SKILL.md` is the reusable Forge workflow behavior layer.
- `runtime/adapters/*` is the tool-specific bridge only.
- `CLAUDE.md` and `AGENTS.md` are entrypoints.

## Skill Map

| Shared skill | Codex intent |
|---|---|
| `forge-ask` | Repository understanding |
| `forge-plan` | ECP/change planning |
| `forge-implement` | Execution task cards |
| `forge-execute` | Bounded code changes |
| `forge-test` | Structured validation |
| `forge-review` | MR-style review |
| `forge-incident` | Diagnosis and mitigation |
| `forge-refactor` | Bounded technical debt work |

## Safety

- Repo and `.forge/context` are higher authority than this adapter or any skill.
- Keep repository-owned cognition out of Codex adapter files.
- Preserve scoped loading, validation honesty, artifact non-authority, and unknown boundaries.
- Stop for HIGH-risk decisions without human approval.
- Do not infer topology, ownership, contracts, or business rules across repositories.
- Do not duplicate lifecycle semantics, governance rules, mode behavior, or repo-specific cognition.
- Do not add orchestration, runtime execution, memory, scheduler, CI/CD, deploy behavior, or autonomous chaining.

For `execute`, require approved task cards or an execution contract. Stop if scope is unclear, and distinguish implementation failures from environment or tooling failures.
