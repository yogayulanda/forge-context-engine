# Backend Retry Flow

Use this example for a bounded backend retry improvement.

## Ask

```text
Use Forge ask mode to explain how this consumer handles retryable failure, non-retryable failure, duplicate messages, and DLQ behavior.
Cite repository evidence and list unknowns.
```

Expected output:

- handler/service/repository path
- retry decision point
- idempotency evidence
- DLQ evidence or unknowns
- current validation gaps

## Plan

```text
Use Forge plan mode for improving retry behavior in this consumer.
Preserve the public event schema and existing service boundary.
Cover validation, rollback, and out-of-scope changes.
```

Expected output:

- narrow change goal
- affected files and flows
- retry/idempotency risks
- validation plan
- rollback notes
- required confirmations

## Implementation

```text
Use Forge implementation mode for the approved retry plan.
Produce an ECP and stop if retry/DLQ contract values are missing.
```

Expected output:

- readiness status
- execution values used
- ECP task cards
- stop conditions
- test expectations

## Execute

```text
Use Forge execute mode for the approved retry ECP.
Keep the diff minimal and do not change schema, deployment, or unrelated handlers.
```

Expected output:

- changed files
- validation run
- validation gaps
- rollback notes
- reviewer focus
