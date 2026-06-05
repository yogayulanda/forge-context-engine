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

## Core lifecycle

Use only these active core modes:

```text
init -> ask -> plan -> implementation -> execute -> review -> verify-context
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

Legacy names such as `planning`, `testing`, `incident`, and `refactor` are not active core modes. If present, they are legacy aliases or scenario guidance only.

## Bootstrap

1. Read `.forge/forge.config.yaml`.
2. Apply `run.interaction`, `workflow.default_mode`, and `policy.require_human_confirmation_for`.
3. Resolve the requested core mode or compatibility/scenario guidance and read only that contract file.
4. Read `.forge/context/00-meta/conventions.md` when task behavior, output shape, evidence handling, validation reporting, risk boundaries, or language rules need it.
5. Load scoped convention files only when relevant to the task category.
6. Use `.forge/context/00-meta/context-manifest.md` only as a routing index when navigation help is needed.
7. Load only the smallest relevant repository evidence and scoped `.forge/context` needed for the task.

Do not broad-load `.forge/context`, do not load every mode file by default, and do not load compatibility/scenario files unless the request or evidence makes them relevant. For small plans, inspect the smallest relevant code surface first. If context remains insufficient, state what is missing instead of reading everything.

Normal prompt UX:
- Use: `Use Forge plan mode for adding a small health check function.`
- Not required: `Use Forge plan mode for adding a small health check function. Do not edit files.`
- The second form is allowed as a safety probe, but read-only core modes already carry their own no-edit boundary.

## Source of truth

- `.forge/context` is the committed curated source of truth.
- `.forge/context-patches` contains reviewable context update proposals.
- `.forge/generated` contains generated artifacts only.
- `.forge/temp` and `.forge/cache` are local-only and must not be pushed.
- Adapters are entrypoints only. They do not own lifecycle, policy, validation, artifact, or repository-cognition semantics.

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

Do not copy engine-only folders such as `docs/`, `specs/`, `validation-cases/`, `runtime/adapters/`, or `runtime/skills/` into every target repository.
