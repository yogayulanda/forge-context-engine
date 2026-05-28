# Implementation Task Cards

Use this step after the plan is approved and the engineer needs execution-ready task cards.

## Scenario

The approved plan allows a bounded retry history update, but execution values still need to be explicit before code changes begin.

Example execution values:

```text
duplicate_behavior = keep first successful history record and do not create a second record
retryable_failure_behavior = return retryable error from handler without raw payload logging
non_retryable_failure_behavior = record sanitized failure reason when contract permits
schema_change_allowed = false
```

These values are examples only. A real repository must use values approved for that repository.

## Example Forge Prompt

```text
Use Forge implementation mode for the approved retry history update plan.

Produce execution-ready task cards.
Stop with NEEDS_CONFIRMATION if retry behavior, duplicate handling, schema authority, or required validation values are missing.

Keep the task cards scoped to the existing handler -> service -> repository path.
Do not write code.
```

## Expected Output Shape

- readiness status such as `READY_FOR_EXECUTION` or `NEEDS_CONFIRMATION`
- execution values used
- numbered task cards with likely files
- dependency order
- acceptance criteria
- validation expectations
- stop conditions
- intentionally unchanged scope

## What The Engineer Should Check

- The task cards are small enough to execute and review.
- Every task maps to the approved plan.
- Missing values produce `NEEDS_CONFIRMATION`, not guessed defaults.
- The task cards preserve existing boundaries and naming style.
- Validation is attached to behavior, not only to file edits.

## What Should Stop The Workflow

- The assistant cannot list execution values.
- A task card requires schema, API, deployment, or producer changes that were out of scope.
- Idempotency, retry, or non-retryable behavior is still unresolved.
- The assistant starts generating code in implementation mode.
- The task cards include unrelated cleanup.

## What Should Remain Out Of Scope

- code edits
- broad refactors
- new public contracts
- deployment automation
- hidden generated artifacts as source of truth
- persistent assistant state
