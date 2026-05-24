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
- `layers/<related>`
- `knowledge/decisions/`
- `knowledge/inferred.md`
- `generated/<relevant>`
## exclude
- `systems/<unrelated>`
- `layers/<unrelated>`
## token_budget
6000
## notes
- Define or implement task-scoped unit, integration, regression, coverage, and operational verification tests.
- Follow existing repo test placement conventions when clear; report the detected convention instead of forcing a new layout.
- If no convention exists, colocate unit tests near target packages/files and place non-unit tests under `testing/integration`, `testing/e2e`, `testing/mocks`, `testing/fixtures`, or `testing/helpers` as appropriate.
- Keep unit, integration, e2e, mocks, fakes, stubs, fixtures, and helpers distinct; avoid mixing unrelated test concerns in one folder without reason.
- Reason about test isolation, mocks/fakes/stubs, fixtures, helpers, test dependencies, retry/error paths, rollback paths, and missing coverage.
- Do not become generic architecture planning, review mode, or broad implementation redesign.
- Redact credentials, tokens, cookies, private keys, and credential-bearing URLs from test evidence and validation notes.
- Report test strategy or test changes, loaded context, missing evidence or ambiguity, commands run or skipped, and whether testing mode was sufficient.
