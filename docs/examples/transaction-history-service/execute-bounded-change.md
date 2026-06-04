# Execute Bounded Change

Use this step only when an ECP is approved.

## Scenario

The engineer has approved an ECP for a narrow retry history update. The assistant may now modify the repository inside the approved file and behavior boundary.

## Example Forge Prompt

```text
Use Forge execute mode for ECP ecp.retry-history.r1.

Approved boundary:
- update the inbound event handler and history service only
- preserve public event schema
- preserve read APIs
- preserve database schema
- avoid raw payload logging
- do not modify deployment, build pipeline, or unrelated handlers

Run the narrow validation available in this repository and report environment blockers honestly.
```

## Expected Output Shape

- execute status such as `SUCCESS`, `PARTIAL_SUCCESS`, `BLOCKED`, `BLOCKED_BY_ENVIRONMENT`, or `NOT_VALIDATED`
- changed files grouped by responsibility
- validation commands run
- validation gaps and environment blockers
- manual checks still needed
- rollback notes
- intentionally unchanged scope
- reviewer focus
- hidden-change check
- recommended next action

## What The Engineer Should Check

- The diff only touches approved files.
- The implementation preserves public contracts and existing boundaries.
- Sensitive payloads are not logged or copied into docs/tests.
- Validation output distinguishes run checks from checks that could not run.
- The result does not claim success if validation failed or was blocked.

## What Should Stop The Workflow

- Approved ECP is missing.
- Execution requires a new contract decision.
- The assistant needs to alter schema, deployment, build pipeline, or unrelated components.
- Required tooling is missing and the result would otherwise imply validation passed.
- The diff includes broad formatting, generated churn, or unrelated cleanup.

## What Should Remain Out Of Scope

- plan redesign
- additional ECP tasks not approved by the engineer
- producer service changes
- release or deployment behavior
- background job or timed-run design
- self-directed follow-up execution
