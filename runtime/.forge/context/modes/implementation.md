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
- Break work into explicit executable tasks with likely files/components, dependency ordering, migration/runtime sequencing when relevant, validation notes, and rollback visibility.
- Do not modify code, redesign architecture, repeat full ECP reasoning, or silently redefine approved plans.
- Load only task-relevant layers, systems, decisions, and inferences; use on-demand context only when task decomposition requires it.
- Keep task scope bounded; do not introduce speculative redesign, ownership, topology, contracts, or behavior not supported by evidence.
- If `runtime.non_interactive: false`, ask execution-blocking decisions before final task breakdown; if `true`, emit a blocked implementation report.
- Continue on labeled proposed defaults only when low-risk, reversible, and non-authoritative; do not promote them into confirmed architecture/runtime behavior.
- Never copy raw secrets from configs, env files, logs, fixtures, docs, or generated output into code or Forge context.
- Report task list, likely files/components, dependencies, loaded context, missing evidence or ambiguity, proposed vs confirmed boundaries, and whether implementation mode was sufficient.
