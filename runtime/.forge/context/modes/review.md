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
- `01-core/constraints.md` — when review touches validation, security, or compliance code paths

## exclude

- `knowledge/assumptions.md` — review is fact-based, not assumption-based

## audit focus *(v0.2.1)*

When reviewing context (not code), apply:
- Evidence consistency sweep (J-rules)
- Phantom ADR check (K1, K2)
- Validation layer attribution (J10–J13) — required-fields claims must match actual service-layer empty-checks
- Drift detection (K3) — `evidence: ref` paths still exist and unchanged

## token_budget

medium
