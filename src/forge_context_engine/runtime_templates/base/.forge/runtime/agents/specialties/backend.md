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
- The repo's shared error catalog, response helper, and lint config, when they exist.
- Language overlay when one matches, for example `backend-go`.

## As planner
- Record the existing structure in the SDD: layout (per layer or per feature), error catalog, and response helper paths. New files go into that structure.
- Name the entry point (endpoint, consumer, job), the layers it passes through, and the data it reads or writes.
- State the contract impact explicitly: request/response fields, status codes, event schema. `none` must be backed by evidence.
- State the data impact: new or changed tables, columns, indexes, or queries. A schema change is a migration and a high-risk area.
- A new error code is a contract change and goes in the SDD. Changing or removing an existing code is a contract break.
- If the repo has no shared error catalog or response helper, ask in the Clarify step; do not plan a new one silently.
- For any write path: who retries it, whether it must be idempotent, and what the idempotency key is.
- For any outbound call: timeout value, retry policy, and what happens on partial failure.
- Acceptance criteria include at least one failure path (invalid input, dependency down, duplicate request).
- ECP: list files per layer in dependency order (model -> repository -> service -> handler -> tests).

## As executor
- The repo's existing pattern wins over this file: structure, naming, errors, responses. Do not move, rename, or tidy code outside ECP scope.
- Keep business rules in the service layer; handlers only parse, validate, and map errors.
- Validate input at the boundary. Return errors through the shared error catalog and responses through the shared helper; no ad-hoc error codes or hand-built responses.
- Wrap errors with internal context for logs. An error that maps to no catalog entry becomes the generic internal error; never leak internal detail to clients.
- Handle each error once: return it or log it, not both. Never swallow an error or log and continue on a write path.
- Readability: names state intent (`pendingTransfers`, not `data2`); one job per function; guard clauses and early return instead of deep nesting; named constants instead of magic numbers; comments explain why, not what; no commented-out code or TODO without a ticket.
- Money never uses binary floating point; use integer minor units or the repo's decimal type. Durations use typed time values; stored timestamps are UTC.
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
- Structure: new code follows the existing layout and patterns; no unrelated moves or renames.
- Errors: catalog and response helper used; no internal detail in client responses.
- Readability: unclear names, multi-job functions, deep nesting, or dead code are MINOR; readability that hides a logic, error, or contract problem is MAJOR.
- Observability: errors are logged once with enough context to trace a request.
- Tests: assert behavior, not implementation; cover at least one failure path.
