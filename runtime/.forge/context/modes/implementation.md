---
id: mode.implementation
title: "Mode: Implementation"
type: mode
status: confirmed
confidence: high
source: human
evidence: [{ type: doc, ref: ../../../../specs/mode-invocation.md }]
owner: forge-context-engine
updated: 2026-05-25
---
# Mode: Implementation
## include
- `layers/<related>`
- `systems/<related>`
- `knowledge/decisions/`
- `knowledge/inferred.md`
## on_demand
- `knowledge/assumptions.md`
- `generated/<relevant>`
## exclude
- `systems/<unrelated>`
- `layers/<unrelated>`
## token_budget
8000
## notes
- Convert an approved ECP, approved phases, or simple request into a task breakdown humans can execute or review.
- When persistence helps continuity, write or reference an Execution Contract Artifact with readiness status, task cards, dependency order, stop conditions, do-not-change boundaries, acceptance criteria, and ECP reference.
- If blockers affect runtime, contracts/schema, DLQ/replay, idempotency, security/compliance, ownership, destructive changes, acceptance criteria, or rollback, stop with `NEEDS_CONFIRMATION`.
- `NEEDS_CONFIRMATION` must lead with blocker(s), explain execution impact briefly, then show `Recommended`, `Alternative`, and reply instructions: `1`, `2`, or concrete custom value.
- For multiple blockers, use numbered blocker lines with one-line impact; avoid long defensive prose before the recommendation.
- Use concrete labels such as `Format event Kafka yang akan diterima service` or `Nilai runtime/config yang wajib dipastikan`; avoid abstract labels like `Inbound contract`.
- If blockers remain, ask confirmation first when interactive; in non-interactive repos emit `NEEDS_CONFIRMATION`; do not emit execution-ready task cards.
- When `READY_FOR_EXECUTION` or `READY_FOR_PARTIAL_EXECUTION`, emit bounded task cards: Task ID, Title, Priority, Impact, Scope, Depends On, Parallel Safe, Goal, Why, Likely Files, Do Not Change, Out Of Scope, Derived From, Acceptance Criteria, and Test Expectation.
- Prefer output order: Status; `Nilai eksekusi yang dipakai` when concrete; `Yang sengaja tidak diubah`; Task Cards; Dependency Order; Parallelization Notes; Ready For Execute Checklist; What executor must stop on.
- Readiness status is required: `NEEDS_CONFIRMATION`, `NEEDS_HUMAN_APPROVAL`, `READY_FOR_PARTIAL_EXECUTION`, or `READY_FOR_EXECUTION`.
- Before `READY_FOR_EXECUTION`, include concrete `Nilai eksekusi yang dipakai`; do not use conditional or unavailable values.
- Do not modify code, redesign architecture, repeat full ECP reasoning, silently redefine approved plans, or invent unsupported ownership/topology/contracts/behavior.
- Use scoped evidence first; report `CONTEXT_BUDGET_LIMITED`, `DRIFT_DETECTED`, or `DRIFT_RISK` when missing/stale evidence affects task safety.
- Cross-repo contracts stay evidence/unknowns; governance uses `NEEDS_HUMAN_APPROVAL` for HIGH risk. Never copy raw secrets into code/context or add orchestration, agents, schedulers, workflow engines, DAGs, Jira/story-point planning, or tooling.
