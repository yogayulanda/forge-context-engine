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
- active `.forge/context/*.md` entries labeled `inferred`

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
- If the user references a saved plan artifact, read it first and verify it is a plan artifact before continuing.
- Check whether the saved plan still has enough evidence and whether current repository/context evidence materially contradicts it; if so, stop with `needs_more_evidence` or `blocked_by_decision`.
- Produce a bounded, tool-ready ECP.
- Convert the approved plan into a readiness package only; do not execute it.
- Keep mode boundaries separate from assumptions carried into the ECP.
- Resolve only execution packaging details that are safe and evidenced.
- Keep universal edit guidance tool-aware: use the smallest safe edit mechanism available in the target tool, then add tool-specific notes only as sub-guidance.
- Default to chat output; save an ECP artifact only when the user explicitly asks or approves persistence.
- When saving, use `.forge/generated/ecp/YYYY-MM-DD-<slug>-ecp.md` and avoid overwriting an existing artifact without explicit approval.
- Do not silently widen scope beyond the approved plan or saved plan artifact.
- Stop if required domain, security, architecture, contract, data, or migration decisions are missing.

## outputs
Execution Context Package (ECP) with:
- Goal.
- Approved scope.
- Non-goals.
- Mode Boundary.
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
- Target Tool Instructions:
  - Use the smallest safe edit mechanism available in the target tool.
  - For Codex, prefer `apply_patch` for scoped edits.
  - For Claude Code, use its normal file-edit workflow while preserving approved scope.
  - For Copilot, produce the smallest reviewable patch or task guidance according to the active Copilot workflow.
  - Do not widen scope beyond the approved ECP.
  - Do not commit or push unless explicitly requested by the human.

## status values
- `ecp_ready`
- `blocked_by_decision`
- `needs_more_evidence`
- `needs_plan_approval`

## boundaries
- Implementation mode produces an ECP/readiness package only.
- It does not edit files, stage, commit, push, or apply changes.
- Execution requires explicit approval and `execute` mode.
- Do not edit code, stage, commit, push, merge, deploy, or apply changes.
- Do not silently redefine the approved plan.
- Do not produce execution instructions while critical blockers remain.

## next mode transitions
- Use `execute` only after human approval of the ECP.
- Return to `plan` when the approved plan is insufficient or contradicted by evidence.
