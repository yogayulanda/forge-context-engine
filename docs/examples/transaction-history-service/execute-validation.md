# Execute Validation

Use this step to validate the change and make remaining gaps visible.

## Scenario

A bounded retry history update has been implemented. The engineer needs validation evidence before review.

## Example Forge Prompt

```text
Use Forge execute mode to run scoped validation for the retry history update.

Separate:
- unit checks
- integration or repository checks
- duplicate replay checks
- retryable failure checks
- non-retryable failure checks
- manual checks
- environment blockers

Do not redesign the change. Do not mark blocked checks as passed.
```

## Expected Output Shape

- validation status such as `PASSED`, `FAILED`, `PARTIAL`, `BLOCKED_BY_ENVIRONMENT`, or `NOT_RUN`
- validation scope
- commands run
- results and failures
- blocked checks with reason
- manual validation checklist
- unvalidated risk
- suggested next action

## What The Engineer Should Check

- The validation scope matches the approved change.
- Tests cover normal update, duplicate replay, retryable failure, and non-retryable failure when applicable.
- Missing tooling or services are reported as environment blockers.
- Manual checks are specific enough to perform.
- The output does not become an MR review.

## What Should Stop The Workflow

- Required test data would expose real customer, partner, credential, or production details.
- The assistant cannot run or describe relevant validation and still claims `PASSED`.
- Validation requires out-of-scope infrastructure changes.
- A failed test reveals an unresolved contract or data-safety issue.

## What Should Remain Out Of Scope

- approving merge readiness
- fixing unrelated tests
- changing lifecycle semantics
- creating build pipelines
- production replay
- release management
