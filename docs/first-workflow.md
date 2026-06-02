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

The plan may be persisted as an ECP artifact if continuity helps, but the artifact is only a handoff record. A newly produced ECP has `status: proposed` until the human explicitly approves it.

## Human Approval — Plan

After reviewing the planning output, approve explicitly before continuing:

```text
"Approved. Use Forge implementation mode for the retry plan."
```

The assistant must not proceed to implementation until this signal is given. Reference the ECP artifact ID in the next request if continuity is useful.

State after this step:

```text
Planning → Approved
```

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

If retry/DLQ contract, idempotency behavior, or runtime config is unclear, Forge should return `NEEDS_CONFIRMATION` instead of pretending the task is ready. A newly produced Execution Contract has `status: proposed` until the human explicitly approves it.

## Human Approval — Task Cards

After reviewing the implementation task cards, approve explicitly before execution:

```text
"Approved. Use Forge execute mode for task cards IMP-001 and IMP-002."
```

The assistant must not execute code changes until this signal is given.

State after this step:

```text
Implementation → Approved
```

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
Reviewing -> Completed (if APPROVED)
```

Merge, release, deploy, and production rollout remain outside Forge.

## After Review: Fix Loop

If review returns `NEEDS_CHANGES`:

For `CRITICAL` or `MAJOR` findings:

```text
"Use Forge implementation mode for fixing [finding description].
Scope: only the files identified in the review finding."
```

Get implementation task cards. Human approves. Execute. Then re-review.

For `MINOR` findings:

```text
"Use Forge execute mode to fix [finding description] in [file].
Do not change any other files."
```

Review will verify prior findings are resolved when re-invoked. Review findings do not automatically become execute tasks; the human must name the fix scope.

State after fix loop completes:

```text
Reviewing -> Completed
```

## What Changes Through The Lifecycle

| Step | Main output | Mutation allowed? |
|---|---|---|
| `ask` | Evidence-based understanding | No |
| `planning` | ECP (`status: proposed`) | No |
| human approval — plan | ECP transitions to `approved` | N/A |
| `implementation` | Execution Contract (`status: proposed`) | No |
| human approval — task cards | Execution Contract transitions to `approved` | N/A |
| `execute` | Bounded repository changes and validation report | Yes, inside approved scope |
| `testing` | Structured validation result | Maybe, if test changes are the scoped task |
| `review` | MR readiness and findings | No, unless separately asked to execute fixes |
| fix loop | Bounded code fix | Yes, inside approved fix scope |

## Good Workflow Signals

- Every claim points back to repository evidence or is labeled unknown.
- Mode transitions are human-directed.
- `execute` does not redefine the plan.
- Validation reports missing tooling as an environment blocker, not a fake success.
- Review findings are concrete enough for an engineer to fix.
- No artifact becomes a source of truth over current code.
