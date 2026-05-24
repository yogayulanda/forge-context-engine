---
id: mode.testing
title: "Mode: Testing"
type: mode
status: confirmed
confidence: high
source: human
owner: forge-context-engine
updated: 2026-05-24
---

# Mode: Testing

## include

- `layers/testing`
- `systems/<related>`
- `knowledge/assumptions.md`

## on_demand

- `knowledge/decisions/`
- `knowledge/inferred.md`
- `generated/<relevant>`

## exclude

- `systems/<unrelated>`
- `layers/<unrelated>`

## token_budget

6000

## notes

- Define or execute validation strategy for the requested scope.
- Reason about coverage, gaps, assumptions, rollback, regression risk, and operational verification.
- Validate blocking vs proposed-default paths where relevant; verify unresolved proposed defaults remain visible before production finalization.
- Redact credentials, tokens, cookies, private keys, and credential-bearing URLs from test evidence and validation notes.
- Distinguish executed tests, planned tests, inferred confidence, and unresolved unknowns.
- Report validation areas, loaded context, missing evidence or ambiguity, test evidence, and whether testing mode was sufficient.
