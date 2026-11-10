---
id: specialty.backend
title: "Specialty: Backend"
type: meta
status: confirmed
confidence: high
source: human
evidence: [{ type: doc, ref: ../../modes/orchestrate.md }]
owner: forge-context-engine
updated: 2026-11-10
applies_to: [planner, executor, reviewer]
applies_when: layer backend is active and the change touches server, API, service, repository, or worker code
---

# Specialty: Backend

Overlay for `forge-orchestrate` workers. Each worker reads `Load` and only the `As <role>` section for its own role. It never changes the role's steps, gates, stop conditions, or limits.

To customize, copy this file to `.forge/agents/backend.md` and edit the copy. A file in `.forge/agents/` with the same name wins, and `forge update` never overwrites it. Put team-specific rules (libraries, error shapes, naming, test commands) in the copy, not here.

## Load
- `.forge/context` layer `backend` files.
- Interfaces/contracts and data/persistence profile files when the change touches an endpoint, message, or table.
- The nearest existing handler, service, and repository for the same resource, as the pattern to copy.

## As planner
- Name the entry point (endpoint, consumer, job), the layers it passes through, and the data it reads or writes.
- State the contract impact explicitly: request/response fields, status codes, event schema. `none` must be backed by evidence.
- State the data impact: new or changed tables, columns, indexes, or queries. A schema change is a migration and a high-risk area.
- For any write path: who retries it, whether it must be idempotent, and what the idempotency key is.
- For any outbound call: timeout value, retry policy, and what happens on partial failure.
- Acceptance criteria include at least one failure path (invalid input, dependency down, duplicate request).
- ECP: list files per layer in dependency order (model -> repository -> service -> handler -> tests).

## As executor
- Copy the structure of the nearest existing handler/service/repository; do not introduce a new layering style.
- Keep business rules in the service layer; handlers only parse, validate, and map errors.
- Validate input at the boundary and return the repo's standard error shape and status codes.
- Wrap errors with context; never swallow an error or log and continue on a write path.
- Use the repo's existing transaction helper; keep a transaction from the first write to the last, never across an outbound call.
- Make every outbound call honor a context deadline or explicit timeout.
- Log with the repo's logger and existing field names; never log secrets, tokens, or full PII.
- Write table-driven unit tests next to the code: success path, validation failure, dependency failure.
- Run the repo's formatter, linter, and unit tests for the changed packages before reporting.

## As reviewer
- Contract: response fields, status codes, and error shapes match the SDD; no silent field rename or removal.
- Correctness: nil/empty handling, integer and decimal handling for amounts, time zones, and pagination bounds.
- Concurrency: shared state is guarded; goroutines/threads have an exit path; no unbounded fan-out.
- Resilience: timeouts are bounded and named, retries are idempotent, and partial failure leaves consistent data.
- Data: queries use existing indexes or the SDD names the new one; no N+1 loops over the database.
- Observability: errors are logged once with enough context to trace a request.
- Tests: assert behavior, not implementation; cover at least one failure path.
