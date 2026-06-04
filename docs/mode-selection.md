# Mode Selection

Use this page when the question is: Which Forge mode should I use right now?

## Quick Choice

| Situation | Use | Why |
|---|---|---|
| I need to initialize Forge context/config for this repo. | `init` | Creates confirmed `.forge/context` and `forge.config.yaml` through bounded scan and human confirmation. |
| I need to understand current code or context. | `ask` | Answers from context and scoped evidence without creating a plan or changing files. |
| I need to shape a non-trivial change. | `plan` | Produces a Quick Plan or SDD with scope, risk, validation, and unknowns. |
| I have an approved plan and need an execution handoff. | `implementation` | Converts the approved plan into an Execution Context Package. |
| I have an approved ECP and want changes applied. | `execute` | Modifies the repository inside the approved scope. |
| I need senior MR-style assessment. | `review` | Checks correctness, scope, validation honesty, security, context impact, and MR readiness. |
| I need to check context freshness/health. | `verify-context` | Verifies `.forge/context` health only. |

## Ask vs Scenario Diagnosis

Use `ask` when you are learning normal behavior:

```text
Use Forge ask mode to explain how payment status is updated.
```

When there is a symptom, failure, regression, alert, or production concern, treat it as an incident scenario. Start with `ask` for evidence gathering, use `plan` if remediation needs design, use `implementation` for the approved ECP, then `execute` and `review`.

## Plan vs Implementation

Use `plan` when the change still needs engineering shape:

```text
Use Forge plan mode for adding retry backoff to this consumer.
Cover risks, validation, rollback, and out-of-scope changes.
```

Use `implementation` when the plan is approved and the next need is an ECP:

```text
Use Forge implementation mode for the approved retry backoff plan.
Produce an Execution Context Package and stop conditions.
```

If contract authority, runtime values, destructive changes, or acceptance criteria are unresolved, `implementation` should stop with confirmation instead of producing an execution-ready ECP.

## Validation vs Review

Validation is not a core lifecycle mode. `execute` runs scoped validation for changed work, and `review` checks validation evidence and gaps.

Use `review` to decide whether a change is acceptable:

```text
Use Forge review mode on this branch.
Focus on correctness, validation honesty, rollback, security, context impact, and MR readiness.
```

## Execute Boundaries

Use `execute` only when the approved ECP and change boundary are clear.

Good execute request:

```text
Use Forge execute mode for the approved retry ECP.
Do not change the event schema, deployment files, or unrelated handlers.
```

Do not use `execute` to:

- discover the whole design
- approve risky decisions
- redefine architecture
- infer missing contracts
- perform broad cleanup
- silently continue through missing values

When the boundary is unclear, go back to `plan` or `implementation`.

## Verify-Context Boundaries

Use `verify-context` only for `.forge/context` health:

```text
Use Forge verify-context mode to check whether context cards are stale after this branch.
```

Do not use `verify-context` to review code, approve an MR, validate a test suite, or check whether an ECP is complete.

## Common Confusion Cases

| Confusion | Use this |
|---|---|
| "I want to know what to change, but not code yet." | `plan` |
| "I know the change; I need the handoff package." | `implementation` |
| "The code is changed; are we ready to merge?" | `review` |
| "Tests are failing; why?" | Incident scenario starting with `ask`; use `execute` only for an approved fix. |
| "Can the assistant fix the review findings?" | `execute` with the approved finding scope, or `implementation` first for major fixes. |
| "Can we clean this package while preserving behavior?" | Refactor scenario using `plan`, `implementation`, `execute`, and `review` as needed. |
| "Can we skip straight to execute?" | Only for clear, low-risk, bounded changes with explicit approval. |
| "Review returned needs fix. What now?" | `implementation` for fix ECP on critical/major findings; `execute` directly for bounded minor fixes with human-named scope. |
| "Can I go back from review to execute?" | Yes - human approves the fix scope, then `execute` with that scoped request. |

## Review Fix Path

When `review` returns findings that need fixes, the fix path is:

For critical or major findings:

1. Use `implementation` to produce a fix ECP for the finding scope.
2. Human approves the ECP.
3. Use `execute` for the approved ECP.
4. Re-use `review` to verify the findings are resolved.

For minor findings:

- Human can directly request `execute` with the precise fix scope named.
- Review will verify residual findings when re-invoked.

Do not re-run `execute` on the original ECP to fix review findings without the human naming the fix scope. Review findings do not automatically become execute tasks.

## Correct Mode Examples

```text
Use Forge ask mode to explain how user permissions are checked for this endpoint.
```

```text
Use Forge plan mode for replacing synchronous notification send with an outbox write.
Preserve existing API behavior.
```

```text
Use Forge implementation mode for the approved outbox plan.
Stop if transaction boundaries or retry semantics are unclear.
```

```text
Use Forge execute mode for the approved ECP.
Run the narrow tests available in this repo and report any environment blockers.
```

```text
Use Forge review mode on this MR and report MR readiness.
```

```text
Use Forge verify-context mode to check affected context cards after this branch.
```
