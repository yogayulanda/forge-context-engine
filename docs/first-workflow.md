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
Use Forge plan mode for a bounded retry behavior improvement.
Do not change the public event schema.
Preserve existing handler -> service -> repository boundaries.
```

Expected `plan` output:

- goal of the change
- affected flow and files
- proposed phases
- risks around idempotency, replay, DLQ, logging, and rollback
- validation plan
- blockers or required confirmations
- explicit out-of-scope items

`Do not edit files` is not required here. Plan mode is already read-only by contract.

State after this step:

```text
Planning
```

The plan may be persisted as a Quick Plan or SDD artifact if continuity helps, but the artifact is only a handoff record. A newly produced plan has `status: proposed` until the human explicitly approves it.

## Human Approval — Plan

After reviewing the plan output, approve explicitly before continuing:

```text
"Approved. Use Forge implementation mode for the retry plan."
```

The assistant must not proceed to implementation until this signal is given. Reference the plan artifact ID in the next request if continuity is useful.

State after this step:

```text
Planning → Approved
```

## Implementation Breakdown

Human request:

```text
Use Forge implementation mode for the approved retry plan.
Produce an ECP/readiness package and stop conditions before coding.
```

Expected `implementation` output:

- readiness status
- execution values being used
- ECP with likely files
- task sequence
- acceptance criteria
- validation commands
- stop conditions

If retry/DLQ contract, idempotency behavior, or runtime config is unclear, Forge should return `NEEDS_CONFIRMATION` instead of pretending the task is ready. A newly produced ECP has `status: proposed` until the human explicitly approves it.

`Do not edit files` is not required here either. Implementation mode is read-only by contract.

## Human Approval - ECP

After reviewing the implementation ECP, approve explicitly before execution:

```text
"Approved. Use Forge execute mode for ECP ecp.retry-plan.r1."
```

The assistant must not execute code changes until this signal is given.

State after this step:

```text
Implementation → Approved
```

## Execute

Human request:

```text
Use Forge execute mode for the approved ECP.
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

## Validation Inside Execute

Human request:

```text
Use Forge execute mode to run scoped validation for the retry change.
Separate unit, integration, runtime-sensitive, and manual validation.
```

Expected validation output inside `execute`:

- one validation status for requested checks
- automated checks run
- environment blockers
- unvalidated scope
- manual checks for retryable failure, non-retryable failure, duplicate replay, and DLQ behavior when relevant

State after this step:

```text
Validating
```

Validation does not become a redesign or review mode.

## Review

Human request:

```text
Use Forge review mode on the retry change.
Focus on correctness, idempotency, retry/DLQ behavior, validation honesty, and the exact diff reviewed.
```

Expected `review` output:

- Review Report
- verdict
- Diff Reviewed
- severity-grouped findings
- validation result assessment
- lifecycle boundary assessment
- security and context impact
- recommended next step that keeps commit/MR decisions with the human

State after this step:

```text
Reviewing -> Completed (if APPROVED)
```

Commit, push, MR/PR, merge, release, deploy, and production rollout remain outside Forge.

## After Review: Fix Loop

If review returns `NEEDS_CHANGES`:

For `CRITICAL` or `MAJOR` findings:

```text
"Use Forge implementation mode for fixing [finding description].
Scope: only the files identified in the review finding."
```

Get the implementation ECP/readiness package. Human approves. Execute. Then re-review.

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
| `plan` | Quick Plan or SDD (`status: proposed`) | No |
| human approval - plan | Plan transitions to approved implementation input | N/A |
| `implementation` | ECP (`status: proposed`) | No |
| human approval - ECP | ECP transitions to approved execution input | N/A |
| `execute` | Bounded repository changes and validation report | Yes, inside approved scope |
| `review` | Verdict, diff reviewed, and findings | No, unless separately asked to execute fixes |
| fix loop | Bounded code fix | Yes, inside approved fix scope |

## Good Workflow Signals

- Every claim points back to repository evidence or is labeled unknown.
- Mode transitions are human-directed.
- `execute` does not redefine the plan.
- Validation reports missing tooling as an environment blocker, not a fake success.
- Review findings are concrete enough for an engineer to fix.
- No artifact becomes a source of truth over current code.
