# First Workflow

This walkthrough shows one realistic Forge workflow from first question to review-ready output.

Example: improve retry behavior for a backend event consumer without changing the public event contract.

The state labels in this walkthrough are human working states. They are not hidden runtime states, workflow triggers, or automation semantics.

## Starting Ask

Human request:

```text
Use Forge ask mode to explain how the event consumer handles retryable and non-retryable failures.
Cite repository evidence and list unknowns.
```

Expected `ask` output:

- current handler, service, and repository path
- where retry decisions are made
- whether idempotency evidence exists
- where DLQ or non-retryable behavior is defined, if present
- unknowns such as missing producer contract or missing broker behavior

State after this step:

```text
Understanding
```

No files are changed.

## Planning

Human request:

```text
Use Forge planning mode for a bounded retry behavior improvement.
Do not change the public event schema.
Preserve existing handler -> service -> repository boundaries.
```

Expected `planning` output:

- goal of the change
- affected flow and files
- proposed phases
- risks around idempotency, replay, DLQ, logging, and rollback
- validation plan
- blockers or required confirmations
- explicit out-of-scope items

State after this step:

```text
Planning
```

The plan may be persisted as an ECP artifact if continuity helps, but the artifact is only a handoff record.

## Implementation Breakdown

Human request:

```text
Use Forge implementation mode for the approved retry plan.
Produce task cards and stop conditions before coding.
```

Expected `implementation` output:

- readiness status
- execution values being used
- task cards with likely files
- dependency order
- acceptance criteria
- test expectations
- stop conditions

If retry/DLQ contract, idempotency behavior, or runtime config is unclear, Forge should return `NEEDS_CONFIRMATION` instead of pretending the task is ready.

State after this step:

```text
Ready
```

Still no code changes.

## Execute

Human request:

```text
Use Forge execute mode for these approved task cards.
Keep the diff minimal and do not change event schema, deployment, or unrelated files.
```

Expected `execute` output:

- clear execution status
- files changed, grouped by responsibility
- validation commands run
- validation that could not run
- rollback notes
- reviewer focus
- hidden change check

State after this step:

```text
Executing -> Validating
```

Files may be modified only inside the approved boundary.

## Testing

Human request:

```text
Use Forge testing mode to validate the retry change.
Separate unit, integration, runtime-sensitive, and manual validation.
```

Expected `testing` output:

- one testing status
- automated checks run
- environment blockers
- unvalidated scope
- manual checks for retryable failure, non-retryable failure, duplicate replay, and DLQ behavior when relevant

State after this step:

```text
Validating
```

Testing does not become a redesign or review mode.

## Review

Human request:

```text
Use Forge review mode on the retry change.
Focus on correctness, idempotency, retry/DLQ behavior, validation honesty, and MR readiness.
```

Expected `review` output:

- review result
- MR readiness
- severity-grouped findings
- validation gaps
- rollback and safety notes
- suggested next action

State after this step:

```text
Reviewing -> Completed
```

Merge, release, deploy, and production rollout remain outside Forge.

## What Changes Through The Lifecycle

| Step | Main output | Mutation allowed? |
|---|---|---|
| `ask` | Evidence-based understanding | No |
| `planning` | Engineering change plan | No |
| `implementation` | Execution task cards and stop conditions | No |
| `execute` | Bounded repository changes and validation report | Yes, inside approved scope |
| `testing` | Structured validation result | Maybe, if test changes are the scoped task |
| `review` | MR readiness and findings | No, unless separately asked to execute fixes |

## Good Workflow Signals

- Every claim points back to repository evidence or is labeled unknown.
- Mode transitions are human-directed.
- `execute` does not redefine the plan.
- Validation reports missing tooling as an environment blocker, not a fake success.
- Review findings are concrete enough for an engineer to fix.
- No artifact becomes a source of truth over current code.
