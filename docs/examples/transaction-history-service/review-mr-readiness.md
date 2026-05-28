# Review MR Readiness

Use this step when the branch or MR needs a senior engineering review.

## Scenario

The retry history update has code changes and validation results. The engineer wants to know whether the MR is ready, needs changes, or has unvalidated risk.

## Example Forge Prompt

```text
Use Forge review mode on this retry history update branch.

Focus on:
- correctness
- idempotency and duplicate replay behavior
- retryable and non-retryable failure behavior
- public contract preservation
- validation honesty
- data-safety and logging
- rollback readiness
- MR readiness

Do not implement fixes unless explicitly asked in a separate execute request.
```

## Expected Output Shape

- review status such as `APPROVED`, `NEEDS_CHANGES`, or `PARTIAL_REVIEW`
- MR readiness
- severity-grouped findings
- validation gaps
- rollback and safety notes
- hidden change check
- suggested next action

## What The Engineer Should Check

- Findings cite files, diffs, tests, or explicit missing evidence.
- Review does not repeat the implementation plan as if it were evidence.
- Validation gaps remain visible.
- Data-safety and logging behavior are checked.
- The next action is clear: merge, fix specific findings, validate more, or ask for confirmation.

## What Should Stop The Workflow

- The branch contains hidden schema, API, deployment, or unrelated changes.
- Retry or duplicate behavior is still not evidenced.
- Sensitive details are present in tests, logs, docs, examples, or review output.
- Required validation did not run and the review still says ready.
- The assistant starts fixing findings without an execute request.

## What Should Remain Out Of Scope

- merging
- deployment
- release notes for production rollout
- self-directed follow-up tasks
- build pipeline or timed-run changes
- broad architecture recommendations
