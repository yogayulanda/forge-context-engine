# Codex Forge Adapter

Codex is skills-first for Forge usage. `AGENTS.md` is the repository-native entrypoint, and Forge requests should resolve to shared skills under `runtime/skills/*/SKILL.md`.

Core examples:
- "Use Forge init mode to initialize context."
- "Use Forge ask mode to explain this flow."
- "Use Forge plan mode for this change."
- "Use Forge implementation mode to create an ECP."
- "Use Forge execute mode for the approved ECP."
- "Use Forge review mode for this MR."
- "Use Forge ai-readiness mode to audit this repo before trusting larger AI changes."
- "Use Forge verify-context mode to check context freshness."

Scenario compatibility examples:
- "Use Forge test scenario guidance to validate this change."
- "Use Forge incident scenario guidance for this bug."
- "Use Forge refactor scenario guidance for this cleanup."

Codex invocation may be `$forge-review`, `/skill forge-review`, or a natural prompt such as "Use Forge review mode", depending on Codex surface or version. Do not create a parallel Codex command-wrapper layer unless the Codex runtime explicitly requires it later.

Normal read-only UX:
- `plan`, `implementation`, and `review` already carry their own no-edit boundary.
- Users do not need to append `Do not edit files` for those modes in normal usage.
- `Do not edit files` remains allowed as an explicit safety probe.

## Loading Contract

1. Resolve the requested Forge mode to `runtime/skills/<skill>/SKILL.md`.
2. Follow the skill's load section.
3. Read `.forge/forge.config.yaml` first.
4. Apply `run.interaction` and related final run config fields.
5. Load `.forge/context/00-meta/conventions.md`.
6. Use `.forge/context/00-meta/context-manifest.md` as an index, not as repository cognition.
7. Load `.forge/context/modes/<mode>.md`.
8. Load only relevant scoped repository context.

Do not broad-load `.forge/context`.

## Skill Map

| Shared skill | Codex intent |
|---|---|
| `forge-init` | Repository context/config initialization |
| `forge-ask` | Repository understanding |
| `forge-plan` | Quick Plan or SDD |
| `forge-implementation` | ECP generation |
| `forge-execute` | Approved ECP execution |
| `forge-review` | Executed-result review |
| `forge-ai-readiness` | Repository AI-readiness audit |
| `forge-verify-context` | Context health/freshness only |
| `forge-test` | Scenario compatibility: validation guidance |
| `forge-incident` | Scenario compatibility: diagnosis |
| `forge-refactor` | Scenario compatibility: behavior-preserving cleanup |

## Safety

- Repo and `.forge/context` are higher authority than this adapter or any skill.
- Keep repository-owned cognition out of Codex adapter files.
- Preserve scoped loading, validation honesty, artifact non-authority, and unknown boundaries.
- Stop for policy/high-risk decisions without human approval.
- Do not infer topology, ownership, contracts, or business rules across repositories.
- Do not duplicate lifecycle semantics, governance rules, mode behavior, or repo-specific cognition.
- Do not add orchestration, runtime execution, memory, scheduler, CI/CD, deploy behavior, or autonomous chaining.

For `execute`, require an approved ECP. Stop if scope is unclear, and distinguish implementation failures from environment or tooling failures.
