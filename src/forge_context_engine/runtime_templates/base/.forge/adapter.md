---
id: meta.adapter
title: Shared Adapter Entry
type: meta
status: confirmed
confidence: high
source: human
evidence: [{ type: doc, ref: ../../../specs/adapter-command-foundation.md }]
owner: forge-context-engine
updated: 2026-06-05
---

# Shared Adapter Entry

Thin adapter contract for target-repository entrypoints such as `AGENTS.md`, `CLAUDE.md`, and optional `.github/copilot-instructions.md`.

## Adapter parity rules

- All tools must honor Forge lifecycle mode boundaries.
- All tools must load context selectively.
- All tools must treat `.forge/context` as the curated source of truth.
- All tools must treat `.forge/generated/...` as working artifacts, not context.
- All tools must treat `.forge/context-patches/...` as proposals only until reviewed and promoted.
- Tool-specific edit mechanics belong in tool wrappers or a clearly labeled `Target Tool Notes` section, not in universal lifecycle artifacts.
- Universal Plan, ECP, Execution Report, and Review artifacts stay tool-neutral unless explicitly targeted.
- Commit, push, merge, and similar repository publication actions remain human-controlled unless explicitly requested.

## Core lifecycle

Use only these active core modes:

```text
init -> ask -> plan -> implementation -> execute -> review
verify-context | update-context
```

- `plan` creates a reviewable plan or SDD and does not edit code.
- `plan` is read-only by definition; users do not need to append "Do not edit files" in normal usage.
- Gate 1 = human approval from `plan` to `implementation`.
- `implementation` creates an ECP/readiness package and does not edit code.
- `implementation` is read-only by definition; users do not need to append "Do not edit files" in normal usage.
- Gate 2 = human approval from ECP to `execute`.
- `execute` applies only an approved ECP within bounded scope and reports validation honestly.
- `review` checks correctness, validation evidence, security, and context impact.
- `review` is read-only by default; fixes require a separately approved execution flow.
- `verify-context` checks `.forge/context` health only.
- `update-context` refreshes active curated context under `.forge/context/` only.

Legacy names such as `planning`, `testing`, `incident`, and `refactor` are not active core modes. If present, they are legacy aliases or scenario guidance only.

## Bootstrap

1. Read `.forge/forge.config.yaml`.
2. Apply `run.interaction`, `workflow.default_mode`, and `policy.require_human_confirmation_for`.
3. Resolve the requested core mode or compatibility/scenario guidance and read only that contract file.
4. Read `.forge/runtime/meta/conventions.md` when task behavior, output shape, evidence handling, validation reporting, risk boundaries, or language rules need it.
5. Load scoped convention files only when relevant to the task category.
6. Use `.forge/runtime/meta/context-manifest.md` only as a routing index when navigation help is needed.
7. If `.forge/workspace.yaml` exists, treat it as a thin coordination layer for cross-repo planning only; it does not replace service-repo context.
8. Load only the smallest relevant repository evidence and scoped `.forge/context` needed for the task.

Do not broad-load `.forge/context`, do not load every mode file by default, and do not load compatibility/scenario files unless the request or evidence makes them relevant. For small plans, inspect the smallest relevant code surface first. If context remains insufficient, state what is missing instead of reading everything.

Workspace loading rule:
- Start from the current repo context for repo-scoped work.
- Load workspace context only when the task spans multiple repos/services, integration boundaries, ownership, dependency flow, or cross-repo planning.
- When workspace context is relevant, load the workspace summary first and then only the linked services needed for the current task.
- Do not treat workspace context as authority for service-specific implementation details; read that service repo's own `.forge/context` when deeper facts are needed.
- When making a cross-repo claim, cite which repo or workspace context source the claim came from.

Normal prompt UX:
- Use: `Use Forge plan mode for adding a small health check function.`
- Not required: `Use Forge plan mode for adding a small health check function. Do not edit files.`
- The second form is allowed as a safety probe, but read-only core modes already carry their own no-edit boundary.

## Source of truth

- `.forge/context` is the committed curated source of truth.
- `.forge/context-patches` contains reviewable context update proposals.
- `.forge/generated` contains generated working artifacts only.
- Saved artifact directories are `.forge/generated/plans/`, `.forge/generated/ecp/`, `.forge/generated/reports/`, and `.forge/generated/reviews/`.
- Save artifacts only when requested or approved. Default behavior is chat output first.
- Continue from a saved artifact only after reading it, verifying type-to-mode fit, and checking for stale or contradictory evidence.
- `.forge/temp` and `.forge/cache` are local-only and must not be pushed.
- Adapters are entrypoints only. They do not own lifecycle, policy, validation, artifact, or repository-cognition semantics.

Artifact boundary rules:
- Universal artifacts must not say things like `Use apply_patch`, `Use Codex`, or `Run Claude tool X` unless the artifact is explicitly target-tool-specific.
- When tool-specific guidance is useful inside a universal artifact, isolate it under a clearly labeled `Target Tool Notes` section.
- `Target Tool Notes` may contain concise tool-specific hints, but the approved scope, task sequence, safety constraints, and validation expectations remain universal.

Artifact continuation examples:

```text
Use Forge implementation mode from .forge/generated/plans/2026-06-05-add-export-plan.md
Use Forge execute mode from .forge/generated/ecp/2026-06-05-add-export-ecp.md
Use Forge review mode from .forge/generated/reports/2026-06-05-add-export-execution-report.md
```

Continuation guardrails:
- Read the referenced artifact first.
- Verify the artifact type matches the requested lifecycle mode.
- Verify the artifact still has enough scope, evidence, and approval state for safe continuation.
- Check for material drift when repository or context evidence contradicts the artifact.
- Do not execute from a plan artifact directly.
- Do not mutate `.forge/context` based only on generated artifact content.

## Cross-tool output expectations

Keep lifecycle artifacts concise. Minimum common shape:

- Plan: `Mode Boundary`, `Assumptions`, `Goal / Scope / Non-goals`, `Evidence`, `Risks`, `Acceptance Criteria`, `Validation Commands`, `Next Step`, `Status`
- ECP: `Approved Scope`, `Files likely to change`, `Task sequence`, `Coding rules`, `Safety constraints`, `Validation commands`, `Stop conditions`, `Expected execution report`, `Status`
- Execution Report: `Changed files`, `What changed`, `Validation run`, `Deviations`, `Remaining risks`, `Status`
- Review: `Verdict`, `Diff Reviewed`, `Findings`, `Validation assessment`, `Context Impact`, `Recommended next step`, `Status`

Tool wrappers may add invocation hints, but they must not redefine these lifecycle expectations or expand them into tool-specific schemas.

## Target repo surface

Default target-repo output:

```text
AGENTS.md
CLAUDE.md
.forge/
```

Optional when GitHub Copilot is selected:

```text
.github/copilot-instructions.md
```

Do not copy engine-only folders such as `docs/`, `specs/`, `validation-cases/`, or `runtime/adapters/` into every target repository.
