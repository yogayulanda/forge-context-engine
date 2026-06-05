---
id: mode.implementation
title: "Mode: Implementation"
type: mode
status: confirmed
confidence: high
source: human
evidence: [{ type: doc, ref: ../../../../specs/mode-invocation.md }]
owner: forge-context-engine
updated: 2026-06-04
---

# Mode: Implementation

## include
- `layers/<related>`
- `systems/<related>`
- `knowledge/decisions/`
- `knowledge/inferred.md`

## on_demand
- Approved plan or SDD
- `knowledge/assumptions.md`
- `.forge/generated/<relevant>`

## exclude
- `systems/<unrelated>`
- `layers/<unrelated>`

## token_budget
8000

## purpose
Convert an approved plan into an Execution Context Package (ECP).

## inputs
- Approved plan with `status: ready_for_implementation`.
- Relevant `.forge/context`.
- Target adapter/tool.
- Validation commands.
- Risk policy and stop conditions.

## behavior
- Verify the plan is approved before generating execution instructions.
- Produce a bounded, tool-ready ECP.
- Resolve only execution packaging details that are safe and evidenced.
- Stop if required domain, security, architecture, contract, data, or migration decisions are missing.

## outputs
Execution Context Package (ECP) with:
- Goal.
- Approved scope.
- Non-goals.
- Relevant context.
- Relevant evidence.
- Allowed files / likely files.
- Task sequence.
- Step-by-step implementation guidance.
- Coding rules.
- Security constraints.
- Validation checklist.
- Acceptance criteria.
- Risk notes.
- Stop conditions.
- Expected execution report format.
- Target tool instructions.

## status values
- `ecp_ready`
- `blocked_by_decision`
- `needs_more_evidence`
- `needs_plan_approval`

## boundaries
- Do not edit code, commit, push, merge, deploy, or apply changes.
- Do not silently redefine the approved plan.
- Do not produce execution instructions while critical blockers remain.

## next mode transitions
- Use `execute` only after human approval of the ECP.
- Return to `plan` when the approved plan is insufficient or contradicted by evidence.
