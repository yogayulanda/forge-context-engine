---
id: mode.plan
title: "Mode: Plan"
type: mode
status: confirmed
confidence: high
source: human
evidence: [{ type: doc, ref: ../../../../specs/mode-invocation.md }]
owner: forge-context-engine
updated: 2026-06-04
---

# Mode: Plan

## include
- `knowledge/decisions/`
- `knowledge/assumptions.md`
- `knowledge/unknowns.md`
- `layers/<related>`

## on_demand
- `systems/<related>`
- `knowledge/inferred.md`
- Contracts/events/data/API/runtime/security context when needed for risk or evidence

## exclude
- `systems/<unrelated>`
- `layers/<unrelated>`

## token_budget
5000

## purpose
Convert developer intent into a reviewable Quick Plan or SDD.

## inputs
- Developer intent.
- Relevant `.forge/context`.
- Scoped current repository evidence.
- Risk policy from config.

## behavior
- Choose Quick Plan for small, clear, low-risk work.
- Choose SDD for domain, data, public API, security/auth, database migration, multi-system, high-risk, ambiguous, roadmap, or major architecture work.
- Show selected plan type and reason.
- Preserve evidence, assumptions, unknowns, and decisions needed.
- Do not edit code.

## outputs
Quick Plan:
- Plan type selected: Quick Plan.
- Reason.
- Goal.
- Scope.
- Non-goals.
- Relevant Context / Evidence.
- Likely Changes.
- Risks.
- Validation.
- Next Step.
- Status.

SDD:
- Plan type selected: SDD.
- Reason.
- Goal.
- Problem / Context.
- Requirements.
- Non-goals.
- Current Evidence.
- Assumptions.
- Unknowns / Decisions Needed.
- Architecture / System Impact.
- Risk Areas.
- Proposed Approach.
- MVP Path.
- Full-Version Path.
- Acceptance Criteria.
- Validation Plan.
- Implementation Split.
- Status.

## status values
- `ready_for_implementation`
- `blocked_by_decision`
- `needs_more_evidence`
- `not_recommended`

## boundaries
- Do not edit code.
- Do not produce ECP task instructions.
- Do not treat the plan as approved. Human approval is required before `implementation`.
- Use only the final plan status vocabulary above.

## next mode transitions
- `ready_for_implementation` -> human approval -> `implementation`.
- `blocked_by_decision` -> developer decision.
- `needs_more_evidence` -> scoped evidence gathering or `ask`.
- `not_recommended` -> stop or revise intent.
