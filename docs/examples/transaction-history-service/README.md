# Transaction History Service Workflow

This example shows Forge across a realistic service change:

```text
ask -> planning -> implementation -> execute -> testing -> review
```

The reference pattern is a generic transaction history service: a backend service stores immutable history records, exposes read APIs, and may consume sanitized event messages from another system. Names, paths, payloads, and scenarios are intentionally generic for public documentation.

This is not a demo repository and not a product architecture. Use it as a workflow visibility example for how Forge keeps real engineering work bounded.

## Walkthrough

| Step | Example |
|---|---|
| Understand current behavior | [ask-current-flow.md](ask-current-flow.md) |
| Plan a retry/history update | [planning-retry-history-update.md](planning-retry-history-update.md) |
| Produce task cards | [implementation-task-cards.md](implementation-task-cards.md) |
| Execute a bounded change | [execute-bounded-change.md](execute-bounded-change.md) |
| Validate behavior | [testing-validation.md](testing-validation.md) |
| Review MR readiness | [review-mr-readiness.md](review-mr-readiness.md) |

## Shared Scenario

A service team wants to improve how a transaction history service records retry-related history updates from an inbound event consumer. The goal is to make duplicate replay and retry status handling clearer without changing public APIs, event schema, deployment topology, or unrelated read paths.

Example sanitized shape:

```text
cmd/service-main
internal/handler/event
internal/service/history
internal/repository/history
internal/model
```

Example sanitized event:

```json
{
  "event_id": "evt_example_001",
  "reference_id": "ref_example_001",
  "status": "COMPLETED",
  "occurred_at": "2026-01-15T10:30:00Z"
}
```

## Engineer Checks

- Every claim should cite current repository files or be labeled `unknown`.
- Mode transitions should be requested by a human.
- `implementation` should stop when execution values are missing.
- `execute` should only modify approved files.
- `testing` should separate run checks from blocked checks.
- `review` should focus on correctness, validation honesty, and MR readiness.

## Stop The Workflow

Stop instead of continuing when:

- retry, duplicate, or non-retryable behavior has no repository evidence and no approved execution value
- event schema or public API changes are required but not approved
- secrets, customer data, partner identifiers, production incident details, or proprietary names would be exposed
- the assistant starts proposing deploy pipelines, timed jobs, self-directed chains, or external execution systems
- validation cannot run and the output would otherwise imply success

## Out Of Scope

- production architecture diagrams
- real service names, internal paths, credentials, partner/customer identifiers, or incident data
- build pipelines, deployment, release, timed-job, self-directed agent, persistent-state, or cross-step automation behavior
- lifecycle semantic changes to Forge
- broad application redesign
