---
id: mode.review
title: "Mode: Review"
type: mode
status: confirmed
confidence: high
source: human
owner: forge-context-engine
updated: 2026-05-20
---

# Mode: Review

Prepare context for review work: principles, security, related layers, ADRs as guardrails.

## include *(delta above always-loaded core)*

- `layers/<related>` — layers from the review area
- `knowledge/decisions/`

## on_demand

- `layers/security` *(Advanced tier)*
- `systems/<related>` — when review touches a specific unit
- `knowledge/inferred.md`

## exclude

- `knowledge/assumptions.md` — review is fact-based, not assumption-based

## token_budget

medium
