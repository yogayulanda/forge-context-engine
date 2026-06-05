---
id: scenario.refactor
title: "Scenario Guidance: Refactor"
type: scenario
status: confirmed
confidence: high
source: human
evidence: [{ type: doc, ref: ../../../../specs/mode-invocation.md }]
owner: forge-context-engine
updated: 2026-06-05
---

# Scenario Guidance: Refactor

`refactor` is not a core lifecycle mode. Use this file only as compatibility, scenario, or historical guidance for behavior-preserving cleanup.

## route through core modes
- Use `plan` to define refactor scope, risk, non-goals, and behavior-preservation evidence.
- Use `implementation` to produce an ECP after plan approval.
- Use `execute` to apply approved refactor tasks and validation.
- Use `review` to inspect behavior preservation, validation, and context impact.

## include
- `layers/<related>`
- `systems/<related>`
- `knowledge/decisions/`

## on_demand
- `knowledge/inferred.md`
- `knowledge/assumptions.md`
- `.forge/generated/<relevant>`
- Tests, coverage, contracts, and call sites needed to prove behavior preservation

## exclude
- `systems/<unrelated>`
- `layers/<unrelated>`

## token_budget
7000

## notes
- Prefer local simplification, duplication removal, naming cleanup, and structure alignment already supported by repo conventions.
- Classify risk as `low`, `medium`, or `high`.
- High-risk refactors require plan and implementation before execute.
- Do not hide behavior changes, architecture rewrites, paradigm migrations, or unrelated cleanup.
