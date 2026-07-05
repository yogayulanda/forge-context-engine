---
id: mode.plan
title: "Mode: Plan"
type: mode
status: confirmed
confidence: high
source: human
evidence: [{ type: doc, ref: ../../../../specs/mode-invocation.md }]
owner: forge-context-engine
updated: 2026-06-05
---

# Mode: Plan

## include
- `knowledge/decisions/`
- `knowledge/assumptions.md`
- `knowledge/unknowns.md`
- `layers/<related>`

## on_demand
- `systems/<related>`
- active `.forge/context/*.md` entries labeled `inferred`
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
- Keep mode boundaries separate from user/request assumptions.
- Preserve evidence, assumptions, unknowns, and decisions needed.
- State assumptions explicitly when the request is ambiguous, even for small changes.
- Keep small-change output concise, but still include acceptance criteria and validation commands.
- Prefer the smallest relevant code surface and evidence set that can support the plan.
- For changes to existing behavior, first map the affected surface area before locking scope: inspect all discoverable call sites, references, entry points, handlers, routes, tests, and configuration touchpoints that materially affect the change.
- Treat scope as incomplete when only a subset of known usages has been inspected and there is evidence of additional references.
- Default to chat output; save a plan artifact only when the user explicitly asks or approves persistence.
- When saving, use `.forge/generated/plans/YYYY-MM-DD-<slug>-plan.md` and avoid overwriting an existing artifact without explicit approval.
- Saved plans are working artifacts only; they are not approved by creation alone and are not durable context.
- Do not edit code.

## outputs
Quick Plan:
- Plan type selected: Quick Plan.
- Reason.
- Mode Boundary.
- Assumptions.
- Goal.
- Scope.
- Non-goals.
- Relevant Context / Evidence.
- Affected Surface Inventory.
- Likely Changes.
- Risks.
- Acceptance Criteria.
- Validation Commands.
- Next Step.
- Status.

SDD:
- Plan type selected: SDD.
- Reason.
- Mode Boundary.
- Goal.
- Problem / Context.
- Requirements.
- Non-goals.
- Current Evidence.
- Affected Surface Inventory.
- Assumptions.
- Unknowns / Decisions Needed.
- Architecture / System Impact.
- Risk Areas.
- Proposed Approach.
- MVP Path.
- Full-Version Path.
- Acceptance Criteria.
- Validation Commands.
- Implementation Split.
- Next Step.
- Status.

## status values
- `ready_for_implementation`
- `blocked_by_decision`
- `needs_more_context`

## boundaries
- Plan mode is read-only.
- No files are edited, staged, committed, pushed, or applied in this mode.
- This mode stops before implementation.
- Do not edit code.
- Do not produce ECP task instructions.
- Do not treat the plan as approved. Human approval is required before `implementation`.
- Use only the final plan status vocabulary above.

## next mode transitions
- `ready_for_implementation` -> human approval -> `implementation`.
- `blocked_by_decision` -> developer decision.
- `needs_more_context` -> scoped evidence gathering or `ask`.
