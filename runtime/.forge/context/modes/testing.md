---
id: mode.testing
title: "Mode: Testing"
type: mode
status: confirmed
confidence: high
source: human
owner: forge-context-engine
updated: 2026-05-20
---

# Mode: Testing

Prepare context for testing work: testing strategy, related systems, assumptions to validate.

## include *(delta above always-loaded core)*

- `layers/testing`
- `systems/<related>` — units under test
- `knowledge/assumptions.md`

## on_demand

- `knowledge/decisions/` — when tests are tied to specific decisions
- `knowledge/inferred.md`

## exclude

- `layers/<unrelated>` — layers outside testing focus

## token_budget

medium
