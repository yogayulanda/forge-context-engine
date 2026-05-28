# Ask Current Flow

Use this step to understand the current service behavior before proposing a change.

## Scenario

An engineer wants to know how a transaction history service currently handles inbound history events, duplicate messages, status updates, and persistence boundaries.

The service shape is generic:

```text
event handler -> history service -> history repository
```

## Example Forge Prompt

```text
Use Forge ask mode to explain the current transaction history event flow.

Focus on:
- where inbound events enter the service
- how the event maps to a history record
- whether duplicate or replay handling exists
- where status values are validated or persisted
- what repository evidence is missing

Do not propose changes yet. Sanitize any sensitive identifiers in the response.
```

## Expected Output Shape

- concise current-flow summary
- repository evidence grouped by file or component
- known behavior for event intake, service logic, repository writes, and read APIs
- explicit `unknowns` for retry, idempotency, schema authority, or DLQ behavior that cannot be proven
- no implementation plan
- no file changes

## What The Engineer Should Check

- Claims cite current code, docs, migrations, or tests.
- Unknowns are visible instead of replaced with assumptions.
- The answer does not treat a sanitized example as repository truth.
- The answer separates read API behavior from event ingestion behavior.
- Any sensitive or proprietary names are redacted or generalized.

## What Should Stop The Workflow

- The assistant invents event topics, partner systems, production incidents, or ownership.
- The answer exposes real payloads, credentials, customer identifiers, or internal URLs.
- The current behavior cannot be found and the assistant still claims certainty.
- The request has become an incident response or execution request without a new mode.

## What Should Remain Out Of Scope

- retry implementation
- schema redesign
- data backfill
- deployment changes
- producer service changes
- MR review
