---
id: scenario.validation
title: "Scenario Guidance: Validation"
type: scenario
status: confirmed
confidence: high
source: human
evidence: [{ type: doc, ref: ../../../../specs/mode-invocation.md }]
owner: forge-context-engine
updated: 2026-06-05
---

# Scenario Guidance: Validation

`testing` is not a core lifecycle mode. Use this file only as compatibility, scenario, or historical guidance for validation-focused work.

## route through core modes
- Use `execute` for scoped per-task validation, final validation, and in-scope validation fixes.
- Use `review` to inspect validation evidence, validation gaps, risk, and MR readiness.
- Use `plan` when validation scope requires a new decision or broader strategy.

## include
- `layers/testing`
- `systems/<related>`
- `knowledge/assumptions.md`

## on_demand
- `layers/<related>`
- `knowledge/decisions/`
- active `.forge/context/*.md` entries labeled `inferred`
- `.forge/generated/<relevant>`

## exclude
- `systems/<unrelated>`
- `layers/<unrelated>`

## token_budget
6000

## notes
- Validation reports use `passed`, `failed`, `partial`, `blocked_by_environment`, or `not_run` when validation is requested.
- Separate scoped validation, final validation, manual checks, environment blockers, coverage gaps, and risks.
- Do not imply full validation without evidence.
- Do not become planning, execution beyond approved scope, review approval, or redesign.
