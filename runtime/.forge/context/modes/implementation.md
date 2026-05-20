---
id: mode.implementation
title: "Mode: Implementation"
type: mode
status: confirmed
confidence: high
source: human
owner: forge-context-engine
updated: 2026-05-20
---

# Mode: Implementation

Prepare context for implementation work: active layers, related systems, ADRs, relevant inferences.

## include *(delta above always-loaded core)*

- `layers/<active>` — layers relevant to the task
- `systems/<related>` — units touched by the task
- `knowledge/decisions/`
- `knowledge/inferred.md`

## on_demand

- `generated/*` — if code maps or summaries are available

## exclude

- `systems/<unrelated>` — all units outside task scope

## token_budget

medium-high
