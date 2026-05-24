---
id: mode.execute
title: "Mode: Execute"
type: mode
status: confirmed
confidence: high
source: human
owner: forge-context-engine
updated: 2026-05-24
---

# Mode: Execute
## include
- `layers/<related>`
- `systems/<related>`
- `knowledge/decisions/`
- `knowledge/inferred.md`
## on_demand
- Approved implementation task list or ECP/phases
- `knowledge/assumptions.md`
- `generated/<relevant>`
## exclude
- `systems/<unrelated>`
- `layers/<unrelated>`
## token_budget
8000
## notes
- Implement only approved tasks or approved task subsets using scoped execution context and repository consistency rules.
- Preserve repository conventions, minimize unnecessary changes, and keep proposed vs confirmed boundaries visible.
- Do not perform major architecture redesign, invent topology/contracts, broad-load unrelated context, or silently redefine approved plans.
- If `runtime.non_interactive: false`, ask confirmation before dangerous, destructive, or runtime-impacting changes; if `true`, stop safely and emit a blocked report.
- Run narrow implementation verification when relevant; use testing mode for test strategy, test creation, coverage, mocks/fakes/stubs, and broader regression validation.
- Never copy raw secrets from configs, env files, logs, fixtures, docs, or generated output into code or Forge context.
- Report modified files, task completion status, loaded context, missing evidence or ambiguity, and whether execute mode was sufficient.
