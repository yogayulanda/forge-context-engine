---
id: mode.implementation
title: "Mode: Implementation"
type: mode
status: confirmed
confidence: high
source: human
owner: forge-context-engine
updated: 2026-05-24
---

# Mode: Implementation
## include
- `layers/<related>`
- `systems/<related>`
- `knowledge/decisions/`
- `knowledge/inferred.md`
## on_demand
- `knowledge/assumptions.md`
- `generated/<relevant>`
## exclude
- `systems/<unrelated>`
- `layers/<unrelated>`
## token_budget
8000
## notes
- Convert an approved ECP, approved phases, or simple request into a human-reviewable engineering task breakdown.
- Use clarification phase before execution-ready phase: resolve blocking decisions before final executable tasks.
- In interactive repos, stop before final breakdown when blockers affect runtime, contracts, DLQ/replay, idempotency, security/compliance, ownership/governance, destructive boundaries, acceptance criteria, or rollback; output `NEEDS_CONFIRMATION`.
- For each interactive blocker, show title, Recommended option with reason, Alternative option with tradeoff, and reply instructions: `1 = Recommended`, `2 = Alternative`, `custom = provide explicit value`; use 2 options by default, 3 only for major architecture tradeoffs.
- In non-interactive repos, do not ask questions; emit `BLOCKED`, `NEEDS_CONFIRMATION`, or `NEEDS_REVIEW` and continue only with allowed proposed defaults.
- After blockers are resolved, break work into explicit executable tasks with likely files/components, dependency ordering, migration/runtime sequencing when relevant, validation notes, and rollback visibility.
- Readiness status is required: `NEEDS_CONFIRMATION` for missing blockers/values, `READY_FOR_PARTIAL_EXECUTION` for safe scaffolding only, `READY_FOR_EXECUTION` only when required execution values are concrete.
- For execution-sensitive changes, include `Execution Values` before `READY_FOR_EXECUTION`; do not use `READY_FOR_EXECUTION` with conditional or unavailable values.
- Do not modify code, redesign architecture, repeat full ECP reasoning, or silently redefine approved plans.
- Load only task-relevant layers, systems, decisions, and inferences; use on-demand context only when task decomposition requires it.
- Keep task scope bounded; do not introduce speculative redesign, ownership, topology, contracts, or behavior not supported by evidence.
- Continue on labeled proposed defaults only when low-risk, reversible, and non-authoritative; do not promote them into confirmed architecture/runtime behavior.
- Never copy raw secrets from configs, env files, logs, fixtures, docs, or generated output into code or Forge context.
- Report task list, likely files/components, dependencies, loaded context, missing evidence or ambiguity, proposed vs confirmed boundaries, and whether implementation mode was sufficient.
