---
id: mode.planning
title: "Mode: Planning"
type: mode
status: confirmed
confidence: high
source: human
owner: forge-context-engine
updated: 2026-05-20
---

# Mode: Planning

Prepare context for planning work: map intent, gaps, and assumptions before implementation.

## include *(delta above always-loaded core)*

- `knowledge/decisions/`
- `knowledge/assumptions.md`
- `knowledge/unknowns.md`
- `layers/*` summaries (README placeholders or relevant summaries)

## on_demand

- `systems/<unit>` — when planning touches a specific unit

## exclude

- `knowledge/inferred.md` *(unless explicitly needed)*

## token_budget

medium
