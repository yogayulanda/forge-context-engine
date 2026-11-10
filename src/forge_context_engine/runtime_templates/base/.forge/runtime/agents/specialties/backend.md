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

Overlay for `forge-orchestrate` workers. It adds focus and context to a role; it never changes the role's steps, gates, stop conditions, or limits.

To customize, copy this file to `.forge/agents/backend.md` and edit the copy. A file in `.forge/agents/` with the same name wins, and `forge update` never overwrites it.

## Load
- `.forge/context` layer `backend` files, plus the interfaces/contracts and data/persistence profile files when the change touches them.

## Focus
- Follow the repo's existing handler -> service -> repository boundaries.
- Keep transactions, idempotency, retry, and timeout behavior explicit.
- Add or update unit tests next to the changed code.

## Review checklist
- Error paths return or log the repo's standard error shape.
- No new cross-boundary calls without evidence they are allowed.
- Retries are idempotent; timeouts are bounded and named.
- Tests cover the success path and at least one failure path.
