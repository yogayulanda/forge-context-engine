# Mode Selection

Use this page when the question is: Which Forge mode should I use right now?

## Quick Choice

| Situation | Use | Why |
|---|---|---|
| I need to understand current code or context. | `ask` | Answers from evidence without creating a plan or changing files. |
| I need to shape a non-trivial change. | `planning` | Produces scope, risk, validation, rollback, and unknowns. |
| I have an approved direction and need task cards. | `implementation` | Converts intent into executable boundaries and stop conditions. |
| I have approved task cards and want changes applied. | `execute` | Modifies the repository inside the approved scope. |
| I need validation strategy, test changes, or validation reporting. | `testing` | Owns structured validation and gaps. |
| I need senior MR-style assessment. | `review` | Checks correctness, risk, validation honesty, and MR readiness. |
| Something is broken or unclear in operation. | `incident` | Separates symptoms, evidence, likely causes, mitigations, and unknowns. |
| I want behavior-preserving cleanup. | `refactor` | Keeps cleanup bounded and risk-classified. |

## Ask vs Incident

Use `ask` when you are learning normal behavior:

```text
Use Forge ask mode to explain how payment status is updated.
```

Use `incident` when there is a symptom, failure, regression, alert, or production concern:

```text
Use Forge incident mode for duplicate payment status updates after retry.
Separate symptoms, likely causes, and next checks.
```

If the problem is only "I do not know how this works", use `ask`. If the problem is "something appears wrong", use `incident`.

## Planning vs Implementation

Use `planning` when the change still needs engineering shape:

```text
Use Forge planning mode for adding retry backoff to this consumer.
Cover risks, validation, rollback, and out-of-scope changes.
```

Use `implementation` when the plan or intent is approved and the next need is execution readiness:

```text
Use Forge implementation mode for the approved retry backoff plan.
Produce task cards and stop conditions.
```

If contract authority, runtime values, destructive changes, or acceptance criteria are unresolved, `implementation` should stop with confirmation instead of producing ready task cards.

## Testing vs Review

Use `testing` to validate behavior:

```text
Use Forge testing mode to validate retry behavior and idempotent replay.
```

Use `review` to decide whether a change is acceptable:

```text
Use Forge review mode on this branch.
Focus on correctness, validation honesty, rollback, and MR readiness.
```

Testing asks "what has been validated?" Review asks "is this change acceptable?"

## Execute Boundaries

Use `execute` only when the change boundary is clear.

Good execute request:

```text
Use Forge execute mode for task cards TR-1 and TR-2.
Do not change the event schema, deployment files, or unrelated handlers.
```

Do not use `execute` to:

- discover the whole design
- approve risky decisions
- redefine architecture
- infer missing contracts
- perform broad cleanup
- silently continue through missing values

When the boundary is unclear, go back to `planning` or `implementation`.

## Common Confusion Cases

| Confusion | Use this |
|---|---|
| "I want to know what to change, but not code yet." | `planning` |
| "I know the change; I need a safe execution checklist." | `implementation` |
| "The code is changed; are we ready to merge?" | `review` |
| "Tests are failing; why?" | `incident` if diagnosing failure, `testing` if validating a change |
| "Can the assistant fix the review findings?" | `execute` with the approved finding scope |
| "Can we clean this package while preserving behavior?" | `refactor` |
| "Can we skip straight to execute?" | Only for clear, low-risk, bounded changes |
| "Review returned NEEDS_CHANGES. What now?" | `implementation` for fix task cards on `CRITICAL`/`MAJOR` findings; `execute` directly for bounded `MINOR` fixes with human-named scope |
| "Can I go back from review to execute?" | Yes — human approves the fix scope, then `execute` with that scoped request |

## Review Fix Path

When `forge-review` returns `NEEDS_CHANGES`, the fix path is:

For `CRITICAL` or `MAJOR` findings:

1. Use `implementation` to produce fix task cards for the finding scope.
2. Human approves the task cards.
3. Use `execute` for the approved task cards.
4. Re-use `review` to verify the findings are resolved.

For `MINOR` findings:

- Human can directly request `execute` with the precise fix scope named.
- Review will verify residual findings when re-invoked.

Do not re-run `execute` on the original task cards to fix review findings without the human naming the fix scope. Review findings do not automatically become execute tasks.

## Correct Mode Examples

```text
Use Forge ask mode to explain how user permissions are checked for this endpoint.
```

```text
Use Forge planning mode for replacing synchronous notification send with an outbox write.
Preserve existing API behavior.
```

```text
Use Forge implementation mode for the approved outbox plan.
Stop if transaction boundaries or retry semantics are unclear.
```

```text
Use Forge execute mode for the approved task cards.
Run the narrow tests available in this repo and report any environment blockers.
```

```text
Use Forge testing mode to validate unit, integration, rollback, and replay behavior for this change.
```

```text
Use Forge review mode on this MR and report MR readiness.
```

```text
Use Forge incident mode for the 500s on checkout after the last deploy.
Use logs and recent diffs if available; label unknowns.
```

```text
Use Forge refactor mode for this repository package.
Preserve behavior and avoid public contract changes.
```
