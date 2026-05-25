---
id: mode.review
title: "Mode: Review"
type: mode
status: confirmed
confidence: high
source: human
evidence: [{ type: doc, ref: ../../../../specs/mode-invocation.md }]
owner: forge-context-engine
updated: 2026-05-25
---
# Mode: Review
## include
- `layers/<related>`
- `knowledge/decisions/`
## on_demand
- `systems/<related>`
- `knowledge/inferred.md`
- `knowledge/assumptions.md`
- `generated/<relevant>`
## exclude
- `systems/<unrelated>`
- `layers/<unrelated>`
## token_budget
6000
## notes
- Act like a senior MR reviewer: answer acceptability, required fixes, risk, reviewer focus, and MR readiness.
- When persistence helps continuity, write or reference a Review Result Artifact with review result, MR readiness, critical/major findings, reviewer focus, rollback/safety notes, and suggested next action.
- Use one result status: `APPROVED`, `NEEDS_CHANGES`, `BLOCKED`, or `PARTIAL_REVIEW`.
- State MR readiness as exactly one of: `MR-ready`, `not MR-ready`, `MR-ready with accepted risk`, or `cannot determine`.
- Group findings by severity: `CRITICAL`, `MAJOR`, `MINOR`, `INFO`; omit empty groups only when saying `Tidak ada temuan`.
- Every `CRITICAL` or `MAJOR` finding must include affected file/area, what is wrong, why it matters, and suggested fix.
- Check execution contract, approved boundaries, topology drift, service/repository boundary bypass, and unapproved contract/schema changes.
- Check relevant safety risks: secret/raw payload logging, PII exposure, retry/DLQ, idempotency, rollback readiness, and validation honesty.
- Check scoped evidence, drift, cross-repo uncertainty, and concise governance risks; use `CONTEXT_BUDGET_LIMITED` with missing evidence and affected readiness, or drift status, instead of approving unsupported scope.
- Treat hidden validation gaps or unsupported production-ready/test-passed claims as review findings without becoming testing mode.
- Keep testing comments as review findings and coverage gaps, not full test plans.
- Use output sections in order: `Review Result`, `MR readiness`, `Critical findings`, `Major findings`, `Minor findings`, `Info / observations`, `Reviewer perlu fokus ke`, `Yang belum tervalidasi`, `Rollback / safety notes`, and `Suggested next action`.
- Keep critique evidence-based; if review evidence is missing, use `BLOCKED` or `PARTIAL_REVIEW` instead of approval.
- Avoid audit/report prose, broad implementation task lists, nitpicking, lifecycle redesign, tooling, agents, CI/CD, deploy workflow, or runtime executor semantics.
