# Plan Retry History Update

Use this step after the current flow is understood and a bounded change needs engineering shape.

## Scenario

The team wants a safer retry history update path for inbound events. The desired behavior is to preserve the public event schema and existing service boundary while making duplicate replay and retry status persistence easier to validate.

## Example Forge Prompt

```text
Use Forge plan mode for a bounded retry history update in this service.

Preserve:
- public event schema
- existing handler -> service -> repository boundary
- read API behavior
- current deployment and configuration shape

Cover:
- repository evidence
- affected surface inventory across handlers, services, repositories, tests, and config
- proposed change scope
- idempotency and duplicate replay risks
- validation plan
- rollback notes
- required confirmations
- explicit out-of-scope items

Do not write code.
```

## Expected Output Shape

- plan status
- current evidence summary
- affected surface inventory with all discovered usages and entry points
- goal and non-goals
- affected files or components
- proposed phases
- risks and mitigations
- validation plan
- rollback notes
- required confirmations
- out-of-scope list

## What The Engineer Should Check

- The plan keeps the change inside the history service.
- Retry and duplicate behavior are grounded in repository evidence or listed as unknown.
- Public API and event schema changes are explicitly excluded unless approved.
- Rollback is practical and tied to changed files or configuration.
- Validation covers unit, integration, replay, and manual checks when relevant.

## What Should Stop The Workflow

- Missing contract values are treated as confirmed behavior.
- The plan depends on changing an upstream producer without approval.
- The plan introduces new runtime infrastructure, timed jobs, queues, or deployment automation.
- The plan exposes real internal names, payloads, customer data, or production details.
- The plan cannot name what files or components are likely affected.

## What Should Remain Out Of Scope

- source-of-truth ownership changes
- event schema migration
- production replay jobs
- build pipeline design
- self-directed cross-step automation
- broad service architecture redesign
