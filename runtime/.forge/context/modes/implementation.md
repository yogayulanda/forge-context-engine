---
id: mode.implementation
title: "Mode: Implementation"
type: mode
status: confirmed
confidence: high
source: human
evidence: [{ type: doc, ref: ../../../../specs/mode-invocation.md }]
owner: forge-context-engine
updated: 2026-06-05
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
- Convert the approved plan into a readiness package only; do not execute it.
- Resolve only execution packaging details that are safe and evidenced.
- Stop if required domain, security, architecture, contract, data, or migration decisions are missing.

## outputs
Execution Context Package (ECP) with:
- Goal.
- Approved scope.
- Non-goals.
- Assumptions.
- Relevant context.
- Relevant evidence.
- Exact files likely to change.
- Task sequence.
- Coding rules.
- Safety / security constraints.
- Acceptance criteria.
- Validation commands.
- Stop conditions.
- Expected execution report format.
- Status.
- Step-by-step implementation guidance only inside the approved file/scope boundary.
- Risk notes.
- Target tool instructions when adapter-specific instructions are necessary.

## status values
- `ecp_ready`
- `blocked_by_decision`
- `needs_more_evidence`
- `needs_plan_approval`

## boundaries
- Do not edit code, stage, commit, push, merge, deploy, or apply changes.
- Do not silently redefine the approved plan.
- Do not produce execution instructions while critical blockers remain.

## next mode transitions
- Use `execute` only after human approval of the ECP.
- Return to `plan` when the approved plan is insufficient or contradicted by evidence.
